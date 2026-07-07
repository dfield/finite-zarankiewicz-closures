#!/usr/bin/env python3
"""Replay every compressed DRAT core and independently check its derived LRAT."""

from __future__ import annotations

import argparse
import json
import lzma
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Mapping

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "certificates" / "z10_23_sat.json"
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.sat_certificate import (  # noqa: E402
    load_and_verify_z10_23_sat_manifest,
)


def _decompress_proof(case: Mapping[str, Any], destination: BinaryIO) -> None:
    """Stream one direct or byte-split XZ proof into an open destination."""

    proof = case["proof"]
    if not isinstance(proof, dict):
        raise ValueError("missing proof metadata")
    if "file" in proof:
        with lzma.open(ROOT / proof["file"], "rb") as source:
            shutil.copyfileobj(source, destination, length=1024 * 1024)
        return
    with tempfile.NamedTemporaryFile(suffix=".drat.xz") as archive:
        for part in proof["parts"]:
            with (ROOT / part["file"]).open("rb") as source:
                shutil.copyfileobj(source, archive, length=1024 * 1024)
        archive.flush()
        with lzma.open(archive.name, "rb") as source:
            shutil.copyfileobj(source, destination, length=1024 * 1024)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    drat_trim = shutil.which("drat-trim")
    lrat_check = shutil.which("lrat-check")
    if drat_trim is None or lrat_check is None:
        print("drat-trim and lrat-check are required")
        return 2
    integrity = load_and_verify_z10_23_sat_manifest(ROOT)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reports = []
    for case in manifest["profiles"]:
        formula = ROOT / case["formula"]["file"]
        with tempfile.TemporaryDirectory(prefix="z10_23_replay_") as directory:
            proof = Path(directory) / "proof.drat"
            derived_lrat = Path(directory) / "proof.lrat"
            with proof.open("wb") as destination:
                _decompress_proof(case, destination)
            drat_completed = subprocess.run(
                [drat_trim, str(formula), str(proof), "-L", str(derived_lrat)],
                cwd=ROOT,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            drat_verified = (
                drat_completed.returncode == 0 and "VERIFIED" in drat_completed.stdout
            )
            if drat_verified:
                lrat_completed = subprocess.run(
                    [lrat_check, str(formula), str(derived_lrat)],
                    cwd=ROOT,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                lrat_verified = (
                    lrat_completed.returncode == 0 and "VERIFIED" in lrat_completed.stdout
                )
            else:
                lrat_completed = None
                lrat_verified = False
        verified = drat_verified and lrat_verified
        report = {
            "profile": case["profile"],
            "verified": verified,
            "drat_checker": "drat-trim",
            "drat_verified": drat_verified,
            "lrat_checker": "lrat-check",
            "lrat_verified": lrat_verified,
        }
        if not verified:
            report["drat_output_tail"] = drat_completed.stdout[-2000:]
            if lrat_completed is not None:
                report["lrat_output_tail"] = lrat_completed.stdout[-2000:]
            print(json.dumps({"status": "REJECTED", "case": report}, indent=2))
            return 1
        reports.append(report)
    result = {
        "status": "VERIFIED",
        "theorem": manifest["theorem"],
        "integrity": integrity,
        "profile_count": len(reports),
        "profiles": reports,
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = args.output if args.output.is_absolute() else ROOT / args.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
