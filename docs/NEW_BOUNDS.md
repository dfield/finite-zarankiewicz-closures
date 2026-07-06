# Two further closures and new bounds on the 2026 frontier

> **Attribution:** The results in this document were produced by **Claude (Anthropic)** in a verification-and-extension session dated 2026-07-05, building directly on this repository's four closures and on the sources cited in the [literature review](LITERATURE_REVIEW.md). They await independent expert review.

## 1. Summary

This document extends the repository's results on the Bhan--Nobili--Langer frontier ([BNL26], Figure 2) in three ways.

**Two further exact values.**

$$
\boxed{Z(11,19,3,3)=106,}
\qquad
\boxed{Z(12,23,3,3)=134.}
$$

For $(11,19)$, the upper bound is the deletion bound already derived in [`EXTENDED_RESULTS.md`](EXTENDED_RESULTS.md) from the established value $Z(11,18,3,3)=101$; the matching lower bound is a new explicit 106-one matrix, [`data/z11_19_106_matrix.csv`](../data/z11_19_106_matrix.csv), found by simulated annealing over fixed column-degree profiles and verified by exhaustive scan. Bhan--Nobili--Langer's best construction had 102 ones.

For $(12,23)$, Section 3 proves $Z(12,23,3,3)\le134$ by a two-step deficit argument (their reported interval was $125$--$136$), and the matching lower bound is a new explicit 134-one matrix, [`data/z12_23_134_matrix.csv`](../data/z12_23_134_matrix.csv).

With these closures, nine of the paper's 44 open cells are settled and **35 remain open**.

**New elementary upper bounds.**

$$
Z(12,23,3,3)\le134,
\qquad
Z(13,23,3,3)\le144.
$$

The previous published upper bounds were 136 and 145. The proofs use only the row-triple capacity count and the deficit mechanisms already present in this repository — the pair-deficit count of the $Z(10,22)$ proof and the marked-row residues of the $Z(9,23)$ proof — applied at new parameters, with residue moduli 10 and 4 at twelve rows and 5 at thirteen rows. Full proofs are in Sections 3 and 4; every arithmetic step, including the one finite enumeration, is checked by [`scripts/check_new_bounds.py`](../scripts/check_new_bounds.py).

**A propagated bound table.** Closing the table of [BNL26] under the deletion lemma and under two-one-line extensions tightens 20 upper bounds and 17 lower bounds beyond the paper's published intervals, without any new search. The machine-readable result, with per-cell provenance, is [`analysis/new_bounds.json`](../analysis/new_bounds.json). Section 5 lists every change.

## 2. The value $Z(11,19,3,3)=106$

### 2.1 Upper bound

[`EXTENDED_RESULTS.md`](EXTENDED_RESULTS.md) Section 2 already proves

$$
Z(11,19,3,3)\le\left\lfloor\frac{19\cdot101}{18}\right\rfloor=106
$$

from the established value $Z(11,18,3,3)=101$: a $K_{3,3}$-free $11\times19$ matrix with $e$ ones has a column with at most $\lfloor e/19\rfloor$ ones, and deleting it leaves an $11\times18$ matrix. At $e=107$ this leaves at least $107-5=102>101$ ones, a contradiction.

### 2.2 Lower bound

[`data/z11_19_106_matrix.csv`](../data/z11_19_106_matrix.csv) is an $11\times19$ Boolean matrix with 106 ones, column degrees $5^86^{11}$, and row degrees $(8,9,9,9,10,10,10,10,10,10,11)$. Exhaustive inspection of all $\binom{11}{3}\binom{19}{3}=159{,}885$ candidate $3\times3$ submatrices confirms that none is all one; equivalently, every row triple occurs in at most two columns (the used triple capacity is $8\binom53+11\binom63=300$ of the available $2\binom{11}3=330$).

The matrix was found by annealing within the fixed degree profile $5^86^{11}$; the discovery method carries no logical weight, because verification is a direct exhaustive scan.

## 3. Theorem: $Z(12,23,3,3)=134$

The proof of the upper bound has two steps: first 136 ones are excluded by a short pair-count argument (Section 3.1--3.3), then 135 ones are excluded by a residue analysis of the five surviving degree profiles (Section 3.4). The lower bound is discussed in Section 3.5.

### Step one: no 136-one matrix

