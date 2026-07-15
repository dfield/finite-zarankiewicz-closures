import Zarankiewicz.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Algebra.BigOperators.Ring.Finset
import Lean.Elab.Tactic.Omega

/-!
# Double-counting lemmas

Everything in this module is proved for an arbitrary finite Boolean matrix.
No finite search, solver result, or certificate enters these identities.
-/

namespace Zarankiewicz

open scoped BigOperators
open Finset

variable {R C : Type*} [Fintype R] [LinearOrder R]
  [Fintype C] [DecidableEq C]

/-- Every column degree is bounded by the number of rows. -/
theorem columnDegree_le_card (A : BinaryMatrix R C) (c : C) :
    columnDegree A c ≤ Fintype.card R := by
  simpa [columnDegree] using (card_le_univ (columnSupport A c))

/-- The increasing-triple definition controls the load of every unordered
three-element row set. -/
theorem tripleLoad_le_two (A : BinaryMatrix R C) (hA : K33Free A)
    (T : Finset R) (hT : T ∈ rowTriples R) : tripleLoad A T ≤ 2 := by
  have hcard : #T = 3 := (mem_powersetCard.1 hT).2
  obtain ⟨a, b, c, hab, hac, hbc, rfl⟩ := card_eq_three.1 hcard
  have load_eq : tripleLoad A {a, b, c} = commonColumnCount A a b c := by
    simp only [tripleLoad, commonColumnCount, columnSupport]
    congr 1
    ext j
    simp [Finset.subset_iff, and_assoc, and_left_comm, and_comm]
  rcases lt_or_gt_of_ne hab with hab' | hba
  · rcases lt_or_gt_of_ne hac with hac' | hca
    · rcases lt_or_gt_of_ne hbc with hbc' | hcb
      · rw [load_eq]
        exact hA a b c hab' hbc'
      · rw [load_eq]
        simpa [commonColumnCount, and_assoc, and_left_comm, and_comm] using
          hA a c b hac' hcb
    · rw [load_eq]
      simpa [commonColumnCount, and_assoc, and_left_comm, and_comm] using
        hA c a b hca hab'
  · rcases lt_or_gt_of_ne hbc with hbc' | hcb
    · rcases lt_or_gt_of_ne hac with hac' | hca
      · rw [load_eq]
        simpa [commonColumnCount, and_assoc, and_left_comm, and_comm] using
          hA b a c hba hac'
      · rw [load_eq]
        simpa [commonColumnCount, and_assoc, and_left_comm, and_comm] using
          hA b c a hbc' hca
    · rw [load_eq]
      simpa [commonColumnCount, and_assoc, and_left_comm, and_comm] using
        hA c b a hcb hba

/-- The row triples contained in a column are exactly the three-subsets of
that column's support. -/
theorem filter_rowTriples_subset_column (A : BinaryMatrix R C) (c : C) :
    (rowTriples R).filter (fun T => T ⊆ columnSupport A c) =
      (columnSupport A c).powersetCard 3 := by
  ext T
  simp [rowTriples, and_comm]

/-- A cardinality written as a sum of Boolean indicators. -/
theorem card_filter_eq_sum_indicator {α : Type*} [DecidableEq α]
    (s : Finset α) (p : α → Prop) [DecidablePred p] :
    #(s.filter p) = ∑ x ∈ s, if p x then 1 else 0 := by
  simp only [card_eq_sum_ones, sum_filter]

