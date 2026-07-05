> **Attribution:** The proofs, formal arithmetic, verification code, and repository were produced by **GPT 5.6-Sol**. This is a research artifact awaiting independent expert review, not a peer-reviewed publication.

# Four exact finite Zarankiewicz numbers

This repository presents reproducible proofs of four exact values:

$$
\begin{aligned}
Z(9,23,3,3)&=103, & Z(10,21,3,3)&=106,\\
Z(10,22,3,3)&=110, & Z(11,20,3,3)&=111.
\end{aligned}
$$

Here $Z(m,n,3,3)$ is the largest number of ones in an $m\times n$ zero-one matrix with no all-one $3\times3$ submatrix. Each equality comes with an explicit extremal matrix and a reproducible upper-bound certificate.

The four upper bounds use three complementary mechanisms: a marked-row deficit argument for $(9,23)$, vertex-deletion bounds for $(10,21)$ and $(11,20)$, and an exhaustive pair-deficit certificate for $(10,22)$. Computation checks the witnesses and finite arithmetic; no claimed equality rests on an opaque solver verdict.

## Why these cases mattered

The Zarankiewicz problem is a classical question in extremal combinatorics. Reading a Boolean matrix as the adjacency matrix of a bipartite graph turns an all-one $3\times3$ submatrix into a copy of the complete bipartite graph $K_{3,3}$.

The 2026 table of Jay Bhan, Nicole Nobili, and Patrick Langer left these four cells as intervals rather than exact values:

| Cell | Previously reported interval | Closure in this repository |
|---|---:|---|
| $Z(9,23,3,3)$ | $103\text{--}104$ | marked-row deficits exclude 104 |
| $Z(10,21,3,3)$ | $106\text{--}108$ | deletion from $Z(9,21,3,3)=96$ gives the matching upper bound |
| $Z(10,22,3,3)$ | $110\text{--}111$ | pair-deficit enumeration excludes 111 |
| $Z(11,20,3,3)$ | $111\text{--}112$ | two deletion steps from $Z(11,18,3,3)=101$ give the matching upper bound |

Credit for the four previously public lower bounds belongs to Bhan--Nobili--Langer. The contribution presented here is to prove matching upper bounds and independently verify explicit witnesses. Together with the three cells made exact in their paper, these results close seven of that paper's 44 open cells; **37 remain open**. See the [literature review](docs/LITERATURE_REVIEW.md) for the complete attribution chain and the [extended-results proof](docs/EXTENDED_RESULTS.md) for the precise claim boundary.

## The $Z(9,23,3,3)$ proof idea

Treat each column as the set $E_j$ of rows containing a one, and let $d_j=|E_j|$. Every triple of rows may occur together in at most two columns; otherwise those rows and three such columns form a forbidden $3\times3$ block. Therefore

$$
\sum_j\binom{d_j}{3}\le2\binom93=168.
$$

For a hypothetical 104-one matrix, introduce

$$
p(d)=\binom d3-6d+20.
$$

Its values for $d=0,\ldots,9$ are

$$
(20,14,8,3,0,0,4,13,28,50).
$$

The capacity inequality implies $\sum_j p(d_j)\le4$. This leaves only three possible multisets of column degrees:

$$
4^{11}5^{12},\qquad 3^1 4^9 5^{13},\qquad 4^{12}5^{10}6^1.
$$

Now mark one row and count unused row-triple capacity through that row. Contributions from degree-four and degree-five columns are multiples of three. In the three cases above, the exact total deficits are respectively 12, 3, and 0, but their forced residue classes give lower bounds 18, 15, and 12. Each case is contradictory.

That is the entire upper-bound mechanism. The [full proof](docs/PROOF.md) supplies every definition and double count.

## The other three closures

Propagating vertex-deletion bounds through Bhan--Nobili--Langer's table and applying a new pair-deficit certificate gives the other three values:

$$
Z(10,21,3,3)=106,
\qquad Z(10,22,3,3)=110,
\qquad Z(11,20,3,3)=111.
$$

The first and third follow from the elementary deletion lemma. The middle value has an explicit 110-one matrix and a standard-library enumeration excluding all four possible 111-one degree profiles. See [the extended-results proof and precise claim boundary](docs/EXTENDED_RESULTS.md).

## Evidence and trust boundaries

The logical role of computation differs across the four results:

| Result or layer | What it establishes | Artifact |
|---|---|---|
| Human upper-bound proof | Excludes 104 ones for $(9,23)$ | [`docs/PROOF.md`](docs/PROOF.md) |
| Deletion arguments | Give matching upper bounds for $(10,21)$ and $(11,20)$ | [`docs/EXTENDED_RESULTS.md`](docs/EXTENDED_RESULTS.md) |
| Computer-assisted finite proof | Exhaustively excludes the four possible 111-one degree profiles for $(10,22)$ | [`docs/EXTENDED_RESULTS.md`](docs/EXTENDED_RESULTS.md), [`src/finite_zarankiewicz_closures/extended.py`](src/finite_zarankiewicz_closures/extended.py) |
| Explicit constructions | Supply all four matching lower bounds | [`data/`](data/) |
| Independent witness checks | Verify every stored matrix by row-triple capacity and direct $3\times3$ scans | [`scripts/`](scripts/) |
| Exact arithmetic certificate | Recomputes every degree profile and contradiction for $(9,23)$ | [`certificates/degree_deficit.json`](certificates/degree_deficit.json) |
| Lean | Kernel-checks the $(9,23)$ penalty table, degree classification, and terminal residue contradictions | [`lean/`](lean/) |
| Decision models | Reconstruct the 207-cell SAT and 512-column-type MIP formulations for $(9,23)$ | [`models/`](models/) |
| Standard proof traces | Replay the three terminal $(9,23)$ integer contradictions in DRAT and LRAT | [`certificates/`](certificates/) |
| Adversarial audit | Records mutation tests, independent tools, trust assumptions, and limitations | [`docs/ADVERSARIAL_AUDIT.md`](docs/ADVERSARIAL_AUDIT.md) |