Suppose, for contradiction, that a $12\times23$ $K_{3,3}$-free matrix has 136 ones. Let $E_j$ and $d_j$ be the row set and degree of column $j$, and for each row triple $T$ let $\lambda_T$ be the number of columns whose row set contains $T$. As in the four existing proofs, $K_{3,3}$-freeness means $\lambda_T\le2$, and double counting gives

$$
\sum_{j=1}^{23}\binom{d_j}{3}=\sum_T\lambda_T\le2\binom{12}{3}=440. \tag{1}
$$

### 3.1 The degree profile is forced

The integer inequality

$$
\binom d3\ge10d-40 \tag{2}
$$

holds for all $0\le d\le12$ with equality exactly at $d=5$ and $d=6$ (the deficit at $d=4$ is 4, at $d=7$ is 5, and grows monotonically further away). Summing (2) over the 23 columns,

$$
\sum_j\binom{d_j}{3}\;\ge\;10\cdot136-40\cdot23=440.
$$

Combined with (1), equality holds everywhere. Consequently:

- every column degree is 5 or 6; and
- $\sum_T\lambda_T=440$, so $\lambda_T=2$ for **every** row triple $T$.

Solving $a+b=23$, $5a+6b=136$ gives $(a,b)=(2,21)$: exactly two degree-5 columns and twenty-one degree-6 columns.

### 3.2 The pair count

Fix a row pair $P$; there are $\binom{12}2=66$ such pairs, and each lies in $10$ row triples. Since every triple satisfies $\lambda_T=2$,

$$
\sum_{T\supset P}\lambda_T=20.
$$

On the other hand, a column $j$ with $P\subseteq E_j$ contains $d_j-2$ triples through $P$, and columns not containing $P$ contribute nothing, so

$$
\sum_{j:\,P\subseteq E_j}(d_j-2)=20.
$$

Writing $a_P$ for the number of degree-5 columns containing $P$ and $b_P$ for the number of degree-6 columns containing $P$,

$$
3a_P+4b_P=20,\qquad 0\le a_P\le2.
$$

Modulo 4 this forces $3a_P\equiv0\pmod4$, hence $a_P\equiv0\pmod4$, hence $a_P=0$.

### 3.3 The contradiction

Every row pair therefore lies in **no** degree-5 column. But each of the two degree-5 columns contains $\binom52=10$ row pairs, so

$$
\sum_P a_P=2\binom52=20\ne0.
$$

This contradiction shows no 136-one matrix exists. $\blacksquare$

### 3.4 Step two: no 135-one matrix

Now suppose 135 ones. Inequality (2) gives $\sum_j\binom{d_j}3\ge10\cdot135-40\cdot23=430$, so the deficit budget against (1) is 10; since the deficits of (2) at $d=4,7$ are $4$ and $5$ and at least 14 elsewhere, every degree lies in $\{4,5,6,7\}$ with at most two exceptional columns. Exhausting the count and sum equations leaves exactly five profiles (slack $s=440-\sum_j\binom{d_j}3$):

$$
5^36^{20}\ (s{=}10),\quad
4^15^16^{21}\ (s{=}6),\quad
5^46^{18}7^1\ (s{=}5),\quad
4^15^26^{19}7^1\ (s{=}1),\quad
5^56^{16}7^2\ (s{=}0).
$$

Write $u_r,a_r,b_r$ for the number of degree-4, degree-5, degree-7 columns through row $r$, and $x_P,y_P,z_P$ for the same counts through a row pair $P$. Two residue identities do all the work. The row deficit $D_r=110-\sum_{j\ni r}\binom{d_j-1}2$ satisfies, modulo 10 (killing the degree-6 contribution $\binom52=10$ and $110$ itself),

$$
D_r\equiv 7u_r+4a_r+5b_r \pmod{10},\qquad D_r\ge0,\qquad \sum_rD_r=3s. \tag{6}
$$

The pair deficit $D_P=20-\sum_{j\supseteq P}(d_j-2)$ satisfies, modulo 4 (killing the degree-6 contribution),

$$
D_P\equiv 2x_P+y_P+3z_P \pmod4,\qquad D_P\ge0,\qquad \sum_PD_P=3s. \tag{7}
$$

Since each $D_r$ (resp. $D_P$) is congruent to its residue and nonnegative, it is at least that residue; summing residues therefore cannot exceed $3s$. Finally, $K_{3,3}$-freeness bounds shared rows across column triples: for the degree-5 columns,

