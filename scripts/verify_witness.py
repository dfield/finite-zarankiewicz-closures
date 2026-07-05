#!/usr/bin/env python3
"""Verify the bundled 103-one witness by row-triple capacities."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.matrix import (  # noqa: E402
    read_boolean_csv,
    verify_by_row_triples,
)


def main() -> int:
    path = ROOT / "data" / "z9_23_103_matrix.csv"
    raw = path.read_bytes()
    result = verify_by_row_triples(read_boolean_csv(path), raw_bytes=raw)
    print(json.dumps(result.as_dict(), indent=2, sort_keys=True))
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
