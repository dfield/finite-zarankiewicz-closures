import Zarankiewicz.Counting
import Zarankiewicz.Witnesses
import ZarankiewiczZ923.ArithmeticKernel
import Mathlib.Algebra.BigOperators.ModEq

/-!
# Pure-Lean proof of `Z(9,23,3,3) = 103`

This module supplies the combinatorial bridge absent from the earlier
arithmetic-only kernel.  The only concrete computation is the embedded
103-one lower-bound matrix in `Zarankiewicz.Witnesses`.
-/

namespace Zarankiewicz.Exact.Z9_23

open scoped BigOperators
open Finset
open Zarankiewicz

abbrev penalty := ZarankiewiczZ923.penalty

theorem penalty_nat_identity : ∀ d : Fin 10,
    Nat.choose d.val 3 + 20 = 6 * d.val + penalty d.val := by
  decide

theorem incidence_penalty_identity (A : BinaryMatrix (Fin 9) (Fin 23)) :
    (∑ c, Nat.choose (columnDegree A c) 3) + 20 * 23 =
      6 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
  calc
    (∑ c, Nat.choose (columnDegree A c) 3) + 20 * 23 =
        (∑ c, Nat.choose (columnDegree A c) 3) + ∑ _c : Fin 23, 20 := by simp
    _ = ∑ c, (Nat.choose (columnDegree A c) 3 + 20) :=
      sum_add_distrib.symm
    _ = ∑ c, (6 * columnDegree A c + penalty (columnDegree A c)) := by
      apply sum_congr rfl
      intro c hc
      have hlt : columnDegree A c < 10 := by
        have hle := columnDegree_le_card A c
        simpa using Nat.lt_succ_of_le hle
      exact penalty_nat_identity ⟨columnDegree A c, hlt⟩
    _ = (∑ c, 6 * columnDegree A c) + ∑ c, penalty (columnDegree A c) :=
      sum_add_distrib
    _ = 6 * edgeCount A + ∑ c, penalty (columnDegree A c) := by
      rw [edgeCount, mul_sum]

theorem penalty_sum_eq_histogram (A : BinaryMatrix (Fin 9) (Fin 23)) :
    (∑ c, penalty (columnDegree A c)) =
      20 * degreeCount A 0 + 14 * degreeCount A 1 + 8 * degreeCount A 2 +
        3 * degreeCount A 3 + 4 * degreeCount A 6 + 13 * degreeCount A 7 +
        28 * degreeCount A 8 + 50 * degreeCount A 9 := by
  have h := sum_function_mul_degreeCount A penalty
  symm
  simpa [Finset.sum_range_succ, ZarankiewiczZ923.penalty, Nat.mul_comm,
    Nat.add_assoc] using h

theorem degree_profile_of_104 (A : BinaryMatrix (Fin 9) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 104) :
    (degreeCount A 0 = 0 ∧ degreeCount A 1 = 0 ∧ degreeCount A 2 = 0 ∧
      degreeCount A 3 = 0 ∧ degreeCount A 4 = 11 ∧ degreeCount A 5 = 12 ∧
      degreeCount A 6 = 0 ∧ degreeCount A 7 = 0 ∧ degreeCount A 8 = 0 ∧
      degreeCount A 9 = 0) ∨
    (degreeCount A 0 = 0 ∧ degreeCount A 1 = 0 ∧ degreeCount A 2 = 0 ∧
      degreeCount A 3 = 1 ∧ degreeCount A 4 = 9 ∧ degreeCount A 5 = 13 ∧
      degreeCount A 6 = 0 ∧ degreeCount A 7 = 0 ∧ degreeCount A 8 = 0 ∧
      degreeCount A 9 = 0) ∨
    (degreeCount A 0 = 0 ∧ degreeCount A 1 = 0 ∧ degreeCount A 2 = 0 ∧
      degreeCount A 3 = 0 ∧ degreeCount A 4 = 12 ∧ degreeCount A 5 = 10 ∧
      degreeCount A 6 = 1 ∧ degreeCount A 7 = 0 ∧ degreeCount A 8 = 0 ∧
      degreeCount A 9 = 0) := by
  have hinc : (∑ c, Nat.choose (columnDegree A c) 3) ≤ 168 := by
    simpa using sum_choose_columnDegree_le A hA
  have hrel := incidence_penalty_identity A
  have hpenSum : (∑ c, penalty (columnDegree A c)) ≤ 4 := by
    omega
  have hcolumns :
      degreeCount A 0 + degreeCount A 1 + degreeCount A 2 + degreeCount A 3 +
        degreeCount A 4 + degreeCount A 5 + degreeCount A 6 + degreeCount A 7 +
        degreeCount A 8 + degreeCount A 9 = 23 := by
    simpa [Finset.sum_range_succ] using sum_degreeCount A
  have hdegrees :
      degreeCount A 1 + 2 * degreeCount A 2 + 3 * degreeCount A 3 +
        4 * degreeCount A 4 + 5 * degreeCount A 5 + 6 * degreeCount A 6 +
        7 * degreeCount A 7 + 8 * degreeCount A 8 + 9 * degreeCount A 9 = 104 := by
    have h := sum_degree_mul_degreeCount A
    rw [hweight] at h
    simpa [Finset.sum_range_succ, Nat.mul_comm] using h
  have hpenalty :
      20 * degreeCount A 0 + 14 * degreeCount A 1 + 8 * degreeCount A 2 +
        3 * degreeCount A 3 + 4 * degreeCount A 6 + 13 * degreeCount A 7 +
        28 * degreeCount A 8 + 50 * degreeCount A 9 ≤ 4 := by
    have h := sum_function_mul_degreeCount A penalty
    have heq :
        20 * degreeCount A 0 + 14 * degreeCount A 1 + 8 * degreeCount A 2 +
          3 * degreeCount A 3 + 4 * degreeCount A 6 + 13 * degreeCount A 7 +
          28 * degreeCount A 8 + 50 * degreeCount A 9 =
            ∑ c, penalty (columnDegree A c) := by
      simpa [Finset.sum_range_succ, ZarankiewiczZ923.penalty, Nat.mul_comm,
        Nat.add_assoc] using h
    omega
  exact ZarankiewiczZ923.classify_degree_profile
    (degreeCount A 0) (degreeCount A 1) (degreeCount A 2)
    (degreeCount A 3) (degreeCount A 4) (degreeCount A 5)
    (degreeCount A 6) (degreeCount A 7) (degreeCount A 8)
    (degreeCount A 9) hcolumns hdegrees hpenalty