$$
\sum_r\binom{a_r}3\le2\binom{n_5}3,
\qquad
\sum_r\binom{a_r}2\,b_r\le2\binom{n_5}2n_7. \tag{8}
$$

The five profiles die as follows.

1. **$5^36^{20}$, $3s=30$.** By (6), $D_r\ge(4a_r\bmod10)$, and $\sum_ra_r=15$. With $n_a$ rows of each $a$, the residue sum is $4n_1+8n_2+2n_3=60-10n_3$. By (8), $n_3\le2$, so the sum is at least $40>30$.

2. **$4^15^16^{21}$, $3s=18$.** By (7) with $t$ the overlap of the two exceptional columns, the pair residues total
$2\bigl(\binom42-\binom t2\bigr)+\bigl(\binom52-\binom t2\bigr)+3\binom t2=22>18$ for every $t$.

3. **$5^46^{18}7^1$, $3s=15$.** By (6), $D_r\ge\bigl((4a_r+5b_r)\bmod10\bigr)$ with $\sum a_r=20$, $\sum b_r=7$. An exhaustive enumeration of the row-type counts under the two budgets (8) — a few hundred cases, re-run by the checker — shows the residue sum is at least 25.

4. **$4^15^26^{19}7^1$, $3s=3$.** Every row residue must be at most 3. For the four rows of the degree-4 column, (6) allows only $(a,b)\in\{(1,0),(0,1),(2,1)\}$; for the other eight rows only $(0,0)$ at cost 0 or $(2,1)$ at cost 3, and the budget admits at most one of the latter. Hence at most $4+1=5$ rows can meet the degree-7 column, which has seven rows.

5. **$5^56^{16}7^2$, $s=0$.** Every deficit vanishes, so every row satisfies $4a_r+5b_r\equiv0\pmod{10}$, forcing $a_r\in\{0,5\}$. Then $\sum_ra_r=25$ forces five rows with $a_r=5$, giving $\sum_r\binom{a_r}3=50$, against the budget $2\binom53=20$ in (8).

No profile survives, so no 135-one matrix exists, and $Z(12,23,3,3)\le134$. $\blacksquare$

### 3.5 The matching lower bound

