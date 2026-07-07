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
from finite_zarankiewicz_closures.sat_certificate import (
    SatCertificateError,
    _check_cube_archive,
    verify_z10_23_sat_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


class CaseCertificateTests(unittest.TestCase):
    def test_release_backed_cube_archive_metadata_is_strict(self) -> None:
        payload = {
            "format": "TAR+DRAT+xz+github-release-parts",
            "compression": {
                "archive": "deterministic PAX tar",
                "xz_options": ["-T8", "-3"],
            },
            "release": {
                "repository": "dfield/finite-zarankiewicz-closures",
                "tag": "z10-23-certificate-v1",
            },
            "parts": [
                {
                    "name": "sample.cube-proofs.tar.xz.part-00",
                    "bytes": 11,
                    "sha256": "1" * 64,
                },
                {
                    "name": "sample.cube-proofs.tar.xz.part-01",
                    "bytes": 13,
                    "sha256": "2" * 64,
                },
            ],
            "bytes": 24,
            "sha256": "3" * 64,
        }
        self.assertEqual(_check_cube_archive(ROOT, payload), 24)
        for mutate in (
            lambda value: value["release"].__setitem__("tag", "unrecorded"),
            lambda value: value["compression"]["xz_options"].append("unrecorded"),
            lambda value: value["parts"].reverse(),
            lambda value: value["parts"][0].__setitem__("sha256", "bad"),
            lambda value: value.__setitem__("bytes", 25),
        ):
            candidate = copy.deepcopy(payload)
            mutate(candidate)
            with self.assertRaises(SatCertificateError):
                _check_cube_archive(ROOT, candidate)

    def test_z10_23_sat_manifest_rejects_scope_and_toolchain_mutations(self) -> None:
        path = ROOT / "certificates" / "z10_23_sat.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        scope_mutation = copy.deepcopy(manifest)
        scope_mutation["profiles"][0]["profile"] = "4x1,5x22"
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(scope_mutation, ROOT)
        toolchain_mutation = copy.deepcopy(manifest)
        toolchain_mutation["toolchain"]["solver"] = "unrecorded"
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(toolchain_mutation, ROOT)
        commit_mutation = copy.deepcopy(manifest)
        commit_mutation["toolchain"]["proof_tools_commit"] = "unrecorded"
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(commit_mutation, ROOT)
        strategy_mutation = copy.deepcopy(manifest)
        strategy_mutation["profiles"][0]["strategy"] = "unrecorded"
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(strategy_mutation, ROOT)
        chunk_mutation = copy.deepcopy(manifest)
        split_case = next(
            case for case in chunk_mutation["profiles"] if "parts" in case["proof"]
        )
        split_case["proof"]["parts"].reverse()
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(chunk_mutation, ROOT)
        chunk_hash_mutation = copy.deepcopy(manifest)
        split_case = next(
            case for case in chunk_hash_mutation["profiles"] if "parts" in case["proof"]
        )
        split_case["proof"]["parts"][0]["sha256"] = "0" * 64
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(chunk_hash_mutation, ROOT)
        cube_count_mutation = copy.deepcopy(manifest)
        cube_case = next(
            case
            for case in cube_count_mutation["profiles"]
            if case["strategy"] == "row_stabilizer_cube_cover"
        )
        cube_case["proof"]["catalog"]["count"] -= 1
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(cube_count_mutation, ROOT)
        cube_index_mutation = copy.deepcopy(manifest)
        cube_case = next(
            case
            for case in cube_index_mutation["profiles"]
            if case["strategy"] == "row_stabilizer_cube_cover"
        )
        cube_case["proof"]["proof_index"]["sha256"] = "0" * 64
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(cube_index_mutation, ROOT)

    def test_all_stored_certificates_pass(self) -> None:
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
            "z10_23_112": lambda c: c["upper_bound"]["sat_integrity_report"].__setitem__(
                "sat_profiles", 12
            ),
            "z11_19_106": lambda c: c["upper_bound"]["steps"][0].__setitem__(
                "source_upper_bound", 102
            ),
            "z11_20_111": lambda c: c["upper_bound"]["steps"][1].__setitem__(
                "recomputed_upper_bound", 112
            ),
            "z11_23_123": lambda c: c["upper_bound"]["steps"][0].__setitem__(
                "recomputed_upper_bound", 124
            ),
            "z12_23_134": lambda c: c["upper_bound"]["detailed_report"]["at_135"][
                "cases"
            ]["5^4 6^18 7^1"].__setitem__("minimum_row_residue_sum", 24),
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
