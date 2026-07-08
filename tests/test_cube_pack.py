from __future__ import annotations

import json
from pathlib import Path
import tarfile
import tempfile
import unittest

from scripts.pack_z10_23_cube_release import pack


class CubePackTests(unittest.TestCase):
    def test_release_archive_is_deterministic_and_reassembles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            proofs = work / "proofs"
            proofs.mkdir()
            (proofs / "leaf-00000000.drat").write_bytes(b"first proof\n")
            (proofs / "leaf-00000001.drat").write_bytes(b"second proof\n")
            (work / "metadata.json").write_text(
                json.dumps(
                    {
                        "status": "VERIFIED_CUBE_LEAF_PROOFS",
                        "proofs": {"count": 2},
                    }
                )
                + "\n",
                encoding="ascii",
            )
            first = pack("sample", work, threads=1, preset="-0", part_bytes=37)
            second = pack("sample", work, threads=1, preset="-0", part_bytes=37)
            self.assertEqual(first, second)
            archive = work / "sample.cube-proofs.tar.xz"
            combined = b"".join(
                (work / part["name"]).read_bytes() for part in second["parts"]
            )
            self.assertEqual(combined, archive.read_bytes())
            with tarfile.open(archive, mode="r:xz") as handle:
                self.assertEqual(
                    handle.getnames(),
                    [
                        "proofs/leaf-00000000.drat",
                        "proofs/leaf-00000001.drat",
                    ],
                )


if __name__ == "__main__":
    unittest.main()
