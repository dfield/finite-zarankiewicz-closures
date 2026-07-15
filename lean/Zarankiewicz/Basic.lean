import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Fintype.Card
import Mathlib.Algebra.BigOperators.Group.Finset.Basic

/-!
# Finite Zarankiewicz matrices

This module gives the theorem-level definitions used by the pure-Lean
formalization.  A binary matrix is represented extensionally as a function
from rows and columns to `Bool`.
-/

namespace Zarankiewicz

open scoped BigOperators
open Finset

/-- A finite Boolean matrix with row type `R` and column type `C`. -/
abbrev BinaryMatrix (R C : Type*) := R → C → Bool

/-- The rows occupied by a fixed column. -/
def columnSupport {R C : Type*} [Fintype R] [DecidableEq R]
    (A : BinaryMatrix R C) (c : C) : Finset R :=
  Finset.univ.filter fun r => A r c = true

/-- The number of ones in a fixed column. -/
def columnDegree {R C : Type*} [Fintype R] [DecidableEq R]
    (A : BinaryMatrix R C) (c : C) : Nat :=
  #(columnSupport A c)

/-- The total number of ones in a matrix. -/
def edgeCount {R C : Type*} [Fintype R] [DecidableEq R]
    [Fintype C] [DecidableEq C] (A : BinaryMatrix R C) : Nat :=
  ∑ c, columnDegree A c

/-- All unordered triples of rows. -/
def rowTriples (R : Type*) [Fintype R] [DecidableEq R] : Finset (Finset R) :=
  Finset.univ.powersetCard 3

/-- The number of columns containing every row of `T`. -/
def tripleLoad {R C : Type*} [Fintype R] [DecidableEq R]
    [Fintype C] [DecidableEq C] (A : BinaryMatrix R C) (T : Finset R) : Nat :=
  #(Finset.univ.filter fun c => T ⊆ columnSupport A c)

/-- Number of columns simultaneously occupied by three named rows. -/
def commonColumnCount {R C : Type*} [Fintype C] [DecidableEq C]
    (A : BinaryMatrix R C) (a b c : R) : Nat :=
  #(Finset.univ.filter fun j =>
      A a j = true ∧ A b j = true ∧ A c j = true)

/-- A matrix is `K_{3,3}`-free when each increasing row triple occurs in at
most two columns.  Using increasing triples avoids sixfold work in concrete
kernel evaluation while expressing exactly the usual forbidden-submatrix
condition. -/
def K33Free {R C : Type*} [LinearOrder R]
    [Fintype C] [DecidableEq C] (A : BinaryMatrix R C) : Prop :=
  ∀ a b c : R, a < b → b < c → commonColumnCount A a b c ≤ 2

/-- There is a `K_{3,3}`-free matrix with at least `e` ones. -/
def LowerBound (m n e : Nat) : Prop :=
  ∃ A : BinaryMatrix (Fin m) (Fin n), K33Free A ∧ e ≤ edgeCount A

/-- Every `K_{3,3}`-free matrix of the indicated dimensions has at most `e` ones. -/
def UpperBound (m n e : Nat) : Prop :=
  ∀ A : BinaryMatrix (Fin m) (Fin n), K33Free A → edgeCount A ≤ e

/-- The exact finite Zarankiewicz assertion `Z(m,n,3,3)=e`. -/
def Exact (m n e : Nat) : Prop := LowerBound m n e ∧ UpperBound m n e

/-- Decode a list of column bitmasks into a matrix.  Extra or missing masks are
read as zero; each concrete witness separately proves its dimensions and weight. -/
def ofColumnMasks (m n : Nat) (masks : List Nat) : BinaryMatrix (Fin m) (Fin n) :=
  fun r c => (masks.getD c.val 0).testBit r.val

end Zarankiewicz
