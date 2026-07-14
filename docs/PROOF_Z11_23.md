# Candidate dossier for $Z(11,23,3,3)=123$

The proposed equality is **conditional** on completing the $Z(10,23)$ upper-bound certificate. The unconditional interval currently established is

$$
\boxed{123\le Z(11,23,3,3)\le125}.
$$

## Established lower bound

[`z11_23_123_matrix.csv`](../data/z11_23_123_matrix.csv) is an explicit $11\times23$ Boolean matrix with 123 ones and no all-one $3\times3$ submatrix. It is independently checked as its own artifact. Therefore

$$
Z(11,23,3,3)\ge123.
$$

The current upper bound 125 is the literature bound and also follows by deleting a row from the safe bound $Z(10,23,3,3)\le114$:

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot114}{10}\right\rfloor
=125.
$$

## Conditional exact-value argument

Assume the pending certificate establishes

$$
Z(10,23,3,3)\le112.
$$

Then an $11\times23$ matrix with 124 ones has a row of degree at most
$\lfloor124/11\rfloor=11$. Deleting it leaves at least 113 ones in ten rows,
contradicting that assumed upper bound. Equivalently,

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot112}{10}\right\rfloor
=123.
$$

Together with the checked witness, this would prove

$$
Z(11,23,3,3)=123.
$$

The quotient arithmetic is checked in Lean, but Lean does not supply the missing $Z(10,23)$ premise. See [`SAT_Z10_23_STATUS.md`](SAT_Z10_23_STATUS.md) for that dependency.
