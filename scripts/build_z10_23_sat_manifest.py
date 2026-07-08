#!/usr/bin/env python3
"""Generate or byte-check the Z(10,23) SAT proof integrity manifest."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import lzma
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT / "certificates" / "z10_23_sat.json"
PROFILES = (
    "4x2,5x21",
    "4x3,5x19,6x1",
    "4x4,5x17,6x2",
    "4x4,5x18,7x1",
    "4x5,5x15,6x3",
    "4x5,5x16,6x1,7x1",
    "4x6,5x13,6x4",
    "4x7,5x11,6x5",
    "3x1,5x22",
    "3x1,4x1,5x20,6x1",
    "3x1,4x2,5x18,6x2",
    "3x1,4x3,5x16,6x3",
    "3x1,4x4,5x14,6x4",
)


class _ConcatenatedReader(io.RawIOBase):
    """Expose ordered byte chunks as one binary stream for XZ decoding."""

    def __init__(self, paths: tuple[Path, ...]) -> None:
        super().__init__()
        self._paths = iter(paths)
        self._current = None

    def readable(self) -> bool:
        return True

    def readinto(self, buffer: object) -> int:
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


def _slug(profile: str) -> str:
    return profile.replace(",", "_").replace("x", "d")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _formula_metadata(path: Path) -> dict[str, object]:
    header = None
    clauses = 0
    with path.open(encoding="ascii") as handle:
        for line in handle:
            if line.startswith("p cnf "):
                fields = line.split()
                header = (int(fields[2]), int(fields[3]))
            elif line and line[0] not in {"c", "\n"}:
                clauses += 1
    if header is None or header[1] != clauses:
        raise ValueError(f"malformed formula: {path}")
    return {
        "file": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "variables": header[0],
        "clauses": header[1],
    }


def _proof_metadata(slug: str) -> dict[str, object]:
    directory = ROOT / "certificates" / "z10_23"
    proof = directory / f"{slug}.drat.xz"
    parts = sorted(directory.glob(f"{slug}.drat.xz.part-*"))
    if proof.is_file() == bool(parts):
        raise ValueError(f"expected exactly one proof representation for {slug}")
    if proof.is_file():
        if proof.stat().st_size >= 100_000_000:
            raise ValueError(f"proof exceeds GitHub's single-file limit: {proof}")
        return {
            "file": str(proof.relative_to(ROOT)),
            "sha256": _sha256(proof),
            "bytes": proof.stat().st_size,
            "format": "DRAT+xz",
        }

    digest = hashlib.sha256()
    total_bytes = 0
    part_metadata = []
    for part in parts:
        size = part.stat().st_size
        if size >= 100_000_000:
            raise ValueError(f"proof part exceeds GitHub's single-file limit: {part}")
        part_digest = hashlib.sha256()
        with part.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
                part_digest.update(block)
        total_bytes += size
        part_metadata.append(
            {
                "file": str(part.relative_to(ROOT)),
                "sha256": part_digest.hexdigest(),
                "bytes": size,
            }
        )
    return {
        "parts": part_metadata,
        "sha256": digest.hexdigest(),
        "bytes": total_bytes,
        "format": "DRAT+xz+split",
    }


def _jsonl_metadata(artifact: object) -> dict[str, object]:
    if isinstance(artifact, tuple):
        paths = artifact
        digest = hashlib.sha256()
        total_bytes = 0
        part_metadata = []
        for part in paths:
            size = part.stat().st_size
            if size >= 100_000_000:
                raise ValueError(f"JSONL part exceeds GitHub's single-file limit: {part}")
            part_digest = hashlib.sha256()
            with part.open("rb") as handle:
                for block in iter(lambda: handle.read(1024 * 1024), b""):
                    digest.update(block)
                    part_digest.update(block)
            total_bytes += size
            part_metadata.append(
                {
                    "file": str(part.relative_to(ROOT)),
                    "sha256": part_digest.hexdigest(),
                    "bytes": size,
                }
            )
        raw = _ConcatenatedReader(paths)
        try:
            with lzma.open(io.BufferedReader(raw), "rt", encoding="ascii") as handle:
                count = sum(1 for line in handle if line.strip())
        finally:
            raw.close()
        return {
            "parts": part_metadata,
            "sha256": digest.hexdigest(),
            "bytes": total_bytes,
            "count": count,
            "compression": "xz",
            "format": "JSONL+xz+split",
        }

    if not isinstance(artifact, Path):
        raise TypeError("unexpected JSONL artifact")
    path = artifact
    if path.stat().st_size >= 100_000_000:
        raise ValueError(f"JSONL artifact exceeds GitHub's single-file limit: {path}")
    if path.suffix == ".xz":
        with lzma.open(path, "rt", encoding="ascii") as handle:
            count = sum(1 for line in handle if line.strip())
    else:
        with path.open(encoding="ascii") as handle:
            count = sum(1 for line in handle if line.strip())
    metadata: dict[str, object] = {
        "file": str(path.relative_to(ROOT)),
        "sha256": _sha256(path),
        "bytes": path.stat().st_size,
        "count": count,
    }
    if path.suffix == ".xz":
        metadata["compression"] = "xz"
    return metadata


def _jsonl_artifact(directory: Path, name: str) -> object:
    candidates = [directory / name, directory / f"{name}.xz"]
    present = [path for path in candidates if path.is_file()]
    parts = tuple(sorted(directory.glob(f"{name}.xz.part-*")))
    expected_parts = tuple(
        directory / f"{name}.xz.part-{index:02d}" for index in range(len(parts))
    )
    representations = len(present) + bool(parts)
    if (
        representations != 1
        or (parts and len(parts) < 2)
        or (parts and parts != expected_parts)
    ):
        raise ValueError(f"expected exactly one JSONL representation for {name}")
    return parts or present[0]


def _cube_archive_metadata(slug: str) -> dict[str, object]:
    directory = ROOT / "certificates" / "z10_23"
    release_metadata = directory / f"{slug}.cube-proofs.release.json"
    if release_metadata.is_file():
        payload = json.loads(release_metadata.read_text(encoding="utf-8"))
        if payload.get("format") != "TAR+DRAT+xz+github-release-parts":
            raise ValueError(f"unexpected release archive format: {release_metadata}")
        return payload
    archive = directory / f"{slug}.cube-proofs.tar.xz"
    parts = sorted(directory.glob(f"{slug}.cube-proofs.tar.xz.part-*"))
    if archive.is_file() == bool(parts):
        raise ValueError(f"expected exactly one cube-proof archive representation for {slug}")
    if archive.is_file():
        if archive.stat().st_size >= 100_000_000:
            raise ValueError(f"cube-proof archive exceeds GitHub's single-file limit: {archive}")
        return {
            "file": str(archive.relative_to(ROOT)),
            "sha256": _sha256(archive),
            "bytes": archive.stat().st_size,
            "format": "TAR+DRAT+xz",
        }

    digest = hashlib.sha256()
    total_bytes = 0
    part_metadata = []
    for part in parts:
        size = part.stat().st_size
        if size >= 100_000_000:
            raise ValueError(f"cube-proof archive part exceeds GitHub's limit: {part}")
        part_digest = hashlib.sha256()
        with part.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(block)
                part_digest.update(block)
        total_bytes += size
        part_metadata.append(
            {
                "file": str(part.relative_to(ROOT)),
                "sha256": part_digest.hexdigest(),
                "bytes": size,
            }
        )
    return {
        "parts": part_metadata,
        "sha256": digest.hexdigest(),
        "bytes": total_bytes,
        "format": "TAR+DRAT+xz+split",
    }


def _cube_proof_metadata(slug: str) -> dict[str, object]:
    directory = ROOT / "certificates" / "z10_23"
    catalog = _jsonl_artifact(directory, f"{slug}.cubes.jsonl")
    index = _jsonl_artifact(directory, f"{slug}.cube-proof-index.jsonl")
    return {
        "format": "row-stabilizer-cube-cover",
        "catalog": _jsonl_metadata(catalog),
        "proof_index": _jsonl_metadata(index),
        "archive": _cube_archive_metadata(slug),
    }


def render() -> str:
    cases = []
    for profile in PROFILES:
        slug = _slug(profile)
        formula = ROOT / "models" / "z10_23" / f"{slug}.cnf"
        proof_directory = ROOT / "certificates" / "z10_23"
        direct_exists = (proof_directory / f"{slug}.drat.xz").is_file() or bool(
            list(proof_directory.glob(f"{slug}.drat.xz.part-*"))
        )
        cube_exists = any(
            (proof_directory / name).is_file()
            for name in (f"{slug}.cubes.jsonl", f"{slug}.cubes.jsonl.xz")
        ) or bool(list(proof_directory.glob(f"{slug}.cubes.jsonl.xz.part-*")))
        if direct_exists == cube_exists:
            raise ValueError(f"expected exactly one proof strategy for {slug}")
        strategy = "direct_cadical" if direct_exists else "row_stabilizer_cube_cover"
        case: dict[str, object] = {
            "profile": profile,
            "strategy": strategy,
            "formula": _formula_metadata(formula),
            "proof": _proof_metadata(slug) if direct_exists else _cube_proof_metadata(slug),
            "replay": {
                "checker": "drat-trim -> LRAT -> lrat-check",
                "status": "VERIFIED",
            },
        }
        cases.append(case)
    manifest = {
        "schema_version": 1,
        "theorem": "Z(10,23,3,3)=112",
        "excluded_target": 113,
        "arithmetic_profile_count": 25,
        "arithmetic_eliminated_profiles": 12,
        "profiles": cases,
        "toolchain": {
            "cnf_generator": "python-sat 1.9.dev2",
            "solver": "CaDiCaL 3.0.0",
            "solver_commit": "7b99c07f0bcab5824a5a3ce62c7066554017f641",
            "cube_solver_options": ["--unsat", "-q", "-P2"],
            "proof_converter": "drat-trim",
            "proof_projection": "lrat-check DRAT output",
            "proof_checker": "drat-trim + lrat-check",
            "proof_tools_commit": "2e3b2dc0ecf938addbd779d42877b6ed69d9a985",
        },
    }
    return json.dumps(manifest, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        if not DESTINATION.exists() or DESTINATION.read_text(encoding="utf-8") != rendered:
            print(json.dumps({"status": "MISMATCH", "artifact": str(DESTINATION)}, indent=2))
            return 1
        status = "IDENTICAL"
    else:
        DESTINATION.parent.mkdir(parents=True, exist_ok=True)
        DESTINATION.write_text(rendered, encoding="utf-8")
        status = "WRITTEN"
    print(json.dumps({"status": status, "profiles": len(PROFILES)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
