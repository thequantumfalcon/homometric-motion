module

public import GaussianChargeApplication

@[expose] public section

open MeasureTheory ProbabilityTheory Matrix
open scoped RealInnerProductSpace ComplexConjugate

namespace HomometricMotion

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

def integer_charge {r : ℕ} (p : Fin r → (ι × ι)) : ι → ℤ :=
  ∑ k, (Pi.single (p k).1 (1 : ℤ) - Pi.single (p k).2 (1 : ℤ))

noncomputable def charge_vector (u : ι → ℤ) : EuclideanSpace ℝ ι :=
  WithLp.toLp 2 (fun i => (u i : ℝ))

noncomputable def charge_support (r : ℕ) : Finset (ι → ℤ) := by
  classical
  exact Finset.univ.image (integer_charge (ι := ι) (r := r))

noncomputable def charge_multiplicity (r : ℕ) (u : ι → ℤ) : ℕ := by
  classical
  exact (Finset.univ.filter (fun p : Fin r → (ι × ι) => integer_charge p = u)).card

omit [Fintype ι] in
theorem charge_vector_of_tuple {r : ℕ} (p : Fin r → (ι × ι)) :
    charge_vector (integer_charge p) = moment_charge p := by
  ext i
  simp only [charge_vector, integer_charge, moment_charge, PiLp.toLp_apply,
    WithLp.ofLp_sum, Finset.sum_apply, Pi.sub_apply, Int.cast_sum, Int.cast_sub,
    PiLp.sub_apply, PiLp.single_apply, Pi.single_apply]
  apply Finset.sum_congr rfl
  intro k hk
  split_ifs <;> norm_num

theorem integer_charge_total_zero {r : ℕ} (p : Fin r → (ι × ι)) :
    ∑ i, integer_charge p i = 0 := by
  have h := moment_charge_total_zero p
  rw [← charge_vector_of_tuple] at h
  have h' : (∑ i, (integer_charge p i : ℝ)) = 0 := by
    simpa [charge_vector] using h
  exact_mod_cast h'

theorem charge_histogram_sum (r : ℕ) (f : (ι → ℤ) → ℝ) :
    (∑ p : Fin r → (ι × ι), f (integer_charge p)) =
      ∑ u ∈ charge_support r, (charge_multiplicity r u : ℝ) * f u := by
  classical
  have h := Finset.sum_fiberwise_of_maps_to'
    (s := (Finset.univ : Finset (Fin r → (ι × ι))))
    (t := charge_support (ι := ι) r) (g := integer_charge)
    (fun p hp => Finset.mem_image.mpr ⟨p, hp, rfl⟩) f
  simpa [charge_multiplicity, nsmul_eq_mul] using h.symm

theorem charge_histogram_mass (r : ℕ) :
    (∑ u ∈ charge_support (ι := ι) r, (charge_multiplicity r u : ℝ)) =
      (Fintype.card ι : ℝ) ^ (2 * r) := by
  have h := charge_histogram_sum (ι := ι) r (fun _ => (1 : ℝ))
  simpa [Fintype.card_fun, Fintype.card_prod, ← pow_two, pow_mul] using h.symm

theorem finite_physical_gaussian_intensity_histogram
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef)
    (x : EuclideanSpace ℝ ι) (ω β : ℝ) (hβ : 0 ≤ β) (r : ℕ) :
    (∫ y : EuclideanSpace ℝ ι,
      (‖∑ i, Complex.exp (((ω * (x i + Real.sqrt β * y i) : ℝ) : ℂ) *
        Complex.I)‖ ^ 2) ^ r ∂(multivariateGaussian 0 D)) =
      ∑ u ∈ charge_support r, (charge_multiplicity r u : ℝ) *
        (Real.cos (ω * ⟪x, charge_vector u⟫) *
        Real.exp (-(β * ω ^ 2 / 2) * (charge_vector u ⬝ᵥ D *ᵥ charge_vector u))) := by
  rw [finite_physical_gaussian_intensity_moment D hD x ω β hβ r]
  simpa only [charge_vector_of_tuple] using
    charge_histogram_sum r (fun u =>
      Real.cos (ω * ⟪x, charge_vector u⟫) *
      Real.exp (-(β * ω ^ 2 / 2) * (charge_vector u ⬝ᵥ D *ᵥ charge_vector u)))

end HomometricMotion

#print axioms HomometricMotion.charge_vector_of_tuple
#print axioms HomometricMotion.integer_charge_total_zero
#print axioms HomometricMotion.charge_histogram_sum
#print axioms HomometricMotion.charge_histogram_mass
#print axioms HomometricMotion.finite_physical_gaussian_intensity_histogram
