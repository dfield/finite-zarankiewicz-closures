import Zarankiewicz.PairCounting

/-!
# Three-column incidence budgets

The stronger incidence lemmas used by the `Z(12,23)` row-type argument live
separately from the pair-deficit core so unrelated exact-value modules rebuild
quickly.
-/

namespace Zarankiewicz

open scoped BigOperators
open Finset

variable {R C : Type*} [Fintype R] [LinearOrder R]
  [Fintype C] [DecidableEq C]

/-- Three distinct columns of a `K_{3,3}`-free matrix have at most two common
rows. -/
def commonRowCount (A : BinaryMatrix R C) (a b c : C) : Nat :=
  #(Finset.univ.filter fun r =>
      A r a = true ∧ A r b = true ∧ A r c = true)

theorem commonRowCount_le_two (A : BinaryMatrix R C) (hA : K33Free A)
    (a b c : C) (hab : a ≠ b) (hac : a ≠ c) (hbc : b ≠ c) :
    commonRowCount A a b c ≤ 2 := by
  by_contra hnot
  have hthree : 3 ≤ commonRowCount A a b c := by omega
  let S : Finset R := Finset.univ.filter fun r =>
    A r a = true ∧ A r b = true ∧ A r c = true
  have hScard : 3 ≤ #S := by simpa [S, commonRowCount] using hthree
  obtain ⟨T, hTmem⟩ := powersetCard_nonempty.2 hScard
  have ⟨hTsub, hTcard⟩ := mem_powersetCard.1 hTmem
  have hTrow : T ∈ rowTriples R := by
    simp [rowTriples, hTcard]
  have hload := tripleLoad_le_two A hA T hTrow
  have hcols : ({a, b, c} : Finset C) ⊆
      Finset.univ.filter (fun j => T ⊆ columnSupport A j) := by
    rw [insert_subset_iff, insert_subset_iff, singleton_subset_iff]
    constructor
    · simp only [mem_filter, mem_univ, true_and]
      intro r hr
      have hrS := hTsub hr
      simpa [S, columnSupport] using (mem_filter.1 hrS).2.1
    constructor
    · simp only [mem_filter, mem_univ, true_and]
      intro r hr
      have hrS := hTsub hr
      simpa [S, columnSupport] using (mem_filter.1 hrS).2.2.1
    · simp only [mem_filter, mem_univ, true_and]
      intro r hr
      have hrS := hTsub hr
      simpa [S, columnSupport] using (mem_filter.1 hrS).2.2.2
  have hsetcard : #({a, b, c} : Finset C) = 3 := by
    simp [hab, hac, hbc]
  have hle := card_le_card hcols
  simp only [tripleLoad] at hload
  omega

/-- Number of row pairs simultaneously contained in three columns. -/
def commonPairCount (A : BinaryMatrix R C) (a b c : C) : Nat :=
  #((rowPairs R).filter fun P =>
      P ⊆ columnSupport A a ∧ P ⊆ columnSupport A b ∧
        P ⊆ columnSupport A c)

/-- Three distinct columns of a `K_{3,3}`-free matrix have at most one common
row pair. -/
theorem commonPairCount_le_one (A : BinaryMatrix R C) (hA : K33Free A)
    (a b c : C) (hab : a ≠ b) (hac : a ≠ c) (hbc : b ≠ c) :
    commonPairCount A a b c ≤ 1 := by
  let S : Finset R := Finset.univ.filter fun r =>
    A r a = true ∧ A r b = true ∧ A r c = true
  have hScard : #S ≤ 2 := by
    simpa [S, commonRowCount] using
      commonRowCount_le_two A hA a b c hab hac hbc
  have hfilter : (rowPairs R).filter (fun P =>
      P ⊆ columnSupport A a ∧ P ⊆ columnSupport A b ∧
        P ⊆ columnSupport A c) = S.powersetCard 2 := by
    ext P
    simp only [mem_filter, mem_powersetCard]
    constructor
    · rintro ⟨hP, hPa, hPb, hPc⟩
      refine ⟨?_, (mem_powersetCard.1 hP).2⟩
      intro r hr
      simp only [S, mem_filter, mem_univ, true_and]
      exact ⟨by simpa [columnSupport] using hPa hr,
        by simpa [columnSupport] using hPb hr,
        by simpa [columnSupport] using hPc hr⟩
    · rintro ⟨hPS, hPcard⟩
      have hP : P ∈ rowPairs R := by
        simp [rowPairs, hPcard]
      refine ⟨hP, ?_, ?_, ?_⟩
      · intro r hr
        have hrS := hPS hr
        simpa [S, columnSupport] using (mem_filter.1 hrS).2.1
      · intro r hr
        have hrS := hPS hr
        simpa [S, columnSupport] using (mem_filter.1 hrS).2.2.1
      · intro r hr
        have hrS := hPS hr
        simpa [S, columnSupport] using (mem_filter.1 hrS).2.2.2
  unfold commonPairCount
  rw [hfilter, card_powersetCard]
  have hcases : #S = 0 ∨ #S = 1 ∨ #S = 2 := by omega
  rcases hcases with hzero | hone | htwo
  · simp [hzero]
  · simp [hone]
  · simp [htwo]

