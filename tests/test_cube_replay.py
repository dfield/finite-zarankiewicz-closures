from __future__ import annotations

import hashlib
import io
import json
import lzma
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scripts import replay_z10_23_certificates as replay


class CubeReplayTests(unittest.TestCase):
    def test_jsonl_reader_reassembles_split_xz_stream(self) -> None:
        raw = lzma.compress(b'{"value":1}\n{"value":2}\n')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            split = len(raw) // 2
            parts = []
            for index, block in enumerate((raw[:split], raw[split:])):
                path = root / f"records.jsonl.xz.part-{index:02d}"
                path.write_bytes(block)
                parts.append({"file": path.name})
            with patch.object(replay, "ROOT", root):
                records = list(
                    replay._jsonl_records(
                        {
                            "parts": parts,
                            "compression": "xz",
                            "format": "JSONL+xz+split",
                        }
                    )
                )
            self.assertEqual(records, [{"value": 1}, {"value": 2}])

    @staticmethod
    def _fixture(root: Path, count: int = 7) -> tuple[dict[str, object], Path]:
        catalog = [
            {"masks": [7, position + 8], "reason": "proof_required"}
            for position in range(count)
        ]
        proofs = [f"proof-{position}".encode("ascii") for position in range(count)]
        index = [
            {
                "index": position,
                "masks": leaf["masks"],
                "literals": [],
                "file": f"proofs/leaf-{position:08d}.drat",
                "bytes": len(proofs[position]),
                "sha256": hashlib.sha256(proofs[position]).hexdigest(),
            }
            for position, leaf in enumerate(catalog)
        ]
        catalog_path = root / "catalog.jsonl"
        catalog_path.write_text(
            "".join(json.dumps(record) + "\n" for record in catalog),
            encoding="ascii",
        )
        index_path = root / "index.jsonl"
        index_path.write_text(
            "".join(json.dumps(record) + "\n" for record in index),
            encoding="ascii",
        )
        archive_path = root / "proofs.tar.xz"
        with tarfile.open(archive_path, "w:xz", format=tarfile.PAX_FORMAT) as archive:
            for record, payload in zip(index, proofs):
                info = tarfile.TarInfo(record["file"])
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
        formula = root / "formula.cnf"
        formula.write_text("p cnf 1 1\n1 0\n", encoding="ascii")
        case: dict[str, object] = {
            "profile": "test-profile",
            "strategy": "row_stabilizer_cube_cover",
            "proof": {
                "catalog": {"file": catalog_path.name},
                "proof_index": {"file": index_path.name},
                "archive": {"file": archive_path.name},
            },
        }
        return case, formula

    def test_cube_replay_streams_archive_in_index_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case, formula = self._fixture(root)
            with (
                patch.object(replay, "ROOT", root),
                patch.object(replay, "_replay_cube_leaf", return_value=(True, "")),
            ):
                report = replay._replay_cube_case(
                    case, formula, "drat-trim", "lrat-check", workers=2
                )
            self.assertTrue(report["verified"])
            self.assertEqual(report["leaf_count"], 7)

    def test_cube_replay_rejects_index_order_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            case, formula = self._fixture(root)
            index_path = root / "index.jsonl"
            records = index_path.read_text(encoding="ascii").splitlines()
            records[0], records[1] = records[1], records[0]
            index_path.write_text("\n".join(records) + "\n", encoding="ascii")
            with (
                patch.object(replay, "ROOT", root),
                patch.object(replay, "_replay_cube_leaf", return_value=(True, "")),
                self.assertRaises(ValueError),
            ):
                replay._replay_cube_case(
                    case, formula, "drat-trim", "lrat-check", workers=2
                )


if __name__ == "__main__":
    unittest.main()
