# Proof dossier for $Z(11,23,3,3)=123$

## Upper bound

The completed value $Z(10,23,3,3)=112$ gives the upper bound by vertex
deletion. In an $11\times23$ matrix with $e$ ones, some row has degree at most
$\lfloor e/11\rfloor$. At $e=124$, deleting such a row leaves at least

$$
124-\left\lfloor\frac{124}{11}\right\rfloor
=124-11
=113
$$

ones in ten rows, contradicting $Z(10,23,3,3)=112$. Equivalently,

$$
Z(11,23,3,3)
\le\left\lfloor\frac{11\cdot112}{10}\right\rfloor
=123.
$$

## Lower bound

[`z11_23_123_matrix.csv`](../data/z11_23_123_matrix.csv) is an explicit
$11\times23$ Boolean matrix with 123 ones and no all-one $3\times3$
submatrix. It is obtained by deleting one 11-one row from the stored 134-one
$12\times23$ witness, and is independently checked as its own artifact.
Therefore

$$
Z(11,23,3,3)\ge123.
$$

The two bounds prove

$$
\boxed{Z(11,23,3,3)=123}.
$$

Lean checks the quotient and excluded-target arithmetic. The package and
standalone witness verifiers check the lower-bound matrix directly.
