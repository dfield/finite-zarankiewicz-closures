# Certificates and candidate proof artifacts

## Publishable theorem certificates

Each established exact value has a standalone JSON certificate:

| Result | Certificate | Upper-bound mechanism |
|---|---|---|
| $Z(9,23,3,3)=103$ | [`z9_23_103.json`](z9_23_103.json) | marked-row deficit, binding [`degree_deficit.json`](degree_deficit.json) |
| $Z(10,21,3,3)=106$ | [`z10_21_106.json`](z10_21_106.json) | vertex deletion |
| $Z(10,22,3,3)=110$ | [`z10_22_110.json`](z10_22_110.json) | four-profile pair-deficit enumeration |
| $Z(11,19,3,3)=106$ | [`z11_19_106.json`](z11_19_106.json) | vertex deletion |
| $Z(11,20,3,3)=111$ | [`z11_20_111.json`](z11_20_111.json) | two vertex-deletion steps |
| $Z(12,23,3,3)=134$ | [`z12_23_134.json`](z12_23_134.json) | two-stage row/pair-deficit enumeration |

Every certificate binds the checked witness and recomputed case-specific upper-bound data. Verify all six with:

```bash
python3 scripts/check_case_certificates.py --check
```

The upper-bound-only claim $Z(13,23,3,3)\le144$ has [`z13_23_upper_144.json`](z13_23_upper_144.json):

```bash
python3 scripts/check_frontier_certificate.py --check
```

## Candidate artifacts

The directory [`z10_23/`](z10_23/) contains partial direct traces, cover catalogs, proof indexes, and packaging sidecars produced while attempting to certify $Z(10,23,3,3)=112$. They are retained for audit and continuation, but the directory is not a complete proof family.

In particular, this publication boundary has neither a final `z10_23_sat.json` manifest nor a `z10_23_112.json` exact-value certificate. It also has no `z11_23_123.json` exact-value certificate, because that proposed upper bound depends on the unfinished $Z(10,23)$ proof. See [`docs/SAT_Z10_23_STATUS.md`](../docs/SAT_Z10_23_STATUS.md).

Once every required asset exists, the optional heavyweight integrity gate is:

```bash
make candidate-certificate
```

Passing manifest integrity alone will still not promote the result; independent DRAT/LRAT replay and an explicit status update are required.

## Historical terminal traces

The six `terminal_*.drat` and `terminal_*.lrat` files replay the three terminal aggregations in the established $Z(9,23)$ marked-row proof. They have no bearing on the two candidates.

```bash
python3 scripts/replay_certificates.py
```
