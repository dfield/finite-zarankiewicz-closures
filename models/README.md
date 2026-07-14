# Decision models for six established cases and two candidates

Each tracked case has deterministic formulations at its proposed first excluded weight:

| Result or candidate | Status | Target | Direct cell CNF | Column-support LP/MIP |
|---|---|---:|---|---|
| $Z(9,23)=103$ | established | 104 | [`cells_9x23_exact_104.cnf`](cells_9x23_exact_104.cnf) | [`column_types_9x23_exact_104.lp`](column_types_9x23_exact_104.lp) |
| $Z(10,21)=106$ | established | 107 | [`cells_10x21_exact_107.cnf`](cells_10x21_exact_107.cnf) | [`column_types_10x21_exact_107.lp`](column_types_10x21_exact_107.lp) |
| $Z(10,22)=110$ | established | 111 | [`cells_10x22_exact_111.cnf`](cells_10x22_exact_111.cnf) | [`column_types_10x22_exact_111.lp`](column_types_10x22_exact_111.lp) |
| $Z(10,23)=112$ | **candidate** | 113 | [`cells_10x23_exact_113.cnf`](cells_10x23_exact_113.cnf) | [`column_types_10x23_exact_113.lp`](column_types_10x23_exact_113.lp) |
| $Z(11,19)=106$ | established | 107 | [`cells_11x19_exact_107.cnf`](cells_11x19_exact_107.cnf) | [`column_types_11x19_exact_107.lp`](column_types_11x19_exact_107.lp) |
| $Z(11,20)=111$ | established | 112 | [`cells_11x20_exact_112.cnf`](cells_11x20_exact_112.cnf) | [`column_types_11x20_exact_112.lp`](column_types_11x20_exact_112.lp) |
| $Z(11,23)=123$ | **candidate** | 124 | [`cells_11x23_exact_124.cnf`](cells_11x23_exact_124.cnf) | [`column_types_11x23_exact_124.lp`](column_types_11x23_exact_124.lp) |
| $Z(12,23)=134$ | established | 135 | [`cells_12x23_exact_135.cnf`](cells_12x23_exact_135.cnf) | [`column_types_12x23_exact_135.lp`](column_types_12x23_exact_135.lp) |

The cell models contain one variable per matrix entry, every forbidden all-one $3\times3$ clause, and an exact-cardinality circuit. The column models use one integer variable per support and one capacity constraint per row triple.

[`manifest.json`](manifest.json) records dimensions, hashes, and `publication_status` for all sixteen files. Regenerate or byte-check them with:

```bash
python3 scripts/generate_models.py --check
```

These are decision formulations and regression artifacts, not unsatisfiability certificates. This distinction is decisive for the two candidate rows. The three historical `terminal_*.cnf` files are scoped only to terminal aggregations in the $Z(9,23)$ proof.
