from __future__ import annotations

import itertools
import random
import tempfile
import unittest
from pathlib import Path

from finite_zarankiewicz_closures.encodings import (
    CNF,
    add_at_most,
    add_exactly,
    build_cell_cnf,
    column_constraints_hold,
    column_counts,
    column_type_lp_text,
    write_cell_cnf,
)


def _satisfiable(clauses: list[tuple[int, ...]], assumptions: list[int]) -> bool:
    """Tiny DPLL oracle used only for exhaustive tests of small encodings."""

    initial = {abs(literal): literal > 0 for literal in assumptions}
    if any(initial[abs(literal)] != (literal > 0) for literal in assumptions):
        return False

    def search(assignment: dict[int, bool]) -> bool:
        while True:
            unit = None
            unresolved_clauses: list[list[int]] = []
            for clause in clauses:
                unresolved = [literal for literal in clause if abs(literal) not in assignment]
                if any(assignment.get(abs(literal)) == (literal > 0) for literal in clause):
                    continue
                if not unresolved:
                    return False
                if len(unresolved) == 1:
                    unit = unresolved[0]
                    break
                unresolved_clauses.append(unresolved)
            if unit is None:
                if not unresolved_clauses:
                    return True
                chosen = min(unresolved_clauses, key=len)[0]
                for literal in (chosen, -chosen):
                    branch = assignment.copy()
                    branch[abs(literal)] = literal > 0
                    if search(branch):
                        return True
                return False
            variable = abs(unit)
            value = unit > 0
            if variable in assignment and assignment[variable] != value:
                return False
            assignment[variable] = value

    return search(initial)


def _is_k33_free(matrix: list[list[int]]) -> bool:
    return not any(
        all(matrix[row][column] for row in rows for column in columns)
        for rows in itertools.combinations(range(len(matrix)), 3)
        for columns in itertools.combinations(range(len(matrix[0])), 3)
    )


class EncodingTests(unittest.TestCase):
    def test_at_most_circuit_is_exhaustive_on_small_inputs(self) -> None:
        for size in range(1, 7):
            for bound in range(size + 1):
                cnf = CNF(variables=size)
                add_at_most(cnf, list(range(1, size + 1)), bound)
                for bits in itertools.product((0, 1), repeat=size):
                    assumptions = [index + 1 if bit else -(index + 1) for index, bit in enumerate(bits)]
                    observed = _satisfiable(cnf.clauses, assumptions)
                    self.assertEqual(observed, sum(bits) <= bound, (size, bound, bits))

    def test_exactly_circuit_and_signed_literals_are_exhaustive(self) -> None:
        for size in range(1, 7):
            for target in range(size + 1):
                cnf = CNF(variables=size)
                add_exactly(cnf, list(range(1, size + 1)), target)
                signed = CNF(variables=size)
                # Alternating signs exercise the lower-bound circuit's signed inputs.
                literals = [index if index % 2 else -index for index in range(1, size + 1)]
                add_at_most(signed, literals, target)
                for bits in itertools.product((0, 1), repeat=size):
                    assumptions = [
                        index + 1 if bit else -(index + 1)
                        for index, bit in enumerate(bits)
                    ]
                    self.assertEqual(
                        _satisfiable(cnf.clauses, assumptions),
                        sum(bits) == target,
                        ("exactly", size, target, bits),
                    )
                    literal_count = sum(
                        bit if literal > 0 else 1 - bit
                        for literal, bit in zip(literals, bits)
                    )
                    self.assertEqual(
                        _satisfiable(signed.clauses, assumptions),
                        literal_count <= target,
                        ("signed", size, target, bits),
                    )

    def test_cell_forbidders_are_complete_and_unique(self) -> None:
        cnf, metadata = build_cell_cnf(4, 5, 7)
        expected = set()
        for rows in itertools.combinations(range(4), 3):
            for columns in itertools.combinations(range(5), 3):
                expected.add(tuple(-(row * 5 + column + 1) for row in rows for column in columns))
        self.assertEqual(set(cnf.clauses[: len(expected)]), expected)
        self.assertEqual(metadata["forbidden_submatrix_clauses"], 40)

    def test_known_small_value_z_3_4_is_ten(self) -> None:
        maxima = 0
        for bits in itertools.product((0, 1), repeat=12):
            matrix = [list(bits[row * 4 : (row + 1) * 4]) for row in range(3)]
            if _is_k33_free(matrix):
                maxima = max(maxima, sum(bits))
        self.assertEqual(maxima, 10)

    def test_column_formulation_matches_direct_semantics_on_random_matrices(self) -> None:
        rng = random.Random(20260704)
        for _ in range(100):
            matrix = [[rng.randrange(2) for _ in range(6)] for _ in range(5)]
            weight = sum(map(sum, matrix))
            observed = column_constraints_hold(
                column_counts(matrix), rows=5, columns=6, target_ones=weight
            )
            self.assertEqual(observed, _is_k33_free(matrix))

    def test_column_model_has_every_required_constraint(self) -> None:
        text, metadata = column_type_lp_text(9, 23, 104)
        self.assertEqual(metadata["support_variables"], 512)
        self.assertEqual(metadata["row_triple_constraints"], 84)
        self.assertEqual(text.count("\n triple_"), 84)
        self.assertTrue(text.endswith("End\n"))

    def test_dimacs_header_matches_generated_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "small.cnf"
            metadata = write_cell_cnf(path, rows=3, columns=4, target_ones=10)
            lines = path.read_text(encoding="ascii").splitlines()
            header = next(line for line in lines if line.startswith("p cnf ")).split()
            clauses = [line for line in lines if line and line[0] not in {"c", "p"}]
            self.assertEqual(int(header[2]), metadata["variables_total"])
            self.assertEqual(int(header[3]), len(clauses))
            self.assertTrue(all(line.endswith(" 0") for line in clauses))


if __name__ == "__main__":
    unittest.main()
