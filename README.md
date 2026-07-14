> **Attribution:** GPT 5.6-Sol produced the original four closures, formal arithmetic, verification code, and repository. Claude (Anthropic) produced the $Z(11,19)$ witness, the $Z(12,23)$ proof and witness, and the $Z(13,23)$ bound. OpenAI Codex is performing the replayable certification work for the two candidates. This is a research artifact awaiting independent expert review, not a peer-reviewed publication.

# Six exact finite Zarankiewicz numbers and two candidates

This repository separates results that are ready to publish as theorem claims from promising cases whose upper bounds are not yet fully certified. The authoritative machine-readable boundary is [`analysis/result_status.json`](analysis/result_status.json).

## Established results

The repository gives reproducible proofs of

$$
\begin{aligned}
Z(9,23,3,3)&=103, & Z(10,21,3,3)&=106,\\
Z(10,22,3,3)&=110, & Z(11,19,3,3)&=106,\\
Z(11,20,3,3)&=111, & Z(12,23,3,3)&=134.
\end{aligned}
$$

It also establishes the new frontier bound

$$
Z(13,23,3,3)\le 144.
$$

Here $Z(m,n,3,3)$ is the maximum number of ones in an $m\times n$ Boolean matrix containing no all-one $3\times3$ submatrix.

| Result | Upper-bound method | Reproducible evidence |
|---|---|---|
| $Z(9,23,3,3)=103$ | marked-row deficit argument | [`docs/PROOF.md`](docs/PROOF.md), [`certificates/z9_23_103.json`](certificates/z9_23_103.json) |
| $Z(10,21,3,3)=106$ | vertex deletion from $Z(9,21)=96$ | [`docs/PROOF_Z10_21.md`](docs/PROOF_Z10_21.md), [`certificates/z10_21_106.json`](certificates/z10_21_106.json) |
| $Z(10,22,3,3)=110$ | finite pair-deficit enumeration | [`docs/PROOF_Z10_22.md`](docs/PROOF_Z10_22.md), [`certificates/z10_22_110.json`](certificates/z10_22_110.json) |
| $Z(11,19,3,3)=106$ | vertex deletion from $Z(11,18)=101$ | [`docs/PROOF_Z11_19.md`](docs/PROOF_Z11_19.md), [`certificates/z11_19_106.json`](certificates/z11_19_106.json) |
| $Z(11,20,3,3)=111$ | two deletion steps | [`docs/PROOF_Z11_20.md`](docs/PROOF_Z11_20.md), [`certificates/z11_20_111.json`](certificates/z11_20_111.json) |
| $Z(12,23,3,3)=134$ | two-stage row/pair deficit argument | [`docs/PROOF_Z12_23.md`](docs/PROOF_Z12_23.md), [`certificates/z12_23_134.json`](certificates/z12_23_134.json) |
| $Z(13,23,3,3)\le144$ | finite profile and marked-row deficit argument | [`docs/BOUND_Z13_23.md`](docs/BOUND_Z13_23.md), [`certificates/z13_23_upper_144.json`](certificates/z13_23_upper_144.json) |

Each equality has both a checked construction for the lower bound and an independently recomputed upper-bound certificate. The six case certificates—not the generic SAT/MIP models—define the publication gate.

## Candidates retained with caveats

Two proposed equalities are useful research outputs but are **not theorem claims in this version**:

| Candidate | Fully checked now | Missing before equality may be claimed |
|---|---|---|
| $Z(10,23,3,3)=112$ | a valid 112-one witness; exhaustive enumeration of 25 feasible 113-one profiles; arithmetic contradictions for 12 profiles; safe bound $Z(10,23)\le114$ | a complete replayable refutation of the 13 surviving profiles at 113 ones |
| $Z(11,23,3,3)=123$ | a valid 123-one witness and current bound $Z(11,23)\le125$ | the upper bound 123, which follows by vertex deletion if $Z(10,23)\le112$ is certified |

Thus the currently established intervals are

$$
112\le Z(10,23,3,3)\le114,
\qquad
123\le Z(11,23,3,3)\le125.
$$

The candidate dossiers deliberately retain the models, partial traces, AWS production notes, and conditional argument:

- [`docs/SAT_Z10_23_STATUS.md`](docs/SAT_Z10_23_STATUS.md) gives the concise certification status;
- [`docs/PROOF_Z10_23.md`](docs/PROOF_Z10_23.md) gives the proved arithmetic reduction and the remaining proof obligation;
- [`docs/PROOF_Z11_23.md`](docs/PROOF_Z11_23.md) gives the checked lower bound and conditional deletion implication;
- [`docs/AWS_Z10_23_RUN.md`](docs/AWS_Z10_23_RUN.md) records the ongoing proof-production run.

An historical untraced solver sweep is recorded only as corroborating discovery evidence in [`analysis/sat_cross_check.json`](analysis/sat_cross_check.json). It is not load-bearing.

## Relation to the 2026 table

Bhan--Nobili--Langer listed 44 open cells in Figure 2 of [arXiv:2605.01120v2](https://arxiv.org/html/2605.01120v2). Their paper made three of those cells exact. The six established repository equalities settle six more, so 9 of the 44 are exact and **35 remain open** at this publication boundary. The two candidates are included among those 35 until their upper bounds are certified.

The checked witnesses also propagate lower bounds, and the established equalities and $Z(13,23)\le144$ propagate upper bounds. The conservative updated table is in [`analysis/new_bounds.json`](analysis/new_bounds.json) and explained in [`docs/NEW_BOUNDS.md`](docs/NEW_BOUNDS.md).

## Verification

Python 3.11 or later is sufficient for the core gate; the reusable package has no runtime dependency outside the standard library.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
make verify
```

`make verify` checks:

- all eight matrices, with the two candidate matrices classified only as lower-bound witnesses;
- all six exact-value certificates and the $Z(13,23)$ upper-bound certificate;
- the arithmetic front end for the $Z(10,23)$ candidate without treating it as a completed refutation;
- deterministic models, propagated bounds, checksums, tests, and repository-audit invariants.

Lean checks the arithmetic kernels:

```bash
cd lean
lake build
lake env lean PrintAxioms.lean
```

Lean formalizes the load-bearing arithmetic endpoints, not the complete Boolean-matrix arguments. See [`lean/README.md`](lean/README.md) and [`docs/ADVERSARIAL_AUDIT.md`](docs/ADVERSARIAL_AUDIT.md) for the exact trust boundary.

The generic excluded-target CNFs and column-type MIPs in [`models/`](models/) are transparent decision formulations and regression artifacts. For a candidate, a model file does **not** establish unsatisfiability. Once the full $Z(10,23)$ proof family and final manifest exist, the separate heavyweight gate will be:

```bash
make candidate-certificate
```

That command is intentionally outside `make verify` while the final replayable certificate is absent.

## Repository map

| Path | Purpose |
|---|---|
| [`docs/`](docs/) | proofs, candidate dossiers, methods, literature review, audit, and reproducibility guide |
| [`data/`](data/) | eight checked matrices: six exact-value witnesses and two candidate lower-bound witnesses |
| [`certificates/`](certificates/) | six publishable exact-value certificates, one frontier certificate, and clearly scoped partial candidate artifacts |
| [`analysis/`](analysis/) | result-status boundary, source-table reconstruction, candidate record, and propagated bounds |
| [`models/`](models/) | deterministic decision models, each tagged `established` or `candidate` |
| [`lean/`](lean/) | Lean arithmetic audit |
| [`scripts/`](scripts/) | independent regenerators, verifiers, and repository audit |
| [`tests/`](tests/) | regression and mutation tests |

## Scope and review status

The internal checks support the six exact values and the $Z(13,23)$ upper bound listed above. The two proposed equalities remain explicitly provisional. No claim here supersedes the need for independent mathematical and computational review, and no generic solver status is accepted as proof.

Start with [`docs/LITERATURE_REVIEW.md`](docs/LITERATURE_REVIEW.md), then review the case dossiers and run `make verify`. Contribution and review guidance is in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License and citation

The repository is released under the [MIT License](LICENSE).

Citation metadata is provided in [`CITATION.cff`](CITATION.cff).
