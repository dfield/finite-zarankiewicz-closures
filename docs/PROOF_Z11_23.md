# Proof of $Z(11,23,3,3)=123$

The checked witness [`z11_23_123_matrix.csv`](../data/z11_23_123_matrix.csv) is an $11\times23$ Boolean matrix with 123 ones and no all-one $3\times3$ submatrix. Therefore

$$
Z(11,23,3,3)\ge123.
$$

For the upper bound, suppose an $11\times23$ $K_{3,3}$-free matrix had 124 ones. Its eleven row degrees sum to 124, so some row has degree at most

$$
\left\lfloor\frac{124}{11}\right\rfloor=11.
$$

Deleting that row leaves a $10\times23$ $K_{3,3}$-free matrix with at least

$$
124-11=113
$$

ones. This contradicts the independently certified result $Z(10,23,3,3)=112$ proved in [`PROOF_Z10_23.md`](PROOF_Z10_23.md). Thus

$$
Z(11,23,3,3)\le123.
$$

Combining both inequalities gives

$$
\boxed{Z(11,23,3,3)=123}.
$$

The case certificate [`z11_23_123.json`](../certificates/z11_23_123.json) binds the witness, deletion arithmetic, and the SHA-256 digest of the source $Z(10,23)$ master manifest. Lean checks the deletion arithmetic conditionally on the $Z(10,23)$ bound; the computer-assisted certificate family described in the source dossier supplies that premise.
