import GaussianMoments

open MeasureTheory ProbabilityTheory Matrix
open scoped RealInnerProductSpace ComplexConjugate

namespace HomometricMotion

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

noncomputable def nominal_phase (x : EuclideanSpace ℝ ι) (ω : ℝ) (i : ι) : ℂ :=
  Complex.exp (((ω * x i : ℝ) : ℂ) * Complex.I)

theorem moment_charge_total_zero {r : ℕ} (p : Fin r → (ι × ι)) :
    ∑ i, moment_charge p i = 0 := by
  have h := inner_moment_charge (WithLp.toLp 2 (fun _ : ι => (1 : ℝ))) p
  simpa [PiLp.inner_apply] using h

theorem nominal_moment_weight {r : ℕ}
    (x : EuclideanSpace ℝ ι) (ω : ℝ) (p : Fin r → (ι × ι)) :
    moment_weight (nominal_phase x ω) p =
      Complex.exp (((ω * ⟪x, moment_charge p⟫ : ℝ) : ℂ) * Complex.I) := by
  unfold moment_weight nominal_phase
  calc
    _ = ∏ k, Complex.exp (((ω * (x (p k).1 - x (p k).2) : ℝ) : ℂ) *
        Complex.I) := by
      apply Finset.prod_congr rfl
      intro k hk
      rw [phase_mul_conj]
      simp only [mul_sub]
    _ = _ := tuple_phase_product ω x p

theorem nominal_moment_weight_real {r : ℕ}
    (x : EuclideanSpace ℝ ι) (ω : ℝ) (p : Fin r → (ι × ι)) :
    (moment_weight (nominal_phase x ω) p).re = Real.cos (ω * ⟪x, moment_charge p⟫) := by
  rw [nominal_moment_weight, Complex.exp_re]
  simp

theorem physical_amplitude_factorization
    (x y : EuclideanSpace ℝ ι) (ω β : ℝ) :
    (∑ i, Complex.exp (((ω * (x i + Real.sqrt β * y i) : ℝ) : ℂ) * Complex.I)) =
      ∑ i, nominal_phase x ω i *
        Complex.exp ((((ω * Real.sqrt β) * y i : ℝ) : ℂ) * Complex.I) := by
  apply Finset.sum_congr rfl
  intro i hi
  unfold nominal_phase
  rw [← Complex.exp_add]
  congr 1
  push_cast
  ring

theorem physical_strength_exponent (ω β : ℝ) (hβ : 0 ≤ β) (q : ℝ) :
    -((ω * Real.sqrt β) ^ 2 * q) / 2 = -(β * ω ^ 2 / 2) * q := by
  rw [mul_pow, Real.sq_sqrt hβ]
  ring

theorem physical_intensity_power_integrable
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (x : EuclideanSpace ℝ ι) (ω β : ℝ) (r : ℕ) :
    Integrable (fun y : EuclideanSpace ℝ ι =>
      (‖∑ i, Complex.exp (((ω * (x i + Real.sqrt β * y i) : ℝ) : ℂ) *
        Complex.I)‖ ^ 2) ^ r) μ := by
  simp_rw [physical_amplitude_factorization]
  exact finite_intensity_power_integrable μ (nominal_phase x ω) (ω * Real.sqrt β) r

theorem finite_physical_gaussian_intensity_moment
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef)
    (x : EuclideanSpace ℝ ι) (ω β : ℝ) (hβ : 0 ≤ β) (r : ℕ) :
    (∫ y : EuclideanSpace ℝ ι,
      (‖∑ i, Complex.exp (((ω * (x i + Real.sqrt β * y i) : ℝ) : ℂ) *
        Complex.I)‖ ^ 2) ^ r ∂(multivariateGaussian 0 D)) =
    ∑ p : Fin r → (ι × ι), Real.cos (ω * ⟪x, moment_charge p⟫) *
      Real.exp (-(β * ω ^ 2 / 2) * (moment_charge p ⬝ᵥ D *ᵥ moment_charge p)) := by
  simp_rw [physical_amplitude_factorization]
  rw [finite_gaussian_intensity_moment D hD (nominal_phase x ω) (ω * Real.sqrt β) r]
  apply Finset.sum_congr rfl
  intro p hp
  rw [nominal_moment_weight_real, physical_strength_exponent ω β hβ]

end HomometricMotion

#print axioms HomometricMotion.moment_charge_total_zero
#print axioms HomometricMotion.nominal_moment_weight
#print axioms HomometricMotion.nominal_moment_weight_real
#print axioms HomometricMotion.physical_amplitude_factorization
#print axioms HomometricMotion.physical_strength_exponent
#print axioms HomometricMotion.physical_intensity_power_integrable
#print axioms HomometricMotion.finite_physical_gaussian_intensity_moment
