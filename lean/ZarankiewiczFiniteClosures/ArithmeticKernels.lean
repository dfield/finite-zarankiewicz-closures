import Lean.Elab.Tactic.Omega

/-!
# Arithmetic kernels for three additional finite closures

This file checks the arithmetic endpoints for `Z(10,21,3,3) = 106`,
`Z(10,22,3,3) = 110`, and `Z(11,20,3,3) = 111`.  As with the original
`ZarankiewiczZ923` module, the combinatorial reductions remain in the proof
documents and Python certificates.  In particular, Lean checks the reported
finite minima for the pair-deficit cases but does not re-run the orbit search.
-/

namespace ZarankiewiczFiniteClosures

def chooseThree (d : Nat) : Nat := d * (d - 1) * (d - 2) / 6

/-! ## Vertex-deletion arithmetic -/

theorem z10_21_deletion_bound : (10 * 96) / 9 = 106 := by decide

theorem z11_19_deletion_bound : (19 * 101) / 18 = 106 := by decide

theorem z11_20_deletion_bound : (20 * 106) / 19 = 111 := by decide

theorem z10_21_excluded_target
    (deletedDegree : Nat)
    (hdegree : deletedDegree ≤ 10)
    (hremaining : 107 ≤ 96 + deletedDegree) : False := by
  omega

theorem z11_19_excluded_target
    (deletedDegree : Nat)
    (hdegree : deletedDegree ≤ 5)
    (hremaining : 107 ≤ 101 + deletedDegree) : False := by
  omega

theorem z11_20_excluded_target
    (deletedDegree : Nat)
    (hdegree : deletedDegree ≤ 5)
    (hremaining : 112 ≤ 106 + deletedDegree) : False := by
  omega

/-! ## The `Z(10,22)` degree-profile boundary -/

def z10Penalty : Nat → Nat
  | 0 => 40
  | 1 => 30
  | 2 => 20
  | 3 => 11
  | 4 => 4
  | 5 => 0
  | 6 => 0
  | 7 => 5
  | 8 => 16
  | 9 => 34
  | 10 => 60
  | _ => 0

theorem z10_penalty_eq_formula : ∀ d : Fin 11,
    (z10Penalty d.val : Int) = (chooseThree d.val : Int) - 10 * (d.val : Int) + 40 := by
  decide

theorem z10_penalty_table :
    List.ofFn (fun d : Fin 11 => z10Penalty d.val) =
      [40, 30, 20, 11, 4, 0, 0, 5, 16, 34, 60] := by
  decide

theorem z10_22_affine_base : 10 * 111 - 40 * 22 = 230 := by decide

theorem z10_22_triple_capacity : 2 * chooseThree 10 = 240 := by decide

theorem z10_penalty_budget_structure
    (n0 n1 n2 n3 n4 n7 n8 n9 n10 : Nat)
    (hpenalty :
      40 * n0 + 30 * n1 + 20 * n2 + 11 * n3 + 4 * n4 + 5 * n7 +
        16 * n8 + 34 * n9 + 60 * n10 ≤ 10) :
    n0 = 0 ∧ n1 = 0 ∧ n2 = 0 ∧ n3 = 0 ∧ n8 = 0 ∧ n9 = 0 ∧ n10 = 0 ∧
      n4 ≤ 2 ∧ n7 ≤ 2 ∧ 4 * n4 + 5 * n7 ≤ 10 := by
  omega

theorem classify_z10_22_degree_profile
    (n4 n5 n6 n7 : Nat)
    (hcolumns : n4 + n5 + n6 + n7 = 22)
    (hweight : 4 * n4 + 5 * n5 + 6 * n6 + 7 * n7 = 111)
    (hpenalty : 4 * n4 + 5 * n7 ≤ 10) :
    (n4 = 0 ∧ n5 = 21 ∧ n6 = 1 ∧ n7 = 0) ∨
    (n4 = 1 ∧ n5 = 19 ∧ n6 = 2 ∧ n7 = 0) ∨
    (n4 = 2 ∧ n5 = 17 ∧ n6 = 3 ∧ n7 = 0) ∨
    (n4 = 1 ∧ n5 = 20 ∧ n6 = 0 ∧ n7 = 1) := by
  have hn4 : n4 = 0 ∨ n4 = 1 ∨ n4 = 2 := by omega
  have hn7 : n7 = 0 ∨ n7 = 1 ∨ n7 = 2 := by omega
  rcases hn4 with hn4 | hn4 | hn4 <;>
    rcases hn7 with hn7 | hn7 | hn7 <;> omega

/-! ## Terminal arithmetic for the four profiles -/

theorem z10_22_case_a_impossible (columnsThroughRow : Nat)
    (hdivisibility : 4 * columnsThroughRow = 45) : False := by
  omega

theorem z10_22_case_b_orbit_minima :
    List.all [21, 21, 21, 33, 48] (fun minimum => 18 < minimum) = true := by
  decide

theorem z10_22_case_b_impossible (pairDeficit : Nat)
    (hexact : pairDeficit = 18) (hlower : 21 ≤ pairDeficit) : False := by
  omega

theorem z10_22_case_c_impossible (pairDeficit : Nat)
    (hexact : pairDeficit = 6) (hlower : 12 ≤ pairDeficit) : False := by
  omega

theorem z10_22_case_d_impossible (rowDeficit : Nat)
    (hexact : rowDeficit = 3) (hlower : 9 ≤ rowDeficit) : False := by
  omega

end ZarankiewiczFiniteClosures
