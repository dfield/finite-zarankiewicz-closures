#!/usr/bin/env python3
"""Exact-rational DGH LP bound E(m,n;3,3): maximize sum d*x_d subject to
   sum x_d = n, Roman capacity, and DGH Thm 1.2 constraints (v=1,2; k=3..m).
   Small dense simplex over Fractions (Bland's rule)."""
import math, json, sys
from fractions import Fraction as F

S3 = 3; T3 = 3

def dgh_constraint(m, v, k):
    denb = math.comb(k - v, S3 - v)
    avail = (T3 - 1) * math.comb(m - v, S3 - v)
    alpha = avail % denb
    coef = {}
    for d in range(S3 - 1, m + 1):
        if d < k:
            small = math.comb(d - v, S3 - v) if d - v >= S3 - v else 0
            coef[d] = F(small - alpha, denb - alpha) * math.comb(d, v)
        else:
            coef[d] = F(math.comb(d, v))
    rhs = F(math.comb(m, v) * (avail - alpha), denb)
    return coef, rhs

def simplex_max(c, A, b):
    """max c^T x, Ax <= b, x >= 0. Dense tableau, Bland. Returns optimum (Fraction)."""
    mrows = len(A); ncols = len(c)
    # tableau: rows = constraints, cols = ncols + mrows slacks + rhs
    Tb = [[F(A[i][j]) for j in range(ncols)] + [F(1) if k == i else F(0) for k in range(mrows)] + [F(b[i])]
          for i in range(mrows)]
    cost = [F(-x) for x in c] + [F(0)] * mrows + [F(0)]
    basis = [ncols + i for i in range(mrows)]
    # Phase: b >= 0 assumed except equality encoded rows; ensure b >= 0 by flipping? We
    # guarantee b >= 0 in construction (n, capacities are nonnegative).
    for bi in b:
        assert bi >= 0
    while True:
        # entering: first negative cost (Bland)
        e = next((j for j in range(ncols + mrows) if cost[j] < 0), None)
        if e is None:
            break
        # ratio test
        best = None; brow = None
        for i in range(mrows):
            if Tb[i][e] > 0:
                r = Tb[i][-1] / Tb[i][e]
                if best is None or r < best or (r == best and basis[i] < basis[brow]):
                    best = r; brow = i
        if brow is None:
            raise RuntimeError("unbounded")
        piv = Tb[brow][e]
        Tb[brow] = [x / piv for x in Tb[brow]]
        for i in range(mrows):
            if i != brow and Tb[i][e] != 0:
                f = Tb[i][e]
                Tb[i] = [a - f * p for a, p in zip(Tb[i], Tb[brow])]
        if cost[e] != 0:
            f = cost[e]
            cost = [a - f * p for a, p in zip(cost, Tb[brow])]
        basis[brow] = e
    return cost[-1]

def dgh_lp(m, n):
    degs = list(range(0, m + 1))
    c = [F(d) for d in degs]
    A = []; b = []
    # sum x_d <= n  and  -sum x_d <= -n ... need b>=0; use <= n plus objective pressure
    # (объective is increasing in x so equality binds upward; but extra columns of degree 0
    # cost nothing; sum <= n suffices since adding columns never hurts the max)
    A.append([F(1)] * len(degs)); b.append(F(n))
    A.append([F(math.comb(d, 3)) for d in degs]); b.append(F(2 * math.comb(m, 3)))
    for v in (1, 2):
        for k in range(3, m + 1):
            coef, rhs = dgh_constraint(m, v, k)
            if rhs < 0:  # infeasible-looking rows shouldn't occur; skip negatives for b>=0
                continue
            A.append([coef.get(d, F(0)) for d in degs]); b.append(rhs)
    return simplex_max(c, A, b)

if __name__ == "__main__":
    cells = [(9,23),(10,21),(10,22),(10,23),(11,19),(11,20),(11,21),(11,22),(11,23)] + \
            [(m,n) for m in range(12,17) for n in range(17,24)]
    out = {}
    for (m,n) in cells:
        v1 = dgh_lp(m,n)
        v2 = dgh_lp(n,m)
        v = min(v1, v2)
        out[f"{m},{n}"] = {"lp": str(v), "floor": v.numerator // v.denominator,
                           "lp_rows_side": str(v1), "lp_cols_side": str(v2)}
        print(f"({m},{n}): E = {v} -> {v.numerator//v.denominator}", flush=True)
    json.dump(out, open(sys.path[0] + "/dgh_lp.json", "w"), indent=1)
