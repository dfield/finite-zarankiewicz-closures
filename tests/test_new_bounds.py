from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.check_new_bounds import BNL_OPEN, build_table, degree_profiles


ROOT = Path(__file__).resolve().parents[1]


def profile_label(profile: dict[int, int]) -> str:
    """Render a degree profile in the SAT cross-check's stable notation."""

    return ",".join(f"{degree}x{count}" for degree, count in sorted(profile.items()))


class NewBoundTests(unittest.TestCase):
    def test_sat_session_record_is_explicitly_non_load_bearing(self) -> None:
        report = json.loads(
            (ROOT / "analysis" / "sat_cross_check.json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["evidence_status"], "UNVERIFIED_SESSION_RECORD")
        self.assertIn(
            "not a repository theorem",
            report["repository_targets_cross_check"]["review_note"],
        )

    def test_sat_frontier_profile_catalog_is_complete(self) -> None:
        report = json.loads(
            (ROOT / "analysis" / "sat_cross_check.json").read_text(encoding="utf-8")
        )["frontier_observations"]
        for total, expected_count in ((113, 25), (114, 11)):
            with self.subTest(total=total):
                generated = {
                    profile_label(profile) for profile in degree_profiles(10, 23, total)
                }
                recorded = set(report[f"10,23 at {total}"])
                self.assertEqual(len(generated), expected_count)
                self.assertEqual(recorded, generated)

    def test_degree_one_profile_is_explicitly_filter_killed(self) -> None:
        report = json.loads(
            (ROOT / "analysis" / "sat_cross_check.json").read_text(encoding="utf-8")
        )["frontier_observations"]["10,23 at 113"]
        self.assertEqual(report["1x1,5x20,6x2"], "FILTER-KILLED")

    def test_propagated_improvement_counts_match_documentation(self) -> None:
        table = build_table()["cells"]
        improved_upper = 0
        improved_lower = 0
        for (rows, columns), (old_lower, old_upper) in BNL_OPEN.items():
            cell = table[f"{rows},{columns}"]
            improved_upper += cell["upper"] < old_upper
            improved_lower += cell["lower"] > old_lower
        self.assertEqual(improved_upper, 20)
        self.assertEqual(improved_lower, 17)


if __name__ == "__main__":
    unittest.main()
