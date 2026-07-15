import Zarankiewicz.Basic

/-!
# Kernel-checked lower-bound witnesses

Each matrix is stored as one natural-number bitmask per column.  The proofs use
ordinary kernel reduction (`decide`), not `native_decide`, an external program,
or an imported certificate.
-/

namespace Zarankiewicz.Witnesses

open Zarankiewicz

def z9_23 : BinaryMatrix (Fin 9) (Fin 23) := ofColumnMasks 9 23
  [326, 308, 267, 360, 456, 185, 417, 94, 464, 197, 203, 109,
   151, 115, 295, 285, 244, 174, 396, 226, 337, 314, 402]

def z10_21 : BinaryMatrix (Fin 10) (Fin 21) := ofColumnMasks 10 21
  [27, 189, 214, 234, 310, 335, 376, 396, 419, 465, 558, 604,
   627, 647, 688, 713, 789, 809, 834, 922, 996]

def z10_22 : BinaryMatrix (Fin 10) (Fin 22) := ofColumnMasks 10 22
  [27, 189, 214, 234, 310, 335, 376, 396, 419, 465, 558, 604,
   627, 647, 688, 713, 789, 809, 834, 922, 996, 101]

def z10_23 : BinaryMatrix (Fin 10) (Fin 23) := ofColumnMasks 10 23
  [15, 113, 402, 676, 840, 803, 453, 665, 598, 234, 316, 707,
   789, 425, 358, 220, 183, 347, 621, 910, 538, 880, 688]

def z11_19 : BinaryMatrix (Fin 11) (Fin 19) := ofColumnMasks 11 19
  [1081, 1543, 1420, 810, 1872, 357, 94, 713, 966, 1334, 1237,
   797, 1690, 175, 1355, 1644, 627, 1953, 504]

def z11_20 : BinaryMatrix (Fin 11) (Fin 20) := ofColumnMasks 11 20
  [211, 252, 359, 426, 571, 590, 677, 880, 918, 969, 1129, 1167,
   1370, 1457, 1476, 1621, 1688, 1762, 1795, 1836]

def z11_23 : BinaryMatrix (Fin 11) (Fin 23) := ofColumnMasks 11 23
  [31, 227, 805, 1353, 1681, 1606, 906, 1330, 1196, 468, 632, 1415,
   1579, 851, 717, 441, 366, 694, 1242, 1820, 1077, 1760, 1376]

def z12_23 : BinaryMatrix (Fin 12) (Fin 23) := ofColumnMasks 12 23
  [63, 455, 1611, 2707, 3363, 3213, 1813, 2661, 2393, 937, 1265,
   2830, 3158, 1702, 1434, 882, 732, 1388, 2484, 3640, 2154, 3520,
   2752]

theorem z9_23_free : K33Free z9_23 := by
  unfold K33Free
  decide

theorem z9_23_weight : edgeCount z9_23 = 103 := by decide

theorem z10_21_free : K33Free z10_21 := by
  unfold K33Free
  decide

theorem z10_21_weight : edgeCount z10_21 = 106 := by decide

theorem z10_22_free : K33Free z10_22 := by
  unfold K33Free
  decide

theorem z10_22_weight : edgeCount z10_22 = 110 := by decide

theorem z10_23_free : K33Free z10_23 := by
  unfold K33Free
  decide

theorem z10_23_weight : edgeCount z10_23 = 112 := by decide

theorem z11_19_free : K33Free z11_19 := by
  unfold K33Free
  decide

theorem z11_19_weight : edgeCount z11_19 = 106 := by decide

theorem z11_20_free : K33Free z11_20 := by
  unfold K33Free
  decide

theorem z11_20_weight : edgeCount z11_20 = 111 := by decide

theorem z11_23_free : K33Free z11_23 := by
  unfold K33Free
  decide

theorem z11_23_weight : edgeCount z11_23 = 123 := by decide

theorem z12_23_free : K33Free z12_23 := by
  unfold K33Free
  decide

theorem z12_23_weight : edgeCount z12_23 = 134 := by decide

theorem z9_23_lower : LowerBound 9 23 103 :=
  ⟨z9_23, z9_23_free, z9_23_weight.ge⟩

theorem z10_21_lower : LowerBound 10 21 106 :=
  ⟨z10_21, z10_21_free, z10_21_weight.ge⟩

theorem z10_22_lower : LowerBound 10 22 110 :=
  ⟨z10_22, z10_22_free, z10_22_weight.ge⟩

theorem z10_23_lower : LowerBound 10 23 112 :=
  ⟨z10_23, z10_23_free, z10_23_weight.ge⟩

theorem z11_19_lower : LowerBound 11 19 106 :=
  ⟨z11_19, z11_19_free, z11_19_weight.ge⟩

theorem z11_20_lower : LowerBound 11 20 111 :=
  ⟨z11_20, z11_20_free, z11_20_weight.ge⟩

theorem z11_23_lower : LowerBound 11 23 123 :=
  ⟨z11_23, z11_23_free, z11_23_weight.ge⟩

theorem z12_23_lower : LowerBound 12 23 134 :=
  ⟨z12_23, z12_23_free, z12_23_weight.ge⟩

end Zarankiewicz.Witnesses
