#!/usr/bin/env python3
"""Enumerate the complete degree-six-support orbit cover for profile C."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Iterable


ROWS = 10
FIXED_ROWS = (0, 1, 2)
FREE_ROWS = tuple(range(3, 10))
FIXED_MASK = sum(1 << row for row in FIXED_ROWS)
ROW_GROUP_ORDER = math.factorial(len(FIXED_ROWS)) * math.factorial(len(FREE_ROWS))
EXPECTED_RAW_STATES = 950_250
EXPECTED_ORBITS = 236
ORIGINAL_GENERATED_AT = "2026-07-15T00:56:15.680302+00:00"
SUPPORT_PERMUTATIONS = tuple(itertools.permutations(range(3)))


def canonical_json(value: dict[str, object]) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def popcount(mask: int) -> int:
    return bin(mask).count("1")


def support(mask: int) -> list[int]:
    return [row for row in range(ROWS) if mask & (1 << row)]


def pattern_counts(masks: tuple[int, int, int], rows: Iterable[int]) -> tuple[int, ...]:
    counts = [0] * 8
    for row in rows:
        pattern = sum(((mask >> row) & 1) << index for index, mask in enumerate(masks))
        counts[pattern] += 1
    return tuple(counts)


def canonical_signature(masks: tuple[int, int, int]) -> tuple[int, ...]:
    """Return a complete invariant for S_3 x S_7 acting on an unordered triple.

    For a labeled triple of supports, rows in either stabilizer block are
    classified by their three-bit membership pattern.  Pattern multiplicities
    are complete invariants under row permutations.  Minimizing over the six
    support labelings makes the invariant complete for an unordered multiset.
    """

    signatures = []
    for permutation in SUPPORT_PERMUTATIONS:
        ordered = tuple(masks[index] for index in permutation)
        signatures.append(
            (*pattern_counts(ordered, FIXED_ROWS), *pattern_counts(ordered, FREE_ROWS))
        )
    return min(signatures)


def admissible(masks: tuple[int, int, int]) -> bool:
    if masks[0] == masks[2]:
        return False
    if popcount(masks[0] & masks[1] & masks[2]) >= 3:
        return False
    return sum(mask & FIXED_MASK == FIXED_MASK for mask in masks) <= 1


def build(output: Path, generated_at: str = ORIGINAL_GENERATED_AT) -> dict[str, object]:
    degree_six_masks = tuple(
        sum(1 << row for row in rows)
        for rows in itertools.combinations(range(ROWS), 6)
    )
    orbit_data: dict[tuple[int, ...], dict[str, object]] = {}
    raw_states = 0
    for indices in itertools.combinations_with_replacement(
        range(len(degree_six_masks)), 3
    ):
        masks = tuple(degree_six_masks[index] for index in indices)
        if not admissible(masks):
            continue
        raw_states += 1
        signature = canonical_signature(masks)
        item = orbit_data.get(signature)
        if item is None:
            orbit_data[signature] = {"representative": masks, "orbit_size": 1}
        else:
            item["orbit_size"] = int(item["orbit_size"]) + 1

    if raw_states != EXPECTED_RAW_STATES or len(orbit_data) != EXPECTED_ORBITS:
        raise RuntimeError("profile-C degree-six orbit census changed unexpectedly")
    if sum(int(item["orbit_size"]) for item in orbit_data.values()) != raw_states:
        raise RuntimeError("profile-C orbit sizes do not cover every raw state")
    if any(ROW_GROUP_ORDER % int(item["orbit_size"]) for item in orbit_data.values()):
        raise RuntimeError("a profile-C orbit size does not divide the row-group order")

    output.mkdir(parents=True, exist_ok=False)
    catalog = output / "profile-c-degree6-orbits.jsonl"
    with catalog.open("w", encoding="ascii") as handle:
        for index, signature in enumerate(sorted(orbit_data)):
            item = orbit_data[signature]
            masks = tuple(int(mask) for mask in item["representative"])
            record = {
                "schema_version": 1,
                "index": index,
                "profile": "3x1,4x3,5x16,6x3",
                "degree": 6,
                "degree_six_support_masks": list(masks),
                "degree_six_supports": [support(mask) for mask in masks],
                "orbit_size": int(item["orbit_size"]),
                "canonical_signature": {
                    "fixed_block_pattern_counts": list(signature[:8]),
                    "free_block_pattern_counts": list(signature[8:]),
                },
            }
            handle.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")

    metadata: dict[str, object] = {
        "schema_version": 1,
        "status": "COMPLETE_ORBIT_COVER",
        # Preserve the original production timestamp so the checked metadata
        # file, not only its catalog, regenerates byte-for-byte.
        "generated_at": generated_at,
        "profile": "3x1,4x3,5x16,6x3",
        "fixed_degree_three_support": list(FIXED_ROWS),
        "classified_object": "unordered multiset of the three degree-six supports",
        "raw_state_count": raw_states,
        "orbit_count": len(orbit_data),
        "orbit_size_sum": sum(int(item["orbit_size"]) for item in orbit_data.values()),
        "symmetry": {
            "row_group": "S_3 x S_7",
            "row_group_order": ROW_GROUP_ORDER,
            "support_multiset": "unordered",
            "complete_invariant": (
                "three-bit row-membership pattern counts in the fixed and free "
                "row blocks, minimized over all six support labelings"
            ),
        },
        "admissibility_filters": [
            "support multiplicity at most two",
            "the three degree-six supports have no common row triple",
            "at most one degree-six support contains the fixed triple",
        ],
        "catalog": {
            "file": catalog.name,
            "bytes": catalog.stat().st_size,
            "sha256": sha256(catalog),
        },
    }
    report = output / "profile-c-degree6-orbits.json"
    report.write_text(canonical_json(metadata), encoding="ascii")
    print(canonical_json({**metadata, "report": report.name}), end="")
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--generated-at",
        default=ORIGINAL_GENERATED_AT,
        help="provenance timestamp (defaults to the original certified run)",
    )
    args = parser.parse_args()
    build(args.output, args.generated_at)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
