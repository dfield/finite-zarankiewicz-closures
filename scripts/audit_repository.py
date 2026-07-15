#!/usr/bin/env python3
"""Run repository-wide structural and artifact-integrity checks.

This gate is intentionally independent of unit-test discovery.  It checks the
proof-first Git history, strict DIMACS structure, exact generated clauses,
documentation links, source docstrings, prohibited path leakage, JSON reports,
and the mathematical witness/certificate from their public APIs.
"""

from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_TREE_NAMES = frozenset({".git", ".lake", "__pycache__", ".venv"})
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.certificate import verify_certificate  # noqa: E402
from finite_zarankiewicz_closures.case_certificates import (  # noqa: E402
    ALL_CASE_SPECS,
    CASE_SPECS,
    verify_case_certificate,
)
from finite_zarankiewicz_closures.extended import (  # noqa: E402
    extended_frontier_report,
    z10_22_certificate_report,
    z12_23_certificate_report,
    z13_23_upper_report,
    verify_z13_23_upper_certificate,
)
from finite_zarankiewicz_closures.matrix import (  # noqa: E402
    read_boolean_csv,
    verify_by_row_triples,
)


EXPECTED_FILES = (
    "README.md",
    "docs/PROOF.md",
    "docs/PROOF_Z10_21.md",
    "docs/PROOF_Z10_22.md",
    "docs/PROOF_Z10_23.md",
    "docs/PROOF_Z11_19.md",
    "docs/PROOF_Z11_20.md",
    "docs/PROOF_Z11_23.md",
    "docs/PROOF_Z12_23.md",
    "docs/BOUND_Z13_23.md",
    "docs/NEW_BOUNDS.md",
    "docs/SAT_Z10_23_STATUS.md",
    "docs/LITERATURE_REVIEW.md",
    "docs/METHODS.md",
    "docs/ADVERSARIAL_AUDIT.md",
    "docs/REPRODUCIBILITY.md",
    "docs/AWS_Z10_23_RUN.md",
    "docs/EXTENDED_RESULTS.md",
    "data/z9_23_103_matrix.csv",
    "data/z10_21_106_matrix.csv",
    "data/z10_22_110_matrix.csv",
    "data/z10_23_112_matrix.csv",
    "data/z11_19_106_matrix.csv",
    "data/z11_20_111_matrix.csv",
    "data/z11_23_123_matrix.csv",
    "data/z12_23_134_matrix.csv",
    "certificates/degree_deficit.json",
    "certificates/z9_23_103.json",
    "certificates/z10_21_106.json",
    "certificates/z10_22_110.json",
    "certificates/z10_23_112.json",
    "certificates/z10_23_sat.json",
    "certificates/z10_23/vipr/profile-b-vipr-final-manifest.json",
    "certificates/z10_23/vipr/profile-c-vipr-final-manifest.json",
    "certificates/z10_23/vipr/profile-b-deficit-orbits.jsonl",
    "certificates/z10_23/vipr/profile-c-degree6-orbits.jsonl",
    "certificates/z10_23/vipr/3d1_4d4_5d14_6d4.vipr-certificates.release.json",
    "certificates/z10_23/vipr/3d1_4d3_5d16_6d3.vipr-certificates.release.json",
    "certificates/z11_19_106.json",
    "certificates/z11_20_111.json",
    "certificates/z11_23_123.json",
    "certificates/z12_23_134.json",
    "certificates/z13_23_upper_144.json",
    "models/cells_9x23_exact_104.cnf",
    "models/column_types_9x23_exact_104.lp",
    "models/cells_10x21_exact_107.cnf",
    "models/column_types_10x21_exact_107.lp",
    "models/cells_10x22_exact_111.cnf",
    "models/column_types_10x22_exact_111.lp",
    "models/cells_10x23_exact_113.cnf",
    "models/column_types_10x23_exact_113.lp",
    "models/cells_11x19_exact_107.cnf",
    "models/column_types_11x19_exact_107.lp",
    "models/cells_11x20_exact_112.cnf",
    "models/column_types_11x20_exact_112.lp",
    "models/cells_11x23_exact_124.cnf",
    "models/column_types_11x23_exact_124.lp",
    "models/cells_12x23_exact_135.cnf",
    "models/column_types_12x23_exact_135.lp",
    "analysis/dgh_boundary.json",
    "analysis/local_kernel_catalog.csv",
    "analysis/extended_results.json",
    "analysis/new_bounds.json",
    "analysis/sat_cross_check.json",
    "analysis/result_status.json",
    "lean/ZarankiewiczZ923/ArithmeticKernel.lean",
    "lean/ZarankiewiczFiniteClosures/ArithmeticKernels.lean",
    "artifacts.sha256",
)