/-- The central double count: column triples equal row-triple loads. -/
theorem sum_choose_columnDegree_eq_sum_tripleLoad (A : BinaryMatrix R C) :
    (∑ c, Nat.choose (columnDegree A c) 3) =
      ∑ T ∈ rowTriples R, tripleLoad A T := by
  calc
    (∑ c, Nat.choose (columnDegree A c) 3) =
        ∑ c, #((columnSupport A c).powersetCard 3) := by
          apply sum_congr rfl
          intro c hc
          exact (card_powersetCard 3 (columnSupport A c)).symm
    _ = ∑ c, #((rowTriples R).filter (fun T => T ⊆ columnSupport A c)) := by
          apply sum_congr rfl
          intro c hc
          rw [filter_rowTriples_subset_column]
    _ = ∑ c, ∑ T ∈ rowTriples R,
          if T ⊆ columnSupport A c then 1 else 0 := by
          apply sum_congr rfl
          intro c hc
          exact card_filter_eq_sum_indicator _ _
    _ = ∑ T ∈ rowTriples R, ∑ c,
          if T ⊆ columnSupport A c then 1 else 0 := by
          rw [Finset.sum_comm]
    _ = ∑ T ∈ rowTriples R, tripleLoad A T := by
          apply sum_congr rfl
          intro T hT
          rw [tripleLoad, card_filter_eq_sum_indicator]

/-- Row-triple capacity for a `K_{3,3}`-free matrix. -/
theorem sum_choose_columnDegree_le (A : BinaryMatrix R C) (hA : K33Free A) :
    (∑ c, Nat.choose (columnDegree A c) 3) ≤
      2 * Nat.choose (Fintype.card R) 3 := by
  rw [sum_choose_columnDegree_eq_sum_tripleLoad]
  calc
    (∑ T ∈ rowTriples R, tripleLoad A T) ≤
        ∑ T ∈ rowTriples R, 2 := by
          exact sum_le_sum fun T hT => tripleLoad_le_two A hA T hT
    _ = #(rowTriples R) * 2 := sum_const_nat fun _ _ => rfl
    _ = Nat.choose (Fintype.card R) 3 * 2 := by
          simp [rowTriples, card_powersetCard]
    _ = 2 * Nat.choose (Fintype.card R) 3 := Nat.mul_comm _ _

/-- Number of columns of a specified degree. -/
def degreeCount (A : BinaryMatrix R C) (d : Nat) : Nat :=
  #(Finset.univ.filter fun c => columnDegree A c = d)

theorem columnDegree_ne_of_degreeCount_eq_zero (A : BinaryMatrix R C)
    (d : Nat) (hzero : degreeCount A d = 0) (c : C) :
    columnDegree A c ≠ d := by
  intro heq
  have hmem : c ∈ Finset.univ.filter (fun j => columnDegree A j = d) := by
    simp [heq]
  have hpos : 0 < degreeCount A d := by
    unfold degreeCount
    exact card_pos.mpr ⟨c, hmem⟩
  omega

/-- Regroup any column-degree statistic by degree fibers. -/
theorem sum_function_mul_degreeCount (A : BinaryMatrix R C) (f : Nat → Nat) :
    (∑ d ∈ range (Fintype.card R + 1), f d * degreeCount A d) =
      ∑ c, f (columnDegree A c) := by
  have hmap : ∀ c ∈ (Finset.univ : Finset C),
      columnDegree A c ∈ range (Fintype.card R + 1) := by
    intro c hc
    simp only [mem_range]
    have hle := columnDegree_le_card A c
    omega
  calc
    (∑ d ∈ range (Fintype.card R + 1), f d * degreeCount A d) =
        ∑ d ∈ range (Fintype.card R + 1),
          ∑ c ∈ Finset.univ with columnDegree A c = d, f d := by
            apply sum_congr rfl
            intro d hd
            unfold degreeCount
            rw [sum_const_nat (m := f d) (fun _ _ => rfl), Nat.mul_comm]
    _ = ∑ c ∈ Finset.univ, f (columnDegree A c) := by
          exact sum_fiberwise_of_maps_to' hmap f
    _ = ∑ c, f (columnDegree A c) := rfl

