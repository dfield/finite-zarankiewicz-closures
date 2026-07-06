# Adversarial audit

## Audit objective

This audit asks how any of the six claimed exact values or the additional $Z(13,23)$ bound could be wrong even if ordinary happy-path tests pass. It treats prose, data, generators, certificates, formal code, and literature claims as separate attack surfaces.

The original audit was completed on 2026-07-04 and extended for the two later closures on 2026-07-06. “Full” here means every evidence layer shipped by the repository was placed in scope; it does not mean the work has received external peer review or that every possible implementation has been verified.

## Threat model

The principal failure modes considered were:

1. an invalid 103-one matrix is accepted because of a parser or indexing bug;
2. the degree-case certificate omits a profile or trusts a forged arithmetic field;
3. the SAT and MIP generators encode a different problem;
4. a proof trace is malformed or is presented as covering a broader reduction than it does;
5. Lean succeeds because of an admission, custom axiom, or inaccurately stated boundary;
6. a literature table is misread as exact;
7. generated evidence depends on a local path, timestamp, random seed, or unavailable private source; or
8. documentation silently upgrades corroborating computation into a theorem's logical basis; or
9. the extended table is mistranscribed, a deletion bound is rounded incorrectly, or a finite profile/orbit is omitted from the $(10,22)$ or $(12,23)$ certificate.

## 1. Original human-proof audit

The proof was written and committed before implementation. The audit independently checked the following numerical identities:

- $2\binom93=168$;
- $6\cdot104-20\cdot23=164$;
- the penalty table $(20,14,8,3,0,0,4,13,28,50)$;
- the only degree histograms under penalty four;
- triple-incidence totals 164, 167, and 168;
- exact marked-deficit totals 12, 3, and 0; and
- residue lower bounds 18, 15, and 12.

The central congruence was checked in both directions: a marked degree-four column contributes $\binom32=3$, and a marked degree-five column contributes $\binom42=6$, both zero modulo three. The exceptional marked contributions are 1 for degree three and 10 for degree six, yielding residue one inside either exceptional support and residue two outside.

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
- a deliberately forced all-one $3\times3$ block; and
- every zero-to-one extension of the 103-one witness.

Every one-bit extension is rejected with an actual forbidden submatrix, not merely a weight mismatch. This also checks that the construction is maximal under adding a single one.

The five additional matrices are checked twice: the package verifier recomputes row-triple capacities, while the standalone verifier scans every candidate submatrix without importing project code. The two later witnesses add scans of 159,885 candidates for $11\times19$ and 389,620 candidates for $12\times23$.

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

The extended certificate independently enumerates the four possible degree profiles at 111 ones for a 10-by-22 matrix. Its two finite residue searches cover:

- every intersection size $2,3,4,5,6$ for the two degree-six columns and all 210 degree-four columns in profile $4^1 5^{19}6^2$; and
- 77 row-symmetry orbits for three degree-six columns, with all 22,155 unordered degree-four multisets in each orbit, in profile $4^2 5^{17}6^3$.

The minimum residue sums are recomputed rather than trusted from JSON. The other two profiles are rejected by transparent divisibility and symmetric-difference arguments.

Six case-specific wrapper certificates bind those upper-bound checks to the exact witness file, dimensions, weight, row and column sums, exhaustive row-triple result, and SHA-256 digest. The checker regenerates all fields, and mutation tests require an altered exact value to be rejected for every case.

The $Z(12,23)$ certificate separately classifies the unique profile at 136 and all five profiles at 135. It recomputes the pair equation, all residue budgets, and the minimum value 25 in the sole row-type enumeration. The $Z(13,23)$ report independently classifies the three profiles at 145 and checks each marked-row deficit contradiction.

## 4. Encoding audit

The sequential threshold circuit was checked by a separate DPLL implementation on every assignment of one through six base variables, every possible bound, both positive and signed literals, and every exact target. The direct $K_{3,3}$ clauses were compared with an independently constructed set in a smaller model.

The known value $Z(3,4,3,3)=10$ was established by direct enumeration of all $2^{12}$ matrices. CaDiCaL 3.0.0 then reported SAT at weight 10 and UNSAT at weight 11 for generated CNFs.

Thirty seeded 5-by-6 matrices were fixed cell by cell. Direct semantics, CaDiCaL, and the column-support evaluator agreed on all 30. The sample includes both valid and invalid matrices. The seed and per-case outcomes are preserved in [`audit/model_validation.json`](../audit/model_validation.json).

