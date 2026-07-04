# Literature review and prior status

## Scope and search date

This review records the literature relevant to the exact finite problem

$$
Z(9,23,3,3),
$$

with a search cutoff of **2026-07-04**. It is intended to be complete for the chain of published and publicly posted results that leads directly to the previously reported interval

$$
103\le Z(9,23,3,3)\le104,
$$

and for the finite computational methods used to study nearby cases. The Zarankiewicz literature is much larger than this one finite problem, so the discussion of general asymptotic theory and geometric variants is necessarily selective. Füredi and Simonovits's historical survey is a suitable entry point for that broader literature [FS13].

The search covered exact-title, exact-parameter, author, DOI, arXiv, and citation-forward queries. In particular, variants of `Z(9,23,3,3)`, `z_3(9,23)`, and `9 23 103 104 Zarankiewicz` were checked, as were later references to Tan [Tan22], Davies--Gill--Horsley [DGH26], and Bhan--Nobili--Langer [BNL26]. No public source located by that search determined this value before the present work. That statement is deliberately dated: it cannot rule out unpublished work, an unindexed source, or a later revision.

## 1. The problem in context

A Boolean $m\times n$ matrix can be read as the bipartite adjacency matrix of a graph with parts of sizes $m$ and $n$. An all-one $s\times t$ submatrix is exactly a copy of $K_{s,t}$. Thus

$$
Z(m,n,s,t)
$$

is the largest number of edges in a subgraph of $K_{m,n}$ that contains no $K_{s,t}$, with the orientation of the two parts fixed. Some authors write $z(m,n;s,t)$, $Z_{s,t}(m,n)$, or $z_s(m,n)$ when $s=t$. This repository uses $Z(m,n,s,t)$.

Zarankiewicz posed the original matrix problem as Problem P101 in 1951 [Zar51]. The foundational theorem of Kővári, Sós, and Turán gave a general upper bound and established the problem as a central example of bipartite extremal graph theory [KST54]. Čulík [Cul56] and Reiman [Rei58] developed early refinements and constructions. Guy's surveys assembled the early finite questions and their connections [Guy68, Guy69].

The general theory has several strands:

- **Counting and convexity.** Count the small subsets contained in neighborhoods and compare them with the capacity allowed by excluding $K_{s,t}$. Roman's finite upper bounds are a particularly effective form of this method [Rom75].
- **Algebraic and geometric constructions.** Finite planes, designs, and norm graphs supply dense examples for many parameter ranges; see, for example, Füredi [Fur96], Kollár--Rónyai--Szabó [KRS96], and the geometric discussion of Damásdi--Héger--Szőnyi [DHS13].
- **Asymptotic estimates.** The orders of magnitude and leading constants remain subtle even when one or both part sizes grow. Nikiforov [Nik10], Conlon [Con21], and the survey of Füredi--Simonovits [FS13] place the finite questions within this wider program.
- **Exact finite computation.** Integer programming, canonical generation, and SAT can close small cases that are beyond a single coarse counting inequality. Irving [Irv78], Goddard--Henning--Oellermann [GHO00], Collins--Riasanovsky--Wallace--Radziszowski [CRWR16], and Tan [Tan22] are important points in this line.

The proof in this repository belongs to the first and fourth strands: a computation-discovered degree pattern is distilled into an elementary counting and congruence argument, while independent programs check the construction and the finite arithmetic.

## 2. Roman's degree bound and why 104 appeared

Roman's 1975 paper derives a family of finite upper bounds by counting column degrees [Rom75]. For the present parameters, let the column degrees be $d_1,\ldots,d_{23}$. Every three-row set can occur in at most two columns of a $K_{3,3}$-free matrix, so

$$
\sum_{j=1}^{23}\binom{d_j}{3}\le 2\binom{9}{3}=168.
$$

Optimizing the total degree $\sum_j d_j$ under this constraint gives the familiar upper bound 104. The continuous relaxation is fractional, while the integer boundary at 104 is concentrated near degrees four and five. This is exactly the setting in which a degree-only bound can miss compatibility information: it knows how many triple incidences exist in total, but not whether those incidences can be distributed consistently among the 84 row triples.

Roman's work is therefore not merely historical background. It provides the inequality from which the proof here starts, and it explains why the old upper bound stopped one edge above the construction.

## 3. Finite tables, Ramsey connections, and computation

