#!/usr/bin/env python3
"""Verify the 2026-07-05 frontier extension: the fifth closure Z(11,19,3,3)=106,
two new elementary upper bounds Z(12,23,3,3)<=135 and Z(13,23,3,3)<=144, and the
propagated bound table in analysis/new_bounds.json.

Standard library only.  Usage:
    python3 scripts/check_new_bounds.py --check    # verify everything
    python3 scripts/check_new_bounds.py --write    # regenerate analysis/new_bounds.json
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WITNESS = ROOT / "data" / "z11_19_106_matrix.csv"
TABLE = ROOT / "analysis" / "new_bounds.json"

C = math.comb


# ---------------------------------------------------------------- witness ----

def check_witness() -> dict:
    """Exhaustively verify the 11x19 lower-bound witness for Z(11,19,3,3)>=106."""
    rows = [[int(x) for x in r] for r in csv.reader(WITNESS.open())]
    assert len(rows) == 11 and all(len(r) == 19 for r in rows), "shape must be 11x19"
    assert all(x in (0, 1) for r in rows for x in r), "entries must be 0/1"
    ones = sum(map(sum, rows))
    assert ones == 106, f"expected 106 ones, found {ones}"
    checked = 0
    for cols in itertools.combinations(range(19), 3):
        full = 0
        for r in rows:
            if r[cols[0]] and r[cols[1]] and r[cols[2]]:
                full += 1
                assert full <= 2, f"all-one 3x3 submatrix at columns {cols}"
        checked += 1
    assert checked == C(19, 3)
    return {
        "file": "data/z11_19_106_matrix.csv",
        "ones": ones,
        "column_triples_checked": checked,
        "sha256": hashlib.sha256(WITNESS.read_bytes()).hexdigest(),
    }


# ------------------------------------------------- upper bound Z(11,19) ------

def check_deletion_chain() -> dict:
    """Z(11,18)=101 (Tan 2022, reproduced in Bhan--Nobili--Langer Figure 2) implies
    Z(11,19,3,3) <= floor(19*101/18) = 106: an 11x19 matrix with e ones has a
    column with at most floor(e/19) ones; deleting it leaves at least
    e - floor(e/19) <= Z(11,18) ones.  e = 107 gives 107 - 5 = 102 > 101."""
    assert 19 * 101 // 18 == 106
    assert 107 - (107 // 19) == 102 and 102 > 101
    assert 106 - (106 // 19) == 101 and 101 <= 101
    return {"deletion_bound": "Z(11,19)<=106", "source_value": "Z(11,18)=101"}


# ------------------------------------------- profile enumeration helpers -----

def degree_profiles(m: int, n: int, total: int):
    """All multisets of column degrees (0..m), n columns, sum = total, satisfying
    the Roman row-triple capacity sum C(d,3) <= 2*C(m,3)."""
    cap = 2 * C(m, 3)
    out = []

    def rec(d, ncols, tot, used, cur):
        if ncols == 0:
            if tot == total:
                out.append(dict(cur))
            return
        if tot + m * ncols < total or tot > total:
            return
        if d > m:
            return
        for k in range(ncols + 1):
            t2, u2 = tot + k * d, used + k * C(d, 3)
            if t2 > total or u2 > cap:
                break
            if k:
                cur[d] = k
            rec(d + 1, ncols - k, t2, u2, cur)
            if k:
                del cur[d]

    rec(0, n, 0, 0, {})
    return out


# --------------------------------------------- theorem: Z(12,23) <= 135 ------

def check_z12_23_upper() -> dict:
    """A 12x23 K33-free matrix cannot have 136 ones.

    Step 1 (classification): C(d,3) >= 10d - 40 with equality exactly at d=5,6,
    so 2*C(12,3) = 440 >= sum C(d_j,3) >= 10*136 - 40*23 = 440 forces every
    degree into {5,6}, every row triple covered exactly twice, and the unique
    profile 5^2 6^21.

    Step 2 (pair count): for each of the C(12,2)=66 row pairs P, summing
    lambda_T = 2 over the 10 triples T containing P gives
    sum_{j: P in E_j} (d_j - 2) = 20, i.e. 3*a_P + 4*b_P = 20 with a_P <= 2.
    Modulo 4 this forces a_P = 0 for every pair.  But the two degree-5 columns
    contain 2*C(5,2) = 20 pairs in total, so sum_P a_P = 20.  Contradiction."""
    # Step 1 -- the penalty line and exhaustive classification.
    for d in range(0, 13):
        gap = C(d, 3) - (10 * d - 40)
        assert gap >= 0 and (gap == 0) == (d in (5, 6))
    assert 10 * 136 - 40 * 23 == 2 * C(12, 3) == 440
    profiles = degree_profiles(12, 23, 136)
    assert profiles == [{5: 2, 6: 21}], f"unexpected profiles {profiles}"
    # Step 2 -- no solution of 3a+4b=20 with 0<=a<=2 has a>0.
    solutions = [(a, b) for a in range(0, 3) for b in range(0, 6)
                 if 3 * a + 4 * b == 20]
    assert solutions == [(0, 5)], solutions
    total_pair_incidences_deg5 = 2 * C(5, 2)
    assert total_pair_incidences_deg5 == 20 != 0
    return {"theorem": "Z(12,23,3,3)<=135", "unique_profile_at_136": "5^2 6^21",
            "pair_equation_solutions": solutions}


# --------------------------------------------- theorem: Z(13,23) <= 144 ------

def check_z13_23_upper() -> dict:
    """A 13x23 K33-free matrix cannot have 145 ones.

    Classification: C(d,3) >= 15d - 70 with equality exactly at d=6,7; the
    excess at d=5 is 5 and at d=8 is 6, and 2*C(13,3) - (15*145 - 70*23) = 7,
    so at most one exceptional degree (5 or 8) can occur.  Exactly three
    profiles survive: 6^16 7^7 (slack 7), 5^1 6^14 7^8 (slack 2), and
    8^1 6^17 7^5 (slack 1).

    Marked-row residues: the deficit of row r is
    D_r = 2*C(12,2) - sum_{j: r in E_j} C(d_j - 1, 2) >= 0 and
    sum_r D_r = 3 * slack.  Contributions are 6, 10, 15, 21 for degrees
    5, 6, 7, 8.  Modulo 5, degree-6 and degree-7 columns contribute 0, and
    132 = 2*C(12,2) is congruent to 2, so a row in no exceptional column has
    D_r >= 2.  Counting such rows kills each profile:
      6^16 7^7:      all 13 rows give >= 26 > 21;
      5^1 6^14 7^8:  the >= 8 rows outside the degree-5 column give >= 16 > 6;
      8^1 6^17 7^5:  the >= 5 rows outside the degree-8 column give >= 10 > 3."""
    for d in range(0, 14):
        gap = C(d, 3) - (15 * d - 70)
        assert gap >= 0 and (gap == 0) == (d in (6, 7))
    assert 2 * C(13, 3) - (15 * 145 - 70 * 23) == 7
    profiles = degree_profiles(13, 23, 145)
    expect = [{6: 16, 7: 7}, {5: 1, 6: 14, 7: 8}, {6: 17, 7: 5, 8: 1}]
    assert sorted(map(sorted, (p.items() for p in profiles))) == \
        sorted(map(sorted, (p.items() for p in expect))), profiles
    assert 2 * C(12, 2) == 132 and 132 % 5 == 2
    for d, contrib in ((6, 10), (7, 15)):
        assert C(d - 1, 2) == contrib and contrib % 5 == 0
    kills = {}
    for prof in profiles:
        slack = 2 * C(13, 3) - sum(k * C(d, 3) for d, k in prof.items())
        exceptional = sum(k for d, k in prof.items() if d in (5, 8))
        rows_in_exceptional = sum(d * k for d, k in prof.items() if d in (5, 8))
        clean_rows = 13 - rows_in_exceptional
        assert exceptional <= 1
        # every clean row has D_r ≡ 2 (mod 5), hence D_r >= 2
        lower = 2 * clean_rows
        assert lower > 3 * slack, (prof, lower, slack)
        kills[str(prof)] = {"slack": slack, "clean_rows": clean_rows,
                            "forced_sum": lower, "budget": 3 * slack}
    return {"theorem": "Z(13,23,3,3)<=144", "profiles_at_145": kills}


# --------------------------------------------------- propagated table --------

ESTABLISHED = {
    # Bhan--Nobili--Langer Figure 2 "previously established" cells (values from
    # Tan 2022, arXiv:2203.02283, Table 3).
    (8, 16): 70, (8, 17): 74, (8, 18): 77, (8, 19): 81, (8, 20): 84,
    (8, 21): 87, (8, 22): 90, (8, 23): 94,
    (9, 16): 77, (9, 17): 81, (9, 18): 85, (9, 19): 89, (9, 20): 93,
    (9, 21): 96, (9, 22): 100,
    (10, 16): 85, (10, 17): 90, (10, 18): 94, (10, 19): 98, (10, 20): 102,
    (11, 16): 92, (11, 17): 96, (11, 18): 101,
    (12, 16): 99, (13, 16): 107, (14, 16): 115, (15, 16): 123, (16, 16): 128,
}
CLOSED = {
    # this repository (docs/PROOF.md, docs/EXTENDED_RESULTS.md)
    (9, 23): 103, (10, 21): 106, (10, 22): 110, (11, 20): 111,
    # Bhan--Nobili--Langer
    (11, 21): 116, (11, 22): 121, (12, 22): 132,
    # this extension (docs/NEW_BOUNDS.md)
    (11, 19): 106,
}
BNL_OPEN = {
    (10, 23): (112, 115), (11, 23): (118, 125),
    (12, 17): (102, 108), (12, 18): (108, 113), (12, 19): (110, 118),
    (12, 20): (113, 122), (12, 21): (116, 127), (12, 23): (125, 136),
    (13, 17): (106, 116), (13, 18): (115, 121), (13, 19): (114, 125),
    (13, 20): (119, 130), (13, 21): (127, 135), (13, 22): (137, 140),
    (13, 23): (135, 145),
    (14, 17): (118, 124), (14, 18): (124, 129), (14, 19): (121, 135),
    (14, 20): (125, 140), (14, 21): (131, 145), (14, 22): (137, 150),
    (14, 23): (138, 155),
    (15, 17): (125, 132), (15, 18): (132, 138), (15, 19): (132, 143),
    (15, 20): (138, 149), (15, 21): (139, 154), (15, 22): (143, 160),
    (15, 23): (149, 165),
    (16, 17): (128, 141), (16, 18): (130, 146), (16, 19): (132, 152),
    (16, 20): (146, 158), (16, 21): (147, 164), (16, 22): (149, 169),
    (16, 23): (158, 175),
}
THEOREM_UPPER = {(12, 23): 135, (13, 23): 144}


def build_table() -> dict:
    cells = [(m, n) for m in range(8, 17) for n in range(16, 24)]
    U, L, usrc, lsrc = {}, {}, {}, {}
    for cell in cells:
        if cell in ESTABLISHED or cell in CLOSED:
            v = ESTABLISHED.get(cell, CLOSED.get(cell))
            U[cell] = L[cell] = v
            usrc[cell] = lsrc[cell] = ("established" if cell in ESTABLISHED
                                       else "closed")
        else:
            lo, hi = BNL_OPEN[cell]
            L[cell], U[cell] = lo, hi
            lsrc[cell] = "BNL2026"
            usrc[cell] = "literature"
    for cell, v in THEOREM_UPPER.items():
        if v < U[cell]:
            U[cell] = v
            usrc[cell] = "deficit-theorem"
    changed = True
    while changed:
        changed = False
        for (m, n) in cells:
            if (m, n) in ESTABLISHED or (m, n) in CLOSED:
                continue
            if (m - 1, n) in U and m * U[(m - 1, n)] // (m - 1) < U[(m, n)]:
                U[(m, n)] = m * U[(m - 1, n)] // (m - 1)
                usrc[(m, n)] = f"deletion-from-({m-1},{n})"
                changed = True
            if (m, n - 1) in U and n * U[(m, n - 1)] // (n - 1) < U[(m, n)]:
                U[(m, n)] = n * U[(m, n - 1)] // (n - 1)
                usrc[(m, n)] = f"deletion-from-({m},{n-1})"
                changed = True
            for src in ((m - 1, n), (m, n - 1)):
                if src in L and L[src] + 2 > L[(m, n)]:
                    L[(m, n)] = L[src] + 2
                    lsrc[(m, n)] = f"two-one-line-extension-of-{src}"
                    changed = True
    table = {}
    for (m, n) in cells:
        table[f"{m},{n}"] = {
            "lower": L[(m, n)], "upper": U[(m, n)],
            "lower_source": lsrc[(m, n)], "upper_source": usrc[(m, n)],
        }
    return {
        "generated_by": "scripts/check_new_bounds.py --write",
        "scope": "Z(m,n,3,3) for 8<=m<=16, 16<=n<=23",
        "notes": [
            "Every lower bound is an explicit construction from the cited source, "
            "extended monotonically (a new row or column with two ones never "
            "creates K33).",
            "Every upper bound is the literature value, the deficit theorems of "
            "docs/NEW_BOUNDS.md, or a floor(k/(k-1) * bound) deletion propagation.",
            "Solver verdicts are intentionally excluded from this table.",
        ],
        "cells": table,
    }


def run(check_only: bool) -> int:
    report = {
        "witness": check_witness(),
        "deletion_chain": check_deletion_chain(),
        "z12_23": check_z12_23_upper(),
        "z13_23": check_z13_23_upper(),
    }
    table = build_table()
    # closure consistency: the new exact value must agree with the table
    cell = table["cells"]["11,19"]
    assert cell["lower"] == cell["upper"] == 106, cell
    if check_only:
        stored = json.loads(TABLE.read_text())
        if stored != table:
            print("MISMATCH: analysis/new_bounds.json is stale", file=sys.stderr)
            return 1
        report["table"] = {"status": "IDENTICAL", "cells": len(table["cells"])}
    else:
        TABLE.write_text(json.dumps(table, indent=1, sort_keys=True) + "\n")
        report["table"] = {"status": "WRITTEN", "cells": len(table["cells"])}
    report["status"] = "VERIFIED"
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(run(check_only=args.check))
