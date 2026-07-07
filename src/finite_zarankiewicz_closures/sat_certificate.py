"""Integrity checks for the traced ``Z(10,23,3,3)`` SAT certificate family.

The core gate deliberately does not implement an LRAT kernel.  It recomputes
the arithmetic profile scope, checks every formula/proof hash and DIMACS
header, and binds those artifacts to the case certificate.  The optional
``scripts/replay_z10_23_certificates.py`` command decompresses each DRAT core,
converts it to LRAT with ``drat-trim``, and checks that LRAT with the independent
``lrat-check`` program.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .extended import z10_23_profile_report


class SatCertificateError(ValueError):
    """Raised when the stored SAT manifest or an artifact fails integrity checks."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_profile(label: str) -> str:
    terms = []
    for term in label.split():
        degree, count = term.split("^", 1)
        terms.append((int(degree), int(count)))
    return ",".join(f"{degree}x{count}" for degree, count in sorted(terms))


def _resolve_artifact(root: Path, payload: Mapping[str, Any]) -> tuple[Path, str]:
    """Resolve one declared artifact and check its path and byte length."""

    relative = payload.get("file")
    expected_hash = payload.get("sha256")
    expected_bytes = payload.get("bytes")
    if not isinstance(relative, str) or not isinstance(expected_hash, str):
        raise SatCertificateError("artifact metadata lacks a file or SHA-256")
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError as error:
        raise SatCertificateError(f"SAT artifact escapes repository root: {relative}") from error
    if not path.is_file():
        raise SatCertificateError(f"missing SAT artifact: {relative}")
    if expected_bytes is not None and path.stat().st_size != expected_bytes:
        raise SatCertificateError(f"SAT artifact size mismatch: {relative}")
    return path, expected_hash


def _check_hashed_file(root: Path, payload: Mapping[str, Any]) -> Path:
    path, expected_hash = _resolve_artifact(root, payload)
    if _sha256(path) != expected_hash:
        raise SatCertificateError(f"SAT artifact hash mismatch: {payload['file']}")
    return path


def _check_dimacs(path: Path, payload: Mapping[str, Any]) -> None:
    header = None
    clause_count = 0
    with path.open(encoding="ascii") as handle:
        for line_number, line in enumerate(handle, start=1):
            if line.startswith("p cnf "):
                if header is not None:
                    raise SatCertificateError(f"multiple DIMACS headers: {path}")
                fields = line.split()
                if len(fields) != 4:
                    raise SatCertificateError(f"malformed DIMACS header: {path}")
                header = (int(fields[2]), int(fields[3]))
            elif line and line[0] not in {"c", "\n"}:
                if header is None:
                    raise SatCertificateError(f"clause before DIMACS header: {path}")
                try:
                    literals = [int(token) for token in line.split()]
                except ValueError as error:
                    raise SatCertificateError(
                        f"noninteger DIMACS token: {path}:{line_number}"
                    ) from error
                if not literals or literals[-1] != 0 or 0 in literals[:-1]:
                    raise SatCertificateError(
                        f"malformed DIMACS clause: {path}:{line_number}"
                    )
                if any(abs(literal) > header[0] for literal in literals[:-1]):
                    raise SatCertificateError(
                        f"DIMACS literal outside header range: {path}:{line_number}"
                    )
                clause_count += 1
    if header is None or header[1] != clause_count:
        raise SatCertificateError(f"DIMACS body count mismatch: {path}")
    if header != (payload.get("variables"), payload.get("clauses")):
        raise SatCertificateError(f"DIMACS metadata mismatch: {path}")


