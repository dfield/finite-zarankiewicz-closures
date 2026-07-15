# Methods

## 1. Proof layers

The repository keeps five evidence layers distinct:

1. human-readable combinatorial arguments;
2. explicit lower-bound matrices;
3. standard-library arithmetic and finite-enumeration checkers;
4. solver-generated certificates checked by independent proof checkers; and
5. Lean formalization of the certificate-free combinatorial kernels.

No generic solver verdict, model file, checkpoint, or cloud-job status is treated as a theorem. Each exact value has a checked witness and a case-specific upper-bound certificate.

## 2. Matrix model and witness checks

A Boolean $m\times n$ matrix is identified with a bipartite graph. It is $K_{3,3}$-free exactly when every three rows have at most two common one-columns. For a matrix with row supports $R_i$, the package verifier checks

$$
|R_a\cap R_b\cap R_c|\le2
$$

for every row triple. A second standalone implementation scans every choice of three rows and three columns directly. Raw CSV bytes, dimensions, weight, row sums, column sums, and SHA-256 digest are recorded in each case certificate.

## 3. Arithmetic upper-bound mechanisms

The certificate-free cases use three recurring methods.

### Triple capacity

If column $j$ has support $E_j$ and degree $d_j$, then

$$
\sum_j\binom{d_j}{3}\le2\binom m3.
$$

Convex integer penalties classify the possible degree histograms near a proposed optimum.

### Deficits and residues

Writing $\lambda_T$ for the number of columns through a row triple, the unused capacity $2-\lambda_T$ can be summed over triples containing a marked row or pair. Small congruences force a residue total larger than the available deficit budget. This underlies the $Z(9,23)$, $Z(10,22)$, $Z(12,23)$, and $Z(13,23)$ arguments.

### Vertex deletion

If $Z(m-1,n,3,3)\le B$, averaging row degrees gives

$$
Z(m,n,3,3)\le\left\lfloor\frac{mB}{m-1}\right\rfloor.
$$

The symmetric column version is used as well. This closes $Z(10,21)$, $Z(11,19)$, $Z(11,20)$, and—after the certified $Z(10,23)$ bound—$Z(11,23)$.

## 4. Case-certificate regeneration

[`case_certificates.py`](../src/finite_zarankiewicz_closures/case_certificates.py) regenerates one standalone JSON certificate for each of the eight exact values. Stored inputs are treated as untrusted: witness invariants and upper-bound data are recomputed and required to match semantically, including nested reports and artifact hashes.

```bash
python3 scripts/check_case_certificates.py --check
```

Representative mutation tests alter theorem scope, arithmetic data, toolchain identities, cover counts, proof-index hashes, release-part metadata, and witness values. Each mutation must be rejected.

## 5. $Z(10,23)$ arithmetic reduction

At 113 ones, the triple-capacity equations admit exactly 25 degree profiles. Deletion eliminates nine, row-deficit residues eliminate two, and a pair-residue enumeration eliminates one. The remaining thirteen are exact finite decision instances.

The profile formulas fix column degrees, enforce the row-triple capacities, add sound lexicographic symmetry breaking, and require minimum row degree ten. Formula hashes and DIMACS dimensions are bound in [`z10_23_sat.json`](../certificates/z10_23_sat.json).

## 6. DRAT/LRAT certificate path

Ten profiles have direct CaDiCaL 3.0.0 DRAT traces. One additional profile uses a canonical row-stabilizer cube cover with 17,170 leaves. For each direct or leaf proof:

1. `drat-trim` checks the DRAT derivation and emits LRAT;
2. `lrat-check` independently checks the LRAT; and
3. the proof or archive member is bound by exact name, size, and SHA-256 digest.

The cube verifier independently regenerates the canonical cover and streams the catalog, proof index, and archive in lockstep. It rejects missing, duplicate, reordered, noncanonical, or extra leaves.

## 7. Exact SCIP/VIPR certificate path

Two profiles use exact integer programming because their direct SAT refinements remained expensive. Row symmetry reduces them to finite orbit covers:

| Profile | Raw states | Orbits |
|---|---:|---:|
| $3^1 4^4 5^{14}6^4$ | 295,001 | 209 |
| $3^1 4^3 5^{16}6^3$ | 950,250 | 236 |

The verifier independently reconstructs both raw state spaces, group actions, orbit representatives, and orbit sizes. It then regenerates the OPB formula for every representative.

SCIP 10.0.3 ran in exact mode with presolve, conflict analysis, and—on the final residual stage—separation disabled. Only complete certificates accepted by the unmodified `viprchk` source are retained. The verifier rejects weak/incomplete proof features and parses the model embedded in each VIPR certificate, comparing every coefficient, sense, and right-hand side with the regenerated OPB. This model binding is essential: a valid infeasibility proof for a different program is not accepted.

The checked-in aggregate manifests contain leaf-level formula and certificate hashes; deterministic release sidecars bind the split proof streams published outside Git.

## 8. Models versus certificates

The generic excluded-target CNFs and column-support LPs in [`models/`](../models/) are regenerated byte-for-byte. They are useful for encoding validation and independent experiments, but do not establish unsatisfiability. The $Z(10,23)$ theorem uses the stronger profile-specific formulas and their proof family.

## 9. Lean boundary

The Lean project formalizes Boolean matrices, witnesses, triple counting, deficit arithmetic, and deletion lemmas. It currently provides unconditional end-to-end exact theorems for $Z(9,23)$, $Z(10,22)$, and $Z(12,23)$, plus an unconditional upper theorem for $Z(13,23)$. The deletion-derived results expose their historical starting bounds as hypotheses.

Lean does not replay DRAT/LRAT or VIPR and does not contain a certificate-free proof of $Z(10,23)=112$. The published equality therefore rests on the external certificate chain described above, not on a hidden Lean axiom. The source tree contains no `sorry`, `admit`, project `axiom`, or `native_decide`.

## 10. Reproducibility

```bash
make verify
make z10-23-certificate
```

The first command checks the complete local publication artifact. The second isolates the deep $Z(10,23)$ integrity check. Full external-checker replay requires the release assets and pinned proof tools described in [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).
