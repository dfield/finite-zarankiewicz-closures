#!/usr/bin/env python3
"""Fetch and hash-check every release-backed Z(10,23) proof archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATES = ROOT / "certificates" / "z10_23"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "build" / "z10_23_assets")
    args = parser.parse_args()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    sidecars = sorted(CERTIFICATES.glob("*.cube-proofs.release.json"))
    sidecars.extend(sorted((CERTIFICATES / "vipr").glob("*.vipr-certificates.release.json")))
    if not sidecars:
        raise RuntimeError("no release-backed proof metadata is present")
    gh = shutil.which("gh")
    if gh is None:
        raise RuntimeError("GitHub CLI (gh) is required")

    fetched = []
    for sidecar in sidecars:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        release = metadata["release"]
        for part in metadata["parts"]:
            destination = output / part["name"]
            if (
                destination.is_file()
                and destination.stat().st_size == part["bytes"]
                and sha256(destination) == part["sha256"]
            ):
                status = "REUSED"
            else:
                completed = subprocess.run(
                    [
                        gh,
                        "release",
                        "download",
                        release["tag"],
                        "--repo",
                        release["repository"],
                        "--pattern",
                        part["name"],
                        "--dir",
                        str(output),
                        "--clobber",
                    ],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                if completed.returncode != 0:
                    raise RuntimeError(completed.stdout[-2000:])
                if (
                    destination.stat().st_size != part["bytes"]
                    or sha256(destination) != part["sha256"]
                ):
                    raise RuntimeError(f"downloaded asset failed integrity: {part['name']}")
                status = "FETCHED"
            fetched.append(
                {
                    "asset": part["name"],
                    "bytes": part["bytes"],
                    "sha256": part["sha256"],
                    "sidecar": str(sidecar.relative_to(ROOT)),
                    "status": status,
                }
            )
    print(
        json.dumps(
            {
                "status": "VERIFIED",
                "directory": str(output),
                "asset_count": len(fetched),
                "assets": fetched,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
