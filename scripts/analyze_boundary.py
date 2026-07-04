#!/usr/bin/env python3
"""Regenerate or byte-check the exact LP boundary and kernel catalog."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zarankiewicz_z9_23.boundary import (  # noqa: E402
    KERNEL_FIELDS,
    boundary_report,
    kernel_catalog_rows,
)


def rendered_artifacts() -> tuple[str, str]:
    report = json.dumps(boundary_report(), indent=2, sort_keys=True) + "\n"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=KERNEL_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(kernel_catalog_rows())
    return report, output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report, catalog = rendered_artifacts()
    destinations = {
        ROOT / "analysis" / "dgh_boundary.json": report,
        ROOT / "analysis" / "local_kernel_catalog.csv": catalog,
    }
    if args.check:
        mismatches = [
            str(path.relative_to(ROOT))
            for path, expected in destinations.items()
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        print(json.dumps({"status": "IDENTICAL" if not mismatches else "MISMATCH", "mismatches": mismatches}, indent=2))
        return 1 if mismatches else 0
    for path, content in destinations.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    print(json.dumps({"status": "GENERATED", "files": [str(path.relative_to(ROOT)) for path in destinations]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
