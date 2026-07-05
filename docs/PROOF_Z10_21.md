# A proof that $Z(10,21,3,3)=106$

> **Attribution:** GPT 5.6-Sol generated this proof dossier, certificate code, and verification artifacts. The result awaits independent expert review.

## Statement

$$
\boxed{Z(10,21,3,3)=106}.
$$

## Lower bound

[`z10_21_106_matrix.csv`](../data/z10_21_106_matrix.csv) is a $10\times21$ Boolean matrix with 106 ones. The primary verifier checks every row triple; the standalone verifier checks all

$$
\binom{10}{3}\binom{21}{3}=159{,}600
$$

candidate $3\times3$ submatrices. Both find no all-one submatrix.

## Upper bound

The standard deletion lemma says that if $Z(m-1,n,3,3)\le B$, then

$$
Z(m,n,3,3)\le\left\lfloor\frac{mB}{m-1}\right\rfloor.
$$

Indeed, an $m$-row matrix with $e$ ones has a row of degree at most $\lfloor e/m\rfloor$. Deleting that row leaves at least $\lceil(m-1)e/m\rceil$ ones, which cannot exceed $B$.

The established neighboring value $Z(9,21,3,3)=96$ therefore gives

$$
Z(10,21,3,3)
\le\left\lfloor\frac{10\cdot96}{9}\right\rfloor
=106.
$$

Together with the explicit construction, equality follows.

## Case-specific evidence

- JSON certificate: [`z10_21_106.json`](../certificates/z10_21_106.json)
- Lean arithmetic: `z10_21_deletion_bound` and `z10_21_excluded_target` in [`ArithmeticKernels.lean`](../lean/ZarankiewiczFiniteClosures/ArithmeticKernels.lean)
- Cell CNF at 107 ones: [`cells_10x21_exact_107.cnf`](../models/cells_10x21_exact_107.cnf)
- Column-support LP at 107 ones: [`column_types_10x21_exact_107.lp`](../models/column_types_10x21_exact_107.lp)

Lean checks the quotient and terminal arithmetic, not the combinatorial deletion lemma or CSV witness. The SAT/MIP files are transparent decision formulations, not UNSAT certificates.
