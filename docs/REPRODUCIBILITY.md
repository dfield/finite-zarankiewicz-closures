# Reproducibility guide

## Publication boundary

The core gate certifies six exact values and $Z(13,23,3,3)\le144$. It also verifies two candidate matrices and the $Z(10,23)$ arithmetic reduction without promoting either candidate to an equality. See [`analysis/result_status.json`](../analysis/result_status.json).

## Minimal environment

- Python 3.9 or later;
- a complete Git clone for the proof-first history audit; and
- no Python runtime dependency outside the standard library.

Lean, CaDiCaL, `drat-trim`, and `lrat-check` are optional. The first audits arithmetic kernels; the others validate encodings or replay proof traces when complete traces exist.

## One-command core gate

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
make verify
```

This runs tests, checks all eight matrices, verifies six exact-value certificates and the frontier certificate, regenerates the bound analyses and all sixteen models, checks artifact hashes, and runs the repository audit. It does not invoke Lean or an external SAT checker.

## Individual gates

### Tests

```bash
make test
```

Expected: all tests pass. The final-manifest mutation test for $Z(10,23)$ is skipped while that candidate manifest is absent; the test suite separately requires its status to remain pending.

### Witnesses

```bash
make witness
PYTHONPATH=src python3 scripts/check_extended_results.py --check
python3 scripts/verify_extended_witnesses_independent.py
```

Expected: all eight matrices are $K_{3,3}$-free at their recorded weights. The 112- and 123-one matrices prove lower bounds only.

### Exact and frontier certificates

```bash
make certificate
```

Expected: the marked-row subcertificate, six case-specific exact certificates, and the $Z(13,23)\le144$ certificate report `VERIFIED`. No $Z(10,23)$ or $Z(11,23)$ exact-value certificate is part of this gate.

### Extended table

```bash
make extended
make new-bounds
```

Expected facts include:

- 44 cells in the paper boundary;
- 9 exact cells after combining the paper and repository results;
- 35 remaining open cells;
- $112\le Z(10,23)\le114$;
- $123\le Z(11,23)\le125$;
- 20 improved upper bounds and 17 improved lower bounds relative to the paper intervals.

### Decision models

```bash
make models
```

Expected: `status: IDENTICAL` for eight cell CNFs and eight column-support LPs. [`models/manifest.json`](../models/manifest.json) labels six cases `established` and two `candidate`. A deterministic model is not an UNSAT certificate.

### Boundary diagnostics

```bash
make analysis
```

Expected: the exact-rational DGH relaxation and local-kernel catalog match their stored forms. These are diagnostic for $Z(9,23)$, not theorem certificates.

### Lean

```bash
cd lean
lake build
lake env lean AxiomAudit.lean
```

Expected: both libraries build and the axiom audit prints the declared arithmetic theorems. Candidate arithmetic appears only as partial or conditional coverage; Lean does not supply the missing SAT premise.

## External trace replay

The three historical terminal aggregations in the established $Z(9,23)$ proof can be replayed with pinned `drat-trim` and `lrat-check` binaries:

```bash
python3 scripts/replay_certificates.py
```

The intended $Z(10,23)$ replay path is heavier:

```bash
python3 scripts/replay_z10_23_certificates.py --workers 4
```

That command is not part of the current publication gate because the final manifest and complete proof assets do not yet exist. Once they do, first run:

```bash
make candidate-certificate
```

then perform semantic replay and inspect the resulting audit before changing the result status. Solver output, S3 checkpoints, and manifest integrity without semantic replay are insufficient.

## Artifact integrity and determinism

```bash
make checksums
python3 scripts/audit_repository.py
```

The audit checks local links, required files, JSON syntax, model structure and hashes, result-status consistency, mathematical APIs, Lean source admissions, proof-first history, path hygiene, and every entry in [`artifacts.sha256`](../artifacts.sha256).

Generated artifacts are deterministic:

- analyses are compared structurally or byte-for-byte with recomputation;
- exact certificates are regenerated from untrusted inputs;
- model files are regenerated in a temporary directory;
- witness digests bind raw CSV bytes; and
- no timestamp, hostname, temporary path, or random solver verdict enters a theorem certificate.

## Clean-clone procedure

```bash
git clone https://github.com/dfield/finite-zarankiewicz-closures.git
cd finite-zarankiewicz-closures
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
make verify
```

The core gate is self-contained in the clone. Candidate promotion will additionally require release-bound proof assets, independent replay tools, and an explicit coherent update of every theorem/candidate status surface.
