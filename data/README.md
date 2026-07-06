# Witness data

[`z9_23_103_matrix.csv`](z9_23_103_matrix.csv) is the explicit lower-bound witness for

$$
Z(9,23,3,3)\ge103.
$$

The file has exactly nine rows, 23 comma-separated Boolean entries per row, and 103 ones. Row and column indices used by programs are zero-based; the proof uses ordinary one-based mathematical labels.

Verify it in two independent ways from the repository root:

```sh
python3 scripts/verify_witness.py
python3 scripts/verify_witness_independent.py
```

The first checks the 84 row-triple capacities. The second is standalone and examines all 148,764 candidate $3\times3$ submatrices. The matrix is also maximal: changing any one of its zero entries to one creates a forbidden submatrix, as tested in `tests/test_matrix.py`.

Bhan, Nobili, and Langer publicly established the 103 lower bound before this repository. See [`docs/LITERATURE_REVIEW.md`](../docs/LITERATURE_REVIEW.md) for attribution and source details.

## Additional witnesses

Five further matrices support the extended finite-table results:

| File | Dimensions | Ones | Role |
|---|---:|---:|---|
| [`z10_21_106_matrix.csv`](z10_21_106_matrix.csv) | $10\times21$ | 106 | Lower bound matching the deletion upper bound |
| [`z10_22_110_matrix.csv`](z10_22_110_matrix.csv) | $10\times22$ | 110 | Lower bound matching the pair-deficit upper bound |
| [`z11_19_106_matrix.csv`](z11_19_106_matrix.csv) | $11\times19$ | 106 | Lower bound matching the deletion upper bound from $Z(11,18,3,3)=101$ |
| [`z11_20_111_matrix.csv`](z11_20_111_matrix.csv) | $11\times20$ | 111 | Lower bound matching the two-step deletion upper bound |
| [`z12_23_134_matrix.csv`](z12_23_134_matrix.csv) | $12\times23$ | 134 | Lower bound matching the two-stage deficit theorem $Z(12,23,3,3)\le134$ |

The 110-one matrix is row-regular with row sum 11, and every row triple occurs in exactly two columns. The $11\times19$ matrix has column degrees $5^86^{11}$ and row degrees $(8,9^3,10^6,11)$; the $12\times23$ matrix has column degrees $4^15^26^{20}$ and row degrees $(11^{10},12^2)$. Their exhaustive direct scans inspect 159,885 and 389,620 candidate $3\times3$ submatrices respectively.

Verify all five additional matrices with both the package checker and the independent direct scanner:

```sh
PYTHONPATH=src python3 scripts/check_extended_results.py --check
python3 scripts/verify_extended_witnesses_independent.py
```

Recheck the two later upper-bound theorems and the propagated table with:

```sh
python3 scripts/check_new_bounds.py --check
```