/-- The degree fibers partition all columns. -/
theorem sum_degreeCount (A : BinaryMatrix R C) :
    (∑ d ∈ range (Fintype.card R + 1), degreeCount A d) = Fintype.card C := by
  unfold degreeCount
  rw [sum_card_fiberwise_eq_card_filter Finset.univ
    (range (Fintype.card R + 1)) (columnDegree A)]
  have hall : Finset.univ.filter
      (fun c => columnDegree A c ∈ range (Fintype.card R + 1)) = Finset.univ := by
    apply filter_eq_self.2
    intro c hc
    simp only [mem_range]
    have hle := columnDegree_le_card A c
    omega
  rw [hall, card_univ]

/-- Weight recovered from the degree histogram. -/
theorem sum_degree_mul_degreeCount (A : BinaryMatrix R C) :
    (∑ d ∈ range (Fintype.card R + 1), d * degreeCount A d) = edgeCount A := by
  simpa [edgeCount] using sum_function_mul_degreeCount A (fun d => d)

/-! ## Triple deficits and marked rows -/

/-- Unused capacity on a row triple. -/
def tripleDeficit (A : BinaryMatrix R C) (T : Finset R) : Nat :=
  2 - tripleLoad A T

/-- Total unused row-triple capacity. -/
def totalDeficit (A : BinaryMatrix R C) : Nat :=
  ∑ T ∈ rowTriples R, tripleDeficit A T

/-- Unused plus used row-triple capacity is the full capacity. -/
theorem totalDeficit_add_sum_choose (A : BinaryMatrix R C) (hA : K33Free A) :
    totalDeficit A + (∑ c, Nat.choose (columnDegree A c) 3) =
      2 * Nat.choose (Fintype.card R) 3 := by
  rw [sum_choose_columnDegree_eq_sum_tripleLoad]
  unfold totalDeficit tripleDeficit
  rw [← sum_add_distrib]
  calc
    (∑ T ∈ rowTriples R, ((2 - tripleLoad A T) + tripleLoad A T)) =
        ∑ T ∈ rowTriples R, 2 := by
          apply sum_congr rfl
          intro T hT
          rw [Nat.sub_add_cancel (tripleLoad_le_two A hA T hT)]
    _ = #(rowTriples R) * 2 := sum_const_nat fun _ _ => rfl
    _ = Nat.choose (Fintype.card R) 3 * 2 := by
          simp [rowTriples, card_powersetCard]
    _ = 2 * Nat.choose (Fintype.card R) 3 := Nat.mul_comm _ _

/-- Unused capacity on triples containing a marked row. -/
def rowDeficit (A : BinaryMatrix R C) (r : R) : Nat :=
  ∑ T ∈ rowTriples R, if r ∈ T then tripleDeficit A T else 0

/-- Used capacity on triples containing a marked row. -/
def rowUsed (A : BinaryMatrix R C) (r : R) : Nat :=
  ∑ T ∈ rowTriples R, if r ∈ T then tripleLoad A T else 0

/-- Summing marked-row deficits counts each row triple three times. -/
theorem sum_rowDeficit (A : BinaryMatrix R C) :
    (∑ r, rowDeficit A r) = 3 * totalDeficit A := by
  unfold rowDeficit totalDeficit
  rw [Finset.sum_comm]
  calc
    (∑ T ∈ rowTriples R, ∑ r, if r ∈ T then tripleDeficit A T else 0) =
        ∑ T ∈ rowTriples R, 3 * tripleDeficit A T := by
          apply sum_congr rfl
          intro T hT
          have hcard : #T = 3 := (mem_powersetCard.1 hT).2
          rw [← sum_filter]
          have hfilter : (Finset.univ.filter fun r => r ∈ T) = T := by simp
          rw [hfilter, sum_const_nat (m := tripleDeficit A T) (fun _ _ => rfl),
            hcard, Nat.mul_comm]
    _ = 3 * ∑ T ∈ rowTriples R, tripleDeficit A T := by
          rw [mul_sum]

