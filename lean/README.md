# Lean arithmetic audit

This directory formalizes the finite arithmetic kernel of the proof in [`docs/PROOF.md`](../docs/PROOF.md). It checks:

1. the ten values of \(p(d)=\binom d3-6d+20\);
2. the fact that the penalty budget leaves exactly three degree histograms; and
3. the three modulo-three marked-row contradictions.

It intentionally makes a narrower claim than “the theorem is fully formalized.” The translation from a Boolean matrix to triple capacities and marked-row deficits is still justified by the human double counts and checked independently in Python. Keeping that boundary explicit is preferable to presenting a formal arithmetic endpoint as a complete formalization.

The project uses Lean 4.29.0 and only the bundled `Std` library. There are no external packages, custom axioms, or admitted results.

## Build

From this directory:

```sh
lake build
```

For the audit used in this repository:

```sh
lake env lean ZarankiewiczZ923/ArithmeticKernel.lean
lake env lean AxiomAudit.lean
rg -n '^[[:space:]]*(sorry|admit|axiom)\b|:=[[:space:]]*(by[[:space:]]+)?(sorry|admit)\b' . --glob '*.lean'
```

The first command kernel-checks the source, the second prints every theorem's axiom dependencies, and the final command is a simple guard against accidentally weakening the formalization boundary.
