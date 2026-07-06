# Methods and proof-to-code correspondence

## 1. Separation of roles

The repository contains four kinds of upper-bound argument, with different trust boundaries:

- the $(9,23)$ marked-row proof in [`PROOF.md`](PROOF.md) is human-readable and does not logically require computation;
- the $(10,21)$, $(11,19)$, and $(11,20)$ proofs are elementary applications of vertex deletion;
- the $(10,22)$ proof includes an exhaustive standard-library enumeration of two finite residue cases; and
- the $(12,23)$ proof combines a forced-profile pair count with a five-profile row/pair-deficit certificate. The same machinery gives $Z(13,23)\le144$.

The remaining computational methods have narrower corroborating or reproducibility roles:

- check the explicit lower-bound witness;
- recompute the finite arithmetic and case split;
- preserve the original SAT and integer-programming decision formulations;
- diagnose why a published degree-only LP stops at 104; and
- expose mistakes through implementation diversity and mutation tests.

This separation matters. No claimed value relies on an opaque `UNSAT` line, but the $(10,22)$ and $(12,23)$ finite enumerations are genuine computer-assisted proof components and are labeled as such.

## 2. The $(9,23)$ proof-to-code map

| Human-proof step | Python check | Lean declaration | Adversarial coverage |
|---|---|---|---|
| A row triple occurs in at most two columns | `verify_by_row_triples` in `matrix.py` | Outside the declared Lean scope | Direct verifier separately scans all row/column triples |
| $p(d)=\binom d3-6d+20$ has the stated ten values | `penalty` in `certificate.py` | `penalty_eq_formula`, `penalty_table` | Certificate penalty mutation; Lean uses kernel `decide` |
| Total penalty is at most four | `verify_certificate` recomputes 164 and 168 | `affine_base`, `total_triple_capacity` | Mutated bases and tables are rejected |
| Exactly three degree profiles survive | `enumerate_degree_profiles` does not trust JSON cases | `classify_degree_profile` | Missing, duplicate, and altered profiles are rejected |
| Marked deficits sum to $3D$ | Recomputed for each case | Exact sum is a hypothesis at the formal boundary | Each certificate incidence and deficit is recomputed |
| Residues force lower bounds 18, 15, 12 | Categories are derived from the profile | Three `*_deficits_impossible` theorems | Residue and lower-bound mutations are rejected |
| A 103-one construction exists | Two witness verifiers | Outside the declared Lean scope | All 104 one-bit extensions and a forced $3\times3$ block are rejected |

Package files live under [`src/finite_zarankiewicz_closures/`](../src/finite_zarankiewicz_closures/). Command-line scripts only locate repository-relative inputs and format reports.

## 3. Lower-bound witness

[`data/z9_23_103_matrix.csv`](../data/z9_23_103_matrix.csv) is a 9-by-23 Boolean matrix with 103 ones. Its row sums are

$$
(11,11,11,11,11,11,12,12,13),
$$

and its column sums are twelve 4s and eleven 5s.

The primary verifier computes, for each of the $\binom93=84$ row triples, the list of columns containing all three rows. It accepts only when every list has size at most two.

The standalone verifier intentionally imports no project package. It parses the CSV independently and inspects every one of

$$
\binom93\binom{23}3=148{,}764
$$

row-triple/column-triple choices. Agreement between these algorithms reduces the risk of a shared representation error.

## 4. Case-specific JSON certificates

[`scripts/check_case_certificates.py`](../scripts/check_case_certificates.py) regenerates one standalone certificate for each of the six exact values. Each certificate binds the complete witness report and SHA-256 digest to the case's own upper-bound mechanism: marked-row deficits, deletion, pair-deficit enumeration, or the two-stage $(12,23)$ deficit proof. Stored fields are compared with recomputation, and mutation tests require every schema to reject altered values.

The original detailed subcertificate, [`certificates/degree_deficit.json`](../certificates/degree_deficit.json), remains the arithmetic payload for the $(9,23)$ case.

[`certificates/degree_deficit.json`](../certificates/degree_deficit.json) is a transparent mirror of the upper-bound arithmetic. It records:

