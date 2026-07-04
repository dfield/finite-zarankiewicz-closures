# Witness data

[`z9_23_103_matrix.csv`](z9_23_103_matrix.csv) is the explicit lower-bound witness for

\[
Z(9,23,3,3)\ge103.
\]

The file has exactly nine rows, 23 comma-separated Boolean entries per row, and 103 ones. Row and column indices used by programs are zero-based; the proof uses ordinary one-based mathematical labels.

Verify it in two independent ways from the repository root:

```sh
python3 scripts/verify_witness.py
python3 scripts/verify_witness_independent.py
```

The first checks the 84 row-triple capacities. The second is standalone and examines all 148,764 candidate \(3\times3\) submatrices. The matrix is also maximal: changing any one of its zero entries to one creates a forbidden submatrix, as tested in `tests/test_matrix.py`.

Bhan, Nobili, and Langer publicly established the 103 lower bound before this repository. See [`docs/LITERATURE_REVIEW.md`](../docs/LITERATURE_REVIEW.md) for attribution and source details.
