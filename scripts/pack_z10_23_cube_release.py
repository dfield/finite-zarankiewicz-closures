#!/usr/bin/env python3
"""Pack finalized Z(10,23) cube proofs into hash-bound release assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tarfile
import threading


PART_BYTES = 1_800_000_000
RELEASE = {
    "repository": "dfield/finite-zarankiewicz-closures",
    "tag": "z10-23-certificate-v1",
}


def pack(
    slug: str,
    work: Path,
    threads: int = 8,
    preset: str = "-3",
    part_bytes: int = PART_BYTES,
) -> dict[str, object]:
    metadata = json.loads((work / "metadata.json").read_text(encoding="ascii"))
    if metadata.get("status") != "VERIFIED_CUBE_LEAF_PROOFS":
        raise RuntimeError("finalized proof metadata is missing")
    proof_metadata = metadata.get("proofs")
    proof_count = proof_metadata.get("count") if isinstance(proof_metadata, dict) else None
    if not isinstance(proof_count, int) or proof_count <= 0:
        raise RuntimeError("finalized proof count is missing")
    if threads <= 0 or not 0 < part_bytes < 2_000_000_000:
        raise ValueError("invalid archive resource setting")

    archive = work / f"{slug}.cube-proofs.tar.xz"
    archive.unlink(missing_ok=True)
    for stale in work.glob(f"{archive.name}.part-*"):
        stale.unlink()

    xz = subprocess.Popen(
        ["xz", f"-T{threads}", preset, "-c"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if xz.stdin is None or xz.stdout is None or xz.stderr is None:
        raise RuntimeError("failed to open xz stream")

    parts: list[dict[str, object]] = []
    stream_digest = hashlib.sha256()
    stream_bytes = 0
    drain_errors: list[BaseException] = []

    def drain_parts() -> None:
        nonlocal stream_bytes
        part_index = 0
        destination = None
        destination_path = None
        part_digest = hashlib.sha256()
        part_size = 0
        try:
            while block := xz.stdout.read(8 * 1024 * 1024):
                stream_digest.update(block)
                stream_bytes += len(block)
                offset = 0
                while offset < len(block):
                    if destination is None:
                        destination_path = work / (
                            f"{archive.name}.part-{part_index:02d}"
                        )
                        destination = destination_path.open("wb")
                        part_digest = hashlib.sha256()
                        part_size = 0
                    count = min(part_bytes - part_size, len(block) - offset)
                    chunk = block[offset : offset + count]
                    destination.write(chunk)
                    part_digest.update(chunk)
                    part_size += count
                    offset += count
                    if part_size == part_bytes:
                        destination.close()
                        parts.append(
                            {
                                "name": destination_path.name,
                                "bytes": part_size,
                                "sha256": part_digest.hexdigest(),
                            }
                        )
                        destination = None
                        part_index += 1
            if destination is not None:
                destination.close()
                parts.append(
                    {
                        "name": destination_path.name,
                        "bytes": part_size,
                        "sha256": part_digest.hexdigest(),
                    }
                )
        except BaseException as error:
            drain_errors.append(error)
            if destination is not None:
                destination.close()
            xz.stdout.close()

    drainer = threading.Thread(target=drain_parts, name="cube-archive-splitter")
    drainer.start()
    tar_error = None
    try:
        with tarfile.open(
            fileobj=xz.stdin,
            mode="w|",
            format=tarfile.PAX_FORMAT,
        ) as tar:
            for index in range(proof_count):
                path = work / "proofs" / f"leaf-{index:08d}.drat"
                if not path.is_file():
                    raise RuntimeError(f"missing finalized proof leaf {index}")
                info = tarfile.TarInfo(f"proofs/{path.name}")
                info.size = path.stat().st_size
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                with path.open("rb") as handle:
                    tar.addfile(info, handle)
    except BaseException as error:
        tar_error = error
    finally:
        try:
            xz.stdin.close()
        except BrokenPipeError as error:
            if tar_error is None:
                tar_error = error
    xz_errors = xz.stderr.read()
    xz.stderr.close()
    returncode = xz.wait()
    drainer.join()
    xz.stdout.close()
    if drain_errors:
        raise RuntimeError("archive splitter failed") from drain_errors[0]
    if tar_error is not None:
        raise RuntimeError("archive construction failed") from tar_error
    if returncode != 0:
        raise RuntimeError(
            f"archive compression failed: xz={returncode}\n"
            + xz_errors.decode(errors="replace")[-2000:]
        )
    if not parts or sum(int(part["bytes"]) for part in parts) != stream_bytes:
        raise RuntimeError("archive splitter produced an incomplete stream")

    tester = subprocess.Popen(
        ["xz", f"-T{threads}", "-t"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    if tester.stdin is None or tester.stderr is None:
        raise RuntimeError("failed to open xz integrity check")
    for part in parts:
        with (work / str(part["name"])).open("rb") as source:
            shutil.copyfileobj(source, tester.stdin, length=8 * 1024 * 1024)
    tester.stdin.close()
    tester_errors = tester.stderr.read()
    tester.stderr.close()
    tester_returncode = tester.wait()
    if tester_returncode != 0:
        raise RuntimeError(
            f"archive integrity check failed: xz={tester_returncode}\n"
            + tester_errors.decode(errors="replace")[-2000:]
        )

    release_metadata = {
        "format": "TAR+DRAT+xz+github-release-parts",
        "compression": {
            "archive": "deterministic PAX tar",
            "xz_options": [f"-T{threads}", preset],
            "xz_version": subprocess.run(
                ["xz", "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            ).stdout.splitlines()[0],
        },
        "release": RELEASE,
        "parts": parts,
        "bytes": stream_bytes,
        "sha256": stream_digest.hexdigest(),
    }
    sidecar = work / f"{slug}.cube-proofs.release.json"
    sidecar.write_text(
        json.dumps(release_metadata, indent=2, sort_keys=True) + "\n",
        encoding="ascii",
    )
    return release_metadata


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug")
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--preset", default="-3")
    parser.add_argument("--part-bytes", type=int, default=PART_BYTES)
    args = parser.parse_args()
    result = pack(
        args.slug,
        args.work.resolve(),
        args.threads,
        args.preset,
        args.part_bytes,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