- the problem parameters;
- the affine identity and ten penalties;
- the three surviving degree histograms;
- triple incidences and exact deficit totals;
- row categories and their residues; and
- an equivalent aggregate row cut for each case.

The checker treats every field as untrusted. It independently enumerates all ten-entry degree histograms satisfying

$$
\sum_d n_d=23,\qquad \sum_d d n_d=104,\qquad \sum_d p(d)n_d\le4.
$$

Only after comparing the enumerated set with the JSON does it check each case. Consequently, deleting a difficult case from the certificate cannot make the checker pass.

This exact-integer subcertificate is the replayable nonexistence certificate for the marked-row reduction. The other five case certificates contain their corresponding deletion arithmetic, four-profile report, or two-stage deficit report. All use only the Python standard library.

## 5. Cell-level SAT models

Each exact-value theorem has a direct cell CNF at its first excluded weight: 104, 107, 111, 107, 112, and 135 for $(9,23)$, $(10,21)$, $(10,22)$, $(11,19)$, $(11,20)$, and $(12,23)$ respectively. The $(9,23)$ model in [`models/cells_9x23_exact_104.cnf`](../models/cells_9x23_exact_104.cnf) illustrates the encoding and uses the base variable

$$
x_{r,c}=23r+c+1
$$

for zero-based row $r$ and column $c$. Thus variables 1 through 207 are matrix cells.

For every $R\in\binom{[9]}3$ and $C\in\binom{[23]}3$, the model contains

$$
\bigvee_{r\in R,\,c\in C}\neg x_{r,c}.
$$

There are 148,764 such clauses. They occur first in lexicographic combination order, making them independently stream-checkable.

Exactly 104 cells are true. The generator encodes both an at-most-104 bound on the positive literals and an at-most-103 bound on their negations. Each bound uses a sequential threshold circuit in which every auxiliary variable is defined by an equivalence, not merely constrained by a one-way implication. This slightly larger encoding is easier to audit because a base assignment has a unique threshold extension.

That model has 32,654 variables and 277,931 clauses. [`scripts/generate_models.py`](../scripts/generate_models.py) regenerates all six cell CNFs deterministically; [`models/manifest.json`](../models/manifest.json) records every dimension and hash.

## 6. Column-type integer models

For each case and every bit mask $S$ on its row set, the integer variable $x_S$ counts columns whose support is exactly $S$. For the $(9,23)$ case the LP/MIP file imposes

$$
\sum_S x_S=23,
\qquad
\sum_S |S|x_S=104,
\qquad
\sum_{S\supseteq T}x_S\le2
\quad(T\in\tbinom{[9]}3),
$$

with $0\le x_S\le23$ integral. The six stored LPs use 512, 1,024, 1,024, 2,048, 2,048, and 4,096 support variables according to their row counts. Each has two structural equalities and one inequality per row triple.

The cell and column models use different base objects: individual entries versus exact column supports. Their shared semantic core is only the definition of a forbidden row triple. None is presented as an UNSAT certificate for the claimed upper bound.

## 7. Encoding validation

The pure-Python test suite checks the cardinality circuit exhaustively for every Boolean assignment of up to six literals, every possible bound, positive and alternating signed literals, and every exact target. It also constructs the complete expected set of forbidden clauses in a smaller instance.

For end-to-end implementation diversity, [`scripts/validate_models.py`](../scripts/validate_models.py) uses CaDiCaL to solve:

- the known case $Z(3,4,3,3)=10$ at targets 10 and 11; and
- 30 fixed 5-by-6 matrices generated with seed `20260704`.

For each random matrix, every cell is fixed by a unit clause. CaDiCaL satisfiability, direct forbidden-submatrix semantics, and the column-type constraint evaluator agree. The recorded report is [`audit/model_validation.json`](../audit/model_validation.json).

This validates the generators; it is not a solver proof of the 9-by-23 theorem.

## 8. Terminal DRAT and LRAT traces

The three degree cases also have tiny propositional encodings of their final aggregate contradictions:

| Case | Forced units | At-most bound | Contradiction |
|---|---:|---:|---:|
| $4^{11}5^{12}$ | 164 | 162 | $164>162$ |
| $3^1 4^9 5^{13}$ | 166 | 162 | $166>162$ |
| $4^{12}5^{10}6^1$ | 166 | 162 | $166>162$ |

