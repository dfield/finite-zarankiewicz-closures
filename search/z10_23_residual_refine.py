#!/usr/bin/env python3
"""Refine exactly the timed-out leaves of a complete Z(10,23) cube cover.

The input catalog remains untrusted: this program first checks that it is a
complete canonical row-stabilizer cover.  It then validates every residual
record against the catalog leaf at the recorded global index and bisects only
those leaves inside their immediate next canonical column.  Finally it checks
the complete output catalog again and emits deterministic task, reuse, and
parent-to-child maps.

No SAT verdict is used to establish coverage.  Residual JSONL files select
leaves to refine; the standard-library cube-cover checker establishes that
the resulting catalog is still prefix-free and exhaustive.
"""

from __future__ import annotations

import argparse
import collections
from contextlib import ExitStack
import hashlib
import heapq
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Iterable, Iterator, TextIO


def _load_cover_module() -> Any:
    root = Path(__file__).resolve().parents[1]
    candidates = (
        Path(__file__).resolve().with_name("z1023-cube-cover.py"),
        root / "src" / "finite_zarankiewicz_closures" / "cube_cover.py",
    )
    for path in candidates:
        if not path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("z1023_cube_cover", path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise RuntimeError("cannot locate the cube-cover checker")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _json_lines(handle: TextIO) -> Iterator[dict[str, Any]]:
    for line_number, line in enumerate(handle, 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"malformed JSONL record {line_number}") from error
        if not isinstance(record, dict):
            raise RuntimeError(f"JSONL record {line_number} is not an object")
        yield record


def _residual_records(
    paths: list[Path], stack: ExitStack
) -> Iterator[tuple[int, int, dict[str, Any]]]:
    streams: list[Iterable[tuple[int, int, dict[str, Any]]]] = []
    for source_number, path in enumerate(paths):
        handle = stack.enter_context(path.open(encoding="ascii"))

        def records(
            source: TextIO = handle,
            source_index: int = source_number,
            source_path: Path = path,
        ) -> Iterator[tuple[int, int, dict[str, Any]]]:
            previous = -1
            for record in _json_lines(source):
                index = record.get("index")
                if not isinstance(index, int) or isinstance(index, bool) or index < 0:
                    raise RuntimeError(f"invalid residual index in {source_path}")
                if index <= previous:
                    raise RuntimeError(f"residual indexes are not increasing in {source_path}")
                if record.get("status") != "TIMEOUT":
                    raise RuntimeError(f"non-timeout residual record in {source_path}")
                previous = index
                yield index, source_index, record

        streams.append(records())

    previous = -1
    for index, source_index, record in heapq.merge(*streams):
        if index == previous:
            raise RuntimeError(f"duplicate residual index {index}")
        previous = index
        yield index, source_index, record


def _compatible_children(
    cover: Any,
    masks: list[int],
    literals: list[int],
    degrees: list[int],
) -> list[int]:
    assignments = {
        (abs(literal) - 1) // 23: literal > 0
        for literal in literals
    }
    return [
        child
        for child in cover.child_masks(masks, degrees)
        if all(
            bool(child & (1 << row)) == value
            for row, value in assignments.items()
        )
    ]


def bisect_leaf(
    cover: Any,
    leaf: dict[str, Any],
    degrees: list[int],
    split_bits: int,
) -> list[dict[str, Any]]:
    """Return a deterministic partition of one leaf's matching next column."""

    masks = list(leaf["masks"])
    literals = list(leaf.get("literals", []))
    children = _compatible_children(cover, masks, literals, degrees)
    if not children:
        return [dict(leaf)]
    if len(children) == 1:
        return [{"masks": masks + [children[0]], "reason": "proof_required"}]

    branches = [(literals, children)]
    for _ in range(split_bits):
        refined: list[tuple[list[int], list[int]]] = []
        for branch_literals, branch_children in branches:
            if len(branch_children) == 1:
                refined.append((branch_literals, branch_children))
                continue
            assigned_rows = {
                (abs(literal) - 1) // 23 for literal in branch_literals
            }
            candidates = []
            for row in range(10):
                if row in assigned_rows:
                    continue
                positive = sum(
                    bool(child & (1 << row)) for child in branch_children
                )
                negative = len(branch_children) - positive
                if positive and negative:
                    candidates.append(
                        (abs(positive - negative), -min(positive, negative), row)
                    )
            if not candidates:
                raise RuntimeError(
                    f"cannot bisect leaf {masks=} {branch_literals=}"
                )
            row = min(candidates)[2]
            variable = row * 23 + len(masks) + 1
            for value in (True, False):
                subset = [
                    child
                    for child in branch_children
                    if bool(child & (1 << row)) == value
                ]
                if subset:
                    refined.append(
                        (
                            branch_literals + [variable if value else -variable],
                            subset,
                        )
                    )
        branches = refined

    replacements: list[dict[str, Any]] = []
    for branch_literals, branch_children in branches:
        if len(branch_children) == 1:
            replacements.append(
                {
                    "masks": masks + [branch_children[0]],
                    "reason": "proof_required",
                }
            )
        else:
            replacements.append(
                {
                    "literals": branch_literals,
                    "masks": masks,
                    "reason": "proof_required",
                }
            )
    return replacements


def _write_jsonl(handle: TextIO, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")


def refine(
    profile: str,
    catalog_path: Path,
    residual_paths: list[Path],
    output: Path,
    split_bits: int,
    shards: int,
) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError(f"output already exists: {output}")
    if split_bits <= 0 or shards <= 0:
        raise ValueError("split bits and shard count must be positive")
    for path in (catalog_path, *residual_paths):
        if not path.is_file():
            raise RuntimeError(f"missing input: {path}")

    cover = _load_cover_module()
    with catalog_path.open(encoding="ascii") as handle:
        input_cover = cover.verify_cube_catalog(profile, _json_lines(handle))
    degrees = cover.ordered_degrees(profile)

    output.mkdir(parents=True)
    catalog_temporary = output / "cubes.jsonl.tmp"
    reuse_temporary = output / "reuse-map.jsonl.tmp"
    refinement_temporary = output / "refinement-map.jsonl.tmp"
    task_temporaries = [output / f"task-indices-{index:02d}.txt.tmp" for index in range(shards)]

    task_counts = [0] * shards
    replacement_counts: collections.Counter[int] = collections.Counter()
    output_leaf_count = 0
    reused_leaves = 0
    residual_parents = 0
    unchanged_residuals = 0

    with ExitStack() as stack:
        catalog = stack.enter_context(catalog_path.open(encoding="ascii"))
        destination = stack.enter_context(catalog_temporary.open("x", encoding="ascii"))
        reuse_map = stack.enter_context(reuse_temporary.open("x", encoding="ascii"))
        refinement_map = stack.enter_context(
            refinement_temporary.open("x", encoding="ascii")
        )
        task_handles = [
            stack.enter_context(path.open("x", encoding="ascii"))
            for path in task_temporaries
        ]
        residuals = _residual_records(residual_paths, stack)
        current = next(residuals, None)

        for parent_index, leaf in enumerate(_json_lines(catalog)):
            if current is not None and current[0] < parent_index:
                raise RuntimeError(f"residual index {current[0]} is outside the catalog")
            if current is None or current[0] != parent_index:
                _write_jsonl(destination, leaf)
                _write_jsonl(
                    reuse_map,
                    {"new_index": output_leaf_count, "parent_index": parent_index},
                )
                output_leaf_count += 1
                reused_leaves += 1
            else:
                _, source_index, residual = current
                masks = residual.get("masks")
                literals = residual.get("literals", [])
                if masks != leaf.get("masks") or literals != leaf.get("literals", []):
                    raise RuntimeError(
                        f"residual leaf {parent_index} does not match the catalog"
                    )
                replacements = bisect_leaf(cover, leaf, degrees, split_bits)
                first_new_index = output_leaf_count
                for replacement in replacements:
                    _write_jsonl(destination, replacement)
                    shard = output_leaf_count % shards
                    task_handles[shard].write(f"{output_leaf_count}\n")
                    task_counts[shard] += 1
                    output_leaf_count += 1
                _write_jsonl(
                    refinement_map,
                    {
                        "child_count": len(replacements),
                        "first_new_index": first_new_index,
                        "parent_index": parent_index,
                        "residual_source": source_index,
                    },
                )
                replacement_counts[len(replacements)] += 1
                residual_parents += 1
                if len(replacements) == 1 and replacements[0] == leaf:
                    unchanged_residuals += 1
                current = next(residuals, None)

            if (parent_index + 1) % 100_000 == 0:
                print(
                    json.dumps(
                        {
                            "input_processed": parent_index + 1,
                            "output_leaves": output_leaf_count,
                            "residual_parents": residual_parents,
                        },
                        sort_keys=True,
                    ),
                    flush=True,
                )

        if current is not None:
            raise RuntimeError(f"residual index {current[0]} is outside the catalog")

    if residual_parents == 0:
        raise RuntimeError("no residual leaves were selected")
    if sum(task_counts) != output_leaf_count - reused_leaves:
        raise RuntimeError("task partition does not match the refined leaves")

    with catalog_temporary.open(encoding="ascii") as handle:
        output_cover = cover.verify_cube_catalog(profile, _json_lines(handle))
    if output_cover.get("leaf_count") != output_leaf_count:
        raise RuntimeError("output cover count does not match the generated catalog")

    files = {
        "catalog": catalog_temporary,
        "reuse_map": reuse_temporary,
        "refinement_map": refinement_temporary,
    }
    files.update(
        {f"task_indices_{index:02d}": path for index, path in enumerate(task_temporaries)}
    )
    artifacts = {
        name: {
            "bytes": path.stat().st_size,
            "file": path.name.removesuffix(".tmp"),
            "sha256": _sha256(path),
        }
        for name, path in files.items()
    }

    for path in files.values():
        os.replace(path, path.with_name(path.name.removesuffix(".tmp")))

    report: dict[str, Any] = {
        "schema_version": 1,
        "status": "COMPLETE_REFINED_COVER",
        "profile": profile,
        "strategy": "bisect_timed_out_leaves_in_immediate_next_column",
        "split_bits": split_bits,
        "input": {
            "catalog": {
                "bytes": catalog_path.stat().st_size,
                "count": input_cover["leaf_count"],
                "file": catalog_path.name,
                "sha256": _sha256(catalog_path),
            },
            "cover": input_cover,
            "residuals": [
                {
                    "bytes": path.stat().st_size,
                    "file": path.name,
                    "sha256": _sha256(path),
                }
                for path in residual_paths
            ],
        },
        "output": {
            "artifacts": artifacts,
            "cover": output_cover,
            "leaf_count": output_leaf_count,
            "refined_task_count": sum(task_counts),
            "residual_parent_count": residual_parents,
            "reused_leaf_count": reused_leaves,
            "task_counts": task_counts,
            "replacement_counts": {
                str(count): replacement_counts[count]
                for count in sorted(replacement_counts)
            },
            "unchanged_residual_count": unchanged_residuals,
        },
    }
    report_path = output / "refinement.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(json.dumps(report, sort_keys=True), flush=True)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile")
    parser.add_argument("--catalog", type=Path, required=True)
    parser.add_argument("--residual", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--split-bits", type=int, default=1)
    parser.add_argument("--shards", type=int, default=3)
    args = parser.parse_args()
    refine(
        args.profile,
        args.catalog.resolve(),
        [path.resolve() for path in args.residual],
        args.output.resolve(),
        args.split_bits,
        args.shards,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
