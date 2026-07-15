import Zarankiewicz.Counting
import ZarankiewiczFiniteClosures.ArithmeticKernels
import Mathlib.Algebra.BigOperators.ModEq

/-!
# Pure-Lean proof of `Z(13,23,3,3) ≤ 144`
-/

namespace Zarankiewicz.Bounds.Z13_23

open scoped BigOperators
open Finset
open Zarankiewicz

abbrev penalty := ZarankiewiczFiniteClosures.z13Penalty

theorem penalty_nat_identity : ∀ d : Fin 14,
    Nat.choose d.val 3 + 70 = 15 * d.val + penalty d.val := by
  decide

theorem incidence_penalty_identity (A : BinaryMatrix (Fin 13) (Fin 23)) :
    (∑ c, Nat.choose (columnDegree A c) 3) + 70 * 23 =
      15 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
  calc
    (∑ c, Nat.choose (columnDegree A c) 3) + 70 * 23 =
        (∑ c, Nat.choose (columnDegree A c) 3) + ∑ _c : Fin 23, 70 := by simp
    _ = ∑ c, (Nat.choose (columnDegree A c) 3 + 70) := sum_add_distrib.symm
    _ = ∑ c, (15 * columnDegree A c + penalty (columnDegree A c)) := by
      apply sum_congr rfl
      intro c hc
      have hlt : columnDegree A c < 14 := by
        have hle := columnDegree_le_card A c
        simpa using Nat.lt_succ_of_le hle
      exact penalty_nat_identity ⟨columnDegree A c, hlt⟩
    _ = (∑ c, 15 * columnDegree A c) + ∑ c, penalty (columnDegree A c) :=
      sum_add_distrib
    _ = 15 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
      rw [edgeCount, mul_sum]

theorem penalty_sum_eq_histogram (A : BinaryMatrix (Fin 13) (Fin 23)) :
    (∑ c, penalty (columnDegree A c)) =
      70 * degreeCount A 0 + 55 * degreeCount A 1 + 40 * degreeCount A 2 +
        26 * degreeCount A 3 + 14 * degreeCount A 4 + 5 * degreeCount A 5 +
        6 * degreeCount A 8 + 19 * degreeCount A 9 + 40 * degreeCount A 10 +
        70 * degreeCount A 11 + 110 * degreeCount A 12 +
        161 * degreeCount A 13 := by
  have h := sum_function_mul_degreeCount A penalty
  symm
  simpa [Finset.sum_range_succ, ZarankiewiczFiniteClosures.z13Penalty,
    Nat.mul_comm, Nat.add_assoc] using h

