"""Deterministic generators for two exact decision formulations.

The cell model is a DIMACS CNF over one variable per matrix entry, plus a
fully defined threshold circuit for the exact-weight constraint.  The
column-type model is an LP/MIP file with one nonnegative integer variable for
each of the 512 possible column supports.

These generators are not needed for the human upper-bound proof.  They make
the original decision problem reproducible and provide an independent way to
cross-check the subset translation used by the proof.
"""

from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence, Union


ClauseTerm = Union[int, bool]


@dataclass
class CNF:
    """A small DIMACS builder with explicit variable allocation."""

    variables: int
    clauses: list[tuple[int, ...]] = field(default_factory=list)

    def new_variable(self) -> int:
        self.variables += 1
        return self.variables

    def add_clause(self, *terms: ClauseTerm) -> None:
        """Add a clause while simplifying Boolean constants and duplicates."""

        if any(term is True for term in terms):
            return
        literals: list[int] = []
        seen: set[int] = set()
        for term in terms:
            if term is False:
                continue
            if type(term) is not int or term == 0:
                raise ValueError(f"invalid clause term: {term!r}")
            if -term in seen:
                return
            if term not in seen:
                seen.add(term)
                literals.append(term)
        self.clauses.append(tuple(literals))


def _negate(term: ClauseTerm) -> ClauseTerm:
    if term is True:
        return False
    if term is False:
        return True
    return -term


def add_at_most(cnf: CNF, literals: Sequence[int], bound: int) -> None:
    """Encode ``sum(literals) <= bound`` with an exact threshold circuit.

    For each prefix and threshold, an auxiliary variable is defined to mean
    "at least this many prefix literals are true."  Encoding the equivalence,
    rather than only one implication, costs a few clauses but makes the model
    especially easy to audit and gives each base assignment a unique extension.
    Signed input literals are supported.
    """

    n = len(literals)
    if bound >= n:
        return
    if bound < 0:
        cnf.add_clause()  # the empty clause is immediate contradiction
        return
    threshold_limit = bound + 1
    previous: dict[int, int] = {}
    for prefix_size, literal in enumerate(literals, start=1):
        current: dict[int, int] = {}
        for threshold in range(1, min(prefix_size, threshold_limit) + 1):
            z = cnf.new_variable()
            current[threshold] = z
            a: ClauseTerm = previous.get(threshold, False)
            b: ClauseTerm = True if threshold == 1 else previous.get(threshold - 1, False)
            # z <-> (a OR (literal AND b)).
            cnf.add_clause(-z, a, literal)
            cnf.add_clause(-z, a, b)
            cnf.add_clause(_negate(a), z)
            cnf.add_clause(-literal, _negate(b), z)
        previous = current
    cnf.add_clause(-previous[threshold_limit])


def add_exactly(cnf: CNF, literals: Sequence[int], target: int) -> None:
    """Encode an exact cardinality as two independently allocated bounds."""

    if not 0 <= target <= len(literals):
        cnf.add_clause()
        return
    add_at_most(cnf, literals, target)
    add_at_most(cnf, [-literal for literal in literals], len(literals) - target)


def cell_variable(row: int, column: int, columns: int) -> int:
    """Return the one-based DIMACS identifier for a zero-based matrix cell."""

    return row * columns + column + 1


def build_cell_cnf(rows: int, columns: int, target_ones: int) -> tuple[CNF, dict[str, int]]:
    """Build the direct exact-weight cell formulation.

    There is one nine-literal negative clause for every choice of three rows
    and three columns.  Such a clause is false exactly when that 3-by-3
    submatrix is all one.
    """

    if rows < 3 or columns < 3:
        raise ValueError("the K_3,3 formulation requires at least three rows and columns")
    base_variables = rows * columns
    cnf = CNF(variables=base_variables)
    forbidden = 0
    for row_triple in itertools.combinations(range(rows), 3):
        for column_triple in itertools.combinations(range(columns), 3):
            cnf.add_clause(
                *(
                    -cell_variable(row, column, columns)
                    for row in row_triple
                    for column in column_triple
                )
            )
            forbidden += 1
    add_exactly(cnf, list(range(1, base_variables + 1)), target_ones)
    metadata = {
        "rows": rows,
        "columns": columns,
        "target_ones": target_ones,
        "base_cell_variables": base_variables,
        "forbidden_submatrix_clauses": forbidden,
        "variables_total": cnf.variables,
        "clauses_total": len(cnf.clauses),
    }
    return cnf, metadata


def dimacs_text(cnf: CNF, comments: Iterable[str] = ()) -> str:
    """Serialize a CNF deterministically in DIMACS format."""

    lines = [f"c {comment}" for comment in comments]
    lines.append(f"p cnf {cnf.variables} {len(cnf.clauses)}")
    lines.extend(" ".join(map(str, clause)) + (" " if clause else "") + "0" for clause in cnf.clauses)
    return "\n".join(lines) + "\n"


