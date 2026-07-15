# Seven further exact values in the 2026 finite table

> **Attribution:** GPT 5.6-Sol generated the original extensions. Claude (Anthropic) supplied the later $Z(11,19)$ witness and the $Z(12,23)$ proof and witness. OpenAI Codex completed the replayable $Z(10,23)$ certification and its $Z(11,23)$ consequence. All results await independent expert review.

## 1. Scope

[Bhan, Nobili, and Langer](https://arxiv.org/html/2605.01120v2) listed 44 previously open values of $Z(m,n,3,3)$ in Figure 2. Their paper made three exact:

$$
Z(11,21,3,3)=116,\qquad
Z(11,22,3,3)=121,\qquad
Z(12,22,3,3)=132.
$$

Alongside the repository's marked-row result $Z(9,23,3,3)=103$, the extended work establishes seven more:

$$
\begin{aligned}
Z(10,21,3,3)&=106, & Z(10,22,3,3)&=110,\\
Z(10,23,3,3)&=112, & Z(11,19,3,3)&=106,\\
Z(11,20,3,3)&=111, & Z(11,23,3,3)&=123,\\
Z(12,23,3,3)&=134.
\end{aligned}
$$

Thus 11 of the original 44 cells are exact and **33 remain open**.

## 2. Deletion lemma

If $Z(m-1,n,3,3)\le B$, then

$$
Z(m,n,3,3)\le\left\lfloor\frac{mB}{m-1}\right\rfloor. \tag{1}
$$

Indeed, an $m$-row matrix with $e$ ones has a row of degree at most $\lfloor e/m\rfloor$. Deleting it leaves at least $\lceil(m-1)e/m\rceil$ ones, which cannot exceed $B$. The same argument applies to columns.

Equation (1) gives

$$
Z(10,21,3,3)\le\left\lfloor\frac{10\cdot96}{9}\right\rfloor=106,
$$

and

$$
Z(11,19,3,3)\le\left\lfloor\frac{19\cdot101}{18}\right\rfloor=106,
\qquad
Z(11,20,3,3)\le\left\lfloor\frac{20\cdot106}{19}\right\rfloor=111.
$$

The checked witnesses attain all three bounds.

The certified value $Z(10,23,3,3)=112$ similarly gives

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot112}{10}\right\rfloor
=123,
$$

again attained by a checked witness. See [`PROOF_Z11_23.md`](PROOF_Z11_23.md).

## 3. Non-deletion closures

- [`PROOF.md`](PROOF.md) proves $Z(9,23,3,3)=103$ by a marked-row deficit congruence.
- [`PROOF_Z10_22.md`](PROOF_Z10_22.md) proves $Z(10,22,3,3)=110$ by classifying four degree profiles and eliminating them with row/pair deficits.
- [`PROOF_Z10_23.md`](PROOF_Z10_23.md) proves $Z(10,23,3,3)=112$ by eliminating twelve of 25 profiles arithmetically and refuting the other thirteen with complete replayable DRAT/LRAT and exact SCIP/VIPR certificates.
- [`PROOF_Z12_23.md`](PROOF_Z12_23.md) proves $Z(12,23,3,3)=134$ by excluding 136 and 135 ones with forced-profile and row/pair-deficit arguments.
- [`BOUND_Z13_23.md`](BOUND_Z13_23.md) establishes the additional frontier bound $Z(13,23,3,3)\le144$.

All eight exact cases have separate checked witnesses and standalone JSON certificates.

## 4. Reproduction and trust boundary

```bash
make verify
```

The standard-library gate regenerates all arithmetic reports, verifies all eight witnesses, checks the case certificates, and deeply audits the $Z(10,23)$ cover/formula integrity layer. The full $Z(10,23)$ semantic replay uses the external `drat-trim`, `lrat-check`, and `viprchk` executables plus release-bound proof bodies; see [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md).

Lean proves several cases end-to-end and checks the remaining arithmetic/deletion kernels. It does not replay DRAT/LRAT or VIPR and therefore is not the sole trust basis for $Z(10,23)$.

## 5. Remaining open cells

The 33 unresolved cells from the paper are:

- $(12,n)$ for $n\in\{17,18,19,20,21\}$; and
- $(m,n)$ for $13\le m\le16$ and $17\le n\le23$.

The exact set, source intervals, and propagated improvements are stored in [`extended_results.json`](../analysis/extended_results.json) and [`new_bounds.json`](../analysis/new_bounds.json).
