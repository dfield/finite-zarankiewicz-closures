import Zarankiewicz.Counting
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Order.Fin.Basic
import Lean.Elab.Tactic.Omega

/-!
# Row and column deletion

These lemmas formalize the standard averaging-and-deletion arguments used to
transfer finite Zarankiewicz upper bounds between adjacent dimensions.  They
operate on the matrix itself; no certificate or external computation is used.
-/

namespace Zarankiewicz

open scoped BigOperators
open Finset

variable {R C : Type*} [Fintype R] [DecidableEq R]
  [Fintype C] [DecidableEq C]

/-- The number of ones in a fixed row. -/
def rowDegree (A : BinaryMatrix R C) (r : R) : Nat :=
  #(Finset.univ.filter fun c => A r c = true)

/-- Summing the row degrees recovers the matrix weight. -/
theorem sum_rowDegree_eq_edgeCount (A : BinaryMatrix R C) :
    (∑ r, rowDegree A r) = edgeCount A := by
  unfold rowDegree edgeCount columnDegree columnSupport
  simp_rw [card_filter_eq_sum_indicator]
  rw [Finset.sum_comm]

/-- Remove one column, retaining the original order of the other columns. -/
def deleteColumn {m n : Nat} (A : BinaryMatrix (Fin m) (Fin (n + 1)))
    (c : Fin (n + 1)) : BinaryMatrix (Fin m) (Fin n) :=
  fun r j => A r (c.succAbove j)

/-- Remove one row, retaining the original order of the other rows. -/
def deleteRow {m n : Nat} (A : BinaryMatrix (Fin (m + 1)) (Fin n))
    (r : Fin (m + 1)) : BinaryMatrix (Fin m) (Fin n) :=
  fun i c => A (r.succAbove i) c

@[simp] theorem columnDegree_deleteColumn {m n : Nat}
    (A : BinaryMatrix (Fin m) (Fin (n + 1))) (c : Fin (n + 1)) (j : Fin n) :
    columnDegree (deleteColumn A c) j = columnDegree A (c.succAbove j) := by
  rfl

@[simp] theorem rowDegree_deleteRow {m n : Nat}
    (A : BinaryMatrix (Fin (m + 1)) (Fin n)) (r : Fin (m + 1)) (i : Fin m) :
    rowDegree (deleteRow A r) i = rowDegree A (r.succAbove i) := by
  rfl

/-- Matrix weight decomposes into a removed column and the remaining matrix. -/
theorem columnDegree_add_edgeCount_deleteColumn {m n : Nat}
    (A : BinaryMatrix (Fin m) (Fin (n + 1))) (c : Fin (n + 1)) :
    columnDegree A c + edgeCount (deleteColumn A c) = edgeCount A := by
  rw [edgeCount, edgeCount]
  simp only [columnDegree_deleteColumn]
  exact (Fin.sum_univ_succAbove (columnDegree A) c).symm

/-- Matrix weight decomposes into a removed row and the remaining matrix. -/
theorem rowDegree_add_edgeCount_deleteRow {m n : Nat}
    (A : BinaryMatrix (Fin (m + 1)) (Fin n)) (r : Fin (m + 1)) :
    rowDegree A r + edgeCount (deleteRow A r) = edgeCount A := by
  rw [← sum_rowDegree_eq_edgeCount A, ← sum_rowDegree_eq_edgeCount (deleteRow A r)]
  simp only [rowDegree_deleteRow]
  exact (Fin.sum_univ_succAbove (rowDegree A) r).symm

/-- Deleting a row preserves `K_{3,3}`-freeness. -/
theorem K33Free.deleteRow {m n : Nat}
    {A : BinaryMatrix (Fin (m + 1)) (Fin n)} (hA : K33Free A)
    (r : Fin (m + 1)) : K33Free (deleteRow A r) := by
  intro a b c hab hbc
  simpa [commonColumnCount, deleteRow] using
    hA (r.succAbove a) (r.succAbove b) (r.succAbove c)
      (r.strictMono_succAbove hab) (r.strictMono_succAbove hbc)