/-- Three-column incidences through row pairs inside one column-degree class. -/
theorem sum_choose_pairColumnDegreeCount_le
    (A : BinaryMatrix R C) (hA : K33Free A) (d : Nat) :
    (∑ P ∈ rowPairs R, Nat.choose (pairColumnDegreeCount A P d) 3) ≤
      Nat.choose (degreeCount A d) 3 := by
  let F : Finset C := Finset.univ.filter fun c => columnDegree A c = d
  let G : Finset R → Finset C := fun P =>
    F.filter fun c => P ⊆ columnSupport A c
  have hGcard : ∀ P, #(G P) = pairColumnDegreeCount A P d := by
    intro P
    unfold G F pairColumnDegreeCount
    rw [filter_filter]
  calc
    (∑ P ∈ rowPairs R, Nat.choose (pairColumnDegreeCount A P d) 3) =
        ∑ P ∈ rowPairs R, #((G P).powersetCard 3) := by
          apply sum_congr rfl
          intro P hP
          rw [card_powersetCard, hGcard]
    _ = ∑ P ∈ rowPairs R,
          ∑ Q ∈ F.powersetCard 3, if Q ⊆ G P then 1 else 0 := by
          apply sum_congr rfl
          intro P hP
          rw [← card_filter_eq_sum_indicator]
          congr 1
          ext Q
          simp only [mem_filter, mem_powersetCard]
          constructor
          · rintro ⟨hQG, hQcard⟩
            exact ⟨⟨fun c hc => (mem_filter.1 (hQG hc)).1, hQcard⟩, hQG⟩
          · rintro ⟨⟨_hQF, hQcard⟩, hQG⟩
            exact ⟨hQG, hQcard⟩
    _ = ∑ Q ∈ F.powersetCard 3,
          ∑ P ∈ rowPairs R, if Q ⊆ G P then 1 else 0 := by
          rw [Finset.sum_comm]
    _ ≤ ∑ _Q ∈ F.powersetCard 3, 1 := by
          apply sum_le_sum
          intro Q hQ
          have hQcard : #Q = 3 := (mem_powersetCard.1 hQ).2
          obtain ⟨a, b, c, hab, hac, hbc, hQeq⟩ := card_eq_three.1 hQcard
          have haF : a ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hbF : b ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hcF : c ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hinner : (∑ P ∈ rowPairs R, if Q ⊆ G P then 1 else 0) =
              commonPairCount A a b c := by
            rw [← card_filter_eq_sum_indicator]
            unfold commonPairCount
            congr 1
            ext P
            rw [hQeq]
            simp only [mem_filter]
            rw [insert_subset_iff, insert_subset_iff, singleton_subset_iff]
            simp [G, haF, hbF, hcF, and_assoc, and_left_comm, and_comm]
          rw [hinner]
          exact commonPairCount_le_one A hA a b c hab hac hbc
    _ = Nat.choose (degreeCount A d) 3 := by
          rw [sum_const_nat (m := 1) (fun _ _ => rfl), card_powersetCard]
          simp [F, degreeCount]

