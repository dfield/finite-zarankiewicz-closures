from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.check_new_bounds import BNL_OPEN, build_table, degree_profiles
from finite_zarankiewicz_closures.extended import z10_23_profile_report


ROOT = Path(__file__).resolve().parents[1]


class NewBoundTests(unittest.TestCase):
    def test_sat_session_record_marks_candidate_as_pending(self) -> None:
        report = json.loads(
            (ROOT / "analysis" / "sat_cross_check.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            report["evidence_status"],
            "ACTIVE_CERTIFICATION_PENDING",
        )
        self.assertEqual(
            report["candidate_result"]["sat_profiles_requiring_certificates"],
            13,
        )
        self.assertEqual(report["candidate_result"]["current_interval"], [112, 114])
        self.assertEqual(
            report["historical_untraced_session"]["status"],
            "CORROBORATING_ONLY",
        )

    def test_sat_frontier_profile_catalog_is_complete(self) -> None:
        recorded = json.loads(
            (ROOT / "analysis" / "sat_cross_check.json").read_text(encoding="utf-8")
        )["historical_untraced_session"]["profile_counts"]
        for total, expected_count in ((113, 25), (114, 11)):
            with self.subTest(total=total):
                generated = list(degree_profiles(10, 23, total))
                self.assertEqual(len(generated), expected_count)
                self.assertEqual(recorded[str(total)], expected_count)

    def test_independent_enumerators_agree_on_every_113_profile(self) -> None:
        report = z10_23_profile_report()
        partitioned = set()
        for key in (
            "low_degree_column_profiles",
            "two_degree_three_profiles",
            "residue_profiles",
            "sat_profiles",
        ):
            partitioned.update(report[key])
        independently_generated = {
            " ".join(f"{degree}^{count}" for degree, count in sorted(profile.items()))
            for profile in degree_profiles(10, 23, 113)
        }
        self.assertEqual(len(partitioned), 25)
        self.assertEqual(partitioned, independently_generated)

    def test_pending_candidate_has_no_final_manifest(self) -> None:
        self.assertFalse((ROOT / "certificates" / "z10_23_sat.json").exists())
        self.assertFalse((ROOT / "audit" / "z10_23_sat_replay.json").exists())

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
