#!/usr/bin/env python3
"""Tier-2 deficit filter: configuration-level residue analysis for profiles with a
small set of 'exceptional' columns over a uniform-residue base.

For a profile with exceptional columns of degrees (e_1..e_k) (k small) and base
degrees whose row-weights C(d-1,2) (resp. pair-weights d-2) are all divisible by
g_row (resp. g_pair):

  Enumerate multisets of row membership patterns A subset [k] (how each of the m
  rows meets the exceptional columns), subject to:
    - column sizes: #(rows with i in A) = e_i,
    - K33 legality among exceptional columns: any 3 of them share <= 2 rows,
      and any pattern multiset where 3+ rows share 3+ common columns is illegal.
  For each configuration:
    row residues  r_r = (2*C(m-1,2) - sum_{i in A_r} C(e_i - 1, 2)) mod g_row
    pair residues r_P = (2*(m-2)   - sum_{i in A_a & A_b} ... ) computed from
                  common membership of the two rows, mod g_pair
  Since all base contributions vanish mod g, D_r == r_r (mod g_row) with D_r>=0,
  so sum_r D_r = 3s forces  sum_r r_r <= 3s  and  sum_r r_r == 3s (mod g_row);
  similarly for pairs. If NO legal configuration satisfies all four conditions,
  the profile is impossible.  (Necessary conditions only: a surviving
  configuration proves nothing.)
"""
import math
from itertools import combinations

C = math.comb