Both DRAT and LRAT traces are stored for each CNF. `drat-trim` and `lrat-check` replay all six traces. These files certify only the terminal aggregation; the JSON checker establishes why the matrix problem reduces to those aggregations.

## 9. Davies--Gill--Horsley boundary

[`analysis/dgh_boundary.json`](../analysis/dgh_boundary.json) evaluates the full degree-count constraints of Davies--Gill--Horsley using exact rational arithmetic. The fractional profile

$$
n_4=31/3,\qquad n_5=38/3
$$

has 23 columns, saturates the 168 triple-incidence capacity, satisfies every listed DGH inequality, and has objective $314/3$. Roman's affine inequality supplies the matching upper bound, so the relaxation optimum is exactly $314/3$, whose floor is 104.

All three integral 104-one profiles also satisfy every DGH inequality. This identifies the lost information: a degree histogram does not record which rows belong to which columns. The marked-row congruence does.

[`analysis/local_kernel_catalog.csv`](../analysis/local_kernel_catalog.csv) records the complete row-symmetry quotient of the one-column kernels used during extraction: restrictions to three through five rows, all ambient degrees, and marked-row membership for degrees three through six. It is not described as an exhaustive catalog of arbitrary multi-column submatrices.

## 10. Lean boundary

The Lean subproject checks arithmetic endpoints for all six exact values and the $(13,23)$ bound using Lean 4.29.0 and `Std` only. The original library checks the $(9,23)$ penalty table, profile classification, and residue contradictions. The additional library checks the deletion chains, the $(10,22)$ certificate endpoints, both stages of the $(12,23)$ profile argument, and the $(13,23)$ profile/residue arithmetic. Kernel `decide` handles executable finite identities; `omega` checks the Presburger consequences.

The following are not formalized in Lean:

- the definition of a Boolean matrix;
- the equivalence between $K_{3,3}$-freeness and row-triple capacity;
- the combinatorial double counts and deletion lemma;
- the $Z(10,22)$ row-symmetry orbit enumeration; and
- the six CSV witnesses.

Those layers are human-readable and independently executable, but they remain outside the proof assistant. [`lean/README.md`](../lean/README.md) and [`lean/AxiomAudit.lean`](../lean/AxiomAudit.lean) make the six-case boundary testable.

## 11. Additional finite-table certificate

[`EXTENDED_RESULTS.md`](EXTENDED_RESULTS.md) and [`NEW_BOUNDS.md`](NEW_BOUNDS.md) close five additional cells from the 2026 table. Three closures use vertex deletion. The $Z(10,22,3,3)=110$ and $Z(12,23,3,3)=134$ bounds use finite degree-profile and deficit certificates.

| Result | Upper-bound mechanism | Computational role |
|---|---|---|
| $Z(10,21,3,3)=106$ | One row-deletion step from $Z(9,21,3,3)=96$ | Arithmetic replay only |
| $Z(10,22,3,3)=110$ | Four-profile pair-deficit elimination | Exhaustive finite enumeration is required |
| $Z(11,19,3,3)=106$ | One column-deletion step from $Z(11,18,3,3)=101$ | Arithmetic replay only |
| $Z(11,20,3,3)=111$ | Two column-deletion steps from $Z(11,18,3,3)=101$ | Arithmetic replay only |
| $Z(12,23,3,3)=134$ | Forced profile at 136 plus five-profile deficit elimination at 135 | One finite row-type enumeration is required |
| $Z(13,23,3,3)\le144$ | Three-profile marked-row residue argument | Finite profile classification only |

The two nontrivial finite subcases are checked by row-symmetry reduction:

- 1,050 configurations for profile $4^1 5^{19}6^2$; and
- 77 exceptional-column orbits, each with 22,155 degree-four multisets, for profile $4^2 5^{17}6^3$.

The reusable implementation is [`extended.py`](../src/finite_zarankiewicz_closures/extended.py), and [`check_extended_results.py`](../scripts/check_extended_results.py) compares its recomputed output byte-for-byte with [`extended_results.json`](../analysis/extended_results.json). The independent witness checker imports no package code, but it verifies constructions rather than independently reimplementing the $(10,22)$ upper-bound enumeration.
