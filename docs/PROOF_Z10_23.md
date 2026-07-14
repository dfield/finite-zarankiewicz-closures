# Candidate dossier for $Z(10,23,3,3)=112$

## 1. Status and evidence boundary

The proposed equality

$$
Z(10,23,3,3)=112
$$

is **not yet an established theorem in this repository**. The checked matrix proves $Z(10,23,3,3)\ge112$. The arithmetic front end reduces the excluded target 113 to thirteen SAT instances, but a final proof manifest and independent replay audit covering every instance are not present at this publication boundary.

The unconditional result currently supported here is

$$
112\le Z(10,23,3,3)\le114.
$$

The authoritative status record is [`analysis/result_status.json`](../analysis/result_status.json).

## 2. Translation to row subsets

Suppose that a $10\times23$ $K_{3,3}$-free Boolean matrix has 113 ones. For column $j$, let $E_j\subseteq[10]$ be its support and put $d_j=|E_j|$. If $\lambda_T$ is the number of columns containing a row triple $T$, then $K_{3,3}$-freeness is equivalent to $\lambda_T\le2$. Therefore

$$
\sum_{j=1}^{23}\binom{d_j}{3}
=\sum_{T\in\binom{[10]}3}\lambda_T
\le2\binom{10}{3}=240. \tag{1}
$$

For $0\le d\le10$, define

$$
p(d)=\binom d3-10d+40.
$$

The values are

$$
(p(0),\ldots,p(10))=(40,30,20,11,4,0,0,5,16,34,60).
$$

Consequently,

$$
\sum_jp(d_j)
=\sum_j\binom{d_j}{3}-10\cdot113+40\cdot23
\le30. \tag{2}
$$

Exhausting the nonnegative integer solutions to the column count, degree sum, and (1) gives exactly 25 profiles. The standard-library function `z10_23_profile_report()` regenerates this list.

## 3. Twelve profiles have arithmetic contradictions

Five profiles contain a column of degree at most two. Deleting that column leaves at least 111 ones in a $10\times22$ matrix, contradicting the established value $Z(10,22,3,3)=110$.

Four profiles contain two degree-three columns. Deleting both leaves 107 ones in a $10\times21$ matrix, contradicting $Z(10,21,3,3)=106$.

Two further profiles are eliminated by row-deficit congruences. For a row $r$, put

$$
D_r=72-\sum_{j:r\in E_j}\binom{d_j-1}{2}\ge0.
$$

If

$$
s=240-\sum_j\binom{d_j}{3},
$$

then double counting gives $\sum_rD_r=3s$. The profiles $4^6 5^{14}6^2 7^1$ and $3^1 4^3 5^{17}6^1 7^1$ have minimum residue sums 6 and 9, respectively, exceeding their budgets 3 and 6.

The twelfth profile, $3^1 4^2 5^{19}7^1$, is eliminated by a finite pair-residue enumeration. For a row pair $P$,

$$
D_P=16-\sum_{j:P\subseteq E_j}(d_j-2)\ge0,
\qquad
\sum_PD_P=18. \tag{3}
$$

Enumerating unlabelled row-membership multiplicities in the four exceptional columns gives 1,577 configurations, of which 1,380 satisfy the triple-overlap restriction. The minimum legal sum of the least nonnegative residues in (3) is 39, contradicting the budget 18. The checker recomputes all three counts.

Thus twelve of the 25 profiles are unconditionally impossible.

## 4. The thirteen remaining proof obligations

The profiles still requiring propositional certificates are

$$
\begin{aligned}
&4^2 5^{21},\quad 4^3 5^{19}6^1,\quad 4^4 5^{17}6^2,
  \quad 4^4 5^{18}7^1,\\
&4^5 5^{15}6^3,\quad 4^5 5^{16}6^1 7^1,
  \quad 4^6 5^{13}6^4,\quad 4^7 5^{11}6^5,\\
&3^1 5^{22},\quad 3^1 4^1 5^{20}6^1,
  \quad 3^1 4^2 5^{18}6^2,\\
&3^1 4^3 5^{16}6^3,\quad 3^1 4^4 5^{14}6^4.
\end{aligned}
$$

For each profile, the deterministic CNF uses cell variables $x_{rj}$ and enforces:

1. the specified degree of every column;
2. at most two columns containing each row triple;
3. lexicographically nonincreasing rows and, inside equal-degree blocks, lexicographically nonincreasing columns; and
4. row degree at least ten, since deleting any row leaves at most $Z(9,23,3,3)=103$ ones.

The generic models and partial proof-production files are useful, but they do not by themselves prove unsatisfiability. Before the equality may be promoted, the repository must contain and verify all of the following:

1. a final manifest binding all thirteen exact CNFs by SHA-256;
2. a checked DRAT proof for every direct case and every retained cover leaf;
3. independent DRAT-to-LRAT conversion and LRAT replay;
4. a deterministic completeness check for every split cover, rejecting missing, overlapping, duplicate, or noncanonical leaves; and
5. a recorded end-to-end replay audit whose inputs match the checked-in or release-bound artifacts.

The AWS workflow is producing and recovering these artifacts. Operational `UNSAT` output, checkpoint presence, or an S3 upload is not theorem evidence. See [`AWS_Z10_23_RUN.md`](AWS_Z10_23_RUN.md) and [`SAT_Z10_23_STATUS.md`](SAT_Z10_23_STATUS.md).

## 5. Established lower and upper bounds

[`z10_23_112_matrix.csv`](../data/z10_23_112_matrix.csv) is a $10\times23$ Boolean matrix with 112 ones and no all-one $3\times3$ submatrix. Two exhaustive verifiers check it directly. Hence

$$
Z(10,23,3,3)\ge112.
$$

The established value $Z(9,23,3,3)=103$ gives, by vertex deletion,

$$
Z(10,23,3,3)
\le\left\lfloor\frac{10\cdot103}{9}\right\rfloor
=114.
$$

Therefore the publishable conclusion is

$$
\boxed{112\le Z(10,23,3,3)\le114}.
$$

If the thirteen propositional obligations are all replayably refuted, the upper endpoint improves to 112 and the proposed equality follows.

## 6. Reproduction and trust boundary

The witness, profile enumeration, twelve arithmetic eliminations, and current interval are covered by the core gate:

```bash
make verify
```

The Lean development checks arithmetic endpoints only; it does not replay SAT proofs or formalize the Boolean-matrix reduction. Once a complete SAT manifest and all bound assets exist, the separate heavyweight gate is:

```bash
make candidate-certificate
```

That gate is deliberately not part of the publishable theorem suite yet. The original untraced solver sweep remains `CORROBORATING_ONLY` in [`analysis/sat_cross_check.json`](../analysis/sat_cross_check.json).
