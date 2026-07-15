# Reproducibility guide

## Publication boundary

The repository certifies eight exact values and $Z(13,23,3,3)\le144$. The $Z(10,23)=112$ upper bound is computer-assisted and has two verification levels:

- a self-contained integrity and completeness gate in the Git clone; and
- a heavyweight semantic replay using approximately 25.3 GB of release-bound proof streams and three external checkers.

See [`result_status.json`](../analysis/result_status.json).

## Minimal environment

- Python 3.9 or later;
- a complete Git clone for the proof-first history audit; and
- no Python runtime dependency outside the standard library.

Lean and the external proof checkers are separate optional environments.

## One-command local gate

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
make verify
```

This runs the unit and mutation tests, checks all eight matrices and exact-value certificates, regenerates the two VIPR orbit covers and all 445 OPB leaves, checks the frontier certificate, regenerates the bound analyses and all sixteen models, verifies artifact hashes, and runs the structural repository audit. It does not download large release assets or invoke an external proof checker.

## Individual gates

### Tests and witnesses

```bash
make test
make witness
PYTHONPATH=src python3 scripts/check_extended_results.py --check
python3 scripts/verify_extended_witnesses_independent.py
```

Expected: all eight matrices are $K_{3,3}$-free at their recorded exact weights, and representative corruptions of formulas, manifests, covers, release metadata, and case certificates are rejected.

### Exact and frontier certificates

```bash
make certificate
```

Expected: the marked-row subcertificate, eight case-specific exact certificates, the complete local $Z(10,23)$ manifest layer, and the $Z(13,23)\le144$ certificate report `VERIFIED`.

### Isolated $Z(10,23)$ integrity gate

```bash
make z10-23-certificate
```

Expected summary:

- 25 arithmetic profiles and 12 arithmetic eliminations;
- 13 certified profiles: 10 direct, one cube-cover, and two VIPR-cover cases;
- 17,170 cube leaves;
- 445 VIPR orbits covering 1,245,251 raw states; and
- 25,345,672,172 bytes of release-bound compressed proof material.

This gate reconstructs covers, formulas, and metadata but does not read the large proof bodies.

### Extended table

```bash
make extended
make new-bounds
```

Expected facts include:

- 44 cells in the paper boundary;
- 11 exact cells after combining the paper and repository results;
- 33 remaining open cells;
- $Z(10,23)=112$ and $Z(11,23)=123$;
- 21 improved upper bounds and 17 improved lower bounds relative to the paper intervals.

### Decision models

```bash
make models
```

Expected: `status: IDENTICAL` for eight cell CNFs and eight column-support LPs. [`models/manifest.json`](../models/manifest.json) labels all eight cases `established`. A deterministic model is not, by itself, an UNSAT certificate.

### Lean

```bash
cd lean
lake build
lake env lean AxiomAudit.lean
```

Lean proves $Z(9,23)=103$, $Z(10,22)=110$, and $Z(12,23)=134$ end-to-end and proves $Z(13,23)\le144$. Deletion-derived theorem types retain their external historical starting bounds as visible parameters. Lean does not replay or replace the $Z(10,23)$ DRAT/LRAT and VIPR evidence.

## Full $Z(10,23)$ external replay

### 1. Build or obtain the pinned checkers

The accepted tool identities are fixed in [`z10_23_sat.json`](../certificates/z10_23_sat.json):

- `drat-trim` and `lrat-check` from proof-tools commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985`;
- `viprchk` from [scipopt/vipr](https://github.com/scipopt/vipr) commit `30f2951d1e90e47afa821bdd1b12b82246656c42`.

A minimal VIPR build is:

```bash
git clone https://github.com/scipopt/vipr.git
cd vipr
git checkout 30f2951d1e90e47afa821bdd1b12b82246656c42
cmake -S . -B build -DVIPRCOMP=off
cmake --build build --parallel
```

### 2. Fetch and check the release assets

The GitHub CLI must be authenticated only if the release is not public.

```bash
python3 scripts/fetch_z10_23_release_assets.py \
  --output build/z10_23_assets
```

The fetcher reads all three checked-in release sidecars, downloads sixteen split parts, and checks each byte count and SHA-256 digest before reuse.

### 3. Replay

```bash
PATH=/path/to/proof-tools:$PATH \
VIPRCHK=/path/to/vipr/build/viprchk \
Z10_23_ASSET_DIR=build/z10_23_assets \
python3 scripts/replay_z10_23_certificates.py \
  --workers 8 \
  --output audit/z10_23_sat_replay.json
```

To replay one profile during review, repeat `--profile` with its canonical manifest label, for example:

```bash
VIPRCHK=/path/to/vipr/build/viprchk \
Z10_23_ASSET_DIR=build/z10_23_assets \
python3 scripts/replay_z10_23_certificates.py \
  --profile 3x1,4x3,5x16,6x3 --workers 8
```

The replay streams archives, checks every member against its leaf manifest, regenerates every leaf formula, verifies embedded VIPR models coefficient-for-coefficient, and invokes the appropriate independent checker. It never accepts a solver status string in place of a proof.

## Historical $Z(9,23)$ traces

The three terminal DRAT/LRAT aggregations in the $Z(9,23)$ proof can be replayed separately:

```bash
python3 scripts/replay_certificates.py
```

Their scope is limited to the marked-row proof endpoints.

## Artifact integrity and determinism

```bash
make checksums
python3 scripts/audit_repository.py
```

The audit checks local links, required files, JSON syntax, model structure and hashes, publication-status consistency, mathematical APIs, Lean admissions, proof-first history, path hygiene, and every entry in [`artifacts.sha256`](../artifacts.sha256).

Generated theorem artifacts contain no timestamp, hostname, temporary path, or untraced solver verdict. Operational AWS manifests may record timestamps for provenance, but the deterministic checked-in aggregate and release descriptors bind only theorem-relevant content.

## Clean-clone procedure

```bash
git clone https://github.com/dfield/finite-zarankiewicz-closures.git
cd finite-zarankiewicz-closures
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
make verify
```

The local gate is self-contained in the clone. The external semantic replay additionally requires the release assets and pinned checker builds above.
