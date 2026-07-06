#!/usr/bin/env python3
"""Driver: for a cell (m,n) and target ones T, enumerate feasible column-degree
profiles and run zsearch2 in parallel until one hits. Verifies hits independently."""
import sys, math, itertools, subprocess, os, csv, tempfile

S = os.path.dirname(os.path.abspath(__file__))
C = math.comb

def profiles(m, n, T, dmin=0, dmax=None, cap_slack=None):
    dmax = dmax or min(m, 9)
    cap = 2*C(m,3)
    out = []
    # multisets of degrees d in [dmin,dmax], n columns, sum T, sum C(d,3) <= cap
    def rec(d, ncols, tot, capused, counts):
        if ncols == 0:
            if tot == T:
                out.append((capused, dict(counts)))
            return
        if d > dmax: return
        # prune: max achievable with remaining cols
        if tot + dmax*ncols < T: return
        if tot + d*ncols > T and d > dmin: pass
        maxk = ncols
        for k in range(maxk+1):
            t2 = tot + k*d
            c2 = capused + k*C(d,3)
            if t2 > T or c2 > cap: break
            counts.append((d,k))
            rec(d+1, ncols-k, t2, c2, counts)
            counts.pop()
    rec(dmin, n, 0, 0, [])
    # prefer more slack (easier), then fewer extreme degrees
    out.sort(key=lambda x: x[0])
    return [(cap - capused, cnts) for capused, cnts in out]

def prof_str(cnts):
    return ",".join(f"{d}x{k}" for d,k in sorted(cnts.items()) if k>0)

def verify(path, m, n, T):
    rows = [[int(x) for x in r] for r in csv.reader(open(path))]
    assert len(rows)==m and all(len(r)==n for r in rows)
    ones = sum(map(sum, rows))
    if ones != T: return False, f"ones={ones}"
    for cols in itertools.combinations(range(n), 3):
        cnt = 0
        for r in rows:
            if r[cols[0]] and r[cols[1]] and r[cols[2]]:
                cnt += 1
                if cnt == 3: return False, f"K33 at cols {cols}"
    return True, "ok"

def attack(m, n, T, per_run=60, seeds=(1,2,3,4), max_profiles=None, verbose=True):
    profs = profiles(m, n, T)
    if verbose:
        print(f"[{m}x{n} T={T}] {len(profs)} feasible profiles")
    if not profs:
        print(f"[{m}x{n} T={T}] IMPOSSIBLE by column capacity (no profile)")
        return None
    if max_profiles: profs = profs[:max_profiles]
    for slack, cnts in profs:
        ps = prof_str(cnts)
        outs = []
        procs = []
        for sd in seeds:
            o = os.path.join(S, f"w_{m}_{n}_{T}_{sd}.csv")
            p = subprocess.Popen([os.path.join(S,"zsearch2"), str(m), str(n), ps, str(per_run), str(sd), o],
                                 stdout=subprocess.PIPE, text=True)
            procs.append((p,o,sd))
        hit = None
        for p,o,sd in procs:
            p.wait()
            if p.returncode == 0 and hit is None:
                hit = o
        for p,o,sd in procs:
            if hit != o and os.path.exists(o) and o != hit:
                try: os.remove(o)
                except OSError: pass
        if verbose:
            print(f"  profile {ps} slack={slack}: {'HIT' if hit else 'miss'}", flush=True)
        if hit:
            ok, msg = verify(hit, m, n, T)
            if not ok:
                print(f"  VERIFY FAILED: {msg}"); continue
            final = os.path.join(S, f"witness_{m}x{n}_{T}.csv")
            os.replace(hit, final)
            print(f"[{m}x{n} T={T}] FOUND & VERIFIED -> {final}")
            return final
    return None

if __name__ == "__main__":
    m, n, T = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    per = int(sys.argv[4]) if len(sys.argv)>4 else 60
    mp = int(sys.argv[5]) if len(sys.argv)>5 else None
    attack(m, n, T, per_run=per, max_profiles=mp)
