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
import io
from itertools import zip_longest
import json
import lzma
from pathlib import Path
import re
from typing import Any, Iterator, Mapping

from .cube_cover import CubeCoverError, verify_cube_catalog
from .extended import z10_23_profile_report
from .vipr_certificate import ViprCertificateError, verify_vipr_cover


class SatCertificateError(ValueError):
    """Raised when the stored SAT manifest or an artifact fails integrity checks."""


_CUBE_RELEASE_REPOSITORY = "dfield/finite-zarankiewicz-closures"
_CUBE_RELEASE_TAG = "z10-23-certificate-v1"


class _ConcatenatedReader(io.RawIOBase):
    """Expose ordered byte chunks as one non-seekable binary stream."""

    def __init__(self, paths: list[Path]) -> None:
        super().__init__()
        self._paths = iter(paths)
        self._current = None

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: Any) -> int:
        view = memoryview(buffer).cast("B")
        written = 0
        while written < len(view):
            if self._current is None:
                try:
                    self._current = next(self._paths).open("rb")
                except StopIteration:
                    break
            count = self._current.readinto(view[written:])
            if count:
                written += count
                continue
            self._current.close()
            self._current = None
        return written

    def close(self) -> None:
        if self._current is not None:
            self._current.close()
            self._current = None
        super().close()


