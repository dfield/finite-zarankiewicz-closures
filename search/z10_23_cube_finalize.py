#!/usr/bin/env python3
"""Validate and index a complete distributed Z(10,23) cube-proof workspace."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.cube_cover import verify_cube_catalog  # noqa: E402
from search.z10_23_certify import SAT_PROFILES, canonical_profile  # noqa: E402


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def finalize(profile: str, catalog: Path, work: Path, formula: Path) -> dict[str, object]:
    canonical = canonical_profile(profile)
    if canonical not in SAT_PROFILES:
        raise ValueError(f"profile is outside the thirteen-case scope: {canonical}")
    leaves = [json.loads(line) for line in catalog.read_text(encoding="ascii").splitlines()]
    cover_report = verify_cube_catalog(canonical, leaves)
    records = []
    for index, leaf in enumerate(leaves):
        checkpoint = work / "checkpoints" / f"leaf-{index:08d}.json"
        proof = work / "proofs" / f"leaf-{index:08d}.drat"
        if not checkpoint.is_file() or not proof.is_file():
            raise RuntimeError(f"missing proof leaf {index}")
        record = json.loads(checkpoint.read_text(encoding="ascii"))
        if (
            record.get("index") != index
            or record.get("masks") != leaf.get("masks")
            or record.get("literals", []) != leaf.get("literals", [])
            or record.get("file") != f"proofs/leaf-{index:08d}.drat"
            or record.get("bytes") != proof.stat().st_size
            or record.get("sha256") != sha256(proof)
            or record.get("status") != "VERIFIED"
            or record.get("solver_options") != ["--unsat", "-q", "-P2"]
            or record.get("replay")
            != "drat-trim -> LRAT -> lrat-check; projected DRAT -> drat-trim"
        ):
            raise RuntimeError(f"invalid proof leaf {index}")
        records.append(record)

    expected_names = {f"leaf-{index:08d}" for index in range(len(leaves))}
    proof_names = {path.stem for path in (work / "proofs").glob("leaf-*.drat")}
    checkpoint_names = {
        path.stem for path in (work / "checkpoints").glob("leaf-*.json")
    }
    if proof_names != expected_names or checkpoint_names != expected_names:
        raise RuntimeError("proof workspace contains missing or extra leaves")

    stored_catalog = work / "cubes.jsonl"
    if catalog.resolve() != stored_catalog.resolve():
        shutil.copyfile(catalog, stored_catalog)
    index_path = work / "proof-index.jsonl"
    with index_path.open("w", encoding="ascii") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

    header = formula.read_bytes().splitlines()[0].split()
    if header[:2] != [b"p", b"cnf"] or len(header) != 4:
        raise RuntimeError("malformed base formula")
    metadata: dict[str, object] = {
        "schema_version": 1,
        "status": "VERIFIED_CUBE_LEAF_PROOFS",
        "profile": canonical,
        "formula": {
            "file": formula.name,
            "bytes": formula.stat().st_size,
            "sha256": sha256(formula),
            "variables": int(header[2]),
            "clauses": int(header[3]),
        },
        "catalog": {
            "file": stored_catalog.name,
            "count": len(leaves),
            "bytes": stored_catalog.stat().st_size,
            "sha256": sha256(stored_catalog),
            "completeness": cover_report,
        },
        "proof_index": {
            "file": index_path.name,
            "count": len(records),
            "bytes": index_path.stat().st_size,
            "sha256": sha256(index_path),
        },
        "proofs": {
            "count": len(records),
            "bytes": sum(int(record["bytes"]) for record in records),
            "verification": "every leaf independently DRAT/LRAT replayed",
        },
        "toolchain": {
            "solver": subprocess.run(
                ["cadical", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            ).stdout.strip(),
            "solver_options": ["--unsat", "-q", "-P2"],
            "proof_converter": "drat-trim",
            "proof_checker": "lrat-check + drat-trim",
        },
    }
    (work / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--formula", type=Path, required=True)
    args = parser.parse_args()
    result = finalize(
        args.profile,
        args.catalog.resolve(),
        args.work.resolve(),
        args.formula.resolve(),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
