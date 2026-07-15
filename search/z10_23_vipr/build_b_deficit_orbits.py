#!/usr/bin/env python3
"""Build the complete S3 x S7 orbit cover of profile-B triple deficits."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import re
from typing import Any


ROWS = 10
TRIPLES = tuple(itertools.combinations(range(ROWS), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
FIXED_TRIPLE = TRIPLE_INDEX[(0, 1, 2)]
GENERATORS = (
    (0, 1),
    (1, 2),
    *zip(range(3, 9), range(4, 10)),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def transformations() -> tuple[tuple[int, ...], ...]:
    result = []
    for first, second in GENERATORS:
        moved = []
        for triple in TRIPLES:
            image = tuple(
                sorted(
                    second if row == first else first if row == second else row
                    for row in triple
                )
            )
            moved.append(TRIPLE_INDEX[image])
        result.append(tuple(moved))
    return tuple(result)


def moved(state: tuple[int, int, int], transformation: tuple[int, ...]) -> tuple[int, int, int]:
    return tuple(sorted(transformation[index] for index in state))


def enumerate_orbits() -> list[tuple[tuple[int, int, int], int]]:
    maps = transformations()
    seen: set[tuple[int, int, int]] = set()
    orbits: list[tuple[tuple[int, int, int], int]] = []
    state_count = 0
    for state in itertools.combinations_with_replacement(range(len(TRIPLES)), 3):
        if state[0] == state[2] or state.count(FIXED_TRIPLE) > 1:
            continue
        state_count += 1
        if state in seen:
            continue
        orbit = {state}
        frontier = [state]
        while frontier:
            current = frontier.pop()
            for transformation in maps:
                image = moved(current, transformation)
                if image not in orbit:
                    orbit.add(image)
                    frontier.append(image)
        seen.update(orbit)
        orbits.append((min(orbit), len(orbit)))
    if state_count != 295001 or len(seen) != state_count or len(orbits) != 209:
        raise RuntimeError(
            f"unexpected orbit census: states={state_count}, seen={len(seen)}, orbits={len(orbits)}"
        )
    if sum(size for _, size in orbits) != state_count:
        raise RuntimeError("orbit sizes do not partition the state census")
    return sorted(orbits)


def triple_variables(path: Path) -> dict[tuple[int, int, int], list[tuple[int, int]]]:
    result: dict[tuple[int, int, int], list[tuple[int, int]]] = {}
    with path.open(encoding="ascii") as handle:
        for line in handle:
            record = json.loads(line)
            if record.get("kind") != "triple_deficit":
                continue
            label = tuple(record["label"])
            result.setdefault(label, []).append((record["threshold"], record["variable"]))
    for label, variables in result.items():
        variables.sort()
        bound = 1 if label == (0, 1, 2) else 2
        if [threshold for threshold, _ in variables] != list(range(1, bound + 1)):
            raise RuntimeError(f"bad deficit variable map for {label}")
    if set(result) != set(TRIPLES):
        raise RuntimeError("deficit variable map does not cover every row triple")
    return result


def leaf_formula(base: Path, units: list[int], destination: Path) -> None:
    lines = base.read_text(encoding="ascii").splitlines()
    match = re.fullmatch(
        r"\* #variable= (\d+) #constraint= (\d+) #equal= (\d+) intsize= (\d+)",
        lines[0],
    )
    if match is None:
        raise RuntimeError("unexpected OPB header")
    variables, constraints, equalities, integer_size = map(int, match.groups())
    lines[0] = (
        f"* #variable= {variables} #constraint= {constraints + len(units)} "
        f"#equal= {equalities} intsize= {integer_size}"
    )
    lines.extend(
        f"+1 x{literal} >= 1;" if literal > 0 else f"-1 x{-literal} >= 0;"
        for literal in units
    )
    destination.write_text("\n".join(lines) + "\n", encoding="ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--formula", type=Path, required=True)
    parser.add_argument("--variables", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-formulas", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    variables = triple_variables(args.variables)
    records: list[dict[str, Any]] = []
    for index, (state, orbit_size) in enumerate(enumerate_orbits()):
        multiplicity = {triple_index: state.count(triple_index) for triple_index in set(state)}
        units = []
        for triple in TRIPLES:
            deficit = multiplicity.get(TRIPLE_INDEX[triple], 0)
            for threshold, variable in variables[triple]:
                units.append(variable if threshold <= deficit else -variable)
        if len(units) != 239 or len({abs(literal) for literal in units}) != 239:
            raise RuntimeError("leaf does not assign all triple-deficit variables")
        records.append(
            {
                "index": index,
                "deficit_triples": [list(TRIPLES[item]) for item in state],
                "orbit_size": orbit_size,
                "units": units,
            }
        )
    catalog = args.output / "profile-b-deficit-orbits.jsonl"
    with catalog.open("w", encoding="ascii") as handle:
        for record in records:
            handle.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")
    metadata = {
        "schema_version": 1,
        "status": "COMPLETE_ORBIT_COVER",
        "profile": "3x1,4x4,5x14,6x4",
        "triple_deficit": 3,
        "fixed_degree_three_support": [0, 1, 2],
        "group": "S_3 x S_7 stabilizer of the fixed support",
        "generators": [list(pair) for pair in GENERATORS],
        "raw_state_count": 295001,
        "orbit_count": len(records),
        "orbit_size_sum": sum(record["orbit_size"] for record in records),
        "unit_count_per_leaf": 239,
        "formula": {
            "file": args.formula.name,
            "bytes": args.formula.stat().st_size,
            "sha256": sha256(args.formula),
        },
        "variable_map": {
            "file": args.variables.name,
            "bytes": args.variables.stat().st_size,
            "sha256": sha256(args.variables),
        },
        "catalog": {
            "file": catalog.name,
            "bytes": catalog.stat().st_size,
            "sha256": sha256(catalog),
            "records": len(records),
        },
    }
    metadata_path = args.output / "profile-b-deficit-orbits.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="ascii")
    if args.sample_formulas:
        args.sample_formulas.mkdir(parents=True, exist_ok=True)
        for record in records[:3]:
            leaf_formula(
                args.formula,
                record["units"],
                args.sample_formulas / f"leaf-{record['index']:06d}.opb",
            )
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
