from __future__ import annotations

import copy
import hashlib
import json
import lzma
import tempfile
import unittest
from pathlib import Path

from finite_zarankiewicz_closures.case_certificates import (
    ALL_CASE_SPECS,
    CANDIDATE_CASE_SPECS,
    CASE_SPECS,
    CaseCertificateError,
    verify_case_certificate,
)
from finite_zarankiewicz_closures.sat_certificate import (
    SatCertificateError,
    _check_cube_archive,
    _check_cube_proof,
    _load_jsonl,
    verify_z10_23_sat_manifest,
)
from finite_zarankiewicz_closures.cube_cover import child_masks, ordered_degrees


ROOT = Path(__file__).resolve().parents[1]
Z10_SAT_MANIFEST = ROOT / "certificates" / "z10_23_sat.json"


class CaseCertificateTests(unittest.TestCase):
    @staticmethod
    def _release_archive_payload() -> dict[str, object]:
        return {
            "format": "TAR+DRAT+xz+github-release-parts",
            "compression": {
                "archive": "deterministic PAX tar",
                "xz_options": ["-T8", "-3"],
                "xz_version": "xz (XZ Utils) 5.4.1",
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

    def test_xz_jsonl_artifact_is_hash_checked_and_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "records.jsonl.xz"
            with lzma.open(path, "wt", encoding="ascii") as handle:
                handle.write('{"value":1}\n{"value":2}\n')
            payload = {
                "file": path.name,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "bytes": path.stat().st_size,
                "count": 2,
                "compression": "xz",
            }
            self.assertEqual(
                _load_jsonl(root, payload, "test records"),
                [{"value": 1}, {"value": 2}],
            )
            payload["compression"] = "unrecorded"
            with self.assertRaises(SatCertificateError):
                _load_jsonl(root, payload, "test records")

            raw = path.read_bytes()
            split_at = len(raw) // 2
            parts = []
            part_paths = []
            for index, block in enumerate((raw[:split_at], raw[split_at:])):
                part = root / f"records.jsonl.xz.part-{index:02d}"
                part.write_bytes(block)
                part_paths.append(part)
                parts.append(
                    {
                        "file": part.name,
                        "sha256": hashlib.sha256(block).hexdigest(),
                        "bytes": len(block),
                    }
                )
            split_payload = {
                "parts": parts,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
                "count": 2,
                "compression": "xz",
                "format": "JSONL+xz+split",
            }
            self.assertEqual(
                _load_jsonl(root, split_payload, "test records"),
                [{"value": 1}, {"value": 2}],
            )
            split_payload["parts"][0]["sha256"] = "0" * 64
            with self.assertRaises(SatCertificateError):
                _load_jsonl(root, split_payload, "test records")
            split_payload["parts"][0]["sha256"] = hashlib.sha256(
                raw[:split_at]
            ).hexdigest()
            for index, part in enumerate(part_paths):
                renamed = root / f"records.jsonl.xz.part-{index:06d}"
                part.rename(renamed)
                split_payload["parts"][index]["file"] = renamed.name
            self.assertEqual(
                _load_jsonl(root, split_payload, "test records"),
                [{"value": 1}, {"value": 2}],
            )
            split_payload["parts"][1]["file"] = "records.jsonl.xz.part-000002"
            with self.assertRaises(SatCertificateError):
                _load_jsonl(root, split_payload, "test records")

    def test_release_backed_cube_archive_metadata_is_strict(self) -> None:
        payload = self._release_archive_payload()
        self.assertEqual(_check_cube_archive(ROOT, payload), 24)
        for mutate in (
            lambda value: value["release"].__setitem__("tag", "unrecorded"),
            lambda value: value["compression"]["xz_options"].append("unrecorded"),
            lambda value: value["parts"].reverse(),
            lambda value: value["parts"][1].__setitem__(
                "name", "sample.cube-proofs.tar.xz.part-02"
            ),
            lambda value: value["parts"][0].__setitem__("sha256", "bad"),
            lambda value: value.__setitem__("bytes", 25),
        ):
            candidate = copy.deepcopy(payload)
            mutate(candidate)
            with self.assertRaises(SatCertificateError):
                _check_cube_archive(ROOT, candidate)

        large = copy.deepcopy(payload)
        large["parts"] = [
            {
                "name": f"sample.cube-proofs.tar.xz.part-{index:06d}",
                "bytes": 1,
                "sha256": f"{index:064x}",
            }
            for index in range(101)
        ]
        large["bytes"] = 101
        self.assertEqual(_check_cube_archive(ROOT, large), 101)

    def test_cube_catalog_and_compressed_index_are_checked_in_one_stream(self) -> None:
        profile = "3x1,4x2,5x18,6x2"
        degrees = ordered_degrees(profile)
        prefixes = [[(1 << degrees[0]) - 1]]
        while len(prefixes[0]) < 3:
            prefixes = [
                prefix + [mask]
                for prefix in prefixes
                for mask in child_masks(prefix, degrees)
            ]
        catalog = [
            {"masks": prefix, "reason": "proof_required"}
            for prefix in prefixes
        ]
        index = [
            {
                "index": position,
                "masks": leaf["masks"],
                "literals": [],
                "file": f"proofs/leaf-{position:08d}.drat",
                "bytes": 1,
                "sha256": "0" * 64,
                "status": "VERIFIED",
                "solver_options": ["--unsat", "-q", "-P2"],
                "replay": (
                    "drat-trim -> LRAT -> lrat-check; projected DRAT -> drat-trim"
                ),
            }
            for position, leaf in enumerate(catalog)
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog_path = root / "catalog.jsonl"
            catalog_path.write_text(
                "".join(json.dumps(record) + "\n" for record in catalog),
                encoding="ascii",
            )
            index_path = root / "index.jsonl.xz"
            with lzma.open(index_path, "wt", encoding="ascii") as handle:
                for record in index:
                    handle.write(json.dumps(record) + "\n")
            payload = {
                "format": "row-stabilizer-cube-cover",
                "catalog": {
                    "file": catalog_path.name,
                    "sha256": hashlib.sha256(catalog_path.read_bytes()).hexdigest(),
                    "bytes": catalog_path.stat().st_size,
                    "count": len(catalog),
                },
                "proof_index": {
                    "file": index_path.name,
                    "sha256": hashlib.sha256(index_path.read_bytes()).hexdigest(),
                    "bytes": index_path.stat().st_size,
                    "count": len(index),
                    "compression": "xz",
                },
                "archive": self._release_archive_payload(),
            }
            archive_bytes, report = _check_cube_proof(root, profile, payload)
            self.assertEqual(archive_bytes, 24)
            self.assertEqual(report["leaf_count"], len(catalog))

    def test_z10_23_sat_manifest_rejects_scope_and_toolchain_mutations(self) -> None:
        path = Z10_SAT_MANIFEST
        manifest = json.loads(path.read_text(encoding="utf-8"))
        scope_mutation = copy.deepcopy(manifest)
        scope_mutation["profiles"][0]["profile"] = "4x1,5x22"
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(scope_mutation, ROOT)
        toolchain_mutation = copy.deepcopy(manifest)
        toolchain_mutation["toolchain"]["sat"]["solver"] = "unrecorded"
        with self.assertRaises(SatCertificateError):
            verify_z10_23_sat_manifest(toolchain_mutation, ROOT)
        commit_mutation = copy.deepcopy(manifest)
        commit_mutation["toolchain"]["sat"]["proof_tools_commit"] = "unrecorded"
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

    def test_publication_gate_contains_all_established_cases(self) -> None:
        self.assertEqual(len(ALL_CASE_SPECS), 8)
        self.assertEqual(len(CASE_SPECS), 8)
        self.assertEqual(CANDIDATE_CASE_SPECS, ())

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
            "z10_23_112": lambda c: c["upper_bound"]["detailed_report"].__setitem__(
                "vipr_orbits", 444
            ),
            "z11_19_106": lambda c: c["upper_bound"]["steps"][0].__setitem__(
                "source_upper_bound", 102
            ),
            "z11_20_111": lambda c: c["upper_bound"]["steps"][1].__setitem__(
                "recomputed_upper_bound", 112
            ),
            "z11_23_123": lambda c: c["upper_bound"]["steps"][0].__setitem__(
                "remaining_ones_at_least", 112
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
