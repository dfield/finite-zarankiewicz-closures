#!/usr/bin/env python3
"""Replay every compressed DRAT core and independently check its derived LRAT."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
import hashlib
import json
import lzma
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Iterator, Mapping

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "certificates" / "z10_23_sat.json"
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.sat_certificate import (  # noqa: E402
    load_and_verify_z10_23_sat_manifest,
)


def _decompress_proof(case: Mapping[str, Any], destination: BinaryIO) -> None:
    """Stream one direct or byte-split XZ proof into an open destination."""

    proof = case["proof"]
    if not isinstance(proof, dict):
        raise ValueError("missing proof metadata")
    if "file" in proof:
        with lzma.open(ROOT / proof["file"], "rb") as source:
            shutil.copyfileobj(source, destination, length=1024 * 1024)
        return
    with tempfile.NamedTemporaryFile(suffix=".drat.xz") as archive:
        for part in proof["parts"]:
            with (ROOT / part["file"]).open("rb") as source:
                shutil.copyfileobj(source, archive, length=1024 * 1024)
        archive.flush()
        with lzma.open(archive.name, "rb") as source:
            shutil.copyfileobj(source, destination, length=1024 * 1024)


@contextmanager
def _cube_archive(case: Mapping[str, Any]) -> Iterator[Path]:
    """Yield a direct or reassembled cube-proof tar/xz archive path."""

    archive = case["proof"]["archive"]
    if archive.get("format") == "TAR+DRAT+xz+github-release-parts":
        release = archive["release"]
        asset_directory = os.environ.get("Z10_23_ASSET_DIR")
        with tempfile.TemporaryDirectory(prefix="z10_23_release_assets_") as directory:
            temporary = Path(directory)
            combined = temporary / "cube-proofs.tar.xz"
            digest = hashlib.sha256()
            total_bytes = 0
            with combined.open("wb") as output:
                for part in archive["parts"]:
                    if asset_directory:
                        source = Path(asset_directory) / part["name"]
                    else:
                        gh = shutil.which("gh")
                        if gh is None:
                            raise RuntimeError(
                                "gh is required to fetch release-backed proof archives"
                            )
                        completed = subprocess.run(
                            [
                                gh,
                                "release",
                                "download",
                                release["tag"],
                                "--repo",
                                release["repository"],
                                "--pattern",
                                part["name"],
                                "--dir",
                                str(temporary),
                                "--clobber",
                            ],
                            check=False,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            text=True,
                        )
                        if completed.returncode != 0:
                            raise RuntimeError(completed.stdout[-2000:])
                        source = temporary / part["name"]
                    if (
                        not source.is_file()
                        or source.stat().st_size != part["bytes"]
                        or _sha256(source) != part["sha256"]
                    ):
                        raise ValueError(f"release asset integrity failure: {part['name']}")
                    with source.open("rb") as handle:
                        for block in iter(lambda: handle.read(1024 * 1024), b""):
                            digest.update(block)
                            output.write(block)
                            total_bytes += len(block)
            if total_bytes != archive["bytes"] or digest.hexdigest() != archive["sha256"]:
                raise ValueError("reassembled release archive integrity failure")
            yield combined
        return
    if "file" in archive:
        yield ROOT / archive["file"]
        return
    with tempfile.NamedTemporaryFile(suffix=".cube-proofs.tar.xz") as combined:
        for part in archive["parts"]:
            with (ROOT / part["file"]).open("rb") as source:
                shutil.copyfileobj(source, combined, length=1024 * 1024)
        combined.flush()
        yield Path(combined.name)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _leaf_formula(
    base: Path,
    masks: list[int],
    literals: list[int],
    destination: Path,
) -> None:
    """Append one cube's cell literals as unit clauses to the base formula."""

    raw = base.read_bytes()
    header, separator, body = raw.partition(b"\n")
    fields = header.split()
    if not separator or fields[:2] != [b"p", b"cnf"] or len(fields) != 4:
        raise ValueError(f"malformed base formula: {base}")
    variables, clauses = int(fields[2]), int(fields[3])
    units = [
        row * 23 + column + 1
        if mask & (1 << row)
        else -(row * 23 + column + 1)
        for column, mask in enumerate(masks)
        for row in range(10)
    ] + literals
    with destination.open("wb") as handle:
        handle.write(f"p cnf {variables} {clauses + len(units)}\n".encode())
        handle.write(body)
        for literal in units:
            handle.write(f"{literal} 0\n".encode())


