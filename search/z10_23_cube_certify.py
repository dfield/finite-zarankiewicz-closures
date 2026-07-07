#!/usr/bin/env python3
"""Produce replayable proof cores for a complete Z(10,23) cube catalog.

The companion ``z10_23_certify.py cubes`` command creates a deterministic
canonical-prefix cover.  This command treats that catalog as untrusted,
rechecks its completeness with the standard-library verifier, materializes
each leaf as the base CNF plus unit clauses, and runs

``CaDiCaL -> drat-trim -> LRAT -> lrat-check -> compact DRAT -> drat-trim``.

It stores the compact leaf cores in a deterministic tar/xz archive, splitting
the compressed byte stream below GitHub's 100 MB per-file limit when needed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import lzma
import multiprocessing
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from typing import Any, Optional


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.cube_cover import verify_cube_catalog  # noqa: E402
from search.z10_23_certify import (  # noqa: E402
    PROOF_PART_BYTES,
    SAT_PROFILES,
    build_profile_formula,
    canonical_profile,
    profile_slug,
)


ROWS = 10
COLUMNS = 23
_BASE_HEADER: tuple[int, int] | None = None
_BASE_BODY = b""
_PROOFS: Path | None = None
_CHECKPOINTS: Path | None = None
_TOOLS: dict[str, str] = {}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _proof_tools() -> dict[str, str]:
    tools = {name: shutil.which(name) for name in ("cadical", "drat-trim", "lrat-check")}
    missing = [name for name, path in tools.items() if path is None]
    if missing:
        raise RuntimeError(f"missing external tools: {', '.join(missing)}")
    return {name: str(path) for name, path in tools.items() if path is not None}


def _initialize(cnf_path: str, work: str, tools: dict[str, str]) -> None:
    global _BASE_HEADER, _BASE_BODY, _PROOFS, _CHECKPOINTS, _TOOLS
    raw = Path(cnf_path).read_bytes()
    header, separator, body = raw.partition(b"\n")
    fields = header.split()
    if not separator or fields[:2] != [b"p", b"cnf"] or len(fields) != 4:
        raise RuntimeError("malformed base DIMACS header")
    _BASE_HEADER = (int(fields[2]), int(fields[3]))
    _BASE_BODY = body
    root = Path(work)
    _PROOFS = root / "proofs"
    _CHECKPOINTS = root / "checkpoints"
    _TOOLS = tools


def _run(command: list[str], accepted: tuple[int, ...] = (0,)) -> str:
    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        text=True,
    )
    if completed.returncode not in accepted:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            + completed.stdout[-4000:]
        )
    return completed.stdout


def _units(masks: list[int]) -> list[int]:
    return [
        row * COLUMNS + column + 1
        if mask & (1 << row)
        else -(row * COLUMNS + column + 1)
        for column, mask in enumerate(masks)
        for row in range(ROWS)
    ]


def _prove_leaf(task: tuple[int, list[int]]) -> dict[str, Any]:
    if _BASE_HEADER is None or _PROOFS is None or _CHECKPOINTS is None:
        raise RuntimeError("proof worker was not initialized")
    index, masks = task
    name = f"leaf-{index:08d}.drat"
    destination = _PROOFS / name
    checkpoint = _CHECKPOINTS / f"leaf-{index:08d}.json"
    if destination.is_file() and checkpoint.is_file():
        record = json.loads(checkpoint.read_text(encoding="ascii"))
        if (
            record.get("index") == index
            and record.get("masks") == masks
            and record.get("bytes") == destination.stat().st_size
            and record.get("sha256") == _sha256(destination)
        ):
            return record

    variables, clauses = _BASE_HEADER
    units = _units(masks)
    with tempfile.TemporaryDirectory(prefix=f"z10_23_leaf_{index:08d}_") as directory:
        temporary = Path(directory)
        formula = temporary / "leaf.cnf"
        raw = temporary / "raw.drat"
        lrat = temporary / "proof.lrat"
        core = temporary / "core.drat"
        with formula.open("wb") as handle:
            handle.write(f"p cnf {variables} {clauses + len(units)}\n".encode())
            handle.write(_BASE_BODY)
            for literal in units:
                handle.write(f"{literal} 0\n".encode())
        _run([_TOOLS["cadical"], "--unsat", "-q", str(formula), str(raw)], (0, 20))
        drat_output = _run(
            [_TOOLS["drat-trim"], str(formula), str(raw), "-L", str(lrat)]
        )
        if "VERIFIED" not in drat_output:
            raise RuntimeError(f"drat-trim did not verify leaf {index}")
        lrat_output = _run(
            [_TOOLS["lrat-check"], str(formula), str(lrat), str(core)]
        )
        if "VERIFIED" not in lrat_output:
            raise RuntimeError(f"lrat-check did not verify leaf {index}")
        core_output = _run([_TOOLS["drat-trim"], str(formula), str(core)])
        if "VERIFIED" not in core_output:
            raise RuntimeError(f"projected DRAT did not verify leaf {index}")
        os.replace(core, destination)

    record: dict[str, Any] = {
        "index": index,
        "masks": masks,
        "file": f"proofs/{name}",
        "bytes": destination.stat().st_size,
        "sha256": _sha256(destination),
        "replay": "drat-trim -> LRAT -> lrat-check; projected DRAT -> drat-trim",
        "status": "VERIFIED",
    }
    staged = checkpoint.with_suffix(".tmp")
    staged.write_text(json.dumps(record, sort_keys=True) + "\n", encoding="ascii")
    os.replace(staged, checkpoint)
    return record


def _archive(proofs: Path, destination: Path) -> tuple[dict[str, Any], int]:
    uncompressed_bytes = 0
    with lzma.open(
        destination,
        "wb",
        format=lzma.FORMAT_XZ,
        preset=9 | lzma.PRESET_EXTREME,
    ) as compressed:
        with tarfile.open(fileobj=compressed, mode="w|", format=tarfile.PAX_FORMAT) as archive:
            for path in sorted(proofs.glob("leaf-*.drat")):
                info = tarfile.TarInfo(f"proofs/{path.name}")
                info.size = path.stat().st_size
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                uncompressed_bytes += info.size
                with path.open("rb") as handle:
                    archive.addfile(info, handle)
    compressed_bytes = destination.stat().st_size
    compressed_sha256 = _sha256(destination)
    if compressed_bytes < 100_000_000:
        return {
            "file": destination.name,
            "sha256": compressed_sha256,
            "bytes": compressed_bytes,
            "format": "TAR+DRAT+xz",
        }, uncompressed_bytes

    parts = []
    with destination.open("rb") as source:
        part_index = 0
        while source.tell() < compressed_bytes:
            part = destination.with_name(f"{destination.name}.part-{part_index:02d}")
            remaining = PROOF_PART_BYTES
            with part.open("wb") as output:
                while remaining:
                    block = source.read(min(1024 * 1024, remaining))
                    if not block:
                        break
                    output.write(block)
                    remaining -= len(block)
            parts.append(
                {"file": part.name, "sha256": _sha256(part), "bytes": part.stat().st_size}
            )
            part_index += 1
    destination.unlink()
    return {
        "parts": parts,
        "sha256": compressed_sha256,
        "bytes": compressed_bytes,
        "format": "TAR+DRAT+xz+split",
    }, uncompressed_bytes


def certify(profile: str, catalog_path: Path, output: Path, workers: int) -> dict[str, Any]:
    canonical = canonical_profile(profile)
    if canonical not in SAT_PROFILES:
        raise ValueError(f"profile is outside the thirteen-case scope: {canonical}")
    output.mkdir(parents=True, exist_ok=True)
    work = output / f".{profile_slug(canonical)}.cube-work"
    (work / "proofs").mkdir(parents=True, exist_ok=True)
    (work / "checkpoints").mkdir(exist_ok=True)
    slug = profile_slug(canonical)
    formula = output / f"{slug}.cnf"
    cnf, _, degrees = build_profile_formula(canonical)
    cnf.to_file(str(formula))
    catalog = [json.loads(line) for line in catalog_path.read_text(encoding="ascii").splitlines()]
    cover_report = verify_cube_catalog(canonical, catalog)
    tasks = [(index, leaf["masks"]) for index, leaf in enumerate(catalog)]
    tools = _proof_tools()
    records: dict[int, dict[str, Any]] = {}
    started = time.monotonic()
    with multiprocessing.Pool(
        processes=workers,
        initializer=_initialize,
        initargs=(str(formula), str(work), tools),
    ) as pool:
        for record in pool.imap_unordered(_prove_leaf, tasks):
            records[int(record["index"])] = record
            if len(records) % 100 == 0 or len(records) == len(tasks):
                print(
                    json.dumps(
                        {"completed": len(records), "total": len(tasks)}, sort_keys=True
                    ),
                    flush=True,
                )

    stored_catalog = output / f"{slug}.cubes.jsonl"
    shutil.copyfile(catalog_path, stored_catalog)
    proof_index = output / f"{slug}.cube-proof-index.jsonl"
    with proof_index.open("w", encoding="ascii") as handle:
        for index in range(len(records)):
            handle.write(
                json.dumps(records[index], sort_keys=True, separators=(",", ":")) + "\n"
            )
    archive_path = output / f"{slug}.cube-proofs.tar.xz"
    archive, uncompressed_bytes = _archive(work / "proofs", archive_path)
    metadata = {
        "schema_version": 1,
        "profile": canonical,
        "column_order": degrees,
        "strategy": "row_stabilizer_cube_cover",
        "formula": {
            "file": formula.name,
            "sha256": _sha256(formula),
            "variables": cnf.nv,
            "clauses": len(cnf.clauses),
        },
        "catalog": {
            "file": stored_catalog.name,
            "sha256": _sha256(stored_catalog),
            "bytes": stored_catalog.stat().st_size,
            "count": len(catalog),
            "completeness": cover_report,
        },
        "proof_index": {
            "file": proof_index.name,
            "sha256": _sha256(proof_index),
            "bytes": proof_index.stat().st_size,
            "count": len(records),
        },
        "archive": archive,
        "uncompressed_proof_bytes": uncompressed_bytes,
        "replay": {
            "every_leaf": "drat-trim -> LRAT -> lrat-check",
            "projected_core": "drat-trim VERIFIED",
        },
        "toolchain": {
            "cadical_version": _run([tools["cadical"], "--version"]).strip(),
            "proof_converter": "drat-trim",
            "proof_checker": "lrat-check + drat-trim",
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    (output / f"{slug}.cube.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    shutil.rmtree(work)
    return metadata


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args(argv)
    if args.workers <= 0:
        parser.error("--workers must be positive")
    result = certify(
        args.profile,
        args.catalog.resolve(),
        args.output.resolve(),
        args.workers,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
