#!/usr/bin/env python3
"""Standalone checker for five exact and two candidate matrix witnesses."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPECS = (
    ("z10_21_106_matrix.csv", 10, 21, 106),
    ("z10_22_110_matrix.csv", 10, 22, 110),
    ("z10_23_112_matrix.csv", 10, 23, 112),
    ("z11_19_106_matrix.csv", 11, 19, 106),
    ("z11_20_111_matrix.csv", 11, 20, 111),
    ("z11_23_123_matrix.csv", 11, 23, 123),
    ("z12_23_134_matrix.csv", 12, 23, 134),
)


def main() -> int:
    reports = []
    valid = True
    for filename, expected_rows, expected_columns, expected_ones in SPECS:
        path = ROOT / "data" / filename
        raw = path.read_bytes()
        with path.open(newline="", encoding="ascii") as handle:
            text_rows = list(csv.reader(handle))
        dimensions_ok = len(text_rows) == expected_rows and all(
            len(row) == expected_columns for row in text_rows
        )
        entries_ok = dimensions_ok and all(
            cell in {"0", "1"} for row in text_rows for cell in row
        )
        matrix = (
            [[1 if cell == "1" else 0 for cell in row] for row in text_rows]
            if entries_ok
            else []
        )
        ones = sum(map(sum, matrix)) if entries_ok else None
        checked = 0
        violation = None
        if entries_ok:
            for row_triple in itertools.combinations(range(expected_rows), 3):
                for column_triple in itertools.combinations(range(expected_columns), 3):
                    checked += 1
                    if all(
                        matrix[row][column]
                        for row in row_triple
                        for column in column_triple
                    ):
                        violation = {
                            "rows": list(row_triple),
                            "columns": list(column_triple),
                        }
                        break
                if violation is not None:
                    break
        expected_checks = math_comb(expected_rows, 3) * math_comb(expected_columns, 3)
        case_valid = (
            dimensions_ok
            and entries_ok
            and ones == expected_ones
            and violation is None
            and checked == expected_checks
        )
        valid = valid and case_valid
        reports.append(
            {
                "file": f"data/{filename}",
                "valid": case_valid,
                "ones": ones,
                "candidate_submatrices_checked": checked,
                "expected_candidate_submatrices": expected_checks,
                "first_violation": violation,
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    print(json.dumps({"status": "VERIFIED" if valid else "FAILED", "witnesses": reports}, indent=2, sort_keys=True))
    return 0 if valid else 1


def math_comb(n: int, k: int) -> int:
    """Compute a binomial coefficient without importing project code."""

    if k < 0 or k > n:
        return 0
    result = 1
    for index in range(1, min(k, n - k) + 1):
        result = result * (n - index + 1) // index
    return result


if __name__ == "__main__":
    raise SystemExit(main())
