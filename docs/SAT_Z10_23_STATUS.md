# Status of the candidate value $Z(10,23,3,3)=112$

This value is **not currently a theorem of the repository**.

Bhan--Nobili--Langer supply a 112-one lower-bound construction. The contributed 2026-07-05 session recorded CaDiCaL `UNSAT` verdicts for the degree-profile subproblems at 113 and 114 ones, but retained no DIMACS files, hashes, solver transcripts, or proof traces.

## Complete profile boundary at 113

There are 25 row-triple-capacity-feasible column-degree profiles, not 24. The profile

$$
1^1 5^{20}6^2
$$

is excluded without SAT: deleting its degree-one column would leave a $10\times22$ $K_{3,3}$-free matrix with 112 ones, contradicting $Z(10,22,3,3)=110$. The remaining 24 profiles are listed in [`sat_cross_check.json`](../analysis/sat_cross_check.json) with the session's unverified verdicts.

Testing 113 ones is sufficient. If a denser valid matrix existed, changing ones to zero would preserve $K_{3,3}$-freeness until exactly 113 ones remained.

## What the integration review established

- The 25-profile catalog at 113 and 11-profile catalog at 114 are regenerated exactly.
- The missing degree-one profile is explicitly recorded as `FILTER-KILLED`.
- The profile SAT encoding agrees with direct brute force on 160 complete small instances.
- [`sat_tool.py`](../search/sat_tool.py) can now emit deterministic DIMACS with a SHA-256 digest and can impose the valid minimum-row-degree reduction inherited from $Z(9,23)=103$.
- A representative large profile did not produce a certifiable verdict within the bounded integration trial. No solver outcome from that trial is used mathematically.

## Requirement for promotion

To promote $Z(10,23,3,3)=112$ to an exact repository result, every one of the 24 surviving profiles must have either:

1. a transparent mathematical elimination; or
2. a deterministic CNF, recorded hash, `UNSAT` proof trace, and successful independent proof-checker replay.

Until that evidence exists, [`analysis/sat_cross_check.json`](../analysis/sat_cross_check.json) is labeled `UNVERIFIED_SESSION_RECORD`, and the solver-free frontier remains

$$
112\le Z(10,23,3,3)\le114.
$$
