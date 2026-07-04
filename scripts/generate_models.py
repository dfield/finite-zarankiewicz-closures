#!/usr/bin/env python3
"""Generate or byte-check the two exact decision models."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zarankiewicz_z9_23.encodings import write_cell_cnf, write_column_type_lp  # noqa: E402


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate in a temporary directory and require byte-for-byte identity",
    )
    args = parser.parse_args()
    destinations = {
        "cell_cnf": ROOT / "models" / "cells_9x23_exact_104.cnf",
        "column_lp": ROOT / "models" / "column_types_9x23_exact_104.lp",
    }

    if args.check:
        with tempfile.TemporaryDirectory(prefix="z9-23-model-check-") as directory:
            temporary = Path(directory)
            reports = {
                "cell_cnf": write_cell_cnf(temporary / destinations["cell_cnf"].name),
                "column_lp": write_column_type_lp(temporary / destinations["column_lp"].name),
            }
            for name, destination in destinations.items():
                generated = temporary / destination.name
                if not destination.exists() or generated.read_bytes() != destination.read_bytes():
                    print(json.dumps({"status": "MISMATCH", "artifact": name}, indent=2))
                    return 1
                reports[name]["stored_sha256"] = _sha256(destination)
        print(json.dumps({"status": "IDENTICAL", "models": reports}, indent=2, sort_keys=True))
        return 0

    reports = {
        "cell_cnf": write_cell_cnf(destinations["cell_cnf"]),
        "column_lp": write_column_type_lp(destinations["column_lp"]),
    }
    metadata_path = ROOT / "models" / "manifest.json"
    metadata_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "models": reports,
                "monotonicity_note": (
                    "Testing exactly 104 ones suffices: deleting ones preserves K_3,3-freeness, "
                    "so any denser witness would contain a 104-one witness."
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "GENERATED", "models": reports}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
