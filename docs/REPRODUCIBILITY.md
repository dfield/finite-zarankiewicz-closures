# Reproducibility guide

## Minimal environment

The core verification requires:

- Python 3.9 or later;
- a POSIX-like shell for the `Makefile`; and
- no Python package outside the standard library.

Lean is optional for checking the mathematical result but required to rebuild the formal arithmetic layer. The subproject pins Lean 4.29.0 and uses only `Std`.

External SAT, MIP, DRAT, and LRAT tools are optional for the core integrity gate. Semantic replay of the $Z(10,23)$ proof requires `drat-trim` and `lrat-check` and is the strongest review path for that computer-assisted result.

Python 3.9 is retained deliberately as an archival compatibility floor even though upstream support ended in October 2025. Continuous integration checks both Python 3.9 and current stable Python 3.14; the core has no third-party Python dependencies.

## One-command core gate

From the repository root:

```sh
make verify
```

This runs tests, all eight witness checks, all eight case-certificate paths, deterministic model regeneration, and the repository audit. It does not invoke external solvers or Lean.

## Continuous integration

The GitHub Actions workflow runs `make verify` on Python 3.9 and 3.14 and builds the Lean arithmetic kernel on every push and pull request. It can also be started manually with `workflow_dispatch`.

## Individual commands and expected facts

### Python tests

```sh
make test
```

Expected: `OK`. The named cases in [`tests/`](../tests/) define the coverage; the precise count is secondary.

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

Expected: the detailed marked-row checker reports `VERIFIED` with three profiles, followed by eight `VERIFIED` case certificates. The latter bind every witness hash to its case-specific upper-bound mechanism.

### Additional exact values

```sh
make extended
```

Expected from the primary checker:

- `status: IDENTICAL`;
- `source_open_cases: 44`;
- `remaining_open_cases: 33`; and
- seven verified additional witnesses.

The independent checker must inspect the complete candidate sets for all seven additional matrices, including 212,520 for $10\times23$, 292,215 for $11\times23$, and 389,620 for $12\times23$. The standard-library upper-bound certificates must reproduce 25 $(10,23)$ profiles at 113, the four $(10,22)$ profiles, five $(12,23)$ profiles at 135, and three $(13,23)$ profiles at 145.

### Decision models

```sh
make models
```

Expected: `status: IDENTICAL` for all sixteen files. The schema-v2 manifest covers eight cell CNFs and eight column-support LPs:

| Case | Cell variables | Cell clauses | Support variables | Triple constraints |
|---|---:|---:|---:|---:|
| $(9,23)$ at 104 | 32,654 | 277,931 | 512 | 84 |
| $(10,21)$ at 107 | 33,596 | 292,514 | 1,024 | 120 |
| $(10,22)$ at 111 | 36,849 | 330,656 | 1,024 | 120 |
| $(10,23)$ at 113 | 40,246 | 371,894 | 1,024 | 120 |
| $(11,19)$ at 107 | 33,277 | 291,530 | 2,048 | 165 |
| $(11,20)$ at 112 | 36,846 | 333,944 | 2,048 | 165 |
| $(11,23)$ at 124 | 48,633 | 484,976 | 2,048 | 165 |
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

Expected: both Lean libraries build and the axiom audit prints the arithmetic theorems for all eight exact results and the additional frontier bound. The exact boundary is listed in [`ADVERSARIAL_AUDIT.md`](ADVERSARIAL_AUDIT.md).

## Optional independent tools

The audit machine used:

| Tool | Recorded version | Purpose |
|---|---|---|
| Python | 3.9.6 | Core checks and generators |
| Lean | 4.29.0 | Formal arithmetic |
| CaDiCaL | 3.0.0, commit `7b99c07f0bcab5824a5a3ce62c7066554017f641` | Small-instance validation and profile proof production |
| GLPK / `glpsol` | 5.0 | Independent LP/MIP parser |
| `drat-trim` | commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` | DRAT-to-LRAT conversion and DRAT replay |
| `lrat-check` | commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` | LRAT replay |

Run:

```sh
python3 scripts/validate_models.py
glpsol --lp models/column_types_9x23_exact_104.lp --check
python3 scripts/replay_certificates.py
python3 scripts/replay_z10_23_certificates.py --output audit/z10_23_sat_replay.json
```

The first command regenerates temporary small CNFs and uses seed `20260704`. The second should report 86 rows, 512 columns, 6,399 matrix nonzeros, and 512 integer variables. The third requires all six small terminal trace checks to report true. The fourth expands ten direct profile cores and every leaf core in three complete-cover archives, converts them to LRAT, checks both stages, and can take substantially longer. Pass `--workers N` to parallelize leaf replay.

To regenerate one of the three cover families from scratch after installing
`python-sat`, CaDiCaL, `drat-trim`, and `lrat-check`:

```sh
python3 search/z10_23_certify.py frontier '3x1,4x2,5x18,6x2' \
  --output build/z10_23 --depth 4
python3 search/z10_23_cube_certify.py '3x1,4x2,5x18,6x2' \
  --catalog build/z10_23/3d1_4d2_5d18_6d2.cubes.jsonl \
  --output build/z10_23 --workers 4
```

The first command performs no SAT search. It writes the complete canonical
depth-four frontier: 1,479 prefixes for $3^1 4^2 5^{18}6^2$ and 773 prefixes
for each of the other two cover profiles. The second command does not trust
the catalog's leaf labels: it recomputes trie completeness, independently
proves every prefix formula, performs both replay stages, and writes the
deterministic archive and proof index. Thus no conflict budget, timeout, or
incremental solver verdict is part of the certificate.

External output is summarized in [`audit/model_validation.json`](../audit/model_validation.json), [`audit/certificate_replay.json`](../audit/certificate_replay.json), and [`audit/z10_23_sat_replay.json`](../audit/z10_23_sat_replay.json). Temporary paths and timing noise are intentionally not stored.

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
- extended finite-table report;
- profile CNFs, ten direct compressed DRAT cores, and three complete cube-cover proof archives for $Z(10,23)$, with oversized compressed streams stored as hash-bound sub-100 MB byte chunks; and
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

Then, if the optional tools are installed, run the four external commands above. No command requires a file outside the cloned repository.
