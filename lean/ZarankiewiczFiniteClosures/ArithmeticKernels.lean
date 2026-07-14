import Lean.Elab.Tactic.Omega

/-!
# Arithmetic kernels for additional finite closures and frontier bounds

This file checks arithmetic endpoints for five further exact values, two
candidate implications, and the bound `Z(13,23,3,3) ≤ 144`. As with the
original `ZarankiewiczZ923` module, the combinatorial reductions remain in the
proof documents and Python certificates. In particular, Lean checks reported
finite minima but does not re-run row-symmetry or row-type enumeration or
replay the still-incomplete `Z(10,23)` propositional certificates.
-/

namespace ZarankiewiczFiniteClosures

def chooseThree (d : Nat) : Nat := d * (d - 1) * (d - 2) / 6

/-! ## Vertex-deletion arithmetic -/

theorem z10_21_deletion_bound : (10 * 96) / 9 = 106 := by decide

theorem z11_19_deletion_bound : (19 * 101) / 18 = 106 := by decide

theorem z11_20_deletion_bound : (20 * 106) / 19 = 111 := by decide

theorem z11_23_deletion_bound : (11 * 112) / 10 = 123 := by decide

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

theorem z11_23_excluded_target
    (deletedDegree : Nat)
    (hdegree : deletedDegree ≤ 11)
    (hremaining : 124 ≤ 112 + deletedDegree) : False := by
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

/-! ## The `Z(10,23)` arithmetic front end -/

theorem z10_23_affine_base : 10 * 113 - 40 * 23 = 210 := by decide

theorem z10_23_penalty_budget : 240 - 210 = 30 := by decide

theorem z10_23_low_column_impossible
    (columnDegree : Nat)
    (hdegree : columnDegree ≤ 2)
    (hremaining : 113 ≤ 110 + columnDegree) : False := by
  omega

theorem z10_23_two_degree_three_impossible
    (firstDegree secondDegree : Nat)
    (hfirst : firstDegree ≤ 3)
    (hsecond : secondDegree ≤ 3)
    (hremaining : 113 ≤ 106 + firstDegree + secondDegree) : False := by
  omega

theorem z10_23_two_six_residue_minima :
    List.all [18, 15, 12, 9, 6] (fun minimum => 3 < minimum) = true := by
  decide

theorem z10_23_three_six_residue_minima :
    List.all [18, 15, 12, 9] (fun minimum => 6 < minimum) = true := by
  decide

theorem z10_23_exceptional_profile_impossible
    (pairResidue : Nat)
    (hbudget : pairResidue ≤ 18)
    (henumeratedMinimum : 39 ≤ pairResidue) : False := by
  omega

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

/-! ## The `Z(12,23)` two-stage deficit boundary -/

def z12Penalty : Nat → Nat
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
  | 11 => 95
  | 12 => 140
  | _ => 0

theorem z12_penalty_eq_formula : ∀ d : Fin 13,
    (z12Penalty d.val : Int) = (chooseThree d.val : Int) - 10 * (d.val : Int) + 40 := by
  decide

theorem z12_penalty_table :
    List.ofFn (fun d : Fin 13 => z12Penalty d.val) =
      [40, 30, 20, 11, 4, 0, 0, 5, 16, 34, 60, 95, 140] := by
  decide

theorem z12_23_at_136_profile
    (n5 n6 : Nat)
    (hcolumns : n5 + n6 = 23)
    (hweight : 5 * n5 + 6 * n6 = 136) :
    n5 = 2 ∧ n6 = 21 := by
  omega

theorem z12_23_at_136_pair_equation
    (degreeFive degreeSix : Nat)
    (hdegreeFive : degreeFive ≤ 2)
    (hequation : 3 * degreeFive + 4 * degreeSix = 20) :
    degreeFive = 0 ∧ degreeSix = 5 := by
  omega

theorem z12_23_penalty_budget_structure
    (n0 n1 n2 n3 n4 n7 n8 n9 n10 n11 n12 : Nat)
    (hpenalty :
      40 * n0 + 30 * n1 + 20 * n2 + 11 * n3 + 4 * n4 + 5 * n7 +
        16 * n8 + 34 * n9 + 60 * n10 + 95 * n11 + 140 * n12 ≤ 10) :
    n0 = 0 ∧ n1 = 0 ∧ n2 = 0 ∧ n3 = 0 ∧ n8 = 0 ∧ n9 = 0 ∧
      n10 = 0 ∧ n11 = 0 ∧ n12 = 0 ∧ n4 ≤ 2 ∧ n7 ≤ 2 ∧
      4 * n4 + 5 * n7 ≤ 10 := by
  omega

