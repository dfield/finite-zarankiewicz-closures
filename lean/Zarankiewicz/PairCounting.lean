import Zarankiewicz.Counting
import Lean.Elab.Tactic.Omega

/-!
# Pair-deficit identities

This module develops the pair analogue of the marked-row identities in
`Zarankiewicz.Counting`.  It is the common combinatorial bridge needed by the
`Z(10,22)` and `Z(12,23)` case proofs.
-/

namespace Zarankiewicz

open scoped BigOperators
open Finset

variable {R C : Type*} [Fintype R] [LinearOrder R]
  [Fintype C] [DecidableEq C]

/-- All unordered pairs of rows. -/
def rowPairs (R : Type*) [Fintype R] [DecidableEq R] : Finset (Finset R) :=
  Finset.univ.powersetCard 2

/-- Unused triple capacity on triples containing a fixed row pair. -/
def pairDeficit (A : BinaryMatrix R C) (P : Finset R) : Nat :=
  ∑ T ∈ rowTriples R, if P ⊆ T then tripleDeficit A T else 0

/-- Used triple capacity on triples containing a fixed row pair. -/
def pairUsed (A : BinaryMatrix R C) (P : Finset R) : Nat :=
  ∑ T ∈ rowTriples R, if P ⊆ T then tripleLoad A T else 0

/-- Summing pair deficits counts each row-triple deficit three times. -/
theorem sum_pairDeficit (A : BinaryMatrix R C) :
    (∑ P ∈ rowPairs R, pairDeficit A P) = 3 * totalDeficit A := by
  unfold pairDeficit totalDeficit
  rw [Finset.sum_comm]
  calc
    (∑ T ∈ rowTriples R,
        ∑ P ∈ rowPairs R, if P ⊆ T then tripleDeficit A T else 0) =
        ∑ T ∈ rowTriples R, 3 * tripleDeficit A T := by
          apply sum_congr rfl
          intro T hT
          have hcard : #T = 3 := (mem_powersetCard.1 hT).2
          rw [← sum_filter]
          have hfilter : (rowPairs R).filter (fun P => P ⊆ T) =
              T.powersetCard 2 := by
            ext P
            simp [rowPairs, rowTriples, and_comm]
          rw [hfilter, sum_const_nat (m := tripleDeficit A T) (fun _ _ => rfl),
            card_powersetCard, hcard]
          rfl
    _ = 3 * ∑ T ∈ rowTriples R, tripleDeficit A T := by
          exact (Finset.mul_sum _ _ _).symm

/-- Number of triples in `S` containing the two-element set `P`. -/
def pairTripleCount (S P : Finset R) : Nat :=
  #((S.powersetCard 3).filter fun T => P ⊆ T)

