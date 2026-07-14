#!/usr/bin/env python3
"""Check established values, candidate lower bounds, and frontier certificates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.extended import (  # noqa: E402
    extended_frontier_report,
    z10_22_certificate_report,
    z10_23_profile_report,
    z12_23_certificate_report,
    z13_23_upper_report,
)
from finite_zarankiewicz_closures.matrix import (  # noqa: E402
    read_boolean_csv,
    verify_by_row_triples,
)


WITNESSES = (
    ("z10_21_106_matrix.csv", 10, 21, 106, "established"),
    ("z10_22_110_matrix.csv", 10, 22, 110, "established"),
    ("z10_23_112_matrix.csv", 10, 23, 112, "candidate_lower_bound"),
    ("z11_19_106_matrix.csv", 11, 19, 106, "established"),
    ("z11_20_111_matrix.csv", 11, 20, 111, "established"),
    ("z11_23_123_matrix.csv", 11, 23, 123, "candidate_lower_bound"),
    ("z12_23_134_matrix.csv", 12, 23, 134, "established"),
)


def report() -> dict[str, object]:
    """Return the independently recomputed extended-results report."""

    witnesses = []
    for filename, rows, columns, ones, publication_status in WITNESSES:
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
        witnesses.append(
            {
                "file": f"data/{filename}",
                "publication_status": publication_status,
                **result.as_dict(),
            }
        )
    return {
        "status": "VERIFIED",
        "frontier": extended_frontier_report(),
        "z10_22_upper_certificate": z10_22_certificate_report(),
        "z10_23_arithmetic_front_end": z10_23_profile_report(),
        "z12_23_upper_certificate": z12_23_certificate_report(),
        "z13_23_upper_certificate": z13_23_upper_report(),
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
