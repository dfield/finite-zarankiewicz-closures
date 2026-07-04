#!/usr/bin/env python3
"""Standalone exhaustive verifier for the 103-one matrix.

This script intentionally imports no project module.  It parses the CSV on its
own and inspects all C(9,3)*C(23,3)=148,764 candidate submatrices directly.
That independence is useful because a shared helper bug cannot make the two
witness checks agree.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    path = ROOT / "data" / "z9_23_103_matrix.csv"
    raw = path.read_bytes()
    try:
        with path.open(newline="", encoding="ascii") as handle:
            text_rows = list(csv.reader(handle))
        dimensions_ok = len(text_rows) == 9 and all(len(row) == 23 for row in text_rows)
        entries_ok = dimensions_ok and all(cell in {"0", "1"} for row in text_rows for cell in row)
        matrix = [[1 if cell == "1" else 0 for cell in row] for row in text_rows] if entries_ok else []
    except (OSError, UnicodeError, csv.Error):
        dimensions_ok = False
        entries_ok = False
        matrix = []

    ones = sum(sum(row) for row in matrix) if entries_ok else None
    checked = 0
    violation = None
    if entries_ok:
        for row_triple in itertools.combinations(range(9), 3):
            for column_triple in itertools.combinations(range(23), 3):
                checked += 1
                if all(matrix[row][column] for row in row_triple for column in column_triple):
                    violation = {"rows": list(row_triple), "columns": list(column_triple)}
                    break
            if violation is not None:
                break
    valid = dimensions_ok and entries_ok and ones == 103 and violation is None and checked == 148_764
    result = {
        "valid": valid,
        "dimensions_ok": dimensions_ok,
        "entries_ok": entries_ok,
        "ones": ones,
        "candidate_submatrices_checked": checked,
        "expected_candidate_submatrices": 148_764,
        "first_violation": violation,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
