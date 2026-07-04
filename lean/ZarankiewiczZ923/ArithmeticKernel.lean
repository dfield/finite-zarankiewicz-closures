import Lean.Elab.Tactic.Omega

/-!
# Arithmetic kernel for `Z(9,23,3,3) = 103`

This file checks the finite arithmetic at the center of `docs/PROOF.md`:

* the ten values of the one-column penalty;
* the classification of all degree histograms at weight 104; and
* the three marked-row residue contradictions.

It uses only Lean and `Std`; there is no Mathlib dependency, no custom axiom,
and no `sorry`.  The combinatorial double-counting that turns a Boolean matrix
into these hypotheses remains part of the human-readable proof and the Python
audit.  The repository does not claim that this file formalizes that layer.
-/

namespace ZarankiewiczZ923

/-- The concrete binomial coefficient `d choose 3`, written in an executable form. -/
def chooseThree (d : Nat) : Nat := d * (d - 1) * (d - 2) / 6

/--
The nonnegative penalty `p(d) = (d choose 3) - 6d + 20` for the ten possible
column degrees.  Values outside the matrix range are deliberately set to zero;
all theorems connecting this table to the formula use `Fin 10`.
-/
def penalty : Nat → Nat
  | 0 => 20
  | 1 => 14
  | 2 => 8
  | 3 => 3
  | 4 => 0
  | 5 => 0
  | 6 => 4
  | 7 => 13
  | 8 => 28
  | 9 => 50
  | _ => 0

/-- The table is exactly the integer-valued formula used in the paper proof. -/
theorem penalty_eq_formula : ∀ d : Fin 10,
    (penalty d.val : Int) = (chooseThree d.val : Int) - 6 * (d.val : Int) + 20 := by
  decide

/-- The complete penalty table, exposed as a separately checked regression fact. -/
theorem penalty_table :
    List.ofFn (fun d : Fin 10 => penalty d.val) = [20, 14, 8, 3, 0, 0, 4, 13, 28, 50] := by
  decide

/-- The affine base in equation (2) of the proof is 164. -/
theorem affine_base : 6 * 104 - 20 * 23 = 164 := by decide

/-- The 84 row triples, each with capacity two, supply 168 units. -/
theorem total_triple_capacity : 2 * chooseThree 9 = 168 := by decide

/-- A penalty budget of four leaves only degrees 3--6, with at most one exception. -/
theorem penalty_budget_structure
    (n0 n1 n2 n3 n6 n7 n8 n9 : Nat)
    (hpenalty :
      20 * n0 + 14 * n1 + 8 * n2 + 3 * n3 + 4 * n6 + 13 * n7 +
        28 * n8 + 50 * n9 ≤ 4) :
    n0 = 0 ∧ n1 = 0 ∧ n2 = 0 ∧ n7 = 0 ∧ n8 = 0 ∧ n9 = 0 ∧
      n3 ≤ 1 ∧ n6 ≤ 1 ∧ n3 + n6 ≤ 1 := by
  omega

/--
Every degree histogram of 23 columns, total degree 104, and penalty at most
four is one of the three histograms in equation (4) of the human proof.

Writing all ten variables explicitly keeps the statement independent of any
list indexing convention.  `omega` checks the resulting Presburger formula.
-/
theorem classify_degree_profile
    (n0 n1 n2 n3 n4 n5 n6 n7 n8 n9 : Nat)
    (hcolumns : n0 + n1 + n2 + n3 + n4 + n5 + n6 + n7 + n8 + n9 = 23)
    (hweight :
      n1 + 2 * n2 + 3 * n3 + 4 * n4 + 5 * n5 + 6 * n6 + 7 * n7 +
        8 * n8 + 9 * n9 = 104)
    (hpenalty :
      20 * n0 + 14 * n1 + 8 * n2 + 3 * n3 + 4 * n6 + 13 * n7 +
        28 * n8 + 50 * n9 ≤ 4) :
    (n0 = 0 ∧ n1 = 0 ∧ n2 = 0 ∧ n3 = 0 ∧ n4 = 11 ∧ n5 = 12 ∧
      n6 = 0 ∧ n7 = 0 ∧ n8 = 0 ∧ n9 = 0) ∨
    (n0 = 0 ∧ n1 = 0 ∧ n2 = 0 ∧ n3 = 1 ∧ n4 = 9 ∧ n5 = 13 ∧
      n6 = 0 ∧ n7 = 0 ∧ n8 = 0 ∧ n9 = 0) ∨
    (n0 = 0 ∧ n1 = 0 ∧ n2 = 0 ∧ n3 = 0 ∧ n4 = 12 ∧ n5 = 10 ∧
      n6 = 1 ∧ n7 = 0 ∧ n8 = 0 ∧ n9 = 0) := by
  obtain ⟨hn0, hn1, hn2, hn7, hn8, hn9, hn3le, hn6le, hsumle⟩ :=
    penalty_budget_structure n0 n1 n2 n3 n6 n7 n8 n9 hpenalty
  have hn3 : n3 = 0 ∨ n3 = 1 := by omega
  have hn6 : n6 = 0 ∨ n6 = 1 := by omega
  rcases hn3 with hn3 | hn3 <;> rcases hn6 with hn6 | hn6 <;> omega

