"""Strict parsing and row-triple verification of Boolean matrices.

The main verifier implements the subset formulation from Section 2 of the
human proof.  For every triple of rows it counts columns containing that
triple; a count of three would be a forbidden all-one 3-by-3 submatrix.

``scripts/verify_witness_independent.py`` deliberately does not import this
module.  It performs the slower direct enumeration of all row/column triples,
providing an implementation-diverse check of the same witness.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Sequence


Matrix = list[list[int]]


@dataclass(frozen=True)
class MatrixCheck:
    """Structured result returned by :func:`verify_by_row_triples`.

    ``first_violation`` is zero-indexed when present.  A result is valid only
    when dimensions, entries, weight, and the forbidden-submatrix condition
    all pass; this avoids accidentally accepting a mathematically valid matrix
    for the wrong parameter set.
    """

    valid: bool
    rows: int
    columns: int
    ones: int
    row_sums: tuple[int, ...]
    column_sums: tuple[int, ...]
    row_triples_checked: int
    maximum_common_columns: int
    first_violation: dict[str, list[int]] | None
    sha256: str | None = None

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""

        return asdict(self)


def read_boolean_csv(path: Path) -> Matrix:
    """Read a nonempty rectangular CSV containing only literal ``0``/``1``.

    The parser is intentionally stricter than ``int(cell)``: values such as
    ``+1``, ``1.0``, empty cells, and surrounding whitespace are rejected.
    Silent normalization would make malformed certificate data harder to
    detect during an adversarial audit.
    """

    with path.open(newline="", encoding="ascii") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        raise ValueError("matrix CSV is empty")
    width = len(rows[0])
    if width == 0:
        raise ValueError("matrix CSV has an empty first row")
    if any(len(row) != width for row in rows):
        raise ValueError("matrix CSV is not rectangular")
    for row_number, row in enumerate(rows, start=1):
        for column_number, cell in enumerate(row, start=1):
            if cell not in {"0", "1"}:
                raise ValueError(
                    f"non-Boolean cell at row {row_number}, column {column_number}: {cell!r}"
                )
    return [[1 if cell == "1" else 0 for cell in row] for row in rows]


def _validate_in_memory_matrix(matrix: Sequence[Sequence[int]]) -> tuple[int, int]:
    """Reject malformed in-memory inputs before combinatorial checking."""

    if not matrix:
        raise ValueError("matrix has no rows")
    columns = len(matrix[0])
    if columns == 0:
        raise ValueError("matrix has no columns")
    if any(len(row) != columns for row in matrix):
        raise ValueError("matrix is not rectangular")
    if any(type(value) is not int or value not in (0, 1) for row in matrix for value in row):
        raise ValueError("matrix entries must be integer zeros or ones")
    return len(matrix), columns


def verify_by_row_triples(
    matrix: Sequence[Sequence[int]],
    *,
    expected_rows: int = 9,
    expected_columns: int = 23,
    expected_ones: int = 103,
    raw_bytes: bytes | None = None,
) -> MatrixCheck:
    """Verify dimensions, weight, and :math:`K_{3,3}`-freeness.

    For each row triple ``T``, the checker computes the columns whose supports
    contain ``T``.  At most two such columns are allowed.  This checks all 84
    row triples for the target instance and is equivalent to checking every
    possible 3-by-3 all-one submatrix.
    """

    rows, columns = _validate_in_memory_matrix(matrix)
    row_sums = tuple(sum(row) for row in matrix)
    column_sums = tuple(sum(matrix[row][column] for row in range(rows)) for column in range(columns))
    checked = 0
    maximum_common = 0
    first_violation: dict[str, list[int]] | None = None

    for row_triple in itertools.combinations(range(rows), 3):
        checked += 1
        common = [
            column
            for column in range(columns)
            if all(matrix[row][column] == 1 for row in row_triple)
        ]
        maximum_common = max(maximum_common, len(common))
        if len(common) >= 3 and first_violation is None:
            first_violation = {
                "rows": list(row_triple),
                "columns": common[:3],
            }

    ones = sum(row_sums)
    valid = (
        rows == expected_rows
        and columns == expected_columns
        and ones == expected_ones
        and first_violation is None
    )
    digest = hashlib.sha256(raw_bytes).hexdigest() if raw_bytes is not None else None
    return MatrixCheck(
        valid=valid,
        rows=rows,
        columns=columns,
        ones=ones,
        row_sums=row_sums,
        column_sums=column_sums,
        row_triples_checked=checked,
        maximum_common_columns=maximum_common,
        first_violation=first_violation,
        sha256=digest,
    )