def repository_paths() -> Iterator[Path]:
    """Yield publishable paths without descending into VCS or build caches."""

    for directory, names, files in os.walk(ROOT, followlinks=False):
        names[:] = [name for name in names if name not in EXCLUDED_TREE_NAMES]
        base = Path(directory)
        yield from (base / name for name in names)
        yield from (base / name for name in files)


def repository_files() -> Iterator[Path]:
    """Yield ordinary publishable files."""

    yield from (path for path in repository_paths() if path.is_file())


def sha256(path: Path) -> str:
    """Hash one file incrementally so large compressed proofs remain safe."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_required_files() -> dict[str, object]:
    """Require the reviewer-facing and mathematical deliverables."""

    missing = [relative for relative in EXPECTED_FILES if not (ROOT / relative).is_file()]
    if missing:
        raise AssertionError(f"missing required files: {missing}")
    return {"required_files": len(EXPECTED_FILES)}


def check_no_path_leaks_or_symlinks() -> dict[str, object]:
    """Reject private-workspace markers, absolute user paths, and symlinks."""

    symlinks = [
        path.relative_to(ROOT).as_posix()
        for path in repository_paths()
        if path.is_symlink()
    ]
    if symlinks:
        raise AssertionError(f"symlinks are not permitted: {symlinks}")
    oversized = [
        (path.relative_to(ROOT).as_posix(), path.stat().st_size)
        for path in repository_files()
        if path.stat().st_size >= 100_000_000
    ]
    if oversized:
        raise AssertionError(f"files exceed the GitHub 100 MB limit: {oversized}")
    # Construct the markers so the scanner does not contain the strings it rejects.
    markers = {
        "private workspace marker": ("r" + "55").encode("ascii"),
        "POSIX user path": ("/" + "Users" + "/").encode("ascii"),
        "Windows user path": ("C:" + "\\" + "Users" + "\\").encode("ascii"),
        "file URI": ("file" + "://").encode("ascii"),
    }
    findings: list[tuple[str, str]] = []
    scanned = 0
    maximum_marker_length = max(map(len, markers.values()))
    text_suffixes = {
        ".bib",
        ".c",
        ".cff",
        ".cnf",
        ".csv",
        ".drat",
        ".h",
        ".json",
        ".lean",
        ".lp",
        ".lrat",
        ".md",
        ".py",
        ".sha256",
        ".toml",
        ".txt",
        ".yaml",
        ".yml",
    }
    text_names = {"Makefile", ".gitignore", "LICENSE"}
    for path in repository_files():
        if path.suffix.lower() not in text_suffixes and path.name not in text_names:
            continue
        scanned += 1
        tail = b""
        found: set[str] = set()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                lowered = (tail + block).lower()
                for label, marker in markers.items():
                    if label not in found and marker.lower() in lowered:
                        findings.append((path.relative_to(ROOT).as_posix(), label))
                        found.add(label)
                tail = lowered[-maximum_marker_length:]
    if findings:
        raise AssertionError(f"path/provenance leakage: {findings}")
    return {"files_scanned": scanned, "symlinks": 0, "oversized_files": 0, "leaks": 0}


def check_markdown_links() -> dict[str, object]:
    """Check every local Markdown link target."""

    pattern = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
    checked = 0
    broken: list[str] = []
    for path in repository_files():
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        for raw_target in pattern.findall(text):
            target = raw_target.strip().split()[0].strip("<>")
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            checked += 1
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                broken.append(f"{path.relative_to(ROOT)} -> outside repository: {target}")
                continue
            if not resolved.exists():
                broken.append(f"{path.relative_to(ROOT)} -> {target}")
    if broken:
        raise AssertionError(f"broken local Markdown links: {broken}")
    return {"local_links_checked": checked}


def check_python_documentation() -> dict[str, object]:
    """Require module and public API docstrings in the reusable package."""

    modules = 0
    public_objects = 0
    missing: list[str] = []
    package = ROOT / "src" / "finite_zarankiewicz_closures"
    for path in sorted(package.glob("*.py")):
        modules += 1
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if ast.get_docstring(tree) is None:
            missing.append(f"{path.name}: module")
        for node in tree.body:
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ) and not node.name.startswith("_"):
                public_objects += 1
                if ast.get_docstring(node) is None:
                    missing.append(f"{path.name}: {node.name}")
    if missing:
        raise AssertionError(f"missing public documentation: {missing}")
    return {"package_modules": modules, "documented_public_objects": public_objects}


def parse_dimacs(
    path: Path, expected_prefix: Iterator[tuple[int, ...]] | None = None
) -> tuple[int, int]:
    """Strictly parse one-clause-per-line DIMACS and optionally check a prefix."""

    variables = None
    declared_clauses = None
    clauses = 0
    expected = iter(expected_prefix) if expected_prefix is not None else None
    expected_exhausted = False
    with path.open(encoding="ascii") as handle:
        for line_number, raw in enumerate(handle, start=1):
            line = raw.strip()
            if not line or line.startswith("c"):
                continue
            if line.startswith("p "):
                if variables is not None:
                    raise AssertionError(f"{path.name}: duplicate header")
                fields = line.split()
                if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
                    raise AssertionError(f"{path.name}: malformed header")
                variables, declared_clauses = int(fields[2]), int(fields[3])
                continue
            if variables is None:
                raise AssertionError(f"{path.name}:{line_number}: clause before header")
            values = [int(token) for token in line.split()]
            if not values or values[-1] != 0 or 0 in values[:-1]:
                raise AssertionError(f"{path.name}:{line_number}: malformed clause terminator")
            clause = tuple(values[:-1])
            if any(abs(literal) > variables for literal in clause):
                raise AssertionError(f"{path.name}:{line_number}: variable outside header range")
            if expected is not None and not expected_exhausted:
                try:
                    wanted = next(expected)
                except StopIteration:
                    expected_exhausted = True
                else:
                    if clause != wanted:
                        raise AssertionError(
                            f"{path.name}: forbidden-clause mismatch at index {clauses}"
                        )
            clauses += 1
    if variables is None or declared_clauses is None or clauses != declared_clauses:
        raise AssertionError(
            f"{path.name}: header/body mismatch, declared {declared_clauses}, found {clauses}"
        )
    if expected is not None and not expected_exhausted:
        try:
            next(expected)
        except StopIteration:
            pass
        else:
            raise AssertionError(f"{path.name}: expected prefix was truncated")
    return variables, clauses


def expected_cell_forbidders(rows: int, columns: int) -> Iterator[tuple[int, ...]]:
    """Yield all direct forbidden clauses independently of the generator."""

    for row_triple in itertools.combinations(range(rows), 3):
        for column_triple in itertools.combinations(range(columns), 3):
            yield tuple(
                -(row * columns + column + 1)
                for row in row_triple
                for column in column_triple
            )


def check_models() -> dict[str, object]:
    """Parse all CNFs and verify stored model metadata and hashes."""

    manifest = json.loads((ROOT / "models" / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 2 or set(manifest.get("cases", {})) != {
        case.slug for case in ALL_CASE_SPECS
    }:
        raise AssertionError("model manifest does not cover every tracked case")
    case_reports = {}
    for case in ALL_CASE_SPECS:
        entry = manifest["cases"][case.slug]
        if entry.get("publication_status") != case.publication_status:
            raise AssertionError(f"wrong publication status: {case.slug}")
        cell_metadata = entry["cell_cnf"]
        column_metadata = entry["column_lp"]
        cell = ROOT / cell_metadata["file"]
        cell_variables, cell_clauses = parse_dimacs(
            cell, expected_cell_forbidders(case.rows, case.columns)
        )
        if (
            cell_variables != cell_metadata["variables_total"]
            or cell_clauses != cell_metadata["clauses_total"]
        ):
            raise AssertionError(f"unexpected cell-model dimensions: {case.slug}")
        if cell_metadata["forbidden_submatrix_clauses"] != math.comb(
            case.rows, 3
        ) * math.comb(case.columns, 3):
            raise AssertionError(f"wrong forbidden-clause count: {case.slug}")
        if sha256(cell) != cell_metadata["sha256"]:
            raise AssertionError(f"cell model hash mismatch: {case.slug}")
        lp_path = ROOT / column_metadata["file"]
        lp = lp_path.read_text(encoding="ascii")
        expected_triples = math.comb(case.rows, 3)
        expected_supports = 1 << case.rows
        if (
            lp.count("\n triple_") != expected_triples
            or lp.count("\n x_") != expected_supports
            or not lp.endswith("End\n")
            or sha256(lp_path) != column_metadata["sha256"]
        ):
            raise AssertionError(f"column LP has unexpected structure: {case.slug}")
        case_reports[case.slug] = {
            "publication_status": case.publication_status,
            "cell_variables": cell_variables,
            "cell_clauses": cell_clauses,
            "forbidden_prefix_clauses": cell_metadata["forbidden_submatrix_clauses"],
            "column_support_variables": expected_supports,
            "column_triple_constraints": expected_triples,
        }
    terminal_dimensions = {}
    for case in ("balanced", "one_degree_3", "one_degree_6"):
        terminal_dimensions[case] = parse_dimacs(ROOT / "models" / f"terminal_{case}.cnf")
    return {
        "cases": case_reports,
        "terminal_dimensions": terminal_dimensions,
    }


def check_json_and_recorded_reports() -> dict[str, object]:
    """Parse every JSON file and require successful recorded audit reports."""

    parsed = 0
    for path in repository_files():
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
            parsed += 1
    for relative in (
        "audit/model_validation.json",
        "audit/certificate_replay.json",
    ):
        report = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        if report.get("status") != "VERIFIED":
            raise AssertionError(f"recorded audit report is not verified: {relative}")
    status = json.loads(
        (ROOT / "analysis" / "result_status.json").read_text(encoding="utf-8")
    )
    expected_exact = {case.theorem for case in CASE_SPECS}
    if status.get("schema_version") != 1 or set(
        status.get("established_exact_values", [])
    ) != expected_exact:
        raise AssertionError("result-status exact theorem boundary is inconsistent")
    if status.get("candidates") != []:
        raise AssertionError("result-status candidate boundary is inconsistent")
    return {"json_files_parsed": parsed, "verified_recorded_reports": 2}


def check_mathematical_artifacts() -> dict[str, object]:
    """Invoke the public witness and certificate APIs on stored inputs."""

    matrix_path = ROOT / "data" / "z9_23_103_matrix.csv"
    matrix = read_boolean_csv(matrix_path)
    matrix_report = verify_by_row_triples(matrix, raw_bytes=matrix_path.read_bytes())
    if not matrix_report.valid:
        raise AssertionError("stored witness failed the row-triple verifier")
    certificate = json.loads(
        (ROOT / "certificates" / "degree_deficit.json").read_text(encoding="utf-8")
    )
    certificate_report = verify_certificate(certificate)
    if certificate_report["status"] != "VERIFIED":
        raise AssertionError("stored exact certificate failed")
    extended_witnesses = []
    for filename, rows, columns, ones in (
        ("z10_21_106_matrix.csv", 10, 21, 106),
        ("z10_22_110_matrix.csv", 10, 22, 110),
        ("z10_23_112_matrix.csv", 10, 23, 112),
        ("z11_19_106_matrix.csv", 11, 19, 106),
        ("z11_20_111_matrix.csv", 11, 20, 111),
        ("z11_23_123_matrix.csv", 11, 23, 123),
        ("z12_23_134_matrix.csv", 12, 23, 134),
    ):
        path = ROOT / "data" / filename
        report = verify_by_row_triples(
            read_boolean_csv(path),
            expected_rows=rows,
            expected_columns=columns,
            expected_ones=ones,
            raw_bytes=path.read_bytes(),
        )
        if not report.valid:
            raise AssertionError(f"stored extended witness failed: {filename}")
        extended_witnesses.append(report.ones)
    extended_certificate = z10_22_certificate_report()
    if extended_certificate["status"] != "VERIFIED":
        raise AssertionError("extended exact certificate failed")
    z12_certificate = z12_23_certificate_report()
    if z12_certificate["status"] != "VERIFIED":
        raise AssertionError("Z(12,23) exact certificate failed")
    z13_certificate = z13_23_upper_report()
    if z13_certificate["status"] != "VERIFIED":
        raise AssertionError("Z(13,23) upper-bound certificate failed")
    stored_z13_certificate = json.loads(
        (ROOT / "certificates" / "z13_23_upper_144.json").read_text(encoding="utf-8")
    )
    verify_z13_23_upper_certificate(stored_z13_certificate)
    frontier = extended_frontier_report()
    if frontier["source_open_cases"] != 44 or frontier["remaining_open_cases"] != 33:
        raise AssertionError("extended frontier count mismatch")
    case_certificate_reports = []
    for case in CASE_SPECS:
        case_path = ROOT / "certificates" / f"{case.slug}.json"
        case_certificate_reports.append(
            verify_case_certificate(
                json.loads(case_path.read_text(encoding="utf-8")), ROOT
            )
        )
    return {
        "witness_ones": matrix_report.ones,
        "extended_witness_ones": extended_witnesses,
        "row_triples_checked": matrix_report.row_triples_checked,
        "profiles_enumerated": certificate_report["profiles_enumerated"],
        "extended_profiles_enumerated": len(extended_certificate["degree_profiles"]),
        "z12_profiles_enumerated": len(z12_certificate["at_135"]["degree_profiles"]),
        "z13_profiles_enumerated": len(z13_certificate["cases"]),
        "remaining_open_cases": frontier["remaining_open_cases"],
        "case_certificates_verified": len(case_certificate_reports),
    }


def check_lean_source_boundary() -> dict[str, object]:
    """Reject explicit admissions or project-declared axioms in Lean source."""

    forbidden = re.compile(
        r"^\s*(?:sorry|admit|axiom)\b|:=\s*(?:by\s+)?(?:sorry|admit)\b"
    )
    findings = []
    files = 0
    for path in (ROOT / "lean").rglob("*.lean"):
        if ".lake" in path.parts:
            continue
        files += 1
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if forbidden.search(line):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}")
    if findings:
        raise AssertionError(f"Lean admissions/custom axioms found: {findings}")
    recorded = (ROOT / "audit" / "lean_axioms.txt").read_text(encoding="utf-8")
    if "native_decide" in recorded or "does not depend on any axioms" not in recorded:
        raise AssertionError("Lean axiom audit is missing or contains a native trust axiom")
    return {"lean_source_files": files, "admissions": 0, "project_axioms": 0}


def check_proof_first_history() -> dict[str, object]:
    """Verify that the root Git commit contains the human proof and no code."""

    shallow = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if shallow == "true":
        raise AssertionError(
            "proof-first history cannot be audited in a shallow clone; "
            "fetch the full Git history"
        )

    root_commit = subprocess.run(
        ["git", "rev-list", "--max-parents=0", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip().splitlines()
    if len(root_commit) != 1:
        raise AssertionError("expected exactly one Git root commit")
    files = subprocess.run(
        ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", root_commit[0]],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip().splitlines()
    if files != ["docs/PROOF.md"]:
        raise AssertionError(f"root commit is not proof-only: {files}")
    return {"root_commit": root_commit[0], "root_commit_files": files}


def check_readme_attribution_and_checksums() -> dict[str, object]:
    """Check the required attribution and every artifact hash."""

    readme_lines = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()
    if not readme_lines or "GPT 5.6-Sol" not in "\n".join(readme_lines[:5]):
        raise AssertionError("README top does not attribute GPT 5.6-Sol")
    lines = (ROOT / "artifacts.sha256").read_text(encoding="ascii").splitlines()
    checked = 0
    for line in lines:
        digest, relative = line.split("  ", 1)
        path = ROOT / relative
        if not path.is_file() or sha256(path) != digest:
            raise AssertionError(f"artifact checksum mismatch: {relative}")
        checked += 1
    return {"readme_attribution": True, "artifact_hashes_checked": checked}


def main() -> int:
    checks = {
        "deliverables": check_required_files(),
        "path_hygiene": check_no_path_leaks_or_symlinks(),
        "markdown": check_markdown_links(),
        "python_documentation": check_python_documentation(),
        "models": check_models(),
        "json_reports": check_json_and_recorded_reports(),
        "mathematics": check_mathematical_artifacts(),
        "lean_boundary": check_lean_source_boundary(),
        "proof_first_history": check_proof_first_history(),
        "attribution_and_hashes": check_readme_attribution_and_checksums(),
    }
    print(json.dumps({"status": "VERIFIED", "checks": checks}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
