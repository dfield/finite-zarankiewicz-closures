#!/usr/bin/env python3
"""Check the JSON mirror of the proof's exact arithmetic."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.certificate import (  # noqa: E402
    CertificateError,
    verify_certificate,
)


def main() -> int:
    path = ROOT / "certificates" / "degree_deficit.json"
    raw = path.read_bytes()
    try:
        certificate = json.loads(raw)
        report = verify_certificate(certificate)
    except (OSError, UnicodeError, json.JSONDecodeError, CertificateError) as error:
        print(json.dumps({"status": "REJECTED", "error": str(error)}, indent=2))
        return 1
    report["certificate_sha256"] = hashlib.sha256(raw).hexdigest()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
