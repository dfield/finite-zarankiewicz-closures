#!/usr/bin/env python3
"""Check the follow-on exact values, frontier, and finite certificate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zarankiewicz_z9_23.extended import (  # noqa: E402
    extended_frontier_report,
    z10_22_certificate_report,
)
from zarankiewicz_z9_23.matrix import read_boolean_csv, verify_by_row_triples  # noqa: E402


WITNESSES = (
    ("z10_21_106_matrix.csv", 10, 21, 106),
    ("z10_22_110_matrix.csv", 10, 22, 110),
    ("z11_20_111_matrix.csv", 11, 20, 111),
)


def report() -> dict[str, object]:
    """Return the independently recomputed extended-results report."""

    witnesses = []
    for filename, rows, columns, ones in WITNESSES:
        path = ROOT / "data" / filename
        result = verify_by_row_triples(
            read_boolean_csv(path),
            expected_rows=rows,
            expected_columns=columns,
            expected_ones=ones,
            raw_bytes=path.read_bytes(),
        )
        if not result.valid:
            raise AssertionError(f"extended witness failed: {filename}")
        witnesses.append({"file": f"data/{filename}", **result.as_dict()})
    return {
        "status": "VERIFIED",
        "frontier": extended_frontier_report(),
        "z10_22_upper_certificate": z10_22_certificate_report(),
        "witnesses": witnesses,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the recomputed report with analysis/extended_results.json",
    )
    args = parser.parse_args()
    observed = report()
    destination = ROOT / "analysis" / "extended_results.json"
    rendered = json.dumps(observed, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not destination.exists() or destination.read_text(encoding="utf-8") != rendered:
            print(json.dumps({"status": "MISMATCH", "artifact": str(destination)}, indent=2))
            return 1
        print(
            json.dumps(
                {
                    "status": "IDENTICAL",
                    "source_open_cases": observed["frontier"]["source_open_cases"],
                    "remaining_open_cases": observed["frontier"]["remaining_open_cases"],
                    "witnesses": len(observed["witnesses"]),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    destination.write_text(rendered, encoding="utf-8")
    print(json.dumps({"status": "GENERATED", "artifact": str(destination)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
