#!/usr/bin/env python3
"""Generate or byte-check the six established exact-value certificates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.case_certificates import (  # noqa: E402
    CASE_SPECS,
    rendered_case_certificates,
    verify_case_certificate,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = rendered_case_certificates(ROOT)
    reports = []
    for case in CASE_SPECS:
        destination = ROOT / "certificates" / f"{case.slug}.json"
        if args.check:
            if (
                not destination.exists()
                or destination.read_text(encoding="utf-8") != rendered[case.slug]
            ):
                print(json.dumps({"status": "MISMATCH", "artifact": str(destination)}, indent=2))
                return 1
        else:
            destination.write_text(rendered[case.slug], encoding="utf-8")
        certificate = json.loads(rendered[case.slug])
        reports.append(verify_case_certificate(certificate, ROOT))
    print(json.dumps({"status": "VERIFIED", "cases": reports}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
