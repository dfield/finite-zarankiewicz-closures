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
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from zarankiewicz_z9_23.certificate import verify_certificate  # noqa: E402
from zarankiewicz_z9_23.matrix import read_boolean_csv, verify_by_row_triples  # noqa: E402


EXPECTED_FILES = (
    "README.md",
    "docs/PROOF.md",
    "docs/LITERATURE_REVIEW.md",
    "docs/METHODS.md",
    "docs/ADVERSARIAL_AUDIT.md",
    "docs/REPRODUCIBILITY.md",
    "data/z9_23_103_matrix.csv",
    "certificates/degree_deficit.json",
    "models/cells_9x23_exact_104.cnf",
    "models/column_types_9x23_exact_104.lp",
    "analysis/dgh_boundary.json",
    "analysis/local_kernel_catalog.csv",
    "lean/ZarankiewiczZ923/ArithmeticKernel.lean",
    "artifacts.sha256",
)


def repository_files() -> Iterator[Path]:
    """Yield ordinary files while excluding VCS and build caches."""

    excluded = {".git", ".lake", "__pycache__", ".venv"}
    for path in ROOT.rglob("*"):
        if any(part in excluded for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file():
            yield path


def check_required_files() -> dict[str, object]:
    """Require the reviewer-facing and mathematical deliverables."""

    missing = [relative for relative in EXPECTED_FILES if not (ROOT / relative).is_file()]
    if missing:
        raise AssertionError(f"missing required files: {missing}")
    return {"required_files": len(EXPECTED_FILES)}


def check_no_path_leaks_or_symlinks() -> dict[str, object]:
    """Reject private-workspace markers, absolute user paths, and symlinks."""

    symlinks = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_symlink()]
    if symlinks:
        raise AssertionError(f"symlinks are not permitted: {symlinks}")
    # Construct the markers so the scanner does not contain the strings it rejects.
    markers = {
        "private workspace marker": ("r" + "55").encode("ascii"),
        "POSIX user path": ("/" + "Users" + "/").encode("ascii"),
        "Windows user path": ("C:" + "\\" + "Users" + "\\").encode("ascii"),
        "file URI": ("file" + "://").encode("ascii"),
    }
    findings: list[tuple[str, str]] = []
    scanned = 0
    for path in repository_files():
        scanned += 1
        lowered = path.read_bytes().lower()
        for label, marker in markers.items():
            if marker.lower() in lowered:
                findings.append((path.relative_to(ROOT).as_posix(), label))
    if findings:
        raise AssertionError(f"path/provenance leakage: {findings}")
    return {"files_scanned": scanned, "symlinks": 0, "leaks": 0}


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
    package = ROOT / "src" / "zarankiewicz_z9_23"
    for path in sorted(package.glob("*.py")):
        modules += 1
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if ast.get_docstring(tree) is None:
            missing.append(f"{path.name}: module")
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
                public_objects += 1
                if ast.get_docstring(node) is None:
                    missing.append(f"{path.name}: {node.name}")
    if missing:
        raise AssertionError(f"missing public documentation: {missing}")
    return {"package_modules": modules, "documented_public_objects": public_objects}


def parse_dimacs(path: Path, expected_prefix: Iterator[tuple[int, ...]] | None = None) -> tuple[int, int]:
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


def expected_cell_forbidders() -> Iterator[tuple[int, ...]]:
    """Yield all direct 9-by-23 forbidden clauses independently of the generator."""

    for rows in itertools.combinations(range(9), 3):
        for columns in itertools.combinations(range(23), 3):
            yield tuple(-(row * 23 + column + 1) for row in rows for column in columns)


def check_models() -> dict[str, object]:
    """Parse all CNFs and verify stored model metadata and hashes."""

    cell = ROOT / "models" / "cells_9x23_exact_104.cnf"
    cell_variables, cell_clauses = parse_dimacs(cell, expected_cell_forbidders())
    if (cell_variables, cell_clauses) != (32654, 277931):
        raise AssertionError("unexpected target cell-model dimensions")
    terminal_dimensions = {}
    for case in ("balanced", "one_degree_3", "one_degree_6"):
        terminal_dimensions[case] = parse_dimacs(ROOT / "models" / f"terminal_{case}.cnf")
    manifest = json.loads((ROOT / "models" / "manifest.json").read_text(encoding="utf-8"))
    expected_hashes = {
        "cell_cnf": hashlib.sha256(cell.read_bytes()).hexdigest(),
        "column_lp": hashlib.sha256(
            (ROOT / "models" / "column_types_9x23_exact_104.lp").read_bytes()
        ).hexdigest(),
    }
    for name, digest in expected_hashes.items():
        if manifest["models"][name]["sha256"] != digest:
            raise AssertionError(f"model manifest hash mismatch: {name}")
    lp = (ROOT / "models" / "column_types_9x23_exact_104.lp").read_text(encoding="ascii")
    if lp.count("\n triple_") != 84 or lp.count("\n x_") != 512 or not lp.endswith("End\n"):
        raise AssertionError("column LP has unexpected structure")
    return {
        "cell_variables": cell_variables,
        "cell_clauses": cell_clauses,
        "forbidden_prefix_clauses": 148764,
        "terminal_dimensions": terminal_dimensions,
        "column_support_variables": 512,
        "column_triple_constraints": 84,
    }


def check_json_and_recorded_reports() -> dict[str, object]:
    """Parse every JSON file and require successful recorded audit reports."""

    parsed = 0
    for path in repository_files():
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
            parsed += 1
    for relative in ("audit/model_validation.json", "audit/certificate_replay.json"):
        report = json.loads((ROOT / relative).read_text(encoding="utf-8"))
        if report.get("status") != "VERIFIED":
            raise AssertionError(f"recorded audit report is not verified: {relative}")
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
    return {
        "witness_ones": matrix_report.ones,
        "row_triples_checked": matrix_report.row_triples_checked,
        "profiles_enumerated": certificate_report["profiles_enumerated"],
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
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
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