[`data/z12_23_134_matrix.csv`](../data/z12_23_134_matrix.csv) is an explicit $12\times23$ Boolean matrix with 134 ones, column degrees $4^15^26^{20}$, and row degrees $(11^{10},12^2)$. Exhaustive inspection of all $\binom{12}3\binom{23}3=389{,}620$ candidate $3\times3$ submatrices confirms that none is all one. (Independently of this artifact, appending a two-one column to Bhan--Nobili--Langer's $Z(12,22,3,3)=132$ construction also gives 134.) Hence

$$
Z(12,23,3,3)=134 .
$$

The matrix was found by per-profile SAT search; the discovery method carries no logical weight, because the verification is a direct scan.

## 4. Theorem: $Z(13,23,3,3)\le144$

Suppose a $13\times23$ $K_{3,3}$-free matrix has 145 ones. Now

$$
\sum_j\binom{d_j}{3}\le2\binom{13}{3}=572, \tag{3}
$$

and the line through degrees 6 and 7 gives the integer inequality

$$
\binom d3\ge15d-70, \tag{4}
$$

valid for $0\le d\le13$ with equality exactly at $d=6,7$; the deficit is 5 at $d=5$, 6 at $d=8$, and at least 14 elsewhere. Summing (4),

$$
\sum_j\binom{d_j}{3}\ge15\cdot145-70\cdot23=565,
$$

so the total deficit budget is $572-565=7$: at most one column may have degree outside $\{6,7\}$, and its degree must be 5 or 8. Exhausting $a+b=23$ (or 22) with the degree sums leaves exactly three profiles:

| Profile | $\sum_j\binom{d_j}3$ | slack $s=572-\sum_j\binom{d_j}3$ | $3s$ |
|---|---:|---:|---:|
| $6^{16}7^{7}$ | 565 | 7 | 21 |
| $5^{1}6^{14}7^{8}$ | 570 | 2 | 6 |
| $8^{1}6^{17}7^{5}$ | 571 | 1 | 3 |

### 4.1 Marked-row deficits modulo 5

For each triple put $\delta_T=2-\lambda_T\ge0$, and for each row $r$ put $D_r=\sum_{T\ni r}\delta_T$. Exactly as in the $Z(9,23)$ proof,

$$
\sum_{r=1}^{13}D_r=3\sum_T\delta_T=3s,
\qquad
D_r=2\binom{12}{2}-\sum_{j:\,r\in E_j}\binom{d_j-1}{2}
=132-\sum_{j:\,r\in E_j}\binom{d_j-1}{2}. \tag{5}
$$

The column contributions in (5) are $\binom52=10$ for degree 6 and $\binom62=15$ for degree 7 — both divisible by 5 — and $132\equiv2\pmod5$.

Call a row **clean** if it lies in no degree-5 and no degree-8 column. For a clean row, (5) gives $D_r\equiv2\pmod5$, and since $D_r\ge0$,

$$
D_r\ge2 .
$$

### 4.2 The three contradictions

- **$6^{16}7^{7}$.** All 13 rows are clean, so $\sum_rD_r\ge26>21=3s$.
- **$5^{1}6^{14}7^{8}$.** The single degree-5 column meets 5 rows, so at least 8 rows are clean and $\sum_rD_r\ge16>6=3s$.
- **$8^{1}6^{17}7^{5}$.** The single degree-8 column meets 8 rows, so at least 5 rows are clean and $\sum_rD_r\ge10>3=3s$.

All profiles are impossible, so no 145-one matrix exists. $\blacksquare$

## 5. The propagated bound table

Two elementary observations close the published table under implication:

1. **Deletion (upper bounds).** If $Z(m-1,n,3,3)\le B$ then $Z(m,n,3,3)\le\lfloor mB/(m-1)\rfloor$, and symmetrically in $n$. This is the lemma of [`EXTENDED_RESULTS.md`](EXTENDED_RESULTS.md) Section 2.
2. **Two-one-line extension (lower bounds).** Appending a row or column with exactly two ones can never create a $K_{3,3}$ (an all-one $3\times3$ block needs three ones from every participating line), so $Z(m,n,3,3)\ge Z(m-1,n,3,3)+2$ and $Z(m,n,3,3)\ge Z(m,n-1,3,3)+2$.

Seeding with the "previously established" cells of [BNL26] Figure 2 (values from Tan's Table 3, [Tan22]), the eight closures, the paper's published intervals, and the two theorems above, and iterating to a fixpoint, produces [`analysis/new_bounds.json`](../analysis/new_bounds.json). The changed cells:

| Cell | [BNL26] interval | New interval | Upper-bound mechanism |
|---|---:|---:|---|
| $(10,23)$ | 112--115 | 112--**114** | deletion from $Z(9,23)=103$ |
| $(11,23)$ | 118--125 | **123**--125 | (lower bound lift from $Z(11,22)=121$) |
| $(12,17)$ | 102--108 | 102--**104** | deletion from $Z(11,17)=96$ |
| $(12,18)$ | 108--113 | 108--**110** | deletion from $Z(11,18)=101$ |
| $(12,19)$ | 110--118 | 110--**115** | deletion from $Z(11,19)=106$ |
| $(12,20)$ | 113--122 | 113--**121** | deletion from $Z(11,20)=111$ |
| $(12,21)$ | 116--127 | **118**--**126** | deletion from $Z(11,21)=116$ |
| $(12,23)$ | 125--136 | **134** (closed) | Section 3 theorem |
| $(13,17)$ | 106--116 | **109**--**112** | deletion from $(12,17)$ |
| $(13,18)$ | 115--121 | 115--**118** | deletion from $(13,17)$ |
| $(13,19)$ | 114--125 | **117**--**124** | deletion from $(13,18)$ |
| $(13,23)$ | 135--145 | **139**--**144** | Section 4 theorem |
| $(14,17)$ | 118--124 | 118--**120** | deletion from $(13,17)$ |
| $(14,18)$ | 124--129 | 124--**127** | deletion from $(13,18)$ |
| $(14,19)$ | 121--135 | **126**--**133** | deletion from $(13,19)$ |
| $(14,20)$ | 125--140 | **128**--140 | (lower bound lift only) |
| $(14,22)$ | 137--150 | **139**--150 | (lower bound lift only) |
| $(14,23)$ | 138--155 | **141**--155 | (lower bound lift only) |
| $(15,17)$ | 125--132 | 125--**128** | deletion from $(14,17)$ |
| $(15,18)$ | 132--138 | 132--**135** | deletion from $(15,17)$ |
| $(15,19)$ | 132--143 | **134**--**142** | deletion from $(15,18)$ |
| $(15,21)$ | 139--154 | **140**--154 | (lower bound lift only) |
| $(16,17)$ | 128--141 | **130**--**136** | deletion from $Z(16,16)=128$ |
| $(16,18)$ | 130--146 | **134**--**144** | deletion from $(16,17)$ |
| $(16,19)$ | 132--152 | **136**--**151** | deletion from $(15,19)$ |
| $(16,21)$ | 147--164 | **148**--164 | (lower bound lift only) |
| $(16,22)$ | 149--169 | **150**--169 | (lower bound lift only) |

Cells not listed are unchanged. Note that $(12,19)$, $(12,20)$, and $(12,21)$ inherit their improvements from this session's closure of $(11,19)$ and from the repository's $(11,20)$ and the paper's $(11,21)$ values through a single deletion step each; the remaining improvements chain through the $n=16$ and $n=17$ columns.

## 6. Provenance, trust boundary, and what is *not* claimed

- The $Z(11,19)$ **upper** bound and every deletion-propagated bound depend on the correctness of the established values in [BNL26] Figure 2 / Tan's Table 3 — the same dependency already accepted by [`EXTENDED_RESULTS.md`](EXTENDED_RESULTS.md) for $Z(10,21)$ and $Z(11,20)$. The witness and both deficit theorems are self-contained.
- The theorems of Sections 3 and 4 are fully elementary; [`scripts/check_new_bounds.py`](../scripts/check_new_bounds.py) re-derives the profile classifications by exhaustive enumeration and re-checks every displayed number, in the standard library only.
- During the same session, per-profile SAT runs (CaDiCaL via PySAT, with sequential-counter cardinality encodings and double-lex symmetry breaking) produced two families of verdicts, recorded in [`analysis/sat_cross_check.json`](../analysis/sat_cross_check.json):
  - **Cross-check of this repository.** Every capacity-feasible column-degree profile at all four previously excluded targets — $(9,23)$ at 104, $(10,21)$ at 107, $(10,22)$ at 111, and $(11,20)$ at 112 — returned `UNSAT`. This confirms the four published upper bounds by a mechanism independent of the marked-row, deletion, and pair-deficit proofs.
  - **Frontier observations.** All 11 profiles of a hypothetical 114-one $10\times23$ matrix returned `UNSAT`. At 113 ones, 24 profiles returned `UNSAT`; the twenty-fifth profile, $1^15^{20}6^2$, is killed arithmetically (and is also impossible because deleting its degree-one column would leave 112 ones in a $10\times22$ matrix, contradicting $Z(10,22,3,3)=110$). Modulo the unlogged solver verdicts this gives $Z(10,23,3,3)\le112$, and Bhan--Nobili--Langer's 112-one construction then closes the cell at $Z(10,23,3,3)=112$.

  **No claim in the solver-free table rests on those verdicts** — in particular the $(10,23)$ value is deliberately *not* entered in [`analysis/new_bounds.json`](../analysis/new_bounds.json), because no independently checkable proof trace was retained. The 2026-07-06 integration audit checked the profile catalog and small instances of the encoding but could not certify the recorded large UNSAT outcomes. Thus $Z(10,23,3,3)=112$ is a research lead, not a repository theorem. A proof-logged rerun (plus the elementary elimination of the one degree-one profile) would be required to upgrade it; see [`SAT_Z10_23_STATUS.md`](SAT_Z10_23_STATUS.md).
- The figure-2 transcription used here was re-read from the arXiv HTML of [BNL26] v2 during the session and matches [`analysis/extended_results.json`](../analysis/extended_results.json); the upper bounds equal $\min(\text{[Tan22] Table 3},\ \text{[DGH26] Table 2})$ cell-by-cell, and an exact-rational re-computation of the [DGH26] linear program reproduced their published values for every open cell.

## 7. Reproduction

```sh
# everything claimed above (witness scan, both theorems, the propagated table)
python3 scripts/check_new_bounds.py --check

# regenerate the machine-readable table after an intentional change
python3 scripts/check_new_bounds.py --write
```

The checker requires only Python 3.9+. Its profile enumerator uses convexity and degree-sum pruning so the complete check remains suitable for the repository's CI matrix.
