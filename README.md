> **Attribution:** The original four closures, formal arithmetic, verification code, and repository were produced by **GPT 5.6-Sol**. The $Z(11,19)$ witness, $Z(12,23)$ proof and witness, and $Z(13,23)$ bound were produced by **Claude (Anthropic)**. The traced $Z(10,23)$ certification and its $Z(11,23)$ consequence were completed with **OpenAI Codex**. All additions were subsequently audited and integrated with the repository's uniform verification layers. This is a research artifact awaiting independent expert review, not a peer-reviewed publication.

# Eight exact finite Zarankiewicz numbers

This repository presents reproducible proofs of eight exact values:

$$
\begin{aligned}
Z(9,23,3,3)&=103, & Z(10,21,3,3)&=106,\\
Z(10,22,3,3)&=110, & Z(10,23,3,3)&=112,\\
Z(11,19,3,3)&=106, & Z(11,20,3,3)&=111,\\
Z(11,23,3,3)&=123, & Z(12,23,3,3)&=134.
\end{aligned}
$$

Here $Z(m,n,3,3)$ is the largest number of ones in an $m\times n$ zero-one matrix with no all-one $3\times3$ submatrix. Each equality comes with an explicit extremal matrix and a reproducible upper-bound certificate.

The eight upper bounds use complementary mechanisms: a marked-row deficit argument for $(9,23)$; vertex-deletion bounds for $(10,21)$, $(11,19)$, $(11,20)$, and $(11,23)$; an exhaustive pair-deficit certificate for $(10,22)$; a profile reduction plus ten direct proof cores and three complete proof-backed cube covers for $(10,23)$; and a two-stage row/pair-deficit certificate for $(12,23)$. Every SAT leaf is independently replayed through DRAT and LRAT checking; no claimed equality rests on an opaque solver verdict.

## Why these cases mattered

The Zarankiewicz problem is a classical question in extremal combinatorics. Reading a Boolean matrix as the adjacency matrix of a bipartite graph turns an all-one $3\times3$ submatrix into a copy of the complete bipartite graph $K_{3,3}$.

The 2026 table of Jay Bhan, Nicole Nobili, and Patrick Langer left these eight cells as intervals rather than exact values:

| Cell | Previously reported interval | Closure in this repository |
|---|---:|---|
| $Z(9,23,3,3)$ | $103\text{--}104$ | marked-row deficits exclude 104 |
| $Z(10,21,3,3)$ | $106\text{--}108$ | deletion from $Z(9,21,3,3)=96$ gives the matching upper bound |
| $Z(10,22,3,3)$ | $110\text{--}111$ | pair-deficit enumeration excludes 111 |
| $Z(10,23,3,3)$ | $112\text{--}115$ | arithmetic reduction plus direct and complete-cover DRAT/LRAT certificates excludes 113 |
| $Z(11,19,3,3)$ | $102\text{--}108$ | deletion from $Z(11,18,3,3)=101$ plus a new 106-one witness |
| $Z(11,20,3,3)$ | $111\text{--}112$ | two deletion steps from $Z(11,18,3,3)=101$ give the matching upper bound |
| $Z(11,23,3,3)$ | $118\text{--}125$ | deletion from $Z(10,23,3,3)=112$ plus an explicit 123-one witness |
| $Z(12,23,3,3)$ | $125\text{--}136$ | two-stage deficit analysis excludes 136 and 135; a new witness has 134 ones |

Credit for the five previously public matching lower bounds belongs to Bhan--Nobili--Langer. The three later witnesses are explicit repository artifacts with their own attribution and exhaustive checks. Together with the three cells made exact in the paper, the eight repository closures settle eleven of the paper's 44 open cells; **33 remain open**. The same follow-up proves $Z(13,23,3,3)\le144$ and propagates improved bounds across the table. See the [literature review](docs/LITERATURE_REVIEW.md), [`NEW_BOUNDS.md`](docs/NEW_BOUNDS.md), and the case-specific proof dossiers.

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

## The other seven closures

Propagating vertex-deletion bounds through Bhan--Nobili--Langer's table and applying finite deficit and propositional certificates gives the other seven values:

$$
Z(10,21,3,3)=106,
\qquad Z(10,22,3,3)=110,
\qquad Z(10,23,3,3)=112,
$$

$$
Z(11,19,3,3)=106,
\qquad Z(11,20,3,3)=111,
\qquad Z(11,23,3,3)=123,
$$

$$
Z(12,23,3,3)=134.
$$

