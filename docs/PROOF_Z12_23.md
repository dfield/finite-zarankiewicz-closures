# Proof that $Z(12,23,3,3)=134$

This note records the case-specific proof of

$$
Z(12,23,3,3)=134.
$$

The proof and witness were produced by Claude (Anthropic) on 2026-07-05 and independently checked during integration. A fuller derivation appears in [`NEW_BOUNDS.md`](NEW_BOUNDS.md).

## Lower bound

[`data/z12_23_134_matrix.csv`](../data/z12_23_134_matrix.csv) is a $12\times23$ Boolean matrix with 134 ones. Its column-degree multiset is $4^1 5^2 6^{20}$ and its sorted row degrees are $(11^{10},12^2)$.

A direct scan checks all

$$
\binom{12}{3}\binom{23}{3}=389{,}620
$$

candidate $3\times3$ submatrices and finds no violation. Hence $Z(12,23,3,3)\ge134$.

## Excluding 136 ones

For a column of degree $d$, put

$$
p(d)=\binom d3-10d+40\ge0.
$$

Equality holds only at $d=5,6$. At 136 ones, row-triple capacity forces equality everywhere, so the unique degree profile is $5^2 6^{21}$ and every row triple occurs exactly twice.

For a row pair $P$, let $a_P$ and $b_P$ count the degree-five and degree-six columns containing $P$. Summing the two coverings of each of the ten row triples containing $P$ gives

$$
3a_P+4b_P=20,
\qquad 0\le a_P\le2.
$$

The only solution is $(a_P,b_P)=(0,5)$. Thus no row pair lies in either degree-five column, contradicting the $2\binom52=20$ pair incidences supplied by those columns.

## Excluding 135 ones

The same penalty inequality leaves exactly five profiles. Write $s$ for unused row-triple capacity; the total marked-row and marked-pair deficits are both $3s$.

| Profile | Deficit contradiction |
|---|---|
| $5^3 6^{20}$ | Row residues modulo 10 sum to at least 40, but $3s=30$. |
| $4^1 5^1 6^{21}$ | Pair residues modulo 4 sum to 22 for every exceptional-column overlap, but $3s=18$. |
| $5^4 6^{18}7^1$ | Exhaustive row-type enumeration gives minimum row-residue sum 25, but $3s=15$. |
| $4^1 5^2 6^{19}7^1$ | The residue budget permits the degree-seven column to meet at most five rows, not seven. |
| $5^5 6^{16}7^2$ | Zero residue forces five rows into all five degree-five columns, requiring 50 triple incidences when only 20 are available. |

Therefore neither 135 nor 136 ones is possible. By deleting ones, any matrix with more than 135 ones would yield one with exactly 135, so $Z(12,23,3,3)\le134$.

## Reproducible evidence

- Case certificate: [`certificates/z12_23_134.json`](../certificates/z12_23_134.json)
- Excluded-target models: [`cells_12x23_exact_135.cnf`](../models/cells_12x23_exact_135.cnf) and [`column_types_12x23_exact_135.lp`](../models/column_types_12x23_exact_135.lp)
- Standard-library certificate: `z12_23_certificate_report` in [`extended.py`](../src/finite_zarankiewicz_closures/extended.py)
- Lean arithmetic: the `z12_23_*` theorems in [`ArithmeticKernels.lean`](../lean/ZarankiewiczFiniteClosures/ArithmeticKernels.lean)
- Independent witness scan: [`verify_extended_witnesses_independent.py`](../scripts/verify_extended_witnesses_independent.py)

The finite row-type enumeration in the third profile is a proof component. Lean checks its recorded minimum and all surrounding arithmetic but does not rerun that enumeration.