/-- Mixed three-column incidences through row pairs: two columns from one
degree class and one from a distinct class. -/
theorem sum_choose_two_mul_pairColumnDegreeCount_le
    (A : BinaryMatrix R C) (hA : K33Free A) (d e : Nat) (hde : d ≠ e) :
    (∑ P ∈ rowPairs R, Nat.choose (pairColumnDegreeCount A P d) 2 *
        pairColumnDegreeCount A P e) ≤
      Nat.choose (degreeCount A d) 2 * degreeCount A e := by
  let F : Finset C := Finset.univ.filter fun c => columnDegree A c = d
  let H : Finset C := Finset.univ.filter fun c => columnDegree A c = e
  let G : Finset R → Finset C := fun P =>
    F.filter fun c => P ⊆ columnSupport A c
  let J : Finset R → Finset C := fun P =>
    H.filter fun c => P ⊆ columnSupport A c
  let X : Finset (Finset C × C) := (F.powersetCard 2).product H
  have hGcard : ∀ P, #(G P) = pairColumnDegreeCount A P d := by
    intro P
    unfold G F pairColumnDegreeCount
    rw [filter_filter]
  have hJcard : ∀ P, #(J P) = pairColumnDegreeCount A P e := by
    intro P
    unfold J H pairColumnDegreeCount
    rw [filter_filter]
  calc
    (∑ P ∈ rowPairs R, Nat.choose (pairColumnDegreeCount A P d) 2 *
        pairColumnDegreeCount A P e) =
        ∑ P ∈ rowPairs R, #((G P).powersetCard 2) * #(J P) := by
          apply sum_congr rfl
          intro P hP
          rw [card_powersetCard, hGcard, hJcard]
    _ = ∑ P ∈ rowPairs R, #(((G P).powersetCard 2).product (J P)) := by
          simp
    _ = ∑ P ∈ rowPairs R,
          #(X.filter fun x => x.1 ⊆ G P ∧ x.2 ∈ J P) := by
          apply sum_congr rfl
          intro P hP
          congr 1
          ext x
          rcases x with ⟨Q, c⟩
          simp [X, G, J]
          constructor
          · rintro ⟨⟨hQG, hQcard⟩, hcH, hcJ⟩
            exact ⟨⟨⟨fun a ha => (mem_filter.1 (hQG ha)).1, hQcard⟩,
              hcH⟩, hQG, hcH, hcJ⟩
          · rintro ⟨⟨⟨_hQF, hQcard⟩, hcH⟩, hQG, _hcH, hcJ⟩
            exact ⟨⟨hQG, hQcard⟩, hcH, hcJ⟩
    _ = ∑ P ∈ rowPairs R, ∑ x ∈ X,
          if x.1 ⊆ G P ∧ x.2 ∈ J P then 1 else 0 := by
          apply sum_congr rfl
          intro P hP
          exact card_filter_eq_sum_indicator _ _
    _ = ∑ x ∈ X, ∑ P ∈ rowPairs R,
          if x.1 ⊆ G P ∧ x.2 ∈ J P then 1 else 0 := by
          rw [Finset.sum_comm]
    _ ≤ ∑ _x ∈ X, 1 := by
          apply sum_le_sum
          rintro ⟨Q, c⟩ hx
          have hQ : Q ∈ F.powersetCard 2 := (mem_product.1 hx).1
          have hcH : c ∈ H := (mem_product.1 hx).2
          have hQcard : #Q = 2 := (mem_powersetCard.1 hQ).2
          obtain ⟨a, b, hab, hQeq⟩ := card_eq_two.1 hQcard
          have haF : a ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hbF : b ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hadeg : columnDegree A a = d := (mem_filter.1 haF).2
          have hbdeg : columnDegree A b = d := (mem_filter.1 hbF).2
          have hcdeg : columnDegree A c = e := (mem_filter.1 hcH).2
          have hac : a ≠ c := by
            intro heq
            subst c
            exact hde (hadeg.symm.trans hcdeg)
          have hbc : b ≠ c := by
            intro heq
            subst c
            exact hde (hbdeg.symm.trans hcdeg)
          have hinner : (∑ P ∈ rowPairs R,
              if Q ⊆ G P ∧ c ∈ J P then 1 else 0) =
              commonPairCount A a b c := by
            rw [← card_filter_eq_sum_indicator]
            unfold commonPairCount
            congr 1
            ext P
            rw [hQeq]
            simp only [mem_filter]
            rw [insert_subset_iff, singleton_subset_iff]
            simp [G, J, haF, hbF, hcH, and_assoc, and_left_comm, and_comm]
          rw [hinner]
          exact commonPairCount_le_one A hA a b c hab hac hbc
    _ = Nat.choose (degreeCount A d) 2 * degreeCount A e := by
          rw [sum_const_nat (m := 1) (fun _ _ => rfl)]
          simp [X, F, H, degreeCount, card_powersetCard, Nat.mul_comm]

