# Certificates

## Exact-value certificates

Each established value has a standalone JSON certificate that binds its checked witness to a recomputed upper-bound argument:

| Result | Certificate | Upper-bound mechanism |
|---|---|---|
| $Z(9,23,3,3)=103$ | [`z9_23_103.json`](z9_23_103.json) | marked-row deficit; binds [`degree_deficit.json`](degree_deficit.json) |
| $Z(10,21,3,3)=106$ | [`z10_21_106.json`](z10_21_106.json) | vertex deletion |
| $Z(10,22,3,3)=110$ | [`z10_22_110.json`](z10_22_110.json) | four-profile pair-deficit argument |
| $Z(10,23,3,3)=112$ | [`z10_23_112.json`](z10_23_112.json) | arithmetic reduction and complete replayable proof family |
| $Z(11,19,3,3)=106$ | [`z11_19_106.json`](z11_19_106.json) | vertex deletion |
| $Z(11,20,3,3)=111$ | [`z11_20_111.json`](z11_20_111.json) | two vertex-deletion steps |
| $Z(11,23,3,3)=123$ | [`z11_23_123.json`](z11_23_123.json) | minimum-row deletion from $Z(10,23)=112$ |
| $Z(12,23,3,3)=134$ | [`z12_23_134.json`](z12_23_134.json) | two-stage row/pair-deficit argument |

Regenerate or byte-check all eight:

```bash
python3 scripts/check_case_certificates.py --check
```

The upper-bound-only result $Z(13,23,3,3)\le144$ has [`z13_23_upper_144.json`](z13_23_upper_144.json).

## $Z(10,23)$ proof family

[`z10_23_sat.json`](z10_23_sat.json) is the master manifest for the thirteen non-arithmetic profiles at 113 ones. The [`z10_23/`](z10_23/) tree contains local formulas, direct compressed proofs, the complete cube catalog and proof index, two VIPR orbit catalogs, aggregate manifests, and release sidecars.

Large proof bodies are published as split assets under the GitHub release tag `z10-23-certificate-v1`; they are not committed to Git. The sidecars fix every part name, size, and SHA-256 digest. The self-contained integrity gate deeply regenerates both orbit covers and all 445 OPB formulas:

```bash
make z10-23-certificate
```

The external semantic replay is:

```bash
python3 scripts/fetch_z10_23_release_assets.py --output build/z10_23_assets
Z10_23_ASSET_DIR=build/z10_23_assets \
VIPRCHK=/path/to/viprchk \
python3 scripts/replay_z10_23_certificates.py --workers 8
```

See [`docs/PROOF_Z10_23.md`](../docs/PROOF_Z10_23.md) for the reduction and trust boundary.

## Historical terminal traces

The `terminal_*.drat` and `terminal_*.lrat` files replay the three terminal aggregations in the $Z(9,23)$ marked-row proof. They do not cover $Z(10,23)$.

```bash
python3 scripts/replay_certificates.py
```
