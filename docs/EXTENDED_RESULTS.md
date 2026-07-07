# Seven further exact values in the 2026 finite table

> **Attribution:** GPT 5.6-Sol generated the original three extensions. Claude (Anthropic) produced the later $Z(11,19)$ witness and $Z(12,23)$ proof and witness. The traced $Z(10,23)$ certification and its $Z(11,23)$ consequence were completed with OpenAI Codex. These additions were independently audited and integrated into the repository's verification layers. The results await independent expert review.

## 1. Scope and status

[Bhan, Nobili, and Langer](https://arxiv.org/html/2605.01120v2) reported 44 previously open values of $Z(m,n,3,3)$ in Figure 2. Their paper closed three of them:

$$
Z(11,21,3,3)=116,\qquad
Z(11,22,3,3)=121,\qquad
Z(12,22,3,3)=132.
$$

Alongside this repository's marked-row result $Z(9,23,3,3)=103$, the extended analysis closes seven more:

$$
\boxed{Z(10,21,3,3)=106},\qquad
\boxed{Z(10,22,3,3)=110},\qquad
\boxed{Z(10,23,3,3)=112},
$$

$$
\boxed{Z(11,19,3,3)=106},\qquad
\boxed{Z(11,20,3,3)=111},\qquad
\boxed{Z(11,23,3,3)=123},
$$

$$
\boxed{Z(12,23,3,3)=134}.
$$

Thus eleven of the paper's 44 open cells are now closed by the paper and this repository, and **33 remain open**. This document does not claim exact values for those 33 cases.

For case-by-case review, see the dedicated dossiers for [$Z(10,21,3,3)=106$](PROOF_Z10_21.md), [$Z(10,22,3,3)=110$](PROOF_Z10_22.md), [$Z(10,23,3,3)=112$](PROOF_Z10_23.md), [$Z(11,19,3,3)=106$](PROOF_Z11_19.md), [$Z(11,20,3,3)=111$](PROOF_Z11_20.md), [$Z(11,23,3,3)=123$](PROOF_Z11_23.md), and [$Z(12,23,3,3)=134$](PROOF_Z12_23.md).

## 2. The deletion lemma

If $Z(m-1,n,3,3)\le B$, then

$$
Z(m,n,3,3)\le\left\lfloor\frac{mB}{m-1}\right\rfloor.
$$

Indeed, an $m$-row matrix with $e$ ones has a row containing at most $\lfloor e/m\rfloor$ ones. Deleting that row leaves at least $\lceil (m-1)e/m\rceil$ ones, which cannot exceed $B$. The same argument applies when adding a column instead of a row.

Since the established value $Z(9,21,3,3)=96$ appears in the paper's table,

$$
Z(10,21,3,3)
\le\left\lfloor\frac{10\cdot96}{9}\right\rfloor
=106.
$$

The paper supplies a 106-one construction, so equality holds.

Similarly, the established value $Z(11,18,3,3)=101$ gives

$$
Z(11,19,3,3)
\le\left\lfloor\frac{19\cdot101}{18}\right\rfloor
=106,
$$

and then

$$
Z(11,20,3,3)
\le\left\lfloor\frac{20\cdot106}{19}\right\rfloor
=111.
$$

The explicit matrices [`z11_19_106_matrix.csv`](../data/z11_19_106_matrix.csv) and [`z11_20_111_matrix.csv`](../data/z11_20_111_matrix.csv) prove equality in both deletion bounds.

After the traced proof of $Z(10,23,3,3)=112$ described in Section 4, the same lemma gives

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot112}{10}\right\rfloor
=123.
$$

The explicit 123-one matrix [`z11_23_123_matrix.csv`](../data/z11_23_123_matrix.csv) gives equality.

## 3. The value $Z(10,22,3,3)=110$

### 3.1 Lower bound

[`z10_22_110_matrix.csv`](../data/z10_22_110_matrix.csv) is a $10\times22$ matrix with 110 ones. Every row has sum 11. Its column degrees are

$$
4^5 5^{12}6^5.
$$

Those degrees use all $2\binom{10}{3}=240$ row-triple capacity units. Direct verification confirms that every row triple occurs in exactly two columns, so the matrix is $K_{3,3}$-free.

### 3.2 Degree profiles at 111

Suppose a 111-one matrix existed, and let $d_1,\ldots,d_{22}$ be its column degrees. Row-triple counting gives

$$
\sum_j\binom{d_j}{3}\le2\binom{10}{3}=240.
$$

The integer inequality

$$
\binom d3\ge10d-40
$$

is sharp at $d=5,6$. Enumerating the nonnegative penalties subject to 22 columns and total degree 111 leaves exactly four profiles:

