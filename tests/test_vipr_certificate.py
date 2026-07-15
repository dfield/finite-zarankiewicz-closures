from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import unittest

from finite_zarankiewicz_closures.vipr_certificate import (
    ViprCertificateError,
    render_vipr_leaf_formula,
    verify_vipr_embedded_model,
)


ROOT = Path(__file__).resolve().parents[1]


class ViprCertificateTests(unittest.TestCase):
    OPB = """* #variable= 2 #constraint= 2 #equal= 1 intsize= 2
* fixture
+1 x1 -1 x2 >= 0;
+1 x1 +1 x2 = 1;
"""
    VIPR = """VER 1.0
VAR 2
t_x1
t_x2
INT 2
0
1
OBJ min
0
CON 6 4
C0 G 0 2 0 1 1 -1
C1 E 1 2 0 1 1 1
B0 G 0 1 0 1
B1 L 1 1 0 1
B2 G 0 1 1 1
B3 L 1 1 1 1
RTP infeas
SOL 0
DER 1
D0 G 1 0 { lin 0 } -1
"""

    def test_embedded_model_is_bound_coefficient_for_coefficient(self) -> None:
        report = verify_vipr_embedded_model(self.OPB, io.StringIO(self.VIPR))
        self.assertEqual(
            report,
            {"variables": 2, "model_constraints": 2, "bound_constraints": 4},
        )
        mutated = self.VIPR.replace("C0 G 0 2 0 1 1 -1", "C0 G 0 2 0 1 1 -2")
        with self.assertRaises(ViprCertificateError):
            verify_vipr_embedded_model(self.OPB, io.StringIO(mutated))

    def test_stored_leaf_zero_formulas_regenerate_byte_exactly(self) -> None:
        directory = ROOT / "certificates" / "z10_23" / "vipr"
        for profile, catalog_name, manifest_name in (
            (
                "3x1,4x4,5x14,6x4",
                "profile-b-deficit-orbits.jsonl",
                "profile-b-vipr-final-manifest.json",
            ),
            (
                "3x1,4x3,5x16,6x3",
                "profile-c-degree6-orbits.jsonl",
                "profile-c-vipr-final-manifest.json",
            ),
        ):
            with self.subTest(profile=profile):
                record = json.loads(
                    (directory / catalog_name).read_text(encoding="ascii").splitlines()[0]
                )
                manifest = json.loads(
                    (directory / manifest_name).read_text(encoding="ascii")
                )
                formula, _ = render_vipr_leaf_formula(ROOT, profile, record)
                payload = formula.encode("ascii")
                self.assertEqual(len(payload), manifest["leaves"][0]["formula"]["bytes"])
                self.assertEqual(
                    hashlib.sha256(payload).hexdigest(),
                    manifest["leaves"][0]["formula"]["sha256"],
                )


if __name__ == "__main__":
    unittest.main()