theorem classify_z12_23_degree_profile
    (n4 n5 n6 n7 : Nat)
    (hcolumns : n4 + n5 + n6 + n7 = 23)
    (hweight : 4 * n4 + 5 * n5 + 6 * n6 + 7 * n7 = 135)
    (hpenalty : 4 * n4 + 5 * n7 ≤ 10) :
    (n4 = 0 ∧ n5 = 3 ∧ n6 = 20 ∧ n7 = 0) ∨
    (n4 = 1 ∧ n5 = 1 ∧ n6 = 21 ∧ n7 = 0) ∨
    (n4 = 0 ∧ n5 = 4 ∧ n6 = 18 ∧ n7 = 1) ∨
    (n4 = 1 ∧ n5 = 2 ∧ n6 = 19 ∧ n7 = 1) ∨
    (n4 = 0 ∧ n5 = 5 ∧ n6 = 16 ∧ n7 = 2) := by
  have hn4 : n4 = 0 ∨ n4 = 1 ∨ n4 = 2 := by omega
  have hn7 : n7 = 0 ∨ n7 = 1 ∨ n7 = 2 := by omega
  rcases hn4 with hn4 | hn4 | hn4 <;>
    rcases hn7 with hn7 | hn7 | hn7 <;> omega

theorem z12_23_case_one_impossible (rowResidue : Nat)
    (hbudget : rowResidue ≤ 30) (hlower : 40 ≤ rowResidue) : False := by
  omega

theorem z12_23_case_two_impossible (pairResidue : Nat)
    (hexact : pairResidue = 22) (hbudget : pairResidue ≤ 18) : False := by
  omega

theorem z12_23_case_three_minimum : 15 < 25 := by decide

theorem z12_23_case_four_impossible (degreeSevenRows : Nat)
    (hrequired : degreeSevenRows = 7) (hmaximum : degreeSevenRows ≤ 5) : False := by
  omega

theorem z12_23_case_five_impossible (tripleIncidence : Nat)
    (hforced : tripleIncidence = 50) (havailable : tripleIncidence ≤ 20) : False := by
  omega

/-! ## The `Z(13,23) ≤ 144` marked-row boundary -/

def z13Penalty : Nat → Nat
  | 0 => 70
  | 1 => 55
  | 2 => 40
  | 3 => 26
  | 4 => 14
  | 5 => 5
  | 6 => 0
  | 7 => 0
  | 8 => 6
  | 9 => 19
  | 10 => 40
  | 11 => 70
  | 12 => 110
  | 13 => 161
  | _ => 0

theorem z13_penalty_eq_formula : ∀ d : Fin 14,
    (z13Penalty d.val : Int) = (chooseThree d.val : Int) - 15 * (d.val : Int) + 70 := by
  decide

theorem z13_23_penalty_budget_structure
    (n0 n1 n2 n3 n4 n5 n8 n9 n10 n11 n12 n13 : Nat)
    (hpenalty :
      70 * n0 + 55 * n1 + 40 * n2 + 26 * n3 + 14 * n4 + 5 * n5 +
        6 * n8 + 19 * n9 + 40 * n10 + 70 * n11 + 110 * n12 + 161 * n13 ≤ 7) :
    n0 = 0 ∧ n1 = 0 ∧ n2 = 0 ∧ n3 = 0 ∧ n4 = 0 ∧ n9 = 0 ∧
      n10 = 0 ∧ n11 = 0 ∧ n12 = 0 ∧ n13 = 0 ∧ n5 ≤ 1 ∧ n8 ≤ 1 ∧
      5 * n5 + 6 * n8 ≤ 7 := by
  omega

theorem classify_z13_23_degree_profile
    (n5 n6 n7 n8 : Nat)
    (hcolumns : n5 + n6 + n7 + n8 = 23)
    (hweight : 5 * n5 + 6 * n6 + 7 * n7 + 8 * n8 = 145)
    (hpenalty : 5 * n5 + 6 * n8 ≤ 7) :
    (n5 = 0 ∧ n6 = 16 ∧ n7 = 7 ∧ n8 = 0) ∨
    (n5 = 1 ∧ n6 = 14 ∧ n7 = 8 ∧ n8 = 0) ∨
    (n5 = 0 ∧ n6 = 17 ∧ n7 = 5 ∧ n8 = 1) := by
  have hn5 : n5 = 0 ∨ n5 = 1 := by omega
  have hn8 : n8 = 0 ∨ n8 = 1 := by omega
  rcases hn5 with hn5 | hn5 <;> rcases hn8 with hn8 | hn8 <;> omega

theorem z13_23_clean_row_contradiction
    (forcedDeficit deficitBudget : Nat)
    (hlower : 2 * forcedDeficit ≤ deficitBudget)
    (hstrict : deficitBudget < 2 * forcedDeficit) : False := by
  omega

theorem z13_23_case_deficit_bounds : 21 < 26 ∧ 6 < 16 ∧ 3 < 10 := by
  decide

end ZarankiewiczFiniteClosures
