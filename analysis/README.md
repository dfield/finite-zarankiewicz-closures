# Diagnostic and status analysis

- [`result_status.json`](result_status.json) is the authoritative publication boundary: six exact values, one additional upper bound, and two provisional candidates.
- [`extended_results.json`](extended_results.json) reconstructs the 44-cell paper boundary, records 9 exact cells and the 35-cell remaining frontier, tags seven additional matrices by role, and recomputes the finite certificates.
- [`new_bounds.json`](new_bounds.json) gives the conservative propagated table. It uses candidate matrices as lower bounds but never as exact seeds.
- [`sat_cross_check.json`](sat_cross_check.json) records the $Z(10,23)$ arithmetic progress, missing certificate, and historical untraced sweep.
- [`dgh_boundary.json`](dgh_boundary.json) evaluates the Davies--Gill--Horsley degree-count relaxation for $Z(9,23)$.
- [`local_kernel_catalog.csv`](local_kernel_catalog.csv) lists the row-symmetry quotient used in the $Z(9,23)$ proof.

Regenerate or check the generated analyses with:

```bash
python3 scripts/analyze_boundary.py --check
PYTHONPATH=src python3 scripts/check_extended_results.py --check
python3 scripts/check_new_bounds.py --check
```

The DGH relaxation and model catalogs are diagnostic. The exact claims rest on their case-specific proofs and certificates.
