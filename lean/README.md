# Lean end-to-end proofs

The Lean 4.29.0 subproject models Boolean matrices, proves counting and deletion lemmas, checks all eight embedded witnesses, and closes three exact values without importing JSON, SAT, Python, or certificate output. Computational upper bounds remain visible parameters rather than hidden axioms.

| Result | Lean status | Public theorem |
|---|---|---|
| $Z(9,23)=103$ | end-to-end | `Zarankiewicz.Exact.Z9_23.exact_value` |
| $Z(10,21)=106$ | conditional on $Z(9,21)\le96$ | `Zarankiewicz.Exact.DeletionClosures.z10_21_exact` |
| $Z(10,22)=110$ | end-to-end | `Zarankiewicz.Exact.Z10_22.exact_value` |
| $Z(10,23)=112$ | conditional on the external certificate bound $Z(10,23)\le112$ | `Zarankiewicz.Exact.DeletionClosures.z10_23_exact_of_upper` |
| $Z(11,19)=106$ | conditional on $Z(11,18)\le101$ | `Zarankiewicz.Exact.DeletionClosures.z11_19_exact` |
| $Z(11,20)=111$ | conditional on $Z(11,18)\le101$ | `Zarankiewicz.Exact.DeletionClosures.z11_20_exact` |
| $Z(11,23)=123$ | conditional on $Z(10,23)\le112$; deletion formalized | `Zarankiewicz.Exact.DeletionClosures.z11_23_exact` |
| $Z(12,23)=134$ | end-to-end | `Zarankiewicz.Exact.Z12_23.exact_value` |
| $Z(13,23)\le144$ | end-to-end upper bound | `Zarankiewicz.Bounds.Z13_23.upper_bound` |

All eight lower-bound matrices are embedded as column bitmasks in [`Zarankiewicz/Witnesses.lean`](Zarankiewicz/Witnesses.lean). Ordinary kernel reduction (`by decide`) checks their weights and $K_{3,3}$-freeness. The upper bounds for $(9,23)$, $(10,22)$, and $(12,23)$ are fully combinatorial Lean proofs. In particular, the $(10,22)$ proof replaces the old Python orbit enumerations with row/pair incidence identities and `omega`.

The conditional theorem types intentionally expose their inputs. Tan's bounds $Z(9,21)\le96$ and $Z(11,18)\le101$ were obtained by SAT classification; this branch neither imports their certificates nor declares them as axioms. The $Z(10,23)\le112$ premise is likewise supplied by the repository's DRAT/LRAT and VIPR certificate chain, not by Lean. Given these premises, [`Zarankiewicz/Deletion.lean`](Zarankiewicz/Deletion.lean) proves the complete averaging arguments on matrices, including $Z(11,23)\le123$.

The project uses Mathlib for finite-set infrastructure and tactics. It contains no `sorry`, `admit`, project `axiom`, or `native_decide`. External bounds appear only as ordinary theorem parameters.

## Build and audit

```bash
lake build
lake env lean AxiomAudit.lean
```

[`AxiomAudit.lean`](AxiomAudit.lean) prints dependencies for the public end-to-end and conditional theorems. The observed dependencies are only Lean's standard `propext`, `Classical.choice`, and `Quot.sound`, chiefly through `omega`.

For a faster edit/check loop, build only the changed module:

```bash
lake build +Zarankiewicz.Exact.Z10_22:olean
lake build +Zarankiewicz.Exact.Z12_23:olean
lake build +Zarankiewicz.Exact.DeletionClosures:olean
```

Lake then reuses the shared cached `.olean` files instead of recompiling every case.
