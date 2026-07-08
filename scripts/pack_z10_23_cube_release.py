#!/usr/bin/env python3
"""Pack finalized Z(10,23) cube proofs into hash-bound release assets."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile


PART_BYTES = 1_800_000_000
RELEASE = {
    "repository": "dfield/finite-zarankiewicz-closures",
    "tag": "z10-23-certificate-v1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
    if threads <= 0 or not 0 < part_bytes < 2_000_000_000:
        raise ValueError("invalid archive resource setting")

    archive = work / f"{slug}.cube-proofs.tar.xz"
    with archive.open("wb") as output:
        xz = subprocess.Popen(
            ["xz", f"-T{threads}", preset, "-c"],
            stdin=subprocess.PIPE,
            stdout=output,
            stderr=subprocess.PIPE,
        )
        if xz.stdin is None or xz.stderr is None:
            raise RuntimeError("failed to open xz stream")
        with tarfile.open(
            fileobj=xz.stdin,
            mode="w|",
            format=tarfile.PAX_FORMAT,
        ) as tar:
            for path in sorted((work / "proofs").glob("leaf-*.drat")):
                info = tarfile.TarInfo(f"proofs/{path.name}")
                info.size = path.stat().st_size
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                with path.open("rb") as handle:
                    tar.addfile(info, handle)
        xz.stdin.close()
        xz_errors = xz.stderr.read()
        xz.stderr.close()
        returncode = xz.wait()
    if returncode != 0:
        raise RuntimeError(
            f"archive compression failed: xz={returncode}\n"
            + xz_errors.decode(errors="replace")[-2000:]
        )
    subprocess.run(["xz", f"-T{threads}", "-t", str(archive)], check=True)

    total_bytes = archive.stat().st_size
    stream_sha256 = sha256(archive)
    for stale in work.glob(f"{archive.name}.part-*"):
        stale.unlink()
    parts = []
    with archive.open("rb") as source:
        part_index = 0
        while source.tell() < total_bytes:
            part = archive.with_name(f"{archive.name}.part-{part_index:02d}")
            remaining = part_bytes
            with part.open("wb") as destination:
                while remaining:
                    block = source.read(min(8 * 1024 * 1024, remaining))
                    if not block:
                        break
                    destination.write(block)
                    remaining -= len(block)
            parts.append(
                {
                    "name": part.name,
                    "bytes": part.stat().st_size,
                    "sha256": sha256(part),
                }
            )
            part_index += 1

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
        "bytes": total_bytes,
        "sha256": stream_sha256,
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
