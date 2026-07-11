# Discovery and optional proof-generation tools

Most of these programs were used to *discover* the results documented in
[`docs/NEW_BOUNDS.md`](../docs/NEW_BOUNDS.md). Unlogged verdicts are not
proofs: the elementary bounds are rechecked by
[`scripts/check_new_bounds.py`](../scripts/check_new_bounds.py), the
$Z(10,23)$ SAT case carries a DRAT core replayed through independent LRAT checking, and every
witness matrix is checked by exhaustive scan.

| File | Purpose | Dependencies |
|---|---|---|
| `zsearch.c` | free-form simulated annealing for $K_{3,3}$-free matrices | C99, `gcc -O3` |
| `zsearch2.c` | annealing with a fixed column-degree profile (the workhorse; found the $Z(11,19)$ witness) | C99 |
| `drive.py` | profile enumeration + parallel search driver + independent verifier | Python 3.9+ |
| `filters.py` | the general row/pair deficit profile filter behind the two new upper-bound theorems | Python 3.9+ |
| `sat_tool.py` | per-profile SAT feasibility (sequential-counter cardinalities, double-lex symmetry breaking) | `pip install python-sat` |
| `tier2.py` | configuration-level residue filter (found the five profile kills behind the $Z(12,23,3,3)\le134$ theorem) | Python 3.9+ |
| `z10_23_certify.py` | deterministic profile CNFs, complete fixed row-stabilizer frontiers, optional adaptive search cubes, and direct checked compressed DRAT cores for $Z(10,23,3,3)=112$ | `python-sat`, CaDiCaL, `drat-trim`, `lrat-check` |
| `z10_23_cube_certify.py` | completeness checking plus proof production and independent replay for full or partially fixed canonical cube leaves | CaDiCaL, `drat-trim`, `lrat-check` |
| `z10_23_residual_refine.py` | deterministic structural refinement of timeout manifests, with complete-cover rechecking and reuse/parent-to-child maps | Python standard library |
| `z10_23_cube_finalize.py` | deterministic validation and indexing of a proof family produced in distributed shards | CaDiCaL |
| `lp_dgh.py` | exact-rational Davies--Gill--Horsley LP, reproduces their published table | Python 3.9+ |

Build the annealers with:

```sh
gcc -O3 -march=native -o zsearch  zsearch.c  -lm
gcc -O3 -march=native -o zsearch2 zsearch2.c -lm
```

Example (reproduces the shape of the $Z(11,19)$ discovery; annealing is
seeded, so the exact matrix depends on the seed):

```sh
./zsearch2 11 19 "5x8,6x11" 60 1 witness.csv
python3 drive.py 11 19 106 60
```

`filters.py` run as a script re-derives the profile kills used in the two
elementary theorems. `sat_tool.py` exits 0/1/2 for SAT/UNSAT/unknown; an
untraced verdict from that exploratory tool remains only a research pointer.

For an auditable SAT rerun, emit the exact DIMACS input first. At 113 ones,
the established neighboring values imply that every row has degree at least
10 and every column has degree at least 3; profiles violating the latter bound
should be eliminated before solving.

```sh
python3 sat_tool.py 10 23 "4x2,5x21" \
  --min-row-degree 10 --cnf profile.cnf --emit-only
cadical profile.cnf profile.drat
drat-trim profile.cnf profile.drat
```

For the completed case, list the exact SAT scope, regenerate a direct proof,
write a fixed proof frontier, or generate an adaptive cube partition for
search experiments:

```sh
python3 z10_23_certify.py list
python3 z10_23_certify.py direct '4x4,5x18,7x1' --output build/z10_23
python3 z10_23_certify.py frontier '3x1,4x2,5x18,6x2' \
  --depth 4 --output build/z10_23
python3 z10_23_certify.py cubes '4x2,5x21' --output build/z10_23
```

The fixed frontier command performs no SAT search. Its catalog becomes proof
only when `z10_23_cube_certify.py` independently refutes every retained leaf
and the standard-library trie checker confirms completeness. A difficult
frontier leaf may be replaced by partial assignments in its immediate next
column. The checker expands each such partial leaf over every matching
canonical support and still requires an exact, prefix-free partition, so this
adaptive refinement changes proof granularity without trusting a solver
verdict for coverage.

For a distributed timeout pass, refine only the recorded residual leaves while
retaining a complete global catalog:

```sh
python3 z10_23_residual_refine.py '3x1,4x4,5x14,6x4' \
  --catalog build/r6/cubes.jsonl \
  --residual build/r6/unresolved.shard-00.jsonl \
  --residual build/r6/unresolved.shard-01.jsonl \
  --residual build/r6/unresolved.shard-02.jsonl \
  --output build/r7 --split-bits 1 --shards 3
```

The command checks the input cover, requires every residual record to match
its indexed catalog leaf, bisects that leaf inside its immediate next column,
and checks the resulting complete cover before publishing any task files.

Proof conversion, hashing, and compression stream their large intermediate
files. Direct traces at or above GitHub's 100 MB repository-file limit are
written as ordered 95,000,000-byte parts. The much larger cube-proof archives
are stored as release assets; small checked-in sidecars bind every asset part,
its exact concatenation, and the deterministic PAX-tar/XZ settings. If a completed
CaDiCaL run left a raw trace after an interrupted parent process, pass
`--reuse-raw` to `direct` to validate and convert that trace without solving
the profile again. Incremental assumption runs over a cube catalog are useful
search evidence, but their raw trace is not accepted as a proof of the unsplit
base CNF. Every checked-in trace is produced directly from the corresponding
base formula and replayed against that same file.

An `UNSAT` line without the emitted formula, its hash, and a checked proof
trace is not accepted as a repository theorem. The checked-in CNFs and DRAT/LRAT
files, rather than the generator's authority, are the load-bearing SAT
artifacts.
