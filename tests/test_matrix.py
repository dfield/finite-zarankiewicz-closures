from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from finite_zarankiewicz_closures.matrix import read_boolean_csv, verify_by_row_triples


ROOT = Path(__file__).resolve().parents[1]
WITNESS = ROOT / "data" / "z9_23_103_matrix.csv"


class WitnessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.matrix = read_boolean_csv(WITNESS)

    def test_witness_has_expected_invariants(self) -> None:
        result = verify_by_row_triples(self.matrix, raw_bytes=WITNESS.read_bytes())
        self.assertTrue(result.valid)
        self.assertEqual(result.ones, 103)
        self.assertEqual(result.row_triples_checked, 84)
        self.assertLessEqual(result.maximum_common_columns, 2)
        self.assertEqual(sorted(result.column_sums), [4] * 12 + [5] * 11)

    def test_every_zero_to_one_extension_is_rejected(self) -> None:
        """The witness is maximal as well as extremal by weight."""

        zeroes = [
            (row, column)
            for row in range(9)
            for column in range(23)
            if self.matrix[row][column] == 0
        ]
        for row, column in zeroes:
            mutated = [values[:] for values in self.matrix]
            mutated[row][column] = 1
            result = verify_by_row_triples(mutated, expected_ones=104)
            self.assertFalse(result.valid, (row, column))
            self.assertIsNotNone(result.first_violation, (row, column))

    def test_forced_all_one_submatrix_is_rejected(self) -> None:
        mutated = [row[:] for row in self.matrix]
        for row in (0, 1, 2):
            for column in (0, 1, 2):
                mutated[row][column] = 1
        result = verify_by_row_triples(mutated, expected_ones=sum(map(sum, mutated)))
        self.assertFalse(result.valid)
        self.assertIsNotNone(result.first_violation)

    def test_wrong_dimensions_weight_and_entries_are_rejected(self) -> None:
        self.assertFalse(verify_by_row_triples(self.matrix[:-1]).valid)
        self.assertFalse(verify_by_row_triples(self.matrix, expected_ones=104).valid)
        malformed = [row[:] for row in self.matrix]
        malformed[0][0] = 2
        with self.assertRaises(ValueError):
            verify_by_row_triples(malformed)

    def test_csv_parser_rejects_near_boolean_spellings(self) -> None:
        for bad in ("2", "1.0", "+1", " 1", "", "true"):
            with self.subTest(bad=bad), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.csv"
                path.write_text(f"0,{bad}\n1,0\n", encoding="ascii")
                with self.assertRaises(ValueError):
                    read_boolean_csv(path)

    def test_independent_script_checks_all_submatrices(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "verify_witness_independent.py")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn('"candidate_submatrices_checked": 148764', completed.stdout)


if __name__ == "__main__":
    unittest.main()
