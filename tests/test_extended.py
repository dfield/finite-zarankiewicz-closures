from __future__ import annotations

import unittest
from pathlib import Path

from finite_zarankiewicz_closures.extended import (
    PAPER_OPEN_BOUNDS,
    deletion_upper,
    extended_frontier_report,
    z10_22_certificate_report,
    z10_23_profile_report,
    z12_23_certificate_report,
    z13_23_upper_report,
    z13_23_upper_certificate,
    verify_z13_23_upper_certificate,
)
from finite_zarankiewicz_closures.matrix import read_boolean_csv, verify_by_row_triples


ROOT = Path(__file__).resolve().parents[1]


class ExtendedResultTests(unittest.TestCase):
    def test_deletion_bounds_close_two_paper_cells(self) -> None:
        self.assertEqual(deletion_upper(96, 10), 106)
        self.assertEqual(deletion_upper(101, 19), 106)
        self.assertEqual(deletion_upper(106, 20), 111)

    def test_frontier_counts_are_explicit(self) -> None:
        report = extended_frontier_report()
        self.assertEqual(len(PAPER_OPEN_BOUNDS), 44)
        self.assertEqual(report["source_open_cases"], 44)
        self.assertEqual(report["remaining_open_cases"], 33)

    def test_z10_22_upper_certificate_is_recomputed(self) -> None:
        report = z10_22_certificate_report()
        self.assertEqual(report["status"], "VERIFIED")
        self.assertEqual(report["excluded_target"], 111)
        self.assertEqual(len(report["degree_profiles"]), 4)
        self.assertEqual(report["case_c"]["minimum_pair_residue_sum"], 12)

    def test_z10_23_arithmetic_front_end_is_recomputed(self) -> None:
        report = z10_23_profile_report()
        self.assertEqual(report["status"], "ARITHMETIC_FRONT_END_VERIFIED")
        self.assertEqual(report["profile_count"], 25)
        self.assertEqual(len(report["sat_profiles"]), 13)
        self.assertEqual(
            report["exceptional_pair_residue"]["minimum_pair_residue_sum"],
            39,
        )

    def test_z12_23_upper_certificate_is_recomputed(self) -> None:
        report = z12_23_certificate_report()
        self.assertEqual(report["status"], "VERIFIED")
        self.assertEqual(report["excluded_targets"], [136, 135])
        self.assertEqual(len(report["at_135"]["degree_profiles"]), 5)
        self.assertEqual(
            report["at_135"]["cases"]["5^4 6^18 7^1"]["minimum_row_residue_sum"],
            25,
        )

    def test_z13_23_upper_certificate_is_recomputed(self) -> None:
        report = z13_23_upper_report()
        self.assertEqual(report["status"], "VERIFIED")
        self.assertEqual(report["upper_bound"], 144)
        self.assertEqual(len(report["cases"]), 3)

    def test_z13_23_standalone_certificate_rejects_mutation(self) -> None:
        certificate = z13_23_upper_certificate()
        self.assertEqual(verify_z13_23_upper_certificate(certificate)["status"], "VERIFIED")
        certificate["upper_bound"]["cases"][0]["forced_deficit"] = 21
        with self.assertRaises(ValueError):
            verify_z13_23_upper_certificate(certificate)

    def test_additional_witnesses(self) -> None:
        for filename, rows, columns, ones in (
            ("z10_21_106_matrix.csv", 10, 21, 106),
            ("z10_22_110_matrix.csv", 10, 22, 110),
            ("z10_23_112_matrix.csv", 10, 23, 112),
            ("z11_19_106_matrix.csv", 11, 19, 106),
            ("z11_20_111_matrix.csv", 11, 20, 111),
            ("z11_23_123_matrix.csv", 11, 23, 123),
            ("z12_23_134_matrix.csv", 12, 23, 134),
        ):
            path = ROOT / "data" / filename
            result = verify_by_row_triples(
                read_boolean_csv(path),
                expected_rows=rows,
                expected_columns=columns,
                expected_ones=ones,
                raw_bytes=path.read_bytes(),
            )
            self.assertTrue(result.valid, filename)


if __name__ == "__main__":
    unittest.main()
