> **Attribution:** The proof, formal arithmetic, verification code, and repository were produced by **GPT 5.6-Sol**. This is a research artifact awaiting independent expert review, not a peer-reviewed publication.

# Closing the finite case $Z(9,23,3,3)$

This repository presents a reproducible proof that

$$
\boxed{Z(9,23,3,3)=103}.
$$

In plain language: place as many ones as possible in a 9-row, 23-column zero-one matrix, subject to the rule that no choice of three rows and three columns may form an all-one square. The answer is 103. A concrete 103-one matrix exists, while the proof shows that 104 ones are impossible.

The upper bound is an elementary counting argument, not a solver verdict. Computation is used to check the witness, mirror the finite arithmetic, reproduce the original decision formulations, and provide additional certificate layers.

## Why this case mattered

The Zarankiewicz problem is a classical question in extremal combinatorics. Reading a Boolean matrix as the adjacency matrix of a bipartite graph turns an all-one $3\times3$ submatrix into a copy of the complete bipartite graph $K_{3,3}$.

Immediately before this work, the public literature gave

$$
103\le Z(9,23,3,3)\le104.
$$

The 104 upper bound comes from the degree-counting method of Steven Roman. The 103 lower bound was reported in 2026 by Jay Bhan, Nicole Nobili, and Patrick Langer using LLM-guided evolutionary search. Their paper displayed the one-edge gap rather than claiming this cell was exact. Jeremy Tan's earlier SAT table likewise listed 104 as an upper bound, and the strengthened linear program of Sara Davies, Peter Gill, and Daniel Horsley does not remove the last edge.

Credit for the previously public 103 lower bound belongs to Bhan--Nobili--Langer. The contribution presented here is the upper-bound proof excluding 104, together with a deliberately redundant verification package. See the [literature review](docs/LITERATURE_REVIEW.md) for the complete attribution chain and dated search protocol.

## The proof idea

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

## Evidence and trust boundaries

No single program is asked to carry the theorem. The repository separates the evidence into layers:

| Layer | What it establishes | Artifact |
|---|---|---|
| Human proof | No 104-one matrix can exist | [`docs/PROOF.md`](docs/PROOF.md) |
| Explicit construction | A 103-one matrix exists | [`data/z9_23_103_matrix.csv`](data/z9_23_103_matrix.csv) |
| Independent witness checks | Row-triple capacities and all 148,764 candidate submatrices both pass | [`scripts/verify_witness.py`](scripts/verify_witness.py), [`scripts/verify_witness_independent.py`](scripts/verify_witness_independent.py) |
| Exact arithmetic certificate | Independently enumerates all degree profiles and checks each contradiction | [`certificates/degree_deficit.json`](certificates/degree_deficit.json) |
| Lean | Kernel-checks the penalty table, degree-profile classification, and terminal residue contradictions | [`lean/`](lean/) |
| Decision models | Reconstructs the 207-cell SAT and 512-column-type MIP formulations | [`models/`](models/) |
| Standard proof traces | Replays the three terminal integer contradictions in DRAT and LRAT | [`certificates/`](certificates/) |
| Adversarial audit | Records mutation tests, independent tools, trust assumptions, and limitations | [`docs/ADVERSARIAL_AUDIT.md`](docs/ADVERSARIAL_AUDIT.md) |

Two boundaries are important:

- The Lean development formalizes the arithmetic kernel, not the complete matrix-to-counting translation. The repository does not call this a fully formalized theorem.
- The DRAT/LRAT files certify the three terminal aggregations, not the full 8.2 MB cell CNF. The independently checked JSON certificate covers the mathematical reduction. There is no claim of a monolithic raw-cell LRAT proof.

## Quick verification

The core audit needs only Python 3.9 or later and the standard library:

```sh
make test
make witness
make certificate
make models
```

Or run the consolidated gate:

```sh
make verify
```

Expected headline results are:

- 19 Python tests pass;
- both witness verifiers report `valid: true`;
- the exact certificate reports `VERIFIED` and three enumerated profiles;
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
│   ├── LITERATURE_REVIEW.md     prior work and dated status search
│   ├── METHODS.md               models, certificates, and proof/code map
│   ├── ADVERSARIAL_AUDIT.md     attack surface, tests, findings, limits
│   └── REPRODUCIBILITY.md       commands and expected outputs
├── data/                        explicit 103-one matrix
├── certificates/                exact JSON reduction and terminal traces
├── models/                      deterministic SAT/MIP artifacts
├── analysis/                    exact DGH boundary and kernel catalog
├── lean/                        formal arithmetic subproject
├── src/zarankiewicz_z9_23/      documented standard-library package
├── scripts/                     small command-line entry points
├── tests/                       adversarial and semantic regression tests
└── audit/                       recorded external-tool reports
```

The Git history itself records the proof-first workflow: the root commit contains only [`docs/PROOF.md`](docs/PROOF.md), and implementation begins later.

## Reproducibility and review

All core generators are deterministic. The randomized model-validation sample uses the fixed seed `20260704`. Stored outputs contain no machine-specific paths or timestamps. Artifact hashes are collected in [`artifacts.sha256`](artifacts.sha256).

Reviewers are encouraged to begin with the six-page-equivalent [proof](docs/PROOF.md), then run the two witness verifiers and the exact certificate checker. The SAT/MIP and proof-trace layers are intentionally secondary. A suggested review sequence and issue-reporting guidance appear in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Status and humility

The repository's internal checks support the exact value 103, and no mathematical gap is presently known. Nevertheless:

- this work has not yet been independently peer reviewed;
- the literature search cannot exclude unpublished or poorly indexed prior work;
- the novelty assessment is therefore dated and provisional; and
- any correction, simplification, or earlier reference is welcome.

The exact claim should be judged from the proof, not from the amount of automation surrounding it.

## Citation and license

Machine-readable citation metadata is in [`CITATION.cff`](CITATION.cff), and full prior-work metadata is in [`references.bib`](references.bib). Code, proof text, data, and generated artifacts are released under the [MIT License](LICENSE).