$$
5^{21}6^1,\qquad
4^1 5^{19}6^2,\qquad
4^2 5^{17}6^3,\qquad
4^1 5^{20}7^1.
$$

### 3.3 Pair deficits

For each row triple $T$, put $\delta_T=2-\lambda_T$. For a row pair $P$, define

$$
D_P=\sum_{T\supset P}\delta_T
=16-\sum_{j:P\subseteq E_j}(d_j-2).
$$

If $D=\sum_T\delta_T$, then

$$
\sum_{P\in\binom{[10]}2}D_P=3D.
$$

Degree-five columns contribute three to the second expression for $D_P$. Consequently, the exceptional degree-four, degree-six, and degree-seven columns determine $D_P$ modulo three.

### 3.4 Eliminate the four profiles

1. **Profile $5^{21}6^1$.** Let $E$ be the degree-six column. Nonnegativity and residues force $D_P=0$ for the 15 pairs inside $E$ and $D_P=1$ for the other 30 pairs. Hence the number of degree-five columns through a pair is four inside $E$ and five otherwise. For a row outside $E$, the sum of those nine pair degrees is 45. But each degree-five column through that row contributes four, so the sum must be divisible by four. Contradiction.

2. **Profile $4^1 5^{19}6^2$.** Let $g_P$ indicate containment in the degree-four column and let $q_P$ count containment in the two degree-six columns. Then $D_P\ge (16-2g_P-4q_P)\bmod3$.

   Up to row permutation, the degree-six columns intersect in $k=2,3,4,5,6$ rows. Exhausting the 210 possible degree-four columns gives minimum residue sums $21,21,21,33,48$, respectively. Every value exceeds $\sum_PD_P=18$.

3. **Profile $4^2 5^{17}6^3$.** With $g_P$ and $q_P$ now counting the two degree-four and three degree-six columns, $D_P\ge (16-2g_P-4q_P)\bmod3$.

   Fixing one degree-six column, classifying a second by intersection size, and classifying the third under the stabilizer gives 77 row-symmetry orbits. For each orbit, all 22,155 unordered multisets of two degree-four columns are checked. The minimum residue sum is 12, exceeding $\sum_PD_P=6$.

4. **Profile $4^1 5^{20}7^1$.** The analogous one-row deficits sum to three. A row in exactly one of the degree-four and degree-seven columns has deficit at least three. Their symmetric difference has size at least three, so the total row deficit is at least nine. Contradiction.

All four profiles are impossible. Therefore 111 ones cannot occur, and the 110-one matrix is optimal.

## 4. The traced value $Z(10,23,3,3)=112$

At 113 ones, row-triple capacity leaves exactly 25 column-degree profiles. Low-degree deletion eliminates nine, and row/pair-deficit residues eliminate three more. The remaining thirteen profiles are translated to deterministic CNFs. Every CNF has a direct, checked, compressed DRAT core of the unsplit base formula, and every core is converted to independently checked LRAT. Optional row-stabilizer cube searches are non-load-bearing. The explicit matrix [`z10_23_112_matrix.csv`](../data/z10_23_112_matrix.csv) supplies the lower bound.

The complete reduction, formula semantics, symmetry argument, and trust boundary are in [`PROOF_Z10_23.md`](PROOF_Z10_23.md). [`z10_23_sat.json`](../certificates/z10_23_sat.json) binds all formula and proof hashes, and `scripts/replay_z10_23_certificates.py` independently replays every DRAT core through LRAT checking.

## 5. Reproducibility and trust boundary

Run the complete standard-library check with:

```sh
PYTHONPATH=src python3 scripts/check_extended_results.py --check
PYTHONPATH=src python3 scripts/check_case_certificates.py --check
python3 scripts/verify_extended_witnesses_independent.py
```

The checker independently enumerates the $(10,22)$, $(10,23)$, and $(12,23)$ degree profiles and every finite residue case. It also verifies all seven additional matrices by row-triple capacity. The standalone verifier imports no project module and instead scans every candidate $3\times3$ submatrix.

The finite enumeration is an exhaustive proof component, not a heuristic optimization run. The only SAT-dependent upper bound, $(10,23)$, is backed by independently replayable DRAT/LRAT certificates rather than an opaque `UNSAT` line.

All seven results also have individual JSON certificates, excluded-target SAT/MIP formulations, and Lean arithmetic endpoints. Lean checks the profile classifications and reported finite minima but does not rerun the row-symmetry/row-type searches or replay SAT proofs.

## 6. Remaining open cells

After these closures, the 33 unresolved cells from the paper are:

- $(12,n)$ for $n\in\{17,18,19,20,21\}$; and
- $(m,n)$ for $13\le m\le16$ and $17\le n\le23$.

The machine-readable boundary and the original Figure 2 intervals are stored in [`extended_results.json`](../analysis/extended_results.json).