Three boundaries are important:

- The $(9,23)$ upper bound is entirely human-readable; its computation is corroborating rather than logically necessary.
- The $(10,22)$ upper bound is computer-assisted: its exhaustive standard-library enumeration is a proof component. It is not formalized in Lean and is not presented as a solver certificate.
- The Lean development formalizes only the $(9,23)$ arithmetic kernel, not the complete matrix-to-counting translation. The DRAT/LRAT files likewise certify only its three terminal aggregations, not the full 8.2 MB cell CNF.

## Quick verification

The core audit needs only Python 3.9 or later and the standard library:

```sh
make test
make witness
make certificate
make extended
make models
```

Or run the consolidated gate:

```sh
make verify
```

Expected headline results are:

- 23 Python tests pass;
- the two original witness verifiers accept the 103-one matrix, and the extended verifier accepts all three additional matrices;
- the original certificate reports `VERIFIED` with three profiles, while the extended report is byte-identical and recomputes four profiles at 111 ones;
- both generated decision models are byte-for-byte identical to the stored artifacts; and
- the repository audit reports `VERIFIED`.

### Lean

Lean 4.29.0 is pinned inside the subproject and no external Lean package is required:

```sh
cd lean
lake build
lake env lean AxiomAudit.lean
```

The axiom report is discussed in the [adversarial audit](docs/ADVERSARIAL_AUDIT.md). The executable penalty computations use no axioms; the `omega` proofs use Lean's standard `propext`, `Classical.choice`, and `Quot.sound` principles and no project-specific axiom.

### Optional external replays

If CaDiCaL, GLPK, `drat-trim`, and `lrat-check` are installed:

```sh
python3 scripts/validate_models.py
glpsol --lp models/column_types_9x23_exact_104.lp --check
python3 scripts/replay_certificates.py
```

The versions used for the recorded audit were CaDiCaL 3.0.0 and GLPK 5.0. The DRAT and LRAT checkers are identified by their conventional command names because their binaries do not expose stable semantic version strings.

## What each computational artifact means

The exact decision problem has two formulations.

1. **Cell SAT.** There are 207 cell variables. Every choice of three rows and three columns contributes a nine-literal clause forbidding that all-one submatrix, and a fully defined threshold circuit imposes exactly 104 ones.
2. **Column-type MIP.** For each support $S\subseteq[9]$, an integer $x_S$ counts columns having exactly that support. The model fixes 23 columns and 104 ones and requires every row triple to occur in at most two columns.

Testing exactly 104 is enough: if a denser $K_{3,3}$-free matrix existed, deleting ones would preserve the forbidden-submatrix condition until exactly 104 remained.

The stored models are deterministic outputs. They are included for transparency and regression checking, not as the logical basis of the upper bound. The [methods document](docs/METHODS.md) specifies the encodings and maps each program to the corresponding proof step.

## Repository map

```text
.
├── README.md                    introduction and result status
├── docs/
│   ├── PROOF.md                 human-readable proof, committed before code
│   ├── EXTENDED_RESULTS.md      three further closures and open frontier
│   ├── LITERATURE_REVIEW.md     prior work and dated status search
│   ├── METHODS.md               models, certificates, and proof/code map
│   ├── ADVERSARIAL_AUDIT.md     attack surface, tests, findings, limits
│   └── REPRODUCIBILITY.md       commands and expected outputs
├── data/                        explicit matrices for all claimed lower bounds
├── certificates/                exact JSON reduction and terminal traces
├── models/                      deterministic SAT/MIP artifacts
├── analysis/                    exact boundaries, kernel catalog, and table frontier
├── lean/                        formal arithmetic subproject
├── src/finite_zarankiewicz_closures/ documented standard-library package
├── scripts/                     small command-line entry points
├── tests/                       adversarial and semantic regression tests
└── audit/                       recorded external-tool reports
```

The Git history itself records the proof-first workflow: the root commit contains only [`docs/PROOF.md`](docs/PROOF.md), and implementation begins later.

## Reproducibility and review

All core generators are deterministic. The randomized model-validation sample uses the fixed seed `20260704`. Stored outputs contain no machine-specific paths or timestamps. Artifact hashes are collected in [`artifacts.sha256`](artifacts.sha256).

Reviewers are encouraged to begin with the six-page-equivalent [$(9,23)$ proof](docs/PROOF.md) and the [three further closures](docs/EXTENDED_RESULTS.md), then run both certificate paths and all witness verifiers. The SAT/MIP and proof-trace layers are intentionally secondary. A suggested review sequence and issue-reporting guidance appear in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Status and humility

The repository's internal checks support all four exact values, and no mathematical gap is presently known. Nevertheless:

- this work has not yet been independently peer reviewed;
- the literature search cannot exclude unpublished or poorly indexed prior work;
- the novelty assessment is therefore dated and provisional; and
- any correction, simplification, or earlier reference is welcome.

The exact claims should be judged from the stated proof and trust boundaries, not from the amount of automation surrounding them.

## Citation and license

Machine-readable citation metadata is in [`CITATION.cff`](CITATION.cff), and full prior-work metadata is in [`references.bib`](references.bib). Code, proof text, data, and generated artifacts are released under the [MIT License](LICENSE).
