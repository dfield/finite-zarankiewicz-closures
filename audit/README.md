# Recorded audit reports

- [`model_validation.json`](model_validation.json) records CaDiCaL agreement on the known $3\times4$ case and 30 seeded fixed matrices.
- [`certificate_replay.json`](certificate_replay.json) records successful DRAT and LRAT replay for all three terminal cases.
- `lean_axioms.txt` records the output of the Lean axiom audit.

The reports omit temporary paths, timing data, and host identifiers. They are evidence of specific runs, not substitutes for rerunning the commands. The audit narrative and limitations are in [`docs/ADVERSARIAL_AUDIT.md`](../docs/ADVERSARIAL_AUDIT.md).
