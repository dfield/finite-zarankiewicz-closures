# Exact decision models for all eight cases

Every equality has two deterministic formulations at the first excluded weight:

| Exact value | Excluded target | Direct cell CNF | Column-support LP/MIP |
|---|---:|---|---|
| $Z(9,23,3,3)=103$ | 104 | [`cells_9x23_exact_104.cnf`](cells_9x23_exact_104.cnf) | [`column_types_9x23_exact_104.lp`](column_types_9x23_exact_104.lp) |
| $Z(10,21,3,3)=106$ | 107 | [`cells_10x21_exact_107.cnf`](cells_10x21_exact_107.cnf) | [`column_types_10x21_exact_107.lp`](column_types_10x21_exact_107.lp) |
| $Z(10,22,3,3)=110$ | 111 | [`cells_10x22_exact_111.cnf`](cells_10x22_exact_111.cnf) | [`column_types_10x22_exact_111.lp`](column_types_10x22_exact_111.lp) |
| $Z(10,23,3,3)=112$ | 113 | [`cells_10x23_exact_113.cnf`](cells_10x23_exact_113.cnf) | [`column_types_10x23_exact_113.lp`](column_types_10x23_exact_113.lp) |
| $Z(11,19,3,3)=106$ | 107 | [`cells_11x19_exact_107.cnf`](cells_11x19_exact_107.cnf) | [`column_types_11x19_exact_107.lp`](column_types_11x19_exact_107.lp) |
| $Z(11,20,3,3)=111$ | 112 | [`cells_11x20_exact_112.cnf`](cells_11x20_exact_112.cnf) | [`column_types_11x20_exact_112.lp`](column_types_11x20_exact_112.lp) |
| $Z(11,23,3,3)=123$ | 124 | [`cells_11x23_exact_124.cnf`](cells_11x23_exact_124.cnf) | [`column_types_11x23_exact_124.lp`](column_types_11x23_exact_124.lp) |
| $Z(12,23,3,3)=134$ | 135 | [`cells_12x23_exact_135.cnf`](cells_12x23_exact_135.cnf) | [`column_types_12x23_exact_135.lp`](column_types_12x23_exact_135.lp) |

The cell models contain one variable per matrix entry, every forbidden all-one $3\times3$ clause, and a fully defined exact-cardinality circuit. The column models contain one integer variable per possible exact support and one capacity constraint per row triple.

[`manifest.json`](manifest.json) records dimensions and hashes for all sixteen models. Regenerate or byte-check them with:

```sh
python3 scripts/generate_models.py --check
```

These generic models are transparent decision formulations and regression artifacts, not the logical basis of the upper bounds. The profile-specific CNFs under [`z10_23/`](z10_23/) are different: their checked DRAT cores and derived LRAT refutations are a proof component for $Z(10,23)$. The three historical `terminal_*.cnf` files remain scoped to the final marked-row aggregations.
