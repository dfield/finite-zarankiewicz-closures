# Adversarial audit

## Audit objective

This audit asks how the claimed value \(Z(9,23,3,3)=103\) could be wrong even if ordinary happy-path tests pass. It treats prose, data, generators, certificates, formal code, and literature claims as separate attack surfaces.

The audit was completed against the repository state dated 2026-07-04. “Full” here means every evidence layer shipped by the repository was placed in scope; it does not mean the work has received external peer review or that every possible implementation has been verified.

## Threat model

The principal failure modes considered were:

1. an invalid 103-one matrix is accepted because of a parser or indexing bug;
2. the degree-case certificate omits a profile or trusts a forged arithmetic field;
3. the SAT and MIP generators encode a different problem;
4. a proof trace is malformed or is presented as covering a broader reduction than it does;
5. Lean succeeds because of an admission, custom axiom, or inaccurately stated boundary;
6. a literature table is misread as exact;
7. generated evidence depends on a local path, timestamp, random seed, or unavailable private source; or
8. documentation silently upgrades corroborating computation into the theorem's logical basis.

## 1. Human-proof audit

The proof was written and committed before implementation. The audit independently checked the following numerical identities:

- \(2\binom93=168\);
- \(6\cdot104-20\cdot23=164\);
- the penalty table \((20,14,8,3,0,0,4,13,28,50)\);
- the only degree histograms under penalty four;
- triple-incidence totals 164, 167, and 168;
- exact marked-deficit totals 12, 3, and 0; and
- residue lower bounds 18, 15, and 12.

The central congruence was checked in both directions: a marked degree-four column contributes \(\binom32=3\), and a marked degree-five column contributes \(\binom42=6\), both zero modulo three. The exceptional marked contributions are 1 for degree three and 10 for degree six, yielding residue one inside either exceptional support and residue two outside.

No hidden existence assumption is used in passing from a denser matrix to weight 104: changing ones to zero cannot create an all-one submatrix.

## 2. Witness audit

Two independently implemented algorithms accept the stored matrix.

- The package verifier checks all 84 row triples and finds at most two common columns.
- The standalone script imports no package code and checks all 148,764 row/column triple pairs.

Negative tests include:

- wrong row count;
- wrong expected weight;
- a non-Boolean in-memory entry;
- CSV spellings `2`, `1.0`, `+1`, a space-prefixed one, an empty field, and `true`;
- a deliberately forced all-one \(3\times3\) block; and
- every zero-to-one extension of the 103-one witness.

Every one-bit extension is rejected with an actual forbidden submatrix, not merely a weight mismatch. This also checks that the construction is maximal under adding a single one.

## 3. Exact-certificate audit

The checker independently enumerates degree histograms rather than iterating over the certificate's claimed list. It rejects representative mutations of:

- the target weight;
- one penalty value;
- a deleted degree case;
- a degree count;
- a triple-incidence total;
- a row residue;
- a claimed lower bound;
- an aggregate cut; and
- the conclusion string.

The enumeration uses only nonnegative integer arithmetic and produces exactly three profiles. Category sizes are derived from the exceptional degree, so a certificate cannot choose how many rows are “inside” the exceptional column.

## 4. Encoding audit

The sequential threshold circuit was checked by a separate DPLL implementation on every assignment of one through six base variables, every possible bound, both positive and signed literals, and every exact target. The direct \(K_{3,3}\) clauses were compared with an independently constructed set in a smaller model.

The known value \(Z(3,4,3,3)=10\) was established by direct enumeration of all \(2^{12}\) matrices. CaDiCaL 3.0.0 then reported SAT at weight 10 and UNSAT at weight 11 for generated CNFs.

Thirty seeded 5-by-6 matrices were fixed cell by cell. Direct semantics, CaDiCaL, and the column-support evaluator agreed on all 30. The sample includes both valid and invalid matrices. The seed and per-case outcomes are preserved in [`audit/model_validation.json`](../audit/model_validation.json).

The stored target models regenerate byte-for-byte. GLPK 5.0 parses the column MIP with the expected dimensions. The repository audit parses every DIMACS clause independently, checks header counts and variable ranges, and compares the first 148,764 cell clauses against the lexicographically expected forbidden submatrices.

## 5. Proof-trace audit

`drat-trim` accepts each of the three DRAT files, and `lrat-check` accepts each of the three LRAT files. The recorded report is [`audit/certificate_replay.json`](../audit/certificate_replay.json).

The audit found no basis for describing these traces as a proof of the raw cell CNF, so the documentation does not do so. They replay only the terminal aggregate contradictions. The JSON certificate and its checker are the bridge from the mathematical problem to those endpoints.

## 6. Lean audit

The Lean project contains no `sorry`, `admit`, or declared project axiom. It has no Mathlib or third-party dependency.

An early audit build used `native_decide` for two tiny finite computations. `#print axioms` revealed the generated native-evaluation trust axiom, even though the build was green. That implementation was rejected and replaced with kernel `decide`.

The final axiom report is:

- `penalty_eq_formula`: no axioms;
- `penalty_table`: no axioms;
- `penalty_budget_structure`: `propext`, `Classical.choice`, `Quot.sound`;
- `classify_degree_profile`: the same standard Lean axioms; and
- all three deficit contradictions: `propext`, `Quot.sound`.

These are the standard dependencies of Lean's `omega` tactic, not project-added assumptions. [`lean/AxiomAudit.lean`](../lean/AxiomAudit.lean) reproduces the report.

The audit also rejects a broader formalization claim: the combinatorial translation and witness are not represented in Lean. Both the README and Lean documentation state that limitation prominently.

## 7. Literature audit

The three table-level claims most relevant to the previous one-edge gap were checked against rendered primary sources, not search snippets:

- Tan's \(z_3(9,23)=104\) entry is not marked exact;
- Davies--Gill--Horsley do not list an improvement for this cell; and
- Bhan--Nobili--Langer display upper 104 over lower 103 without a tightness mark.

The search included exact parameter variants, paper titles, DOI and arXiv records, and forward-looking queries through 2026-07-04. No earlier closure was located. The repository describes this as a dated search conclusion and explicitly invites earlier references.

## 8. Portability and provenance audit

The core package uses Python's standard library and supports Python 3.9 onward. The first test run exposed two features that were not available in the actual Python 3.9 interpreter (`type | type` at runtime and `int.bit_count`); both were removed, and the declared compatibility floor was corrected.

All repository text is scanned for prohibited private-workspace markers and absolute user paths. Symlinks are rejected. Stored generator outputs contain no timestamps, hostnames, or resolved paths. Random validation is pinned to seed `20260704`.

The root Git commit contains only the human proof. This makes the requested proof-before-code ordering independently inspectable rather than merely asserted in prose.

## 9. Known limitations

The audit does not remove the need for external review. In particular:

- no independent mathematician has yet signed off on the proof;
- the Lean development is an arithmetic formalization, not an end-to-end theorem;
- no monolithic LRAT trace is provided for the raw 9-by-23 cell model;
- the DGH formula transcription was checked by exact tests and source comparison but is diagnostic, not part of the theorem;
- the finite literature search cannot establish absolute priority; and
- external replay tools add their own trusted implementations.

These limitations do not appear to leave a gap in the elementary proof, but they define the claims that this repository does and does not make.

## Audit verdict

Within the declared scope, all known positive, negative, mutation, regeneration, parser, external-replay, and formal-axiom checks pass. No unresolved mathematical or reproducibility defect is presently known. The result remains appropriately labeled as awaiting independent expert review.