/-- Three-column incidences inside one column-degree class. -/
theorem sum_choose_rowColumnDegreeCount_le
    (A : BinaryMatrix R C) (hA : K33Free A) (d : Nat) :
    (∑ r, Nat.choose (rowColumnDegreeCount A r d) 3) ≤
      2 * Nat.choose (degreeCount A d) 3 := by
  let F : Finset C := Finset.univ.filter fun c => columnDegree A c = d
  let G : R → Finset C := fun r => F.filter fun c => A r c = true
  have hGcard : ∀ r, #(G r) = rowColumnDegreeCount A r d := by
    intro r
    unfold G F rowColumnDegreeCount
    rw [filter_filter]
  calc
    (∑ r, Nat.choose (rowColumnDegreeCount A r d) 3) =
        ∑ r, #((G r).powersetCard 3) := by
          apply sum_congr rfl
          intro r hr
          rw [card_powersetCard, hGcard]
    _ = ∑ r, ∑ Q ∈ F.powersetCard 3, if Q ⊆ G r then 1 else 0 := by
          apply sum_congr rfl
          intro r hr
          rw [← card_filter_eq_sum_indicator]
          congr 1
          ext Q
          simp only [mem_filter, mem_powersetCard]
          constructor
          · rintro ⟨hQG, hQcard⟩
            exact ⟨⟨fun c hc => (mem_filter.1 (hQG hc)).1, hQcard⟩, hQG⟩
          · rintro ⟨⟨_hQF, hQcard⟩, hQG⟩
            exact ⟨hQG, hQcard⟩
    _ = ∑ Q ∈ F.powersetCard 3, ∑ r, if Q ⊆ G r then 1 else 0 := by
          rw [Finset.sum_comm]
    _ ≤ ∑ Q ∈ F.powersetCard 3, 2 := by
          apply sum_le_sum
          intro Q hQ
          have hQcard : #Q = 3 := (mem_powersetCard.1 hQ).2
          obtain ⟨a, b, c, hab, hac, hbc, hQeq⟩ := card_eq_three.1 hQcard
          have haF : a ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hbF : b ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hcF : c ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hinner : (∑ r, if Q ⊆ G r then 1 else 0) =
              commonRowCount A a b c := by
            rw [← card_filter_eq_sum_indicator]
            unfold commonRowCount
            congr 1
            ext r
            rw [hQeq]
            simp only [mem_filter, mem_univ, true_and]
            rw [insert_subset_iff, insert_subset_iff, singleton_subset_iff]
            simp [G, haF, hbF, hcF]
          rw [hinner]
          exact commonRowCount_le_two A hA a b c hab hac hbc
    _ = 2 * Nat.choose (degreeCount A d) 3 := by
          rw [sum_const_nat (m := 2) (fun _ _ => rfl), card_powersetCard]
          simp [F, degreeCount, Nat.mul_comm]

