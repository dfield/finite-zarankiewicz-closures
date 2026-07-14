# Checked witness matrices

Every CSV is an independently checked lower-bound witness. Six match established upper bounds; two support candidates only.

| File | Dimensions | Ones | Publication role |
|---|---:|---:|---|
| [`z9_23_103_matrix.csv`](z9_23_103_matrix.csv) | $9\times23$ | 103 | exact-value witness |
| [`z10_21_106_matrix.csv`](z10_21_106_matrix.csv) | $10\times21$ | 106 | exact-value witness |
| [`z10_22_110_matrix.csv`](z10_22_110_matrix.csv) | $10\times22$ | 110 | exact-value witness |
| [`z10_23_112_matrix.csv`](z10_23_112_matrix.csv) | $10\times23$ | 112 | **candidate lower bound only** |
| [`z11_19_106_matrix.csv`](z11_19_106_matrix.csv) | $11\times19$ | 106 | exact-value witness |
| [`z11_20_111_matrix.csv`](z11_20_111_matrix.csv) | $11\times20$ | 111 | exact-value witness |
| [`z11_23_123_matrix.csv`](z11_23_123_matrix.csv) | $11\times23$ | 123 | **candidate lower bound only** |
| [`z12_23_134_matrix.csv`](z12_23_134_matrix.csv) | $12\times23$ | 134 | exact-value witness |

The package checker uses row-triple capacities; the independent scanner examines all candidate $3\times3$ submatrices. Run both paths with:

```bash
python3 scripts/verify_witness.py
python3 scripts/verify_witness_independent.py
PYTHONPATH=src python3 scripts/check_extended_results.py --check
python3 scripts/verify_extended_witnesses_independent.py
```

A valid matrix proves only a lower bound. In particular, the 112- and 123-one files do not establish their proposed equalities without matching upper bounds.

Bhan--Nobili--Langer publicly supplied five of the matching lower bounds. The provenance of every construction is discussed in [`docs/LITERATURE_REVIEW.md`](../docs/LITERATURE_REVIEW.md).
