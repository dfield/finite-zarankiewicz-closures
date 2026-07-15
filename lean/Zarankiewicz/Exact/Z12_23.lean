import Zarankiewicz.TripleIncidence
import Zarankiewicz.Witnesses
import ZarankiewiczFiniteClosures.ArithmeticKernels
import Mathlib.Tactic.NormNum
import Mathlib.Algebra.BigOperators.ModEq

/-!
# Pure-Lean proof of `Z(12,23,3,3) = 134`

The proof follows the two-stage row/pair-deficit argument in
`docs/PROOF_Z12_23.md`.  This module recomputes every finite case in Lean and
does not read the repository's JSON or Python certificates.
-/

namespace Zarankiewicz.Exact.Z12_23

open scoped BigOperators
open Finset
open Zarankiewicz

abbrev penalty := ZarankiewiczFiniteClosures.z12Penalty

private theorem choose_twelve_three : Nat.choose 12 3 = 220 := by decide

theorem penalty_nat_identity : ∀ d : Fin 13,
    Nat.choose d.val 3 + 40 = 10 * d.val + penalty d.val := by
  decide

theorem incidence_penalty_identity (A : BinaryMatrix (Fin 12) (Fin 23)) :
    (∑ c, Nat.choose (columnDegree A c) 3) + 40 * 23 =
      10 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
  calc
    (∑ c, Nat.choose (columnDegree A c) 3) + 40 * 23 =
        (∑ c, Nat.choose (columnDegree A c) 3) + ∑ _c : Fin 23, 40 := by simp
    _ = ∑ c, (Nat.choose (columnDegree A c) 3 + 40) := sum_add_distrib.symm
    _ = ∑ c, (10 * columnDegree A c + penalty (columnDegree A c)) := by
      apply sum_congr rfl
      intro c hc
      have hlt : columnDegree A c < 13 := by
        have hle := columnDegree_le_card A c
        simpa using Nat.lt_succ_of_le hle
      exact penalty_nat_identity ⟨columnDegree A c, hlt⟩
    _ = (∑ c, 10 * columnDegree A c) + ∑ c, penalty (columnDegree A c) :=
      sum_add_distrib
    _ = 10 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
      rw [edgeCount, mul_sum]

theorem penalty_sum_eq_histogram (A : BinaryMatrix (Fin 12) (Fin 23)) :
    (∑ c, penalty (columnDegree A c)) =
      40 * degreeCount A 0 + 30 * degreeCount A 1 + 20 * degreeCount A 2 +
        11 * degreeCount A 3 + 4 * degreeCount A 4 + 5 * degreeCount A 7 +
        16 * degreeCount A 8 + 34 * degreeCount A 9 + 60 * degreeCount A 10 +
        95 * degreeCount A 11 + 140 * degreeCount A 12 := by
  have h := sum_function_mul_degreeCount A penalty
  symm
  simpa [Finset.sum_range_succ, ZarankiewiczFiniteClosures.z12Penalty,
    Nat.mul_comm, Nat.add_assoc] using h

theorem profile_at_136 (A : BinaryMatrix (Fin 12) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 136) :
    (degreeCount A 0 = 0 ∧ degreeCount A 1 = 0 ∧ degreeCount A 2 = 0 ∧
      degreeCount A 3 = 0 ∧ degreeCount A 4 = 0 ∧ degreeCount A 7 = 0 ∧
      degreeCount A 8 = 0 ∧ degreeCount A 9 = 0 ∧ degreeCount A 10 = 0 ∧
      degreeCount A 11 = 0 ∧ degreeCount A 12 = 0) ∧
    degreeCount A 5 = 2 ∧ degreeCount A 6 = 21 ∧
    (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) ≤ 440 := by
    simpa [choose_twelve_three] using sum_choose_columnDegree_le A hA
  have hrel := incidence_penalty_identity A
  have hpenSum : (∑ c, penalty (columnDegree A c)) = 0 := by omega
  have hpenalty := penalty_sum_eq_histogram A
  rw [hpenSum] at hpenalty
  have h0 : degreeCount A 0 = 0 := by omega
  have h1 : degreeCount A 1 = 0 := by omega
  have h2 : degreeCount A 2 = 0 := by omega
  have h3 : degreeCount A 3 = 0 := by omega
  have h4 : degreeCount A 4 = 0 := by omega
  have h7 : degreeCount A 7 = 0 := by omega
  have h8 : degreeCount A 8 = 0 := by omega
  have h9 : degreeCount A 9 = 0 := by omega
  have h10 : degreeCount A 10 = 0 := by omega
  have h11 : degreeCount A 11 = 0 := by omega
  have h12 : degreeCount A 12 = 0 := by omega
  have hcolumnsFull := sum_degreeCount A
  have hcolumns : degreeCount A 5 + degreeCount A 6 = 23 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h4, h7, h8, h9, h10, h11,
      h12] using hcolumnsFull
  have hweightFull := sum_degree_mul_degreeCount A
  rw [hweight] at hweightFull
  have hdegrees : 5 * degreeCount A 5 + 6 * degreeCount A 6 = 136 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h4, h7, h8, h9, h10, h11,
      h12, Nat.mul_comm] using hweightFull
  have hprofile := ZarankiewiczFiniteClosures.z12_23_at_136_profile
    (degreeCount A 5) (degreeCount A 6) hcolumns hdegrees
  have hincEq : (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by omega
  exact ⟨⟨h0, h1, h2, h3, h4, h7, h8, h9, h10, h11, h12⟩,
    hprofile.1, hprofile.2, hincEq⟩

/-- Number of columns of degree `d` that contain the fixed row pair `P`. -/
def pairDegreeCount (A : BinaryMatrix (Fin 12) (Fin 23))
    (P : Finset (Fin 12)) (d : Nat) : Nat :=
  #(Finset.univ.filter fun c =>
      columnDegree A c = d ∧ P ⊆ columnSupport A c)

