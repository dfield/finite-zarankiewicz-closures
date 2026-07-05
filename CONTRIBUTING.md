# Reviewing and contributing

Independent scrutiny is especially welcome because this repository presents four new exact finite results and has not yet completed peer review.

## Suggested review order

1. Read [`docs/PROOF.md`](docs/PROOF.md) without consulting the code. Check the two double counts, the penalty-based degree classification, and each marked-row residue.
2. Run `make witness` and inspect the explicit matrix in [`data/`](data/).
3. Run `make certificate` and compare all four case certificates with their proof sections.
4. Run `make test`; the tests include deliberate corruptions and exhaustive small cardinality checks.
5. Inspect the four-case formalization boundary in [`lean/README.md`](lean/README.md), then run `lake build` inside `lean/`.
6. Treat the SAT/MIP models and DRAT/LRAT traces as corroborating evidence, not substitutes for Step 1.
7. For the three additional results, read [`docs/EXTENDED_RESULTS.md`](docs/EXTENDED_RESULTS.md), run `make extended`, and inspect the explicit 37-cell claim boundary.

## Useful issue reports

Please open an issue for any of the following:

- a mathematical gap or ambiguous quantifier in either proof document;
- an earlier source that closes any of these exact cases or contains one of the arguments;
- a missing or previously solved cell in the remaining 37-case frontier;
- a witness checker or certificate mutation that is incorrectly accepted;
- a mismatch between a proof equation and its Python or Lean counterpart;
- a deterministic artifact that does not regenerate byte-for-byte; or
- documentation that overstates the scope of a computational or formal check.

For a proposed mathematical correction, include the section and displayed equation. For a reproducibility failure, include the command, interpreter or checker version, exit code, and complete error output. Please do not include private machine paths or credentials in an issue.

## Change discipline

Changes to the proofs should be accompanied by corresponding updates to:

- the exact certificate and its mutation tests;
- the Lean arithmetic file when the changed step is inside its declared scope;
- the proof/code map in [`docs/METHODS.md`](docs/METHODS.md); and
- the audit limitations if the trust boundary changes.

Generated models and analyses should be changed through their generators. Run `make verify` before submitting a patch.
