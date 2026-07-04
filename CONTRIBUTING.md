# Reviewing and contributing

Independent scrutiny is especially welcome because this repository presents a new exact finite result and has not yet completed peer review.

## Suggested review order

1. Read [`docs/PROOF.md`](docs/PROOF.md) without consulting the code. Check the two double counts, the penalty-based degree classification, and each marked-row residue.
2. Run `make witness` and inspect the explicit matrix in [`data/`](data/).
3. Run `make certificate` and compare the JSON cases with the proof.
4. Run `make test`; the tests include deliberate corruptions and exhaustive small cardinality checks.
5. Inspect the explicit formalization boundary in [`lean/README.md`](lean/README.md), then run `lake build` inside `lean/`.
6. Treat the SAT/MIP models and DRAT/LRAT traces as corroborating evidence, not substitutes for Step 1.

## Useful issue reports

Please open an issue for any of the following:

- a mathematical gap or ambiguous quantifier in the proof;
- an earlier source that closes this exact case or contains the marked-row argument;
- a witness checker or certificate mutation that is incorrectly accepted;
- a mismatch between a proof equation and its Python or Lean counterpart;
- a deterministic artifact that does not regenerate byte-for-byte; or
- documentation that overstates the scope of a computational or formal check.

For a proposed mathematical correction, include the section and displayed equation. For a reproducibility failure, include the command, interpreter or checker version, exit code, and complete error output. Please do not include private machine paths or credentials in an issue.

## Change discipline

Changes to the proof should be accompanied by corresponding updates to:

- the exact certificate and its mutation tests;
- the Lean arithmetic file when the changed step is inside its declared scope;
- the proof/code map in [`docs/METHODS.md`](docs/METHODS.md); and
- the audit limitations if the trust boundary changes.

Generated models and analyses should be changed through their generators. Run `make verify` before submitting a patch.
