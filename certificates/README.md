# Case-specific certificates

Each exact value has a standalone JSON certificate:

| Result | Certificate | Upper-bound mechanism |
|---|---|---|
| $Z(9,23,3,3)=103$ | [`z9_23_103.json`](z9_23_103.json) | marked-row deficit; binds the detailed [`degree_deficit.json`](degree_deficit.json) subcertificate |
| $Z(10,21,3,3)=106$ | [`z10_21_106.json`](z10_21_106.json) | one vertex-deletion step |
| $Z(10,22,3,3)=110$ | [`z10_22_110.json`](z10_22_110.json) | four-profile pair-deficit enumeration |
| $Z(11,20,3,3)=111$ | [`z11_20_111.json`](z11_20_111.json) | two vertex-deletion steps |

Every certificate includes the explicit witness's dimensions, weight, row and column sums, exhaustive row-triple result, and SHA-256 digest. The upper-bound section is specific to the case. The checker regenerates these fields rather than trusting the stored JSON:

```sh
python3 scripts/check_case_certificates.py --check
```

Mutation tests alter each case certificate and require rejection.

## Terminal DRAT and LRAT

The six historical DRAT/LRAT files replay the three terminal aggregations in the marked-row proof. They do not cover the other reductions or any raw cell CNF. The other three results instead have case-specific JSON certificates and Lean arithmetic endpoints; no broader proof-trace claim is made.

```sh
python3 scripts/replay_certificates.py
```