def write_cell_cnf(path: Path, *, rows: int = 9, columns: int = 23, target_ones: int = 104) -> dict[str, int | str]:
    """Generate the target DIMACS file and return content-derived metadata."""

    cnf, metadata = build_cell_cnf(rows, columns, target_ones)
    text = dimacs_text(
        cnf,
        comments=(
            f"Z({rows},{columns},3,3) exact-{target_ones} direct cell encoding",
            f"cell(row,column) = row*{columns} + column + 1, with zero-based indices",
            "exact weight uses fully defined sequential threshold circuits",
        ),
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="ascii")
    return {**metadata, "sha256": hashlib.sha256(text.encode("ascii")).hexdigest()}


def _support_name(mask: int, rows: int) -> str:
    width = max(1, (rows + 3) // 4)
    return f"x_{mask:0{width}x}"


def _popcount(mask: int) -> int:
    """Count support bits on Python versions predating ``int.bit_count``."""

    return bin(mask).count("1")


def _wrapped_sum(terms: Sequence[str], *, indent: str = "    ", width: int = 100) -> str:
    """Format an LP sum without relying on parser-specific long-line limits."""

    if not terms:
        return "0"
    lines: list[str] = []
    current = ""
    for index, term in enumerate(terms):
        token = term if index == 0 else f" + {term}"
        if current and len(indent) + len(current) + len(token) > width:
            lines.append(current)
            current = f"+ {term}"
        else:
            current += token
    lines.append(current)
    return ("\n" + indent).join(lines)


def column_type_lp_text(rows: int, columns: int, target_ones: int) -> tuple[str, dict[str, int]]:
    """Return an LP/MIP model with one variable per exact column support."""

    masks = list(range(1 << rows))
    names = {mask: _support_name(mask, rows) for mask in masks}
    lines = [
        f"\\ Exact column-type model for Z({rows},{columns},3,3) at {target_ones} ones",
        "Minimize",
        f" feasibility: 0 {names[0]}",
        "Subject To",
        " columns: " + _wrapped_sum([names[mask] for mask in masks]) + f" = {columns}",
        " ones: "
        + _wrapped_sum(
            [f"{_popcount(mask)} {names[mask]}" for mask in masks if _popcount(mask)]
        )
        + f" = {target_ones}",
    ]
    triple_constraints = 0
    for triple in itertools.combinations(range(rows), 3):
        triple_mask = sum(1 << row for row in triple)
        containing = [names[mask] for mask in masks if mask & triple_mask == triple_mask]
        label = "triple_" + "_".join(map(str, triple))
        lines.append(f" {label}: " + _wrapped_sum(containing) + " <= 2")
        triple_constraints += 1
    lines.append("Bounds")
    lines.extend(f" 0 <= {names[mask]} <= {columns}" for mask in masks)
    lines.append("Generals")
    lines.extend(f" {names[mask]}" for mask in masks)
    lines.append("End")
    text = "\n".join(lines) + "\n"
    metadata = {
        "rows": rows,
        "columns": columns,
        "target_ones": target_ones,
        "support_variables": len(masks),
        "row_triple_constraints": triple_constraints,
        "structural_constraints": triple_constraints + 2,
    }
    return text, metadata


def write_column_type_lp(path: Path, *, rows: int = 9, columns: int = 23, target_ones: int = 104) -> dict[str, int | str]:
    """Generate the target LP file and return content-derived metadata."""

    text, metadata = column_type_lp_text(rows, columns, target_ones)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="ascii")
    return {**metadata, "sha256": hashlib.sha256(text.encode("ascii")).hexdigest()}


def column_counts(matrix: Sequence[Sequence[int]]) -> list[int]:
    """Convert a Boolean matrix to the 512-entry support histogram."""

    if not matrix or not matrix[0]:
        raise ValueError("matrix must be nonempty")
    rows = len(matrix)
    columns = len(matrix[0])
    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix is not rectangular")
    if any(type(value) is not int or value not in (0, 1) for row in matrix for value in row):
        raise ValueError("matrix entries must be integer zeros or ones")
    counts = [0] * (1 << rows)
    for column in range(columns):
        mask = sum(matrix[row][column] << row for row in range(rows))
        counts[mask] += 1
    return counts


def column_constraints_hold(counts: Sequence[int], *, rows: int, columns: int, target_ones: int) -> bool:
    """Evaluate the mathematical column-type constraints without parsing LP."""

    if len(counts) != 1 << rows or any(type(value) is not int or value < 0 for value in counts):
        return False
    if sum(counts) != columns:
        return False
    if sum(_popcount(mask) * count for mask, count in enumerate(counts)) != target_ones:
        return False
    for triple in itertools.combinations(range(rows), 3):
        triple_mask = sum(1 << row for row in triple)
        if sum(count for mask, count in enumerate(counts) if mask & triple_mask == triple_mask) > 2:
            return False
    return True
