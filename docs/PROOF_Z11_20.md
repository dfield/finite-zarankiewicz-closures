# A proof that $Z(11,20,3,3)=111$

> **Attribution:** GPT 5.6-Sol generated this proof dossier, certificate code, and verification artifacts. The result awaits independent expert review.

## Statement

$$
\boxed{Z(11,20,3,3)=111}.
$$

## Lower bound

[`z11_20_111_matrix.csv`](../data/z11_20_111_matrix.csv) is an $11\times20$ Boolean matrix with 111 ones. The package verifier checks all 165 row triples, while the standalone verifier examines

$$
\binom{11}{3}\binom{20}{3}=188{,}100
$$

candidate $3\times3$ submatrices.

## Upper bound

Apply the column version of the deletion lemma twice. From the established value $Z(11,18,3,3)=101$,

$$
Z(11,19,3,3)
\le\left\lfloor\frac{19\cdot101}{18}\right\rfloor
=106.
$$

Therefore

$$
Z(11,20,3,3)
\le\left\lfloor\frac{20\cdot106}{19}\right\rfloor
=111.
$$

The explicit 111-one matrix supplies the matching lower bound.

## Case-specific evidence

- JSON certificate: [`z11_20_111.json`](../certificates/z11_20_111.json)
- End-to-end conditional Lean closure: [`DeletionClosures.lean`](../lean/Zarankiewicz/Exact/DeletionClosures.lean)
- Legacy arithmetic cross-check: `z11_19_deletion_bound`, `z11_20_deletion_bound`, and both excluded-target theorems in [`ArithmeticKernels.lean`](../lean/ZarankiewiczFiniteClosures/ArithmeticKernels.lean)
- Cell CNF at 112 ones: [`cells_11x20_exact_112.cnf`](../models/cells_11x20_exact_112.cnf)
- Column-support LP at 112 ones: [`column_types_11x20_exact_112.lp`](../models/column_types_11x20_exact_112.lp)

Lean now checks an equivalent embedded witness and proves both combinatorial
column-deletion steps in
[`DeletionClosures.lean`](../lean/Zarankiewicz/Exact/DeletionClosures.lean).
The exact theorem deliberately retains $Z(11,18,3,3)\le101$ as a parameter;
the branch imports neither its SAT certificate nor any project axiom. The
SAT/MIP files are reproducible formulations rather than solver certificates.
