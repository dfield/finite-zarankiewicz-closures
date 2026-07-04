# A proof that $Z(9,23,3,3)=103$

This note gives a self-contained proof. It uses only elementary counting and congruences. No solver output is needed for the upper bound.

## 1. Statement and notation

A Boolean matrix is **$K_{3,3}$-free** if it has no all-one $3\times3$ submatrix. The Zarankiewicz number $Z(m,n,3,3)$ is the largest number of ones in an $m\times n$ $K_{3,3}$-free Boolean matrix.

We prove

$$
Z(9,23,3,3)=103.
$$

The lower bound is supplied by an explicit 103-one matrix. The substance of the proof is the upper bound: a 104-one matrix cannot exist.

## 2. Translate columns into subsets

Suppose, for a contradiction, that a $9\times23$ $K_{3,3}$-free Boolean matrix has 104 ones. Identify its nine rows with $[9]=\{1,\ldots,9\}$. For column $j$, let

$$
E_j\subseteq[9]
$$

be the set of rows in which that column contains a one, and put $d_j=|E_j|$.

For each row triple $T\in\binom{[9]}3$, define

$$
\lambda_T=|\{j:T\subseteq E_j\}|.
$$

If $\lambda_T\ge3$, the three rows in $T$ and any three columns counted by $\lambda_T$ form an all-one $3\times3$ submatrix. Thus $K_{3,3}$-freeness is equivalent to

$$
\lambda_T\le2\quad\text{for every }T\in\binom{[9]}3.
$$

Double-counting pairs $(T,j)$ with $T\subseteq E_j$ gives

$$
\sum_{j=1}^{23}\binom{d_j}{3}
=\sum_{T\in\binom{[9]}3}\lambda_T
\le2\binom93=168. \qquad\text{(1)}
$$

## 3. A sharp one-column inequality

For an integer $0\le d\le9$, define

$$
p(d)=\binom d3-6d+20.
$$

The ten possible values are

| $d$ | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|:---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| $p(d)$ | 20 | 14 | 8 | 3 | 0 | 0 | 4 | 13 | 28 | 50 |

In particular, $p(d)\ge0$, equality occurs exactly at $d=4,5$, and the only positive values at most four occur at $d=3,6$.

Because there are 104 ones in total,

$$
\sum_j d_j=104.
$$

Consequently,

$$
\sum_j\binom{d_j}{3}
=6\sum_jd_j-20\cdot23+\sum_jp(d_j)
=164+\sum_jp(d_j). \qquad\text{(2)}
$$

Combining (1) and (2) yields

$$
\sum_jp(d_j)\le4. \qquad\text{(3)}
$$

The table for $p$, together with $\sum_j1=23$ and $\sum_jd_j=104$, leaves exactly three possible multisets of column degrees:

$$
4^{11}5^{12},\qquad
3^1 4^9 5^{13},\qquad
4^{12}5^{10}6^1. \qquad\text{(4)}
$$

For completeness:

- If every column has degree four or five, solving $a+b=23$ and $4a+5b=104$ gives $(a,b)=(11,12)$.
- A degree-three column uses three units of the budget in (3); all other columns must have degree four or five. The same two equations give $3^1 4^9 5^{13}$.
- A degree-six column uses all four units of the budget; all other columns must have degree four or five. The equations give $4^{12}5^{10}6^1$.
- Every other degree has penalty at least eight, and two exceptional columns would exceed the budget.

The total triple incidences $\sum_j\binom{d_j}{3}$ in the three cases are 164, 167, and 168, respectively.

## 4. Mark one row

Define the unused capacity of a row triple by

$$
\delta_T=2-\lambda_T\ge0.
$$

Let

$$
D=\sum_T\delta_T,
\qquad
D_r=\sum_{T\ni r}\delta_T.
$$

Each triple has three rows, so another double count gives

$$
\sum_{r=1}^9D_r=3D. \qquad\text{(5)}
$$

There are $\binom82=28$ row triples containing a fixed row $r$, each with capacity two. A column of degree $d_j$ that contains $r$ contributes $\binom{d_j-1}{2}$ incidences to those triples. Therefore

$$
D_r=56-\sum_{j:r\in E_j}\binom{d_j-1}{2}. \qquad\text{(6)}
$$

Degree-four and degree-five columns contribute 3 and 6 in (6), both divisible by three. This small congruence is the missing overlap information.

## 5. Eliminate the three degree patterns

### Case 1: $4^{11}5^{12}$

There are 164 used triple incidences, so $D=168-164=4$. Equation (5) gives

$$
\sum_rD_r=12.
$$

Equation (6) gives $D_r\equiv56\equiv2\pmod3$ for every row. Since $D_r\ge0$, every $D_r\ge2$. Hence

$$
\sum_rD_r\ge9\cdot2=18,
$$

contradicting $\sum_rD_r=12$.

### Case 2: $3^1 4^9 5^{13}$

There are 167 used triple incidences, so $D=1$ and

$$
\sum_rD_r=3.
$$

Let $E$ be the unique degree-three column. If $r\in E$, that column contributes $\binom22=1$ in (6), so $D_r\equiv1\pmod3$ and $D_r\ge1$. If $r\notin E$, then $D_r\equiv2\pmod3$ and $D_r\ge2$. Thus

$$
\sum_rD_r\ge3\cdot1+6\cdot2=15,
$$

contradicting $\sum_rD_r=3$.

### Case 3: $4^{12}5^{10}6^1$

All 168 triple-capacity units are used, so $D=0$ and

$$
\sum_rD_r=0.
$$

Let $E$ be the unique degree-six column. If $r\in E$, that column contributes $\binom52=10$ in (6), so $D_r\equiv56-10\equiv1\pmod3$ and $D_r\ge1$. If $r\notin E$, then $D_r\equiv2\pmod3$ and $D_r\ge2$. Hence

$$
\sum_rD_r\ge6\cdot1+3\cdot2=12,
$$

contradicting $\sum_rD_r=0$.

All possibilities in (4) are impossible. Therefore no 104-one $9\times23$ $K_{3,3}$-free matrix exists. If a still denser matrix existed, deleting ones until exactly 104 remained would preserve $K_{3,3}$-freeness, so

$$
Z(9,23,3,3)\le103.
$$

## 6. The lower bound

An explicit $9\times23$ matrix with 103 ones is included in this repository. Its row sums are

$$
(11,11,11,11,11,11,12,12,13),
$$

and its column sums consist of twelve 4s and eleven 5s. Direct inspection of all

$$
\binom93\binom{23}3=148{,}764
$$

possible $3\times3$ submatrices confirms that none is all one. Hence

$$
Z(9,23,3,3)\ge103.
$$

Together with the upper bound, this proves

$$
\boxed{Z(9,23,3,3)=103}.
$$

## 7. What is—and is not—computer-assisted

The upper-bound proof above is entirely human-readable. The repository's programs serve three narrower purposes:

1. verify the 103-one witness independently in two ways;
2. check every arithmetic case and coefficient appearing in the proof;
3. replay small DRAT/LRAT certificates for the three terminal linear contradictions.

Those checks are useful safeguards, but none replaces a mathematical step in the argument above.
