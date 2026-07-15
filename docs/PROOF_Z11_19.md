# Proof that $Z(11,19,3,3)=106$

This note isolates the complete case-specific evidence for the exact value

$$
Z(11,19,3,3)=106.
$$

The explicit witness was produced by Claude (Anthropic) on 2026-07-05 and independently checked during integration into this repository.

## Lower bound

[`data/z11_19_106_matrix.csv`](../data/z11_19_106_matrix.csv) is an $11\times19$ Boolean matrix with 106 ones. Its column-degree multiset is $5^8 6^{11}$ and its sorted row degrees are

$$
(8,9,9,9,10,10,10,10,10,10,11).
$$

A direct scan checks all

$$
\binom{11}{3}\binom{19}{3}=159{,}885
$$

candidate $3\times3$ submatrices and finds no all-one submatrix. Hence $Z(11,19,3,3)\ge106$.

## Upper bound

Use the established value $Z(11,18,3,3)=101$. If an $11\times19$ $K_{3,3}$-free matrix had 107 ones, one of its 19 columns would contain at most

$$
\left\lfloor\frac{107}{19}\right\rfloor=5
$$

ones. Deleting that column would leave an $11\times18$ $K_{3,3}$-free matrix with at least

$$
107-5=102>101
$$

ones, contradicting $Z(11,18,3,3)=101$. Thus $Z(11,19,3,3)\le106$.

## Reproducible evidence

- Case certificate: [`certificates/z11_19_106.json`](../certificates/z11_19_106.json)
- Excluded-target models: [`cells_11x19_exact_107.cnf`](../models/cells_11x19_exact_107.cnf) and [`column_types_11x19_exact_107.lp`](../models/column_types_11x19_exact_107.lp)
- End-to-end conditional Lean closure: [`DeletionClosures.lean`](../lean/Zarankiewicz/Exact/DeletionClosures.lean)
- Legacy arithmetic cross-check: `z11_19_deletion_bound` and `z11_19_excluded_target` in [`ArithmeticKernels.lean`](../lean/ZarankiewiczFiniteClosures/ArithmeticKernels.lean)
- Independent direct scan: [`verify_extended_witnesses_independent.py`](../scripts/verify_extended_witnesses_independent.py)

Lean now checks an equivalent embedded bitmask witness and proves the complete
column-deletion implication in
[`DeletionClosures.lean`](../lean/Zarankiewicz/Exact/DeletionClosures.lean).
The exact theorem deliberately retains $Z(11,18,3,3)\le101$ as a parameter,
because that historical input was established by SAT classification and no
certificate is imported into Lean.
