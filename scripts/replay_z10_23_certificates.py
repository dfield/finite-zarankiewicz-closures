#!/usr/bin/env python3
"""Replay every compressed DRAT core and independently check its derived LRAT."""

from __future__ import annotations

import argparse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from contextlib import contextmanager
from functools import lru_cache
import hashlib
import io
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
    _ConcatenatedReader,
    load_and_verify_z10_23_sat_manifest,
)
from finite_zarankiewicz_closures.vipr_certificate import (  # noqa: E402
    render_vipr_leaf_formula,
    verify_compressed_vipr_embedded_model,
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


def _jsonl_records(payload: Mapping[str, Any]) -> Iterator[Mapping[str, Any]]:
    """Stream one integrity-checked manifest JSONL artifact, optionally through XZ."""

    raw = None
    if "parts" in payload:
        raw = _ConcatenatedReader(
            [ROOT / part["file"] for part in payload["parts"]]
        )
        handle = lzma.open(io.BufferedReader(raw), "rt", encoding="ascii")
    else:
        path = ROOT / payload["file"]
    if raw is None and payload.get("compression") == "xz":
        handle = lzma.open(path, "rt", encoding="ascii")
    elif raw is None and payload.get("compression") is None:
        handle = path.open(encoding="ascii")
    elif raw is None:
        raise ValueError(f"unexpected JSONL compression: {payload.get('compression')}")
    try:
        with handle:
            for line in handle:
                if line.strip():
                    yield json.loads(line)
    finally:
        if raw is not None:
            raw.close()


@lru_cache(maxsize=None)
def _base_formula(path_text: str) -> tuple[int, int, bytes]:
    """Read one base formula once for all replay threads in its profile."""

    base = Path(path_text)
    raw = base.read_bytes()
    header, separator, body = raw.partition(b"\n")
    fields = header.split()
    if not separator or fields[:2] != [b"p", b"cnf"] or len(fields) != 4:
        raise ValueError(f"malformed base formula: {base}")
    return int(fields[2]), int(fields[3]), body


def _leaf_formula(
    base: Path,
    masks: list[int],
    literals: list[int],
    destination: Path,
) -> None:
    """Append one cube's cell literals as unit clauses to the base formula."""

    variables, clauses, body = _base_formula(str(base.resolve()))
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
    with tempfile.TemporaryDirectory(prefix="z10_23_cube_archive_") as directory:
        extracted = Path(directory)
        failures: list[dict[str, Any]] = []
        pending: dict[Future[tuple[bool, str]], tuple[int, Path]] = {}
        leaf_count = 0

        def collect(done: set[Future[tuple[bool, str]]]) -> None:
            for future in done:
                position, path = pending.pop(future)
                try:
                    verified, output_tail = future.result()
                    if not verified:
                        failures.append({"leaf": position, "output_tail": output_tail})
                finally:
                    path.unlink(missing_ok=True)

        with _cube_archive(case) as archive_path:
            catalog = _jsonl_records(proof["catalog"])
            index = _jsonl_records(proof["proof_index"])
            with ThreadPoolExecutor(max_workers=workers) as executor:
                with tarfile.open(archive_path, mode="r|xz") as archive:
                    for member in archive:
                        if member.isdir():
                            continue
                        path = Path(member.name)
                        if (
                            path.is_absolute()
                            or ".." in path.parts
                            or member.issym()
                            or member.islnk()
                            or not member.isfile()
                        ):
                            raise ValueError(
                                f"unsafe cube-proof archive member: {member.name}"
                            )
                        leaf = next(catalog, None)
                        record = next(index, None)
                        if leaf is None or record is None:
                            raise ValueError(
                                f"unexpected cube-proof archive member: {member.name}"
                            )
                        expected_name = f"proofs/leaf-{leaf_count:08d}.drat"
                        if (
                            member.name != expected_name
                            or record.get("file") != expected_name
                            or record.get("index") != leaf_count
                            or record.get("masks") != leaf.get("masks")
                            or record.get("literals", []) != leaf.get("literals", [])
                        ):
                            raise ValueError(
                                f"cube-proof archive order mismatch at leaf {leaf_count}"
                            )
                        destination = extracted / member.name
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        source = archive.extractfile(member)
                        if source is None:
                            raise ValueError(
                                f"unreadable cube-proof archive member: {member.name}"
                            )
                        digest = hashlib.sha256()
                        size = 0
                        with destination.open("wb") as handle:
                            while block := source.read(1024 * 1024):
                                digest.update(block)
                                handle.write(block)
                                size += len(block)
                        if (
                            size != record["bytes"]
                            or digest.hexdigest() != record["sha256"]
                        ):
                            raise ValueError(
                                f"cube-proof member integrity failure: {member.name}"
                            )
                        future = executor.submit(
                            _replay_cube_leaf,
                            formula,
                            destination,
                            leaf["masks"],
                            leaf.get("literals", []),
                            drat_trim,
                            lrat_check,
                        )
                        pending[future] = (leaf_count, destination)
                        leaf_count += 1
                        if len(pending) >= max(2, workers * 2):
                            done, _ = wait(pending, return_when=FIRST_COMPLETED)
                            collect(done)
                            if failures:
                                break
                    if not failures and (
                        next(catalog, None) is not None or next(index, None) is not None
                    ):
                        raise ValueError(
                            "cube-proof archive does not contain exactly the indexed leaves"
                        )
                if pending:
                    done, _ = wait(pending)
                    collect(done)
        return {
            "profile": case["profile"],
            "strategy": case["strategy"],
            "verified": not failures,
            "leaf_count": leaf_count,
            "drat_checker": "drat-trim",
            "drat_verified": not failures,
            "lrat_checker": "lrat-check",
            "lrat_verified": not failures,
            **({"failures": failures[:10]} if failures else {}),
        }


@contextmanager
def _vipr_release_parts(archive: Mapping[str, Any]) -> Iterator[list[Path]]:
    """Yield integrity-checked paths for a split release-backed VIPR tar."""

    if archive.get("format") != "TAR+VIPR+xz-members+github-release-parts":
        raise ValueError("unexpected VIPR release archive format")
    release = archive["release"]
    asset_directory = os.environ.get("Z10_23_ASSET_DIR")
    with tempfile.TemporaryDirectory(prefix="z10_23_vipr_assets_") as directory:
        temporary = Path(directory)
        paths = []
        for part in archive["parts"]:
            if asset_directory:
                source = Path(asset_directory) / part["name"]
            else:
                gh = shutil.which("gh")
                if gh is None:
                    raise RuntimeError(
                        "gh is required to fetch release-backed VIPR archives"
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
                raise ValueError(f"VIPR release asset integrity failure: {part['name']}")
            paths.append(source)
        yield paths


def _replay_vipr_leaf(
    compressed: Path,
    formula_text: str,
    viprchk: str,
) -> tuple[bool, str, dict[str, int]]:
    """Bind one certificate to its OPB and check the complete VIPR derivation."""

    with compressed.open("rb") as handle:
        model = verify_compressed_vipr_embedded_model(formula_text, handle)
    with tempfile.TemporaryDirectory(prefix="z10_23_vipr_leaf_") as directory:
        certificate = Path(directory) / "certificate.vipr"
        with lzma.open(compressed, "rb") as source, certificate.open("wb") as output:
            shutil.copyfileobj(source, output, length=8 * 1024 * 1024)
        checked = subprocess.run(
            [viprchk, str(certificate)],
            cwd=ROOT,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    verified = (
        checked.returncode == 0
        and "Successfully verified infeasibility." in checked.stdout
    )
    return verified, checked.stdout[-2000:], model


def _replay_vipr_case(
    case: Mapping[str, Any],
    viprchk: str,
    workers: int,
) -> dict[str, Any]:
    """Stream, model-bind, and independently check every VIPR orbit leaf."""

    proof = case["proof"]
    cover = json.loads((ROOT / proof["cover_manifest"]["file"]).read_text(encoding="ascii"))
    catalog = [
        json.loads(line)
        for line in (ROOT / proof["catalog"]["file"]).read_text(encoding="ascii").splitlines()
        if line.strip()
    ]
    leaves = cover["leaves"]
    if len(catalog) != len(leaves):
        raise ValueError("VIPR catalog and aggregate manifest have different sizes")
    failures: list[dict[str, Any]] = []
    model_bindings = 0
    leaf_count = 0
    pending: dict[
        Future[tuple[bool, str, dict[str, int]]], tuple[int, Path]
    ] = {}

    def collect(done: set[Future[tuple[bool, str, dict[str, int]]]]) -> None:
        nonlocal model_bindings
        for future in done:
            position, path = pending.pop(future)
            try:
                verified, output_tail, model = future.result()
                model_bindings += int(bool(model))
                if not verified:
                    failures.append({"leaf": position, "output_tail": output_tail})
            except Exception as error:  # preserve a compact report for long replays
                failures.append(
                    {
                        "leaf": position,
                        "error": f"{type(error).__name__}: {error}",
                    }
                )
            finally:
                path.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="z10_23_vipr_archive_") as directory:
        extracted = Path(directory)
        with _vipr_release_parts(proof["archive"]) as paths:
            raw = _ConcatenatedReader(paths)
            try:
                with ThreadPoolExecutor(max_workers=workers) as executor:
                    with tarfile.open(fileobj=io.BufferedReader(raw), mode="r|") as archive:
                        for member in archive:
                            if member.isdir():
                                continue
                            path = Path(member.name)
                            if (
                                path.is_absolute()
                                or ".." in path.parts
                                or member.issym()
                                or member.islnk()
                                or not member.isfile()
                                or leaf_count >= len(leaves)
                            ):
                                raise ValueError(
                                    f"unsafe or unexpected VIPR archive member: {member.name}"
                                )
                            expected_name = f"proofs/leaf-{leaf_count:06d}.vipr.xz"
                            artifact = leaves[leaf_count]["artifacts"]["certificate.vipr.xz"]
                            if member.name != expected_name or member.size != artifact["bytes"]:
                                raise ValueError(
                                    f"VIPR archive order mismatch at leaf {leaf_count}"
                                )
                            source = archive.extractfile(member)
                            if source is None:
                                raise ValueError(f"unreadable VIPR member: {member.name}")
                            destination = extracted / f"leaf-{leaf_count:06d}.vipr.xz"
                            digest = hashlib.sha256()
                            size = 0
                            with destination.open("wb") as output:
                                while block := source.read(8 * 1024 * 1024):
                                    digest.update(block)
                                    output.write(block)
                                    size += len(block)
                            if size != artifact["bytes"] or digest.hexdigest() != artifact["sha256"]:
                                raise ValueError(
                                    f"VIPR member integrity failure at leaf {leaf_count}"
                                )
                            formula_text, _ = render_vipr_leaf_formula(
                                ROOT, case["profile"], catalog[leaf_count]
                            )
                            future = executor.submit(
                                _replay_vipr_leaf,
                                destination,
                                formula_text,
                                viprchk,
                            )
                            pending[future] = (leaf_count, destination)
                            leaf_count += 1
                            if len(pending) >= max(2, workers * 2):
                                done, _ = wait(pending, return_when=FIRST_COMPLETED)
                                collect(done)
                                if failures:
                                    break
                        if not failures and leaf_count != len(leaves):
                            raise ValueError("VIPR archive does not contain every indexed leaf")
                    if pending:
                        done, _ = wait(pending)
                        collect(done)
            finally:
                raw.close()
    return {
        "profile": case["profile"],
        "strategy": case["strategy"],
        "verified": not failures and leaf_count == len(leaves),
        "leaf_count": leaf_count,
        "model_bindings_verified": model_bindings,
        "checker": "viprchk",
        **({"failures": failures[:10]} if failures else {}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument(
        "--profile",
        action="append",
        help="replay only this canonical comma-separated degree profile; repeatable",
    )
    args = parser.parse_args()
    if args.workers <= 0:
        parser.error("--workers must be positive")
    integrity = load_and_verify_z10_23_sat_manifest(ROOT)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = manifest["profiles"]
    known_profiles = {case["profile"] for case in cases}
    selected_profiles = set(args.profile or known_profiles)
    unknown = selected_profiles - known_profiles
    if unknown:
        parser.error(f"unknown --profile value(s): {', '.join(sorted(unknown))}")
    cases = [case for case in cases if case["profile"] in selected_profiles]
    needs_sat_tools = any(
        case["strategy"] in {"direct_cadical", "row_stabilizer_cube_cover"}
        for case in cases
    )
    needs_vipr = any(case["strategy"] == "scip_vipr_orbit_cover" for case in cases)
    drat_trim = shutil.which("drat-trim") if needs_sat_tools else None
    lrat_check = shutil.which("lrat-check") if needs_sat_tools else None
    viprchk = (
        os.environ.get("VIPRCHK") or shutil.which("viprchk")
        if needs_vipr
        else None
    )
    missing_tools = []
    if needs_sat_tools and drat_trim is None:
        missing_tools.append("drat-trim")
    if needs_sat_tools and lrat_check is None:
        missing_tools.append("lrat-check")
    if needs_vipr and viprchk is None:
        missing_tools.append("viprchk")
    if missing_tools:
        print(f"required replay tools not found: {', '.join(missing_tools)}")
        return 2
    reports = []
    for case in cases:
        formula = ROOT / case["formula"]["file"]
        if case["strategy"] == "scip_vipr_orbit_cover":
            report = _replay_vipr_case(case, viprchk, args.workers)
            if not report["verified"]:
                print(json.dumps({"status": "REJECTED", "case": report}, indent=2))
                return 1
            reports.append(report)
            continue
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
        "complete_manifest_replay": len(reports) == len(manifest["profiles"]),
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
