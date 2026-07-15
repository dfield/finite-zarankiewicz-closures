#!/usr/bin/env python3
"""Build native pseudo-Boolean support-count models for profiles B and C."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
from typing import Iterable


ROWS = 10
COLUMNS = 23
FIXED_SUPPORT = 7
PROFILES = {
    "B": {3: 1, 4: 4, 5: 14, 6: 4},
    "C": {3: 1, 4: 3, 5: 16, 6: 3},
}


def popcount(mask: int) -> int:
    return bin(mask).count("1")


def masks_of_size(size: int) -> list[int]:
    return [mask for mask in range(1 << ROWS) if popcount(mask) == size]


def swapped_mask(mask: int, first: int, second: int) -> int:
    first_bit = bool(mask & (1 << first))
    second_bit = bool(mask & (1 << second))
    return mask if first_bit == second_bit else mask ^ (1 << first) ^ (1 << second)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def terms(coefficients: Iterable[tuple[int, int]]) -> str:
    rendered = [f"{coefficient:+d} x{variable}" for coefficient, variable in coefficients if coefficient]
    return " ".join(rendered) if rendered else "+0 x1"


def build(
    profile_name: str,
    deficit_links: str = "none",
    row_symmetry: str = "degree-order",
    deficit_incidence_links: bool = False,
    triple_deficits: dict[tuple[int, int, int], int] | None = None,
    complete_degree_supports: tuple[int, ...] | None = None,
) -> tuple[str, list[dict[str, object]], dict[str, object]]:
    profile = PROFILES[profile_name]
    if deficit_links not in {"none", "triple", "all"}:
        raise ValueError(f"unknown deficit-link mode: {deficit_links}")
    if row_symmetry not in {"none", "degree-order", "adjacent-lex", "all-transpositions"}:
        raise ValueError(f"unknown row-symmetry mode: {row_symmetry}")
    if deficit_incidence_links and deficit_links != "all":
        raise ValueError("deficit-incidence links require --deficit-links all")
    all_triples = tuple(itertools.combinations(range(ROWS), 3))
    if triple_deficits is not None:
        if set(triple_deficits) != set(all_triples):
            raise ValueError("a leaf must assign the deficit of every row triple")
        expected_deficit = 240 - sum(
            profile[degree] * len(tuple(itertools.combinations(range(degree), 3)))
            for degree in profile
        )
        if sum(triple_deficits.values()) != expected_deficit:
            raise ValueError("leaf triple deficits have the wrong total")
        for triple, deficit in triple_deficits.items():
            bound = 2 - int(triple == (0, 1, 2))
            if not 0 <= deficit <= bound:
                raise ValueError(f"invalid deficit {deficit} for triple {triple}")
    fixed_degree: int | None = None
    if complete_degree_supports is not None:
        if not complete_degree_supports:
            raise ValueError("a complete support multiset must be nonempty")
        fixed_degree = popcount(complete_degree_supports[0])
        if fixed_degree not in (4, 5, 6):
            raise ValueError("fixed supports must have degree four, five, or six")
        if (
            len(complete_degree_supports) != profile[fixed_degree]
            or any(popcount(mask) != fixed_degree for mask in complete_degree_supports)
            or any(not 0 <= mask < (1 << ROWS) for mask in complete_degree_supports)
        ):
            raise ValueError("fixed supports do not form the complete requested degree group")
        if any(complete_degree_supports.count(mask) > 2 for mask in complete_degree_supports):
            raise ValueError("support multiplicity exceeds the unary domain")
    masks = [mask for degree in (4, 5, 6) for mask in masks_of_size(degree)]
    variables: dict[tuple[int, int], int] = {}
    mapping: list[dict[str, object]] = []
    for mask in masks:
        for occurrence in (1, 2):
            variable = len(variables) + 1
            variables[(mask, occurrence)] = variable
            mapping.append(
                {
                    "variable": variable,
                    "mask": mask,
                    "occurrence": occurrence,
                    "support": [row for row in range(ROWS) if mask & (1 << row)],
                }
            )

    next_variable = len(variables) + 1

    def auxiliary(kind: str, **fields: object) -> int:
        nonlocal next_variable
        variable = next_variable
        next_variable += 1
        mapping.append({"variable": variable, "kind": kind, **fields})
        return variable

    def unary_slack(kind: str, label: list[int], bound: int) -> list[int]:
        slack = [
            auxiliary(kind, label=label, threshold=threshold)
            for threshold in range(1, bound + 1)
        ]
        for first, second in zip(slack, slack[1:]):
            constraints.append(f"+1 x{first} -1 x{second} >= 0;")
        return slack

    constraints: list[str] = []
    groups: dict[str, int] = {}

    def clause(literals: list[int]) -> None:
        negative = sum(literal < 0 for literal in literals)
        coefficients = [
            (1, literal) if literal > 0 else (-1, -literal)
            for literal in literals
        ]
        constraints.append(f"{terms(coefficients)} >= {1 - negative};")

    def add_lex_ge(
        left: list[int],
        right: list[int],
        generator: tuple[int, int],
    ) -> None:
        equal: list[int] = []
        for index, (u, v) in enumerate(zip(left, right)):
            if index == 0:
                clause([u, -v])
            else:
                clause([-equal[index - 1], u, -v])
            current = auxiliary(
                "row_lex_prefix_equal",
                generator=list(generator),
                position=index,
            )
            equal.append(current)
            if index == 0:
                clause([-current, u, -v])
                clause([-current, -u, v])
                clause([current, u, v])
                clause([current, -u, -v])
            else:
                previous = equal[index - 1]
                clause([-current, previous])
                clause([-current, u, -v])
                clause([-current, -u, v])
                clause([current, -previous, u, v])
                clause([current, -previous, -u, -v])

    start = len(constraints)
    for mask in masks:
        constraints.append(
            f"+1 x{variables[(mask, 1)]} -1 x{variables[(mask, 2)]} >= 0;"
        )
    groups["multiplicity_monotonicity"] = len(constraints) - start

    symmetry_generators: list[list[int]] = []
    if row_symmetry in {"adjacent-lex", "all-transpositions"}:
        start = len(constraints)
        semantic_keys = sorted(variables)
        if row_symmetry == "adjacent-lex":
            generators = (
                (0, 1),
                (1, 2),
                *zip(range(3, 9), range(4, 10)),
            )
        else:
            generators = (
                *itertools.combinations(range(3), 2),
                *itertools.combinations(range(3, 10), 2),
            )
        for generator in generators:
            first, second = generator
            moved = [
                key
                for key in semantic_keys
                if swapped_mask(key[0], first, second) != key[0]
            ]
            add_lex_ge(
                [variables[key] for key in moved],
                [
                    variables[(swapped_mask(mask, first, second), occurrence)]
                    for mask, occurrence in moved
                ],
                generator,
            )
            symmetry_generators.append(list(generator))
        groups["row_stabilizer_lex_leaders"] = len(constraints) - start

    start = len(constraints)
    for degree in (4, 5, 6):
        variables_in_group = [
            variables[(mask, occurrence)]
            for mask in masks
            if popcount(mask) == degree
            for occurrence in (1, 2)
        ]
        constraints.append(
            f"{terms((1, variable) for variable in variables_in_group)} = {profile[degree]};"
        )
    groups["degree_group_equalities"] = len(constraints) - start

    if complete_degree_supports is not None:
        start = len(constraints)
        for mask in sorted(set(complete_degree_supports)):
            for occurrence in range(1, complete_degree_supports.count(mask) + 1):
                constraints.append(f"+1 x{variables[(mask, occurrence)]} = 1;")
        groups["complete_degree_support_fixing"] = len(constraints) - start

    triple_incidence = 1 + sum(
        profile[degree] * len(list(itertools.combinations(range(degree), 3)))
        for degree in (4, 5, 6)
    )
    triple_deficit = 2 * len(list(itertools.combinations(range(ROWS), 3))) - triple_incidence
    triple_slack: list[int] = []
    triple_slack_by_triple: dict[tuple[int, int, int], list[int]] = {}
    start = len(constraints)
    for triple in all_triples:
        triple_mask = sum(1 << row for row in triple)
        bound = 2 - int(triple_mask == FIXED_SUPPORT)
        contained = [
            variables[(mask, occurrence)]
            for mask in masks
            if mask & triple_mask == triple_mask
            for occurrence in (1, 2)
        ]
        if triple_deficits is not None:
            constraints.append(
                f"{terms((1, variable) for variable in contained)} = "
                f"{bound - triple_deficits[triple]};"
            )
        elif deficit_links in {"triple", "all"}:
            slack = unary_slack("triple_deficit", list(triple), bound)
            triple_slack.extend(slack)
            triple_slack_by_triple[triple] = slack
            constraints.append(
                f"{terms((1, variable) for variable in [*contained, *slack])} = {bound};"
            )
        else:
            constraints.append(
                f"{terms((-1, variable) for variable in contained)} >= {-bound};"
            )
    groups["row_triple_capacities"] = len(constraints) - start
    if triple_slack:
        start = len(constraints)
        constraints.append(
            f"{terms((1, variable) for variable in triple_slack)} = {triple_deficit};"
        )
        groups["global_triple_deficit"] = len(constraints) - start

    row_deficit_total = 3 * triple_deficit
    row_slack: list[int] = []
    row_slack_by_row: dict[int, list[int]] = {}
    start = len(constraints)
    for row in range(ROWS):
        fixed = int(bool(FIXED_SUPPORT & (1 << row)))
        incident = [
            variables[(mask, occurrence)]
            for mask in masks
            if mask & (1 << row)
            for occurrence in (1, 2)
        ]
        constraints.append(f"{terms((1, variable) for variable in incident)} >= {10 - fixed};")
    groups["minimum_row_degrees"] = len(constraints) - start

    # These are exact sums of the relevant triple capacities.  Optional unary
    # slack variables expose their small, globally fixed deficits directly.
    start = len(constraints)
    for row in range(ROWS):
        fixed = int(bool(FIXED_SUPPORT & (1 << row)))
        weighted = [
            ((popcount(mask) - 1) * (popcount(mask) - 2) // 2, variables[(mask, occurrence)])
            for mask in masks
            if mask & (1 << row)
            for occurrence in (1, 2)
        ]
        if deficit_links == "all":
            slack = unary_slack("row_deficit", [row], row_deficit_total)
            row_slack.extend(slack)
            row_slack_by_row[row] = slack
            constraints.append(f"{terms([*weighted, *((1, variable) for variable in slack)])} = {72 - fixed};")
        else:
            constraints.append(f"{terms((-coefficient, variable) for coefficient, variable in weighted)} >= {-72 + fixed};")
    groups["row_triple_aggregate_cuts"] = len(constraints) - start
    if row_slack:
        start = len(constraints)
        constraints.append(
            f"{terms((1, variable) for variable in row_slack)} = {row_deficit_total};"
        )
        groups["global_row_deficit"] = len(constraints) - start

    pair_slack: list[int] = []
    pair_slack_by_pair: dict[tuple[int, int], list[int]] = {}
    start = len(constraints)
    for first, second in itertools.combinations(range(ROWS), 2):
        pair_mask = (1 << first) | (1 << second)
        fixed = int(FIXED_SUPPORT & pair_mask == pair_mask)
        weighted = [
            (popcount(mask) - 2, variables[(mask, occurrence)])
            for mask in masks
            if mask & pair_mask == pair_mask
            for occurrence in (1, 2)
        ]
        if deficit_links == "all":
            slack = unary_slack("pair_deficit", [first, second], row_deficit_total)
            pair_slack.extend(slack)
            pair_slack_by_pair[(first, second)] = slack
            constraints.append(f"{terms([*weighted, *((1, variable) for variable in slack)])} = {16 - fixed};")
        else:
            constraints.append(f"{terms((-coefficient, variable) for coefficient, variable in weighted)} >= {-16 + fixed};")
    groups["pair_triple_aggregate_cuts"] = len(constraints) - start
    if pair_slack:
        start = len(constraints)
        constraints.append(
            f"{terms((1, variable) for variable in pair_slack)} = {row_deficit_total};"
        )
        groups["global_pair_deficit"] = len(constraints) - start

    if deficit_incidence_links:
        start = len(constraints)
        for row in range(ROWS):
            induced = [
                variable
                for triple, slack in triple_slack_by_triple.items()
                if row in triple
                for variable in slack
            ]
            constraints.append(
                f"{terms([*((1, variable) for variable in induced), *((-1, variable) for variable in row_slack_by_row[row])])} = 0;"
            )
        for pair, pair_deficit in pair_slack_by_pair.items():
            induced = [
                variable
                for triple, slack in triple_slack_by_triple.items()
                if pair[0] in triple and pair[1] in triple
                for variable in slack
            ]
            constraints.append(
                f"{terms([*((1, variable) for variable in induced), *((-1, variable) for variable in pair_deficit)])} = 0;"
            )
        groups["deficit_incidence_links"] = len(constraints) - start

    if row_symmetry != "none":
        start = len(constraints)
        for first, second in (
            (0, 1),
            (1, 2),
            *zip(range(3, 9), range(4, 10)),
        ):
            difference: list[tuple[int, int]] = []
            for mask in masks:
                coefficient = int(bool(mask & (1 << first))) - int(bool(mask & (1 << second)))
                for occurrence in (1, 2):
                    difference.append((coefficient, variables[(mask, occurrence)]))
            constraints.append(f"{terms(difference)} >= 0;")
        groups["row_degree_stabilizer_order"] = len(constraints) - start

    equality_count = sum(" = " in constraint for constraint in constraints)
    maximum_weight = 1
    for constraint in constraints:
        left = constraint.split(" >= ", 1)[0].split(" = ", 1)[0]
        weight = sum(
            abs(int(token))
            for token in left.split()
            if token.lstrip("+-").isdigit()
        )
        maximum_weight = max(maximum_weight, weight)
    integer_size = maximum_weight.bit_length()
    lines = [
        (
            f"* #variable= {next_variable - 1} #constraint= {len(constraints)} "
            f"#equal= {equality_count} intsize= {integer_size}"
        ),
        f"* Exact support-count model for Z(10,23) profile {profile_name}",
        "* Unique degree-three support fixed to rows 0,1,2 by row symmetry",
        *constraints,
    ]
    metadata: dict[str, object] = {
        "schema_version": 1,
        "profile_name": profile_name,
        "profile": {str(degree): count for degree, count in sorted(profile.items())},
        "rows": ROWS,
        "columns": COLUMNS,
        "target_ones": 113,
        "fixed_degree_three_support": [0, 1, 2],
        "semantic_variables": len(variables),
        "variables": next_variable - 1,
        "constraints": len(constraints),
        "equalities": equality_count,
        "integer_size": integer_size,
        "constraint_groups": groups,
        "multiplicity_domain": [0, 1, 2],
        "deficit_links": deficit_links,
        "deficit_incidence_links": deficit_incidence_links,
        "triple_deficit": triple_deficit,
        "triple_deficit_leaf": triple_deficits is not None,
        "complete_degree_supports": (
            {
                "degree": fixed_degree,
                "masks": list(complete_degree_supports),
                "supports": [
                    [row for row in range(ROWS) if mask & (1 << row)]
                    for mask in complete_degree_supports
                ],
            }
            if complete_degree_supports is not None
            else None
        ),
        "row_and_pair_deficit_total": row_deficit_total,
        "minimum_row_degree": 10,
        "row_symmetry": {
            "mode": row_symmetry,
            "group": "S_3 x S_7 stabilizer of the fixed degree-three support",
            "degree_order": "nonincreasing within the two stabilizer blocks",
            "lex_generators": symmetry_generators,
        },
    }
    return "\n".join(lines) + "\n", mapping, metadata


def write(
    profile_name: str,
    output: Path,
    deficit_links: str = "none",
    row_symmetry: str = "degree-order",
    deficit_incidence_links: bool = False,
) -> dict[str, object]:
    text, mapping, metadata = build(
        profile_name,
        deficit_links=deficit_links,
        row_symmetry=row_symmetry,
        deficit_incidence_links=deficit_incidence_links,
    )
    output.mkdir(parents=True, exist_ok=True)
    stem = f"column-count-{profile_name.lower()}"
    formula = output / f"{stem}.opb"
    variable_map = output / f"{stem}.variables.jsonl"
    report = output / f"{stem}.opb.json"
    formula.write_text(text, encoding="ascii")
    with variable_map.open("w", encoding="ascii") as handle:
        for record in mapping:
            handle.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")
    metadata["artifacts"] = {
        "formula": {"file": formula.name, "bytes": formula.stat().st_size, "sha256": sha256(formula)},
        "variable_map": {
            "file": variable_map.name,
            "bytes": variable_map.stat().st_size,
            "sha256": sha256(variable_map),
            "records": len(mapping),
        },
    }
    report.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="ascii")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument("--profile", choices=("B", "C", "all"), default="all")
    parser.add_argument(
        "--deficit-links",
        choices=("none", "triple", "all"),
        default="none",
    )
    parser.add_argument(
        "--row-symmetry",
        choices=("none", "degree-order", "adjacent-lex", "all-transpositions"),
        default="degree-order",
    )
    parser.add_argument("--deficit-incidence-links", action="store_true")
    args = parser.parse_args()
    names = ("B", "C") if args.profile == "all" else (args.profile,)
    print(
        json.dumps(
            {
                name: write(
                    name,
                    args.output,
                    deficit_links=args.deficit_links,
                    row_symmetry=args.row_symmetry,
                    deficit_incidence_links=args.deficit_incidence_links,
                )
                for name in names
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
