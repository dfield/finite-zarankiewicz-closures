# Reproducibility guide

## Minimal environment

The core verification requires:

- Python 3.9 or later;
- a POSIX-like shell for the `Makefile`; and
- no Python package outside the standard library.

Lean is optional for checking the mathematical result but required to rebuild the formal arithmetic layer. The subproject pins Lean 4.29.0 and uses only `Std`.

External SAT, MIP, DRAT, and LRAT tools are optional corroborating checks.

Python 3.9 is retained deliberately as an archival compatibility floor even though upstream support ended in October 2025. Continuous integration checks both Python 3.9 and current stable Python 3.14; the core has no third-party Python dependencies.

## One-command core gate

From the repository root:

```sh
make verify
```

This runs tests, all six witness checks, all six case-certificate paths, deterministic model regeneration, and the repository audit. It does not invoke external solvers or Lean.

## Continuous integration

The GitHub Actions workflow runs `make verify` on Python 3.9 and 3.14 and builds the Lean arithmetic kernel on every push and pull request. It can also be started manually with `workflow_dispatch`.

## Individual commands and expected facts

### Python tests

```sh
make test
```

Expected: 33 tests and `OK`. The test count is secondary; the named cases in [`tests/`](../tests/) define the coverage.

### Witness

```sh
make witness
```

Expected from the first checker:

- `valid: true`;
- `ones: 103`;
- `row_triples_checked: 84`; and
- `maximum_common_columns: 2`.

Expected from the independent checker:

- `valid: true`; and
- `candidate_submatrices_checked: 148764`.

Both reports must show the same SHA-256 digest.

### Exact certificate

```sh
make certificate
```

Expected: the detailed marked-row checker reports `VERIFIED` with three profiles, followed by six `VERIFIED` case certificates. The latter bind every witness hash to its case-specific upper-bound mechanism.

### Additional exact values

```sh
make extended
```

Expected from the primary checker:

- `status: IDENTICAL`;
- `source_open_cases: 44`;
- `remaining_open_cases: 35`; and
- five verified additional witnesses.

The independent checker must inspect the complete candidate sets for all five additional matrices, including 159,885 for $11\times19$ and 389,620 for $12\times23$. The standard-library upper-bound certificates must reproduce the four $(10,22)$ profiles, five $(12,23)$ profiles at 135, and three $(13,23)$ profiles at 145.

### Decision models

```sh
make models
```

Expected: `status: IDENTICAL` for all twelve files. The schema-v2 manifest covers six cell CNFs and six column-support LPs:

| Case | Cell variables | Cell clauses | Support variables | Triple constraints |
|---|---:|---:|---:|---:|
| $(9,23)$ at 104 | 32,654 | 277,931 | 512 | 84 |
| $(10,21)$ at 107 | 33,596 | 292,514 | 1,024 | 120 |
| $(10,22)$ at 111 | 36,849 | 330,656 | 1,024 | 120 |
| $(11,19)$ at 107 | 33,277 | 291,530 | 2,048 | 165 |
| $(11,20)$ at 112 | 36,846 | 333,944 | 2,048 | 165 |
| $(12,23)$ at 135 | 57,813 | 618,940 | 4,096 | 220 |

To rewrite the artifacts intentionally:

```sh
python3 scripts/generate_models.py
```

### LP boundary diagnostics

```sh
python3 scripts/analyze_boundary.py --check
```

Expected: `status: IDENTICAL`. Removing `--check` rewrites the exact-rational JSON and CSV catalog.

### Lean

```sh
cd lean
lake build
lake env lean AxiomAudit.lean
```

Expected: both Lean libraries build and the axiom audit prints the arithmetic theorems for all six exact results and the additional frontier bound. The exact boundary is listed in [`ADVERSARIAL_AUDIT.md`](ADVERSARIAL_AUDIT.md).

## Optional independent tools

The audit machine used:

| Tool | Recorded version | Purpose |
|---|---|---|
| Python | 3.9.6 | Core checks and generators |
| Lean | 4.29.0 | Formal arithmetic |
| CaDiCaL | 3.0.0 | Small-instance CNF validation |
| GLPK / `glpsol` | 5.0 | Independent LP/MIP parser |
| `drat-trim` | command-line checker | DRAT replay |
| `lrat-check` | command-line checker | LRAT replay |

Run:

```sh
python3 scripts/validate_models.py
glpsol --lp models/column_types_9x23_exact_104.lp --check
python3 scripts/replay_certificates.py
```

The first command regenerates temporary small CNFs and uses seed `20260704`. The second should report 86 rows, 512 columns, 6,399 matrix nonzeros, and 512 integer variables. The third requires all six trace checks to report true.

External output is summarized in [`audit/model_validation.json`](../audit/model_validation.json) and [`audit/certificate_replay.json`](../audit/certificate_replay.json). Temporary paths and timing noise are intentionally not stored.

## Artifact integrity

Run:

```sh
python3 scripts/build_checksums.py --check
```

This compares the selected mathematical and generated artifacts with [`artifacts.sha256`](../artifacts.sha256). A hash mismatch is not automatically a mathematical failure—an intentional regeneration changes hashes—but it must be explained and reviewed.

## Determinism

The following outputs are byte-deterministic:

- cell CNF;
- column-type LP;
- model metadata;
- exact DGH boundary report;
- local-kernel catalog;
- extended finite-table report; and
- artifact checksum file.

Reports from external tools retain semantic outcomes and tool versions while omitting elapsed time, temporary directories, and machine identifiers.

## Clean-clone procedure

For the strongest local reproduction:

```sh
git clone git@github.com:dfield/finite-zarankiewicz-closures.git
cd finite-zarankiewicz-closures
make verify
cd lean && lake build && lake env lean AxiomAudit.lean
```

Then, if the optional tools are installed, run the three external commands above. No command requires a file outside the cloned repository.