def tier2_profile_dead(m, n, T, counts, max_k=5, verbose=False):
    cap3 = 2 * C(m, 3)
    used = sum(nd * C(d, 3) for d, nd in counts.items())
    if used > cap3:
        return True
    s = cap3 - used
    # exceptional = degrees with smallest multiplicities until k <= max_k,
    # base = the rest; require base weights share a residue class
    items = sorted(counts.items(), key=lambda kv: kv[1])
    exc = []
    base = dict(counts)
    for d, nd in items:
        if sum(kv for kv in base.values()) - nd >= 1 and len(exc) + nd <= max_k and nd < base.get(d, 0) + 1:
            # tentatively move all nd columns of degree d to exceptional
            if len(exc) + nd <= max_k:
                exc += [d] * nd
                del base[d]
    if not base or len(exc) == 0 or len(exc) > max_k:
        return False
    def gcds(vals):
        g = 0
        for v in vals: g = math.gcd(g, v)
        return g
    g_row = gcds([C(d - 1, 2) for d in base])
    g_pair = gcds([d - 2 for d in base])
    if g_row <= 1 and g_pair <= 1:
        return False
    k = len(exc)
    cap_row = 2 * C(m - 1, 2)
    cap_pair = 2 * (m - 2)
    w_row = [C(d - 1, 2) for d in exc]
    w_pair = [d - 2 for d in exc]
    patterns = []
    for mask in range(1 << k):
        patterns.append(mask)
    # residues per pattern
    def rrow(mask):
        e = sum(w_row[i] for i in range(k) if mask >> i & 1)
        return (cap_row - e) % g_row if g_row > 1 else 0
    RR = [rrow(msk) for msk in patterns]
    # DFS over pattern counts
    target_sizes = exc
    found_ok = [False]

    def pair_sum_ok(countvec):
        if g_pair <= 1:
            return True
        tot = 0
        pats = [p for p in range(1 << k) if countvec[p]]
        for ai in range(len(pats)):
            A = pats[ai]
            xa = countvec[A]
            for bi in range(ai, len(pats)):
                B = pats[bi]
                xb = countvec[B]
                npairs = xa * (xa - 1) // 2 if A == B else xa * xb
                if not npairs:
                    continue
                common = A & B
                e = sum(w_pair[i] for i in range(k) if common >> i & 1)
                tot += npairs * ((cap_pair - e) % g_pair)
                if tot > 3 * s:
                    return False
        return tot <= 3 * s and (3 * s - tot) % g_pair == 0

    def legal_triples(countvec):
        # any 3 exceptional columns share at most 2 rows
        for t in combinations(range(k), 3):
            tm = (1 << t[0]) | (1 << t[1]) | (1 << t[2])
            shared = sum(c for p, c in enumerate(countvec) if p & tm == tm)
            if shared > 2:
                return False
        return True

    # enumerate counts of each pattern via DFS on patterns
    cnt = [0] * (1 << k)
    colneed = list(target_sizes)

    def dfs(pidx, rows_left, rowsum_res):
        if found_ok[0]:
            return
        if rowsum_res > 3 * s:
            return
        if pidx == (1 << k):
            if any(colneed):
                return
            if (3 * s - rowsum_res) % (g_row if g_row > 1 else 1) != 0 and g_row > 1:
                return
            if not legal_triples(cnt):
                return
            if not pair_sum_ok(cnt):
                return
            found_ok[0] = True
            return
        p = pidx
        maxc = rows_left
        for i in range(k):
            if p >> i & 1:
                maxc = min(maxc, colneed[i])
        for c in range(maxc, -1, -1):
            cnt[p] = c
            for i in range(k):
                if p >> i & 1:
                    colneed[i] -= c
            ok = all(v >= 0 for v in colneed)
            if ok:
                # prune: remaining patterns must be able to satisfy colneed
                dfs(pidx + 1, rows_left - c, rowsum_res + c * RR[p])
            cnt[p] = 0
            for i in range(k):
                if p >> i & 1:
                    colneed[i] += c
            if found_ok[0]:
                return

    # iterate patterns from full masks down doesn't matter; order 1..2^k-1 then 0
    # simpler: reorder patterns so mask 0 (rows outside all exceptional) is last
    order = [p for p in range(1, 1 << k)] + [0]
    cnt2 = [0] * (1 << k)

    def dfs2(oidx, rows_left, rowsum_res):
        if found_ok[0]:
            return
        if rowsum_res > 3 * s:
            return
        if oidx == len(order):
            if any(colneed) or rows_left != 0:
                return
            if g_row > 1 and (3 * s - rowsum_res) % g_row != 0:
                return
            if not legal_triples(cnt2):
                return
            if not pair_sum_ok(cnt2):
                return
            found_ok[0] = True
            return
        p = order[oidx]
        if p == 0:
            # remaining rows all get pattern 0
            if any(colneed):
                return
            dfs_c = rows_left
            cnt2[0] = dfs_c
            dfs2(oidx + 1, 0, rowsum_res + dfs_c * RR[0])
            cnt2[0] = 0
            return
        maxc = rows_left
        for i in range(k):
            if p >> i & 1:
                maxc = min(maxc, colneed[i])
        for c in range(maxc, -1, -1):
            cnt2[p] = c
            for i in range(k):
                if p >> i & 1:
                    colneed[i] -= c
            dfs2(oidx + 1, rows_left - c, rowsum_res + c * RR[p])
            cnt2[p] = 0
            for i in range(k):
                if p >> i & 1:
                    colneed[i] += c
            if found_ok[0]:
                return

    dfs2(0, m, 0)
    if verbose and not found_ok[0]:
        print(f"    tier2 kill: exc={exc} base={sorted(base)} g_row={g_row} g_pair={g_pair} s={s}")
    return not found_ok[0]

if __name__ == "__main__":
    import filters, sys
    for (m, n, T) in [(12, 23, 135), (10, 23, 113), (11, 23, 125), (12, 18, 110), (12, 17, 104)]:
        profs = [p for p in filters.all_profiles(m, n, T) if filters.profile_ok(m, n, T, p)]
        dead = 0
        for p in profs:
            if tier2_profile_dead(m, n, T, p, verbose=True):
                dead += 1
                print(f"  ({m},{n}) T={T}: profile {p} TIER2-KILLED")
        print(f"({m},{n}) T={T}: {len(profs)} tier1-surviving profiles, {dead} killed by tier2, {len(profs)-dead} remain")