/-- Number of three-subsets of `S` that contain `r`. -/
def markedTripleCount (S : Finset R) (r : R) : Nat :=
  #((S.powersetCard 3).filter fun T => r ∈ T)

/-- Choosing a triple through `r` is the same as choosing two further
elements from `S \ {r}`. -/
theorem markedTripleCount_eq (S : Finset R) (r : R) :
    markedTripleCount S r =
      if r ∈ S then Nat.choose (#S - 1) 2 else 0 := by
  by_cases hr : r ∈ S
  · simp only [markedTripleCount, if_pos hr]
    let source := (S.powersetCard 3).filter fun T => r ∈ T
    let target := (S.erase r).powersetCard 2
    have hcard : #source = #target := by
      have hi : ∀ T ∈ source, T.erase r ∈ target := by
        intro T hT
        simp only [source, mem_filter, mem_powersetCard] at hT
        rcases hT with ⟨⟨hTS, hTcard⟩, hrT⟩
        apply mem_powersetCard.2
        constructor
        · intro x hx
          have hxT : x ∈ T := (mem_erase.1 hx).2
          have hxS : x ∈ S := hTS hxT
          exact mem_erase.2 ⟨(mem_erase.1 hx).1, hxS⟩
        · rw [card_erase_of_mem hrT, hTcard]
      have hj : ∀ U ∈ target, insert r U ∈ source := by
        intro U hU
        simp only [target, mem_powersetCard] at hU
        rcases hU with ⟨hUS, hUcard⟩
        simp only [source, mem_filter, mem_powersetCard]
        constructor
        · constructor
          · intro x hx
            rcases mem_insert.1 hx with rfl | hxU
            · exact hr
            · exact (erase_subset _ _ (hUS hxU))
          · have hnot : r ∉ U := by
              intro hru
              exact (mem_erase.1 (hUS hru)).1 rfl
            rw [card_insert_of_notMem hnot, hUcard]
        · exact mem_insert_self _ _
      have hleft : ∀ T (hT : T ∈ source), insert r (T.erase r) = T := by
        intro T hT
        simp only [source, mem_filter] at hT
        exact insert_erase hT.2
      have hright : ∀ U (hU : U ∈ target), (insert r U).erase r = U := by
        intro U hU
        simp only [target, mem_powersetCard] at hU
        have hnot : r ∉ U := by
          intro hru
          exact (mem_erase.1 (hU.1 hru)).1 rfl
        exact erase_insert hnot
      exact card_bij' (fun T _ => T.erase r) (fun U _ => insert r U)
        hi hj hleft hright
    rw [hcard, card_powersetCard, card_erase_of_mem hr]
  · simp only [markedTripleCount, if_neg hr]
    have hempty : (S.powersetCard 3).filter (fun T => r ∈ T) = ∅ := by
      apply eq_empty_iff_forall_notMem.2
      intro T hT
      simp only [mem_filter, mem_powersetCard] at hT
      exact hr (hT.1.1 hT.2)
    rw [hempty, card_empty]

/-- Swap the marked-row incidence count from row triples to columns. -/
theorem rowUsed_eq_sum_markedTripleCount (A : BinaryMatrix R C) (r : R) :
    rowUsed A r = ∑ c, markedTripleCount (columnSupport A c) r := by
  unfold rowUsed
  simp_rw [tripleLoad, card_filter_eq_sum_indicator]
  calc
    (∑ T ∈ rowTriples R,
        if r ∈ T then
          ∑ c ∈ Finset.univ, if T ⊆ columnSupport A c then 1 else 0
        else 0) =
        ∑ T ∈ rowTriples R, ∑ c,
          if r ∈ T ∧ T ⊆ columnSupport A c then 1 else 0 := by
          apply sum_congr rfl
          intro T hT
          by_cases hrT : r ∈ T <;> simp [hrT]
    _ = ∑ c, ∑ T ∈ rowTriples R,
          if r ∈ T ∧ T ⊆ columnSupport A c then 1 else 0 := by
          rw [Finset.sum_comm]
    _ = ∑ c, markedTripleCount (columnSupport A c) r := by
          apply sum_congr rfl
          intro c hc
          rw [← card_filter_eq_sum_indicator]
          unfold markedTripleCount
          congr 1
          ext T
          simp [rowTriples, and_assoc, and_left_comm, and_comm]

/-- The marked-row used capacity is the familiar column-degree expression. -/
theorem rowUsed_eq_sum_choose (A : BinaryMatrix R C) (r : R) :
    rowUsed A r =
      ∑ c, if A r c = true then Nat.choose (columnDegree A c - 1) 2 else 0 := by
  rw [rowUsed_eq_sum_markedTripleCount]
  apply sum_congr rfl
  intro c hc
  rw [markedTripleCount_eq]
  simp [columnSupport, columnDegree]

/-- Marked-row unused plus used capacity equals twice the number of row
triples through the marked row. -/
theorem rowDeficit_add_rowUsed (A : BinaryMatrix R C) (hA : K33Free A) (r : R) :
    rowDeficit A r + rowUsed A r =
      2 * Nat.choose (Fintype.card R - 1) 2 := by
  unfold rowDeficit rowUsed
  rw [← sum_add_distrib]
  calc
    (∑ T ∈ rowTriples R,
        ((if r ∈ T then tripleDeficit A T else 0) +
          if r ∈ T then tripleLoad A T else 0)) =
        ∑ T ∈ rowTriples R, if r ∈ T then 2 else 0 := by
          apply sum_congr rfl
          intro T hT
          by_cases hrT : r ∈ T
          · simp only [hrT, if_true, tripleDeficit]
            rw [Nat.sub_add_cancel (tripleLoad_le_two A hA T hT)]
          · simp [hrT]
    _ = 2 * markedTripleCount (Finset.univ : Finset R) r := by
          rw [← sum_filter, sum_const_nat (m := 2) (fun _ _ => rfl)]
          simp [markedTripleCount, rowTriples, Nat.mul_comm]
    _ = 2 * Nat.choose (Fintype.card R - 1) 2 := by
          rw [markedTripleCount_eq]
          simp

/-- Marked-row deficit formula used in the case proofs. -/
theorem rowDeficit_add_sum_choose (A : BinaryMatrix R C) (hA : K33Free A) (r : R) :
    rowDeficit A r +
      (∑ c, if A r c = true then Nat.choose (columnDegree A c - 1) 2 else 0) =
        2 * Nat.choose (Fintype.card R - 1) 2 := by
  rw [← rowUsed_eq_sum_choose]
  exact rowDeficit_add_rowUsed A hA r

/-! ## Removing ones -/

/-- The set of matrix ones, represented as a dependent pair `(column,row)`. -/
def edgeFinset (A : BinaryMatrix R C) : Finset (Σ _ : C, R) :=
  Finset.univ.sigma fun c => columnSupport A c

theorem card_edgeFinset (A : BinaryMatrix R C) : #(edgeFinset A) = edgeCount A := by
  simp [edgeFinset, edgeCount, columnDegree]

/-- Construct a matrix from a finite set of `(column,row)` incidences. -/
def ofEdgeFinset (E : Finset (Σ _ : C, R)) : BinaryMatrix R C :=
  fun r c => decide (Sigma.mk c r ∈ E)

theorem edgeFinset_ofEdgeFinset (E : Finset (Σ _ : C, R)) :
    edgeFinset (ofEdgeFinset E) = E := by
  ext x
  rcases x with ⟨c, r⟩
  simp [edgeFinset, ofEdgeFinset, columnSupport]

/-- Entrywise containment of ones. -/
def MatrixLE (A B : BinaryMatrix R C) : Prop :=
  ∀ r c, A r c = true → B r c = true

theorem ofEdgeFinset_le (A : BinaryMatrix R C) (E : Finset (Σ _ : C, R))
    (hE : E ⊆ edgeFinset A) : MatrixLE (ofEdgeFinset E) A := by
  intro r c hrc
  have hmem : Sigma.mk c r ∈ E := by
    simpa [ofEdgeFinset] using hrc
  have := hE hmem
  simpa [edgeFinset, columnSupport] using this

/-- Turning ones into zeros preserves `K_{3,3}`-freeness. -/
theorem K33Free.mono {A B : BinaryMatrix R C} (hA : K33Free A)
    (hBA : MatrixLE B A) : K33Free B := by
  intro a b c hab hbc
  apply le_trans (card_le_card ?_) (hA a b c hab hbc)
  intro j hj
  simp only [commonColumnCount, mem_filter, mem_univ, true_and] at hj ⊢
  exact ⟨hBA a j hj.1, hBA b j hj.2.1, hBA c j hj.2.2⟩

/-- Any prescribed number of ones up to the current weight can be retained. -/
theorem exists_submatrix_of_edgeCount_le (A : BinaryMatrix R C) (e : Nat)
    (he : e ≤ edgeCount A) :
    ∃ B : BinaryMatrix R C, MatrixLE B A ∧ edgeCount B = e := by
  have he' : e ≤ #(edgeFinset A) := by simpa [card_edgeFinset] using he
  obtain ⟨E, hEA, hEcard⟩ := exists_subset_card_eq he'
  refine ⟨ofEdgeFinset E, ofEdgeFinset_le A E hEA, ?_⟩
  rw [← card_edgeFinset, edgeFinset_ofEdgeFinset, hEcard]

/-- Sum a pointwise lower bound with one value on `E` and another off `E`. -/
theorem sum_lower_on_subset (f : R → Nat) (E : Finset R) (inside outside : Nat)
    (hin : ∀ r ∈ E, inside ≤ f r)
    (hout : ∀ r ∈ (Finset.univ : Finset R), r ∉ E → outside ≤ f r) :
    #E * inside + (Fintype.card R - #E) * outside ≤ ∑ r, f r := by
  have hsub : E ⊆ (Finset.univ : Finset R) := subset_univ E
  have hdecomp :
      (∑ r, f r) = (∑ r ∈ E, f r) + (∑ r ∈ Finset.univ \ E, f r) := by
    calc
      (∑ r, f r) = ∑ r ∈ E ∪ (Finset.univ \ E), f r := by
        rw [union_sdiff_of_subset hsub]
      _ = (∑ r ∈ E, f r) + (∑ r ∈ Finset.univ \ E, f r) :=
        sum_union disjoint_sdiff
  have hinSum : #E * inside ≤ ∑ r ∈ E, f r := by
    calc
      #E * inside = ∑ r ∈ E, inside := (sum_const_nat fun _ _ => rfl).symm
      _ ≤ ∑ r ∈ E, f r := sum_le_sum hin
  have houtSum : #(Finset.univ \ E) * outside ≤
      ∑ r ∈ Finset.univ \ E, f r := by
    calc
      #(Finset.univ \ E) * outside = ∑ r ∈ Finset.univ \ E, outside :=
        (sum_const_nat fun _ _ => rfl).symm
      _ ≤ ∑ r ∈ Finset.univ \ E, f r := by
        apply sum_le_sum
        intro r hr
        exact hout r (mem_univ r) (mem_sdiff.1 hr).2
  have hcard : #(Finset.univ \ E) = Fintype.card R - #E := by
    rw [card_sdiff_of_subset hsub, card_univ]
  rw [hcard] at houtSum
  calc
    #E * inside + (Fintype.card R - #E) * outside ≤
        (∑ r ∈ E, f r) + (∑ r ∈ Finset.univ \ E, f r) :=
      Nat.add_le_add hinSum houtSum
    _ = ∑ r, f r := hdecomp.symm

end Zarankiewicz
