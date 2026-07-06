# Lean arithmetic audit for all six exact values

This directory formalizes the finite arithmetic kernels for every exact result in the repository.

| Result | Lean coverage |
|---|---|
| $Z(9,23,3,3)=103$ | penalty formula and table, three-profile classification, three marked-row contradictions |
| $Z(10,21,3,3)=106$ | deletion-bound quotient and the excluded-target arithmetic contradiction |
| $Z(10,22,3,3)=110$ | penalty formula and table, four-profile classification, case-B minima table, and four terminal contradictions |
| $Z(11,19,3,3)=106$ | deletion-bound quotient and excluded-target arithmetic contradiction |
| $Z(11,20,3,3)=111$ | both deletion-bound quotients and both excluded-target arithmetic contradictions |
| $Z(12,23,3,3)=134$ | penalty formula, profile classifications at 136 and 135, pair equation, recorded row-type minimum, and five terminal contradictions |
| $Z(13,23,3,3)\le144$ | penalty formula, three-profile classification, and marked-row deficit endpoint |

The project intentionally makes a narrower claim than “the six exact theorems are fully formalized.” The Boolean-matrix definitions, combinatorial double counts, deletion lemma, witness CSVs, and the finite row-symmetry/row-type enumerations remain in the human-readable proofs and independently checked Python certificates. Lean checks the arithmetic consequences supplied by those layers.

The project pins Lean 4.29.0, uses only the bundled `Std` library, and contains no external packages, custom axioms, or admitted results.

## Build

From this directory:

```sh
lake build
lake env lean AxiomAudit.lean
```

For the source-level admission guard used by the audit:

```sh
rg -n '^[[:space:]]*(sorry|admit|axiom)\b|:=[[:space:]]*(by[[:space:]]+)?(sorry|admit)\b' . --glob '*.lean'
```

[`AxiomAudit.lean`](AxiomAudit.lean) prints every theorem's axiom dependencies. Executable tables and quotient computations use no axioms; the `omega` proofs use Lean's standard `propext`, `Classical.choice`, and `Quot.sound` principles where reported.