def contribution (A : BinaryMatrix (Fin 9) (Fin 23)) (r : Fin 9) (c : Fin 23) : Nat :=
  if A r c = true then Nat.choose (columnDegree A c - 1) 2 else 0

def rowContribution (A : BinaryMatrix (Fin 9) (Fin 23)) (r : Fin 9) : Nat :=
  ∑ c, contribution A r c

theorem row_formula (A : BinaryMatrix (Fin 9) (Fin 23)) (hA : K33Free A) (r : Fin 9) :
    rowDeficit A r + rowContribution A r = 56 := by
  simpa [rowContribution, contribution] using rowDeficit_add_sum_choose A hA r

theorem degree_ne_of_count_zero (A : BinaryMatrix (Fin 9) (Fin 23))
    (d : Nat) (hzero : degreeCount A d = 0) (c : Fin 23) :
    columnDegree A c ≠ d := by
  intro heq
  have hmem : c ∈ Finset.univ.filter (fun j => columnDegree A j = d) := by
    simp [heq]
  have hpos : 0 < degreeCount A d := by
    unfold degreeCount
    exact card_pos.mpr ⟨c, hmem⟩
  omega

theorem contribution_modEq_zero_of_degree_four_or_five
    (A : BinaryMatrix (Fin 9) (Fin 23)) (r : Fin 9) (c : Fin 23)
    (hdeg : columnDegree A c = 4 ∨ columnDegree A c = 5) :
    contribution A r c ≡ 0 [MOD 3] := by
  rcases hdeg with hdeg | hdeg <;>
    by_cases hrc : A r c = true <;>
      simp [contribution, hdeg, hrc, Nat.ModEq, Nat.choose]

theorem rowContribution_modEq_zero
    (A : BinaryMatrix (Fin 9) (Fin 23)) (r : Fin 9)
    (hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5) :
    rowContribution A r ≡ 0 [MOD 3] := by
  unfold rowContribution
  exact Nat.ModEq.sum_zero fun c _ =>
    contribution_modEq_zero_of_degree_four_or_five A r c (hdeg c)

theorem rowContribution_modEq_exception
    (A : BinaryMatrix (Fin 9) (Fin 23)) (r : Fin 9) (e : Fin 23)
    (hdeg : ∀ c, c ≠ e → columnDegree A c = 4 ∨ columnDegree A c = 5) :
    rowContribution A r ≡ contribution A r e [MOD 3] := by
  unfold rowContribution
  have h := Nat.sum_modEq_ite (n := 3) (s := (Finset.univ : Finset (Fin 23)))
    (a := e) (f := fun c => contribution A r c)
    (fun c _ hce => contribution_modEq_zero_of_degree_four_or_five A r c (hdeg c hce))
  simpa using h