/-- Deleting a column preserves `K_{3,3}`-freeness. -/
theorem K33Free.deleteColumn {m n : Nat}
    {A : BinaryMatrix (Fin m) (Fin (n + 1))} (hA : K33Free A)
    (c : Fin (n + 1)) : K33Free (deleteColumn A c) := by
  intro a b d hab hbd
  let S : Finset (Fin n) := Finset.univ.filter fun j =>
    Zarankiewicz.deleteColumn A c a j = true ∧
      Zarankiewicz.deleteColumn A c b j = true ∧
      Zarankiewicz.deleteColumn A c d j = true
  let T : Finset (Fin (n + 1)) := Finset.univ.filter fun j =>
    A a j = true ∧ A b j = true ∧ A d j = true
  have hsubset : S.map c.succAboveEmb ⊆ T := by
    intro j hj
    simp only [S, mem_map] at hj
    rcases hj with ⟨i, hi, rfl⟩
    simp only [T, mem_filter, mem_univ, true_and]
    simpa [S, deleteColumn] using hi
  have hcard : #S ≤ #T := by
    calc
      #S = #(S.map c.succAboveEmb) := (card_map c.succAboveEmb).symm
      _ ≤ #T := card_le_card hsubset
  simpa [commonColumnCount, S, T] using
    le_trans hcard (hA a b d hab hbd)

/-! ## Averaging and adjacent-dimension bounds -/

/-- If the total weight is below `|R| (k+1)`, some row has degree at most
`k`. -/
theorem exists_rowDegree_le_of_edgeCount_lt_mul (A : BinaryMatrix R C)
    (k : Nat) (hweight : edgeCount A < Fintype.card R * (k + 1)) :
    ∃ r, rowDegree A r ≤ k := by
  by_contra h
  simp only [not_exists, not_le] at h
  have hlower : Fintype.card R * (k + 1) ≤ ∑ r, rowDegree A r := by
    calc
      Fintype.card R * (k + 1) = ∑ _r : R, (k + 1) := by simp
      _ ≤ ∑ r, rowDegree A r := sum_le_sum fun r _ => h r
  rw [sum_rowDegree_eq_edgeCount] at hlower
  omega

/-- If the total weight is below `|C| (k+1)`, some column has degree at most
`k`. -/
theorem exists_columnDegree_le_of_edgeCount_lt_mul (A : BinaryMatrix R C)
    (k : Nat) (hweight : edgeCount A < Fintype.card C * (k + 1)) :
    ∃ c, columnDegree A c ≤ k := by
  by_contra h
  simp only [not_exists, not_le] at h
  have hlower : Fintype.card C * (k + 1) ≤ ∑ c, columnDegree A c := by
    calc
      Fintype.card C * (k + 1) = ∑ _c : C, (k + 1) := by simp
      _ ≤ ∑ c, columnDegree A c := sum_le_sum fun c _ => h c
  rw [← edgeCount] at hlower
  omega

/-- Add one row by thinning to the first forbidden weight, averaging, and
deleting a low-degree row. -/
theorem UpperBound.addRow_of_average {m n e k : Nat}
    (hbase : UpperBound m n e)
    (haverage : e + k + 1 < (m + 1) * (k + 1)) :
    UpperBound (m + 1) n (e + k) := by
  intro A hA
  by_contra htooMany
  have htarget : e + k + 1 ≤ edgeCount A := by omega
  obtain ⟨B, hBA, hBweight⟩ :=
    exists_submatrix_of_edgeCount_le A (e + k + 1) htarget
  have hBfree : K33Free B := hA.mono hBA
  have havg : edgeCount B < Fintype.card (Fin (m + 1)) * (k + 1) := by
    simpa [hBweight] using haverage
  obtain ⟨r, hr⟩ := exists_rowDegree_le_of_edgeCount_lt_mul B k havg
  have hdecomp := rowDegree_add_edgeCount_deleteRow B r
  have hremaining : e + 1 ≤ edgeCount (deleteRow B r) := by omega
  have hupper := hbase (deleteRow B r) (hBfree.deleteRow r)
  omega

/-- Add one column by thinning to the first forbidden weight, averaging, and
deleting a low-degree column. -/
theorem UpperBound.addColumn_of_average {m n e k : Nat}
    (hbase : UpperBound m n e)
    (haverage : e + k + 1 < (n + 1) * (k + 1)) :
    UpperBound m (n + 1) (e + k) := by
  intro A hA
  by_contra htooMany
  have htarget : e + k + 1 ≤ edgeCount A := by omega
  obtain ⟨B, hBA, hBweight⟩ :=
    exists_submatrix_of_edgeCount_le A (e + k + 1) htarget
  have hBfree : K33Free B := hA.mono hBA
  have havg : edgeCount B < Fintype.card (Fin (n + 1)) * (k + 1) := by
    simpa [hBweight] using haverage
  obtain ⟨c, hc⟩ := exists_columnDegree_le_of_edgeCount_lt_mul B k havg
  have hdecomp := columnDegree_add_edgeCount_deleteColumn B c
  have hremaining : e + 1 ≤ edgeCount (deleteColumn B c) := by omega
  have hupper := hbase (deleteColumn B c) (hBfree.deleteColumn c)
  omega

end Zarankiewicz