def _check_proof_artifact(root: Path, payload: Mapping[str, Any]) -> int:
    """Verify one direct or byte-split compressed DRAT artifact."""

    proof_format = payload.get("format")
    if proof_format == "DRAT+xz":
        path = _check_hashed_file(root, payload)
        if not path.name.endswith(".drat.xz") or path.stat().st_size >= 100_000_000:
            raise SatCertificateError(f"unexpected proof file: {path}")
        return path.stat().st_size
    if proof_format != "DRAT+xz+split":
        raise SatCertificateError("unexpected proof format")

    parts = payload.get("parts")
    if not isinstance(parts, list) or len(parts) < 2:
        raise SatCertificateError("split proof must contain at least two parts")
    relative_names = [part.get("file") for part in parts if isinstance(part, dict)]
    if (
        len(relative_names) != len(parts)
        or not all(isinstance(name, str) for name in relative_names)
        or relative_names != sorted(relative_names)
    ):
        raise SatCertificateError("split proof parts are not in canonical order")
    digest = hashlib.sha256()
    total_bytes = 0
    for part in parts:
        path, expected_hash = _resolve_artifact(root, part)
        if ".drat.xz.part-" not in path.name or path.stat().st_size >= 100_000_000:
            raise SatCertificateError(f"unexpected split proof part: {path}")
        part_digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
                part_digest.update(block)
        if part_digest.hexdigest() != expected_hash:
            raise SatCertificateError(f"SAT artifact hash mismatch: {part['file']}")
        total_bytes += path.stat().st_size
    if digest.hexdigest() != payload.get("sha256"):
        raise SatCertificateError("reassembled compressed proof hash mismatch")
    if total_bytes != payload.get("bytes"):
        raise SatCertificateError("reassembled compressed proof size mismatch")
    return total_bytes


def verify_z10_23_sat_manifest(manifest: Mapping[str, Any], root: Path) -> dict[str, Any]:
    """Check an untrusted manifest against arithmetic scope and file contents."""

    if manifest.get("schema_version") != 1:
        raise SatCertificateError("unsupported Z(10,23) SAT manifest schema")
    if manifest.get("theorem") != "Z(10,23,3,3)=112":
        raise SatCertificateError("unexpected theorem in SAT manifest")
    if manifest.get("excluded_target") != 113:
        raise SatCertificateError("unexpected excluded target in SAT manifest")
    if manifest.get("arithmetic_profile_count") != 25:
        raise SatCertificateError("unexpected arithmetic profile count in SAT manifest")
    if manifest.get("arithmetic_eliminated_profiles") != 12:
        raise SatCertificateError("unexpected arithmetic elimination count in SAT manifest")
    if manifest.get("toolchain") != {
        "cnf_generator": "python-sat 1.9.dev2",
        "solver": "CaDiCaL 3.0.0",
        "solver_commit": "7b99c07f0bcab5824a5a3ce62c7066554017f641",
        "proof_converter": "drat-trim",
        "proof_projection": "lrat-check DRAT output",
        "proof_checker": "drat-trim + lrat-check",
        "proof_tools_commit": "2e3b2dc0ecf938addbd779d42877b6ed69d9a985",
    }:
        raise SatCertificateError("unexpected SAT proof toolchain metadata")

    arithmetic = z10_23_profile_report()
    expected_profiles = {_canonical_profile(label) for label in arithmetic["sat_profiles"]}
    cases = manifest.get("profiles")
    if not isinstance(cases, list) or len(cases) != 13:
        raise SatCertificateError("SAT manifest must contain thirteen profiles")
    observed_profiles = {case.get("profile") for case in cases if isinstance(case, dict)}
    if observed_profiles != expected_profiles:
        raise SatCertificateError("SAT manifest profile scope differs from arithmetic reduction")

    total_compressed_bytes = 0
    for case in cases:
        profile = case["profile"]
        if case.get("strategy") != "direct_cadical":
            raise SatCertificateError(f"non-direct SAT strategy for {profile}")

        formula_payload = case.get("formula")
        proof_payload = case.get("proof")
        if not isinstance(formula_payload, dict) or not isinstance(proof_payload, dict):
            raise SatCertificateError(f"incomplete SAT artifact metadata: {profile}")
        formula_path = _check_hashed_file(root, formula_payload)
        _check_dimacs(formula_path, formula_payload)
        proof_bytes = _check_proof_artifact(root, proof_payload)
        if case.get("replay") != {
            "checker": "drat-trim -> LRAT -> lrat-check",
            "status": "VERIFIED",
        }:
            raise SatCertificateError(f"missing independent replay record: {profile}")
        total_compressed_bytes += proof_bytes

    return {
        "status": "VERIFIED",
        "theorem": manifest["theorem"],
        "arithmetic_profiles": arithmetic["profile_count"],
        "arithmetic_eliminations": arithmetic["profile_count"] - len(cases),
        "sat_profiles": len(cases),
        "direct_profiles": len(cases),
        "compressed_proof_bytes": total_compressed_bytes,
    }


def load_and_verify_z10_23_sat_manifest(root: Path) -> dict[str, Any]:
    """Load the repository manifest and verify its complete integrity layer."""

    path = root / "certificates" / "z10_23_sat.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return verify_z10_23_sat_manifest(manifest, root)
