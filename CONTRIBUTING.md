# Reviewing and contributing

Independent scrutiny is especially welcome because these results have not completed peer review.

## Suggested review order

1. Read [`analysis/result_status.json`](analysis/result_status.json) so the theorem/candidate boundary is explicit.
2. Read [`docs/PROOF.md`](docs/PROOF.md) and the five other established case dossiers without consulting the code.
3. Run `make verify`; compare the six case certificates with their proof sections.
4. Inspect [`lean/README.md`](lean/README.md), then run `lake build` inside `lean/`.
5. Treat generic SAT/MIP models as regression artifacts, not upper-bound proofs.
6. Review [`docs/PROOF_Z10_23.md`](docs/PROOF_Z10_23.md) and [`docs/PROOF_Z11_23.md`](docs/PROOF_Z11_23.md) as candidate dossiers. Do not report their proposed equalities as established.
7. Review [`docs/NEW_BOUNDS.md`](docs/NEW_BOUNDS.md) and the explicit 35-cell frontier.

## Useful issue reports

Please report:

- a mathematical gap or ambiguous quantifier;
- an earlier source for any claimed result;
- a missing or previously solved cell in the 35-case frontier;
- a witness or certificate mutation that is incorrectly accepted;
- a mismatch between prose, Python, JSON, or Lean;
- a deterministic artifact that does not regenerate byte-for-byte; or
- any wording that promotes a candidate beyond its evidence.

For a mathematical correction, identify the section and displayed equation. For a reproducibility failure, include the command, tool version, exit code, and complete error output, without private paths or credentials.

## Change discipline

Changes to established proofs must update the case certificate, mutation tests, Lean arithmetic when in scope, proof/code map, and audit boundary. Candidate promotion additionally requires a complete replayable proof family, independent audit, machine-readable status change, and removal of every provisional caveat in one coherent commit.

Generated models and analyses should be changed through their generators. Run `make verify` before submitting a patch.
