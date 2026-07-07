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
import re
from typing import Any, Mapping

from .cube_cover import CubeCoverError, verify_cube_catalog
from .extended import z10_23_profile_report


class SatCertificateError(ValueError):
    """Raised when the stored SAT manifest or an artifact fails integrity checks."""


_CUBE_RELEASE_REPOSITORY = "dfield/finite-zarankiewicz-closures"
_CUBE_RELEASE_TAG = "z10-23-certificate-v1"


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


def _check_cube_archive(root: Path, payload: Mapping[str, Any]) -> int:
    """Check one direct or byte-split tar/xz archive of cube-leaf proofs."""

    proof_format = payload.get("format")
    if proof_format == "TAR+DRAT+xz+github-release-parts":
        release = payload.get("release")
        parts = payload.get("parts")
        if payload.get("compression") != {
            "archive": "deterministic PAX tar",
            "xz_options": ["-T8", "-3"],
            "xz_version": "xz (XZ Utils) 5.4.1",
        }:
            raise SatCertificateError("unexpected cube-proof release compression")
        if release != {
            "repository": _CUBE_RELEASE_REPOSITORY,
            "tag": _CUBE_RELEASE_TAG,
        }:
            raise SatCertificateError("unexpected cube-proof release location")
        if not isinstance(parts, list) or not parts:
            raise SatCertificateError("release-backed cube proof has no parts")
        names = [part.get("name") for part in parts if isinstance(part, dict)]
        if (
            len(names) != len(parts)
            or not all(isinstance(name, str) for name in names)
            or names != sorted(names)
            or any(
                ".cube-proofs.tar.xz.part-" not in name or "/" in name or "\\" in name
                for name in names
            )
        ):
            raise SatCertificateError("release-backed cube-proof parts are not canonical")
        hex_digest = re.compile(r"[0-9a-f]{64}")
        total_bytes = 0
        for part in parts:
            size = part.get("bytes")
            digest = part.get("sha256")
            if (
                not isinstance(size, int)
                or not 0 < size < 2_000_000_000
                or not isinstance(digest, str)
                or hex_digest.fullmatch(digest) is None
            ):
                raise SatCertificateError("invalid release-backed cube-proof part")
            total_bytes += size
        if (
            payload.get("bytes") != total_bytes
            or not isinstance(payload.get("sha256"), str)
            or hex_digest.fullmatch(payload["sha256"]) is None
        ):
            raise SatCertificateError("invalid release-backed cube-proof stream metadata")
        return total_bytes
    if proof_format == "TAR+DRAT+xz":
        path = _check_hashed_file(root, payload)
        if not path.name.endswith(".cube-proofs.tar.xz") or path.stat().st_size >= 100_000_000:
            raise SatCertificateError(f"unexpected cube-proof archive: {path}")
        return path.stat().st_size
    if proof_format != "TAR+DRAT+xz+split":
        raise SatCertificateError("unexpected cube-proof archive format")

    parts = payload.get("parts")
    if not isinstance(parts, list) or len(parts) < 2:
        raise SatCertificateError("split cube-proof archive must contain at least two parts")
    names = [part.get("file") for part in parts if isinstance(part, dict)]
    if (
        len(names) != len(parts)
        or not all(isinstance(name, str) for name in names)
        or names != sorted(names)
    ):
        raise SatCertificateError("cube-proof archive parts are not in canonical order")
    digest = hashlib.sha256()
    total_bytes = 0
    for part in parts:
        path, expected_hash = _resolve_artifact(root, part)
        if ".cube-proofs.tar.xz.part-" not in path.name or path.stat().st_size >= 100_000_000:
            raise SatCertificateError(f"unexpected cube-proof archive part: {path}")
        part_digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
                part_digest.update(block)
        if part_digest.hexdigest() != expected_hash:
            raise SatCertificateError(f"SAT artifact hash mismatch: {part['file']}")
        total_bytes += path.stat().st_size
    if digest.hexdigest() != payload.get("sha256"):
        raise SatCertificateError("reassembled cube-proof archive hash mismatch")
    if total_bytes != payload.get("bytes"):
        raise SatCertificateError("reassembled cube-proof archive size mismatch")
    return total_bytes


