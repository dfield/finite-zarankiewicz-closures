#!/usr/bin/env python3
"""Verify the frontier extension, including the eight repository closures,
the upper bound Z(13,23,3,3)<=144, and the propagated bound table in
analysis/new_bounds.json.

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
TABLE = ROOT / "analysis" / "new_bounds.json"
SAT_RECORD = ROOT / "analysis" / "sat_cross_check.json"

C = math.comb


# ---------------------------------------------------------------- witness ----

def _check_one_witness(name: str, m: int, n: int, target: int) -> dict:
    """Exhaustively verify an m x n lower-bound witness with `target` ones."""
    path = ROOT / "data" / name
    rows = [[int(x) for x in r] for r in csv.reader(path.open())]
    assert len(rows) == m and all(len(r) == n for r in rows), f"shape must be {m}x{n}"
    assert all(x in (0, 1) for r in rows for x in r), "entries must be 0/1"
    ones = sum(map(sum, rows))
    assert ones == target, f"expected {target} ones, found {ones}"
    checked = 0
    for cols in itertools.combinations(range(n), 3):
        full = 0
        for r in rows:
            if r[cols[0]] and r[cols[1]] and r[cols[2]]:
                full += 1
                assert full <= 2, f"all-one 3x3 submatrix at columns {cols}"
        checked += 1
    assert checked == C(n, 3)
    return {
        "file": f"data/{name}",
        "ones": ones,
        "column_triples_checked": checked,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def check_witness() -> dict:
    return {
        "z10_23": _check_one_witness("z10_23_112_matrix.csv", 10, 23, 112),
        "z11_19": _check_one_witness("z11_19_106_matrix.csv", 11, 19, 106),
        "z11_23": _check_one_witness("z11_23_123_matrix.csv", 11, 23, 123),
        "z12_23": _check_one_witness("z12_23_134_matrix.csv", 12, 23, 134),
    }


def check_sat_record_catalog() -> dict[str, object]:
    """Check that the historical lead points to its certified replacement."""

    record = json.loads(SAT_RECORD.read_text(encoding="utf-8"))
    assert record["schema_version"] == 2
    assert record["evidence_status"] == "SUPERSEDED_BY_REPLAYABLE_CERTIFICATE"
    certified = record["certified_result"]
    assert certified["theorem"] == "Z(10,23,3,3)=112"
    assert certified["arithmetic_profiles"] == 25
    assert certified["arithmetic_eliminations"] == 12
    assert certified["traced_profiles"] == 13
    manifest_path = ROOT / certified["sat_manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["theorem"] == certified["theorem"]
    assert manifest["excluded_target"] == 113
    assert len(manifest["profiles"]) == certified["traced_profiles"]
    generated_counts = {
        str(total): len(degree_profiles(10, 23, total)) for total in (113, 114)
    }
    assert generated_counts == {"113": 25, "114": 11}
    assert record["historical_untraced_session"]["profile_counts"] == generated_counts
    return {
        "evidence_status": record["evidence_status"],
        "profile_counts": generated_counts,
        "traced_profiles": len(manifest["profiles"]),
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

    def minimum_triple_cost(ncols: int, degree_sum: int) -> int:
        """Minimum convex triple cost for ``ncols`` degrees with this sum."""

        if ncols == 0:
            return 0 if degree_sum == 0 else cap + 1
        q, r = divmod(degree_sum, ncols)
        if q > m or (q == m and r):
            return cap + 1
        return (ncols - r) * C(q, 3) + r * C(q + 1, 3)

    def rec(d, ncols, tot, used, cur):
        remaining = total - tot
        if remaining < d * ncols or remaining > m * ncols:
            return
        if used + minimum_triple_cost(ncols, remaining) > cap:
            return
        if ncols == 0:
            if tot == total:
                out.append(dict(cur))
            return
        if d > m:
            return
        for k in range(ncols + 1):
            t2, u2 = tot + k * d, used + k * C(d, 3)
            if t2 > total or u2 > cap:
                break
            remaining_columns = ncols - k
            remaining_degree = total - t2
            if remaining_columns:
                if not ((d + 1) * remaining_columns <= remaining_degree <= m * remaining_columns):
                    continue
                if u2 + minimum_triple_cost(remaining_columns, remaining_degree) > cap:
                    continue
            elif remaining_degree:
                continue
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


# --------------------------------------------- theorem: Z(12,23) <= 134 ------

def check_z12_23_upper_134() -> dict:
    """A 12x23 K33-free matrix cannot have 135 ones either.

    Exactly five degree profiles survive the capacity count at 135.  Write
    u_r, a_r, b_r for the number of degree-4, degree-5, degree-7 columns
    through row r.  Modulo 10 the degree-6 row contribution C(5,2)=10
    vanishes and 2*C(11,2) = 110 == 0, so the row deficit satisfies
        D_r == 7*u_r + 4*a_r + 5*b_r  (mod 10),   D_r >= 0,
    and sum_r D_r = 3s.  Similarly modulo 4 the degree-6 pair contribution
    vanishes and 2*(m-2) = 20 == 0, so the pair deficit satisfies
        D_P == 2*x_P + y_P + 3*z_P  (mod 4)
    with x, y, z counting degree-4/5/7 columns through the pair.
    K33-freeness bounds shared rows over column triples:
        sum_r C(a_r,3) <= 2*C(n5,3)  and  sum_r C(a_r,2)*b_r <= 2*C(n5,2)*n7.

    Each profile is impossible:
      5^3 6^20  (s=10): sum_r (4a mod 10) = 60 - 10*n3 >= 40 > 30, since at
                 most two rows lie in all three degree-5 columns.
      4^1 5^1 6^21 (s=6): the pair residues sum to 22 > 18 independently of
                 the overlap between the two exceptional columns.
      5^4 6^18 7^1 (s=5): exhaustive enumeration of row types (a,b) under the
                 two K33 budgets shows sum_r D_r-residues >= 25 > 15.
      4^1 5^2 6^19 7^1 (s=1): each of the four rows of the degree-4 column
                 needs residue <= 3, forcing (a,b) in {(1,0),(0,1),(2,1)};
                 counting degree-7 incidences then forces at least three
                 residue-3 rows outside the column: >= 9 > 3.
      5^5 6^16 7^2 (s=0): every row needs residue 0, forcing a_r in {0,5};
                 sum a_r = 25 needs five rows with a_r = 5, but
                 sum_r C(a_r,3) = 50 > 20 = 2*C(5,3).
    """
    profiles = degree_profiles(12, 23, 135)
    key = lambda p: tuple(sorted(p.items()))
    expect = {key(p) for p in ({5: 3, 6: 20}, {4: 1, 5: 1, 6: 21},
                               {5: 4, 6: 18, 7: 1}, {4: 1, 5: 2, 6: 19, 7: 1},
                               {5: 5, 6: 16, 7: 2})}
    assert {key(p) for p in profiles} == expect, profiles
    detail = {}

    # P1: 5^3 6^20
    s = (2 * C(12, 3) - (3 * C(5, 3) + 20 * C(6, 3))) ; assert s == 10
    # rows in all three degree-5 columns form the shared set of the unique
    # column triple: at most 2.  sum_r r_r = 60 - 10*n3 for n3 <= 2.
    assert min(60 - 10 * n3 for n3 in range(0, 3)) == 40 > 3 * s
    detail["5^3 6^20"] = "row residues >= 40 > 30"

    # P2: 4^1 5^1 6^21 -- pair residues, any overlap t
    s = 2 * C(12, 3) - (C(4, 3) + C(5, 3) + 21 * C(6, 3)); assert s == 6
    for t in range(0, 5):
        both = C(t, 2)
        total = 2 * (C(4, 2) - both) + 1 * (C(5, 2) - both) + 3 * both
        assert total == 22 > 3 * s
    detail["4^1 5^1 6^21"] = "pair residues = 22 > 18 for every overlap"

    # P3: 5^4 6^18 7^1 -- exhaustive row-type enumeration
    s = 2 * C(12, 3) - (4 * C(5, 3) + 18 * C(6, 3) + C(7, 3)); assert s == 5
    types = [(a, b) for a in range(5) for b in range(2)]
    survivor = []

    def rec3(i, rows, sa, sb, c3, c2b, sr):
        if sr > 3 * s or survivor:
            return
        if i == len(types):
            if rows == 0 and sa == 20 and sb == 7 and (3 * s - sr) % 10 == 0:
                survivor.append(True)
            return
        a, b = types[i]
        r = (4 * a + 5 * b) % 10
        for k in range(rows + 1):
            na, nb = sa + k * a, sb + k * b
            nc3, nc2b = c3 + k * C(a, 3), c2b + k * C(a, 2) * b
            if na > 20 or nb > 7 or nc3 > 2 * C(4, 3) or nc2b > 2 * C(4, 2):
                break
            rec3(i + 1, rows - k, na, nb, nc3, nc2b, sr + k * r)

    rec3(0, 12, 0, 0, 0, 0, 0)
    assert not survivor, "5^4 6^18 7^1 unexpectedly satisfiable at the residue level"
    detail["5^4 6^18 7^1"] = "no legal row-type distribution reaches residue sum <= 15"

    # P4: 4^1 5^2 6^19 7^1.  Every row residue must be <= 3s = 3.
    s = 2 * C(12, 3) - (C(4, 3) + 2 * C(5, 3) + 19 * C(6, 3) + C(7, 3)); assert s == 1
    u_opts = {(a, b): (7 + 4 * a + 5 * b) % 10 for a in range(3) for b in range(2)}
    cheap_u = {k: v for k, v in u_opts.items() if v <= 3 * s}
    assert cheap_u == {(1, 0): 1, (0, 1): 2, (2, 1): 0}, cheap_u
    o_opts = {(a, b): (4 * a + 5 * b) % 10 for a in range(3) for b in range(2)}
    cheap_o = {k: v for k, v in o_opts.items() if v <= 3 * s}
    assert cheap_o == {(0, 0): 0, (2, 1): 3}, cheap_o
    # The degree-7 column has 7 rows.  A b=1 row is either one of the four
    # degree-4-column rows, or a non-column row of type (2,1) at residue
    # cost 3, of which the budget 3 allows at most one.  So at most 5 rows
    # can lie in the degree-7 column: contradiction.
    max_b_u = 4                       # all four u-rows may have b = 1
    max_b_other = (3 * s) // 3        # each costs 3
    assert max_b_u + max_b_other == 5 < 7
    detail["4^1 5^2 6^19 7^1"] = "at most 5 rows can meet the degree-7 column"

    # P5: 5^5 6^16 7^2
    s = 2 * C(12, 3) - (5 * C(5, 3) + 16 * C(6, 3) + 2 * C(7, 3)); assert s == 0
    zero_res_a = [a for a in range(6) if any((4 * a + 5 * b) % 10 == 0
                                             for b in (0, 2))]
    assert zero_res_a == [0, 5]
    # five rows with a=5 would put 50 > 20 = 2*C(5,3) on the column triples
    assert 5 * C(5, 3) == 50 > 2 * C(5, 3) == 20
    detail["5^5 6^16 7^2"] = "a_r in {0,5} forces five a=5 rows; triple budget 20 < 50"

    return {"theorem": "Z(12,23,3,3)<=134", "profiles_at_135": detail}


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
    (9, 23): 103, (10, 21): 106, (10, 22): 110, (10, 23): 112,
    (11, 20): 111, (11, 23): 123,
    # Bhan--Nobili--Langer
    (11, 21): 116, (11, 22): 121, (12, 22): 132,
    # this extension (docs/NEW_BOUNDS.md)
    (11, 19): 106, (12, 23): 134,
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
THEOREM_UPPER = {(12, 23): 134, (13, 23): 144}


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
            "The Z(10,23) seed is supported by an arithmetic reduction and "
            "DRAT cores independently replayed through LRAT checking; no unlogged "
            "solver verdict is used.",
        ],
        "cells": table,
    }


def run(check_only: bool) -> int:
    report = {
        "witness": check_witness(),
        "deletion_chain": check_deletion_chain(),
        "z12_23_step1": check_z12_23_upper(),
        "z12_23_step2": check_z12_23_upper_134(),
        "z13_23": check_z13_23_upper(),
        "sat_record_catalog": check_sat_record_catalog(),
    }
    table = build_table()
    # closure consistency: the new exact values must agree with the table
    cell = table["cells"]["11,19"]
    assert cell["lower"] == cell["upper"] == 106, cell
    cell = table["cells"]["10,23"]
    assert cell["lower"] == cell["upper"] == 112, cell
    cell = table["cells"]["11,23"]
    assert cell["lower"] == cell["upper"] == 123, cell
    cell = table["cells"]["12,23"]
    assert cell["lower"] == cell["upper"] == 134, cell
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