theorem profile_data (A : BinaryMatrix (Fin 13) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 145) :
    (degreeCount A 0 = 0 ∧ degreeCount A 1 = 0 ∧ degreeCount A 2 = 0 ∧
      degreeCount A 3 = 0 ∧ degreeCount A 4 = 0 ∧ degreeCount A 9 = 0 ∧
      degreeCount A 10 = 0 ∧ degreeCount A 11 = 0 ∧ degreeCount A 12 = 0 ∧
      degreeCount A 13 = 0) ∧
    ((degreeCount A 5 = 0 ∧ degreeCount A 6 = 16 ∧ degreeCount A 7 = 7 ∧
        degreeCount A 8 = 0) ∨
      (degreeCount A 5 = 1 ∧ degreeCount A 6 = 14 ∧ degreeCount A 7 = 8 ∧
        degreeCount A 8 = 0) ∨
      (degreeCount A 5 = 0 ∧ degreeCount A 6 = 17 ∧ degreeCount A 7 = 5 ∧
        degreeCount A 8 = 1)) := by
  have hinc := sum_choose_columnDegree_le A hA
  have hchoose : Nat.choose 13 3 = 286 := by decide
  simp at hinc
  rw [hchoose] at hinc
  have hrel := incidence_penalty_identity A
  have hpenSum : (∑ c, penalty (columnDegree A c)) ≤ 7 := by omega
  have hpenalty :
      70 * degreeCount A 0 + 55 * degreeCount A 1 + 40 * degreeCount A 2 +
        26 * degreeCount A 3 + 14 * degreeCount A 4 + 5 * degreeCount A 5 +
        6 * degreeCount A 8 + 19 * degreeCount A 9 + 40 * degreeCount A 10 +
        70 * degreeCount A 11 + 110 * degreeCount A 12 +
        161 * degreeCount A 13 ≤ 7 := by
    rw [← penalty_sum_eq_histogram]
    exact hpenSum
  obtain ⟨h0, h1, h2, h3, h4, h9, h10, h11, h12, h13,
      h5le, h8le, hsmall⟩ :=
    ZarankiewiczFiniteClosures.z13_23_penalty_budget_structure
      (degreeCount A 0) (degreeCount A 1) (degreeCount A 2)
      (degreeCount A 3) (degreeCount A 4) (degreeCount A 5)
      (degreeCount A 8) (degreeCount A 9) (degreeCount A 10)
      (degreeCount A 11) (degreeCount A 12) (degreeCount A 13) hpenalty
  have hcolumnsFull := sum_degreeCount A
  have hcolumns : degreeCount A 5 + degreeCount A 6 + degreeCount A 7 +
      degreeCount A 8 = 23 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h4, h9, h10, h11, h12, h13]
      using hcolumnsFull
  have hweightFull := sum_degree_mul_degreeCount A
  rw [hweight] at hweightFull
  have hdegrees : 5 * degreeCount A 5 + 6 * degreeCount A 6 +
      7 * degreeCount A 7 + 8 * degreeCount A 8 = 145 := by
    simpa [Finset.sum_range_succ, h0, h1, h2, h3, h4, h9, h10, h11, h12, h13,
      Nat.mul_comm] using hweightFull
  have hprofiles := ZarankiewiczFiniteClosures.classify_z13_23_degree_profile
    (degreeCount A 5) (degreeCount A 6) (degreeCount A 7) (degreeCount A 8)
    hcolumns hdegrees hsmall
  exact ⟨⟨h0, h1, h2, h3, h4, h9, h10, h11, h12, h13⟩, hprofiles⟩

def contribution (A : BinaryMatrix (Fin 13) (Fin 23)) (r : Fin 13) (c : Fin 23) : Nat :=
  if A r c = true then Nat.choose (columnDegree A c - 1) 2 else 0

def rowContribution (A : BinaryMatrix (Fin 13) (Fin 23)) (r : Fin 13) : Nat :=
  ∑ c, contribution A r c

theorem row_formula (A : BinaryMatrix (Fin 13) (Fin 23)) (hA : K33Free A) (r : Fin 13) :
    rowDeficit A r + rowContribution A r = 132 := by
  simpa [rowContribution, contribution] using rowDeficit_add_sum_choose A hA r

theorem contribution_modEq_zero_of_degree_six_or_seven
    (A : BinaryMatrix (Fin 13) (Fin 23)) (r : Fin 13) (c : Fin 23)
    (hdeg : columnDegree A c = 6 ∨ columnDegree A c = 7) :
    contribution A r c ≡ 0 [MOD 5] := by
  rcases hdeg with hdeg | hdeg <;>
    by_cases hrc : A r c = true <;>
      simp [contribution, hdeg, hrc, Nat.ModEq, Nat.choose]

theorem rowContribution_modEq_zero
    (A : BinaryMatrix (Fin 13) (Fin 23)) (r : Fin 13)
    (hdeg : ∀ c, columnDegree A c = 6 ∨ columnDegree A c = 7) :
    rowContribution A r ≡ 0 [MOD 5] := by
  unfold rowContribution
  exact Nat.ModEq.sum_zero fun c _ =>
    contribution_modEq_zero_of_degree_six_or_seven A r c (hdeg c)

theorem rowContribution_modEq_exception
    (A : BinaryMatrix (Fin 13) (Fin 23)) (r : Fin 13) (e : Fin 23)
    (hdeg : ∀ c, c ≠ e → columnDegree A c = 6 ∨ columnDegree A c = 7)
    (hre : A r e ≠ true) : rowContribution A r ≡ 0 [MOD 5] := by
  unfold rowContribution
  have h := Nat.sum_modEq_ite (n := 5) (s := (Finset.univ : Finset (Fin 23)))
    (a := e) (f := fun c => contribution A r c)
    (fun c _ hce => contribution_modEq_zero_of_degree_six_or_seven A r c (hdeg c hce))
  have hezero : contribution A r e = 0 := by simp [contribution, hre]
  simpa [hezero] using h