def _load_jsonl(root: Path, payload: Mapping[str, Any], label: str) -> list[Mapping[str, Any]]:
    path = _check_hashed_file(root, payload)
    records: list[Mapping[str, Any]] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="ascii").splitlines(), start=1):
            record = json.loads(line)
            if not isinstance(record, dict):
                raise SatCertificateError(f"{label} record is not an object: {path}:{line_number}")
            records.append(record)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise SatCertificateError(f"malformed {label}: {path}") from error
    if payload.get("count") != len(records):
        raise SatCertificateError(f"{label} count mismatch: {path}")
    return records


def _check_cube_proof(
    root: Path,
    profile: str,
    payload: Mapping[str, Any],
) -> tuple[int, dict[str, Any]]:
    """Check a complete canonical cover and its hash-bound leaf proof index."""

    if payload.get("format") != "row-stabilizer-cube-cover":
        raise SatCertificateError(f"unexpected cube-cover format for {profile}")
    catalog_payload = payload.get("catalog")
    index_payload = payload.get("proof_index")
    archive_payload = payload.get("archive")
    if not all(isinstance(item, dict) for item in (catalog_payload, index_payload, archive_payload)):
        raise SatCertificateError(f"incomplete cube-cover metadata for {profile}")
    catalog = _load_jsonl(root, catalog_payload, "cube catalog")
    try:
        cover_report = verify_cube_catalog(profile, catalog)
    except CubeCoverError as error:
        raise SatCertificateError(f"invalid cube cover for {profile}: {error}") from error
    index = _load_jsonl(root, index_payload, "cube proof index")
    if len(index) != len(catalog):
        raise SatCertificateError(f"cube proof count differs from catalog for {profile}")
    hex_digest = re.compile(r"[0-9a-f]{64}")
    for position, (leaf, proof) in enumerate(zip(catalog, index)):
        expected_file = f"proofs/leaf-{position:08d}.drat"
        if (
            proof.get("index") != position
            or proof.get("masks") != leaf.get("masks")
            or proof.get("literals", []) != leaf.get("literals", [])
        ):
            raise SatCertificateError(f"cube proof index mismatch for {profile} leaf {position}")
        if proof.get("file") != expected_file:
            raise SatCertificateError(f"noncanonical cube proof name for {profile} leaf {position}")
        if (
            not isinstance(proof.get("bytes"), int)
            or proof["bytes"] <= 0
            or not isinstance(proof.get("sha256"), str)
            or hex_digest.fullmatch(proof["sha256"]) is None
            or proof.get("status") != "VERIFIED"
            or proof.get("solver_options") != ["--unsat", "-q", "-P2"]
            or proof.get("replay")
            != "drat-trim -> LRAT -> lrat-check; projected DRAT -> drat-trim"
        ):
            raise SatCertificateError(f"invalid cube proof record for {profile} leaf {position}")
    archive_bytes = _check_cube_archive(root, archive_payload)
    return archive_bytes, cover_report


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
        "cube_solver_options": ["--unsat", "-q", "-P2"],
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
    direct_profiles = 0
    cube_profiles = 0
    cube_leaves = 0
    for case in cases:
        profile = case["profile"]
        formula_payload = case.get("formula")
        proof_payload = case.get("proof")
        if not isinstance(formula_payload, dict) or not isinstance(proof_payload, dict):
            raise SatCertificateError(f"incomplete SAT artifact metadata: {profile}")
        formula_path = _check_hashed_file(root, formula_payload)
        _check_dimacs(formula_path, formula_payload)
        strategy = case.get("strategy")
        if strategy == "direct_cadical":
            proof_bytes = _check_proof_artifact(root, proof_payload)
            direct_profiles += 1
        elif strategy == "row_stabilizer_cube_cover":
            proof_bytes, cover_report = _check_cube_proof(root, profile, proof_payload)
            cube_profiles += 1
            cube_leaves += cover_report["leaf_count"]
        else:
            raise SatCertificateError(f"unexpected SAT strategy for {profile}")
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
        "direct_profiles": direct_profiles,
        "cube_cover_profiles": cube_profiles,
        "cube_leaves": cube_leaves,
        "compressed_proof_bytes": total_compressed_bytes,
    }


def load_and_verify_z10_23_sat_manifest(root: Path) -> dict[str, Any]:
    """Load the repository manifest and verify its complete integrity layer."""

    path = root / "certificates" / "z10_23_sat.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return verify_z10_23_sat_manifest(manifest, root)
