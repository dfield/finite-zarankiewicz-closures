"""Pure-Python completeness checks for canonical row-stabilizer cube covers.

The SAT formulas order rows lexicographically and order equal-degree columns
lexicographically.  Once a column prefix is fixed, rows with the same prefix
form stabilizer cells; the next support must be an initial segment in each
cell.  This module recomputes that finite branching rule without importing a
SAT package.  A leaf catalog is complete exactly when its prefix trie contains
every permitted child at every non-leaf node.
"""

from __future__ import annotations

import collections
import itertools
from typing import Any, Iterable, Mapping


ROWS = 10
COLUMNS = 23
TARGET = 113
_LEAF = "__leaf__"


class CubeCoverError(ValueError):
    """Raised when a row-stabilizer cube catalog is not a complete partition."""


def parse_profile(profile: str) -> dict[int, int]:
    """Parse and validate the canonical ``degree x multiplicity`` notation."""

    counts: dict[int, int] = {}
    try:
        for term in profile.split(","):
            degree_text, count_text = term.split("x", 1)
            degree, count = int(degree_text), int(count_text)
            if not 0 <= degree <= ROWS or count <= 0 or degree in counts:
                raise CubeCoverError(f"invalid profile term: {term}")
            counts[degree] = count
    except (TypeError, ValueError) as error:
        if isinstance(error, CubeCoverError):
            raise
        raise CubeCoverError("malformed cube-cover profile") from error
    if sum(counts.values()) != COLUMNS:
        raise CubeCoverError("cube-cover profile does not contain 23 columns")
    if sum(degree * count for degree, count in counts.items()) != TARGET:
        raise CubeCoverError("cube-cover profile does not contain 113 ones")
    return counts


def ordered_degrees(profile: str) -> list[int]:
    """Use the same rare-block-first column order as the CNF generator."""

    counts = parse_profile(profile)
    groups = sorted(counts.items(), key=lambda item: (item[1], item[0]))
    return [degree for degree, count in groups for _ in range(count)]


def _support(mask: int) -> set[int]:
    return {row for row in range(ROWS) if mask & (1 << row)}


def child_masks(prefix_masks: list[int], degrees: list[int]) -> list[int]:
    """Enumerate all canonical next-column supports for one fixed prefix."""

    column = len(prefix_masks)
    if not 0 < column < len(degrees):
        return []
    prefix = [_support(mask) for mask in prefix_masks]
    degree = degrees[column]
    patterns = sorted(
        {tuple(row in support for support in prefix) for row in range(ROWS)},
        reverse=True,
    )
    cells = [
        [
            row
            for row in range(ROWS)
            if tuple(row in support for support in prefix) == pattern
        ]
        for pattern in patterns
    ]
    children: list[int] = []
    for counts in itertools.product(*(range(len(cell) + 1) for cell in cells)):
        if sum(counts) != degree:
            continue
        support = {
            row
            for cell, count in zip(cells, counts)
            for row in cell[:count]
        }
        if degrees[column - 1] == degree:
            previous_vector = tuple(row in prefix[-1] for row in range(ROWS))
            vector = tuple(row in support for row in range(ROWS))
            if previous_vector < vector:
                continue
        if any(
            len(prefix[left] & prefix[right] & support) > 2
            for left, right in itertools.combinations(range(len(prefix)), 2)
        ):
            continue
        children.append(sum(1 << row for row in support))
    return children


def verify_cube_catalog(
    profile: str,
    records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """Verify that proof leaves form a complete, prefix-free canonical cover."""

    degrees = ordered_degrees(profile)
    expected_root = (1 << degrees[0]) - 1
    trie: dict[Any, Any] = {}
    depth_counts: collections.Counter[int] = collections.Counter()
    record_count = 0
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            raise CubeCoverError(f"cube record {index} is not an object")
        masks = record.get("masks")
        reason = record.get("reason")
        if reason not in {"solver_unsat", "no_canonical_child"}:
            raise CubeCoverError(f"cube record {index} has an invalid reason")
        if (
            not isinstance(masks, list)
            or not 1 <= len(masks) <= COLUMNS
            or any(not isinstance(mask, int) or not 0 <= mask < (1 << ROWS) for mask in masks)
        ):
            raise CubeCoverError(f"cube record {index} has invalid masks")
        if masks[0] != expected_root:
            raise CubeCoverError(f"cube record {index} has a noncanonical root")
        for column, mask in enumerate(masks):
            if bin(mask).count("1") != degrees[column]:
                raise CubeCoverError(
                    f"cube record {index} has the wrong degree at column {column}"
                )
        node = trie
        for mask in masks:
            if _LEAF in node:
                raise CubeCoverError("cube catalog contains a leaf and its descendant")
            node = node.setdefault(mask, {})
        if node:
            raise CubeCoverError("cube catalog contains a duplicate or prefix leaf")
        node[_LEAF] = True
        depth_counts[len(masks)] += 1
        record_count += 1
    if record_count == 0 or set(trie) != {expected_root}:
        raise CubeCoverError("cube catalog does not have the unique canonical root")

    visited_leaves = 0

    def visit(prefix: list[int], node: Mapping[Any, Any]) -> None:
        nonlocal visited_leaves
        if _LEAF in node:
            if len(node) != 1:
                raise CubeCoverError("cube leaf has descendants")
            visited_leaves += 1
            return
        if len(prefix) >= len(degrees):
            raise CubeCoverError("full column assignment is not a proved leaf")
        expected = child_masks(prefix, degrees)
        observed = [key for key in node if isinstance(key, int)]
        if set(observed) != set(expected) or len(observed) != len(expected):
            raise CubeCoverError(
                f"incomplete cube split at depth {len(prefix)}: "
                f"expected {len(expected)}, found {len(observed)}"
            )
        for mask in expected:
            visit(prefix + [mask], node[mask])

    visit([expected_root], trie[expected_root])
    if visited_leaves != record_count:
        raise CubeCoverError("cube trie traversal did not visit every leaf")
    return {
        "status": "COMPLETE",
        "profile": profile,
        "leaf_count": record_count,
        "minimum_depth": min(depth_counts),
        "maximum_depth": max(depth_counts),
        "depth_counts": {
            str(depth): depth_counts[depth] for depth in sorted(depth_counts)
        },
    }
