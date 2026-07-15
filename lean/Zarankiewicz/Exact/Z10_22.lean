import Zarankiewicz.TripleIncidence
import Zarankiewicz.Witnesses
import ZarankiewiczFiniteClosures.ArithmeticKernels

/-!
# Pure-Lean proof of `Z(10,22,3,3) = 110`

This module internalizes the degree-profile and pair-deficit proof from
`docs/PROOF_Z10_22.md`.  In particular, the finite exceptional-column cases
are proved in Lean rather than imported from the Python certificate.
-/

namespace Zarankiewicz.Exact.Z10_22

open scoped BigOperators
open Finset
open Zarankiewicz

abbrev penalty := ZarankiewiczFiniteClosures.z10Penalty

theorem penalty_nat_identity : ∀ d : Fin 11,
    Nat.choose d.val 3 + 40 = 10 * d.val + penalty d.val := by
  decide

theorem incidence_penalty_identity (A : BinaryMatrix (Fin 10) (Fin 22)) :
    (∑ c, Nat.choose (columnDegree A c) 3) + 40 * 22 =
      10 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
  calc
    (∑ c, Nat.choose (columnDegree A c) 3) + 40 * 22 =
        (∑ c, Nat.choose (columnDegree A c) 3) + ∑ _c : Fin 22, 40 := by simp
    _ = ∑ c, (Nat.choose (columnDegree A c) 3 + 40) := sum_add_distrib.symm
    _ = ∑ c, (10 * columnDegree A c + penalty (columnDegree A c)) := by
      apply sum_congr rfl
      intro c hc
      have hlt : columnDegree A c < 11 := by
        have hle := columnDegree_le_card A c
        simpa using Nat.lt_succ_of_le hle
      exact penalty_nat_identity ⟨columnDegree A c, hlt⟩
    _ = (∑ c, 10 * columnDegree A c) + ∑ c, penalty (columnDegree A c) :=
      sum_add_distrib
    _ = 10 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
      rw [edgeCount, mul_sum]

theorem penalty_sum_eq_histogram (A : BinaryMatrix (Fin 10) (Fin 22)) :
    (∑ c, penalty (columnDegree A c)) =
      40 * degreeCount A 0 + 30 * degreeCount A 1 + 20 * degreeCount A 2 +
        11 * degreeCount A 3 + 4 * degreeCount A 4 + 5 * degreeCount A 7 +
        16 * degreeCount A 8 + 34 * degreeCount A 9 +
        60 * degreeCount A 10 := by
  have h := sum_function_mul_degreeCount A penalty
  symm
  simpa [Finset.sum_range_succ, ZarankiewiczFiniteClosures.z10Penalty,
    Nat.mul_comm, Nat.add_assoc] using h

theorem profile_at_111 (A : BinaryMatrix (Fin 10) (Fin 22))
    (hA : K33Free A) (hweight : edgeCount A = 111) :
    (degreeCount A 0 = 0 ∧ degreeCount A 1 = 0 ∧ degreeCount A 2 = 0 ∧
      degreeCount A 3 = 0 ∧ degreeCount A 8 = 0 ∧ degreeCount A 9 = 0 ∧
      degreeCount A 10 = 0) ∧
    ((degreeCount A 4 = 0 ∧ degreeCount A 5 = 21 ∧ degreeCount A 6 = 1 ∧
        degreeCount A 7 = 0) ∨
      (degreeCount A 4 = 1 ∧ degreeCount A 5 = 19 ∧ degreeCount A 6 = 2 ∧
        degreeCount A 7 = 0) ∨
      (degreeCount A 4 = 2 ∧ degreeCount A 5 = 17 ∧ degreeCount A 6 = 3 ∧
        degreeCount A 7 = 0) ∨
      (degreeCount A 4 = 1 ∧ degreeCount A 5 = 20 ∧ degreeCount A 6 = 0 ∧
        degreeCount A 7 = 1)) := by
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) ≤ 240 := by
    simpa using sum_choose_columnDegree_le A hA
  have hrel := incidence_penalty_identity A
  have hpenSum : (∑ c, penalty (columnDegree A c)) ≤ 10 := by omega
  have hpenalty :
      40 * degreeCount A 0 + 30 * degreeCount A 1 + 20 * degreeCount A 2 +
        11 * degreeCount A 3 + 4 * degreeCount A 4 + 5 * degreeCount A 7 +
        16 * degreeCount A 8 + 34 * degreeCount A 9 +
        60 * degreeCount A 10 ≤ 10 := by
    rw [← penalty_sum_eq_histogram]
    exact hpenSum
  obtain ⟨h0, h1, h2, h3, h8, h9, h10, h4le, h7le, hsmall⟩ :=
    ZarankiewiczFiniteClosures.z10_penalty_budget_structure
      (degreeCount A 0) (degreeCount A 1) (degreeCount A 2)
      (degreeCount A 3) (degreeCount A 4) (degreeCount A 7)
      (degreeCount A 8) (degreeCount A 9) (degreeCount A 10) hpenalty
  have hcolumnsFull := sum_degreeCount A
  have hcolumns : degreeCount A 4 + degreeCount A 5 + degreeCount A 6 +
      degreeCount A 7 = 22 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h8, h9, h10]
      using hcolumnsFull
  have hweightFull := sum_degree_mul_degreeCount A
  rw [hweight] at hweightFull
  have hdegrees : 4 * degreeCount A 4 + 5 * degreeCount A 5 +
      6 * degreeCount A 6 + 7 * degreeCount A 7 = 111 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h8, h9, h10,
      Nat.mul_comm] using hweightFull
  have hprofiles := ZarankiewiczFiniteClosures.classify_z10_22_degree_profile
    (degreeCount A 4) (degreeCount A 5) (degreeCount A 6) (degreeCount A 7)
    hcolumns hdegrees hsmall
  exact ⟨⟨h0, h1, h2, h3, h8, h9, h10⟩, hprofiles⟩

def contribution (A : BinaryMatrix (Fin 10) (Fin 22))
    (r : Fin 10) (c : Fin 22) : Nat :=
  if A r c = true then Nat.choose (columnDegree A c - 1) 2 else 0

def rowContribution (A : BinaryMatrix (Fin 10) (Fin 22)) (r : Fin 10) : Nat :=
  ∑ c, contribution A r c

theorem row_formula (A : BinaryMatrix (Fin 10) (Fin 22))
    (hA : K33Free A) (r : Fin 10) :
    rowDeficit A r + rowContribution A r = 72 := by
  simpa [rowContribution, contribution] using rowDeficit_add_sum_choose A hA r

theorem rowContribution_eq_degree_classes
    (A : BinaryMatrix (Fin 10) (Fin 22)) (r : Fin 10)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7) :
    rowContribution A r =
      3 * rowColumnDegreeCount A r 4 + 6 * rowColumnDegreeCount A r 5 +
        10 * rowColumnDegreeCount A r 6 + 15 * rowColumnDegreeCount A r 7 := by
  have hpoint : ∀ c : Fin 22,
      contribution A r c =
        (if columnDegree A c = 4 ∧ A r c = true then 3 else 0) +
        (if columnDegree A c = 5 ∧ A r c = true then 6 else 0) +
        (if columnDegree A c = 6 ∧ A r c = true then 10 else 0) +
        (if columnDegree A c = 7 ∧ A r c = true then 15 else 0) := by
    intro c
    rcases hdeg c with h4 | h5 | h6 | h7 <;>
      by_cases hrc : A r c = true <;>
        simp_all [contribution, Nat.choose]
  have hclass : ∀ d k : Nat,
      (∑ c : Fin 22, if columnDegree A c = d ∧ A r c = true then k else 0) =
        k * rowColumnDegreeCount A r d := by
    intro d k
    unfold rowColumnDegreeCount
    rw [card_filter_eq_sum_indicator, mul_sum]
    apply sum_congr rfl
    intro c hc
    by_cases h : columnDegree A c = d ∧ A r c = true <;> simp [h]
  calc
    rowContribution A r = ∑ c, contribution A r c := rfl
    _ = ∑ c,
        ((if columnDegree A c = 4 ∧ A r c = true then 3 else 0) +
        (if columnDegree A c = 5 ∧ A r c = true then 6 else 0) +
        (if columnDegree A c = 6 ∧ A r c = true then 10 else 0) +
        (if columnDegree A c = 7 ∧ A r c = true then 15 else 0)) := by
          apply sum_congr rfl
          intro c hc
          exact hpoint c
    _ = _ := by
          simp only [sum_add_distrib]
          rw [hclass 4 3, hclass 5 6, hclass 6 10, hclass 7 15]