Finite Zarankiewicz numbers are closely connected with bipartite Ramsey numbers: in a two-coloring of a complete bipartite graph, each color class is itself a bipartite graph whose edge count can be compared with a Zarankiewicz bound. Irving explicitly studied this relationship and obtained concrete finite bounds [Irv78]. Goddard, Henning, and Oellermann later systematized further connections and finite cases [GHO00]. A Ramsey implication alone does not determine the present number, because it constrains a graph and its complement simultaneously; a direct Zarankiewicz upper bound must still exclude every 104-edge $K_{3,3}$-free graph.

Collins, Riasanovsky, Wallace, and Radziszowski developed computational methods for diagonal cases and reported new exact values and bounds for forbidden $K_{s,s}$ with $3\le s\le6$ [CRWR16]. Their work also emphasizes a recurring issue in finite tables: a numerical entry is only as reliable as the construction or exhaustive argument behind it.

Tan encoded the matrix entries as Boolean variables, added one clause for each forbidden all-one submatrix, and used cardinality constraints, row-sum partitions, and symmetry breaking to extend and correct finite tables [Tan22]. In Tan's Table 3, $z_3(9,22)=100$ is marked exact, while the entry 104 for $z_3(9,23)$ is an upper bound inherited from Roman rather than a claimed exact value. Tan's public companion code is the Kyoto repository [TanCode].

Two methodological lessons from this literature are followed here:

1. a lower bound is accompanied by a concrete matrix that a small independent checker can inspect; and
2. an unsatisfiable search is not treated as proof unless its reduction or proof trace can be checked independently.

## 4. Strengthened linear programming bounds

Chen, Horsley, and Mammoliti interpret related Zarankiewicz problems through linear hypergraphs and designs, obtaining exact results in a broad unbalanced $s=2$ regime and complementary inequalities to Roman's family [CHM24]. Davies, Gill, and Horsley generalized this approach to add valid degree-count constraints to Roman's linear program for arbitrary fixed $s,t$ [DGH26]. Their method improves many small upper bounds and provides both a full linear program and simpler closed-form consequences.

The parameter pair $(9,23)$ for $s=t=3$ is not among the improvements listed by Davies--Gill--Horsley. Recomputing their degree-count relaxation at total weight 104 gives the exact fractional optimum

$$
\frac{314}{3}=104\frac23,
$$

attained at the fractional degree profile

$$
n_4=\frac{31}{3},\qquad n_5=\frac{38}{3}.
$$

Moreover, each of the three integer degree profiles that survives Roman's inequality at weight 104 also satisfies the Davies--Gill--Horsley degree constraints. Their relaxation therefore cannot see the last contradiction. The missing information is not another condition on the global degree histogram; it is an overlap condition recording how the nearly saturated row triples meet each individual row. The marked-row deficit used in [`PROOF.md`](PROOF.md) supplies precisely that information.

## 5. The one-edge gap reported in 2026

Bhan, Nobili, and Langer used LLM-guided evolutionary search to produce many new lower-bound constructions for $Z(m,n,3,3)$ [BNL26]. They established three new exact values and reported a 103-one construction for the present $9\times23$ case. In their Figure 2, the $(9,23)$ cell has lower bound 103 and upper bound 104 and is not marked as tight. Thus the public status immediately before this work was

$$
103\le Z(9,23,3,3)\le104.
$$

The construction in this repository independently certifies the same lower bound. Credit for publicly reporting the 103 lower bound belongs to Bhan--Nobili--Langer. The contribution claimed here is the elementary upper-bound argument excluding 104, together with a reproducible verification package.

## 6. Relation of the present proof to prior methods

The proof uses only ingredients that are individually classical:

- Roman-style degree counting;
- the elementary identity obtained from
  $p(d)=\binom d3-6d+20$;
- a second double count after marking one row; and
- congruences modulo three.

What appears to be new is their combination at this boundary. The penalty identity reduces every hypothetical 104-one matrix to exactly three degree multisets. For each multiset, the marked-row deficits have an exact global sum but incompatible residue classes. This rules out all three possibilities without enumerating matrices.

This novelty assessment is intentionally modest. The authors located no earlier source containing this exact argument or closing this exact parameter, but a literature search is not a proof of priority. The mathematical claim $Z(9,23,3,3)=103$ stands independently of any novelty claim.

