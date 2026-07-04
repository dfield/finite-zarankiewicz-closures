# Certificates

## Exact mathematical reduction

[`degree_deficit.json`](degree_deficit.json) records the complete finite arithmetic of the upper-bound proof. The checker does not trust its case list: it independently enumerates every degree histogram at weight 104 and penalty at most four, then recomputes all deficits, residues, lower bounds, and aggregate cuts.

```sh
python3 scripts/check_proof_certificate.py
```

This exact-integer JSON/checker pair is the primary replayable certificate for nonexistence at 104.

## Terminal DRAT and LRAT

For each of the three degree profiles, `terminal_CASE.drat` and `terminal_CASE.lrat` certify the unsatisfiability of `models/terminal_CASE.cnf`.

```sh
python3 scripts/replay_certificates.py
```

These traces cover only the last aggregate inequality. They are not a monolithic proof of the cell CNF. The distinction is intentional and documented in [`docs/METHODS.md`](../docs/METHODS.md).
