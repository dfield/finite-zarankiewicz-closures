# A pure-Lean proof that $Z(10,22,3,3)=110$

> **Attribution:** GPT 5.6-Sol generated the original proof dossier, finite certificate, and verification artifacts. OpenAI Codex replaced the two orbit-enumeration steps with kernel-checked incidence arguments and completed the end-to-end Lean theorem. The result awaits independent expert review.

## Statement and lower bound

$$
\boxed{Z(10,22,3,3)=110}.
$$

The matrix in [`data/z10_22_110_matrix.csv`](../data/z10_22_110_matrix.csv) has 110 ones. Its equivalent column-bitmask representation is embedded in [`lean/Zarankiewicz/Witnesses.lean`](../lean/Zarankiewicz/Witnesses.lean). Lean's ordinary kernel evaluator checks both

$$
\operatorname{edgeCount}(A)=110
\qquad\text{and}\qquad
A\text{ is }K_{3,3}\text{-free}.
$$

No CSV parser, Python result, or external certificate is a premise of the Lean lower bound.

## Degree profiles at 111

Suppose that 111 ones were possible. If the column degrees are $d_1,\ldots,d_{22}$, row-triple capacity gives

$$
\sum_j\binom{d_j}{3}\le2\binom{10}{3}=240.
$$

The nonnegative penalty $\binom d3-10d+40$ has values

$$
(40,30,20,11,4,0,0,5,16,34,60)
$$

for $d=0,\ldots,10$. Its total is at most ten. Lean's Presburger kernel reduces the possibilities to

$$
5^{21}6^1,\qquad
4^1 5^{19}6^2,\qquad
4^2 5^{17}6^3,\qquad
4^1 5^{20}7^1.
$$

## Pair deficits

For a row triple $T$, put $\delta_T=2-\lambda_T$. For a row pair $P$, define

$$
D_P=\sum_{T\supset P}\delta_T
=16-\sum_{j:P\subseteq E_j}(d_j-2),
\qquad
\sum_P D_P=3\sum_T\delta_T.
$$

These equalities, the row analogues, and all degree-class incidence identities are proved for Boolean matrices in Lean.

## Elimination of the four profiles

1. For $5^{21}6^1$, all thirty row pairs outside the unique degree-six column have deficit one. Around a row outside that column, the degree-five pair counts sum to 45. Each degree-five column through the row contributes four, so the same sum is divisible by four, a contradiction.

2. For $4^1 5^{19}6^2$, write $x_P$ and $z_P$ for the numbers of degree-four and degree-six columns through $P$, and let

   $$
   r_P=(1+x_P+2z_P)\bmod 3.
   $$

   Here $x_P\le1$ and $z_P\le2$. Lean checks the pointwise identity

   $$
   r_P+z_P+3x_P\binom{z_P}{2}
   =1+x_P+3\binom{z_P}{2}.
   $$

   Summing it and using $x_P\binom{z_P}{2}\le\binom{z_P}{2}$ gives $\sum_P r_P\ge21$, while $r_P\le D_P$ and $\sum_P D_P=18$. This replaces the former five-orbit enumeration.

3. For $4^2 5^{17}6^3$, let $x_r,z_r$ be the corresponding column counts through row $r$. The least row-deficit residue modulo six, together with the row and three-column incidence totals, forces

   $$
   \#\{z_r=0\}=2,\quad
   \#\{z_r=1\}=0,\quad
   \#\{z_r=2\}=6,\quad
   \#\{z_r=3\}=2,
   $$

   and exactly one row has $x_r=2$. Consequently,

   $$
   \sum_r\binom{x_r}{2}=1,\qquad
   \sum_r\binom{z_r}{2}=12,\qquad
   \sum_r\binom{z_r}{3}=2.
   $$

   The first identity gives $x_P\le1$ for every row pair. Marking a row with $z_r=3$ gives

   $$
   \sum_P\binom{z_P}{2}\ge9.
   $$

   Three distinct columns have at most one common row pair, so

   $$
   \sum_P\binom{z_P}{3}\le1,
   \qquad
   \sum_P\binom{z_P}{2}x_P\le6.
   $$

   Finally Lean checks, for $x_P\le1$ and $z_P\le3$,

   $$
   r_P+z_P+6\binom{z_P}{3}
      +3\binom{z_P}{2}x_P
   =1+x_P+3\binom{z_P}{2}
      +9x_P\binom{z_P}{3}.
   $$

   Its summed left side is at most $75$, while its summed right side is at least $84$, a contradiction. This replaces the former 77-orbit, 22,155-multiset sweep.

4. For $4^1 5^{20}7^1$, the degree-four and degree-seven columns have symmetric difference at least three. Each such row forces deficit at least three, giving at least nine units although the complete profile has only three.

Thus 111 ones are impossible and the 110-one construction is optimal.

## Lean theorem and independent evidence

The public theorem is

```lean
Zarankiewicz.Exact.Z10_22.exact_value :
  Zarankiewicz.Exact 10 22 110
```

in [`lean/Zarankiewicz/Exact/Z10_22.lean`](../lean/Zarankiewicz/Exact/Z10_22.lean). It imports no SAT trace or generated certificate and contains no `sorry`, custom axiom, or `native_decide`.

```bash
cd lean
lake build +Zarankiewicz.Exact.Z10_22:olean
lake env lean AxiomAudit.lean
```

The original JSON certificate, Python enumeration, CNF, and LP remain valuable independent checks and discovery artifacts:

- [`certificates/z10_22_110.json`](../certificates/z10_22_110.json)
- [`src/finite_zarankiewicz_closures/extended.py`](../src/finite_zarankiewicz_closures/extended.py)
- [`models/cells_10x22_exact_111.cnf`](../models/cells_10x22_exact_111.cnf)
- [`models/column_types_10x22_exact_111.lp`](../models/column_types_10x22_exact_111.lp)

They are no longer load-bearing for the Lean theorem.
