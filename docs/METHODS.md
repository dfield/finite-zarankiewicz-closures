# Methods and proof-to-code correspondence

## 1. Separation of roles

The mathematical upper bound is the argument in [`PROOF.md`](PROOF.md). None of the computational methods below is required to accept that argument. Their roles are narrower:

- check the explicit lower-bound witness;
- recompute the finite arithmetic and case split;
- preserve the original SAT and integer-programming decision formulations;
- diagnose why a published degree-only LP stops at 104; and
- expose mistakes through implementation diversity and mutation tests.

This separation matters. An opaque `UNSAT` line from a solver would be weaker evidence than the short proof, while the independent checks are still valuable protection against transcription and arithmetic errors.

## 2. Proof-to-code map

| Human-proof step | Python check | Lean declaration | Adversarial coverage |
|---|---|---|---|
| A row triple occurs in at most two columns | `verify_by_row_triples` in `matrix.py` | Outside the declared Lean scope | Direct verifier separately scans all row/column triples |
| \(p(d)=\binom d3-6d+20\) has the stated ten values | `penalty` in `certificate.py` | `penalty_eq_formula`, `penalty_table` | Certificate penalty mutation; Lean uses kernel `decide` |
| Total penalty is at most four | `verify_certificate` recomputes 164 and 168 | `affine_base`, `total_triple_capacity` | Mutated bases and tables are rejected |
| Exactly three degree profiles survive | `enumerate_degree_profiles` does not trust JSON cases | `classify_degree_profile` | Missing, duplicate, and altered profiles are rejected |
| Marked deficits sum to \(3D\) | Recomputed for each case | Exact sum is a hypothesis at the formal boundary | Each certificate incidence and deficit is recomputed |
| Residues force lower bounds 18, 15, 12 | Categories are derived from the profile | Three `*_deficits_impossible` theorems | Residue and lower-bound mutations are rejected |
| A 103-one construction exists | Two witness verifiers | Outside the declared Lean scope | All 104 one-bit extensions and a forced \(3\times3\) block are rejected |

Package files live under [`src/zarankiewicz_z9_23/`](../src/zarankiewicz_z9_23/). Command-line scripts only locate repository-relative inputs and format reports.

## 3. Lower-bound witness

[`data/z9_23_103_matrix.csv`](../data/z9_23_103_matrix.csv) is a 9-by-23 Boolean matrix with 103 ones. Its row sums are

\[
(11,11,11,11,11,11,12,12,13),
\]

and its column sums are twelve 4s and eleven 5s.

The primary verifier computes, for each of the \(\binom93=84\) row triples, the list of columns containing all three rows. It accepts only when every list has size at most two.

The standalone verifier intentionally imports no project package. It parses the CSV independently and inspects every one of

\[
\binom93\binom{23}3=148{,}764
\]

row-triple/column-triple choices. Agreement between these algorithms reduces the risk of a shared representation error.

## 4. Exact JSON certificate

[`certificates/degree_deficit.json`](../certificates/degree_deficit.json) is a transparent mirror of the upper-bound arithmetic. It records:

- the problem parameters;
- the affine identity and ten penalties;
- the three surviving degree histograms;
- triple incidences and exact deficit totals;
- row categories and their residues; and
- an equivalent aggregate row cut for each case.

The checker treats every field as untrusted. It independently enumerates all ten-entry degree histograms satisfying

\[
\sum_d n_d=23,\qquad \sum_d d n_d=104,\qquad \sum_d p(d)n_d\le4.
\]

Only after comparing the enumerated set with the JSON does it check each case. Consequently, deleting a difficult case from the certificate cannot make the checker pass.

This exact-integer certificate is the replayable nonexistence certificate for the mathematical reduction. It is small enough to inspect by hand and uses only the Python standard library.

## 5. Cell-level SAT model

The direct CNF in [`models/cells_9x23_exact_104.cnf`](../models/cells_9x23_exact_104.cnf) uses the base variable

\[
x_{r,c}=23r+c+1
\]

for zero-based row \(r\) and column \(c\). Thus variables 1 through 207 are matrix cells.

For every \(R\in\binom{[9]}3\) and \(C\in\binom{[23]}3\), the model contains

\[
\bigvee_{r\in R,\,c\in C}\neg x_{r,c}.
\]

There are 148,764 such clauses. They occur first in lexicographic combination order, making them independently stream-checkable.

