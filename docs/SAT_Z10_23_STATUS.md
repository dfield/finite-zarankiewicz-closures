# Completed certification of $Z(10,23,3,3)=112$

The candidate value from the 2026-07-05 unlogged SAT sweep has been promoted to a repository theorem:

$$
\boxed{Z(10,23,3,3)=112}.
$$

Bhan--Nobili--Langer supplied the 112-one lower bound. The stored matrix [`z10_23_112_matrix.csv`](../data/z10_23_112_matrix.csv) is checked directly. The completed upper-bound proof excludes 113 ones, which is sufficient because deleting ones preserves $K_{3,3}$-freeness.

## What changed

The original sweep retained no DIMACS files or proof traces and was correctly treated as non-load-bearing. The replacement certification now provides:

1. a standard-library enumeration of all 25 capacity-feasible degree profiles at 113 ones;
2. transparent deletion or deficit contradictions for twelve profiles;
3. one deterministic CNF for each of the remaining thirteen profiles;
4. a compressed DRAT core for every CNF; and
5. a recorded successful `drat-trim` replay and independent `lrat-check` replay for every core.

Every stored trace comes from a direct run on its unsplit base CNF and is then checked against that same file. Deterministic row-stabilizer cubes remain available as a non-load-bearing search aid; an incremental cube `UNSAT` line or raw trace is not accepted as a theorem certificate.

## Review paths

- [`PROOF_Z10_23.md`](PROOF_Z10_23.md) gives the complete mathematical reduction and formula semantics.
- [`z10_23_sat.json`](../certificates/z10_23_sat.json) binds every formula and compressed proof by SHA-256.
- [`z10_23_certify.py`](../search/z10_23_certify.py) regenerates the formulas and proof-production workflow.
- [`replay_z10_23_certificates.py`](../scripts/replay_z10_23_certificates.py) decompresses all thirteen DRAT cores, converts them to LRAT, and semantically checks both stages.
- [`sat_cross_check.json`](../analysis/sat_cross_check.json) preserves the status of the original untraced session as historical corroboration and points to its certified replacement.

The completed value also gives

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot112}{10}\right\rfloor
=123,
$$

which is exact by the stored 123-one witness. See [`PROOF_Z11_23.md`](PROOF_Z11_23.md).
