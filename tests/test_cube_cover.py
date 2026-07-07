from __future__ import annotations

import copy
import unittest

from finite_zarankiewicz_closures.cube_cover import (
    CubeCoverError,
    child_masks,
    ordered_degrees,
    verify_cube_catalog,
)


PROFILES = (
    "3x1,4x2,5x18,6x2",
    "3x1,4x3,5x16,6x3",
    "3x1,4x4,5x14,6x4",
)


def depth_three_catalog(profile: str) -> list[dict[str, object]]:
    degrees = ordered_degrees(profile)
    prefixes = [[(1 << degrees[0]) - 1]]
    while len(prefixes[0]) < 3:
        prefixes = [
            prefix + [mask]
            for prefix in prefixes
            for mask in child_masks(prefix, degrees)
        ]
    return [{"masks": prefix, "reason": "solver_unsat"} for prefix in prefixes]


class CubeCoverTests(unittest.TestCase):
    def test_depth_three_frontier_is_complete(self) -> None:
        for profile in PROFILES:
            with self.subTest(profile=profile):
                catalog = depth_three_catalog(profile)
                self.assertEqual(len(catalog), 40)
                report = verify_cube_catalog(profile, catalog)
                self.assertEqual(report["status"], "COMPLETE")
                self.assertEqual(report["leaf_count"], 40)
                self.assertEqual(report["depth_counts"], {"3": 40})

    def test_missing_branch_is_rejected(self) -> None:
        catalog = depth_three_catalog(PROFILES[0])
        with self.assertRaises(CubeCoverError):
            verify_cube_catalog(PROFILES[0], catalog[:-1])

    def test_wrong_degree_and_prefix_overlap_are_rejected(self) -> None:
        catalog = depth_three_catalog(PROFILES[0])
        wrong_degree = copy.deepcopy(catalog)
        wrong_degree[0]["masks"][2] = 0
        with self.assertRaises(CubeCoverError):
            verify_cube_catalog(PROFILES[0], wrong_degree)

        prefix_overlap = copy.deepcopy(catalog)
        prefix_overlap.append(
            {"masks": prefix_overlap[0]["masks"][:2], "reason": "solver_unsat"}
        )
        with self.assertRaises(CubeCoverError):
            verify_cube_catalog(PROFILES[0], prefix_overlap)


if __name__ == "__main__":
    unittest.main()
