# The upper bound $Z(13,23,3,3)\le144$

Suppose a $13\times23$ $K_{3,3}$-free matrix had 145 ones. Row-triple capacity gives

$$
\sum_j\binom{d_j}{3}\le2\binom{13}{3}=572.
$$

For $0\le d\le13$,

$$
\binom d3\ge15d-70,
$$

with equality only at $d=6,7$. The total penalty budget is

$$
572-(15\cdot145-70\cdot23)=7.
$$

Consequently the only possible degree profiles are

$$
6^{16}7^7,
\qquad 5^1 6^{14}7^8,
\qquad 6^{17}7^5 8^1.
$$

For a row $r$, let $D_r$ be its unused row-triple capacity. Then

$$
D_r=132-\sum_{j:r\in E_j}\binom{d_j-1}{2},
\qquad \sum_rD_r=3s.
$$

Degree-six and degree-seven columns contribute 10 and 15, both divisible by five. A row outside every exceptional degree-five or degree-eight column therefore satisfies $D_r\equiv2\pmod5$ and hence $D_r\ge2$.

- For $6^{16}7^7$, all 13 rows are clean, forcing at least 26 against budget 21.
- For $5^1 6^{14}7^8$, at least 8 rows are clean, forcing at least 16 against budget 6.
- For $6^{17}7^5 8^1$, at least 5 rows are clean, forcing at least 10 against budget 3.

All profiles are impossible, proving $Z(13,23,3,3)\le144$.

The standalone certificate is [`z13_23_upper_144.json`](../certificates/z13_23_upper_144.json), recomputed by `z13_23_upper_report` in [`extended.py`](../src/finite_zarankiewicz_closures/extended.py). Lean checks the profile arithmetic and terminal inequalities in [`ArithmeticKernels.lean`](../lean/ZarankiewiczFiniteClosures/ArithmeticKernels.lean). No matching 144-one construction is claimed; the repository's propagated interval is $139\text{--}144$.