The deletion cases use the elementary averaging lemma. The $(10,22)$ value uses a standard-library enumeration excluding all four possible 111-one degree profiles. For $(10,23)$, arithmetic eliminates twelve of the 25 profiles at 113 ones and replayable SAT proof cores eliminate the other thirteen. The $(12,23)$ value excludes 136 ones by a forced-profile pair count and excludes the five possible 135-one profiles by row/pair residues. See the [extended-results proof](docs/EXTENDED_RESULTS.md), [`PROOF_Z10_23.md`](docs/PROOF_Z10_23.md), [`PROOF_Z11_23.md`](docs/PROOF_Z11_23.md), and [`PROOF_Z12_23.md`](docs/PROOF_Z12_23.md).

## Evidence and trust boundaries

The logical role of computation differs across the eight results:

| Result or layer | What it establishes | Artifact |
|---|---|---|
| Human upper-bound proof | Excludes 104 ones for $(9,23)$ | [`docs/PROOF.md`](docs/PROOF.md) |
| Deletion arguments | Give matching upper bounds for $(10,21)$, $(11,19)$, $(11,20)$, and $(11,23)$ | [`docs/PROOF_Z10_21.md`](docs/PROOF_Z10_21.md), [`docs/PROOF_Z11_19.md`](docs/PROOF_Z11_19.md), [`docs/PROOF_Z11_20.md`](docs/PROOF_Z11_20.md), [`docs/PROOF_Z11_23.md`](docs/PROOF_Z11_23.md) |
| Computer-assisted finite proof | Exhaustively excludes the four possible 111-one degree profiles for $(10,22)$ | [`docs/PROOF_Z10_22.md`](docs/PROOF_Z10_22.md), [`src/finite_zarankiewicz_closures/extended.py`](src/finite_zarankiewicz_closures/extended.py) |
| Traced SAT proof | Reduces 113 ones for $(10,23)$ to thirteen deterministic CNFs; checks ten directly and three by complete canonical cube covers, replaying every DRAT core through independent LRAT checking | [`docs/PROOF_Z10_23.md`](docs/PROOF_Z10_23.md), [`certificates/z10_23_sat.json`](certificates/z10_23_sat.json) |
| Two-stage deficit proof | Excludes 136 and all five 135-one profiles for $(12,23)$ | [`docs/PROOF_Z12_23.md`](docs/PROOF_Z12_23.md), [`src/finite_zarankiewicz_closures/extended.py`](src/finite_zarankiewicz_closures/extended.py) |
| Further frontier bound | Proves $Z(13,23,3,3)\le144$ without claiming equality | [`docs/BOUND_Z13_23.md`](docs/BOUND_Z13_23.md) |
| Explicit constructions | Supply all eight matching lower bounds | [`data/`](data/) |
| Independent witness checks | Verify every stored matrix by row-triple capacity and direct $3\times3$ scans | [`scripts/`](scripts/) |
| Case-specific certificates | Bind each witness hash to its own recomputed upper-bound mechanism | [`certificates/`](certificates/), [`scripts/check_case_certificates.py`](scripts/check_case_certificates.py) |
| Lean | Kernel-checks the arithmetic endpoints, profile classifications, and terminal contradictions for all eight results plus the $(13,23)$ bound | [`lean/`](lean/) |
| Decision models | Reconstruct cell-level SAT and column-type MIP formulations at all eight excluded targets | [`models/`](models/) |
| Standard proof traces | Replay the three terminal $(9,23)$ integer contradictions in DRAT and LRAT | [`certificates/`](certificates/) |
| Adversarial audit | Records mutation tests, independent tools, trust assumptions, and limitations | [`docs/ADVERSARIAL_AUDIT.md`](docs/ADVERSARIAL_AUDIT.md) |

Four boundaries are important:

- The $(9,23)$ upper bound is entirely human-readable; its computation is corroborating rather than logically necessary.
- The $(10,22)$ and $(12,23)$ upper bounds are computer-assisted: their finite standard-library enumerations are proof components. Lean checks the resulting classifications and numerical minima but does not rerun those enumerations.
- The $(10,23)$ upper bound is computer-assisted and proof-producing. Ten checked-in DRAT cores certify unsplit CNFs; three complete adaptive canonical-cover archives certify the remaining CNFs leaf by leaf. Every core is converted to LRAT for independent checking, while the human proof and standard-library checker establish the arithmetic split, formula semantics, and cover completeness. The large cover archives are GitHub release assets whose names, sizes, and SHA-256 digests are fixed by checked-in metadata.
- The Lean development formalizes arithmetic kernels, not the Boolean-matrix reductions, witness CSVs, deletion lemma, combinatorial double counts, or SAT proof checkers.

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