theorem pair_sum_of_degrees_five_six
    (A : BinaryMatrix (Fin 12) (Fin 23)) (P : Finset (Fin 12))
    (hdeg : ∀ c, columnDegree A c = 5 ∨ columnDegree A c = 6) :
    (∑ c, if P ⊆ columnSupport A c then columnDegree A c - 2 else 0) =
      3 * pairDegreeCount A P 5 + 4 * pairDegreeCount A P 6 := by
  unfold pairDegreeCount
  rw [card_filter_eq_sum_indicator, card_filter_eq_sum_indicator, mul_sum, mul_sum,
    ← sum_add_distrib]
  apply sum_congr rfl
  intro c hc
  rcases hdeg c with h5 | h6 <;>
    by_cases hPc : P ⊆ columnSupport A c <;> simp_all

theorem pairDegreeCount_le_degreeCount
    (A : BinaryMatrix (Fin 12) (Fin 23)) (P : Finset (Fin 12)) (d : Nat) :
    pairDegreeCount A P d ≤ degreeCount A d := by
  apply card_le_card
  intro c hc
  simpa [pairDegreeCount, degreeCount] using (mem_filter.1 hc).2.1

/-- The first stage of the proof: 136 ones force an impossible pair incidence. -/
theorem no_matrix_at_136 (A : BinaryMatrix (Fin 12) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 136) : False := by
  obtain ⟨⟨h0, h1, h2, h3, h4, h7, h8, h9, h10, h11, h12⟩,
      h5, h6, hinc⟩ := profile_at_136 A hA hweight
  have hdeg : ∀ c, columnDegree A c = 5 ∨ columnDegree A c = 6 := by
    intro c
    have hle := columnDegree_le_card A c
    simp at hle
    have hn0 := columnDegree_ne_of_degreeCount_eq_zero A 0 h0 c
    have hn1 := columnDegree_ne_of_degreeCount_eq_zero A 1 h1 c
    have hn2 := columnDegree_ne_of_degreeCount_eq_zero A 2 h2 c
    have hn3 := columnDegree_ne_of_degreeCount_eq_zero A 3 h3 c
    have hn4 := columnDegree_ne_of_degreeCount_eq_zero A 4 h4 c
    have hn7 := columnDegree_ne_of_degreeCount_eq_zero A 7 h7 c
    have hn8 := columnDegree_ne_of_degreeCount_eq_zero A 8 h8 c
    have hn9 := columnDegree_ne_of_degreeCount_eq_zero A 9 h9 c
    have hn10 := columnDegree_ne_of_degreeCount_eq_zero A 10 h10 c
    have hn11 := columnDegree_ne_of_degreeCount_eq_zero A 11 h11 c
    have hn12 := columnDegree_ne_of_degreeCount_eq_zero A 12 h12 c
    omega
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by
    simpa [choose_twelve_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 0 := by omega
  have hpairs := sum_pairDeficit A
  rw [hD] at hpairs
  have hpairZero : ∀ P ∈ rowPairs (Fin 12), pairDeficit A P = 0 := by
    intro P hP
    have hle : pairDeficit A P ≤ ∑ Q ∈ rowPairs (Fin 12), pairDeficit A Q := by
      exact single_le_sum (fun _ _ => Nat.zero_le _) hP
    rw [hpairs] at hle
    omega
  have hfiveFiber : #(Finset.univ.filter fun c : Fin 23 => columnDegree A c = 5) = 2 := by
    simpa [degreeCount] using h5
  have hfiberNonempty :
      (Finset.univ.filter fun c : Fin 23 => columnDegree A c = 5).Nonempty := by
    rw [Finset.nonempty_iff_ne_empty]
    intro hempty
    rw [hempty] at hfiveFiber
    simp at hfiveFiber
  obtain ⟨e, he⟩ := hfiberNonempty
  have hedeg : columnDegree A e = 5 := (mem_filter.1 he).2
  have hsupport : #(columnSupport A e) = 5 := by simpa [columnDegree] using hedeg
  obtain ⟨P, hPmem⟩ :=
    (powersetCard_nonempty.2 (show 2 ≤ #(columnSupport A e) by omega))
  have ⟨hPsub, hPcard⟩ := mem_powersetCard.1 hPmem
  have hP : P ∈ rowPairs (Fin 12) := by
    simp [rowPairs, hPcard]
  have hformula := pairDeficit_add_sum_sub_two A hA P hP
  rw [hpairZero P hP] at hformula
  have hsum := pair_sum_of_degrees_five_six A P hdeg
  rw [hsum] at hformula
  norm_num at hformula
  have hxle : pairDegreeCount A P 5 ≤ 2 := by
    rw [← h5]
    exact pairDegreeCount_le_degreeCount A P 5
  have hxzero : pairDegreeCount A P 5 = 0 := by omega
  have hecount : e ∈ Finset.univ.filter fun c : Fin 23 =>
      columnDegree A c = 5 ∧ P ⊆ columnSupport A c := by
    simp [hedeg, hPsub]
  have hxpos : 0 < pairDegreeCount A P 5 := by
    unfold pairDegreeCount
    exact card_pos.mpr ⟨e, hecount⟩
  omega

/-! ## The 135-one boundary -/

theorem profile_at_135 (A : BinaryMatrix (Fin 12) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 135) :
    (degreeCount A 0 = 0 ∧ degreeCount A 1 = 0 ∧ degreeCount A 2 = 0 ∧
      degreeCount A 3 = 0 ∧ degreeCount A 8 = 0 ∧ degreeCount A 9 = 0 ∧
      degreeCount A 10 = 0 ∧ degreeCount A 11 = 0 ∧ degreeCount A 12 = 0) ∧
    ((degreeCount A 4 = 0 ∧ degreeCount A 5 = 3 ∧ degreeCount A 6 = 20 ∧
        degreeCount A 7 = 0) ∨
      (degreeCount A 4 = 1 ∧ degreeCount A 5 = 1 ∧ degreeCount A 6 = 21 ∧
        degreeCount A 7 = 0) ∨
      (degreeCount A 4 = 0 ∧ degreeCount A 5 = 4 ∧ degreeCount A 6 = 18 ∧
        degreeCount A 7 = 1) ∨
      (degreeCount A 4 = 1 ∧ degreeCount A 5 = 2 ∧ degreeCount A 6 = 19 ∧
        degreeCount A 7 = 1) ∨
      (degreeCount A 4 = 0 ∧ degreeCount A 5 = 5 ∧ degreeCount A 6 = 16 ∧
        degreeCount A 7 = 2)) := by
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) ≤ 440 := by
    simpa [choose_twelve_three] using sum_choose_columnDegree_le A hA
  have hrel := incidence_penalty_identity A
  have hpenSum : (∑ c, penalty (columnDegree A c)) ≤ 10 := by omega
  have hpenalty :
      40 * degreeCount A 0 + 30 * degreeCount A 1 + 20 * degreeCount A 2 +
        11 * degreeCount A 3 + 4 * degreeCount A 4 + 5 * degreeCount A 7 +
        16 * degreeCount A 8 + 34 * degreeCount A 9 + 60 * degreeCount A 10 +
        95 * degreeCount A 11 + 140 * degreeCount A 12 ≤ 10 := by
    rw [← penalty_sum_eq_histogram]
    exact hpenSum
  obtain ⟨h0, h1, h2, h3, h8, h9, h10, h11, h12, h4le, h7le, hsmall⟩ :=
    ZarankiewiczFiniteClosures.z12_23_penalty_budget_structure
      (degreeCount A 0) (degreeCount A 1) (degreeCount A 2)
      (degreeCount A 3) (degreeCount A 4) (degreeCount A 7)
      (degreeCount A 8) (degreeCount A 9) (degreeCount A 10)
      (degreeCount A 11) (degreeCount A 12) hpenalty
  have hcolumnsFull := sum_degreeCount A
  have hcolumns : degreeCount A 4 + degreeCount A 5 + degreeCount A 6 +
      degreeCount A 7 = 23 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h8, h9, h10, h11, h12]
      using hcolumnsFull
  have hweightFull := sum_degree_mul_degreeCount A
  rw [hweight] at hweightFull
  have hdegrees : 4 * degreeCount A 4 + 5 * degreeCount A 5 +
      6 * degreeCount A 6 + 7 * degreeCount A 7 = 135 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h8, h9, h10, h11, h12,
      Nat.mul_comm] using hweightFull
  have hprofiles := ZarankiewiczFiniteClosures.classify_z12_23_degree_profile
    (degreeCount A 4) (degreeCount A 5) (degreeCount A 6) (degreeCount A 7)
    hcolumns hdegrees hsmall
  exact ⟨⟨h0, h1, h2, h3, h8, h9, h10, h11, h12⟩, hprofiles⟩

