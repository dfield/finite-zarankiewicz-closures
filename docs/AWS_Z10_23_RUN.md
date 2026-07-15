# AWS proof-production record for $Z(10,23,3,3)=112$

> **Final status:** proof production and aggregate verification completed; dedicated compute was scaled to zero. Cloud state is operational provenance, not theorem evidence by itself.

## Identifiers and isolation

- Project: `zarankiewicz-z10-23-lrat`
- Base run: `z1023-lrat-20260706t190127z-a2e0ce9f`
- Final adaptive stage: `r9`
- Profile-B sweep: `z1023-scip-vipr-b-20260715t004830z-a2e0ce9f`
- Profile-B residual sweep: `z1023-scip-vipr-b-r-20260715t015331z-a2e0ce9f`
- Profile-C sweep: `z1023-scip-vipr-c-20260715t022016z-a2e0ce9f`
- Region: `us-east-2`
- Durable prefix: `zarankiewicz-z10-23-lrat/runs/z1023-lrat-20260706t190127z-a2e0ce9f/`

The work reused the `conway99-stage10` EKS control plane but used a project-specific namespace, service account, ECR repository, encrypted/versioned S3 bucket, IAM role, labels, taints, and run-scoped object prefixes. The dedicated On-Demand node group was capped at six `r7i.2xlarge` instances: 48 vCPUs total.

## Earlier DRAT/LRAT stage

The base and recovery stages produced the ten direct CaDiCaL proof traces and the complete 17,170-leaf cube proof family. Every accepted leaf passed:

1. DRAT replay with the pinned `drat-trim` build;
2. DRAT-to-LRAT conversion;
3. independent LRAT replay with `lrat-check`; and
4. projected-core replay before its encrypted, hash-bound checkpoint was accepted.

Recovery and adaptive refinement were used to finish hard leaves. Failed, timed-out, incomplete, and superseded attempts remain operational history and do not enter the final proof index.

## Final exact SCIP/VIPR stage

The last two profiles were solved as exact integer programs over complete row-symmetry orbit covers.

| Profile | Raw states | Orbits | Verified leaves | Certificate bytes |
|---|---:|---:|---:|---:|
| $3^1 4^4 5^{14}6^4$ | 295,001 | 209 | 209 | 7,914,211,500 |
| $3^1 4^3 5^{16}6^3$ | 950,250 | 236 | 236 | 15,574,768 |

Profile B required a residual run for thirteen certificates whose first exact SCIP output requested unsupported completion steps. The residual run disabled separation as well as presolve and conflict analysis. Only certificates fully accepted by `viprchk` without completion are present in the final aggregate. Profile C completed all 236 representatives directly.

The final aggregate manifest hashes are:

- profile B: `3c46aa06a9f7a33ef42e5328e738f4ecfdcb26f60603b1a85ad01145cbc500af`;
- profile C: `30fd5b8fba89a4d51fcac8e37be2e34535606be36fc19f651fbfa990ef419ded`.

## Pinned proof tools

| Tool | Version or identity |
|---|---|
| CaDiCaL | 3.0.0, commit `7b99c07f0bcab5824a5a3ce62c7066554017f641` |
| `drat-trim` / `lrat-check` | proof-tools commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` |
| SCIP | 10.0.3 exact mode, git hash `d409edf9f6` |
| SCIP archive SHA-256 | `ddbb7129bdb83f8f70ed26391d206fd1658139e44c7c7fd7d73a1e4cefbca94f` |
| `viprchk` source | commit `30f2951d1e90e47afa821bdd1b12b82246656c42` |
| `viprchk` source SHA-256 | `7d20cd04ba11488fbc8ed3fbabfdfa513e161a0c36b75220927f55051614ed2f` |

## Harvest and publication boundary

The final artifacts were harvested from S3, checked against their leaf manifests, packed into deterministic split release streams, and bound into [`z10_23_sat.json`](../certificates/z10_23_sat.json). The repository independently regenerates the covers and formulas without AWS access. The heavyweight replay can obtain the proof bodies from the GitHub release and invoke all three external checkers.

AWS pod status, solver log text, S3 object presence, and autoscaling state are never sufficient for publication. The theorem depends only on the checked witness, arithmetic reduction, complete cover arguments, hash-bound proof bodies, and successful independent proof-checker runs described in [`PROOF_Z10_23.md`](PROOF_Z10_23.md).
