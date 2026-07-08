from __future__ import annotations

import hashlib
import lzma
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_z10_23_sat_manifest as builder


class SatManifestBuilderTests(unittest.TestCase):
    def test_split_xz_jsonl_metadata_binds_parts_and_record_count(self) -> None:
        raw = lzma.compress(b'{"value":1}\n{"value":2}\n')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            split = len(raw) // 2
            paths = []
            for index, block in enumerate((raw[:split], raw[split:])):
                path = root / f"sample.jsonl.xz.part-{index:02d}"
                path.write_bytes(block)
                paths.append(path)
            artifact = builder._jsonl_artifact(root, "sample.jsonl")
            self.assertEqual(artifact, tuple(paths))
            with patch.object(builder, "ROOT", root):
                metadata = builder._jsonl_metadata(artifact)
            self.assertEqual(metadata["count"], 2)
            self.assertEqual(metadata["bytes"], len(raw))
            self.assertEqual(metadata["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(metadata["compression"], "xz")
            self.assertEqual(metadata["format"], "JSONL+xz+split")
            self.assertEqual(len(metadata["parts"]), 2)

            paths[1].rename(root / "sample.jsonl.xz.part-02")
            with self.assertRaises(ValueError):
                builder._jsonl_artifact(root, "sample.jsonl")


if __name__ == "__main__":
    unittest.main()