## 7. Status summary

| Date | Source | Contribution relevant here | Status of $Z(9,23,3,3)$ |
|---|---|---|---|
| 1951 | Zarankiewicz [Zar51] | Posed the matrix extremal problem | Not addressed at this scale |
| 1954 | Kővári--Sós--Turán [KST54] | General counting upper bound | General framework |
| 1975 | Roman [Rom75] | Strong finite degree bounds | Gives the 104 upper bound |
| 1978--2000 | Irving [Irv78]; Goddard--Henning--Oellermann [GHO00] | Finite values and bipartite Ramsey connections | Context, not a closure |
| 2016 | Collins--Riasanovsky--Wallace--Radziszowski [CRWR16] | Computational finite tables | Context, not a closure |
| 2022 | Tan [Tan22] | SAT-based finite tables | Lists 104 as an upper bound |
| 2026 | Davies--Gill--Horsley [DGH26] | Stronger degree-count LP | Does not improve this pair |
| 2026 | Bhan--Nobili--Langer [BNL26] | New 103-one construction | Establishes $103\le Z\le104$ |
| This repository | Elementary proof and checked witness | Excludes 104 and verifies 103 | $Z(9,23,3,3)=103$ |

## 8. Reproducibility of the literature claims

The bibliography is stored in [`references.bib`](../references.bib). Links below point to publisher, DOI, or arXiv records rather than copied papers. The three sources that directly establish the pre-existing numerical status are:

- [Tan, arXiv:2203.02283v2](https://arxiv.org/abs/2203.02283), Table 3;
- [Davies--Gill--Horsley, arXiv:2411.18842v2](https://arxiv.org/abs/2411.18842) and the [journal DOI](https://doi.org/10.1016/j.disc.2025.114924); and
- [Bhan--Nobili--Langer, arXiv:2605.01120v2](https://arxiv.org/abs/2605.01120), Figure 2.

The exact transcription of a table entry was checked against the rendered source, not inferred from search snippets. Dates and version identifiers are included because the recent preprints may be revised.

## References cited by key

The citation keys in this review expand as follows; full metadata appears in [`references.bib`](../references.bib).

- **[BNL26]** Bhan, Nobili, and Langer, *New Bounds for Zarankiewicz Numbers via Reinforced LLM Evolutionary Search*.
- **[CHM24]** Chen, Horsley, and Mammoliti, *Exact Values for Some Unbalanced Zarankiewicz Numbers*.
- **[Con21]** Conlon, *Some Remarks on the Zarankiewicz Problem*.
- **[CRWR16]** Collins, Riasanovsky, Wallace, and Radziszowski, *Zarankiewicz Numbers and Bipartite Ramsey Numbers*.
- **[Cul56]** Čulík, *Teilweise Lösung eines verallgemeinerten Problems von K. Zarankiewicz*.
- **[DGH26]** Davies, Gill, and Horsley, *Improved Upper Bounds on Zarankiewicz Numbers*.
- **[DHS13]** Damásdi, Héger, and Szőnyi, *The Zarankiewicz Problem, Cages, and Geometries*.
- **[FS13]** Füredi and Simonovits, *The History of Degenerate (Bipartite) Extremal Graph Problems*.
- **[Fur96]** Füredi, *An Upper Bound on Zarankiewicz' Problem*.
- **[GHO00]** Goddard, Henning, and Oellermann, *Bipartite Ramsey Numbers and Zarankiewicz Numbers*.
- **[Guy68, Guy69]** Guy's two early surveys of the problem.
- **[Irv78]** Irving, *A Bipartite Ramsey Problem and the Zarankiewicz Numbers*.
- **[KRS96]** Kollár, Rónyai, and Szabó, *Norm-Graphs and Bipartite Turán Numbers*.
- **[KST54]** Kővári, Sós, and Turán, *On a Problem of K. Zarankiewicz*.
- **[Nik10]** Nikiforov, *A Contribution to the Zarankiewicz Problem*.
- **[Rei58]** Reiman, *Über ein Problem von K. Zarankiewicz*.
- **[Rom75]** Roman, *A Problem of Zarankiewicz*.
- **[Tan22]** Tan, *An Attack on Zarankiewicz's Problem through SAT Solving*.
- **[TanCode]** Tan, *Kyoto* companion repository.
- **[Zar51]** Zarankiewicz, Problem P101.
