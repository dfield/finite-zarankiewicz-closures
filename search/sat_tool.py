#!/usr/bin/env python3
"""SAT feasibility for K33-free m x n 0-1 matrices with a fixed column-degree profile.

Encoding:
  x[i][j] cell vars.
  y[T][j] for each row-triple T and column j: (xa & xb & xc) -> y  (one 4-clause).
  For each row-triple T: at-most-2 over {y[T][j] : j} (sequential counter).
  For each column j: exactly d_j ones (sequential counter).
  Symmetry breaking: lex order on consecutive rows (whole matrix),
  and lex order on consecutive columns within each equal-degree block.

Usage: sat_tool.py m n "5x21,6x1" [--solve SOLVER] [--out out.csv] [--time LIMIT]
Exit codes: 0 SAT (witness written), 1 UNSAT, 2 unknown/timeout.
"""
import sys, argparse, itertools, hashlib
from pathlib import Path
from pysat.formula import CNF, IDPool
from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

def build(m, n, degs):
    pool = IDPool()
    X = [[pool.id(("x", i, j)) for j in range(n)] for i in range(m)]
    cnf = CNF()
    triples = list(itertools.combinations(range(m), 3))
    for T in triples:
        a, b, c = T
        ys = []
        for j in range(n):
            y = pool.id(("y", T, j))
            cnf.append([-X[a][j], -X[b][j], -X[c][j], y])
            ys.append(y)
        amo2 = CardEnc.atmost(lits=ys, bound=2, vpool=pool, encoding=EncType.seqcounter)
        cnf.extend(amo2.clauses)
    for j in range(n):
        col = [X[i][j] for i in range(m)]
        eq = CardEnc.equals(lits=col, bound=degs[j], vpool=pool, encoding=EncType.seqcounter)
        cnf.extend(eq.clauses)
    # lex: rows i > i+1  (row i >=lex row i+1) over columns left to right
    def lex_ge(u, v):
        # u >= v lexicographically; standard chain encoding
        k = len(u)
        e = [pool.id(("e", tuple(u), tuple(v), t)) for t in range(k)]
        # e[t] true means u[0..t] == v[0..t]
        # constraints: not(v[0]) or u[0]  (u[0] >= v[0])
        cnf.append([u[0], -v[0]])
        # e[0] <-> (u0 == v0): e0 -> (u0->v0)&(v0->u0)
        cnf.append([-e[0], u[0], -v[0]])
        cnf.append([-e[0], -u[0], v[0]])
        cnf.append([e[0], u[0], v[0]])
        cnf.append([e[0], -u[0], -v[0]])
        for t in range(1, k):
            # if prefix equal, then u[t] >= v[t]
            cnf.append([-e[t-1], u[t], -v[t]])
            # e[t] <-> e[t-1] & (u[t]==v[t])
            cnf.append([-e[t], e[t-1]])
            cnf.append([-e[t], u[t], -v[t]])
            cnf.append([-e[t], -u[t], v[t]])
            cnf.append([e[t], -e[t-1], u[t], v[t]])
            cnf.append([e[t], -e[t-1], -u[t], -v[t]])
    for i in range(m - 1):
        lex_ge([X[i][j] for j in range(n)], [X[i+1][j] for j in range(n)])
    j = 0
    while j < n - 1:
        if degs[j] == degs[j+1]:
            lex_ge([X[i][j] for i in range(m)], [X[i][j+1] for i in range(m)])
        j += 1
    return cnf, X

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("m", type=int); ap.add_argument("n", type=int)
    ap.add_argument("profile")
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--out", default=None)
    ap.add_argument("--time", type=float, default=0, help="soft budget: conflict limit heuristic")
    ap.add_argument("--conflicts", type=int, default=0)
    ap.add_argument(
        "--min-row-degree",
        type=int,
        default=0,
        help="valid neighboring-bound reduction imposed on every row",
    )
    ap.add_argument("--cnf", type=Path, help="write the deterministic DIMACS formula")
    ap.add_argument("--emit-only", action="store_true", help="write/describe the CNF without solving")
    args = ap.parse_args()
    degs = []
    for tok in args.profile.split(","):
        d, k = tok.split("x")
        degs += [int(d)] * int(k)
    degs.sort(reverse=True)
    assert len(degs) == args.n, f"{len(degs)} cols vs n={args.n}"
    cnf, X = build(args.m, args.n, degs)
    if args.min_row_degree:
        if not 0 <= args.min_row_degree <= args.n:
            raise ValueError("minimum row degree is outside 0..n")
        for row in X:
            bound = CardEnc.atleast(
                lits=row,
                bound=args.min_row_degree,
                top_id=cnf.nv,
                encoding=EncType.seqcounter,
            )
            cnf.extend(bound.clauses)
    if args.cnf:
        cnf.to_file(str(args.cnf))
        digest = hashlib.sha256(args.cnf.read_bytes()).hexdigest()
        print(f"CNF vars={cnf.nv} clauses={len(cnf.clauses)} sha256={digest}")
    if args.emit_only:
        if not args.cnf:
            print(f"CNF vars={cnf.nv} clauses={len(cnf.clauses)}")
        return
    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as s:
        if args.conflicts:
            s.conf_budget(args.conflicts)
            res = s.solve_limited()
        else:
            res = s.solve()
        if res is True:
            model = set(l for l in s.get_model() if l > 0)
            rows = [[1 if X[i][j] in model else 0 for j in range(args.n)] for i in range(args.m)]
            ones = sum(map(sum, rows))
            print(f"SAT ones={ones}")
            if args.out:
                with open(args.out, "w") as f:
                    for r in rows:
                        f.write(",".join(map(str, r)) + "\n")
            sys.exit(0)
        elif res is False:
            print("UNSAT")
            sys.exit(1)
        else:
            print("UNKNOWN")
            sys.exit(2)

if __name__ == "__main__":
    main()
