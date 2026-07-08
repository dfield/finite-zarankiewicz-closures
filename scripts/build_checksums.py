#!/usr/bin/env python3
"""Build or verify the deterministic artifact checksum list."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "artifacts.sha256"
PATTERNS = (
    "analysis/*.csv",
    "analysis/*.json",
    "audit/*.json",
    "audit/*.txt",
    "certificates/*.drat",
    "certificates/*.json",
    "certificates/*.lrat",
    "certificates/z10_23/*.drat.xz",
    "certificates/z10_23/*.drat.xz.part-*",
    "certificates/z10_23/*.cubes.jsonl",
    "certificates/z10_23/*.cubes.jsonl.xz",
    "certificates/z10_23/*.cubes.jsonl.xz.part-*",
    "certificates/z10_23/*.cube-proof-index.jsonl",
    "certificates/z10_23/*.cube-proof-index.jsonl.xz",
    "certificates/z10_23/*.cube-proof-index.jsonl.xz.part-*",
    "certificates/z10_23/*.cube-proofs.release.json",
    "certificates/z10_23/*.cube-proofs.tar.xz",
    "certificates/z10_23/*.cube-proofs.tar.xz.part-*",
    "data/*.csv",
    "models/*.cnf",
    "models/*.json",
    "models/*.lp",
    "models/z10_23/*.cnf",
)


def sha256(path: Path) -> str:
    """Hash one artifact without reading a potentially large trace at once."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render() -> str:
    """Return a sorted SHA-256 manifest using repository-relative paths."""

    paths = sorted({path for pattern in PATTERNS for path in ROOT.glob(pattern) if path.is_file()})
    return "".join(
        f"{sha256(path)}  {path.relative_to(ROOT).as_posix()}\n"
        for path in paths
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="ascii") != expected:
            print("artifact checksum manifest is stale")
            return 1
        print(f"VERIFIED: {len(expected.splitlines())} artifact checksums")
        return 0
    OUTPUT.write_text(expected, encoding="ascii")
    print(f"WROTE: {len(expected.splitlines())} artifact checksums")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
