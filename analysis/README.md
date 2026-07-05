# Diagnostic analysis

This directory explains where the previous upper-bound machinery loses the final edge.

- [`dgh_boundary.json`](dgh_boundary.json) evaluates the full Davies--Gill--Horsley degree-count constraints with exact rational arithmetic. Its optimum is \(314/3\), so integer rounding gives 104.
- [`local_kernel_catalog.csv`](local_kernel_catalog.csv) lists the complete row-symmetry quotient of the one-column kernels used to extract the proof.
- [`extended_results.json`](extended_results.json) records the 44-cell boundary from Bhan--Nobili--Langer, the seven cells closed by that paper and this repository, the 37-cell remaining frontier, three checked matrices, and the recomputed $Z(10,22,3,3)$ certificate.

The catalog does not claim to enumerate arbitrary multi-column submatrices. Its scope is precisely the one-column restrictions, ambient degree types, and marked-row membership types described in [`docs/METHODS.md`](../docs/METHODS.md).

Regenerate or check both artifacts with:

```sh
python3 scripts/analyze_boundary.py --check
```

This analysis is diagnostic. The theorem itself follows from the elementary proof and does not depend on a transcription of the DGH inequalities.

Check the follow-on report separately with:

```sh
PYTHONPATH=src python3 scripts/check_extended_results.py --check
```
