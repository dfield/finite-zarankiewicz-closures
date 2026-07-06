#!/usr/bin/env python3
"""Validate generated formulations on known and randomized small instances.

The pure-Python test suite exhaustively audits each encoding component.  This
script adds implementation diversity by asking an installed CaDiCaL binary to
solve complete small CNFs.  It also compares the column-type constraints with
direct matrix semantics on a fixed random sample.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.encodings import (  # noqa: E402
    build_cell_cnf,
    cell_variable,
    column_constraints_hold,
    column_counts,
    dimacs_text,
)


SEED = 20260704


def direct_k33_free(matrix: list[list[int]]) -> bool:
    """Return the definition directly, without using project verifiers."""

    return not any(
        all(matrix[row][column] for row in rows for column in columns)
        for rows in itertools.combinations(range(len(matrix)), 3)
        for columns in itertools.combinations(range(len(matrix[0])), 3)
    )


def cadical_solve(executable: str, path: Path) -> bool:
    """Run CaDiCaL and translate its conventional 10/20 exit status."""

    completed = subprocess.run(
        [executable, "--quiet", str(path)],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    if completed.returncode == 10:
        return True
    if completed.returncode == 20:
        return False
    raise RuntimeError(
        f"CaDiCaL returned {completed.returncode}: {completed.stdout[-1000:]}"
    )


def solve_instance(
    executable: str,
    directory: Path,
    matrix: list[list[int]] | None,
    *,
    rows: int,
    columns: int,
    target: int,
) -> bool:
    """Generate a small CNF, optionally fix every cell, and solve it."""

    cnf, _ = build_cell_cnf(rows, columns, target)
    if matrix is not None:
        for row in range(rows):
            for column in range(columns):
                variable = cell_variable(row, column, columns)
                cnf.add_clause(variable if matrix[row][column] else -variable)
    path = directory / f"instance_{rows}_{columns}_{target}_{len(list(directory.iterdir()))}.cnf"
    path.write_text(dimacs_text(cnf), encoding="ascii")
    return cadical_solve(executable, path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional JSON report path")
    parser.add_argument(
        "--random-cases", type=int, default=30, help="number of seeded fixed matrices"
    )
    args = parser.parse_args()

    cadical = shutil.which("cadical")
    if cadical is None:
        print("CaDiCaL is required for this implementation-diverse validation.", file=sys.stderr)
        return 2
    version = subprocess.run(
        [cadical, "--version"], check=False, capture_output=True, text=True
    ).stdout.strip()
    rng = random.Random(SEED)
    random_reports: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory(prefix="z9-23-validation-") as raw_directory:
        directory = Path(raw_directory)
        known = []
        for target, expected in ((10, True), (11, False)):
            observed = solve_instance(
                cadical, directory, None, rows=3, columns=4, target=target
            )
            row = {
                "problem": "Z(3,4,3,3)",
                "target": target,
                "expected_satisfiable": expected,
                "observed_satisfiable": observed,
            }
            if observed != expected:
                raise AssertionError(row)
            known.append(row)

        for index in range(args.random_cases):
            matrix = [[rng.randrange(2) for _ in range(6)] for _ in range(5)]
            weight = sum(map(sum, matrix))
            expected = direct_k33_free(matrix)
            cell_observed = solve_instance(
                cadical,
                directory,
                matrix,
                rows=5,
                columns=6,
                target=weight,
            )
            column_observed = column_constraints_hold(
                column_counts(matrix), rows=5, columns=6, target_ones=weight
            )
            report = {
                "index": index,
                "ones": weight,
                "direct_k33_free": expected,
                "cell_cnf_satisfiable_when_fixed": cell_observed,
                "column_constraints_hold": column_observed,
            }
            if cell_observed != expected or column_observed != expected:
                raise AssertionError(report)
            random_reports.append(report)

    result = {
        "status": "VERIFIED",
        "solver": {"name": "CaDiCaL", "version": version},
        "seed": SEED,
        "known_cases": known,
        "random_fixed_matrices": random_reports,
        "scope": (
            "Small-instance semantic validation only; the mathematical proofs, not raw-cell "
            "solver runs, establish the six excluded-target impossibility claims."
        ),
    }
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = args.output if args.output.is_absolute() else ROOT / args.output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
