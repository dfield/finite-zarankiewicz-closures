# Adversarial audit

## Audit objective

This audit asks how any of the eight exact values, the $Z(13,23)$ upper bound, or their computational evidence could be wrong even if ordinary happy-path tests pass. Prose, data, generators, covers, certificates, release packaging, formal code, and literature claims are separate attack surfaces.

The original audit began on 2026-07-04. On 2026-07-13 it correctly demoted $Z(10,23)$ and $Z(11,23)$ because the proof family was incomplete. The 2026-07-14 extension promotes them only after completing, aggregating, and independently checking the missing certificate families.

## Threat model

Principal failure modes include:

1. a malformed or incorrectly parsed witness;
2. an omitted degree profile or incorrect arithmetic residue bound;
3. a CNF/OPB encoding a different problem;
4. an incomplete or overlapping symmetry cover;
5. a valid proof paired with the wrong formula;
6. a corrupted, reordered, or missing release part or archive member;
7. acceptance of weak/incomplete VIPR derivations;
8. a Lean admission, project axiom, or overstated formalization boundary;
9. a literature interval misread as exact; or
10. operational solver output silently substituted for a proof certificate.

## 1. Witness audit

Every stored matrix is checked by two independent algorithms. The package verifier intersects row supports for every row triple. The standalone verifier imports no project module and examines every candidate $3\times3$ submatrix.

Negative tests cover malformed dimensions and CSV tokens, non-Boolean values, wrong weights, a forced forbidden block, and every one-bit extension of the original 103-one witness. Case certificates bind raw bytes, dimensions, weight, row and column sums, maximum triple intersection, and SHA-256 digest.

## 2. Arithmetic-certificate audit

Degree profiles are independently enumerated from the count, total-degree, and triple-capacity equations rather than read from a claimed list. Stored arithmetic reports are regenerated and compared semantically.

For $Z(10,23)$, two independent enumerators agree on all 25 profiles at 113 ones and their partition into nine deletion cases, three deficit cases, and thirteen certificate cases. The pair-residue elimination independently regenerates 1,577 exceptional-column configurations, 1,380 legal configurations, and minimum residue sum 39.

The $Z(10,22)$, $Z(12,23)$, and $Z(13,23)$ checkers likewise regenerate every finite profile and residue minimum. Mutation tests alter penalty values, profiles, budgets, aggregate cuts, theorem targets, and nested reports; each alteration must be rejected.

## 3. Encoding audit

The sequential threshold circuit was checked by an independent DPLL implementation on every assignment of up to six base variables, every bound, and signed literals. The direct forbidden-submatrix clause sequence is independently reconstructed. A known small case, $Z(3,4,3,3)=10$, agrees with direct enumeration and solver results.

Thirty seeded $5\times6$ matrices were fixed cell by cell; direct semantics, CaDiCaL, and the column-support formulation agreed on all cases. All sixteen generic target models regenerate byte-for-byte, and the repository audit checks DIMACS headers, literal ranges, exact forbidden-clause prefixes, LP support counts, triple constraints, terminators, and hashes.

For $Z(10,23)$, the theorem uses profile-specific formulas rather than assuming the generic models are UNSAT.

## 4. DRAT/LRAT audit

Ten $Z(10,23)$ profiles have direct DRAT traces. The eleventh SAT-based profile has a complete 17,170-leaf row-stabilizer cover.

The integrity checker:

- independently regenerates the canonical cube cover;
- streams catalog and proof index in lockstep;
- requires one canonical archive member per leaf;
- checks member sizes and SHA-256 hashes; and
- rejects missing, duplicate, extra, reordered, or noncanonical entries.

During production, every accepted proof was replayed by `drat-trim`, converted to LRAT, and checked by `lrat-check`. The public replay script repeats that process from release assets. A proof index status without the corresponding hash-bound proof body is insufficient.

## 5. VIPR orbit-cover audit

