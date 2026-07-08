"""Pure-Python completeness checks for canonical row-stabilizer cube covers.

The SAT formulas order rows lexicographically and order equal-degree columns
lexicographically.  Once a column prefix is fixed, rows with the same prefix
form stabilizer cells; the next support must be an initial segment in each
cell.  This module recomputes that finite branching rule without importing a
SAT package.  A proof leaf may also fix selected cells of the immediate next
column; it then covers every canonical support matching those literals.  A
catalog is complete exactly when these possibly partial leaves induce a
prefix trie containing every permitted child at every non-leaf node.
"""

from __future__ import annotations

import collections
import heapq
import itertools
from pathlib import Path
import tempfile
from typing import Any, Iterable, Iterator, Mapping


ROWS = 10
COLUMNS = 23
TARGET = 113
_SORT_CHUNK_RECORDS = 250_000


class CubeCoverError(ValueError):
    """Raised when a row-stabilizer cube catalog is not a complete partition."""


def _encode_path(path: Iterable[int]) -> bytes:
    """Encode a mask path so byte ordering agrees with tuple ordering."""

    return b"".join(mask.to_bytes(2, "big") for mask in path)


class _ExternalPathSorter:
    """Sort many short paths with bounded memory and standard-library storage."""

    def __init__(self, chunk_records: int = _SORT_CHUNK_RECORDS) -> None:
        self._chunk_records = chunk_records
        self._buffer: list[bytes] = []
        self._chunks: list[Path] = []
        self._temporary = tempfile.TemporaryDirectory(prefix="cube_cover_sort_")

    def add(self, path: Iterable[int]) -> None:
        self._buffer.append(_encode_path(path))
        if len(self._buffer) >= self._chunk_records:
            self._flush()

    def _flush(self) -> None:
        if not self._buffer:
            return
        path = Path(self._temporary.name) / f"chunk-{len(self._chunks):06d}.bin"
        with path.open("wb") as handle:
            for encoded in sorted(self._buffer):
                if len(encoded) > 255:
                    raise CubeCoverError("cube path exceeds the sorter encoding")
                handle.write(bytes((len(encoded),)))
                handle.write(encoded)
        self._chunks.append(path)
        self._buffer.clear()

    @staticmethod
    def _read(path: Path) -> Iterator[bytes]:
        with path.open("rb") as handle:
            while length := handle.read(1):
                size = length[0]
                encoded = handle.read(size)
                if len(encoded) != size:
                    raise CubeCoverError("truncated cube-cover sort chunk")
                yield encoded

    def sorted_paths(self) -> Iterator[bytes]:
        if not self._chunks:
            return iter(sorted(self._buffer))
        self._flush()
        return heapq.merge(*(self._read(path) for path in self._chunks))

    def close(self) -> None:
        self._temporary.cleanup()


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
    depth_counts: collections.Counter[int] = collections.Counter()
    partial_literal_counts: collections.Counter[int] = collections.Counter()
    virtual_depth_counts: collections.Counter[int] = collections.Counter()
    record_count = 0
    sorter = _ExternalPathSorter()
    try:
        for index, record in enumerate(records):
            if not isinstance(record, Mapping):
                raise CubeCoverError(f"cube record {index} is not an object")
            masks = record.get("masks")
            reason = record.get("reason")
            if reason not in {"proof_required", "solver_unsat", "no_canonical_child"}:
                raise CubeCoverError(f"cube record {index} has an invalid reason")
            if (
                not isinstance(masks, list)
                or not 1 <= len(masks) <= COLUMNS
                or any(
                    not isinstance(mask, int) or not 0 <= mask < (1 << ROWS)
                    for mask in masks
                )
            ):
                raise CubeCoverError(f"cube record {index} has invalid masks")
            if masks[0] != expected_root:
                raise CubeCoverError(f"cube record {index} has a noncanonical root")
            for column, mask in enumerate(masks):
                if bin(mask).count("1") != degrees[column]:
                    raise CubeCoverError(
                        f"cube record {index} has the wrong degree at column {column}"
                    )
            literals = record.get("literals", [])
            if not isinstance(literals, list) or any(
                not isinstance(literal, int)
                or isinstance(literal, bool)
                or literal == 0
                for literal in literals
            ):
                raise CubeCoverError(f"cube record {index} has invalid partial literals")
            literal_rows: dict[int, bool] = {}
            for literal in literals:
                variable = abs(literal) - 1
                row, column = divmod(variable, COLUMNS)
                if row >= ROWS or column != len(masks):
                    raise CubeCoverError(
                        f"cube record {index} has a literal outside its immediate next column"
                    )
                if row in literal_rows:
                    raise CubeCoverError(f"cube record {index} repeats a partial cell")
                literal_rows[row] = literal > 0

            if literal_rows:
                if len(masks) >= len(degrees):
                    raise CubeCoverError(f"cube record {index} extends a full assignment")
                matching_children = [
                    child
                    for child in child_masks(masks, degrees)
                    if all(
                        bool(child & (1 << row)) == value
                        for row, value in literal_rows.items()
                    )
                ]
                if not matching_children:
                    raise CubeCoverError(
                        f"cube record {index} has no matching canonical next-column support"
                    )
                for child in matching_children:
                    sorter.add(masks + [child])
                    virtual_depth_counts[len(masks) + 1] += 1
                partial_literal_counts[len(literals)] += 1
            else:
                sorter.add(masks)
                virtual_depth_counts[len(masks)] += 1
            depth_counts[len(masks)] += 1
            record_count += 1
        if record_count == 0:
            raise CubeCoverError("cube catalog does not have the unique canonical root")

        paths = sorter.sorted_paths()
        current = next(paths, None)
        visited_leaves = 0

        def visit(prefix: list[int]) -> None:
            nonlocal current, visited_leaves
            encoded = _encode_path(prefix)
            if current == encoded:
                visited_leaves += 1
                current = next(paths, None)
                return
            if current is None or not current.startswith(encoded):
                raise CubeCoverError(
                    f"incomplete cube split at depth {len(prefix)}"
                )
            if len(prefix) >= len(degrees):
                raise CubeCoverError("full column assignment is not a proved leaf")
            expected = sorted(child_masks(prefix, degrees))
            if not expected:
                raise CubeCoverError(
                    f"incomplete cube split at depth {len(prefix)}: expected no children"
                )
            for mask in expected:
                visit(prefix + [mask])

        visit([expected_root])
        if current is not None:
            raise CubeCoverError("cube catalog contains overlapping or duplicate leaves")
        virtual_leaf_count = sum(virtual_depth_counts.values())
        if visited_leaves != virtual_leaf_count:
            raise CubeCoverError("cube traversal did not visit every virtual leaf")
        return {
            "status": "COMPLETE",
            "profile": profile,
            "leaf_count": record_count,
            "minimum_depth": min(depth_counts),
            "maximum_depth": max(depth_counts),
            "depth_counts": {
                str(depth): depth_counts[depth] for depth in sorted(depth_counts)
            },
            "partial_leaf_count": sum(partial_literal_counts.values()),
            "partial_literal_counts": {
                str(count): partial_literal_counts[count]
                for count in sorted(partial_literal_counts)
            },
            "canonical_leaf_count": virtual_leaf_count,
            "canonical_depth_counts": {
                str(depth): virtual_depth_counts[depth]
                for depth in sorted(virtual_depth_counts)
            },
        }
    finally:
        sorter.close()