All twelve stored target models regenerate byte-for-byte. The repository audit parses every DIMACS clause independently, checks header counts and variable ranges, and compares every forbidden-clause prefix against a separately generated lexicographic sequence. It also checks each LP's support-variable count, row-triple count, terminator, and hash.

## 5. Proof-trace audit

`drat-trim` accepts each of the three DRAT files, and `lrat-check` accepts each of the three LRAT files. The recorded report is [`audit/certificate_replay.json`](../audit/certificate_replay.json).

The audit found no basis for describing these traces as a proof of the raw cell CNF, so the documentation does not do so. They replay only the terminal aggregate contradictions. The JSON certificate and its checker are the bridge from the mathematical problem to those endpoints.

## 6. Lean audit

The Lean project contains no `sorry`, `admit`, or declared project axiom. It has no Mathlib or third-party dependency.

An early audit build used `native_decide` for two tiny finite computations. `#print axioms` revealed the generated native-evaluation trust axiom, even though the build was green. That implementation was rejected and replaced with kernel `decide`.

The original marked-row axiom report is:

- `penalty_eq_formula`: no axioms;
- `penalty_table`: no axioms;
- `penalty_budget_structure`: `propext`, `Classical.choice`, `Quot.sound`;
- `classify_degree_profile`: the same standard Lean axioms; and
- all three deficit contradictions: `propext`, `Quot.sound`.

These are the standard dependencies of Lean's `omega` tactic, not project-added assumptions. [`lean/AxiomAudit.lean`](../lean/AxiomAudit.lean) reproduces the report.

The additional Lean library checks the deletion chains, the $(10,22)$ certificate endpoints, the $(12,23)$ penalty tables and profile classifications at 136 and 135, its five terminal contradictions, and the $(13,23)$ profile/residue arithmetic. Its executable quotient, penalty, and minima facts use no axioms; its `omega` theorems report only the same standard Lean principles.

The audit also rejects a broader formalization claim: the combinatorial translations, deletion lemma, orbit enumeration, and witnesses are not represented in Lean. Both the README and Lean documentation state that limitation prominently.

## 7. Literature audit

The three table-level claims most relevant to the previous one-edge gap were checked against rendered primary sources, not search snippets:

- Tan's $z_3(9,23)=104$ entry is not marked exact;
- Davies--Gill--Horsley do not list an improvement for this cell; and
- Bhan--Nobili--Langer display upper 104 over lower 103 without a tightness mark.

The search included exact parameter variants, paper titles, DOI and arXiv records, and forward-looking queries through 2026-07-04. No earlier closure was located. The repository describes this as a dated search conclusion and explicitly invites earlier references.

The extended audit transcribes all 44 cells that the paper identifies as previously open and checks the set cardinality directly. After the paper's three closures and this repository's six closures, set subtraction leaves 35 cells. The documentation expressly retains their open status.

## 8. Portability and provenance audit

The core package uses Python's standard library and supports Python 3.9 onward. The first test run exposed two features that were not available in the actual Python 3.9 interpreter (`type | type` at runtime and `int.bit_count`); both were removed, and the declared compatibility floor was corrected.

All repository text is scanned for prohibited private-workspace markers and absolute user paths. Symlinks are rejected. Stored generator outputs contain no timestamps, hostnames, or resolved paths. Random validation is pinned to seed `20260704`.

The root Git commit contains only the human proof. This makes the requested proof-before-code ordering independently inspectable rather than merely asserted in prose.

## 9. Known limitations

The audit does not remove the need for external review. In particular:

- no independent mathematician has yet signed off on the proofs;
- the Lean development covers the arithmetic kernels for all six exact results and the additional bound, not end-to-end matrix theorems;
- no monolithic LRAT trace is provided for the raw 9-by-23 cell model;
- the extended finite enumerations are checked by standard-library code; Lean checks their recorded minima and consequences but does not rerun the orbit or row-type searches;
- the DGH formula transcription was checked by exact tests and source comparison but is diagnostic, not part of the theorem;
- the finite literature search cannot establish absolute priority; and
- external replay tools add their own trusted implementations.

These limitations do not presently reveal a gap in the claimed proofs, but they define the claims that this repository does and does not make.

## Audit verdict

Within the declared scope, all known positive, negative, mutation, regeneration, parser, external-replay, and formal-axiom checks pass. No unresolved mathematical or reproducibility defect is presently known. The result remains appropriately labeled as awaiting independent expert review.
