#!/usr/bin/env python3
"""Arithmetic profile filters for K33-free matrices, generalizing the repository's
marked-row (9,23) and pair-deficit (10,22) mechanisms.

For an m x n matrix with T ones and column-degree multiset {n_d}:
  capacity slack s = 2*C(m,3) - sum n_d*C(d,3) must be >= 0            [Roman]
  row deficits:  D_r = 2*C(m-1,2) - sum_{j: r in E_j} C(d_j-1, 2) >= 0,
                 sum_r D_r = 3*s, hence every D_r in [0, 3s].
  pair deficits: D_P = 2*(m-2) - sum_{j: P subset E_j} (d_j - 2) >= 0,
                 sum_P D_P = 3*s, hence every D_P in [0, 3s].
Counting consistency: sum over rows of (# degree-d columns through the row) = n_d * d,
and sum over pairs of (# degree-d columns through the pair) = n_d * C(d,2).

A profile dies if the interval/count conditions cannot all hold. These are
NECESSARY conditions; surviving profiles remain candidates.
"""
import math
from functools import lru_cache


C = math.comb

def _reach(counts, weights, cap, skip=None):
    """Bitset of achievable sums k_d*w_d (0<=k_d<=n_d), truncated at cap."""
    mask = (1 << (cap + 1)) - 1
    R = 1
    for d, nd in counts.items():
        if d == skip:
            continue
        w = weights[d]
        if w == 0 or nd == 0:
            continue
        # add up to nd copies of weight w (binary splitting)
        left = nd
        step = 1
        while left > 0:
            take = min(step, left)
            shift = w * take
            R |= (R << shift) & mask
            left -= take
            step *= 2
    return R & mask

def _side_ok(m, counts, weights, cap, s, unit_counts, npoints):
    """Shared logic for the row (npoints=m, unit_counts[d]=n_d*d) and
    pair (npoints=C(m,2), unit_counts[d]=n_d*C(d,2)) filters.
    Uses subset-sum bitsets; exact and fast."""
    lo = max(0, cap - 3 * s)
    R = _reach(counts, weights, cap)
    W = R & (((1 << (cap - lo + 1)) - 1) << lo)
    if W == 0:
        return False
    hi_sum = W.bit_length() - 1           # max achievable sum in window
    lo_sum = (W & -W).bit_length() - 1    # min achievable sum in window
    min_def = cap - hi_sum
    max_def = cap - lo_sum
    if npoints * min_def > 3 * s:
        return False
    if npoints * max_def < 3 * s:
        return False
    # per-degree count consistency: k_d feasible values given others complete the window
    for d, nd in counts.items():
        w = weights[d]
        if w == 0:
            continue  # k_d unconstrained by the window
        Ro = _reach(counts, weights, cap, skip=d)
        kmin = None; kmax = None
        for k in range(nd + 1):
            base = k * w
            if base > cap:
                break
            # need some sum t of others with lo <= base + t <= cap
            l2 = max(0, lo - base); h2 = cap - base
            seg = (Ro >> l2) & ((1 << (h2 - l2 + 1)) - 1)
            if seg:
                if kmin is None: kmin = k
                kmax = k
        if kmin is None:
            return False
        if not (npoints * kmin <= unit_counts[d] <= npoints * kmax):
            return False
    return True

def profile_ok(m, n, T, counts):
    """counts: dict degree->multiplicity (degrees >= 0), sum d*n_d = T, sum n_d = n."""
    cap3 = 2 * C(m, 3)
    used = sum(nd * C(d, 3) for d, nd in counts.items())
    if used > cap3:
        return False
    s = cap3 - used
    # row filter (degrees >= 1 have row incidences)
    rc = {d: nd for d, nd in counts.items() if d >= 1 and nd > 0}
    if rc:
        wr = {d: C(d - 1, 2) for d in rc}
        ur = {d: rc[d] * d for d in rc}
        if not _side_ok(m, rc, wr, 2 * C(m - 1, 2), s, ur, m):
            return False
    # pair filter (degrees >= 2 contain pairs)
    pc = {d: nd for d, nd in counts.items() if d >= 2 and nd > 0}
    if pc:
        wp = {d: d - 2 for d in pc}
        up = {d: pc[d] * C(d, 2) for d in pc}
        if not _side_ok(m, pc, wp, 2 * (m - 2), s, up, C(m, 2)):
            return False
    return True

def all_profiles(m, n, T, dmin=0):
    """Exact lazy enumeration of degree multisets: n cols, sum d = T, capacity respected."""
    cap = 2 * C(m, 3)
    def rec(d, ncols, tot, capused, cur):
        if ncols == 0:
            if tot == T:
                yield dict(cur)
            return
        if tot + m * ncols < T or tot > T:
            return
        if d > m:
            return
        for k in range(ncols + 1):
            t2 = tot + k * d
            c2 = capused + k * C(d, 3)
            if t2 > T or c2 > cap:
                break
            if k: cur[d] = k
            yield from rec(d + 1, ncols - k, t2, c2, cur)
            if k: del cur[d]
    yield from rec(dmin, n, 0, 0, {})

def surviving_profiles(m, n, T):
    return [p for p in all_profiles(m, n, T) if profile_ok(m, n, T, p)]

def balanced_slack(m, n, T):
    """cap - min possible sum C(d,3): degrees as equal as possible (convexity)."""
    q, r = divmod(T, n)
    if q > m or (q == m and r > 0):
        return -1  # T impossible at all
    return 2 * C(m, 3) - (r * C(q + 1, 3) + (n - r) * C(q, 3))

def max_T_with_survivor(m, n, T_hi, T_lo, skip_slack=40):
    """Walk T downward from T_hi; return largest T with a surviving profile
    (or T_lo-1 if none in range). Also return killed levels detail.
    Fast path: if even the balanced profile has big slack, the filter cannot
    kill everything -> report survivor immediately (conservative)."""
    killed = {}
    for T in range(T_hi, T_lo - 1, -1):
        bs = balanced_slack(m, n, T)
        if bs < 0:
            killed[T] = "impossible-degrees"
            continue
        if bs > skip_slack:
            return T, killed, ["(skipped: slack %d)" % bs]
        nkilled = 0
        surv = None
        for p in all_profiles(m, n, T):
            if profile_ok(m, n, T, p):
                surv = p
                break
            nkilled += 1
        if surv is not None:
            return T, killed, [surv]
        killed[T] = nkilled
    return T_lo - 1, killed, []

if __name__ == "__main__":
    import json, sys
    # sanity: reproduce repo results
    # (9,23) at 104: all three profiles must die on the row filter
    for prof in [{4:11,5:12},{3:1,4:9,5:13},{4:12,5:10,6:1}]:
        print("9,23,104", prof, "ok" if profile_ok(9,23,104,prof) else "KILLED")
    # (10,22) at 111: all four profiles should be killed? (repo needed orbit search for
    # two of them, so our weaker filter may let some survive -- that's expected)
    for prof in [{5:21,6:1},{4:1,5:19,6:2},{4:2,5:17,6:3},{4:1,5:20,7:1}]:
        print("10,22,111", prof, "ok" if profile_ok(10,22,111,prof) else "KILLED")
    # (12,23) at 136
    for prof in all_profiles(12,23,136):
        print("12,23,136", prof if isinstance(prof,dict) else dict(prof), "ok" if profile_ok(12,23,136,prof) else "KILLED")