theorem pairUsed_eq_degree_classes
    (A : BinaryMatrix (Fin 10) (Fin 22)) (P : Finset (Fin 10))
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7) :
    (∑ c, if P ⊆ columnSupport A c then columnDegree A c - 2 else 0) =
      2 * pairColumnDegreeCount A P 4 + 3 * pairColumnDegreeCount A P 5 +
        4 * pairColumnDegreeCount A P 6 + 5 * pairColumnDegreeCount A P 7 := by
  have hpoint : ∀ c : Fin 22,
      (if P ⊆ columnSupport A c then columnDegree A c - 2 else 0) =
        (if columnDegree A c = 4 ∧ P ⊆ columnSupport A c then 2 else 0) +
        (if columnDegree A c = 5 ∧ P ⊆ columnSupport A c then 3 else 0) +
        (if columnDegree A c = 6 ∧ P ⊆ columnSupport A c then 4 else 0) +
        (if columnDegree A c = 7 ∧ P ⊆ columnSupport A c then 5 else 0) := by
    intro c
    rcases hdeg c with h4 | h5 | h6 | h7 <;>
      by_cases hPc : P ⊆ columnSupport A c <;> simp_all
  have hclass : ∀ d k : Nat,
      (∑ c : Fin 22,
        if columnDegree A c = d ∧ P ⊆ columnSupport A c then k else 0) =
        k * pairColumnDegreeCount A P d := by
    intro d k
    unfold pairColumnDegreeCount
    rw [card_filter_eq_sum_indicator, mul_sum]
    apply sum_congr rfl
    intro c hc
    by_cases h : columnDegree A c = d ∧ P ⊆ columnSupport A c <;> simp [h]
  calc
    (∑ c, if P ⊆ columnSupport A c then columnDegree A c - 2 else 0) =
        ∑ c,
          ((if columnDegree A c = 4 ∧ P ⊆ columnSupport A c then 2 else 0) +
          (if columnDegree A c = 5 ∧ P ⊆ columnSupport A c then 3 else 0) +
          (if columnDegree A c = 6 ∧ P ⊆ columnSupport A c then 4 else 0) +
          (if columnDegree A c = 7 ∧ P ⊆ columnSupport A c then 5 else 0)) := by
            apply sum_congr rfl
            intro c hc
            exact hpoint c
    _ = _ := by
          simp only [sum_add_distrib]
          rw [hclass 4 2, hclass 5 3, hclass 6 4, hclass 7 5]

theorem choose_sum_eq_degree_classes
    (A : BinaryMatrix (Fin 10) (Fin 22))
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7) :
    (∑ c, Nat.choose (columnDegree A c) 3) =
      4 * degreeCount A 4 + 10 * degreeCount A 5 +
        20 * degreeCount A 6 + 35 * degreeCount A 7 := by
  have hpoint : ∀ c : Fin 22,
      Nat.choose (columnDegree A c) 3 =
        (if columnDegree A c = 4 then 4 else 0) +
        (if columnDegree A c = 5 then 10 else 0) +
        (if columnDegree A c = 6 then 20 else 0) +
        (if columnDegree A c = 7 then 35 else 0) := by
    intro c
    rcases hdeg c with h4 | h5 | h6 | h7 <;>
      simp_all [Nat.choose]
  have hclass : ∀ d k : Nat,
      (∑ c : Fin 22, if columnDegree A c = d then k else 0) =
        k * degreeCount A d := by
    intro d k
    unfold degreeCount
    rw [card_filter_eq_sum_indicator, mul_sum]
    apply sum_congr rfl
    intro c hc
    by_cases h : columnDegree A c = d <;> simp [h]
  calc
    (∑ c, Nat.choose (columnDegree A c) 3) =
        ∑ c,
          ((if columnDegree A c = 4 then 4 else 0) +
          (if columnDegree A c = 5 then 10 else 0) +
          (if columnDegree A c = 6 then 20 else 0) +
          (if columnDegree A c = 7 then 35 else 0)) := by
            apply sum_congr rfl
            intro c hc
            exact hpoint c
    _ = _ := by
          simp only [sum_add_distrib]
          rw [hclass 4 4, hclass 5 10, hclass 6 20, hclass 7 35]

private theorem choose_ten_three : Nat.choose 10 3 = 120 := by decide

