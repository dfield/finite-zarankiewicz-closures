from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from zarankiewicz_z9_23.certificate import (
    CertificateError,
    enumerate_degree_profiles,
    penalty,
    verify_certificate,
)
from zarankiewicz_z9_23.boundary import boundary_report, kernel_catalog_rows


ROOT = Path(__file__).resolve().parents[1]
CERTIFICATE = ROOT / "certificates" / "degree_deficit.json"


class CertificateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    def test_penalty_table(self) -> None:
        self.assertEqual([penalty(degree) for degree in range(10)], [20, 14, 8, 3, 0, 0, 4, 13, 28, 50])

    def test_profile_enumerator_finds_exactly_three_cases(self) -> None:
        self.assertEqual(
            enumerate_degree_profiles(),
            [
                (0, 0, 0, 0, 11, 12, 0, 0, 0, 0),
                (0, 0, 0, 0, 12, 10, 1, 0, 0, 0),
                (0, 0, 0, 1, 9, 13, 0, 0, 0, 0),
            ],
        )

    def test_certificate_passes(self) -> None:
        report = verify_certificate(self.certificate)
        self.assertEqual(report["status"], "VERIFIED")
        self.assertEqual(report["profiles_enumerated"], 3)

    def test_mutated_fields_are_rejected(self) -> None:
        mutations = [
            ("problem target", lambda c: c["problem"].__setitem__("target_ones", 103)),
            ("penalty", lambda c: c["global_identity"]["penalty_by_column_degree_0_through_9"].__setitem__(4, 1)),
            ("missing profile", lambda c: c["allowed_degree_cases"].pop()),
            ("profile count", lambda c: c["allowed_degree_cases"][0]["counts_by_degree_0_through_9"].__setitem__(4, 10)),
            ("incidence", lambda c: c["allowed_degree_cases"][0].__setitem__("triple_incidences", 165)),
            ("residue", lambda c: c["allowed_degree_cases"][1]["row_categories"][0].__setitem__("deficit_residue_mod_3", 2)),
            ("lower bound", lambda c: c["allowed_degree_cases"][2].__setitem__("certified_lower_bound_sum_row_deficits", 0)),
            ("aggregate", lambda c: c["allowed_degree_cases"][0].__setitem__("aggregate_row_cut_lhs", 162)),
            ("conclusion", lambda c: c.__setitem__("conclusion", "104 exists")),
        ]
        for name, mutate in mutations:
            with self.subTest(name=name):
                candidate = copy.deepcopy(self.certificate)
                mutate(candidate)
                with self.assertRaises(CertificateError):
                    verify_certificate(candidate)

    def test_dgh_boundary_is_exact_and_diagnostic(self) -> None:
        report = boundary_report()
        self.assertEqual(report["full_dgh_lp"]["exact_optimum"], "314/3")
        self.assertEqual(report["full_dgh_lp"]["floor_upper_bound"], 104)
        self.assertEqual(
            report["full_dgh_lp"]["optimal_degree_profile"], {"4": "31/3", "5": "38/3"}
        )
        self.assertEqual(len(report["full_dgh_lp"]["constraint_checks_at_optimum"]), 15)
        self.assertTrue(
            all(
                profile["all_dgh_constraints_satisfied"]
                for profile in report["integer_profiles_at_objective_104"]
            )
        )

    def test_kernel_catalog_is_the_complete_stated_quotient(self) -> None:
        rows = kernel_catalog_rows()
        self.assertEqual(len(rows), 33)
        self.assertEqual(sum(row["family"] == "single_column_restriction" for row in rows), 15)
        self.assertEqual(sum(row["family"] == "sharp_column_penalty" for row in rows), 10)
        self.assertEqual(sum(row["family"] == "marked_row_overlap" for row in rows), 8)


if __name__ == "__main__":
    unittest.main()
