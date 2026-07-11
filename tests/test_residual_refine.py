from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from finite_zarankiewicz_closures.cube_cover import (
    child_masks,
    ordered_degrees,
)
from search.z10_23_residual_refine import refine


PROFILE = "3x1,4x2,5x18,6x2"


def depth_three_catalog() -> list[dict[str, object]]:
    degrees = ordered_degrees(PROFILE)
    prefixes = [[(1 << degrees[0]) - 1]]
    while len(prefixes[0]) < 3:
        prefixes = [
            prefix + [mask]
            for prefix in prefixes
            for mask in child_masks(prefix, degrees)
        ]
    return [{"masks": prefix, "reason": "proof_required"} for prefix in prefixes]


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    with path.open("w", encoding="ascii") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


class ResidualRefineTests(unittest.TestCase):
    def test_one_residual_leaf_is_replaced_by_a_complete_bisection(self) -> None:
        catalog = depth_three_catalog()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog_path = root / "cubes.jsonl"
            residual_path = root / "unresolved.jsonl"
            write_jsonl(catalog_path, catalog)
            write_jsonl(
                residual_path,
                [
                    {
                        "index": 0,
                        "literals": [],
                        "masks": catalog[0]["masks"],
                        "status": "TIMEOUT",
                    }
                ],
            )

            report = refine(
                PROFILE,
                catalog_path,
                [residual_path],
                root / "refined",
                split_bits=1,
                shards=3,
            )

            output = report["output"]
            self.assertEqual(output["cover"]["status"], "COMPLETE")
            self.assertEqual(output["residual_parent_count"], 1)
            self.assertEqual(output["reused_leaf_count"], len(catalog) - 1)
            self.assertEqual(output["replacement_counts"], {"2": 1})
            self.assertEqual(output["refined_task_count"], 2)
            self.assertEqual(output["leaf_count"], len(catalog) + 1)
            self.assertEqual(sum(output["task_counts"]), 2)

    def test_residual_record_must_match_the_indexed_catalog_leaf(self) -> None:
        catalog = depth_three_catalog()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog_path = root / "cubes.jsonl"
            residual_path = root / "unresolved.jsonl"
            write_jsonl(catalog_path, catalog)
            write_jsonl(
                residual_path,
                [
                    {
                        "index": 0,
                        "literals": [],
                        "masks": catalog[1]["masks"],
                        "status": "TIMEOUT",
                    }
                ],
            )

            with self.assertRaisesRegex(RuntimeError, "does not match"):
                refine(
                    PROFILE,
                    catalog_path,
                    [residual_path],
                    root / "refined",
                    split_bits=1,
                    shards=3,
                )


if __name__ == "__main__":
    unittest.main()