theorem no_matrix_at_145 (A : BinaryMatrix (Fin 13) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 145) : False := by
  obtain ⟨⟨h0, h1, h2, h3, h4, h9, h10, h11, h12, h13⟩, hprofiles⟩ :=
    profile_data A hA hweight
  have hallowed : ∀ c, columnDegree A c = 5 ∨ columnDegree A c = 6 ∨
      columnDegree A c = 7 ∨ columnDegree A c = 8 := by
    intro c
    have hle := columnDegree_le_card A c
    simp at hle
    have hn0 := columnDegree_ne_of_degreeCount_eq_zero A 0 h0 c
    have hn1 := columnDegree_ne_of_degreeCount_eq_zero A 1 h1 c
    have hn2 := columnDegree_ne_of_degreeCount_eq_zero A 2 h2 c
    have hn3 := columnDegree_ne_of_degreeCount_eq_zero A 3 h3 c
    have hn4 := columnDegree_ne_of_degreeCount_eq_zero A 4 h4 c
    have hn9 := columnDegree_ne_of_degreeCount_eq_zero A 9 h9 c
    have hn10 := columnDegree_ne_of_degreeCount_eq_zero A 10 h10 c
    have hn11 := columnDegree_ne_of_degreeCount_eq_zero A 11 h11 c
    have hn12 := columnDegree_ne_of_degreeCount_eq_zero A 12 h12 c
    have hn13 := columnDegree_ne_of_degreeCount_eq_zero A 13 h13 c
    omega
  rcases hprofiles with hclean | hfive | height
  · rcases hclean with ⟨h5, h6, h7, h8⟩
    have hdeg : ∀ c, columnDegree A c = 6 ∨ columnDegree A c = 7 := by
      intro c
      have hn5 := columnDegree_ne_of_degreeCount_eq_zero A 5 h5 c
      have hn8 := columnDegree_ne_of_degreeCount_eq_zero A 8 h8 c
      rcases hallowed c with h | h | h | h <;> omega
    have hrel := incidence_penalty_identity A
    rw [penalty_sum_eq_histogram, h0, h1, h2, h3, h4, h5, h8, h9, h10, h11,
      h12, h13] at hrel
    simp at hrel
    have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 565 := by omega
    have htotal := totalDeficit_add_sum_choose A hA
    rw [hinc] at htotal
    simp at htotal
    rw [show Nat.choose 13 3 = 286 by decide] at htotal
    have hD : totalDeficit A = 7 := by omega
    have hrows := sum_rowDeficit A
    rw [hD] at hrows
    have hpoint : ∀ r : Fin 13, 2 ≤ rowDeficit A r := by
      intro r
      have hmod := rowContribution_modEq_zero A r hdeg
      change rowContribution A r % 5 = 0 % 5 at hmod
      have hformula := row_formula A hA r
      omega
    have hlower := sum_lower_on_subset (fun r : Fin 13 => rowDeficit A r)
      (∅ : Finset (Fin 13)) 0 2 (by simp) (by
        intro r hrU hrE
        exact hpoint r)
    simp at hlower
    omega
  · rcases hfive with ⟨h5, h6, h7, h8⟩
    have hfiber : #(Finset.univ.filter fun c : Fin 23 => columnDegree A c = 5) = 1 := by
      simpa [degreeCount] using h5
    obtain ⟨e, heq⟩ := card_eq_one.mp hfiber
    have hedeg : columnDegree A e = 5 := by
      have he : e ∈ Finset.univ.filter (fun c : Fin 23 => columnDegree A c = 5) := by
        rw [heq]
        simp
      exact (mem_filter.1 he).2
    have hunique : ∀ c, columnDegree A c = 5 → c = e := by
      intro c hc
      have hm : c ∈ Finset.univ.filter (fun j : Fin 23 => columnDegree A j = 5) := by
        simp [hc]
      rw [heq] at hm
      simpa using hm
    have hdeg : ∀ c, c ≠ e → columnDegree A c = 6 ∨ columnDegree A c = 7 := by
      intro c hce
      have hn5 : columnDegree A c ≠ 5 := fun hc => hce (hunique c hc)
      have hn8 := columnDegree_ne_of_degreeCount_eq_zero A 8 h8 c
      rcases hallowed c with h | h | h | h <;> omega
    have hrel := incidence_penalty_identity A
    rw [penalty_sum_eq_histogram, h0, h1, h2, h3, h4, h5, h8, h9, h10, h11,
      h12, h13] at hrel
    simp at hrel
    have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 570 := by omega
    have htotal := totalDeficit_add_sum_choose A hA
    rw [hinc] at htotal
    simp at htotal
    rw [show Nat.choose 13 3 = 286 by decide] at htotal
    have hD : totalDeficit A = 2 := by omega
    have hrows := sum_rowDeficit A
    rw [hD] at hrows
    have houtside : ∀ r ∈ (Finset.univ : Finset (Fin 13)),
        r ∉ columnSupport A e → 2 ≤ rowDeficit A r := by
      intro r hrU hr
      have hre : A r e ≠ true := by
        intro htrue
        exact hr (by simp [columnSupport, htrue])
      have hmod := rowContribution_modEq_exception A r e hdeg hre
      change rowContribution A r % 5 = 0 % 5 at hmod
      have hformula := row_formula A hA r
      omega
    have hEcard : #(columnSupport A e) = 5 := by simpa [columnDegree] using hedeg
    have hlower := sum_lower_on_subset (fun r : Fin 13 => rowDeficit A r)
      (columnSupport A e) 0 2 (by simp) houtside
    rw [hEcard] at hlower
    simp at hlower
    omega
  · rcases height with ⟨h5, h6, h7, h8⟩
    have hfiber : #(Finset.univ.filter fun c : Fin 23 => columnDegree A c = 8) = 1 := by
      simpa [degreeCount] using h8
    obtain ⟨e, heq⟩ := card_eq_one.mp hfiber
    have hedeg : columnDegree A e = 8 := by
      have he : e ∈ Finset.univ.filter (fun c : Fin 23 => columnDegree A c = 8) := by
        rw [heq]
        simp
      exact (mem_filter.1 he).2
    have hunique : ∀ c, columnDegree A c = 8 → c = e := by
      intro c hc
      have hm : c ∈ Finset.univ.filter (fun j : Fin 23 => columnDegree A j = 8) := by
        simp [hc]
      rw [heq] at hm
      simpa using hm
    have hdeg : ∀ c, c ≠ e → columnDegree A c = 6 ∨ columnDegree A c = 7 := by
      intro c hce
      have hn5 := columnDegree_ne_of_degreeCount_eq_zero A 5 h5 c
      have hn8 : columnDegree A c ≠ 8 := fun hc => hce (hunique c hc)
      rcases hallowed c with h | h | h | h <;> omega
    have hrel := incidence_penalty_identity A
    rw [penalty_sum_eq_histogram, h0, h1, h2, h3, h4, h5, h8, h9, h10, h11,
      h12, h13] at hrel
    simp at hrel
    have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 571 := by omega
    have htotal := totalDeficit_add_sum_choose A hA
    rw [hinc] at htotal
    simp at htotal
    rw [show Nat.choose 13 3 = 286 by decide] at htotal
    have hD : totalDeficit A = 1 := by omega
    have hrows := sum_rowDeficit A
    rw [hD] at hrows
    have houtside : ∀ r ∈ (Finset.univ : Finset (Fin 13)),
        r ∉ columnSupport A e → 2 ≤ rowDeficit A r := by
      intro r hrU hr
      have hre : A r e ≠ true := by
        intro htrue
        exact hr (by simp [columnSupport, htrue])
      have hmod := rowContribution_modEq_exception A r e hdeg hre
      change rowContribution A r % 5 = 0 % 5 at hmod
      have hformula := row_formula A hA r
      omega
    have hEcard : #(columnSupport A e) = 8 := by simpa [columnDegree] using hedeg
    have hlower := sum_lower_on_subset (fun r : Fin 13 => rowDeficit A r)
      (columnSupport A e) 0 2 (by simp) houtside
    rw [hEcard] at hlower
    simp at hlower
    omega

theorem upper_bound : UpperBound 13 23 144 := by
  intro A hA
  by_contra hnot
  have hge : 145 ≤ edgeCount A := by omega
  obtain ⟨B, hBA, hBweight⟩ := exists_submatrix_of_edgeCount_le A 145 hge
  exact no_matrix_at_145 B (hA.mono hBA) hBweight

end Zarankiewicz.Bounds.Z13_23
