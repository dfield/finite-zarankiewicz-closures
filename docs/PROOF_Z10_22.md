# A computer-assisted proof that $Z(10,22,3,3)=110$

> **Attribution:** GPT 5.6-Sol generated this proof dossier, finite certificate, and verification artifacts. The result awaits independent expert review.

## Statement and lower bound

$$
\boxed{Z(10,22,3,3)=110}.
$$

[`z10_22_110_matrix.csv`](../data/z10_22_110_matrix.csv) has 110 ones. Every row has sum 11, its column profile is $4^5 5^{12}6^5$, and every row triple occurs in exactly two columns. A standalone scan checks all 184,800 candidate $3\times3$ submatrices.

## Degree profiles at 111

Suppose that 111 ones were possible. If the column degrees are $d_1,\ldots,d_{22}$, row-triple capacity gives

$$
\sum_j\binom{d_j}{3}\le2\binom{10}{3}=240.
$$

The nonnegative penalty $\binom d3-10d+40$ has values

$$
(40,30,20,11,4,0,0,5,16,34,60)
$$

for $d=0,\ldots,10$. Its total is at most ten. Exact integer enumeration leaves four profiles:

$$
5^{21}6^1,\qquad
4^1 5^{19}6^2,\qquad
4^2 5^{17}6^3,\qquad
4^1 5^{20}7^1.
$$

## Pair deficits and elimination

For a row triple $T$, put $\delta_T=2-\lambda_T$. For a row pair $P$, define

$$
D_P=\sum_{T\supset P}\delta_T
=16-\sum_{j:P\subseteq E_j}(d_j-2),
\qquad
\sum_P D_P=3\sum_T\delta_T.
$$

Degree-five columns vanish modulo three, so the exceptional columns determine the least possible nonnegative residues.

1. For $5^{21}6^1$, the forced pair degrees give a sum of 45 around a row outside the degree-six column. Every degree-five column through that row contributes four, so this sum must be divisible by four—a contradiction.
2. For $4^1 5^{19}6^2$, the degree-six columns intersect in $k=2,3,4,5,6$ rows. Checking all 210 degree-four columns gives minimum residue sums $21,21,21,33,48$, each greater than the exact total 18.
3. For $4^2 5^{17}6^3$, 77 row-symmetry orbits and all 22,155 unordered degree-four multisets per orbit give minimum residue sum 12, greater than the exact total 6.
4. For $4^1 5^{20}7^1$, the degree-four and degree-seven columns have symmetric difference at least three. Each such row forces deficit at least three, giving at least 9 instead of the exact total 3.

Thus 111 ones are impossible and the 110-one construction is optimal.

## Computer-assisted boundary and evidence

The orbit enumerations in Cases 2 and 3 are exhaustive proof components implemented with the Python standard library. They are not heuristic searches or solver verdicts. Lean checks the penalty table, four-profile classification, reported minima, and terminal contradictions, but does not re-run the orbit enumeration.

- JSON certificate: [`z10_22_110.json`](../certificates/z10_22_110.json)
- Lean arithmetic: [`ArithmeticKernels.lean`](../lean/ZarankiewiczFiniteClosures/ArithmeticKernels.lean)
- Cell CNF at 111 ones: [`cells_10x22_exact_111.cnf`](../models/cells_10x22_exact_111.cnf)
- Column-support LP at 111 ones: [`column_types_10x22_exact_111.lp`](../models/column_types_10x22_exact_111.lp)