private theorem eq_one_of_one_le_of_sum_le_card
    {X : Type*} [DecidableEq X] (s : Finset X) (f : X → Nat)
    (hlower : ∀ x ∈ s, 1 ≤ f x) (hsum : (∑ x ∈ s, f x) ≤ #s) :
    ∀ x ∈ s, f x = 1 := by
  intro x hx
  have hxLower := hlower x hx
  have hrest : #(s.erase x) ≤ ∑ y ∈ s.erase x, f y := by
    calc
      #(s.erase x) = ∑ _y ∈ s.erase x, 1 := by simp
      _ ≤ ∑ y ∈ s.erase x, f y := by
        apply sum_le_sum
        intro y hy
        exact hlower y (mem_of_mem_erase hy)
  have hsumErase := s.sum_erase_add f hx
  have hcardErase := card_erase_of_mem hx
  omega

private theorem card_zeros_add_sum_eq_card
    {X : Type*} [DecidableEq X] (s : Finset X) (f : X → Nat)
    (hbound : ∀ x ∈ s, f x ≤ 1) :
    #(s.filter fun x => f x = 0) + (∑ x ∈ s, f x) = #s := by
  rw [card_filter_eq_sum_indicator, ← sum_add_distrib]
  calc
    (∑ x ∈ s, ((if f x = 0 then 1 else 0) + f x)) =
        ∑ _x ∈ s, 1 := by
      apply sum_congr rfl
      intro x hx
      have hle := hbound x hx
      by_cases hzero : f x = 0
      · simp [hzero]
      · have hone : f x = 1 := by omega
        simp [hzero, hone]
    _ = #s := by simp

/-- The profile `5²¹·6` forces all thirty row pairs outside the unique
degree-six column to have deficit one.  Around a row outside that column this
would put five degree-five columns through each of nine pairs, but the resulting
sum 45 must be divisible by four. -/
theorem case_one_impossible
    (A : BinaryMatrix (Fin 10) (Fin 22)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 0) (h5 : degreeCount A 5 = 21)
    (h6 : degreeCount A 6 = 1) (h7 : degreeCount A 7 = 0) : False := by
  have hinc0 := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc0
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 230 := by
    simpa using hinc0
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 240 := by
    simpa [choose_ten_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 10 := by omega
  have hpairs := sum_pairDeficit A
  rw [hD] at hpairs
  have hpairs' : (∑ P ∈ rowPairs (Fin 10), pairDeficit A P) = 30 := by
    omega
  let Z : Finset (Finset (Fin 10)) := (rowPairs (Fin 10)).filter fun P =>
    pairColumnDegreeCount A P 6 = 0
  have hzBound : ∀ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 6 ≤ 1 := by
    intro P hP
    have h := pairColumnDegreeCount_le_degreeCount A P 6
    rw [h6] at h
    exact h
  have hsumZ0 := sum_pairColumnDegreeCount A 6
  rw [h6] at hsumZ0
  have hsumZ : (∑ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 6) = 15 := by
    simpa [Nat.choose] using hsumZ0
  have hpairCard : #(rowPairs (Fin 10)) = 45 := by
    simp [rowPairs, card_powersetCard, Nat.choose]
  have hpartition : #Z +
      (∑ P ∈ rowPairs (Fin 10), pairColumnDegreeCount A P 6) =
        #(rowPairs (Fin 10)) := by
    simpa [Z] using card_zeros_add_sum_eq_card (rowPairs (Fin 10))
      (fun P => pairColumnDegreeCount A P 6) hzBound
  have hZcard : #Z = 30 := by omega
  have hpairLower : ∀ P ∈ Z, 1 ≤ pairDeficit A P := by
    intro P hPZ
    have hP : P ∈ rowPairs (Fin 10) := (mem_filter.1 hPZ).1
    have hz : pairColumnDegreeCount A P 6 = 0 := (mem_filter.1 hPZ).2
    have hformula := pairDeficit_add_sum_sub_two A hA P hP
    have hclasses := pairUsed_eq_degree_classes A P hdeg
    rw [hclasses] at hformula
    simp at hformula
    have h4P := pairColumnDegreeCount_le_degreeCount A P 4
    have h7P := pairColumnDegreeCount_le_degreeCount A P 7
    rw [h4] at h4P
    rw [h7] at h7P
    omega
  have hZsum : (∑ P ∈ Z, pairDeficit A P) ≤ 30 := by
    calc
      (∑ P ∈ Z, pairDeficit A P) ≤
          ∑ P ∈ rowPairs (Fin 10), pairDeficit A P := by
            exact sum_le_sum_of_subset (filter_subset _ _)
      _ = 30 := hpairs'
  have hZsumCard : (∑ P ∈ Z, pairDeficit A P) ≤ #Z := by omega
  have hpairOne := eq_one_of_one_le_of_sum_le_card Z (pairDeficit A)
    hpairLower hZsumCard
  let R0 : Finset (Fin 10) := Finset.univ.filter fun r =>
    rowColumnDegreeCount A r 6 = 0
  have hsumRows0 := sum_rowColumnDegreeCount A 6
  rw [h6] at hsumRows0
  have hsumRows : (∑ r, rowColumnDegreeCount A r 6) = 6 := by omega
  have hrowPartition : #R0 + (∑ r, rowColumnDegreeCount A r 6) = 10 := by
    have hbound : ∀ r ∈ (Finset.univ : Finset (Fin 10)),
        rowColumnDegreeCount A r 6 ≤ 1 := by
      intro r hr
      have h := rowColumnDegreeCount_le_degreeCount A r 6
      rw [h6] at h
      exact h
    simpa [R0] using card_zeros_add_sum_eq_card (Finset.univ : Finset (Fin 10))
      (fun r => rowColumnDegreeCount A r 6) hbound
  have hR0card : #R0 = 4 := by omega
  have hR0nonempty : R0.Nonempty := card_pos.mp (by omega)
  obtain ⟨r, hrR0⟩ := hR0nonempty
  have hr6 : rowColumnDegreeCount A r 6 = 0 := (mem_filter.1 hrR0).2
  have hpairFive : ∀ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
      pairColumnDegreeCount A {r, s} 5 = 5 := by
    intro s hs
    have hsr : s ≠ r := (mem_erase.1 hs).1
    have hrs : r ≠ s := Ne.symm hsr
    have hPcard : #({r, s} : Finset (Fin 10)) = 2 := by simp [hrs]
    have hP : ({r, s} : Finset (Fin 10)) ∈ rowPairs (Fin 10) := by
      simp [rowPairs, hPcard]
    have hzle := pairColumnDegreeCount_le_rowColumnDegreeCount_of_mem
      A ({r, s} : Finset (Fin 10)) r 6 (by simp)
    have hz : pairColumnDegreeCount A {r, s} 6 = 0 := by omega
    have hPZ : ({r, s} : Finset (Fin 10)) ∈ Z := by
      simp [Z, hP, hz]
    have hdeficit : pairDeficit A {r, s} = 1 := hpairOne {r, s} hPZ
    have hformula := pairDeficit_add_sum_sub_two A hA {r, s} hP
    have hclasses := pairUsed_eq_degree_classes A {r, s} hdeg
    rw [hclasses, hdeficit] at hformula
    simp at hformula
    have h4P := pairColumnDegreeCount_le_degreeCount A {r, s} 4
    have h7P := pairColumnDegreeCount_le_degreeCount A {r, s} 7
    rw [h4] at h4P
    rw [h7] at h7P
    omega
  have hleft : (∑ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
      pairColumnDegreeCount A {r, s} 5) = 45 := by
    calc
      (∑ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
          pairColumnDegreeCount A {r, s} 5) =
          ∑ _s ∈ (Finset.univ : Finset (Fin 10)).erase r, 5 := by
            apply sum_congr rfl
            intro s hs
            exact hpairFive s hs
      _ = 45 := by simp
  have hthrough := sum_pairColumnDegreeCount_through_row A r 5
  rw [hleft] at hthrough
  simp at hthrough
  omega

def exceptionalPairResidue (A : BinaryMatrix (Fin 10) (Fin 22))
    (P : Finset (Fin 10)) : Nat :=
  (1 + pairColumnDegreeCount A P 4 +
    2 * pairColumnDegreeCount A P 6) % 3

/-- The profile `4·5¹⁹·6²` has residue sum at least 21.  This replaces
the former five-orbit enumeration with a single double-counting identity. -/
theorem case_two_impossible
    (A : BinaryMatrix (Fin 10) (Fin 22)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 1) (h5 : degreeCount A 5 = 19)
    (h6 : degreeCount A 6 = 2) (h7 : degreeCount A 7 = 0) : False := by
  have hinc0 := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc0
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 234 := by
    simpa using hinc0
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 240 := by
    simpa [choose_ten_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 6 := by omega
  have hpairs := sum_pairDeficit A
  rw [hD] at hpairs
  have hpairs' : (∑ P ∈ rowPairs (Fin 10), pairDeficit A P) = 18 := by
    omega
  have hxBound : ∀ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 4 ≤ 1 := by
    intro P hP
    have h := pairColumnDegreeCount_le_degreeCount A P 4
    rw [h4] at h
    exact h
  have hzBound : ∀ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 6 ≤ 2 := by
    intro P hP
    have h := pairColumnDegreeCount_le_degreeCount A P 6
    rw [h6] at h
    exact h
  have hresidueLower : ∀ P ∈ rowPairs (Fin 10),
      exceptionalPairResidue A P ≤ pairDeficit A P := by
    intro P hP
    have hformula := pairDeficit_add_sum_sub_two A hA P hP
    have hclasses := pairUsed_eq_degree_classes A P hdeg
    rw [hclasses] at hformula
    simp at hformula
    have h4P := pairColumnDegreeCount_le_degreeCount A P 4
    have h6P := pairColumnDegreeCount_le_degreeCount A P 6
    have h7P := pairColumnDegreeCount_le_degreeCount A P 7
    rw [h4] at h4P
    rw [h6] at h6P
    rw [h7] at h7P
    unfold exceptionalPairResidue
    omega
  have hresidueUpper :
      (∑ P ∈ rowPairs (Fin 10), exceptionalPairResidue A P) ≤ 18 := by
    calc
      (∑ P ∈ rowPairs (Fin 10), exceptionalPairResidue A P) ≤
          ∑ P ∈ rowPairs (Fin 10), pairDeficit A P :=
        sum_le_sum hresidueLower
      _ = 18 := hpairs'
  have hsumX0 := sum_pairColumnDegreeCount A 4
  rw [h4] at hsumX0
  have hsumX : (∑ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 4) = 6 := by
    simpa [Nat.choose] using hsumX0
  have hsumZ0 := sum_pairColumnDegreeCount A 6
  rw [h6] at hsumZ0
  have hsumZ : (∑ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 6) = 30 := by
    simpa [Nat.choose] using hsumZ0
  have hpointIdentity : ∀ P ∈ rowPairs (Fin 10),
      exceptionalPairResidue A P + pairColumnDegreeCount A P 6 +
          3 * (pairColumnDegreeCount A P 4 *
            Nat.choose (pairColumnDegreeCount A P 6) 2) =
        1 + pairColumnDegreeCount A P 4 +
          3 * Nat.choose (pairColumnDegreeCount A P 6) 2 := by
    intro P hP
    have hx := hxBound P hP
    have hz := hzBound P hP
    have hxcases : pairColumnDegreeCount A P 4 = 0 ∨
        pairColumnDegreeCount A P 4 = 1 := by omega
    have hzcases : pairColumnDegreeCount A P 6 = 0 ∨
        pairColumnDegreeCount A P 6 = 1 ∨
        pairColumnDegreeCount A P 6 = 2 := by omega
    rcases hxcases with hx0 | hx1 <;>
      rcases hzcases with hz0 | hz1 | hz2 <;>
      simp_all [exceptionalPairResidue, Nat.choose]
  have hidSum :
      (∑ P ∈ rowPairs (Fin 10),
        (exceptionalPairResidue A P + pairColumnDegreeCount A P 6 +
          3 * (pairColumnDegreeCount A P 4 *
            Nat.choose (pairColumnDegreeCount A P 6) 2))) =
      ∑ P ∈ rowPairs (Fin 10),
        (1 + pairColumnDegreeCount A P 4 +
          3 * Nat.choose (pairColumnDegreeCount A P 6) 2) := by
    apply sum_congr rfl
    intro P hP
    exact hpointIdentity P hP
  have hleftExpand :
      (∑ P ∈ rowPairs (Fin 10),
        (exceptionalPairResidue A P + pairColumnDegreeCount A P 6 +
          3 * (pairColumnDegreeCount A P 4 *
            Nat.choose (pairColumnDegreeCount A P 6) 2))) =
      (∑ P ∈ rowPairs (Fin 10), exceptionalPairResidue A P) +
        (∑ P ∈ rowPairs (Fin 10), pairColumnDegreeCount A P 6) +
        3 * (∑ P ∈ rowPairs (Fin 10),
          pairColumnDegreeCount A P 4 *
            Nat.choose (pairColumnDegreeCount A P 6) 2) := by
    rw [sum_add_distrib, sum_add_distrib, mul_sum]
  have hrightExpand :
      (∑ P ∈ rowPairs (Fin 10),
        (1 + pairColumnDegreeCount A P 4 +
          3 * Nat.choose (pairColumnDegreeCount A P 6) 2)) =
      #(rowPairs (Fin 10)) +
        (∑ P ∈ rowPairs (Fin 10), pairColumnDegreeCount A P 4) +
        3 * (∑ P ∈ rowPairs (Fin 10),
          Nat.choose (pairColumnDegreeCount A P 6) 2) := by
    rw [sum_add_distrib, sum_add_distrib, mul_sum]
    simp
  rw [hleftExpand, hrightExpand] at hidSum
  have hpairCard : #(rowPairs (Fin 10)) = 45 := by
    simp [rowPairs, card_powersetCard, Nat.choose]
  have hmixedLe :
      (∑ P ∈ rowPairs (Fin 10), pairColumnDegreeCount A P 4 *
        Nat.choose (pairColumnDegreeCount A P 6) 2) ≤
      ∑ P ∈ rowPairs (Fin 10),
        Nat.choose (pairColumnDegreeCount A P 6) 2 := by
    apply sum_le_sum
    intro P hP
    have hx := hxBound P hP
    have hxcases : pairColumnDegreeCount A P 4 = 0 ∨
        pairColumnDegreeCount A P 4 = 1 := by omega
    rcases hxcases with hzero | hone <;> simp_all
  have hresidueLowerSum : 21 ≤
      ∑ P ∈ rowPairs (Fin 10), exceptionalPairResidue A P := by
    omega
  omega

def caseThreeRowCode (A : BinaryMatrix (Fin 10) (Fin 22)) (r : Fin 10) : Nat :=
  4 * rowColumnDegreeCount A r 4 + rowColumnDegreeCount A r 6

def caseThreeRowTypeCount (A : BinaryMatrix (Fin 10) (Fin 22)) (k : Nat) : Nat :=
  #(Finset.univ.filter fun r => caseThreeRowCode A r = k)

def caseThreeRowResidue (A : BinaryMatrix (Fin 10) (Fin 22)) (r : Fin 10) : Nat :=
  (6 - ((3 * rowColumnDegreeCount A r 4 +
    4 * rowColumnDegreeCount A r 6) % 6)) % 6

def caseThreeCodeResidue (k : Nat) : Nat :=
  (6 - ((3 * (k / 4) + 4 * (k % 4)) % 6)) % 6

theorem caseThreeRowCode_div_four
    (A : BinaryMatrix (Fin 10) (Fin 22)) (r : Fin 10)
    (hsix : degreeCount A 6 ≤ 3) :
    caseThreeRowCode A r / 4 = rowColumnDegreeCount A r 4 := by
  have hz := rowColumnDegreeCount_le_degreeCount A r 6
  unfold caseThreeRowCode
  omega

theorem caseThreeRowCode_mod_four
    (A : BinaryMatrix (Fin 10) (Fin 22)) (r : Fin 10)
    (hsix : degreeCount A 6 ≤ 3) :
    caseThreeRowCode A r % 4 = rowColumnDegreeCount A r 6 := by
  have hz := rowColumnDegreeCount_le_degreeCount A r 6
  unfold caseThreeRowCode
  omega

theorem caseThreeCodeResidue_at_row
    (A : BinaryMatrix (Fin 10) (Fin 22)) (r : Fin 10)
    (hsix : degreeCount A 6 ≤ 3) :
    caseThreeCodeResidue (caseThreeRowCode A r) = caseThreeRowResidue A r := by
  simp only [caseThreeCodeResidue, caseThreeRowResidue,
    caseThreeRowCode_div_four A r hsix,
    caseThreeRowCode_mod_four A r hsix]

theorem sum_function_mul_caseThreeRowTypeCount
    (A : BinaryMatrix (Fin 10) (Fin 22))
    (hfour : degreeCount A 4 ≤ 2) (hsix : degreeCount A 6 ≤ 3)
    (f : Nat → Nat) :
    (∑ k ∈ range 12, f k * caseThreeRowTypeCount A k) =
      ∑ r, f (caseThreeRowCode A r) := by
  have hmap : ∀ r ∈ (Finset.univ : Finset (Fin 10)),
      caseThreeRowCode A r ∈ range 12 := by
    intro r hr
    simp only [mem_range]
    have hx := rowColumnDegreeCount_le_degreeCount A r 4
    have hz := rowColumnDegreeCount_le_degreeCount A r 6
    unfold caseThreeRowCode
    omega
  calc
    (∑ k ∈ range 12, f k * caseThreeRowTypeCount A k) =
        ∑ k ∈ range 12,
          ∑ r ∈ Finset.univ with caseThreeRowCode A r = k, f k := by
            apply sum_congr rfl
            intro k hk
            unfold caseThreeRowTypeCount
            rw [sum_const_nat (m := f k) (fun _ _ => rfl), Nat.mul_comm]
    _ = ∑ r ∈ Finset.univ, f (caseThreeRowCode A r) := by
          exact sum_fiberwise_of_maps_to' hmap f
    _ = ∑ r, f (caseThreeRowCode A r) := rfl

theorem case_three_row_profile_kernel
    (n0 n1 n2 n3 n4 n5 n6 n7 n8 n9 n10 n11 : Nat)
    (hrows : n0+n1+n2+n3+n4+n5+n6+n7+n8+n9+n10+n11 = 10)
    (hfour : n4+n5+n6+n7 + 2*n8+2*n9+2*n10+2*n11 = 8)
    (hsix : n1+2*n2+3*n3 + n5+2*n6+3*n7 + n9+2*n10+3*n11 = 18)
    (htriple : n3+n7+n11 ≤ 2)
    (hresidue : 2*n1+4*n2+3*n4+5*n5+n6+3*n7+2*n9+4*n10 ≤ 6) :
    n0 + n4 + n8 = 2 ∧
      n1 + n5 + n9 = 0 ∧
      n2 + n6 + n10 = 6 ∧
      n3 + n7 + n11 = 2 ∧
      n4 + n5 + n6 + n7 = 6 ∧
      n8 + n9 + n10 + n11 = 1 := by
  omega

theorem case_three_row_type_aggregates
    (A : BinaryMatrix (Fin 10) (Fin 22)) (hA : K33Free A)
    (h4 : degreeCount A 4 = 2) (h6 : degreeCount A 6 = 3)
    (hresidueSum : (∑ r, caseThreeRowResidue A r) ≤ 6) :
    caseThreeRowTypeCount A 0 + caseThreeRowTypeCount A 4 +
        caseThreeRowTypeCount A 8 = 2 ∧
      caseThreeRowTypeCount A 1 + caseThreeRowTypeCount A 5 +
        caseThreeRowTypeCount A 9 = 0 ∧
      caseThreeRowTypeCount A 2 + caseThreeRowTypeCount A 6 +
        caseThreeRowTypeCount A 10 = 6 ∧
      caseThreeRowTypeCount A 3 + caseThreeRowTypeCount A 7 +
        caseThreeRowTypeCount A 11 = 2 ∧
      caseThreeRowTypeCount A 4 + caseThreeRowTypeCount A 5 +
        caseThreeRowTypeCount A 6 + caseThreeRowTypeCount A 7 = 6 ∧
      caseThreeRowTypeCount A 8 + caseThreeRowTypeCount A 9 +
        caseThreeRowTypeCount A 10 + caseThreeRowTypeCount A 11 = 1 := by
  have hfourLe : degreeCount A 4 ≤ 2 := by omega
  have hsixLe : degreeCount A 6 ≤ 3 := by omega
  have hrows :
      caseThreeRowTypeCount A 0 + caseThreeRowTypeCount A 1 +
        caseThreeRowTypeCount A 2 + caseThreeRowTypeCount A 3 +
        caseThreeRowTypeCount A 4 + caseThreeRowTypeCount A 5 +
        caseThreeRowTypeCount A 6 + caseThreeRowTypeCount A 7 +
        caseThreeRowTypeCount A 8 + caseThreeRowTypeCount A 9 +
        caseThreeRowTypeCount A 10 + caseThreeRowTypeCount A 11 = 10 := by
    have h := sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe
      (fun _ => 1)
    simpa [sum_range_succ, Nat.add_assoc] using h
  have hfourTotal0 := sum_rowColumnDegreeCount A 4
  rw [h4] at hfourTotal0
  have hfourTotal : (∑ r, rowColumnDegreeCount A r 4) = 8 := by omega
  have hfourTypes :
      caseThreeRowTypeCount A 4 + caseThreeRowTypeCount A 5 +
        caseThreeRowTypeCount A 6 + caseThreeRowTypeCount A 7 +
        2 * caseThreeRowTypeCount A 8 + 2 * caseThreeRowTypeCount A 9 +
        2 * caseThreeRowTypeCount A 10 + 2 * caseThreeRowTypeCount A 11 = 8 := by
    calc
      _ = ∑ k ∈ range 12,
          (k / 4) * caseThreeRowTypeCount A k := by
            simp [sum_range_succ, Nat.add_assoc]
      _ = ∑ r, caseThreeRowCode A r / 4 :=
        sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe (fun k => k / 4)
      _ = ∑ r, rowColumnDegreeCount A r 4 := by
        apply sum_congr rfl
        intro r hr
        exact caseThreeRowCode_div_four A r hsixLe
      _ = 8 := hfourTotal
  have hsixTotal0 := sum_rowColumnDegreeCount A 6
  rw [h6] at hsixTotal0
  have hsixTotal : (∑ r, rowColumnDegreeCount A r 6) = 18 := by omega
  have hsixTypes :
      caseThreeRowTypeCount A 1 + 2 * caseThreeRowTypeCount A 2 +
        3 * caseThreeRowTypeCount A 3 + caseThreeRowTypeCount A 5 +
        2 * caseThreeRowTypeCount A 6 + 3 * caseThreeRowTypeCount A 7 +
        caseThreeRowTypeCount A 9 + 2 * caseThreeRowTypeCount A 10 +
        3 * caseThreeRowTypeCount A 11 = 18 := by
    calc
      _ = ∑ k ∈ range 12,
          (k % 4) * caseThreeRowTypeCount A k := by
            simp [sum_range_succ, Nat.add_assoc]
      _ = ∑ r, caseThreeRowCode A r % 4 :=
        sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe (fun k => k % 4)
      _ = ∑ r, rowColumnDegreeCount A r 6 := by
        apply sum_congr rfl
        intro r hr
        exact caseThreeRowCode_mod_four A r hsixLe
      _ = 18 := hsixTotal
  have htriple0 := sum_choose_rowColumnDegreeCount_le A hA 6
  rw [h6] at htriple0
  have htripleBound : (∑ r,
      Nat.choose (rowColumnDegreeCount A r 6) 3) ≤ 2 := by
    simpa [Nat.choose] using htriple0
  have htripleTypes :
      caseThreeRowTypeCount A 3 + caseThreeRowTypeCount A 7 +
        caseThreeRowTypeCount A 11 ≤ 2 := by
    calc
      _ = ∑ k ∈ range 12,
          Nat.choose (k % 4) 3 * caseThreeRowTypeCount A k := by
            simp [sum_range_succ, Nat.add_assoc, Nat.choose]
      _ = ∑ r, Nat.choose (caseThreeRowCode A r % 4) 3 :=
        sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe
          (fun k => Nat.choose (k % 4) 3)
      _ = ∑ r, Nat.choose (rowColumnDegreeCount A r 6) 3 := by
        apply sum_congr rfl
        intro r hr
        rw [caseThreeRowCode_mod_four A r hsixLe]
      _ ≤ 2 := htripleBound
  have hresidueTypes :
      2 * caseThreeRowTypeCount A 1 + 4 * caseThreeRowTypeCount A 2 +
        3 * caseThreeRowTypeCount A 4 + 5 * caseThreeRowTypeCount A 5 +
        caseThreeRowTypeCount A 6 + 3 * caseThreeRowTypeCount A 7 +
        2 * caseThreeRowTypeCount A 9 + 4 * caseThreeRowTypeCount A 10 ≤ 6 := by
    calc
      _ = ∑ k ∈ range 12,
          caseThreeCodeResidue k * caseThreeRowTypeCount A k := by
            simp [caseThreeCodeResidue, sum_range_succ, Nat.add_assoc]
      _ = ∑ r, caseThreeCodeResidue (caseThreeRowCode A r) :=
        sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe
          caseThreeCodeResidue
      _ = ∑ r, caseThreeRowResidue A r := by
        apply sum_congr rfl
        intro r hr
        exact caseThreeCodeResidue_at_row A r hsixLe
      _ ≤ 6 := hresidueSum
  exact case_three_row_profile_kernel
    (caseThreeRowTypeCount A 0) (caseThreeRowTypeCount A 1)
    (caseThreeRowTypeCount A 2) (caseThreeRowTypeCount A 3)
    (caseThreeRowTypeCount A 4) (caseThreeRowTypeCount A 5)
    (caseThreeRowTypeCount A 6) (caseThreeRowTypeCount A 7)
    (caseThreeRowTypeCount A 8) (caseThreeRowTypeCount A 9)
    (caseThreeRowTypeCount A 10) (caseThreeRowTypeCount A 11)
    hrows hfourTypes hsixTypes htripleTypes hresidueTypes

theorem case_three_row_residue_le
    (A : BinaryMatrix (Fin 10) (Fin 22)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 2) (h6 : degreeCount A 6 = 3)
    (h7 : degreeCount A 7 = 0) (r : Fin 10) :
    caseThreeRowResidue A r ≤ rowDeficit A r := by
  have hformula := row_formula A hA r
  have hclasses := rowContribution_eq_degree_classes A r hdeg
  rw [hclasses] at hformula
  have h4r := rowColumnDegreeCount_le_degreeCount A r 4
  have h6r := rowColumnDegreeCount_le_degreeCount A r 6
  have h7r := rowColumnDegreeCount_le_degreeCount A r 7
  rw [h4] at h4r
  rw [h6] at h6r
  rw [h7] at h7r
  have h4cases : rowColumnDegreeCount A r 4 = 0 ∨
      rowColumnDegreeCount A r 4 = 1 ∨
      rowColumnDegreeCount A r 4 = 2 := by omega
  have h6cases : rowColumnDegreeCount A r 6 = 0 ∨
      rowColumnDegreeCount A r 6 = 1 ∨
      rowColumnDegreeCount A r 6 = 2 ∨
      rowColumnDegreeCount A r 6 = 3 := by omega
  rcases h4cases with h40 | h41 | h42 <;>
    rcases h6cases with h60 | h61 | h62 | h63 <;>
    simp_all [caseThreeRowResidue] <;> omega

theorem case_three_row_choose_sums
    (A : BinaryMatrix (Fin 10) (Fin 22))
    (h4 : degreeCount A 4 = 2) (h6 : degreeCount A 6 = 3)
    (hagg :
      caseThreeRowTypeCount A 0 + caseThreeRowTypeCount A 4 +
          caseThreeRowTypeCount A 8 = 2 ∧
        caseThreeRowTypeCount A 1 + caseThreeRowTypeCount A 5 +
          caseThreeRowTypeCount A 9 = 0 ∧
        caseThreeRowTypeCount A 2 + caseThreeRowTypeCount A 6 +
          caseThreeRowTypeCount A 10 = 6 ∧
        caseThreeRowTypeCount A 3 + caseThreeRowTypeCount A 7 +
          caseThreeRowTypeCount A 11 = 2 ∧
        caseThreeRowTypeCount A 4 + caseThreeRowTypeCount A 5 +
          caseThreeRowTypeCount A 6 + caseThreeRowTypeCount A 7 = 6 ∧
        caseThreeRowTypeCount A 8 + caseThreeRowTypeCount A 9 +
          caseThreeRowTypeCount A 10 + caseThreeRowTypeCount A 11 = 1) :
    (∑ r, Nat.choose (rowColumnDegreeCount A r 4) 2) = 1 ∧
      (∑ r, Nat.choose (rowColumnDegreeCount A r 6) 2) = 12 ∧
      (∑ r, Nat.choose (rowColumnDegreeCount A r 6) 3) = 2 := by
  have hfourLe : degreeCount A 4 ≤ 2 := by omega
  have hsixLe : degreeCount A 6 ≤ 3 := by omega
  have hx : (∑ r, Nat.choose (rowColumnDegreeCount A r 4) 2) = 1 := by
    calc
      _ = ∑ r, Nat.choose (caseThreeRowCode A r / 4) 2 := by
        apply sum_congr rfl
        intro r hr
        rw [caseThreeRowCode_div_four A r hsixLe]
      _ = ∑ k ∈ range 12,
          Nat.choose (k / 4) 2 * caseThreeRowTypeCount A k :=
        (sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe
          (fun k => Nat.choose (k / 4) 2)).symm
      _ = caseThreeRowTypeCount A 8 + caseThreeRowTypeCount A 9 +
          caseThreeRowTypeCount A 10 + caseThreeRowTypeCount A 11 := by
            simp [sum_range_succ, Nat.choose, Nat.add_assoc]
      _ = 1 := hagg.2.2.2.2.2
  have hzTwo : (∑ r, Nat.choose (rowColumnDegreeCount A r 6) 2) = 12 := by
    calc
      _ = ∑ r, Nat.choose (caseThreeRowCode A r % 4) 2 := by
        apply sum_congr rfl
        intro r hr
        rw [caseThreeRowCode_mod_four A r hsixLe]
      _ = ∑ k ∈ range 12,
          Nat.choose (k % 4) 2 * caseThreeRowTypeCount A k :=
        (sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe
          (fun k => Nat.choose (k % 4) 2)).symm
      _ = caseThreeRowTypeCount A 2 +
          3 * caseThreeRowTypeCount A 3 + caseThreeRowTypeCount A 6 +
          3 * caseThreeRowTypeCount A 7 + caseThreeRowTypeCount A 10 +
          3 * caseThreeRowTypeCount A 11 := by
            simp [sum_range_succ, Nat.choose, Nat.add_assoc]
      _ = 12 := by omega
  have hzThree : (∑ r, Nat.choose (rowColumnDegreeCount A r 6) 3) = 2 := by
    calc
      _ = ∑ r, Nat.choose (caseThreeRowCode A r % 4) 3 := by
        apply sum_congr rfl
        intro r hr
        rw [caseThreeRowCode_mod_four A r hsixLe]
      _ = ∑ k ∈ range 12,
          Nat.choose (k % 4) 3 * caseThreeRowTypeCount A k :=
        (sum_function_mul_caseThreeRowTypeCount A hfourLe hsixLe
          (fun k => Nat.choose (k % 4) 3)).symm
      _ = caseThreeRowTypeCount A 3 + caseThreeRowTypeCount A 7 +
          caseThreeRowTypeCount A 11 := by
            simp [sum_range_succ, Nat.choose, Nat.add_assoc]
      _ = 2 := hagg.2.2.2.1
  exact ⟨hx, hzTwo, hzThree⟩

theorem pairColumnDegreeCount_le_one_of_row_choose_sum_eq_one
    (A : BinaryMatrix (Fin 10) (Fin 22)) (d : Nat)
    (hrow : (∑ r, Nat.choose (rowColumnDegreeCount A r d) 2) = 1) :
    ∀ P ∈ rowPairs (Fin 10), pairColumnDegreeCount A P d ≤ 1 := by
  intro P hP
  by_contra hnot
  have hpairTwo : 2 ≤ pairColumnDegreeCount A P d := by omega
  have hPcard : #P = 2 := (mem_powersetCard.1 hP).2
  have hterm : ∀ r ∈ P,
      Nat.choose (rowColumnDegreeCount A r d) 2 ≥ 1 := by
    intro r hr
    have hle := pairColumnDegreeCount_le_rowColumnDegreeCount_of_mem A P r d hr
    have hrowTwo : 2 ≤ rowColumnDegreeCount A r d := by omega
    exact Nat.choose_pos hrowTwo
  have hlower : 2 ≤ ∑ r ∈ P,
      Nat.choose (rowColumnDegreeCount A r d) 2 := by
    calc
      2 = ∑ _r ∈ P, 1 := by simp [hPcard]
      _ ≤ ∑ r ∈ P, Nat.choose (rowColumnDegreeCount A r d) 2 := by
        apply sum_le_sum
        intro r hr
        exact hterm r hr
  have hsubset : (∑ r ∈ P, Nat.choose (rowColumnDegreeCount A r d) 2) ≤
      ∑ r, Nat.choose (rowColumnDegreeCount A r d) 2 := by
    exact sum_le_sum_of_subset (by simp)
  omega

theorem case_three_pair_choose_two_lower
    (A : BinaryMatrix (Fin 10) (Fin 22))
    (h6 : degreeCount A 6 = 3)
    (hzTwo : (∑ r, Nat.choose (rowColumnDegreeCount A r 6) 2) = 12)
    (hzThree : (∑ r, Nat.choose (rowColumnDegreeCount A r 6) 3) = 2) :
    9 ≤ ∑ P ∈ rowPairs (Fin 10),
      Nat.choose (pairColumnDegreeCount A P 6) 2 := by
  have hsixLe : degreeCount A 6 ≤ 3 := by omega
  have hrExists : ∃ r : Fin 10, rowColumnDegreeCount A r 6 = 3 := by
    by_contra hnone
    have hnot : ∀ r : Fin 10, rowColumnDegreeCount A r 6 ≠ 3 :=
      not_exists.mp hnone
    have hzero : ∀ r : Fin 10,
        Nat.choose (rowColumnDegreeCount A r 6) 3 = 0 := by
      intro r
      have hrle := rowColumnDegreeCount_le_degreeCount A r 6
      rw [h6] at hrle
      have hrne := hnot r
      have hcases : rowColumnDegreeCount A r 6 = 0 ∨
          rowColumnDegreeCount A r 6 = 1 ∨
          rowColumnDegreeCount A r 6 = 2 := by omega
      rcases hcases with hr0 | hr1 | hr2
      · simp [hr0, Nat.choose]
      · simp [hr1, Nat.choose]
      · simp [hr2, Nat.choose]
    have hsumZero : (∑ r, Nat.choose (rowColumnDegreeCount A r 6) 3) = 0 := by
      apply sum_eq_zero
      intro r hr
      exact hzero r
    omega
  obtain ⟨r, hrSix⟩ := hrExists
  have hfull : rowColumnDegreeCount A r 6 = degreeCount A 6 := by omega
  have hthroughEq : ∀ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
      pairColumnDegreeCount A {r, s} 6 = rowColumnDegreeCount A s 6 := by
    intro s hs
    exact pairColumnDegreeCount_eq_rowColumnDegreeCount_of_full A r s 6 hfull
  have hrowEraseAdd :
      (∑ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
          Nat.choose (rowColumnDegreeCount A s 6) 2) +
        Nat.choose (rowColumnDegreeCount A r 6) 2 = 12 := by
    simpa using (Finset.univ.sum_erase_add
      (fun s : Fin 10 => Nat.choose (rowColumnDegreeCount A s 6) 2)
      (mem_univ r)).trans hzTwo
  have hrowErase :
      (∑ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
        Nat.choose (rowColumnDegreeCount A s 6) 2) = 9 := by
    simp [hrSix] at hrowEraseAdd
    omega
  have hthrough :
      (∑ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
        Nat.choose (pairColumnDegreeCount A {r, s} 6) 2) = 9 := by
    calc
      _ = ∑ s ∈ (Finset.univ : Finset (Fin 10)).erase r,
          Nat.choose (rowColumnDegreeCount A s 6) 2 := by
            apply sum_congr rfl
            intro s hs
            rw [hthroughEq s hs]
      _ = 9 := hrowErase
  have hle := sum_through_row_le_sum_pairs
    (fun P : Finset (Fin 10) => Nat.choose (pairColumnDegreeCount A P 6) 2) r
  rw [hthrough] at hle
  exact hle

theorem case_three_pair_residue_le
    (A : BinaryMatrix (Fin 10) (Fin 22)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 2) (h6 : degreeCount A 6 = 3)
    (h7 : degreeCount A 7 = 0) (P : Finset (Fin 10))
    (hP : P ∈ rowPairs (Fin 10)) :
    exceptionalPairResidue A P ≤ pairDeficit A P := by
  have hformula := pairDeficit_add_sum_sub_two A hA P hP
  have hclasses := pairUsed_eq_degree_classes A P hdeg
  rw [hclasses] at hformula
  simp at hformula
  have h4P := pairColumnDegreeCount_le_degreeCount A P 4
  have h6P := pairColumnDegreeCount_le_degreeCount A P 6
  have h7P := pairColumnDegreeCount_le_degreeCount A P 7
  rw [h4] at h4P
  rw [h6] at h6P
  rw [h7] at h7P
  have h4cases : pairColumnDegreeCount A P 4 = 0 ∨
      pairColumnDegreeCount A P 4 = 1 ∨
      pairColumnDegreeCount A P 4 = 2 := by omega
  have h6cases : pairColumnDegreeCount A P 6 = 0 ∨
      pairColumnDegreeCount A P 6 = 1 ∨
      pairColumnDegreeCount A P 6 = 2 ∨
      pairColumnDegreeCount A P 6 = 3 := by omega
  rcases h4cases with h40 | h41 | h42 <;>
    rcases h6cases with h60 | h61 | h62 | h63 <;>
    simp_all [exceptionalPairResidue] <;> omega

theorem case_three_pair_residue_identity
    (A : BinaryMatrix (Fin 10) (Fin 22)) (P : Finset (Fin 10))
    (hx : pairColumnDegreeCount A P 4 ≤ 1)
    (hz : pairColumnDegreeCount A P 6 ≤ 3) :
    exceptionalPairResidue A P + pairColumnDegreeCount A P 6 +
        6 * Nat.choose (pairColumnDegreeCount A P 6) 3 +
        3 * (Nat.choose (pairColumnDegreeCount A P 6) 2 *
          pairColumnDegreeCount A P 4) =
      1 + pairColumnDegreeCount A P 4 +
        3 * Nat.choose (pairColumnDegreeCount A P 6) 2 +
        9 * (pairColumnDegreeCount A P 4 *
          Nat.choose (pairColumnDegreeCount A P 6) 3) := by
  have hxcases : pairColumnDegreeCount A P 4 = 0 ∨
      pairColumnDegreeCount A P 4 = 1 := by omega
  have hzcases : pairColumnDegreeCount A P 6 = 0 ∨
      pairColumnDegreeCount A P 6 = 1 ∨
      pairColumnDegreeCount A P 6 = 2 ∨
      pairColumnDegreeCount A P 6 = 3 := by omega
  rcases hxcases with hx0 | hx1 <;>
    rcases hzcases with hz0 | hz1 | hz2 | hz3 <;>
    simp_all [exceptionalPairResidue, Nat.choose]

/-- The profile `4²·5¹⁷·6³` is impossible.  The row-type constraints force
at least nine repeated degree-six overlaps on row pairs; the resulting
mod-three residue budget exceeds the complete pair-deficit budget. -/
theorem case_three_impossible
    (A : BinaryMatrix (Fin 10) (Fin 22)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 2) (h5 : degreeCount A 5 = 17)
    (h6 : degreeCount A 6 = 3) (h7 : degreeCount A 7 = 0) : False := by
  have hinc0 := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc0
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 238 := by
    simpa using hinc0
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 240 := by
    simpa [choose_ten_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 2 := by omega
  have hrows0 := sum_rowDeficit A
  rw [hD] at hrows0
  have hrows : (∑ r, rowDeficit A r) = 6 := by omega
  have hpairs0 := sum_pairDeficit A
  rw [hD] at hpairs0
  have hpairs : (∑ P ∈ rowPairs (Fin 10), pairDeficit A P) = 6 := by omega
  have hrowResidueSum : (∑ r, caseThreeRowResidue A r) ≤ 6 := by
    calc
      (∑ r, caseThreeRowResidue A r) ≤ ∑ r, rowDeficit A r := by
        apply sum_le_sum
        intro r hr
        exact case_three_row_residue_le A hA hdeg h4 h6 h7 r
      _ = 6 := hrows
  have hagg := case_three_row_type_aggregates A hA h4 h6 hrowResidueSum
  obtain ⟨hxRows, hzRowsTwo, hzRowsThree⟩ :=
    case_three_row_choose_sums A h4 h6 hagg
  have hxPair : ∀ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 4 ≤ 1 :=
    pairColumnDegreeCount_le_one_of_row_choose_sum_eq_one A 4 hxRows
  have hzPair : ∀ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 6 ≤ 3 := by
    intro P hP
    have h := pairColumnDegreeCount_le_degreeCount A P 6
    rw [h6] at h
    exact h
  have hpairResidueSum :
      (∑ P ∈ rowPairs (Fin 10), exceptionalPairResidue A P) ≤ 6 := by
    calc
      (∑ P ∈ rowPairs (Fin 10), exceptionalPairResidue A P) ≤
          ∑ P ∈ rowPairs (Fin 10), pairDeficit A P := by
            apply sum_le_sum
            intro P hP
            exact case_three_pair_residue_le A hA hdeg h4 h6 h7 P hP
      _ = 6 := hpairs
  have hsumX0 := sum_pairColumnDegreeCount A 4
  rw [h4] at hsumX0
  have hsumX : (∑ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 4) = 12 := by
    simpa [Nat.choose] using hsumX0
  have hsumZ0 := sum_pairColumnDegreeCount A 6
  rw [h6] at hsumZ0
  have hsumZ : (∑ P ∈ rowPairs (Fin 10),
      pairColumnDegreeCount A P 6) = 45 := by
    simpa [Nat.choose] using hsumZ0
  have hchooseTwoLower :=
    case_three_pair_choose_two_lower A h6 hzRowsTwo hzRowsThree
  have hchooseThree0 := sum_choose_pairColumnDegreeCount_le A hA 6
  rw [h6] at hchooseThree0
  have hchooseThree :
      (∑ P ∈ rowPairs (Fin 10),
        Nat.choose (pairColumnDegreeCount A P 6) 3) ≤ 1 := by
    simpa [Nat.choose] using hchooseThree0
  have hmixed0 := sum_choose_two_mul_pairColumnDegreeCount_le
    A hA 6 4 (by omega)
  rw [h6, h4] at hmixed0
  have hmixed :
      (∑ P ∈ rowPairs (Fin 10),
        Nat.choose (pairColumnDegreeCount A P 6) 2 *
          pairColumnDegreeCount A P 4) ≤ 6 := by
    simpa [Nat.choose] using hmixed0
  have hidSum :
      (∑ P ∈ rowPairs (Fin 10),
        (exceptionalPairResidue A P + pairColumnDegreeCount A P 6 +
          6 * Nat.choose (pairColumnDegreeCount A P 6) 3 +
          3 * (Nat.choose (pairColumnDegreeCount A P 6) 2 *
            pairColumnDegreeCount A P 4))) =
      ∑ P ∈ rowPairs (Fin 10),
        (1 + pairColumnDegreeCount A P 4 +
          3 * Nat.choose (pairColumnDegreeCount A P 6) 2 +
          9 * (pairColumnDegreeCount A P 4 *
            Nat.choose (pairColumnDegreeCount A P 6) 3)) := by
    apply sum_congr rfl
    intro P hP
    exact case_three_pair_residue_identity A P (hxPair P hP) (hzPair P hP)
  have hleftExpand :
      (∑ P ∈ rowPairs (Fin 10),
        (exceptionalPairResidue A P + pairColumnDegreeCount A P 6 +
          6 * Nat.choose (pairColumnDegreeCount A P 6) 3 +
          3 * (Nat.choose (pairColumnDegreeCount A P 6) 2 *
            pairColumnDegreeCount A P 4))) =
      (∑ P ∈ rowPairs (Fin 10), exceptionalPairResidue A P) +
        (∑ P ∈ rowPairs (Fin 10), pairColumnDegreeCount A P 6) +
        6 * (∑ P ∈ rowPairs (Fin 10),
          Nat.choose (pairColumnDegreeCount A P 6) 3) +
        3 * (∑ P ∈ rowPairs (Fin 10),
          Nat.choose (pairColumnDegreeCount A P 6) 2 *
            pairColumnDegreeCount A P 4) := by
    rw [sum_add_distrib, sum_add_distrib, sum_add_distrib, mul_sum, mul_sum]
  have hrightExpand :
      (∑ P ∈ rowPairs (Fin 10),
        (1 + pairColumnDegreeCount A P 4 +
          3 * Nat.choose (pairColumnDegreeCount A P 6) 2 +
          9 * (pairColumnDegreeCount A P 4 *
            Nat.choose (pairColumnDegreeCount A P 6) 3))) =
      #(rowPairs (Fin 10)) +
        (∑ P ∈ rowPairs (Fin 10), pairColumnDegreeCount A P 4) +
        3 * (∑ P ∈ rowPairs (Fin 10),
          Nat.choose (pairColumnDegreeCount A P 6) 2) +
        9 * (∑ P ∈ rowPairs (Fin 10),
          pairColumnDegreeCount A P 4 *
            Nat.choose (pairColumnDegreeCount A P 6) 3) := by
    rw [sum_add_distrib, sum_add_distrib, sum_add_distrib, mul_sum, mul_sum]
    simp
  rw [hleftExpand, hrightExpand] at hidSum
  have hpairCard : #(rowPairs (Fin 10)) = 45 := by
    simp [rowPairs, card_powersetCard, Nat.choose]
  omega

/-- The profile `4·5²⁰·7` has at least three rows lying in the degree-seven
column but not the degree-four column.  Each such row consumes at least three
units of row deficit, while the complete profile has only three. -/
theorem case_four_impossible
    (A : BinaryMatrix (Fin 10) (Fin 22)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 1) (h5 : degreeCount A 5 = 20)
    (h6 : degreeCount A 6 = 0) (h7 : degreeCount A 7 = 1) : False := by
  have hinc0 := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc0
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 239 := by
    simpa using hinc0
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 240 := by
    simpa [choose_ten_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 1 := by omega
  have hrows := sum_rowDeficit A
  rw [hD] at hrows
  have hsumU := sum_rowColumnDegreeCount A 4
  have hsumB := sum_rowColumnDegreeCount A 7
  rw [h4] at hsumU
  rw [h7] at hsumB
  have hsumU' : (∑ r, rowColumnDegreeCount A r 4) = 4 := by omega
  have hsumB' : (∑ r, rowColumnDegreeCount A r 7) = 7 := by omega
  let E : Finset (Fin 10) := Finset.univ.filter fun r =>
    rowColumnDegreeCount A r 4 = 0 ∧ rowColumnDegreeCount A r 7 = 1
  have hcover : ∀ r : Fin 10,
      rowColumnDegreeCount A r 7 ≤ rowColumnDegreeCount A r 4 +
        if r ∈ E then 1 else 0 := by
    intro r
    have hu := rowColumnDegreeCount_le_degreeCount A r 4
    have hb := rowColumnDegreeCount_le_degreeCount A r 7
    rw [h4] at hu
    rw [h7] at hb
    by_cases hrE : r ∈ E
    · simp only [hrE, if_true]
      omega
    · simp only [hrE, if_false]
      simp [E] at hrE
      omega
  have hcoverSum : (∑ r, rowColumnDegreeCount A r 7) ≤
      ∑ r, (rowColumnDegreeCount A r 4 + if r ∈ E then 1 else 0) :=
    sum_le_sum fun r _ => hcover r
  have hindicator : (∑ r, if r ∈ E then 1 else 0) = #E := by
    rw [← card_filter_eq_sum_indicator]
    simp
  have hEcard : 3 ≤ #E := by
    rw [sum_add_distrib, hsumU', hsumB', hindicator] at hcoverSum
    omega
  have hinside : ∀ r ∈ E, 3 ≤ rowDeficit A r := by
    intro r hrE
    have hrtype : rowColumnDegreeCount A r 4 = 0 ∧
        rowColumnDegreeCount A r 7 = 1 := by simpa [E] using hrE
    have hformula := row_formula A hA r
    have hclasses := rowContribution_eq_degree_classes A r hdeg
    rw [hclasses] at hformula
    have h6r := rowColumnDegreeCount_le_degreeCount A r 6
    rw [h6] at h6r
    omega
  have hlower := sum_lower_on_subset (fun r : Fin 10 => rowDeficit A r)
    E 3 0 hinside (by simp)
  simp at hlower
  omega

theorem no_matrix_at_111 (A : BinaryMatrix (Fin 10) (Fin 22))
    (hA : K33Free A) (hweight : edgeCount A = 111) : False := by
  obtain ⟨⟨h0, h1, h2, h3, h8, h9, h10⟩, hprofiles⟩ :=
    profile_at_111 A hA hweight
  have hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7 := by
    intro c
    have hle := columnDegree_le_card A c
    simp at hle
    have hn0 := columnDegree_ne_of_degreeCount_eq_zero A 0 h0 c
    have hn1 := columnDegree_ne_of_degreeCount_eq_zero A 1 h1 c
    have hn2 := columnDegree_ne_of_degreeCount_eq_zero A 2 h2 c
    have hn3 := columnDegree_ne_of_degreeCount_eq_zero A 3 h3 c
    have hn8 := columnDegree_ne_of_degreeCount_eq_zero A 8 h8 c
    have hn9 := columnDegree_ne_of_degreeCount_eq_zero A 9 h9 c
    have hn10 := columnDegree_ne_of_degreeCount_eq_zero A 10 h10 c
    omega
  rcases hprofiles with hcase | hcase | hcase | hcase
  · exact case_one_impossible A hA hdeg
      hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2
  · exact case_two_impossible A hA hdeg
      hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2
  · exact case_three_impossible A hA hdeg
      hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2
  · exact case_four_impossible A hA hdeg
      hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2

/-- Every `K_{3,3}`-free `10 × 22` matrix has at most 110 ones. -/
theorem upper_bound : UpperBound 10 22 110 := by
  intro A hA
  by_contra hnot
  have hge : 111 ≤ edgeCount A := by omega
  obtain ⟨B, hBA, hBweight⟩ := exists_submatrix_of_edgeCount_le A 111 hge
  exact no_matrix_at_111 B (hA.mono hBA) hBweight

/-- The end-to-end, pure-Lean exact value `Z(10,22,3,3) = 110`. -/
theorem exact_value : Zarankiewicz.Exact 10 22 110 :=
  ⟨Zarankiewicz.Witnesses.z10_22_lower, upper_bound⟩

end Zarankiewicz.Exact.Z10_22
