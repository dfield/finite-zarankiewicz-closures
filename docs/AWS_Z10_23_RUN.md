# AWS proof-production record for the $Z(10,23)$ candidate

> **Publication status as of 2026-07-13:** proof production is ongoing. This dossier is an operational record, not a completed certificate and not evidence for the equality by itself.

## Identifiers

- Project: `zarankiewicz-z10-23-lrat`
- Base run: `z1023-lrat-20260706t190127z-a2e0ce9f`
- Adaptive stage: `z1023-r8-20260712t160923z-a2e0ce9f`
- Active recovery: `z1023-r8-recovery-20260714t030653z-a2e0ce9f`
- Region: `us-east-2`
- Run-scoped durable prefix: `zarankiewicz-z10-23-lrat/runs/z1023-lrat-20260706t190127z-a2e0ce9f/`

The recovery launch was independently reconstructed from the sealed prior cutoff and binds 5,717,908 outstanding proof tasks. Its configured safety cutoff is `2026-07-14T22:00:00Z`.

## Isolation and capacity

The work uses the existing `conway99-stage10` EKS control plane but project-specific mutable resources:

- namespace and service account `zarankiewicz-z10-23-lrat`;
- managed On-Demand node group `zarankiewicz-z10-23-lrat-od`;
- ECR repository and encrypted, versioned S3 bucket dedicated to the project;
- IRSA role `zarankiewicz-z10-23-lrat-worker-irsa`; and
- run-, stage-, and recovery-scoped object prefixes.

The worker pool is capped at six On-Demand `r7i.2xlarge` instances, eight vCPUs each, for 48 vCPUs. Project labels and taints keep the workload on its dedicated nodes. No Conway workload namespace, job, bucket, or node group is part of the proof state.

The immutable worker image is

```text
624052199967.dkr.ecr.us-east-2.amazonaws.com/zarankiewicz-z10-23-lrat:z1023-lrat-20260706t190127z-a2e0ce9f
```

with manifest digest `sha256:c6e4a1986c13c538105ae17c2e8ee2bf5241a4823e691670fb302d984f39cb18`.

| Tool | Version or source | SHA-256 |
|---|---|---|
| CaDiCaL | 3.0.0 | `0d576865772350ba09ac01e33cb7264c11b94ea8ed7130a519448c38d5656aba` |
| `drat-trim` | proof-tools commit `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` | `9c09fe813af0b52f58d923837a1bc3ca5e6017987c1e9530d62fa5b4f018412a` |
| `lrat-check` | same proof-tools commit | `bf67af3ff4c0ce09a0873ad32ac53d797047d4a31d50bf2effd025c3c9e89986` |
| XZ | 5.4.1 | `31c8422d8432de91ffa9b3713743c98cb8011c561546c76759600c9476357dc0` |

## Durable workflow

The cloud stage handles difficult leaves from complete row-stabilizer covers. Catalog construction and refinement make no SAT claim. For each retained leaf, the intended verified pipeline is:

1. append the catalogued cell literals to the exact base CNF as unit clauses;
2. produce a DRAT trace with the pinned CaDiCaL binary;
3. replay with `drat-trim` and derive LRAT;
4. check LRAT independently with `lrat-check`;
5. replay the projected compact DRAT core; and
6. write an encrypted, hash-bound S3 checkpoint only after all checks succeed.

The recovery task partition was reconstructed twice and required identical manifests before launch. A corrected in-cluster guard uses the AWS SDK, records progress to the recovery prefix, and scales the dedicated node group to zero at completion or cutoff. An earlier guard invocation used an unsupported CLI option; the affected cutoff was manually sealed and capacity was scaled to zero before the corrected recovery was launched. That incident is operational history and no affected pod status is accepted as mathematical evidence.

## What must happen before publication as an equality

Completion of compute is not sufficient. Promotion of $Z(10,23,3,3)=112$ requires:

- a sealed census with exactly one verified core for every retained leaf;
- deterministic cover-completeness audits;
- deterministic proof archives and sidecars binding every part name, size, and SHA-256 digest;
- a final manifest covering all thirteen SAT profiles;
- independent local DRAT and LRAT replay from the published artifacts; and
- a clean-clone repository audit that promotes the candidate explicitly.

None of those final aggregate artifacts is asserted complete in this version. Until they are harvested and replayed, [`analysis/result_status.json`](../analysis/result_status.json) keeps $Z(10,23)=112$ and its dependent $Z(11,23)=123$ as candidates.
