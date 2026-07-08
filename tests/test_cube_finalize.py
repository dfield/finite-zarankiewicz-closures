from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from finite_zarankiewicz_closures.cube_cover import child_masks, ordered_degrees
from search.z10_23_cube_finalize import finalize


PROFILE = "3x1,4x2,5x18,6x2"


def depth_three_catalog() -> list[dict[str, object]]:
    degrees = ordered_degrees(PROFILE)
    prefixes = [[(1 << degrees[0]) - 1]]
    while len(prefixes[0]) < 3:
        prefixes = [
            prefix + [mask]
            for prefix in prefixes
            for mask in child_masks(prefix, degrees)
        ]
    return [{"masks": prefix, "reason": "proof_required"} for prefix in prefixes]


class CubeFinalizeTests(unittest.TestCase):
    def test_distributed_workspace_is_reindexed_deterministically(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / "work"
            proofs = work / "proofs"
            checkpoints = work / "checkpoints"
            proofs.mkdir(parents=True)
            checkpoints.mkdir()
            catalog = root / "catalog.jsonl"
            leaves = depth_three_catalog()
            catalog.write_text(
                "".join(
                    json.dumps(leaf, sort_keys=True, separators=(",", ":")) + "\n"
                    for leaf in leaves
                ),
                encoding="ascii",
            )
            formula = root / "profile.cnf"
            formula.write_text("p cnf 1 1\n1 0\n", encoding="ascii")
            proof_bytes = b"0\n"
            proof_hash = hashlib.sha256(proof_bytes).hexdigest()
            for index, leaf in enumerate(leaves):
                name = f"leaf-{index:08d}"
                (proofs / f"{name}.drat").write_bytes(proof_bytes)
                record = {
                    "index": index,
                    "masks": leaf["masks"],
                    "literals": [],
                    "file": f"proofs/{name}.drat",
                    "bytes": len(proof_bytes),
                    "sha256": proof_hash,
                    "replay": (
                        "drat-trim -> LRAT -> lrat-check; projected DRAT -> drat-trim"
                    ),
                    "solver_options": ["--unsat", "-q", "-P2"],
                    "status": "VERIFIED",
                }
                (checkpoints / f"{name}.json").write_text(
                    json.dumps(record, sort_keys=True) + "\n",
                    encoding="ascii",
                )
            with patch(
                "search.z10_23_cube_finalize.subprocess.run",
                return_value=SimpleNamespace(stdout="sc2021"),
            ):
                metadata = finalize(PROFILE, catalog, work, formula)
            self.assertEqual(metadata["status"], "VERIFIED_CUBE_LEAF_PROOFS")
            self.assertEqual(metadata["catalog"]["count"], len(leaves))
            self.assertEqual(metadata["proof_index"]["count"], len(leaves))
            self.assertEqual(
                len((work / "proof-index.jsonl").read_text().splitlines()),
                len(leaves),
            )
            (proofs / "unexpected.drat").write_bytes(proof_bytes)
            with (
                patch(
                    "search.z10_23_cube_finalize.subprocess.run",
                    return_value=SimpleNamespace(stdout="sc2021"),
                ),
                self.assertRaises(RuntimeError),
            ):
                finalize(PROFILE, catalog, work, formula)


if __name__ == "__main__":
    unittest.main()
