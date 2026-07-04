# Exact decision models

This directory contains deterministic formulations of the hypothetical 104-one matrix.

## `cells_9x23_exact_104.cnf`

The DIMACS file has one base variable per matrix cell, a clause for every forbidden all-one \(3\times3\) submatrix, and a sequential threshold circuit imposing exactly 104 ones.

Metadata in [`manifest.json`](manifest.json) records:

- 207 base variables;
- 32,654 total variables;
- 148,764 forbidden-submatrix clauses; and
- 277,931 total clauses.

## `column_types_9x23_exact_104.lp`

The LP/MIP file has one integer variable for each of the 512 column supports. It fixes 23 columns and total degree 104, then limits every one of the 84 row triples to two containing columns.

## Terminal CNFs

The three `terminal_*.cnf` files encode only the final aggregate contradictions from the degree-deficit proof. Their corresponding DRAT/LRAT traces are under [`certificates/`](../certificates/).

## Regeneration

```sh
python3 scripts/generate_models.py --check
```

Remove `--check` to rewrite the two main models and their manifest. The terminal CNFs are retained certificate inputs rather than products of this generator. Full specifications and trust boundaries are in [`docs/METHODS.md`](../docs/METHODS.md).
