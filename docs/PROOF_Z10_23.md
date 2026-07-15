# Proof of $Z(10,23,3,3)=112$

## 1. The result and its trust boundary

This repository establishes

$$
\boxed{Z(10,23,3,3)=112}.
$$

The lower bound is an explicit matrix checked by two exhaustive verifiers. The upper bound is computer-assisted: an arithmetic front end reduces the excluded target of 113 ones to thirteen finite instances, and replayable DRAT/LRAT or exact SCIP/VIPR certificates refute every instance. Lean checks arithmetic portions of the reduction; it does not replace the external proof certificates.

The authoritative artifacts are [`z10_23_112.json`](../certificates/z10_23_112.json) and [`z10_23_sat.json`](../certificates/z10_23_sat.json).

## 2. Translation to row subsets

Suppose that a $10\times23$ $K_{3,3}$-free Boolean matrix has 113 ones. For column $j$, let $E_j\subseteq[10]$ be its support and put $d_j=|E_j|$. If $\lambda_T$ is the number of columns containing a row triple $T$, then $K_{3,3}$-freeness is equivalent to $\lambda_T\le2$. Hence

$$
\sum_{j=1}^{23}\binom{d_j}{3}
=\sum_{T\in\binom{[10]}3}\lambda_T
\le2\binom{10}{3}=240. \tag{1}
$$

For $0\le d\le10$, define

$$
p(d)=\binom d3-10d+40.
$$

Its values are

$$
(p(0),\ldots,p(10))=(40,30,20,11,4,0,0,5,16,34,60).
$$

Consequently,

$$
\sum_jp(d_j)
=\sum_j\binom{d_j}{3}-10\cdot113+40\cdot23
\le30. \tag{2}
$$

Exhausting the nonnegative integer solutions to the column count, degree sum, and (1) gives exactly 25 profiles. Independent implementations in [`extended.py`](../src/finite_zarankiewicz_closures/extended.py) and [`check_new_bounds.py`](../scripts/check_new_bounds.py) regenerate the same list.

## 3. Twelve arithmetic eliminations

Five profiles contain a column of degree at most two. Deleting that column leaves at least 111 ones in a $10\times22$ matrix, contradicting $Z(10,22,3,3)=110$.

Four profiles contain two degree-three columns. Deleting both leaves 107 ones in a $10\times21$ matrix, contradicting $Z(10,21,3,3)=106$.

For a row $r$, define

$$
D_r=72-\sum_{j:r\in E_j}\binom{d_j-1}{2}\ge0.
$$

If

$$
s=240-\sum_j\binom{d_j}{3},
$$

then double counting gives $\sum_rD_r=3s$. Row-deficit congruences eliminate $4^6 5^{14}6^2 7^1$ and $3^1 4^3 5^{17}6^1 7^1$: their minimum residue sums are 6 and 9, exceeding their budgets 3 and 6.

For a row pair $P$, define

$$
D_P=16-\sum_{j:P\subseteq E_j}(d_j-2)\ge0,
\qquad
\sum_PD_P=18. \tag{3}
$$

For $3^1 4^2 5^{19}7^1$, enumeration of unlabelled row-membership multiplicities in the four exceptional columns gives 1,577 configurations. Exactly 1,380 satisfy the triple-overlap restriction, and the minimum legal residue sum in (3) is 39, contradicting the budget 18. The verifier recomputes the configurations and minimum rather than trusting stored counts.

Thus twelve of the 25 profiles are impossible before invoking a proof-producing solver.

## 4. Complete certificate coverage of the remaining profiles

The remaining thirteen profiles and their certificate strategies are:

| Degree profile | Strategy |
|---|---|
| $4^2 5^{21}$ | direct CaDiCaL DRAT/LRAT |
| $4^3 5^{19}6^1$ | direct CaDiCaL DRAT/LRAT |
| $4^4 5^{17}6^2$ | direct CaDiCaL DRAT/LRAT |
| $4^4 5^{18}7^1$ | direct CaDiCaL DRAT/LRAT |
| $4^5 5^{15}6^3$ | direct CaDiCaL DRAT/LRAT |
| $4^5 5^{16}6^1 7^1$ | direct CaDiCaL DRAT/LRAT |
| $4^6 5^{13}6^4$ | direct CaDiCaL DRAT/LRAT |
| $4^7 5^{11}6^5$ | direct CaDiCaL DRAT/LRAT |
| $3^1 5^{22}$ | direct CaDiCaL DRAT/LRAT |
| $3^1 4^1 5^{20}6^1$ | direct CaDiCaL DRAT/LRAT |
| $3^1 4^2 5^{18}6^2$ | complete row-stabilizer cube cover with 17,170 checked leaves |
| $3^1 4^3 5^{16}6^3$ | exact SCIP/VIPR cover: 236 orbits covering 950,250 states |
| $3^1 4^4 5^{14}6^4$ | exact SCIP/VIPR cover: 209 orbits covering 295,001 states |