Two residual profiles use exact SCIP/VIPR certificates. The repository independently reconstructs:

- 295,001 raw states and 209 orbits for $3^1 4^4 5^{14}6^4$;
- 950,250 raw states and 236 orbits for $3^1 4^3 5^{16}6^3$; and
- every representative's exact OPB formula and indexed formula hash.

This census does not trust the production catalog. It applies the relevant row group actions, recomputes canonical signatures and orbit sizes, and requires the raw-state and orbit totals to match.

Each compressed VIPR certificate is checked at three levels:

1. archive member name, byte length, and SHA-256 digest;
2. coefficient-for-coefficient equality between its embedded model and the independently regenerated OPB; and
3. successful exact infeasibility verification by the unmodified `viprchk` checker.

The aggregate verifier also rejects `AggrRow_`, `lin weak`, and `lin incomplete`. Thirteen first-pass profile-B certificates requiring completion were superseded by a residual run with separation disabled; only the fully checked replacements enter the final aggregate.

Representative mutation tests change orbit data, a formula coefficient, manifest hashes, tool identities, checker status, release order, and aggregate counts. All are rejected.

## 6. Release and provenance audit

Large proof bodies are split below GitHub's per-file limit. Checked-in sidecars bind each part name, size, and SHA-256 digest, plus the reassembled stream size and hash. The fetcher verifies every part before reuse. Stream readers reject unsafe paths, links, nonregular members, extra content, and order mismatches.

AWS stage IDs, logs, checkpoints, pod states, and S3 object presence are provenance only. The theorem-facing master manifest contains the exact formulas, covers, proof indexes, checker identities, aggregate manifests, and release descriptors. The historical untraced sweep remains explicitly non-load-bearing.

## 7. Lean audit

The Lean tree contains no `sorry`, `admit`, project `axiom`, or `native_decide`. `AxiomAudit.lean` reports only standard Lean/Mathlib dependencies such as `propext`, `Classical.choice`, and `Quot.sound`.

Lean proves unconditional end-to-end results for $Z(9,23)$, $Z(10,22)$, and $Z(12,23)$ and the upper bound for $Z(13,23)$. Deletion-derived theorem types expose their historical premises. Lean does not replay DRAT/LRAT or VIPR and is not described as a certificate-free proof of $Z(10,23)$.

## 8. Literature and frontier audit

The 44-cell source boundary was transcribed from Bhan--Nobili--Langer Figure 2 and its cardinality is checked. Combining the paper's three exact cells with the repository's eight gives 11 exact cells and 33 remaining parameters. The literature review states its search cutoff and cannot rule out unpublished, unindexed, or later work.

## 9. Portability audit

The local integrity gate uses the Python standard library and is tested on Python 3.9 and 3.14. Repository text is scanned for private workspace paths; symlinks and files over GitHub's 100 MB Git limit are rejected. Deterministic theorem artifacts contain no hostname, temporary path, or random solver verdict.

The proof-first root commit contains only [`PROOF.md`](PROOF.md), making the original proof-before-code ordering independently inspectable.

## 10. Known limitations

- Independent expert and peer review are still required.
- The full $Z(10,23)$ semantic replay downloads approximately 25.3 GB and trusts the pinned external checker implementations.
- There is no certificate-free Lean proof of $Z(10,23)=112$.
- Some deletion closures depend on historical exact bounds exposed as Lean hypotheses.
- The finite literature search cannot establish absolute priority.
- Diagnostic generic models and the DGH relaxation are not theorem certificates.

## Audit verdict

Within the declared scope, eight exact-value certificates, the frontier certificate, all witnesses, deterministic regenerations, cover-completeness checks, formula/model bindings, release hashes, mutation checks, and formal-axiom checks pass. The former $Z(10,23)$ gap is closed by a complete replayable proof family rather than by solver status, and $Z(11,23)=123$ follows by a checked deletion argument. All claims remain subject to independent review.
