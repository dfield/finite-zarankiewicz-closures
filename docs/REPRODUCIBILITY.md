# Reproducibility guide

## Minimal environment

The core verification requires:

- Python 3.9 or later;
- a POSIX-like shell for the `Makefile`; and
- no Python package outside the standard library.

Lean is optional for checking the mathematical result but required to rebuild the formal arithmetic layer. The subproject pins Lean 4.29.0 and uses only `Std`.

External SAT, MIP, DRAT, and LRAT tools are optional corroborating checks.

## One-command core gate

From the repository root:

```sh
make verify
```

This runs tests, the original and follow-on witness checks, both exact certificates, deterministic model regeneration, and the repository audit. It does not invoke external solvers or Lean.

## Individual commands and expected facts

### Python tests

```sh
make test
```

Expected: 23 tests and `OK`. The test count is secondary; the named cases in [`tests/`](../tests/) define the coverage.

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

Expected: `status: VERIFIED`, `profiles_enumerated: 3`, and the three named cases `balanced`, `one_degree_3`, and `one_degree_6`.

### Follow-on exact values

```sh
make extended
```

Expected from the primary checker:

- `status: IDENTICAL`;
- `source_open_cases: 44`;
- `remaining_open_cases: 37`; and
- three verified follow-on witnesses.

The independent checker must inspect 159,600 candidate submatrices for the $10\times21$ matrix, 184,800 for the $10\times22$ matrix, and 188,100 for the $11\times20$ matrix. The standard-library upper-bound certificate must enumerate four degree profiles, 1,050 profile-B cases, and $77\times22{,}155$ profile-C cases.

### Decision models

```sh
make models
```

Expected: `status: IDENTICAL` for both files. The target cell model metadata is:

- 207 base cell variables;
- 32,654 total variables;
- 148,764 forbidden-submatrix clauses; and
- 277,931 total clauses.

The target column model has 512 support variables and 84 row-triple constraints.

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

Expected: a successful four-job build and the axiom boundary listed in [`ADVERSARIAL_AUDIT.md`](ADVERSARIAL_AUDIT.md).

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
- local-kernel catalog; and
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