def contribution (A : BinaryMatrix (Fin 12) (Fin 23))
    (r : Fin 12) (c : Fin 23) : Nat :=
  if A r c = true then Nat.choose (columnDegree A c - 1) 2 else 0

def rowContribution (A : BinaryMatrix (Fin 12) (Fin 23)) (r : Fin 12) : Nat :=
  ∑ c, contribution A r c

theorem row_formula (A : BinaryMatrix (Fin 12) (Fin 23))
    (hA : K33Free A) (r : Fin 12) :
    rowDeficit A r + rowContribution A r = 110 := by
  simpa [rowContribution, contribution] using rowDeficit_add_sum_choose A hA r

theorem rowContribution_eq_degree_classes
    (A : BinaryMatrix (Fin 12) (Fin 23)) (r : Fin 12)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7) :
    rowContribution A r =
      3 * rowColumnDegreeCount A r 4 + 6 * rowColumnDegreeCount A r 5 +
        10 * rowColumnDegreeCount A r 6 + 15 * rowColumnDegreeCount A r 7 := by
  have hpoint : ∀ c : Fin 23,
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
      (∑ c : Fin 23, if columnDegree A c = d ∧ A r c = true then k else 0) =
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
    (A : BinaryMatrix (Fin 12) (Fin 23)) (P : Finset (Fin 12))
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7) :
    (∑ c, if P ⊆ columnSupport A c then columnDegree A c - 2 else 0) =
      2 * pairColumnDegreeCount A P 4 + 3 * pairColumnDegreeCount A P 5 +
        4 * pairColumnDegreeCount A P 6 + 5 * pairColumnDegreeCount A P 7 := by
  have hpoint : ∀ c : Fin 23,
      (if P ⊆ columnSupport A c then columnDegree A c - 2 else 0) =
        (if columnDegree A c = 4 ∧ P ⊆ columnSupport A c then 2 else 0) +
        (if columnDegree A c = 5 ∧ P ⊆ columnSupport A c then 3 else 0) +
        (if columnDegree A c = 6 ∧ P ⊆ columnSupport A c then 4 else 0) +
        (if columnDegree A c = 7 ∧ P ⊆ columnSupport A c then 5 else 0) := by
    intro c
    rcases hdeg c with h4 | h5 | h6 | h7 <;>
      by_cases hPc : P ⊆ columnSupport A c <;> simp_all
  have hclass : ∀ d k : Nat,
      (∑ c : Fin 23,
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

/-- Encode the row type `(number of degree-five columns, membership count in
degree-seven columns)` as `2a+b`. -/
def rowTypeCode (A : BinaryMatrix (Fin 12) (Fin 23)) (r : Fin 12) : Nat :=
  2 * rowColumnDegreeCount A r 5 + rowColumnDegreeCount A r 7

def rowTypeCount (A : BinaryMatrix (Fin 12) (Fin 23)) (k : Nat) : Nat :=
  #(Finset.univ.filter fun r => rowTypeCode A r = k)

theorem sum_function_mul_rowTypeCount
    (A : BinaryMatrix (Fin 12) (Fin 23))
    (hfive : degreeCount A 5 ≤ 4) (hseven : degreeCount A 7 ≤ 1)
    (f : Nat → Nat) :
    (∑ k ∈ range 10, f k * rowTypeCount A k) =
      ∑ r, f (rowTypeCode A r) := by
  have hmap : ∀ r ∈ (Finset.univ : Finset (Fin 12)), rowTypeCode A r ∈ range 10 := by
    intro r hr
    simp only [mem_range]
    have ha := rowColumnDegreeCount_le_degreeCount A r 5
    have hb := rowColumnDegreeCount_le_degreeCount A r 7
    unfold rowTypeCode
    omega
  calc
    (∑ k ∈ range 10, f k * rowTypeCount A k) =
        ∑ k ∈ range 10,
          ∑ r ∈ Finset.univ with rowTypeCode A r = k, f k := by
            apply sum_congr rfl
            intro k hk
            unfold rowTypeCount
            rw [sum_const_nat (m := f k) (fun _ _ => rfl), Nat.mul_comm]
    _ = ∑ r ∈ Finset.univ, f (rowTypeCode A r) := by
          exact sum_fiberwise_of_maps_to' hmap f
    _ = ∑ r, f (rowTypeCode A r) := rfl

/-- The sole finite arithmetic kernel in the 135-one proof.  The ten
variables are multiplicities of the row types `(a,b)` with `0 ≤ a ≤ 4` and
`0 ≤ b ≤ 1`. -/
theorem case_three_row_type_minimum
    (n00 n10 n20 n30 n40 n01 n11 n21 n31 n41 : Nat)
    (hrows : n00 + n10 + n20 + n30 + n40 + n01 + n11 + n21 + n31 + n41 = 12)
    (hfive : n10 + 2*n20 + 3*n30 + 4*n40 +
      n11 + 2*n21 + 3*n31 + 4*n41 = 20)
    (hseven : n01 + n11 + n21 + n31 + n41 = 7)
    (htriple : n30 + 4*n40 + n31 + 4*n41 ≤ 8)
    (hmixed : n21 + 3*n31 + 6*n41 ≤ 12) :
    25 ≤ 4*n10 + 8*n20 + 2*n30 + 6*n40 +
      5*n01 + 9*n11 + 3*n21 + 7*n31 + n41 := by
  omega

theorem choose_sum_eq_degree_classes
    (A : BinaryMatrix (Fin 12) (Fin 23))
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7) :
    (∑ c, Nat.choose (columnDegree A c) 3) =
      4 * degreeCount A 4 + 10 * degreeCount A 5 +
        20 * degreeCount A 6 + 35 * degreeCount A 7 := by
  have hpoint : ∀ c : Fin 23,
      Nat.choose (columnDegree A c) 3 =
        (if columnDegree A c = 4 then 4 else 0) +
        (if columnDegree A c = 5 then 10 else 0) +
        (if columnDegree A c = 6 then 20 else 0) +
        (if columnDegree A c = 7 then 35 else 0) := by
    intro c
    rcases hdeg c with h4 | h5 | h6 | h7 <;>
      simp_all [Nat.choose]
  have hclass : ∀ d k : Nat,
      (∑ c : Fin 23, if columnDegree A c = d then k else 0) =
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

