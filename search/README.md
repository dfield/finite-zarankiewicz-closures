# Discovery tools (non-load-bearing)

These programs were used to *discover* the results documented in
[`docs/NEW_BOUNDS.md`](../docs/NEW_BOUNDS.md). None of them is part of any
proof: every claimed bound is verified independently by
[`scripts/check_new_bounds.py`](../scripts/check_new_bounds.py) (standard
library only), and every witness matrix is checked by exhaustive scan.

| File | Purpose | Dependencies |
|---|---|---|
| `zsearch.c` | free-form simulated annealing for $K_{3,3}$-free matrices | C99, `gcc -O3` |
| `zsearch2.c` | annealing with a fixed column-degree profile (the workhorse; found the $Z(11,19)$ witness) | C99 |
| `drive.py` | profile enumeration + parallel search driver + independent verifier | Python 3.9+ |
| `filters.py` | the general row/pair deficit profile filter behind the two new upper-bound theorems | Python 3.9+ |
| `sat_tool.py` | per-profile SAT feasibility (sequential-counter cardinalities, double-lex symmetry breaking) | `pip install python-sat` |
| `tier2.py` | configuration-level residue filter (found the five profile kills behind the $Z(12,23,3,3)\le134$ theorem) | Python 3.9+ |
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
theorems. `sat_tool.py` exits 0/1/2 for SAT/UNSAT/unknown; its verdicts are
recorded in `docs/NEW_BOUNDS.md` only as research pointers.

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

An `UNSAT` line without the emitted formula, its hash, and a checked proof
trace is not accepted as a repository theorem.
