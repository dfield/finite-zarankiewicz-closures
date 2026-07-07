#!/usr/bin/env python3
"""Generate or byte-check exact decision models for every exact case."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.encodings import (  # noqa: E402
    write_cell_cnf,
    write_column_type_lp,
)


MODEL_CASES = (
    ("z9_23_103", 9, 23, 104),
    ("z10_21_106", 10, 21, 107),
    ("z10_22_110", 10, 22, 111),
    ("z10_23_112", 10, 23, 113),
    ("z11_19_106", 11, 19, 107),
    ("z11_20_111", 11, 20, 112),
    ("z11_23_123", 11, 23, 124),
    ("z12_23_134", 12, 23, 135),
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _names(rows: int, columns: int, target: int) -> tuple[str, str]:
    return (
        f"cells_{rows}x{columns}_exact_{target}.cnf",
        f"column_types_{rows}x{columns}_exact_{target}.lp",
    )


def _generate_case(
    directory: Path, slug: str, rows: int, columns: int, target: int
) -> dict[str, object]:
    cell_name, column_name = _names(rows, columns, target)
    cell_path = directory / cell_name
    column_path = directory / column_name
    cell = write_cell_cnf(cell_path, rows=rows, columns=columns, target_ones=target)
    column = write_column_type_lp(
        column_path, rows=rows, columns=columns, target_ones=target
    )
    return {
        "slug": slug,
        "rows": rows,
        "columns": columns,
        "excluded_target": target,
        "cell_cnf": {"file": f"models/{cell_name}", **cell},
        "column_lp": {"file": f"models/{column_name}", **column},
        "monotonicity_note": (
            f"Testing exactly {target} ones suffices because deleting ones preserves "
            "K_3,3-freeness."
        ),
    }


def _manifest(cases: dict[str, object]) -> dict[str, object]:
    return {"schema_version": 2, "cases": cases}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate in a temporary directory and require byte-for-byte identity",
    )
    args = parser.parse_args()
    model_directory = ROOT / "models"

    if args.check:
        with tempfile.TemporaryDirectory(prefix="exact-case-model-check-") as raw:
            temporary = Path(raw)
            reports = {}
            for slug, rows, columns, target in MODEL_CASES:
                report = _generate_case(temporary, slug, rows, columns, target)
                reports[slug] = report
                for kind in ("cell_cnf", "column_lp"):
                    name = Path(report[kind]["file"]).name
                    generated = temporary / name
                    destination = model_directory / name
                    if (
                        not destination.exists()
                        or generated.read_bytes() != destination.read_bytes()
                    ):
                        print(
                            json.dumps(
                                {"status": "MISMATCH", "artifact": str(destination)},
                                indent=2,
                            )
                        )
                        return 1
                    if report[kind]["sha256"] != _sha256(destination):
                        raise AssertionError(f"stored hash mismatch: {destination}")
            expected_manifest = (
                json.dumps(_manifest(reports), indent=2, sort_keys=True) + "\n"
            )
            manifest_path = model_directory / "manifest.json"
            if (
                not manifest_path.exists()
                or manifest_path.read_text(encoding="utf-8") != expected_manifest
            ):
                print(json.dumps({"status": "MISMATCH", "artifact": str(manifest_path)}, indent=2))
                return 1
        print(json.dumps({"status": "IDENTICAL", "cases": reports}, indent=2, sort_keys=True))
        return 0

    reports = {}
    for slug, rows, columns, target in MODEL_CASES:
        reports[slug] = _generate_case(model_directory, slug, rows, columns, target)
    manifest_path = model_directory / "manifest.json"
    manifest_path.write_text(
        json.dumps(_manifest(reports), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "GENERATED", "cases": reports}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