/-- A nonnegative integer congruent to one modulo three is at least one. -/
theorem mod_three_eq_one_lower {d : Nat} (h : d % 3 = 1) : 1 ≤ d := by
  omega

/-- A nonnegative integer congruent to two modulo three is at least two. -/
theorem mod_three_eq_two_lower {d : Nat} (h : d % 3 = 2) : 2 ≤ d := by
  omega

/--
The balanced profile cannot have exact marked-row deficit sum 12: all nine
deficits have residue two, so their sum is at least 18.
-/
theorem balanced_deficits_impossible
    (d0 d1 d2 d3 d4 d5 d6 d7 d8 : Nat)
    (hsum : d0 + d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8 = 12)
    (h0 : d0 % 3 = 2) (h1 : d1 % 3 = 2) (h2 : d2 % 3 = 2)
    (h3 : d3 % 3 = 2) (h4 : d4 % 3 = 2) (h5 : d5 % 3 = 2)
    (h6 : d6 % 3 = 2) (h7 : d7 % 3 = 2) (h8 : d8 % 3 = 2) : False := by
  have h0' := mod_three_eq_two_lower h0
  have h1' := mod_three_eq_two_lower h1
  have h2' := mod_three_eq_two_lower h2
  have h3' := mod_three_eq_two_lower h3
  have h4' := mod_three_eq_two_lower h4
  have h5' := mod_three_eq_two_lower h5
  have h6' := mod_three_eq_two_lower h6
  have h7' := mod_three_eq_two_lower h7
  have h8' := mod_three_eq_two_lower h8
  omega

/--
With one degree-three column, three deficits have residue one and six have
residue two.  Their sum is at least 15, contradicting the exact sum three.
-/
theorem degree_three_deficits_impossible
    (d0 d1 d2 d3 d4 d5 d6 d7 d8 : Nat)
    (hsum : d0 + d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8 = 3)
    (h0 : d0 % 3 = 1) (h1 : d1 % 3 = 1) (h2 : d2 % 3 = 1)
    (h3 : d3 % 3 = 2) (h4 : d4 % 3 = 2) (h5 : d5 % 3 = 2)
    (h6 : d6 % 3 = 2) (h7 : d7 % 3 = 2) (h8 : d8 % 3 = 2) : False := by
  have h0' := mod_three_eq_one_lower h0
  have h1' := mod_three_eq_one_lower h1
  have h2' := mod_three_eq_one_lower h2
  have h3' := mod_three_eq_two_lower h3
  have h4' := mod_three_eq_two_lower h4
  have h5' := mod_three_eq_two_lower h5
  have h6' := mod_three_eq_two_lower h6
  have h7' := mod_three_eq_two_lower h7
  have h8' := mod_three_eq_two_lower h8
  omega

/--
With one degree-six column, six deficits have residue one and three have
residue two.  Their sum is at least 12, contradicting the exact sum zero.
-/
theorem degree_six_deficits_impossible
    (d0 d1 d2 d3 d4 d5 d6 d7 d8 : Nat)
    (hsum : d0 + d1 + d2 + d3 + d4 + d5 + d6 + d7 + d8 = 0)
    (h0 : d0 % 3 = 1) (h1 : d1 % 3 = 1) (h2 : d2 % 3 = 1)
    (h3 : d3 % 3 = 1) (h4 : d4 % 3 = 1) (h5 : d5 % 3 = 1)
    (h6 : d6 % 3 = 2) (h7 : d7 % 3 = 2) (h8 : d8 % 3 = 2) : False := by
  have h0' := mod_three_eq_one_lower h0
  have h1' := mod_three_eq_one_lower h1
  have h2' := mod_three_eq_one_lower h2
  have h3' := mod_three_eq_one_lower h3
  have h4' := mod_three_eq_one_lower h4
  have h5' := mod_three_eq_one_lower h5
  have h6' := mod_three_eq_two_lower h6
  have h7' := mod_three_eq_two_lower h7
  have h8' := mod_three_eq_two_lower h8
  omega

end ZarankiewiczZ923
