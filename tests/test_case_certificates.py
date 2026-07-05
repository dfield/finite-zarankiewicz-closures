from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from finite_zarankiewicz_closures.case_certificates import (
    CASE_SPECS,
    CaseCertificateError,
    verify_case_certificate,
)


ROOT = Path(__file__).resolve().parents[1]


class CaseCertificateTests(unittest.TestCase):
    def test_all_four_stored_certificates_pass(self) -> None:
        for case in CASE_SPECS:
            with self.subTest(case=case.slug):
                path = ROOT / "certificates" / f"{case.slug}.json"
                certificate = json.loads(path.read_text(encoding="utf-8"))
                report = verify_case_certificate(certificate, ROOT)
                self.assertEqual(report["status"], "VERIFIED")

    def test_each_case_rejects_mutation(self) -> None:
        for case in CASE_SPECS:
            with self.subTest(case=case.slug):
                path = ROOT / "certificates" / f"{case.slug}.json"
                candidate = json.loads(path.read_text(encoding="utf-8"))
                candidate = copy.deepcopy(candidate)
                candidate["parameters"]["exact_value"] += 1
                with self.assertRaises(CaseCertificateError):
                    verify_case_certificate(candidate, ROOT)

    def test_each_upper_bound_payload_rejects_mutation(self) -> None:
        mutators = {
            "z9_23_103": lambda c: c["upper_bound"].__setitem__("profiles_enumerated", 2),
            "z10_21_106": lambda c: c["upper_bound"]["steps"][0].__setitem__(
                "source_upper_bound", 97
            ),
            "z10_22_110": lambda c: c["upper_bound"]["detailed_report"]["case_c"].__setitem__(
                "minimum_pair_residue_sum", 11
            ),
            "z11_20_111": lambda c: c["upper_bound"]["steps"][1].__setitem__(
                "recomputed_upper_bound", 112
            ),
        }
        for case in CASE_SPECS:
            with self.subTest(case=case.slug):
                path = ROOT / "certificates" / f"{case.slug}.json"
                candidate = json.loads(path.read_text(encoding="utf-8"))
                mutators[case.slug](candidate)
                with self.assertRaises(CaseCertificateError):
                    verify_case_certificate(candidate, ROOT)


if __name__ == "__main__":
    unittest.main()