Exactly 104 cells are true. The generator encodes both an at-most-104 bound on the positive literals and an at-most-103 bound on their negations. Each bound uses a sequential threshold circuit in which every auxiliary variable is defined by an equivalence, not merely constrained by a one-way implication. This slightly larger encoding is easier to audit because a base assignment has a unique threshold extension.

The final model has 32,654 variables and 277,931 clauses. [`scripts/generate_models.py`](../scripts/generate_models.py) regenerates it deterministically.

## 6. Column-type integer model

For every bit mask \(S\subseteq[9]\), the integer variable \(x_S\) counts columns whose support is exactly \(S\). The LP/MIP file imposes

\[
\sum_S x_S=23,
\qquad
\sum_S |S|x_S=104,
\qquad
\sum_{S\supseteq T}x_S\le2
\quad(T\in\tbinom{[9]}3),
\]

with \(0\le x_S\le23\) integral. It contains 512 integer variables, two structural equalities, and 84 row-triple inequalities. GLPK 5.0 independently parsed the stored model as 86 rows, 512 columns, and 6,399 nonzeros.

The cell and column models use different base objects: individual entries versus exact column supports. Their shared semantic core is only the definition of a forbidden row triple.

## 7. Encoding validation

The pure-Python test suite checks the cardinality circuit exhaustively for every Boolean assignment of up to six literals, every possible bound, positive and alternating signed literals, and every exact target. It also constructs the complete expected set of forbidden clauses in a smaller instance.

For end-to-end implementation diversity, [`scripts/validate_models.py`](../scripts/validate_models.py) uses CaDiCaL to solve:

- the known case \(Z(3,4,3,3)=10\) at targets 10 and 11; and
- 30 fixed 5-by-6 matrices generated with seed `20260704`.

For each random matrix, every cell is fixed by a unit clause. CaDiCaL satisfiability, direct forbidden-submatrix semantics, and the column-type constraint evaluator agree. The recorded report is [`audit/model_validation.json`](../audit/model_validation.json).

This validates the generators; it is not a solver proof of the 9-by-23 theorem.

## 8. Terminal DRAT and LRAT traces

The three degree cases also have tiny propositional encodings of their final aggregate contradictions:

| Case | Forced units | At-most bound | Contradiction |
|---|---:|---:|---:|
| \(4^{11}5^{12}\) | 164 | 162 | \(164>162\) |
| \(3^1 4^9 5^{13}\) | 166 | 162 | \(166>162\) |
| \(4^{12}5^{10}6^1\) | 166 | 162 | \(166>162\) |

Both DRAT and LRAT traces are stored for each CNF. `drat-trim` and `lrat-check` replay all six traces. These files certify only the terminal aggregation; the JSON checker establishes why the matrix problem reduces to those aggregations.

## 9. Davies--Gill--Horsley boundary

[`analysis/dgh_boundary.json`](../analysis/dgh_boundary.json) evaluates the full degree-count constraints of Davies--Gill--Horsley using exact rational arithmetic. The fractional profile

\[
n_4=31/3,\qquad n_5=38/3
\]

has 23 columns, saturates the 168 triple-incidence capacity, satisfies every listed DGH inequality, and has objective \(314/3\). Roman's affine inequality supplies the matching upper bound, so the relaxation optimum is exactly \(314/3\), whose floor is 104.

All three integral 104-one profiles also satisfy every DGH inequality. This identifies the lost information: a degree histogram does not record which rows belong to which columns. The marked-row congruence does.

[`analysis/local_kernel_catalog.csv`](../analysis/local_kernel_catalog.csv) records the complete row-symmetry quotient of the one-column kernels used during extraction: restrictions to three through five rows, all ambient degrees, and marked-row membership for degrees three through six. It is not described as an exhaustive catalog of arbitrary multi-column submatrices.

## 10. Lean boundary

The Lean subproject checks the arithmetic endpoint using Lean 4.29.0 and `Std` only. `chooseThree` and the penalty table are executable; kernel `decide` proves their ten finite identities. `omega` checks the Presburger degree classification and residue contradictions.

The following are not formalized in Lean:

- the definition of a Boolean matrix;
- the equivalence between \(K_{3,3}\)-freeness and row-triple capacity;
- the two combinatorial double counts; and
- the CSV witness.

Those layers are human-readable and independently executable, but they remain outside the proof assistant. [`lean/README.md`](../lean/README.md) and [`lean/AxiomAudit.lean`](../lean/AxiomAudit.lean) make this boundary testable.