set_option maxHeartbeats 800000 in
theorem case_one_impossible
    (A : BinaryMatrix (Fin 12) (Fin 23)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 0) (h5 : degreeCount A 5 = 3)
    (h6 : degreeCount A 6 = 20) (h7 : degreeCount A 7 = 0) : False := by
  have hinc := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc
  norm_num at hinc
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by
    simpa [choose_twelve_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 10 := by omega
  have hrows := sum_rowDeficit A
  rw [hD] at hrows
  have hsumA := sum_rowColumnDegreeCount A 5
  rw [h5] at hsumA
  have hsumA' : (∑ r, rowColumnDegreeCount A r 5) = 15 := by omega
  have htriple := sum_choose_rowColumnDegreeCount_le A hA 5
  rw [h5] at htriple
  norm_num [Nat.choose] at htriple
  let N3 : Nat := #((Finset.univ : Finset (Fin 12)).filter fun r =>
    rowColumnDegreeCount A r 5 = 3)
  have hN3eq : N3 = ∑ r, Nat.choose (rowColumnDegreeCount A r 5) 3 := by
    unfold N3
    rw [card_filter_eq_sum_indicator]
    apply sum_congr rfl
    intro r hr
    have ha := rowColumnDegreeCount_le_degreeCount A r 5
    rw [h5] at ha
    have hcases : rowColumnDegreeCount A r 5 = 0 ∨
        rowColumnDegreeCount A r 5 = 1 ∨
        rowColumnDegreeCount A r 5 = 2 ∨
        rowColumnDegreeCount A r 5 = 3 := by omega
    rcases hcases with h | h | h | h <;> simp [h, Nat.choose]
  have hN3 : N3 ≤ 2 := by omega
  have hresIdentity :
      4 * (∑ r, rowColumnDegreeCount A r 5) =
        (∑ r, (4 * rowColumnDegreeCount A r 5) % 10) + 10 * N3 := by
    calc
      4 * (∑ r, rowColumnDegreeCount A r 5) =
          ∑ r, 4 * rowColumnDegreeCount A r 5 := by rw [mul_sum]
      _ = ∑ r,
          ((4 * rowColumnDegreeCount A r 5) % 10 +
            10 * if rowColumnDegreeCount A r 5 = 3 then 1 else 0) := by
            apply sum_congr rfl
            intro r hr
            have ha := rowColumnDegreeCount_le_degreeCount A r 5
            rw [h5] at ha
            by_cases hthree : rowColumnDegreeCount A r 5 = 3
            · simp [hthree]
            · have hcases : rowColumnDegreeCount A r 5 = 0 ∨
                  rowColumnDegreeCount A r 5 = 1 ∨
                  rowColumnDegreeCount A r 5 = 2 := by omega
              rcases hcases with h | h | h <;> simp [h, hthree]
      _ = (∑ r, (4 * rowColumnDegreeCount A r 5) % 10) + 10 * N3 := by
            rw [sum_add_distrib]
            have hindicator :
                (∑ r, 10 * if rowColumnDegreeCount A r 5 = 3 then 1 else 0) =
                  10 * N3 := by
              unfold N3
              rw [card_filter_eq_sum_indicator, mul_sum]
            rw [hindicator]
  have hresLower : 40 ≤ ∑ r, (4 * rowColumnDegreeCount A r 5) % 10 := by
    omega
  have hpoint : ∀ r : Fin 12,
      (4 * rowColumnDegreeCount A r 5) % 10 ≤ rowDeficit A r := by
    intro r
    have hformula := row_formula A hA r
    have hclasses := rowContribution_eq_degree_classes A r hdeg
    rw [hclasses] at hformula
    have h4r := rowColumnDegreeCount_le_degreeCount A r 4
    have h7r := rowColumnDegreeCount_le_degreeCount A r 7
    rw [h4] at h4r
    rw [h7] at h7r
    omega
  have hresUpper : (∑ r, (4 * rowColumnDegreeCount A r 5) % 10) ≤
      ∑ r, rowDeficit A r := sum_le_sum fun r _ => hpoint r
  omega

