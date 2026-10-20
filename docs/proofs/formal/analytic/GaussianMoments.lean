import GaussianIntensity

open MeasureTheory ProbabilityTheory Matrix
open scoped RealInnerProductSpace ComplexConjugate

namespace HomometricMotion

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

noncomputable def moment_charge {r : ℕ} (p : Fin r → (ι × ι)) : EuclideanSpace ℝ ι :=
  ∑ k, (EuclideanSpace.single (p k).1 (1 : ℝ) -
    EuclideanSpace.single (p k).2 (1 : ℝ))

def moment_weight {r : ℕ} (z : ι → ℂ) (p : Fin r → (ι × ι)) : ℂ :=
  ∏ k, z (p k).1 * conj (z (p k).2)

theorem inner_moment_charge {r : ℕ}
    (y : EuclideanSpace ℝ ι) (p : Fin r → (ι × ι)) :
    ⟪y, moment_charge p⟫ = ∑ k, (y (p k).1 - y (p k).2) := by
  simp [moment_charge, inner_sum, inner_sub_right, EuclideanSpace.inner_single_right]

theorem tuple_phase_product {r : ℕ}
    (a : ℝ) (y : EuclideanSpace ℝ ι) (p : Fin r → (ι × ι)) :
    (∏ k, Complex.exp (((a * (y (p k).1 - y (p k).2) : ℝ) : ℂ) * Complex.I)) =
      Complex.exp (((a * ⟪y, moment_charge p⟫ : ℝ) : ℂ) * Complex.I) := by
  rw [← Complex.exp_sum]
  congr 1
  simp only [inner_moment_charge, Finset.mul_sum, Complex.ofReal_sum, Finset.sum_mul]

theorem finite_intensity_power_expansion
    (z : ι → ℂ) (a : ℝ) (r : ℕ) (y : EuclideanSpace ℝ ι) :
    (((‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2) ^ r : ℝ) : ℂ) =
    ∑ p : Fin r → (ι × ι), moment_weight z p *
      Complex.exp (((a * ⟪y, moment_charge p⟫ : ℝ) : ℂ) * Complex.I) := by
  rw [Complex.ofReal_pow, finite_intensity_expansion]
  rw [← Fintype.sum_prod_type']
  rw [Fintype.sum_pow]
  apply Finset.sum_congr rfl
  intro p hp
  rw [Finset.prod_mul_distrib, tuple_phase_product]
  rfl

theorem tuple_intensity_integrable {r : ℕ}
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (z : ι → ℂ) (a : ℝ) (p : Fin r → (ι × ι)) :
    Integrable (fun y : EuclideanSpace ℝ ι => moment_weight z p *
      Complex.exp (((a * ⟪y, moment_charge p⟫ : ℝ) : ℂ) * Complex.I)) μ := by
  apply Integrable.const_mul
  exact continuous_phase_integrable μ
    (fun y => a * ⟪y, moment_charge p⟫) (by fun_prop)

theorem finite_intensity_power_complex_integrable
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (z : ι → ℂ) (a : ℝ) (r : ℕ) :
    Integrable (fun y : EuclideanSpace ℝ ι =>
      (((‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2) ^ r : ℝ) : ℂ)) μ := by
  have hs := integrable_finsetSum Finset.univ
    (fun p hp => tuple_intensity_integrable μ z a (p : Fin r → (ι × ι)))
  exact hs.congr (Filter.Eventually.of_forall
    (fun y => (finite_intensity_power_expansion z a r y).symm))

theorem finite_intensity_power_integrable
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (z : ι → ℂ) (a : ℝ) (r : ℕ) :
    Integrable (fun y : EuclideanSpace ℝ ι =>
      (‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2) ^ r) μ := by
  simpa only [RCLike.re_to_complex, Complex.ofReal_re] using
    (finite_intensity_power_complex_integrable μ z a r).re

theorem gaussian_tuple_phase {r : ℕ}
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef) (a : ℝ) (p : Fin r → (ι × ι)) :
    (∫ y : EuclideanSpace ℝ ι,
      Complex.exp (((a * ⟪y, moment_charge p⟫ : ℝ) : ℂ) * Complex.I)
      ∂(multivariateGaussian 0 D)) =
    (Real.exp (-(a ^ 2 * (moment_charge p ⬝ᵥ D *ᵥ moment_charge p)) / 2) : ℂ) := by
  simpa [Complex.ofReal_exp] using centered_gaussian_linear_phase D hD (moment_charge p) a

theorem finite_gaussian_intensity_complex_moment
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef)
    (z : ι → ℂ) (a : ℝ) (r : ℕ) :
    (∫ y : EuclideanSpace ℝ ι,
      (((‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2) ^ r : ℝ) : ℂ)
      ∂(multivariateGaussian 0 D)) =
    ∑ p : Fin r → (ι × ι), moment_weight z p *
      (Real.exp (-(a ^ 2 * (moment_charge p ⬝ᵥ D *ᵥ moment_charge p)) / 2) : ℂ) := by
  let μ := multivariateGaussian (0 : EuclideanSpace ℝ ι) D
  calc
    _ = ∫ y, ∑ p : Fin r → (ι × ι), moment_weight z p *
      Complex.exp (((a * ⟪y, moment_charge p⟫ : ℝ) : ℂ) * Complex.I) ∂μ := by
      apply integral_congr_ae
      exact Filter.Eventually.of_forall (finite_intensity_power_expansion z a r)
    _ = ∑ p : Fin r → (ι × ι), ∫ y, moment_weight z p *
      Complex.exp (((a * ⟪y, moment_charge p⟫ : ℝ) : ℂ) * Complex.I) ∂μ := by
      exact integral_finsetSum Finset.univ (fun p hp => tuple_intensity_integrable μ z a p)
    _ = _ := by
      apply Finset.sum_congr rfl
      intro p hp
      rw [integral_const_mul, gaussian_tuple_phase D hD a p]

theorem finite_gaussian_intensity_moment
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef)
    (z : ι → ℂ) (a : ℝ) (r : ℕ) :
    (∫ y : EuclideanSpace ℝ ι,
      (‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2) ^ r
      ∂(multivariateGaussian 0 D)) =
    ∑ p : Fin r → (ι × ι), (moment_weight z p).re *
      Real.exp (-(a ^ 2 * (moment_charge p ⬝ᵥ D *ᵥ moment_charge p)) / 2) := by
  have h := congrArg Complex.re (finite_gaussian_intensity_complex_moment D hD z a r)
  rw [integral_complex_ofReal] at h
  simpa only [Complex.re_sum, Complex.ofReal_re, Complex.mul_re,
    Complex.ofReal_im, mul_zero, sub_zero] using h

end HomometricMotion

#print axioms HomometricMotion.inner_moment_charge
#print axioms HomometricMotion.tuple_phase_product
#print axioms HomometricMotion.finite_intensity_power_expansion
#print axioms HomometricMotion.tuple_intensity_integrable
#print axioms HomometricMotion.finite_intensity_power_complex_integrable
#print axioms HomometricMotion.finite_intensity_power_integrable
#print axioms HomometricMotion.gaussian_tuple_phase
#print axioms HomometricMotion.finite_gaussian_intensity_complex_moment
#print axioms HomometricMotion.finite_gaussian_intensity_moment