Each SAT CNF fixes the stated column degrees, enforces at most two columns through every row triple, applies sound row and equal-degree-column lexicographic symmetry breaking, and requires every row degree to be at least ten. The last condition is valid because deleting a row of degree at most nine would leave at least 104 ones in a $9\times23$ matrix, contradicting $Z(9,23,3,3)=103$.

For the ten direct cases, CaDiCaL 3.0.0 produced DRAT proofs. `drat-trim` checks each proof and derives LRAT, and the independent `lrat-check` executable checks the LRAT. For the cube case, the repository independently regenerates the canonical cover, pairs every one of its 17,170 leaves with exactly one proof-index entry and archive member, and applies the same DRAT/LRAT replay to every leaf.

## 5. The two exact SCIP/VIPR covers

The last two profiles were partitioned into row-symmetry orbits. The repository does not trust the stored partition:

- for $3^1 4^4 5^{14}6^4$, it independently enumerates 295,001 admissible raw states and recomputes exactly 209 orbits;
- for $3^1 4^3 5^{16}6^3$, it independently enumerates 950,250 admissible raw states and recomputes exactly 236 orbits; and
- for every representative, it regenerates the exact OPB instance and requires byte-for-byte agreement with the formula hash recorded in the aggregate manifest.

SCIP 10.0.3 ran in exact mode with presolve and conflict analysis disabled. Each accepted certificate was checked by the unmodified `viprchk` source at commit `30f2951d1e90e47afa821bdd1b12b82246656c42`. The integrity checker also rejects certificates containing the forbidden weak or incomplete derivation features `AggrRow_`, `lin weak`, or `lin incomplete`.

A VIPR certificate embeds the model it proves infeasible. For every leaf, [`vipr_certificate.py`](../src/finite_zarankiewicz_closures/vipr_certificate.py) parses those embedded constraints and compares them coefficient-for-coefficient with the independently regenerated OPB formula before accepting the checker result. This prevents a valid certificate for a different model from being substituted.

The two compressed certificate bodies total 7,929,786,268 bytes. Their deterministic release streams total 7,930,142,720 bytes. The complete proof family, including direct and cube DRAT material, is 25,345,672,172 bytes. Every split part name, size, and SHA-256 digest is fixed by a checked-in release sidecar and the master manifest.

## 6. Upper and lower bounds

The complete coverage above proves that no $10\times23$ $K_{3,3}$-free matrix has exactly 113 ones. If a denser example existed, deleting ones until exactly 113 remained would preserve $K_{3,3}$-freeness. Therefore

$$
Z(10,23,3,3)\le112.
$$

[`z10_23_112_matrix.csv`](../data/z10_23_112_matrix.csv) is a $10\times23$ Boolean matrix with 112 ones and no all-one $3\times3$ submatrix, as checked exhaustively by row triples and independently by all $\binom{10}{3}\binom{23}{3}$ candidate submatrices. Hence

$$
Z(10,23,3,3)\ge112.
$$

Combining the bounds gives

$$
\boxed{Z(10,23,3,3)=112}.
$$

## 7. Reproduction

The self-contained integrity gate regenerates the arithmetic classification, both orbit covers, all 445 OPB instances, and all local hashes:

```bash
make z10-23-certificate
```

The heavyweight replay additionally downloads the split proof release and invokes `drat-trim`, `lrat-check`, and `viprchk`:

```bash
python3 scripts/fetch_z10_23_release_assets.py --output build/z10_23_assets
Z10_23_ASSET_DIR=build/z10_23_assets \
VIPRCHK=/path/to/viprchk \
python3 scripts/replay_z10_23_certificates.py --workers 8 \
  --output audit/z10_23_sat_replay.json
```

The historical solver run that retained no proof traces is not used. Cloud job status, log text, and checkpoints are likewise non-load-bearing; only the hash-bound formulas, complete covers, proof indexes, proof bodies, and independent checker results enter the theorem.
