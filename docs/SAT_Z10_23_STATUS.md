# Certification status of $Z(10,23,3,3)=112$

> **Status as of 2026-07-14:** complete replayable certificate; upper bound certified.

The repository establishes

$$
\boxed{Z(10,23,3,3)=112}.
$$

## Completed evidence

- The 112-one matrix [`z10_23_112_matrix.csv`](../data/z10_23_112_matrix.csv) passes two exhaustive $K_{3,3}$-freeness checks.
- Independent enumerators find exactly 25 capacity-feasible degree profiles at 113 ones.
- Deletion and deficit arguments eliminate twelve profiles.
- Ten surviving profiles have direct CaDiCaL DRAT proofs, independently converted to and checked as LRAT.
- One profile has a complete 17,170-leaf row-stabilizer cube cover, with a checked DRAT/LRAT proof for each leaf.
- Two profiles have complete exact SCIP/VIPR covers: 209 orbits covering 295,001 states and 236 orbits covering 950,250 states.
- The repository independently reconstructs both orbit censuses, regenerates every leaf OPB, and compares every VIPR embedded model coefficient-for-coefficient with that regenerated formula.
- [`z10_23_sat.json`](../certificates/z10_23_sat.json) binds all thirteen formulas, proof indexes, catalogs, manifests, checker identities, and split release assets by SHA-256.

The earlier solver sweep that retained no proof traces remains `CORROBORATING_ONLY`. It is not used in the proof.

## Consequence for $Z(11,23)$

The certified upper bound gives

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot112}{10}\right\rfloor
=123.
$$

Together with the checked 123-one witness, this establishes $Z(11,23,3,3)=123$.

See [`PROOF_Z10_23.md`](PROOF_Z10_23.md), [`PROOF_Z11_23.md`](PROOF_Z11_23.md), [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md), and the machine-readable [`result_status.json`](../analysis/result_status.json).
