# Recorded audit reports

- [`model_validation.json`](model_validation.json) records validation of the generic decision encodings.
- [`certificate_replay.json`](certificate_replay.json) records DRAT and LRAT replay for the three terminal cases in the established $Z(9,23)$ proof.
- [`lean_axioms.txt`](lean_axioms.txt) records the Lean axiom audit for arithmetic kernels. Candidate arithmetic theorems in that report do not establish their missing combinatorial or SAT premises.

There is deliberately no completed `z10_23_sat_replay.json` in this publication boundary. Such a report must cover all thirteen surviving profiles before the candidate can be promoted.

Recorded reports omit temporary paths, timing data, and host identifiers. They are evidence of specific runs, not substitutes for rerunning the commands. See [`docs/ADVERSARIAL_AUDIT.md`](../docs/ADVERSARIAL_AUDIT.md).
