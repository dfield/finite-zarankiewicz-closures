import Zarankiewicz.Deletion
import Zarankiewicz.Witnesses

/-!
# Conditional pure-Lean deletion closures

The new witnesses and every averaging/deletion step are formalized here.
The historical starting bounds `Z(9,21) ≤ 96` and `Z(11,18) ≤ 101`, and the
externally certified bound `Z(10,23) ≤ 112`, remain explicit hypotheses. They
cannot honestly be erased from a certificate-free theorem statement.
-/

namespace Zarankiewicz.Exact.DeletionClosures

open Zarankiewicz

/-- The `Z(10,21)=106` closure, conditional only on its historical starting
upper bound. -/
theorem z10_21_upper_bound (hbase : UpperBound 9 21 96) :
    UpperBound 10 21 106 :=
  hbase.addRow_of_average (k := 10) (by omega)

theorem z10_21_exact (hbase : UpperBound 9 21 96) :
    Zarankiewicz.Exact 10 21 106 :=
  ⟨Zarankiewicz.Witnesses.z10_21_lower, z10_21_upper_bound hbase⟩

/-- The `Z(11,19)=106` closure, conditional only on its historical starting
upper bound. -/
theorem z11_19_upper_bound (hbase : UpperBound 11 18 101) :
    UpperBound 11 19 106 :=
  hbase.addColumn_of_average (k := 5) (by omega)

theorem z11_19_exact (hbase : UpperBound 11 18 101) :
    Zarankiewicz.Exact 11 19 106 :=
  ⟨Zarankiewicz.Witnesses.z11_19_lower, z11_19_upper_bound hbase⟩

/-- A second formal column-deletion step closes `Z(11,20)=111` from the same
historical `11 × 18` premise. -/
theorem z11_20_upper_bound (hbase : UpperBound 11 18 101) :
    UpperBound 11 20 111 := by
  have h19 : UpperBound 11 19 106 := z11_19_upper_bound hbase
  exact h19.addColumn_of_average (k := 5) (by omega)

theorem z11_20_exact (hbase : UpperBound 11 18 101) :
    Zarankiewicz.Exact 11 20 111 :=
  ⟨Zarankiewicz.Witnesses.z11_20_lower, z11_20_upper_bound hbase⟩

/-! The final two witnesses are kernel-checked here, while the computational
`Z(10,23)` upper bound remains a visible theorem parameter. -/

theorem z10_23_exact_of_upper (hupper : UpperBound 10 23 112) :
    Zarankiewicz.Exact 10 23 112 :=
  ⟨Zarankiewicz.Witnesses.z10_23_lower, hupper⟩

theorem z11_23_upper_bound (hbase : UpperBound 10 23 112) :
    UpperBound 11 23 123 :=
  hbase.addRow_of_average (k := 11) (by omega)

theorem z11_23_exact (hbase : UpperBound 10 23 112) :
    Zarankiewicz.Exact 11 23 123 :=
  ⟨Zarankiewicz.Witnesses.z11_23_lower, z11_23_upper_bound hbase⟩

end Zarankiewicz.Exact.DeletionClosures
