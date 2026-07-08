from __future__ import annotations

import copy
import unittest

from finite_zarankiewicz_closures.cube_cover import (
    _ExternalPathSorter,
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


def fixed_frontier_catalog(profile: str, depth: int) -> list[dict[str, object]]:
    degrees = ordered_degrees(profile)
    prefixes = [[(1 << degrees[0]) - 1]]
    while len(prefixes[0]) < depth:
        prefixes = [
            prefix + [mask]
            for prefix in prefixes
            for mask in child_masks(prefix, degrees)
        ]
    return [{"masks": prefix, "reason": "proof_required"} for prefix in prefixes]


def split_leaf_by_next_cell(
    profile: str,
    leaf: dict[str, object],
    row: int,
) -> list[dict[str, object]]:
    masks = leaf["masks"]
    assert isinstance(masks, list)
    column = len(masks)
    variable = row * 23 + column + 1
    degrees = ordered_degrees(profile)
    children = child_masks(masks, degrees)
    signs = [
        sign
        for sign in (1, -1)
        if any(bool(mask & (1 << row)) == (sign > 0) for mask in children)
    ]
    return [
        {
            "masks": masks,
            "literals": [sign * variable],
            "reason": "proof_required",
        }
        for sign in signs
    ]


class CubeCoverTests(unittest.TestCase):
    def test_external_path_sorter_merges_multiple_chunks(self) -> None:
        sorter = _ExternalPathSorter(chunk_records=2)
        try:
            paths = ([7, 4, 2], [7], [7, 3], [7, 4], [7, 3, 9])
            for path in paths:
                sorter.add(path)
            observed = list(sorter.sorted_paths())
            expected = sorted(
                b"".join(mask.to_bytes(2, "big") for mask in path)
                for path in paths
            )
            self.assertEqual(observed, expected)
        finally:
            sorter.close()

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

    def test_fixed_depth_four_frontiers_are_complete(self) -> None:
        expected = (1479, 773, 773)
        for profile, count in zip(PROFILES, expected):
            with self.subTest(profile=profile):
                catalog = fixed_frontier_catalog(profile, 4)
                self.assertEqual(len(catalog), count)
                report = verify_cube_catalog(profile, catalog)
                self.assertEqual(report["status"], "COMPLETE")
                self.assertEqual(report["leaf_count"], count)
                self.assertEqual(report["depth_counts"], {"4": count})

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

    def test_partial_next_column_split_is_complete(self) -> None:
        catalog = depth_three_catalog(PROFILES[0])
        replacement = split_leaf_by_next_cell(PROFILES[0], catalog[0], row=0)
        mixed = replacement + catalog[1:]
        report = verify_cube_catalog(PROFILES[0], mixed)
        self.assertEqual(report["status"], "COMPLETE")
        self.assertEqual(report["leaf_count"], len(mixed))
        self.assertEqual(report["partial_leaf_count"], len(replacement))
        self.assertGreaterEqual(report["canonical_leaf_count"], report["leaf_count"])

    def test_missing_and_overlapping_partial_branches_are_rejected(self) -> None:
        catalog = depth_three_catalog(PROFILES[0])
        replacement = split_leaf_by_next_cell(PROFILES[0], catalog[0], row=0)
        self.assertEqual(len(replacement), 2)
        with self.assertRaises(CubeCoverError):
            verify_cube_catalog(PROFILES[0], replacement[:1] + catalog[1:])
        with self.assertRaises(CubeCoverError):
            verify_cube_catalog(PROFILES[0], replacement + replacement[:1] + catalog[1:])

    def test_partial_literals_must_fix_distinct_immediate_cells(self) -> None:
        catalog = depth_three_catalog(PROFILES[0])
        masks = catalog[0]["masks"]
        assert isinstance(masks, list)
        current_column = len(masks)
        valid = current_column + 1
        malformed = copy.deepcopy(catalog)
        malformed[0]["literals"] = [valid, valid]
        with self.assertRaises(CubeCoverError):
            verify_cube_catalog(PROFILES[0], malformed)
        malformed = copy.deepcopy(catalog)
        malformed[0]["literals"] = [current_column]
        with self.assertRaises(CubeCoverError):
            verify_cube_catalog(PROFILES[0], malformed)


if __name__ == "__main__":
    unittest.main()
