#!/usr/bin/env python3
"""Generate and certify the SAT layer for ``Z(10,23,3,3) <= 112``.

The standard-library arithmetic checker reduces the 25 capacity-feasible
degree profiles at 113 ones to thirteen SAT cases.  This optional tool builds
one deterministic CNF per surviving profile, can decompose it into a complete
canonical row-stabilizer cube catalog, and can ask CaDiCaL plus DRAT/LRAT
checkers for a replayable *direct* proof of the unsplit formula.  A catalog is
not itself a proof; ``z10_23_cube_certify.py`` independently proves and checks
every leaf.  Formula and catalog generation require ``python-sat``; the
checked-in formulas and traces do not.

Typical use for one profile::

    python3 search/z10_23_certify.py frontier '3x1,4x2,5x18,6x2' \
      --depth 4 --output build/z10_23
    python3 search/z10_23_certify.py cubes '4x2,5x21' --output build/z10_23
    python3 search/z10_23_certify.py direct '4x2,5x21' --output build/z10_23
    python3 search/z10_23_cube_certify.py '4x2,5x21' \
      --catalog build/z10_23/4d2_5d21.cubes.jsonl --output build/z10_23

The cube run is deterministic.  Equal-degree columns stay contiguous, rare
degree blocks come first, rows and equal-degree columns obey double-lex order,
and every row has degree at least ten by ``Z(9,23,3,3)=103``.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import itertools
import json
import lzma
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, Optional

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from search.sat_tool import build  # noqa: E402


ROWS = 10
COLUMNS = 23
TARGET = 113
PROOF_PART_BYTES = 95_000_000
SAT_PROFILES = (
    "4x2,5x21",
    "4x3,5x19,6x1",
    "4x4,5x17,6x2",
    "4x4,5x18,7x1",
    "4x5,5x15,6x3",
    "4x5,5x16,6x1,7x1",
    "4x6,5x13,6x4",
    "4x7,5x11,6x5",
    "3x1,5x22",
    "3x1,4x1,5x20,6x1",
    "3x1,4x2,5x18,6x2",
    "3x1,4x3,5x16,6x3",
    "3x1,4x4,5x14,6x4",
)


def parse_profile(text: str) -> dict[int, int]:
    """Parse ``degree x multiplicity`` terms and validate the target."""

    counts: dict[int, int] = {}
    for term in text.split(","):
        degree_text, count_text = term.split("x", 1)
        degree, count = int(degree_text), int(count_text)
        if not 0 <= degree <= ROWS or count <= 0 or degree in counts:
            raise ValueError(f"invalid profile term: {term}")
        counts[degree] = count
    if sum(counts.values()) != COLUMNS:
        raise ValueError("profile does not contain 23 columns")
    if sum(degree * count for degree, count in counts.items()) != TARGET:
        raise ValueError("profile does not contain 113 ones")
    return counts


def canonical_profile(text: str) -> str:
    counts = parse_profile(text)
    return ",".join(f"{degree}x{counts[degree]}" for degree in sorted(counts))


def profile_slug(text: str) -> str:
    return canonical_profile(text).replace(",", "_").replace("x", "d")


def ordered_degrees(text: str) -> list[int]:
    """Put rare blocks first while keeping equal degrees contiguous."""

    counts = parse_profile(text)
    groups = sorted(counts.items(), key=lambda item: (item[1], item[0]))
    return [degree for degree, count in groups for _ in range(count)]


def build_profile_formula(text: str) -> tuple[CNF, list[list[int]], list[int]]:
    """Build the deterministic profile CNF plus the neighboring-row cut."""

    degrees = ordered_degrees(text)
    cnf, cells = build(ROWS, COLUMNS, degrees)
    for row in cells:
        lower = CardEnc.atleast(
            lits=row,
            bound=10,
            top_id=cnf.nv,
            encoding=EncType.seqcounter,
        )
        cnf.extend(lower.clauses)
    return cnf, cells, degrees


def _cell_variable(row: int, column: int) -> int:
    # ``sat_tool.build`` allocates the complete row-major cell block first.
    return row * COLUMNS + column + 1


def _assumptions(prefix: Iterable[set[int]]) -> list[int]:
    return [
        _cell_variable(row, column)
        if row in support
        else -_cell_variable(row, column)
        for column, support in enumerate(prefix)
        for row in range(ROWS)
    ]


def _support_masks(prefix: Iterable[set[int]]) -> list[int]:
    return [sum(1 << row for row in support) for support in prefix]


def child_supports(prefix: list[set[int]], degrees: list[int]) -> list[set[int]]:
    """Return all canonical supports for the next column.

    Rows with the same fixed prefix form one stabilizer cell.  Global row-lex
    order forces the next support to be an initial segment of every such cell.
    Equal-degree column lex order supplies the second comparison below.
    """

    column = len(prefix)
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
    children = []
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
        children.append(support)
    return children


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def generate_frontier(
    profile: str,
    output: Path,
    depth: int = 4,
) -> dict[str, object]:
    """Generate a complete fixed-depth canonical prefix cover.

    The catalog deliberately makes no SAT claim.  Every nonterminal prefix is
    marked ``proof_required`` and becomes a theorem certificate only after
    ``z10_23_cube_certify.py`` independently refutes it.  Prefixes with no
    canonical child are retained as earlier terminal leaves and are refuted by
    the same proof-producing path.
    """

    canonical = canonical_profile(profile)
    if canonical not in SAT_PROFILES:
        raise ValueError(f"profile is not in the thirteen-case SAT scope: {canonical}")
    if not 1 <= depth <= COLUMNS:
        raise ValueError("frontier depth must lie between one and 23")
    output.mkdir(parents=True, exist_ok=True)
    slug = profile_slug(canonical)
    formula_path = output / f"{slug}.cnf"
    cubes_path = output / f"{slug}.cubes.jsonl"
    metadata_path = output / f"{slug}.json"

    cnf, _, degrees = build_profile_formula(canonical)
    cnf.to_file(str(formula_path))
    frontier: list[tuple[list[set[int]], Optional[str]]] = [
        ([{row for row in range(degrees[0])}], None)
    ]
    while any(reason is None and len(prefix) < depth for prefix, reason in frontier):
        expanded: list[tuple[list[set[int]], Optional[str]]] = []
        for prefix, reason in frontier:
            if reason is not None or len(prefix) >= depth:
                expanded.append((prefix, reason))
                continue
            children = child_supports(prefix, degrees)
            if children:
                expanded.extend((prefix + [support], None) for support in children)
            else:
                expanded.append((prefix, "no_canonical_child"))
        frontier = expanded

    depth_counts: collections.Counter[int] = collections.Counter()
    with cubes_path.open("w", encoding="ascii") as cube_file:
        for prefix, reason in frontier:
            depth_counts[len(prefix)] += 1
            cube_file.write(
                json.dumps(
                    {
                        "masks": _support_masks(prefix),
                        "reason": reason or "proof_required",
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                )
                + "\n"
            )

    metadata = {
        "schema_version": 1,
        "profile": canonical,
        "column_order": degrees,
        "formula": {
            "file": formula_path.name,
            "sha256": _sha256(formula_path),
            "variables": cnf.nv,
            "clauses": len(cnf.clauses),
        },
        "strategy": "fixed_row_stabilizer_frontier",
        "cubes": {
            "file": cubes_path.name,
            "sha256": _sha256(cubes_path),
            "count": len(frontier),
            "requested_depth": depth,
            "depth_counts": {
                str(level): depth_counts[level] for level in sorted(depth_counts)
            },
        },
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def generate_cubes(
    profile: str,
    output: Path,
    conflict_budget: int,
    maximum_depth: int,
    depth_factor: int = 1,
    escalate_after: int = 99,
    maximum_conflicts: int = 0,
) -> dict[str, object]:
    """Generate an adaptive search-cube catalog (not a proof artifact)."""

    canonical = canonical_profile(profile)
    if canonical not in SAT_PROFILES:
        raise ValueError(f"profile is not in the thirteen-case SAT scope: {canonical}")
    if (
        conflict_budget <= 0
        or maximum_depth <= 0
        or depth_factor <= 0
        or escalate_after < 0
        or maximum_conflicts < 0
    ):
        raise ValueError("cube budgets, depth, and factor must be positive")
    output.mkdir(parents=True, exist_ok=True)
    slug = profile_slug(canonical)
    formula_path = output / f"{slug}.cnf"
    cubes_path = output / f"{slug}.cubes.jsonl"
    metadata_path = output / f"{slug}.json"

    cnf, _, degrees = build_profile_formula(canonical)
    cnf.to_file(str(formula_path))
    first = {row for row in range(degrees[0])}
    statistics: collections.Counter[str] = collections.Counter()
    leaf_count = 0
    calls = 0
    started = time.monotonic()

    with cubes_path.open("w", encoding="ascii") as cube_file:
        with Solver(name="cadical195", bootstrap_with=cnf.clauses) as solver:

            def record(prefix: list[set[int]], reason: str) -> None:
                nonlocal leaf_count
                cube_file.write(
                    json.dumps(
                        {"masks": _support_masks(prefix), "reason": reason},
                        separators=(",", ":"),
                        sort_keys=True,
                    )
                    + "\n"
                )
                cube_file.flush()
                leaf_count += 1

            def visit(prefix: list[set[int]]) -> None:
                nonlocal calls
                calls += 1
                depth = len(prefix)
                budget = conflict_budget * (
                    depth_factor ** max(0, depth - escalate_after)
                )
                if maximum_conflicts:
                    budget = min(budget, maximum_conflicts)
                solver.conf_budget(budget)
                answer = solver.solve_limited(assumptions=_assumptions(prefix))
                if answer is False:
                    statistics[f"unsat_depth_{depth}"] += 1
                    record(prefix, "solver_unsat")
                    return
                if answer is True:
                    raise RuntimeError(
                        f"SAT witness found for {canonical}; the proposed theorem is false"
                    )
                statistics[f"split_depth_{depth}"] += 1
                if depth >= maximum_depth:
                    raise RuntimeError(
                        f"unresolved cube at depth {depth}; increase --maximum-depth"
                    )
                children = child_supports(prefix, degrees)
                statistics[f"children_depth_{depth}"] += len(children)
                if not children:
                    record(prefix, "no_canonical_child")
                    return
                for support in children:
                    visit(prefix + [support])

            visit([first])

    metadata = {
        "schema_version": 1,
        "profile": canonical,
        "column_order": degrees,
        "formula": {
            "file": formula_path.name,
            "sha256": _sha256(formula_path),
            "variables": cnf.nv,
            "clauses": len(cnf.clauses),
        },
        "cubes": {
            "file": cubes_path.name,
            "sha256": _sha256(cubes_path),
            "count": leaf_count,
            "conflict_budget": conflict_budget,
            "maximum_depth": maximum_depth,
            "depth_factor": depth_factor,
            "escalate_after": escalate_after,
            "maximum_conflicts": maximum_conflicts,
            "solver": "CaDiCaL 1.9.5 via python-sat 1.9.dev2",
            "calls": calls,
            "statistics": dict(sorted(statistics.items())),
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def _run(
    command: list[str],
    cwd: Path,
    log: Path,
    accepted_returncodes: tuple[int, ...] = (0,),
) -> None:
    with log.open("w", encoding="utf-8") as handle:
        completed = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            stdout=handle,
            stderr=subprocess.STDOUT,
            text=True,
        )
    if completed.returncode not in accepted_returncodes:
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}")


def _compress_drat(source: Path) -> tuple[dict[str, object], str]:
    """Store one DRAT archive, splitting only its byte stream when necessary."""

    uncompressed_sha256 = _sha256(source)
    destination = source.with_suffix(source.suffix + ".xz")
    compression = "xz preset 6"

    def compress(preset: int) -> None:
        with source.open("rb") as input_file, lzma.open(
            destination, "wb", format=lzma.FORMAT_XZ, preset=preset
        ) as output_file:
            shutil.copyfileobj(input_file, output_file, length=1024 * 1024)

    compress(6)
    if destination.stat().st_size >= 95_000_000:
        destination.unlink()
        compress(9 | lzma.PRESET_EXTREME)
        compression = "xz preset 9 extreme"
    compressed_sha256 = _sha256(destination)
    compressed_bytes = destination.stat().st_size
    for stale_part in destination.parent.glob(f"{destination.name}.part-*"):
        stale_part.unlink()
    if compressed_bytes < 100_000_000:
        artifact: dict[str, object] = {
            "file": destination.name,
            "sha256": compressed_sha256,
            "bytes": compressed_bytes,
            "format": "DRAT+xz",
        }
    else:
        parts = []
        with destination.open("rb") as archive:
            index = 0
            while archive.tell() < compressed_bytes:
                part = destination.with_name(f"{destination.name}.part-{index:02d}")
                remaining = PROOF_PART_BYTES
                with part.open("wb") as output_file:
                    while remaining:
                        block = archive.read(min(1024 * 1024, remaining))
                        if not block:
                            break
                        output_file.write(block)
                        remaining -= len(block)
                parts.append(
                    {
                        "file": part.name,
                        "sha256": _sha256(part),
                        "bytes": part.stat().st_size,
                    }
                )
                index += 1
        destination.unlink()
        artifact = {
            "parts": parts,
            "sha256": compressed_sha256,
            "bytes": compressed_bytes,
            "format": "DRAT+xz+split",
        }
    source.unlink()
    artifact["compression"] = compression
    return artifact, uncompressed_sha256


def _proof_tools() -> dict[str, str]:
    tools = {name: shutil.which(name) for name in ("cadical", "drat-trim", "lrat-check")}
    missing = [name for name, path in tools.items() if path is None]
    if missing:
        raise RuntimeError(f"missing external tools: {', '.join(missing)}")
    return {name: str(path) for name, path in tools.items() if path is not None}


def direct_prove(profile: str, output: Path, reuse_raw: bool = False) -> dict[str, object]:
    """Solve one base profile and store a compact proof with DRAT/LRAT replay."""

    canonical = canonical_profile(profile)
    if canonical not in SAT_PROFILES:
        raise ValueError(f"profile is not in the thirteen-case SAT scope: {canonical}")
    output.mkdir(parents=True, exist_ok=True)
    tools = _proof_tools()
    slug = profile_slug(canonical)
    formula_path = output / f"{slug}.cnf"
    raw = output / f"{slug}.raw.drat"
    lrat = output / f"{slug}.lrat"
    core_drat = output / f"{slug}.drat"
    metadata_path = output / f"{slug}.json"
    started = time.monotonic()
    cnf, _, degrees = build_profile_formula(canonical)
    cnf.to_file(str(formula_path))

    if not reuse_raw:
        _run(
            [tools["cadical"], "--unsat", "-q", str(formula_path), str(raw)],
            output,
            output / f"{slug}.cadical.log",
            (0, 20),
        )
    elif not raw.exists():
        raise RuntimeError(f"--reuse-raw requested but {raw} does not exist")
    _run(
        [tools["drat-trim"], str(formula_path), str(raw), "-L", str(lrat)],
        output,
        output / f"{slug}.lrat-generate.log",
    )
    _run(
        [tools["lrat-check"], str(formula_path), str(lrat), str(core_drat)],
        output,
        output / f"{slug}.lrat-replay.log",
    )
    if "VERIFIED" not in (output / f"{slug}.lrat-replay.log").read_text(
        encoding="utf-8", errors="replace"
    ):
        raise RuntimeError(f"lrat-check did not report VERIFIED for {slug}")
    _run(
        [tools["drat-trim"], str(formula_path), str(core_drat)],
        output,
        output / f"{slug}.core-drat-replay.log",
    )
    if "VERIFIED" not in (output / f"{slug}.core-drat-replay.log").read_text(
        encoding="utf-8", errors="replace"
    ):
        raise RuntimeError(f"drat-trim did not verify the compact core for {slug}")
    drat_artifact, uncompressed_drat_sha256 = _compress_drat(core_drat)
    lrat.unlink()
    raw.unlink()
    metadata = {
        "schema_version": 1,
        "profile": canonical,
        "column_order": degrees,
        "formula": {
            "file": formula_path.name,
            "sha256": _sha256(formula_path),
            "variables": cnf.nv,
            "clauses": len(cnf.clauses),
        },
        "strategy": "direct_cadical",
        "proof": {
            "cadical_version": subprocess.check_output(
                [tools["cadical"], "--version"], text=True
            ).strip(),
            "drat": {
                **drat_artifact,
                "uncompressed_sha256": uncompressed_drat_sha256,
            },
            "independent_replay": {
                "drat_trim": "VERIFIED",
                "lrat_check": "VERIFIED",
            },
        },
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return metadata


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="list the thirteen SAT profiles")
    list_parser.set_defaults(profile=None, output=None)
    for name in ("frontier", "cubes", "direct"):
        command = subparsers.add_parser(name)
        command.add_argument("profile")
        command.add_argument("--output", type=Path, required=True)
        if name == "frontier":
            command.add_argument("--depth", type=int, default=4)
        elif name == "cubes":
            command.add_argument("--conflicts", type=int, default=20_000)
            command.add_argument("--maximum-depth", type=int, default=10)
            command.add_argument("--depth-factor", type=int, default=1)
            command.add_argument("--escalate-after", type=int, default=99)
            command.add_argument("--maximum-conflicts", type=int, default=0)
        elif name == "direct":
            command.add_argument("--reuse-raw", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "list":
        print("\n".join(SAT_PROFILES))
        return 0
    args.output = args.output.resolve()
    if args.command == "frontier":
        result = generate_frontier(args.profile, args.output, args.depth)
    elif args.command == "cubes":
        result = generate_cubes(
            args.profile,
            args.output,
            args.conflicts,
            args.maximum_depth,
            args.depth_factor,
            args.escalate_after,
            args.maximum_conflicts,
        )
    else:
        result = direct_prove(args.profile, args.output, args.reuse_raw)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
