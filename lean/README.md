# Lean arithmetic audit

Lean checks arithmetic kernels for the six established exact values, the $Z(13,23)\le144$ bound, and selected arithmetic implications used in the two candidate dossiers.

| Result | Status | Lean coverage |
|---|---|---|
| $Z(9,23)=103$ | established | penalty table, profile classification, marked-row contradictions |
| $Z(10,21)=106$ | established | deletion quotient and excluded-target arithmetic |
| $Z(10,22)=110$ | established | penalty table, profile classification, finite minima, terminal contradictions |
| $Z(10,23)=112$ | **candidate** | arithmetic profile-reduction endpoints only |
| $Z(11,19)=106$ | established | deletion quotient and excluded-target arithmetic |
| $Z(11,20)=111$ | established | two deletion quotients and contradictions |
| $Z(11,23)=123$ | **candidate** | conditional deletion quotient; the $Z(10,23)\le112$ premise is not supplied |
| $Z(12,23)=134$ | established | classifications at 136 and 135, pair equation, row-type minimum, terminal contradictions |
| $Z(13,23)\le144$ | established bound | profile classification and marked-row endpoint |

The project does not claim end-to-end formalization. Boolean-matrix definitions, combinatorial double counts, deletion premises, witnesses, finite enumerations, and SAT replay live outside Lean. A checked arithmetic implication cannot promote a candidate whose premise is missing.

The project pins Lean 4.29.0, uses only bundled `Std`, and contains no custom axioms or admitted results.

```bash
lake build
lake env lean AxiomAudit.lean
```

[`AxiomAudit.lean`](AxiomAudit.lean) prints theorem dependencies. Executable tables and quotient computations use no axioms; `omega` proofs use Lean's standard principles where reported.