/-- A triple through a fixed pair is obtained by choosing one further point. -/
theorem pairTripleCount_eq (S P : Finset R) (hPcard : #P = 2) :
    pairTripleCount S P = if P ⊆ S then #S - 2 else 0 := by
  by_cases hPS : P ⊆ S
  · simp only [if_pos hPS]
    let source := (S.powersetCard 3).filter fun T => P ⊆ T
    let target := (S \ P).powersetCard 1
    have hcard : #source = #target := by
      have hi : ∀ T ∈ source, T \ P ∈ target := by
        intro T hT
        simp only [source, mem_filter, mem_powersetCard] at hT
        rcases hT with ⟨⟨hTS, hTcard⟩, hPT⟩
        apply mem_powersetCard.2
        constructor
        · intro x hx
          exact mem_sdiff.2 ⟨hTS (mem_sdiff.1 hx).1, (mem_sdiff.1 hx).2⟩
        · rw [card_sdiff_of_subset hPT, hTcard, hPcard]
      have hj : ∀ U ∈ target, P ∪ U ∈ source := by
        intro U hU
        simp only [target, mem_powersetCard] at hU
        rcases hU with ⟨hUS, hUcard⟩
        simp only [source, mem_filter, mem_powersetCard]
        have hdisj : Disjoint P U := by
          rw [Finset.disjoint_left]
          intro x hxP hxU
          exact (mem_sdiff.1 (hUS hxU)).2 hxP
        constructor
        · constructor
          · exact union_subset hPS (fun x hx => (mem_sdiff.1 (hUS hx)).1)
          · rw [card_union_of_disjoint hdisj, hPcard, hUcard]
        · exact subset_union_left
      have hleft : ∀ T (hT : T ∈ source), P ∪ (T \ P) = T := by
        intro T hT
        simp only [source, mem_filter] at hT
        ext x
        by_cases hxP : x ∈ P
        · simp [hxP, hT.2 hxP]
        · simp [hxP]
      have hright : ∀ U (hU : U ∈ target), (P ∪ U) \ P = U := by
        intro U hU
        simp only [target, mem_powersetCard] at hU
        ext x
        have hnot : x ∈ U → x ∉ P := fun hxU => (mem_sdiff.1 (hU.1 hxU)).2
        by_cases hxU : x ∈ U
        · simp [hxU, hnot hxU]
        · simp [hxU]
      exact card_bij' (fun T _ => T \ P) (fun U _ => P ∪ U)
        hi hj hleft hright
    unfold pairTripleCount
    rw [hcard, card_powersetCard, card_sdiff_of_subset hPS, hPcard]
    simp
  · simp only [if_neg hPS, pairTripleCount]
    have hempty : (S.powersetCard 3).filter (fun T => P ⊆ T) = ∅ := by
      apply eq_empty_iff_forall_notMem.2
      intro T hT
      simp only [mem_filter, mem_powersetCard] at hT
      exact hPS (hT.2.trans hT.1.1)
    rw [hempty, card_empty]

/-- Swap the pair incidence count from row triples to columns. -/
theorem pairUsed_eq_sum_pairTripleCount (A : BinaryMatrix R C) (P : Finset R) :
    pairUsed A P = ∑ c, pairTripleCount (columnSupport A c) P := by
  unfold pairUsed
  simp_rw [tripleLoad, card_filter_eq_sum_indicator]
  calc
    (∑ T ∈ rowTriples R,
        if P ⊆ T then
          ∑ c ∈ Finset.univ, if T ⊆ columnSupport A c then 1 else 0
        else 0) =
        ∑ T ∈ rowTriples R, ∑ c,
          if P ⊆ T ∧ T ⊆ columnSupport A c then 1 else 0 := by
          apply sum_congr rfl
          intro T hT
          by_cases hPT : P ⊆ T <;> simp [hPT]
    _ = ∑ c, ∑ T ∈ rowTriples R,
          if P ⊆ T ∧ T ⊆ columnSupport A c then 1 else 0 := by
          rw [Finset.sum_comm]
    _ = ∑ c, pairTripleCount (columnSupport A c) P := by
          apply sum_congr rfl
          intro c hc
          rw [← card_filter_eq_sum_indicator]
          unfold pairTripleCount
          congr 1
          ext T
          simp [rowTriples, and_assoc, and_left_comm, and_comm]

/-- The pair-used capacity is the column-degree expression from the paper. -/
theorem pairUsed_eq_sum_sub_two (A : BinaryMatrix R C) (P : Finset R)
    (hPcard : #P = 2) :
    pairUsed A P =
      ∑ c, if P ⊆ columnSupport A c then columnDegree A c - 2 else 0 := by
  rw [pairUsed_eq_sum_pairTripleCount]
  apply sum_congr rfl
  intro c hc
  rw [pairTripleCount_eq _ _ hPcard]
  rfl

/-- Pair-deficit plus pair-used capacity is twice the number of choices of a
third row. -/
theorem pairDeficit_add_pairUsed (A : BinaryMatrix R C) (hA : K33Free A)
    (P : Finset R) (hP : P ∈ rowPairs R) :
    pairDeficit A P + pairUsed A P = 2 * (Fintype.card R - 2) := by
  have hPcard : #P = 2 := (mem_powersetCard.1 hP).2
  unfold pairDeficit pairUsed
  rw [← sum_add_distrib]
  calc
    (∑ T ∈ rowTriples R,
        ((if P ⊆ T then tripleDeficit A T else 0) +
          if P ⊆ T then tripleLoad A T else 0)) =
        ∑ T ∈ rowTriples R, if P ⊆ T then 2 else 0 := by
          apply sum_congr rfl
          intro T hT
          by_cases hPT : P ⊆ T
          · simp only [hPT, if_true, tripleDeficit]
            rw [Nat.sub_add_cancel (tripleLoad_le_two A hA T hT)]
          · simp [hPT]
    _ = 2 * pairTripleCount (Finset.univ : Finset R) P := by
          rw [← sum_filter, sum_const_nat (m := 2) (fun _ _ => rfl)]
          simp [pairTripleCount, rowTriples, Nat.mul_comm]
    _ = 2 * (Fintype.card R - 2) := by
          rw [pairTripleCount_eq _ _ hPcard]
          simp

/-- Pair-deficit formula used in the case-specific proofs. -/
theorem pairDeficit_add_sum_sub_two (A : BinaryMatrix R C) (hA : K33Free A)
    (P : Finset R) (hP : P ∈ rowPairs R) :
    pairDeficit A P +
      (∑ c, if P ⊆ columnSupport A c then columnDegree A c - 2 else 0) =
        2 * (Fintype.card R - 2) := by
  rw [← pairUsed_eq_sum_sub_two A P (mem_powersetCard.1 hP).2]
  exact pairDeficit_add_pairUsed A hA P hP

/-! ## Degree-class incidences -/

/-- Number of degree-`d` columns through a fixed row. -/
def rowColumnDegreeCount (A : BinaryMatrix R C) (r : R) (d : Nat) : Nat :=
  #(Finset.univ.filter fun c => columnDegree A c = d ∧ A r c = true)

/-- Number of degree-`d` columns through a fixed row pair. -/
def pairColumnDegreeCount (A : BinaryMatrix R C) (P : Finset R) (d : Nat) : Nat :=
  #(Finset.univ.filter fun c =>
      columnDegree A c = d ∧ P ⊆ columnSupport A c)

theorem rowColumnDegreeCount_le_degreeCount
    (A : BinaryMatrix R C) (r : R) (d : Nat) :
    rowColumnDegreeCount A r d ≤ degreeCount A d := by
  apply card_le_card
  intro c hc
  simp only [rowColumnDegreeCount, mem_filter, mem_univ, true_and] at hc
  simp [degreeCount, hc.1]

theorem pairColumnDegreeCount_le_degreeCount
    (A : BinaryMatrix R C) (P : Finset R) (d : Nat) :
    pairColumnDegreeCount A P d ≤ degreeCount A d := by
  apply card_le_card
  intro c hc
  simp only [pairColumnDegreeCount, mem_filter, mem_univ, true_and] at hc
  simp [degreeCount, hc.1]

/-- A degree-class column containing a row pair also contains each marked row
of that pair. -/
theorem pairColumnDegreeCount_le_rowColumnDegreeCount_of_mem
    (A : BinaryMatrix R C) (P : Finset R) (r : R) (d : Nat) (hr : r ∈ P) :
    pairColumnDegreeCount A P d ≤ rowColumnDegreeCount A r d := by
  apply card_le_card
  intro c hc
  simp only [pairColumnDegreeCount, mem_filter, mem_univ, true_and] at hc
  simp only [rowColumnDegreeCount, mem_filter, mem_univ, true_and]
  exact ⟨hc.1, by
    have hrSupport := hc.2 hr
    simpa [columnSupport] using hrSupport⟩

/-- If a row lies in every column of a degree class, intersecting that class
with a second row does not lose any further columns beyond the second row. -/
theorem pairColumnDegreeCount_eq_rowColumnDegreeCount_of_full
    (A : BinaryMatrix R C) (r s : R) (d : Nat)
    (hfull : rowColumnDegreeCount A r d = degreeCount A d) :
    pairColumnDegreeCount A {r, s} d = rowColumnDegreeCount A s d := by
  let F : Finset C := Finset.univ.filter fun c => columnDegree A c = d
  let G : Finset C := Finset.univ.filter fun c =>
    columnDegree A c = d ∧ A r c = true
  have hGF : G ⊆ F := by
    intro c hc
    simp only [G, F, mem_filter, mem_univ, true_and] at hc ⊢
    exact hc.1
  have hcards : #G = #F := by
    simpa [G, F, rowColumnDegreeCount, degreeCount] using hfull
  have hFG : F = G := by
    exact (eq_of_subset_of_card_le hGF (by omega)).symm
  have hevery : ∀ c, columnDegree A c = d → A r c = true := by
    intro c hc
    have hcF : c ∈ F := by simp [F, hc]
    rw [hFG] at hcF
    exact (mem_filter.1 hcF).2.2
  unfold pairColumnDegreeCount rowColumnDegreeCount
  congr 1
  ext c
  simp only [mem_filter, mem_univ, true_and]
  constructor
  · rintro ⟨hcdeg, hpair⟩
    exact ⟨hcdeg, by
      have hsPair : s ∈ ({r, s} : Finset R) := by simp
      have hsSupport := hpair hsPair
      simpa [columnSupport] using hsSupport⟩
  · rintro ⟨hcdeg, hsc⟩
    refine ⟨hcdeg, ?_⟩
    rw [insert_subset_iff, singleton_subset_iff]
    constructor <;> simp [columnSupport, hevery c hcdeg, hsc]

/-- Pairs through one fixed row form a subfamily of all row pairs, so any
nonnegative statistic summed over them is bounded by its global pair sum. -/
theorem sum_through_row_le_sum_pairs (f : Finset R → Nat) (r : R) :
    (∑ s ∈ (Finset.univ : Finset R).erase r, f {r, s}) ≤
      ∑ P ∈ rowPairs R, f P := by
  let S : Finset R := (Finset.univ : Finset R).erase r
  let φ : R → Finset R := fun s => {r, s}
  have hinj : Set.InjOn φ S := by
    intro a ha b hb hab
    have har : a ≠ r := (mem_erase.1 ha).1
    have haMem : a ∈ φ a := by simp [φ]
    rw [hab] at haMem
    simp only [φ, mem_insert, mem_singleton] at haMem
    rcases haMem with harEq | habEq
    · exact (har harEq).elim
    · exact habEq
  have himage : S.image φ ⊆ rowPairs R := by
    intro P hP
    obtain ⟨s, hs, rfl⟩ := mem_image.1 hP
    have hsr : s ≠ r := (mem_erase.1 hs).1
    have hrs : r ≠ s := Ne.symm hsr
    simp [rowPairs, φ, hrs]
  calc
    (∑ s ∈ (Finset.univ : Finset R).erase r, f {r, s}) =
        ∑ s ∈ S, f (φ s) := by rfl
    _ = ∑ P ∈ S.image φ, f P := (sum_image hinj).symm
    _ ≤ ∑ P ∈ rowPairs R, f P := sum_le_sum_of_subset himage

/-- Row incidences with a degree class, counted by rows or by columns. -/
theorem sum_rowColumnDegreeCount (A : BinaryMatrix R C) (d : Nat) :
    (∑ r, rowColumnDegreeCount A r d) = d * degreeCount A d := by
  unfold rowColumnDegreeCount
  simp_rw [card_filter_eq_sum_indicator]
  rw [Finset.sum_comm]
  calc
    (∑ c, ∑ r,
        if columnDegree A c = d ∧ A r c = true then 1 else 0) =
        ∑ c, if columnDegree A c = d then d else 0 := by
          apply sum_congr rfl
          intro c hc
          by_cases hcd : columnDegree A c = d
          · simp only [hcd, true_and, if_true]
            rw [← card_filter_eq_sum_indicator]
            simpa [columnDegree, columnSupport] using hcd
          · simp [hcd]
    _ = d * degreeCount A d := by
          unfold degreeCount
          rw [card_filter_eq_sum_indicator, mul_sum]
          apply sum_congr rfl
          intro c hc
          by_cases hcd : columnDegree A c = d <;> simp [hcd]

/-- Pair incidences with a degree class, counted by pairs or by columns. -/
theorem sum_pairColumnDegreeCount (A : BinaryMatrix R C) (d : Nat) :
    (∑ P ∈ rowPairs R, pairColumnDegreeCount A P d) =
      Nat.choose d 2 * degreeCount A d := by
  unfold pairColumnDegreeCount
  simp_rw [card_filter_eq_sum_indicator]
  rw [Finset.sum_comm]
  calc
    (∑ c, ∑ P ∈ rowPairs R,
        if columnDegree A c = d ∧ P ⊆ columnSupport A c then 1 else 0) =
        ∑ c, if columnDegree A c = d then Nat.choose d 2 else 0 := by
          apply sum_congr rfl
          intro c hc
          by_cases hcd : columnDegree A c = d
          · simp only [hcd, true_and, if_true]
            rw [← card_filter_eq_sum_indicator]
            have hfilter : (rowPairs R).filter
                (fun P => P ⊆ columnSupport A c) =
                (columnSupport A c).powersetCard 2 := by
              ext P
              simp [rowPairs, and_comm]
            rw [hfilter, card_powersetCard]
            simpa [columnDegree] using congrArg (fun n => Nat.choose n 2) hcd
          · simp [hcd]
    _ = Nat.choose d 2 * degreeCount A d := by
          unfold degreeCount
          rw [card_filter_eq_sum_indicator, mul_sum]
          apply sum_congr rfl
          intro c hc
          by_cases hcd : columnDegree A c = d <;> simp [hcd]

/-- Degree-class pair incidences through one marked row. -/
theorem sum_pairColumnDegreeCount_through_row
    (A : BinaryMatrix R C) (r : R) (d : Nat) :
    (∑ s ∈ (Finset.univ : Finset R).erase r,
      pairColumnDegreeCount A {r, s} d) =
      (d - 1) * rowColumnDegreeCount A r d := by
  unfold pairColumnDegreeCount rowColumnDegreeCount
  simp_rw [card_filter_eq_sum_indicator]
  rw [Finset.sum_comm]
  have hcolumn : ∀ c : C,
      (∑ s ∈ (Finset.univ : Finset R).erase r,
        if columnDegree A c = d ∧ {r, s} ⊆ columnSupport A c then 1 else 0) =
      if columnDegree A c = d ∧ A r c = true then d - 1 else 0 := by
    intro c
    by_cases hcd : columnDegree A c = d
    · by_cases hrc : A r c = true
      · simp only [hcd, hrc, true_and, if_true]
        rw [← card_filter_eq_sum_indicator]
        have hfilter : ((Finset.univ : Finset R).erase r).filter
            (fun s => {r, s} ⊆ columnSupport A c) =
            (columnSupport A c).erase r := by
          ext s
          simp only [mem_filter, mem_erase, mem_univ, true_and]
          rw [insert_subset_iff, singleton_subset_iff]
          simp [columnSupport, hrc, and_comm]
        rw [hfilter, card_erase_of_mem (by simp [columnSupport, hrc])]
        simpa [columnDegree] using congrArg (fun n => n - 1) hcd
      · simp only [hcd, true_and, hrc, and_false, if_false]
        apply sum_eq_zero
        intro s hs
        simp only [ite_eq_right_iff]
        intro hsub
        exfalso
        apply hrc
        have hrmem : r ∈ columnSupport A c := hsub (by simp)
        simpa [columnSupport] using hrmem
    · simp [hcd]
  calc
    (∑ c, ∑ s ∈ (Finset.univ : Finset R).erase r,
        if columnDegree A c = d ∧ {r, s} ⊆ columnSupport A c then 1 else 0) =
        ∑ c, if columnDegree A c = d ∧ A r c = true then d - 1 else 0 := by
          apply sum_congr rfl
          intro c hc
          exact hcolumn c
    _ = (d - 1) *
        ∑ c ∈ Finset.univ,
          if columnDegree A c = d ∧ A r c = true then 1 else 0 := by
          rw [mul_sum]
          apply sum_congr rfl
          intro c hc
          by_cases h : columnDegree A c = d ∧ A r c = true <;> simp [h]

end Zarankiewicz
