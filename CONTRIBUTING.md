# Reviewing and contributing

Independent scrutiny is especially welcome because these results have not completed peer review.

## Suggested review order

1. Read [`analysis/result_status.json`](analysis/result_status.json) for the theorem boundary.
2. Read the eight proof dossiers without consulting the code.
3. Run `make verify`; compare all eight case certificates with their proof sections.
4. Inspect [`lean/README.md`](lean/README.md), then run `lake build` inside `lean/`.
5. Treat generic SAT/MIP models as regression artifacts, not upper-bound proofs.
6. Review the full $Z(10,23)$ trust chain in [`docs/PROOF_Z10_23.md`](docs/PROOF_Z10_23.md), then run `make z10-23-certificate`.
7. If resources permit, perform the 25.3 GB external-checker replay described in [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md).
8. Review [`docs/NEW_BOUNDS.md`](docs/NEW_BOUNDS.md) and the explicit 33-cell frontier.

## Useful issue reports

Please report:

- a mathematical gap or ambiguous quantifier;
- an earlier source for any claimed result;
- a missing or previously solved cell in the 33-case frontier;
- a witness, cover, formula-binding, release, or certificate mutation that is incorrectly accepted;
- a mismatch between prose, Python, JSON, Lean, or release metadata;
- a deterministic artifact that does not regenerate byte-for-byte; or
- wording that overstates the Lean or external-certificate boundary.

For a mathematical correction, identify the section and displayed equation. For a reproducibility failure, include the command, tool version, exit code, and complete error output without private paths or credentials.

## Change discipline

Changes to established proofs must update the case certificate, mutation tests, Lean arithmetic when in scope, proof/code map, analysis boundary, and adversarial audit. Changes to the $Z(10,23)$ proof family must also update every affected manifest and release sidecar coherently; never rewrite a proof asset without updating its bound hashes.

Generated models and analyses should be changed through their generators. Run `make verify` before submitting a patch.
