# Recorded audit reports

- [`model_validation.json`](model_validation.json) records validation of the generic decision encodings.
- [`certificate_replay.json`](certificate_replay.json) records DRAT and LRAT replay for the three terminal cases in the established $Z(9,23)$ proof.
- [`lean_axioms.txt`](lean_axioms.txt) records the Lean axiom audit for arithmetic kernels. The audit does not claim that Lean replays the $Z(10,23)$ external certificates.

The self-contained $Z(10,23)$ integrity report is reproduced by `make z10-23-certificate`. A full semantic replay report can be written to `audit/z10_23_sat_replay.json` after downloading the large release assets; it is reproducible rather than committed as a substitute for the underlying proofs.

Recorded reports omit temporary paths, timing data, and host identifiers. They are evidence of specific runs, not substitutes for rerunning the commands. See [`docs/ADVERSARIAL_AUDIT.md`](../docs/ADVERSARIAL_AUDIT.md).
