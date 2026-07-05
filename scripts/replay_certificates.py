#!/usr/bin/env python3
"""Replay the terminal DRAT and LRAT traces with external checkers."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASES = ("balanced", "one_degree_3", "one_degree_6")


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional JSON report path")
    args = parser.parse_args()
    drat_trim = shutil.which("drat-trim")
    lrat_check = shutil.which("lrat-check")
    if drat_trim is None or lrat_check is None:
        print("Both drat-trim and lrat-check are required.", file=sys.stderr)
        return 2

    reports = []
    for case in CASES:
        model = ROOT / "models" / f"terminal_{case}.cnf"
        drat = ROOT / "certificates" / f"terminal_{case}.drat"
        lrat = ROOT / "certificates" / f"terminal_{case}.lrat"
        drat_result = _run([drat_trim, str(model), str(drat)])
        lrat_result = _run([lrat_check, str(model), str(lrat)])
        drat_verified = drat_result.returncode == 0 and "VERIFIED" in drat_result.stdout
        lrat_verified = lrat_result.returncode == 0 and "VERIFIED" in lrat_result.stdout
        report = {
            "case": case,
            "drat_verified": drat_verified,
            "lrat_verified": lrat_verified,
        }
        if not drat_verified or not lrat_verified:
            report["drat_output_tail"] = drat_result.stdout[-1000:]
            report["lrat_output_tail"] = lrat_result.stdout[-1000:]
            print(json.dumps({"status": "REJECTED", "result": report}, indent=2))
            return 1
        reports.append(report)

    result = {
        "status": "VERIFIED",
        "cases": reports,
        "commands": [
            "drat-trim models/terminal_CASE.cnf certificates/terminal_CASE.drat",
            "lrat-check models/terminal_CASE.cnf certificates/terminal_CASE.lrat",
        ],
        "scope": (
            "These traces replay only the three terminal Z(9,23) integer aggregations. The "
            "four case-specific JSON certificates establish each result's separate evidence path."
        ),
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
