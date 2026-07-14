# Certification status of the $Z(10,23,3,3)=112$ candidate

> **Status as of 2026-07-13:** upper bound not yet certified.

The repository does not currently claim

$$
Z(10,23,3,3)=112
$$

as a theorem. It establishes only

$$
112\le Z(10,23,3,3)\le114.
$$

## What is complete

- [`z10_23_112_matrix.csv`](../data/z10_23_112_matrix.csv) is a checked 112-one $K_{3,3}$-free witness.
- Independent standard-library enumerators find exactly 25 capacity-feasible degree profiles at 113 ones.
- Transparent deletion and deficit arguments eliminate twelve profiles.
- Deterministic CNFs exist for the remaining thirteen profiles.
- Partial direct and cover proof-production artifacts are retained for continued certification work.

## What is missing

The equality needs a complete replayable refutation of every one of the thirteen remaining profiles. At this publication boundary there is no final [`certificates/z10_23_sat.json`](../certificates/README.md) manifest and no end-to-end replay audit covering every direct proof and every leaf of each complete cover.

The AWS recovery run is documented in [`AWS_Z10_23_RUN.md`](AWS_Z10_23_RUN.md). Cloud solver output and checkpoints are operational evidence only. Promotion requires hash-bound artifacts, a deterministic cover-completeness check, DRAT replay, derived LRAT replay, and a repository audit that passes from a clean clone.

## Consequence for $Z(11,23)$

If the missing certificate establishes $Z(10,23,3,3)\le112$, then vertex deletion gives

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot112}{10}\right\rfloor
=123.
$$

The checked 123-one witness would then prove $Z(11,23,3,3)=123$. Until that dependency is discharged, the established interval is $123\le Z(11,23,3,3)\le125$.

See [`PROOF_Z10_23.md`](PROOF_Z10_23.md), [`PROOF_Z11_23.md`](PROOF_Z11_23.md), and the machine-readable [`result_status.json`](../analysis/result_status.json).