- the complete Python test suite passes;
- the two original witness verifiers accept the 103-one matrix, and the extended verifier accepts all seven additional matrices;
- all eight case-specific certificates verify, including the finite profile and SAT-proof integrity subcertificates;
- all sixteen generic decision models are byte-for-byte identical to the stored artifacts; and
- the repository audit reports `VERIFIED`.

### Lean

Lean 4.29.0 is pinned inside the subproject and no external Lean package is required. The default build checks both arithmetic libraries:

```sh
cd lean
lake build
lake env lean AxiomAudit.lean
```

The axiom report covers every load-bearing arithmetic theorem for all eight results and the $(13,23)$ bound. It is discussed in the [adversarial audit](docs/ADVERSARIAL_AUDIT.md). Executable tables and quotient computations use no axioms; the `omega` proofs use Lean's standard `propext`, `Classical.choice`, and `Quot.sound` principles and no project-specific axiom.

### Optional external replays

If CaDiCaL, GLPK, `drat-trim`, and `lrat-check` are installed:

```sh
python3 scripts/validate_models.py
glpsol --lp models/column_types_9x23_exact_104.lp --check
python3 scripts/replay_certificates.py
python3 scripts/fetch_z10_23_release_assets.py --output build/z10_23_assets
Z10_23_ASSET_DIR=build/z10_23_assets \
  python3 scripts/replay_z10_23_certificates.py
```

The fetch command downloads and hash-checks the release-backed cube archives.
The last command expands the ten direct $Z(10,23)$ cores and every leaf core
in the three complete cube-cover archives, converts each to LRAT, and
independently checks the derived LRAT. It is intentionally much heavier than
the core gate; `--workers N` parallelizes leaf replay. The versions used for
the recorded audit were CaDiCaL 3.0.0 and GLPK 5.0. Because the DRAT and LRAT
binaries do not expose stable semantic version strings, the certificate
manifest pins their source commit as well as the CaDiCaL source commit.

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
│   ├── PROOF_Z10_21.md          deletion proof and case evidence
│   ├── PROOF_Z10_22.md          computer-assisted proof and case evidence
│   ├── PROOF_Z10_23.md          arithmetic reduction and traced SAT proof
│   ├── PROOF_Z11_19.md          deletion proof and new witness evidence
│   ├── PROOF_Z11_20.md          two-step deletion proof and case evidence
│   ├── PROOF_Z11_23.md          deletion proof from the completed (10,23) case
│   ├── PROOF_Z12_23.md          two-stage deficit proof and witness evidence
│   ├── BOUND_Z13_23.md          further elementary upper bound
│   ├── SAT_Z10_23_STATUS.md      completed trace certification and history
│   ├── NEW_BOUNDS.md            propagated frontier and complete derivations
│   ├── EXTENDED_RESULTS.md      additional closures and open frontier
│   ├── LITERATURE_REVIEW.md     prior work and dated status search
│   ├── METHODS.md               models, certificates, and proof/code map
│   ├── ADVERSARIAL_AUDIT.md     attack surface, tests, findings, limits
│   └── REPRODUCIBILITY.md       commands and expected outputs
├── data/                        explicit matrices for all claimed lower bounds
├── certificates/                eight case certificates, detailed reductions, and proof traces
├── models/                      generic SAT/MIP models plus thirteen profile CNFs
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

Reviewers are encouraged to begin with the [$(9,23)$ proof](docs/PROOF.md), the [extended closures](docs/EXTENDED_RESULTS.md), and the case-specific proof dossiers, then run all eight case certificates, both witness implementations, and the two Lean libraries. The heavier DRAT-to-LRAT replay is a separate review step. A suggested review sequence and issue-reporting guidance appear in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Status and humility

The repository's internal checks support all eight exact values, and no mathematical gap is presently known. Nevertheless:

- this work has not yet been independently peer reviewed;
- the literature search cannot exclude unpublished or poorly indexed prior work;
- the novelty assessment is therefore dated and provisional; and
- any correction, simplification, or earlier reference is welcome.

The exact claims should be judged from the stated proof and trust boundaries, not from the amount of automation surrounding them.

## Citation and license

Machine-readable citation metadata is in [`CITATION.cff`](CITATION.cff), and full prior-work metadata is in [`references.bib`](references.bib). Code, proof text, data, and generated artifacts are released under the [MIT License](LICENSE).