def _replay_cube_leaf(
    formula: Path,
    proof: Path,
    masks: list[int],
    literals: list[int],
    drat_trim: str,
    lrat_check: str,
) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="z10_23_cube_leaf_") as directory:
        leaf_formula = Path(directory) / "leaf.cnf"
        derived_lrat = Path(directory) / "leaf.lrat"
        _leaf_formula(formula, masks, literals, leaf_formula)
        drat_completed = subprocess.run(
            [drat_trim, str(leaf_formula), str(proof), "-L", str(derived_lrat)],
            cwd=ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if drat_completed.returncode != 0 or "VERIFIED" not in drat_completed.stdout:
            return False, drat_completed.stdout[-2000:]
        lrat_completed = subprocess.run(
            [lrat_check, str(leaf_formula), str(derived_lrat)],
            cwd=ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        if lrat_completed.returncode != 0 or "VERIFIED" not in lrat_completed.stdout:
            return False, lrat_completed.stdout[-2000:]
    return True, ""


def _replay_cube_case(
    case: Mapping[str, Any],
    formula: Path,
    drat_trim: str,
    lrat_check: str,
    workers: int,
) -> dict[str, Any]:
    proof = case["proof"]
    catalog_path = ROOT / proof["catalog"]["file"]
    index_path = ROOT / proof["proof_index"]["file"]
    catalog = [json.loads(line) for line in catalog_path.read_text(encoding="ascii").splitlines()]
    index = [json.loads(line) for line in index_path.read_text(encoding="ascii").splitlines()]
    with tempfile.TemporaryDirectory(prefix="z10_23_cube_archive_") as directory:
        extracted = Path(directory)
        expected = {record["file"]: record for record in index}
        observed: set[str] = set()
        with _cube_archive(case) as archive_path:
            with tarfile.open(archive_path, mode="r:xz") as archive:
                for member in archive:
                    path = Path(member.name)
                    if path.is_absolute() or ".." in path.parts or member.issym() or member.islnk():
                        raise ValueError(f"unsafe cube-proof archive member: {member.name}")
                    if member.isdir():
                        continue
                    if not member.isfile() or member.name not in expected:
                        raise ValueError(f"unexpected cube-proof archive member: {member.name}")
                    if member.name in observed:
                        raise ValueError(f"duplicate cube-proof archive member: {member.name}")
                    destination = extracted / member.name
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    source = archive.extractfile(member)
                    if source is None:
                        raise ValueError(f"unreadable cube-proof archive member: {member.name}")
                    with destination.open("wb") as handle:
                        shutil.copyfileobj(source, handle, length=1024 * 1024)
                    record = expected[member.name]
                    if destination.stat().st_size != record["bytes"] or _sha256(destination) != record["sha256"]:
                        raise ValueError(f"cube-proof member integrity failure: {member.name}")
                    observed.add(member.name)
        if observed != set(expected):
            raise ValueError("cube-proof archive does not contain exactly the indexed leaves")

        failures = []
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    _replay_cube_leaf,
                    formula,
                    extracted / record["file"],
                    catalog[position]["masks"],
                    catalog[position].get("literals", []),
                    drat_trim,
                    lrat_check,
                ): position
                for position, record in enumerate(index)
            }
            for future in as_completed(futures):
                verified, output_tail = future.result()
                if not verified:
                    failures.append(
                        {"leaf": futures[future], "output_tail": output_tail}
                    )
        return {
            "profile": case["profile"],
            "strategy": case["strategy"],
            "verified": not failures,
            "leaf_count": len(index),
            "drat_checker": "drat-trim",
            "drat_verified": not failures,
            "lrat_checker": "lrat-check",
            "lrat_verified": not failures,
            **({"failures": failures[:10]} if failures else {}),
        }
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    if args.workers <= 0:
        parser.error("--workers must be positive")
    drat_trim = shutil.which("drat-trim")
    lrat_check = shutil.which("lrat-check")
    if drat_trim is None or lrat_check is None:
        print("drat-trim and lrat-check are required")
        return 2
    integrity = load_and_verify_z10_23_sat_manifest(ROOT)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    reports = []
    for case in manifest["profiles"]:
        formula = ROOT / case["formula"]["file"]
        if case["strategy"] == "row_stabilizer_cube_cover":
            report = _replay_cube_case(
                case, formula, drat_trim, lrat_check, args.workers
            )
            if not report["verified"]:
                print(json.dumps({"status": "REJECTED", "case": report}, indent=2))
                return 1
            reports.append(report)
            continue
        with tempfile.TemporaryDirectory(prefix="z10_23_replay_") as directory:
            proof = Path(directory) / "proof.drat"
            derived_lrat = Path(directory) / "proof.lrat"
            with proof.open("wb") as destination:
                _decompress_proof(case, destination)
            drat_completed = subprocess.run(
                [drat_trim, str(formula), str(proof), "-L", str(derived_lrat)],
                cwd=ROOT,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            drat_verified = (
                drat_completed.returncode == 0 and "VERIFIED" in drat_completed.stdout
            )
            if drat_verified:
                lrat_completed = subprocess.run(
                    [lrat_check, str(formula), str(derived_lrat)],
                    cwd=ROOT,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
                lrat_verified = (
                    lrat_completed.returncode == 0 and "VERIFIED" in lrat_completed.stdout
                )
            else:
                lrat_completed = None
                lrat_verified = False
        verified = drat_verified and lrat_verified
        report = {
            "profile": case["profile"],
            "strategy": case["strategy"],
            "verified": verified,
            "drat_checker": "drat-trim",
            "drat_verified": drat_verified,
            "lrat_checker": "lrat-check",
            "lrat_verified": lrat_verified,
        }
        if not verified:
            report["drat_output_tail"] = drat_completed.stdout[-2000:]
            if lrat_completed is not None:
                report["lrat_output_tail"] = lrat_completed.stdout[-2000:]
            print(json.dumps({"status": "REJECTED", "case": report}, indent=2))
            return 1
        reports.append(report)
    result = {
        "status": "VERIFIED",
        "theorem": manifest["theorem"],
        "integrity": integrity,
        "profile_count": len(reports),
        "profiles": reports,
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
