# Diagnostic analysis

This directory explains where the previous upper-bound machinery loses the final edge.

- [`dgh_boundary.json`](dgh_boundary.json) evaluates the full Davies--Gill--Horsley degree-count constraints with exact rational arithmetic. Its optimum is \(314/3\), so integer rounding gives 104.
- [`local_kernel_catalog.csv`](local_kernel_catalog.csv) lists the complete row-symmetry quotient of the one-column kernels used to extract the proof.

The catalog does not claim to enumerate arbitrary multi-column submatrices. Its scope is precisely the one-column restrictions, ambient degree types, and marked-row membership types described in [`docs/METHODS.md`](../docs/METHODS.md).

Regenerate or check both artifacts with:

```sh
python3 scripts/analyze_boundary.py --check
```

This analysis is diagnostic. The theorem itself follows from the elementary proof and does not depend on a transcription of the DGH inequalities.