def _canonical_numbered_parts(names: list[Any], marker: str) -> bool:
    """Recognize one fixed-width, contiguous ``part-N`` filename sequence."""

    matches = [
        re.fullmatch(rf"(.+{re.escape(marker)})([0-9]+)", name)
        if isinstance(name, str)
        else None
        for name in names
    ]
    bases = {match.group(1) for match in matches if match is not None}
    widths = {len(match.group(2)) for match in matches if match is not None}
    indexes = [int(match.group(2)) for match in matches if match is not None]
    return (
        bool(names)
        and all(match is not None for match in matches)
        and len(bases) == 1
        and len(widths) == 1
        and next(iter(widths), 0) >= 2
        and indexes == list(range(len(names)))
    )


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
        or not _canonical_numbered_parts(relative_names, ".drat.xz.part-")
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
            or not _canonical_numbered_parts(
                names, ".cube-proofs.tar.xz.part-"
            )
            or any(
                ".cube-proofs.tar.xz.part-" not in name or "/" in name or "\\" in name
                for name in names
                if isinstance(name, str)
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
        or not _canonical_numbered_parts(
            names, ".cube-proofs.tar.xz.part-"
        )
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


def _check_jsonl_parts(
    root: Path,
    payload: Mapping[str, Any],
    label: str,
) -> list[Path]:
    """Verify one ordered split XZ stream and return its local part paths."""

    parts = payload.get("parts")
    if (
        payload.get("compression") != "xz"
        or payload.get("format") != "JSONL+xz+split"
        or not isinstance(parts, list)
        or len(parts) < 2
    ):
        raise SatCertificateError(f"invalid split {label} metadata")
    names = [part.get("file") for part in parts if isinstance(part, dict)]
    if (
        len(names) != len(parts)
        or not _canonical_numbered_parts(names, ".jsonl.xz.part-")
    ):
        raise SatCertificateError(f"split {label} parts are not in canonical order")
    digest = hashlib.sha256()
    total_bytes = 0
    paths = []
    for part in parts:
        path, expected_hash = _resolve_artifact(root, part)
        if ".jsonl.xz.part-" not in path.name or path.stat().st_size >= 100_000_000:
            raise SatCertificateError(f"unexpected split {label} part: {path}")
        part_digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
                part_digest.update(block)
        if part_digest.hexdigest() != expected_hash:
            raise SatCertificateError(f"SAT artifact hash mismatch: {part['file']}")
        total_bytes += path.stat().st_size
        paths.append(path)
    if digest.hexdigest() != payload.get("sha256"):
        raise SatCertificateError(f"reassembled split {label} hash mismatch")
    if total_bytes != payload.get("bytes"):
        raise SatCertificateError(f"reassembled split {label} size mismatch")
    return paths


def _iter_jsonl(
    root: Path,
    payload: Mapping[str, Any],
    label: str,
) -> Iterator[Mapping[str, Any]]:
    """Yield hash-checked JSONL objects while enforcing the declared count."""

    split_paths = None
    if "parts" in payload:
        split_paths = _check_jsonl_parts(root, payload, label)
        path = split_paths[0]
    else:
        path = _check_hashed_file(root, payload)
    count = 0
    raw = None
    try:
        compression = payload.get("compression")
        if split_paths is not None:
            raw = _ConcatenatedReader(split_paths)
            handle = lzma.open(io.BufferedReader(raw), "rt", encoding="ascii")
        elif compression is None:
            if not path.name.endswith(".jsonl"):
                raise SatCertificateError(f"uncompressed {label} lacks a .jsonl name: {path}")
            handle = path.open(encoding="ascii")
        elif compression == "xz":
            if not path.name.endswith(".jsonl.xz"):
                raise SatCertificateError(f"compressed {label} lacks a .jsonl.xz name: {path}")
            handle = lzma.open(path, "rt", encoding="ascii")
        else:
            raise SatCertificateError(f"unexpected {label} compression: {compression}")
        with handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                record = json.loads(line)
                if not isinstance(record, dict):
                    raise SatCertificateError(
                        f"{label} record is not an object: {path}:{line_number}"
                    )
                count += 1
                yield record
    except (UnicodeDecodeError, json.JSONDecodeError, lzma.LZMAError) as error:
        raise SatCertificateError(f"malformed {label}: {path}") from error
    finally:
        if raw is not None:
            raw.close()
    if payload.get("count") != count:
        raise SatCertificateError(f"{label} count mismatch: {path}")


def _load_jsonl(root: Path, payload: Mapping[str, Any], label: str) -> list[Mapping[str, Any]]:
    """Load a small JSONL artifact; large proof paths use ``_iter_jsonl``."""

    return list(_iter_jsonl(root, payload, label))


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
    catalog_count = catalog_payload.get("count")
    index_count = index_payload.get("count")
    if (
        not isinstance(catalog_count, int)
        or catalog_count <= 0
        or index_count != catalog_count
    ):
        raise SatCertificateError(f"cube proof count differs from catalog for {profile}")
    hex_digest = re.compile(r"[0-9a-f]{64}")
    missing = object()

    def checked_catalog() -> Iterator[Mapping[str, Any]]:
        catalog = _iter_jsonl(root, catalog_payload, "cube catalog")
        index = _iter_jsonl(root, index_payload, "cube proof index")
        for position, pair in enumerate(zip_longest(catalog, index, fillvalue=missing)):
            leaf, proof = pair
            if leaf is missing or proof is missing:
                raise SatCertificateError(
                    f"cube proof count differs from catalog for {profile}"
                )
            if not isinstance(leaf, Mapping) or not isinstance(proof, Mapping):
                raise SatCertificateError(
                    f"invalid cube proof record for {profile} leaf {position}"
                )
            expected_file = f"proofs/leaf-{position:08d}.drat"
            if (
                proof.get("index") != position
                or proof.get("masks") != leaf.get("masks")
                or proof.get("literals", []) != leaf.get("literals", [])
            ):
                raise SatCertificateError(
                    f"cube proof index mismatch for {profile} leaf {position}"
                )
            if proof.get("file") != expected_file:
                raise SatCertificateError(
                    f"noncanonical cube proof name for {profile} leaf {position}"
                )
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
                raise SatCertificateError(
                    f"invalid cube proof record for {profile} leaf {position}"
                )
            yield leaf

    try:
        cover_report = verify_cube_catalog(profile, checked_catalog())
    except CubeCoverError as error:
        raise SatCertificateError(f"invalid cube cover for {profile}: {error}") from error
    archive_bytes = _check_cube_archive(root, archive_payload)
    return archive_bytes, cover_report


def _check_vipr_proof(
    root: Path,
    profile: str,
    payload: Mapping[str, Any],
) -> tuple[int, dict[str, Any]]:
    """Check local descriptors and deeply audit one exact SCIP/VIPR orbit cover."""

    if payload.get("format") != "exact-scip-vipr-orbit-cover":
        raise SatCertificateError(f"unexpected VIPR-cover format for {profile}")
    descriptors = {
        "cover_manifest": ".json",
        "catalog": ".jsonl",
        "catalog_metadata": ".json",
        "release_sidecar": ".release.json",
    }
    paths = {}
    for field, suffix in descriptors.items():
        descriptor = payload.get(field)
        if not isinstance(descriptor, dict):
            raise SatCertificateError(f"missing {field} for VIPR profile {profile}")
        path = _check_hashed_file(root, descriptor)
        if not path.name.endswith(suffix):
            raise SatCertificateError(f"unexpected {field} name for VIPR profile {profile}")
        paths[field] = path
    archive = payload.get("archive")
    if not isinstance(archive, dict):
        raise SatCertificateError(f"missing release archive for VIPR profile {profile}")
    sidecar = json.loads(paths["release_sidecar"].read_text(encoding="ascii"))
    if archive != sidecar:
        raise SatCertificateError(f"VIPR release sidecar differs from the SAT manifest: {profile}")
    try:
        report = verify_vipr_cover(root, profile)
    except ViprCertificateError as error:
        raise SatCertificateError(f"invalid VIPR cover for {profile}: {error}") from error
    return int(report["release_bytes"]), report


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
        "sat": {
            "cnf_generator": "python-sat 1.9.dev2",
            "solver": "CaDiCaL 3.0.0",
            "solver_commit": "7b99c07f0bcab5824a5a3ce62c7066554017f641",
            "cube_solver_options": ["--unsat", "-q", "-P2"],
            "proof_converter": "drat-trim",
            "proof_projection": "lrat-check DRAT output",
            "proof_checker": "drat-trim + lrat-check",
            "proof_tools_commit": "2e3b2dc0ecf938addbd779d42877b6ed69d9a985",
        },
        "vipr": {
            "solver": "SCIP 10.0.3 exact mode",
            "solver_git_hash": "d409edf9f6",
            "scip_archive_sha256": "ddbb7129bdb83f8f70ed26391d206fd1658139e44c7c7fd7d73a1e4cefbca94f",
            "proof_checker": "viprchk",
            "vipr_source_commit": "30f2951d1e90e47afa821bdd1b12b82246656c42",
            "vipr_source_sha256": "7d20cd04ba11488fbc8ed3fbabfdfa513e161a0c36b75220927f55051614ed2f",
        },
    }:
        raise SatCertificateError("unexpected Z(10,23) proof toolchain metadata")

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
    vipr_profiles = 0
    vipr_orbits = 0
    vipr_raw_states = 0
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
        elif strategy == "scip_vipr_orbit_cover":
            proof_bytes, cover_report = _check_vipr_proof(root, profile, proof_payload)
            vipr_profiles += 1
            vipr_orbits += int(cover_report["orbits"])
            vipr_raw_states += int(cover_report["raw_states"])
        else:
            raise SatCertificateError(f"unexpected SAT strategy for {profile}")
        expected_replay = {
            "checker": (
                "viprchk + regenerated-OPB model binding"
                if strategy == "scip_vipr_orbit_cover"
                else "drat-trim -> LRAT -> lrat-check"
            ),
            "status": "VERIFIED",
        }
        if case.get("replay") != expected_replay:
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
        "vipr_cover_profiles": vipr_profiles,
        "vipr_orbits": vipr_orbits,
        "vipr_raw_states": vipr_raw_states,
        "compressed_proof_bytes": total_compressed_bytes,
    }


def load_and_verify_z10_23_sat_manifest(root: Path) -> dict[str, Any]:
    """Load the repository manifest and verify its complete integrity layer."""

    path = root / "certificates" / "z10_23_sat.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    return verify_z10_23_sat_manifest(manifest, root)
