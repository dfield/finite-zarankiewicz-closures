#!/usr/bin/env python3
"""Deeply verify the complete local integrity layer for ``Z(10,23)=112``."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from finite_zarankiewicz_closures.sat_certificate import (  # noqa: E402
    load_and_verify_z10_23_sat_manifest,
)


def main() -> int:
    report = load_and_verify_z10_23_sat_manifest(ROOT)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