theorem no_matrix_at_104 (A : BinaryMatrix (Fin 9) (Fin 23))
    (hA : K33Free A) (hweight : edgeCount A = 104) : False := by
  rcases degree_profile_of_104 A hA hweight with hbalanced | hthree | hsix
  · rcases hbalanced with ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    have hdeg : ∀ c, columnDegree A c = 4 ∨ columnDegree A c = 5 := by
      intro c
      have hle := columnDegree_le_card A c
      simp at hle
      have hn0 := degree_ne_of_count_zero A 0 h0 c
      have hn1 := degree_ne_of_count_zero A 1 h1 c
      have hn2 := degree_ne_of_count_zero A 2 h2 c
      have hn3 := degree_ne_of_count_zero A 3 h3 c
      have hn6 := degree_ne_of_count_zero A 6 h6 c
      have hn7 := degree_ne_of_count_zero A 7 h7 c
      have hn8 := degree_ne_of_count_zero A 8 h8 c
      have hn9 := degree_ne_of_count_zero A 9 h9 c
      omega
    have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 164 := by
      have hrel := incidence_penalty_identity A
      rw [penalty_sum_eq_histogram, h0, h1, h2, h3, h6, h7, h8, h9]
        at hrel
      simp at hrel
      omega
    have htotal := totalDeficit_add_sum_choose A hA
    rw [hinc] at htotal
    simp at htotal
    rw [show Nat.choose 9 3 = 84 by decide] at htotal
    have hD : totalDeficit A = 4 := by omega
    have hrows := sum_rowDeficit A
    rw [hD] at hrows
    have hpoint : ∀ r : Fin 9, 2 ≤ rowDeficit A r := by
      intro r
      have hmod := rowContribution_modEq_zero A r hdeg
      change rowContribution A r % 3 = 0 % 3 at hmod
      have hformula := row_formula A hA r
      omega
    have hlower := sum_lower_on_subset (fun r : Fin 9 => rowDeficit A r)
      (∅ : Finset (Fin 9)) 0 2 (by simp) (by
        intro r hrU hrE
        exact hpoint r)
    simp at hlower
    omega
  · rcases hthree with ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    have hfiber : #(Finset.univ.filter fun c : Fin 23 => columnDegree A c = 3) = 1 := by
      simpa [degreeCount] using h3
    obtain ⟨e, heq⟩ := card_eq_one.mp hfiber
    have hedeg : columnDegree A e = 3 := by
      have he : e ∈ Finset.univ.filter (fun c : Fin 23 => columnDegree A c = 3) := by
        rw [heq]
        simp
      exact (mem_filter.1 he).2
    have hunique : ∀ c, columnDegree A c = 3 → c = e := by
      intro c hc
      have hmem : c ∈ Finset.univ.filter (fun j : Fin 23 => columnDegree A j = 3) := by
        simp [hc]
      rw [heq] at hmem
      simpa using hmem
    have hdeg : ∀ c, c ≠ e → columnDegree A c = 4 ∨ columnDegree A c = 5 := by
      intro c hce
      have hle := columnDegree_le_card A c
      simp at hle
      have hn0 := degree_ne_of_count_zero A 0 h0 c
      have hn1 := degree_ne_of_count_zero A 1 h1 c
      have hn2 := degree_ne_of_count_zero A 2 h2 c
      have hn6 := degree_ne_of_count_zero A 6 h6 c
      have hn7 := degree_ne_of_count_zero A 7 h7 c
      have hn8 := degree_ne_of_count_zero A 8 h8 c
      have hn9 := degree_ne_of_count_zero A 9 h9 c
      have hn3 : columnDegree A c ≠ 3 := fun hc => hce (hunique c hc)
      omega
    have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 167 := by
      have hrel := incidence_penalty_identity A
      rw [penalty_sum_eq_histogram, h0, h1, h2, h3, h6, h7, h8, h9]
        at hrel
      simp at hrel
      omega
    have htotal := totalDeficit_add_sum_choose A hA
    rw [hinc] at htotal
    simp at htotal
    rw [show Nat.choose 9 3 = 84 by decide] at htotal
    have hD : totalDeficit A = 1 := by omega
    have hrows := sum_rowDeficit A
    rw [hD] at hrows
    have hinside : ∀ r ∈ columnSupport A e, 1 ≤ rowDeficit A r := by
      intro r hr
      have hre : A r e = true := by simpa [columnSupport] using hr
      have hmod := rowContribution_modEq_exception A r e hdeg
      change rowContribution A r % 3 = contribution A r e % 3 at hmod
      have hformula := row_formula A hA r
      simp [contribution, hre, hedeg] at hmod
      omega
    have houtside : ∀ r ∈ (Finset.univ : Finset (Fin 9)),
        r ∉ columnSupport A e → 2 ≤ rowDeficit A r := by
      intro r hrU hr
      have hre : A r e ≠ true := by
        intro htrue
        exact hr (by simp [columnSupport, htrue])
      have hmod := rowContribution_modEq_exception A r e hdeg
      change rowContribution A r % 3 = contribution A r e % 3 at hmod
      have hformula := row_formula A hA r
      simp [contribution, hre, hedeg] at hmod
      omega
    have hEcard : #(columnSupport A e) = 3 := by
      simpa [columnDegree] using hedeg
    have hlower := sum_lower_on_subset (fun r : Fin 9 => rowDeficit A r)
      (columnSupport A e) 1 2 hinside houtside
    rw [hEcard] at hlower
    simp at hlower
    omega
  · rcases hsix with ⟨h0, h1, h2, h3, h4, h5, h6, h7, h8, h9⟩
    have hfiber : #(Finset.univ.filter fun c : Fin 23 => columnDegree A c = 6) = 1 := by
      simpa [degreeCount] using h6
    obtain ⟨e, heq⟩ := card_eq_one.mp hfiber
    have hedeg : columnDegree A e = 6 := by
      have he : e ∈ Finset.univ.filter (fun c : Fin 23 => columnDegree A c = 6) := by
        rw [heq]
        simp
      exact (mem_filter.1 he).2
    have hunique : ∀ c, columnDegree A c = 6 → c = e := by
      intro c hc
      have hmem : c ∈ Finset.univ.filter (fun j : Fin 23 => columnDegree A j = 6) := by
        simp [hc]
      rw [heq] at hmem
      simpa using hmem
    have hdeg : ∀ c, c ≠ e → columnDegree A c = 4 ∨ columnDegree A c = 5 := by
      intro c hce
      have hle := columnDegree_le_card A c
      simp at hle
      have hn0 := degree_ne_of_count_zero A 0 h0 c
      have hn1 := degree_ne_of_count_zero A 1 h1 c
      have hn2 := degree_ne_of_count_zero A 2 h2 c
      have hn3 := degree_ne_of_count_zero A 3 h3 c
      have hn7 := degree_ne_of_count_zero A 7 h7 c
      have hn8 := degree_ne_of_count_zero A 8 h8 c
      have hn9 := degree_ne_of_count_zero A 9 h9 c
      have hn6 : columnDegree A c ≠ 6 := fun hc => hce (hunique c hc)
      omega
    have hinc : (∑ c, Nat.choose (columnDegree A c) 3) = 168 := by
      have hrel := incidence_penalty_identity A
      rw [penalty_sum_eq_histogram, h0, h1, h2, h3, h6, h7, h8, h9]
        at hrel
      simp at hrel
      omega
    have htotal := totalDeficit_add_sum_choose A hA
    rw [hinc] at htotal
    simp at htotal
    rw [show Nat.choose 9 3 = 84 by decide] at htotal
    have hD : totalDeficit A = 0 := by omega
    have hrows := sum_rowDeficit A
    rw [hD] at hrows
    have hinside : ∀ r ∈ columnSupport A e, 1 ≤ rowDeficit A r := by
      intro r hr
      have hre : A r e = true := by simpa [columnSupport] using hr
      have hmod := rowContribution_modEq_exception A r e hdeg
      change rowContribution A r % 3 = contribution A r e % 3 at hmod
      have hformula := row_formula A hA r
      simp [contribution, hre, hedeg, Nat.choose] at hmod
      omega
    have houtside : ∀ r ∈ (Finset.univ : Finset (Fin 9)),
        r ∉ columnSupport A e → 2 ≤ rowDeficit A r := by
      intro r hrU hr
      have hre : A r e ≠ true := by
        intro htrue
        exact hr (by simp [columnSupport, htrue])
      have hmod := rowContribution_modEq_exception A r e hdeg
      change rowContribution A r % 3 = contribution A r e % 3 at hmod
      have hformula := row_formula A hA r
      simp [contribution, hre, hedeg] at hmod
      omega
    have hEcard : #(columnSupport A e) = 6 := by
      simpa [columnDegree] using hedeg
    have hlower := sum_lower_on_subset (fun r : Fin 9 => rowDeficit A r)
      (columnSupport A e) 1 2 hinside houtside
    rw [hEcard] at hlower
    simp at hlower
    omega

/-- No denser matrix exists: retain any 104 ones and apply `no_matrix_at_104`. -/
theorem upper_bound : UpperBound 9 23 103 := by
  intro A hA
  by_contra hnot
  have hge : 104 ≤ edgeCount A := by omega
  obtain ⟨B, hBA, hBweight⟩ := exists_submatrix_of_edgeCount_le A 104 hge
  exact no_matrix_at_104 B (hA.mono hBA) hBweight

/-- The end-to-end, kernel-checked exact value. -/
theorem exact_value : Zarankiewicz.Exact 9 23 103 :=
  ⟨Zarankiewicz.Witnesses.z9_23_lower, upper_bound⟩

end Zarankiewicz.Exact.Z9_23
