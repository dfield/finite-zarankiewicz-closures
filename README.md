> **Attribution:** GPT 5.6-Sol generated the original four closures, formal arithmetic, verification code, and repository. Claude (Anthropic) supplied the $Z(11,19)$ witness, the $Z(12,23)$ proof and witness, and the $Z(13,23)$ bound. OpenAI Codex completed the proof-producing and replayable certification of $Z(10,23)$ and the resulting $Z(11,23)$ closure. This is a research artifact awaiting independent expert review, not a peer-reviewed publication.

# Eight exact finite Zarankiewicz numbers

This repository gives reproducible proofs of eight exact values of $Z(m,n,3,3)$, the maximum number of ones in an $m\times n$ Boolean matrix with no all-one $3\times3$ submatrix:

$$
\begin{aligned}
Z(9,23,3,3)&=103, & Z(10,21,3,3)&=106,\\
Z(10,22,3,3)&=110, & Z(10,23,3,3)&=112,\\
Z(11,19,3,3)&=106, & Z(11,20,3,3)&=111,\\
Z(11,23,3,3)&=123, & Z(12,23,3,3)&=134.
\end{aligned}
$$

It also establishes

$$
Z(13,23,3,3)\le144.
$$

The machine-readable publication boundary is [`analysis/result_status.json`](analysis/result_status.json).

## Results and evidence

| Result | Upper-bound method | Reproducible evidence |
|---|---|---|
| $Z(9,23,3,3)=103$ | marked-row deficit | [`docs/PROOF.md`](docs/PROOF.md), [`lean/Zarankiewicz/Exact/Z9_23.lean`](lean/Zarankiewicz/Exact/Z9_23.lean), [`certificates/z9_23_103.json`](certificates/z9_23_103.json) |
| $Z(10,21,3,3)=106$ | vertex deletion from $Z(9,21)=96$ | [`docs/PROOF_Z10_21.md`](docs/PROOF_Z10_21.md), [`certificates/z10_21_106.json`](certificates/z10_21_106.json) |
| $Z(10,22,3,3)=110$ | pair-deficit residues | [`docs/PROOF_Z10_22.md`](docs/PROOF_Z10_22.md), [`lean/Zarankiewicz/Exact/Z10_22.lean`](lean/Zarankiewicz/Exact/Z10_22.lean), [`certificates/z10_22_110.json`](certificates/z10_22_110.json) |
| $Z(10,23,3,3)=112$ | arithmetic profile reduction plus replayable DRAT/LRAT and exact SCIP/VIPR refutations | [`docs/PROOF_Z10_23.md`](docs/PROOF_Z10_23.md), [`certificates/z10_23_112.json`](certificates/z10_23_112.json), [`certificates/z10_23_sat.json`](certificates/z10_23_sat.json) |
| $Z(11,19,3,3)=106$ | vertex deletion from $Z(11,18)=101$ | [`docs/PROOF_Z11_19.md`](docs/PROOF_Z11_19.md), [`certificates/z11_19_106.json`](certificates/z11_19_106.json) |
| $Z(11,20,3,3)=111$ | two deletion steps | [`docs/PROOF_Z11_20.md`](docs/PROOF_Z11_20.md), [`certificates/z11_20_111.json`](certificates/z11_20_111.json) |
| $Z(11,23,3,3)=123$ | minimum-row deletion from $Z(10,23)=112$ | [`docs/PROOF_Z11_23.md`](docs/PROOF_Z11_23.md), [`certificates/z11_23_123.json`](certificates/z11_23_123.json) |
| $Z(12,23,3,3)=134$ | two-stage row/pair deficit | [`docs/PROOF_Z12_23.md`](docs/PROOF_Z12_23.md), [`lean/Zarankiewicz/Exact/Z12_23.lean`](lean/Zarankiewicz/Exact/Z12_23.lean), [`certificates/z12_23_134.json`](certificates/z12_23_134.json) |
| $Z(13,23,3,3)\le144$ | finite profile and marked-row deficit | [`docs/BOUND_Z13_23.md`](docs/BOUND_Z13_23.md), [`certificates/z13_23_upper_144.json`](certificates/z13_23_upper_144.json) |

