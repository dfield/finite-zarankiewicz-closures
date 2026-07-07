# Case-specific certificates

Each exact value has a standalone JSON certificate:

| Result | Certificate | Upper-bound mechanism |
|---|---|---|
| $Z(9,23,3,3)=103$ | [`z9_23_103.json`](z9_23_103.json) | marked-row deficit; binds the detailed [`degree_deficit.json`](degree_deficit.json) subcertificate |
| $Z(10,21,3,3)=106$ | [`z10_21_106.json`](z10_21_106.json) | one vertex-deletion step |
| $Z(10,22,3,3)=110$ | [`z10_22_110.json`](z10_22_110.json) | four-profile pair-deficit enumeration |
| $Z(10,23,3,3)=112$ | [`z10_23_112.json`](z10_23_112.json) | arithmetic profile reduction plus replayed DRAT/LRAT certificates |
| $Z(11,19,3,3)=106$ | [`z11_19_106.json`](z11_19_106.json) | one vertex-deletion step |
| $Z(11,20,3,3)=111$ | [`z11_20_111.json`](z11_20_111.json) | two vertex-deletion steps |
| $Z(11,23,3,3)=123$ | [`z11_23_123.json`](z11_23_123.json) | one vertex-deletion step from $Z(10,23)=112$ |
| $Z(12,23,3,3)=134$ | [`z12_23_134.json`](z12_23_134.json) | forced 136-one profile plus five-profile row/pair-deficit enumeration at 135 |

Every certificate includes the explicit witness's dimensions, weight, row and column sums, exhaustive row-triple result, and SHA-256 digest. The upper-bound section is specific to the case. The checker regenerates these fields rather than trusting the stored JSON:

```sh
python3 scripts/check_case_certificates.py --check
```

Mutation tests alter each case certificate and require rejection.

The non-exact frontier claim $Z(13,23,3,3)\le144$ has its own upper-bound-only certificate, [`z13_23_upper_144.json`](z13_23_upper_144.json). Check it with:

```sh
python3 scripts/check_frontier_certificate.py --check
```

## Terminal DRAT and LRAT

The six historical DRAT/LRAT files replay the three terminal aggregations in the marked-row proof. They do not cover the other reductions or any raw cell CNF.

```sh
python3 scripts/replay_certificates.py
```

## The $Z(10,23)$ SAT proof family

[`z10_23_sat.json`](z10_23_sat.json) binds the thirteen profile CNFs and every compressed DRAT core. These proofs certify the stored profile formulas, not the generic cell CNF. The replay script checks each core with `drat-trim`, converts it to LRAT, and checks the derived trace with `lrat-check`.

Ten formulas are refuted directly. The other three use complete adaptive
row-stabilizer covers. They begin with fixed depth-four frontiers of 1,479,
773, and 773 prefixes, then replace difficult prefixes by complete partial-
literal partitions of the immediate next column. Catalog generation and
refinement make no SAT claim; every retained leaf has its own independently
checked proof core.

Direct compressed traces larger than GitHub's 100 MB repository-file limit
are stored as ordered 95,000,000-byte parts. The much larger deterministic
leaf-core archives are split into GitHub release assets. In both cases the
manifest binds every part and the SHA-256 and byte length of each exact
concatenation. The replay script reassembles each stream before decompression;
chunking changes only transport, not the DRAT proof.

```sh
python3 scripts/replay_z10_23_certificates.py
```

This replay is intentionally separate from the lightweight standard-library gate because expanding and checking all thirteen traces is resource intensive.