/-- Mixed incidences of two columns from one degree class and one column from
a distinct degree class. -/
theorem sum_choose_two_mul_rowColumnDegreeCount_le
    (A : BinaryMatrix R C) (hA : K33Free A) (d e : Nat) (hde : d ≠ e) :
    (∑ r, Nat.choose (rowColumnDegreeCount A r d) 2 *
        rowColumnDegreeCount A r e) ≤
      2 * Nat.choose (degreeCount A d) 2 * degreeCount A e := by
  let F : Finset C := Finset.univ.filter fun c => columnDegree A c = d
  let H : Finset C := Finset.univ.filter fun c => columnDegree A c = e
  let G : R → Finset C := fun r => F.filter fun c => A r c = true
  let J : R → Finset C := fun r => H.filter fun c => A r c = true
  let X : Finset (Finset C × C) := (F.powersetCard 2).product H
  have hGcard : ∀ r, #(G r) = rowColumnDegreeCount A r d := by
    intro r
    unfold G F rowColumnDegreeCount
    rw [filter_filter]
  have hJcard : ∀ r, #(J r) = rowColumnDegreeCount A r e := by
    intro r
    unfold J H rowColumnDegreeCount
    rw [filter_filter]
  calc
    (∑ r, Nat.choose (rowColumnDegreeCount A r d) 2 *
        rowColumnDegreeCount A r e) =
        ∑ r, #((G r).powersetCard 2) * #(J r) := by
          apply sum_congr rfl
          intro r hr
          rw [card_powersetCard, hGcard, hJcard]
    _ = ∑ r, #(((G r).powersetCard 2).product (J r)) := by
          simp
    _ = ∑ r, #(X.filter fun x => x.1 ⊆ G r ∧ x.2 ∈ J r) := by
          apply sum_congr rfl
          intro r hr
          congr 1
          ext x
          rcases x with ⟨Q, c⟩
          simp [X, G, J]
          constructor
          · rintro ⟨⟨hQG, hQcard⟩, hcH, hrc⟩
            exact ⟨⟨⟨fun a ha => (mem_filter.1 (hQG ha)).1, hQcard⟩,
              hcH⟩, hQG, hcH, hrc⟩
          · rintro ⟨⟨⟨_hQF, hQcard⟩, hcH⟩, hQG, _hcH, hrc⟩
            exact ⟨⟨hQG, hQcard⟩, hcH, hrc⟩
    _ = ∑ r, ∑ x ∈ X, if x.1 ⊆ G r ∧ x.2 ∈ J r then 1 else 0 := by
          apply sum_congr rfl
          intro r hr
          exact card_filter_eq_sum_indicator _ _
    _ = ∑ x ∈ X, ∑ r, if x.1 ⊆ G r ∧ x.2 ∈ J r then 1 else 0 := by
          rw [Finset.sum_comm]
    _ ≤ ∑ _x ∈ X, 2 := by
          apply sum_le_sum
          rintro ⟨Q, c⟩ hx
          have hQ : Q ∈ F.powersetCard 2 := (mem_product.1 hx).1
          have hcH : c ∈ H := (mem_product.1 hx).2
          have hQcard : #Q = 2 := (mem_powersetCard.1 hQ).2
          obtain ⟨a, b, hab, hQeq⟩ := card_eq_two.1 hQcard
          have haF : a ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hbF : b ∈ F := (mem_powersetCard.1 hQ).1 (by simp [hQeq])
          have hadeg : columnDegree A a = d := (mem_filter.1 haF).2
          have hbdeg : columnDegree A b = d := (mem_filter.1 hbF).2
          have hcdeg : columnDegree A c = e := (mem_filter.1 hcH).2
          have hac : a ≠ c := by
            intro heq
            subst c
            exact hde (hadeg.symm.trans hcdeg)
          have hbc : b ≠ c := by
            intro heq
            subst c
            exact hde (hbdeg.symm.trans hcdeg)
          have hinner : (∑ r,
              if Q ⊆ G r ∧ c ∈ J r then 1 else 0) =
              commonRowCount A a b c := by
            rw [← card_filter_eq_sum_indicator]
            unfold commonRowCount
            congr 1
            ext r
            rw [hQeq]
            simp only [mem_filter, mem_univ, true_and]
            rw [insert_subset_iff, singleton_subset_iff]
            simp [G, J, haF, hbF, hcH, and_assoc, and_left_comm, and_comm]
          rw [hinner]
          exact commonRowCount_le_two A hA a b c hab hac hbc
    _ = 2 * Nat.choose (degreeCount A d) 2 * degreeCount A e := by
          rw [sum_const_nat (m := 2) (fun _ _ => rfl)]
          simp [X, F, H, degreeCount, card_powersetCard, Nat.mul_assoc,
            Nat.mul_comm, Nat.mul_left_comm]

end Zarankiewicz