Every equality has a checked construction for its lower bound and a case-specific upper-bound certificate. The generic SAT/MIP models are regression artifacts, not proof substitutes.

## The $Z(10,23)$ certificate

At the excluded target of 113 ones, independent arithmetic enumeration finds 25 feasible degree profiles. Twelve are eliminated by deletion or deficit arguments. The remaining thirteen are covered as follows:

- ten direct CaDiCaL refutations checked through DRAT-to-LRAT conversion and `lrat-check`;
- one complete row-stabilizer cube cover, with a checked DRAT/LRAT proof for every leaf; and
- two exact SCIP/VIPR orbit covers: 445 orbit representatives covering 1,245,251 raw states.

The two VIPR covers contain 209 and 236 representatives. Their catalogs, regenerated OPB formulas, embedded VIPR models, solver/checker identities, aggregate manifests, and split release assets are all SHA-256 bound by [`certificates/z10_23_sat.json`](certificates/z10_23_sat.json). The earlier untraced solver sweep is retained as corroborating history only; it is not load-bearing.

This is a computer-assisted proof. Lean checks the arithmetic front end and deletion arithmetic, but does not replace the DRAT/LRAT or VIPR certificates.

## Relation to the 2026 table

Bhan--Nobili--Langer listed 44 open cells in Figure 2 of [arXiv:2605.01120v2](https://arxiv.org/html/2605.01120v2). Their paper made three exact. The eight repository equalities make 11 of those 44 exact, so **33 remain open**. Propagated bounds are recorded in [`analysis/new_bounds.json`](analysis/new_bounds.json) and explained in [`docs/NEW_BOUNDS.md`](docs/NEW_BOUNDS.md).

## Verification

The core gate uses only the Python standard library:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
make verify
```

It checks all eight witnesses and case certificates, deeply regenerates both VIPR orbit covers and every leaf OPB formula, checks deterministic models and propagated bounds, runs mutation tests, verifies checksums, and audits the repository.

Lean is a separate trust boundary:

```bash
cd lean
lake build
lake env lean AxiomAudit.lean
```

The full external-checker replay downloads about 25.3 GB of split proof assets from the GitHub release and requires `drat-trim`, `lrat-check`, and `viprchk`:

```bash
python3 scripts/fetch_z10_23_release_assets.py --output build/z10_23_assets
Z10_23_ASSET_DIR=build/z10_23_assets VIPRCHK=/path/to/viprchk \
python3 scripts/replay_z10_23_certificates.py --workers 8 \
  --output audit/z10_23_sat_replay.json
```

See [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md) for tool builds, hashes, selective replay, and expected reports.

## Repository map

| Path | Purpose |
|---|---|
| [`docs/`](docs/) | proofs, methods, literature review, audit, and reproducibility |
| [`data/`](data/) | eight independently checked exact-value witnesses |
| [`certificates/`](certificates/) | eight exact-value certificates, the $Z(10,23)$ proof manifest, and one frontier certificate |
| [`analysis/`](analysis/) | publication boundary, source-table reconstruction, and propagated bounds |
| [`models/`](models/) | deterministic excluded-target decision models |
| [`lean/`](lean/) | Lean proofs, conditional deletion closures, and axiom audit |
| [`scripts/`](scripts/) | regenerators, integrity checkers, full replay, and repository audit |
| [`tests/`](tests/) | regression and adversarial mutation tests |

## Scope and review status

The internal gates support the eight exact values and the $Z(13,23)$ upper bound above. The $Z(10,23)$ result is certificate-based and should be independently replayed and reviewed before journal use. No generic solver status, checkpoint, or cloud job state is accepted as proof.

Start with [`docs/LITERATURE_REVIEW.md`](docs/LITERATURE_REVIEW.md), then review the case dossiers and [`docs/ADVERSARIAL_AUDIT.md`](docs/ADVERSARIAL_AUDIT.md). Contribution guidance is in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License and citation

The repository is released under the [MIT License](LICENSE). Citation metadata is in [`CITATION.cff`](CITATION.cff).