theorem case_two_impossible
    (A : BinaryMatrix (Fin 12) (Fin 23)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 1) (h5 : degreeCount A 5 = 1)
    (h6 : degreeCount A 6 = 21) (h7 : degreeCount A 7 = 0) : False := by
  have hinc := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc
  norm_num at hinc
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by
    simpa [choose_twelve_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 6 := by omega
  have hpairs := sum_pairDeficit A
  rw [hD] at hpairs
  have hpoint : ∀ P ∈ rowPairs (Fin 12),
      2 * pairColumnDegreeCount A P 4 + pairColumnDegreeCount A P 5 ≤
        pairDeficit A P := by
    intro P hP
    have hformula := pairDeficit_add_sum_sub_two A hA P hP
    have hclasses := pairUsed_eq_degree_classes A P hdeg
    rw [hclasses] at hformula
    norm_num at hformula
    have h4P := pairColumnDegreeCount_le_degreeCount A P 4
    have h5P := pairColumnDegreeCount_le_degreeCount A P 5
    have h7P := pairColumnDegreeCount_le_degreeCount A P 7
    rw [h4] at h4P
    rw [h5] at h5P
    rw [h7] at h7P
    omega
  have hsum4 := sum_pairColumnDegreeCount A 4
  have hsum5 := sum_pairColumnDegreeCount A 5
  rw [h4] at hsum4
  rw [h5] at hsum5
  norm_num [Nat.choose] at hsum4 hsum5
  have hleft :
      (∑ P ∈ rowPairs (Fin 12),
        (2 * pairColumnDegreeCount A P 4 + pairColumnDegreeCount A P 5)) = 22 := by
    calc
      (∑ P ∈ rowPairs (Fin 12),
          (2 * pairColumnDegreeCount A P 4 + pairColumnDegreeCount A P 5)) =
          2 * (∑ P ∈ rowPairs (Fin 12), pairColumnDegreeCount A P 4) +
            (∑ P ∈ rowPairs (Fin 12), pairColumnDegreeCount A P 5) := by
              rw [sum_add_distrib, ← mul_sum]
      _ = 22 := by omega
  have hlower :
      (∑ P ∈ rowPairs (Fin 12),
        (2 * pairColumnDegreeCount A P 4 + pairColumnDegreeCount A P 5)) ≤
        ∑ P ∈ rowPairs (Fin 12), pairDeficit A P :=
    sum_le_sum hpoint
  omega

theorem case_three_impossible
    (A : BinaryMatrix (Fin 12) (Fin 23)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 0) (h5 : degreeCount A 5 = 4)
    (h6 : degreeCount A 6 = 18) (h7 : degreeCount A 7 = 1) : False := by
  have hinc := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc
  norm_num at hinc
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by
    simpa [choose_twelve_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 5 := by omega
  have hrows := sum_rowDeficit A
  rw [hD] at hrows
  have hsumA := sum_rowColumnDegreeCount A 5
  have hsumB := sum_rowColumnDegreeCount A 7
  rw [h5] at hsumA
  rw [h7] at hsumB
  have hsumA' : (∑ r, rowColumnDegreeCount A r 5) = 20 := by omega
  have hsumB' : (∑ r, rowColumnDegreeCount A r 7) = 7 := by omega
  have htriple := sum_choose_rowColumnDegreeCount_le A hA 5
  rw [h5] at htriple
  norm_num [Nat.choose] at htriple
  have hmixed := sum_choose_two_mul_rowColumnDegreeCount_le A hA 5 7 (by decide)
  rw [h5, h7] at hmixed
  norm_num [Nat.choose] at hmixed
  have hcodeFive : ∀ r : Fin 12,
      rowTypeCode A r / 2 = rowColumnDegreeCount A r 5 := by
    intro r
    have hb := rowColumnDegreeCount_le_degreeCount A r 7
    rw [h7] at hb
    unfold rowTypeCode
    omega
  have hcodeSeven : ∀ r : Fin 12,
      rowTypeCode A r % 2 = rowColumnDegreeCount A r 7 := by
    intro r
    have hb := rowColumnDegreeCount_le_degreeCount A r 7
    rw [h7] at hb
    unfold rowTypeCode
    omega
  have hhistRows := sum_function_mul_rowTypeCount A (by omega) (by omega)
    (fun _ => 1)
  have hrowsRaw :
      rowTypeCount A 0 + rowTypeCount A 1 + rowTypeCount A 2 +
      rowTypeCount A 3 + rowTypeCount A 4 + rowTypeCount A 5 +
      rowTypeCount A 6 + rowTypeCount A 7 + rowTypeCount A 8 +
      rowTypeCount A 9 = 12 := by
    simpa [Finset.sum_range_succ] using hhistRows
  have hhistFive := sum_function_mul_rowTypeCount A (by omega) (by omega)
    (fun k => k / 2)
  simp_rw [hcodeFive] at hhistFive
  rw [hsumA'] at hhistFive
  have hfiveRaw :
      rowTypeCount A 2 + rowTypeCount A 3 +
      2 * rowTypeCount A 4 + 2 * rowTypeCount A 5 +
      3 * rowTypeCount A 6 + 3 * rowTypeCount A 7 +
      4 * rowTypeCount A 8 + 4 * rowTypeCount A 9 = 20 := by
    simpa [Finset.sum_range_succ, Nat.mul_comm, Nat.add_assoc] using hhistFive
  have hhistSeven := sum_function_mul_rowTypeCount A (by omega) (by omega)
    (fun k => k % 2)
  simp_rw [hcodeSeven] at hhistSeven
  rw [hsumB'] at hhistSeven
  have hsevenRaw : rowTypeCount A 1 + rowTypeCount A 3 +
      rowTypeCount A 5 + rowTypeCount A 7 + rowTypeCount A 9 = 7 := by
    simpa [Finset.sum_range_succ, Nat.mul_comm, Nat.add_assoc] using hhistSeven
  have hhistTriple := sum_function_mul_rowTypeCount A (by omega) (by omega)
    (fun k => Nat.choose (k / 2) 3)
  simp_rw [hcodeFive] at hhistTriple
  have htripleRaw : rowTypeCount A 6 + 4 * rowTypeCount A 8 +
      rowTypeCount A 7 + 4 * rowTypeCount A 9 ≤ 8 := by
    have hcalc :
        rowTypeCount A 6 + 4 * rowTypeCount A 8 +
          rowTypeCount A 7 + 4 * rowTypeCount A 9 =
          ∑ r, Nat.choose (rowColumnDegreeCount A r 5) 3 := by
      have h := hhistTriple
      simp [Finset.sum_range_succ, Nat.choose, Nat.mul_comm, Nat.add_assoc] at h
      omega
    omega
  have hhistMixed := sum_function_mul_rowTypeCount A (by omega) (by omega)
    (fun k => Nat.choose (k / 2) 2 * (k % 2))
  simp_rw [hcodeFive, hcodeSeven] at hhistMixed
  have hmixedRaw : rowTypeCount A 5 + 3 * rowTypeCount A 7 +
      6 * rowTypeCount A 9 ≤ 12 := by
    have hcalc : rowTypeCount A 5 + 3 * rowTypeCount A 7 +
        6 * rowTypeCount A 9 =
        ∑ r, Nat.choose (rowColumnDegreeCount A r 5) 2 *
          rowColumnDegreeCount A r 7 := by
      simpa [Finset.sum_range_succ, Nat.choose, Nat.mul_comm, Nat.add_assoc]
        using hhistMixed
    omega
  have hminimum := case_three_row_type_minimum
    (rowTypeCount A 0) (rowTypeCount A 2) (rowTypeCount A 4)
    (rowTypeCount A 6) (rowTypeCount A 8) (rowTypeCount A 1)
    (rowTypeCount A 3) (rowTypeCount A 5) (rowTypeCount A 7)
    (rowTypeCount A 9) (by omega) (by omega) (by omega) (by omega) (by omega)
  have hhistResidue := sum_function_mul_rowTypeCount A (by omega) (by omega)
    (fun k => (4 * (k / 2) + 5 * (k % 2)) % 10)
  simp_rw [hcodeFive, hcodeSeven] at hhistResidue
  have hresLower : 25 ≤ ∑ r,
      (4 * rowColumnDegreeCount A r 5 +
        5 * rowColumnDegreeCount A r 7) % 10 := by
    have hcalc :
        4 * rowTypeCount A 2 + 8 * rowTypeCount A 4 +
          2 * rowTypeCount A 6 + 6 * rowTypeCount A 8 +
          5 * rowTypeCount A 1 + 9 * rowTypeCount A 3 +
          3 * rowTypeCount A 5 + 7 * rowTypeCount A 7 +
          rowTypeCount A 9 =
          ∑ r, (4 * rowColumnDegreeCount A r 5 +
            5 * rowColumnDegreeCount A r 7) % 10 := by
      have h := hhistResidue
      simp [Finset.sum_range_succ, Nat.mul_comm, Nat.add_assoc] at h
      omega
    omega
  have hpoint : ∀ r : Fin 12,
      (4 * rowColumnDegreeCount A r 5 +
        5 * rowColumnDegreeCount A r 7) % 10 ≤ rowDeficit A r := by
    intro r
    have hformula := row_formula A hA r
    have hclasses := rowContribution_eq_degree_classes A r hdeg
    rw [hclasses] at hformula
    have h4r := rowColumnDegreeCount_le_degreeCount A r 4
    rw [h4] at h4r
    omega
  have hresUpper : (∑ r,
      (4 * rowColumnDegreeCount A r 5 +
        5 * rowColumnDegreeCount A r 7) % 10) ≤
      ∑ r, rowDeficit A r := sum_le_sum fun r _ => hpoint r
  omega

theorem case_four_impossible
    (A : BinaryMatrix (Fin 12) (Fin 23)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 1) (h5 : degreeCount A 5 = 2)
    (h6 : degreeCount A 6 = 19) (h7 : degreeCount A 7 = 1) : False := by
  have hinc := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc
  norm_num at hinc
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by
    simpa [choose_twelve_three] using totalDeficit_add_sum_choose A hA
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
  let E : Finset (Fin 12) := Finset.univ.filter fun r =>
    rowColumnDegreeCount A r 4 = 0 ∧ rowColumnDegreeCount A r 7 = 1
  have hcover : ∀ r : Fin 12,
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
    have ha := rowColumnDegreeCount_le_degreeCount A r 5
    rw [h5] at ha
    have hformula := row_formula A hA r
    have hclasses := rowContribution_eq_degree_classes A r hdeg
    rw [hclasses] at hformula
    omega
  have hlower := sum_lower_on_subset (fun r : Fin 12 => rowDeficit A r)
    E 3 0 hinside (by simp)
  norm_num at hlower
  omega

theorem case_five_impossible
    (A : BinaryMatrix (Fin 12) (Fin 23)) (hA : K33Free A)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 ∨
      columnDegree A c = 6 ∨ columnDegree A c = 7)
    (h4 : degreeCount A 4 = 0) (h5 : degreeCount A 5 = 5)
    (h6 : degreeCount A 6 = 16) (h7 : degreeCount A 7 = 2) : False := by
  have hinc := choose_sum_eq_degree_classes A hdeg
  rw [h4, h5, h6, h7] at hinc
  norm_num at hinc
  have htotal : totalDeficit A +
      (∑ c, Nat.choose (columnDegree A c) 3) = 440 := by
    simpa [choose_twelve_three] using totalDeficit_add_sum_choose A hA
  rw [hinc] at htotal
  have hD : totalDeficit A = 0 := by omega
  have hrows := sum_rowDeficit A
  rw [hD] at hrows
  have hrowZero : ∀ r : Fin 12, rowDeficit A r = 0 := by
    intro r
    have hle : rowDeficit A r ≤ ∑ q, rowDeficit A q :=
      single_le_sum (fun _ _ => Nat.zero_le _) (mem_univ r)
    omega
  have htypes : ∀ r : Fin 12,
      rowColumnDegreeCount A r 5 = 0 ∨ rowColumnDegreeCount A r 5 = 5 := by
    intro r
    have hformula := row_formula A hA r
    have hclasses := rowContribution_eq_degree_classes A r hdeg
    rw [hclasses, hrowZero r] at hformula
    have h4r := rowColumnDegreeCount_le_degreeCount A r 4
    have h5r := rowColumnDegreeCount_le_degreeCount A r 5
    have h7r := rowColumnDegreeCount_le_degreeCount A r 7
    rw [h4] at h4r
    rw [h5] at h5r
    rw [h7] at h7r
    omega
  have hsumA := sum_rowColumnDegreeCount A 5
  rw [h5] at hsumA
  have hsumA' : (∑ r, rowColumnDegreeCount A r 5) = 25 := by omega
  have hchooseEq : (∑ r, Nat.choose (rowColumnDegreeCount A r 5) 3) = 50 := by
    calc
      (∑ r, Nat.choose (rowColumnDegreeCount A r 5) 3) =
          ∑ r, 2 * rowColumnDegreeCount A r 5 := by
            apply sum_congr rfl
            intro r hr
            rcases htypes r with h | h <;> simp [h, Nat.choose]
      _ = 2 * ∑ r, rowColumnDegreeCount A r 5 := by rw [mul_sum]
      _ = 50 := by omega
  have htriple := sum_choose_rowColumnDegreeCount_le A hA 5
  rw [h5, hchooseEq] at htriple
  norm_num [Nat.choose] at htriple

theorem no_matrix_at_135 (A : BinaryMatrix (Fin 12) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 135) : False := by
  obtain ⟨⟨h0, h1, h2, h3, h8, h9, h10, h11, h12⟩, hprofiles⟩ :=
    profile_at_135 A hA hweight
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
    have hn11 := columnDegree_ne_of_degreeCount_eq_zero A 11 h11 c
    have hn12 := columnDegree_ne_of_degreeCount_eq_zero A 12 h12 c
    omega
  rcases hprofiles with hcase | hcase | hcase | hcase | hcase
  · exact case_one_impossible A hA hdeg hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2
  · exact case_two_impossible A hA hdeg hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2
  · exact case_three_impossible A hA hdeg hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2
  · exact case_four_impossible A hA hdeg hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2
  · exact case_five_impossible A hA hdeg hcase.1 hcase.2.1 hcase.2.2.1 hcase.2.2.2

theorem upper_bound : UpperBound 12 23 134 := by
  intro A hA
  by_contra hnot
  have hge : 135 ≤ edgeCount A := by omega
  obtain ⟨B, hBA, hBweight⟩ := exists_submatrix_of_edgeCount_le A 135 hge
  exact no_matrix_at_135 B (hA.mono hBA) hBweight

/-- The end-to-end, kernel-checked exact value. -/
theorem exact_value : Zarankiewicz.Exact 12 23 134 :=
  ⟨Zarankiewicz.Witnesses.z12_23_lower, upper_bound⟩

end Zarankiewicz.Exact.Z12_23
