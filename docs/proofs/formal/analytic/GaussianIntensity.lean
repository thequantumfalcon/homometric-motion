import Mathlib.Probability.Distributions.Gaussian.Multivariate
import Mathlib.Tactic.Ring

/- A generic Gaussian phase identity. Positive semidefiniteness is explicit;
   singular covariance is allowed. No graph-specific covariance or intensity
   moment expansion is asserted here. -/

open MeasureTheory ProbabilityTheory Matrix
open scoped RealInnerProductSpace

namespace HomometricMotion

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

theorem centered_gaussian_characteristic
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef) (u : EuclideanSpace ℝ ι) :
    (∫ y : EuclideanSpace ℝ ι,
      Complex.exp (((⟪y, u⟫ : ℝ) : ℂ) * Complex.I)
      ∂(multivariateGaussian 0 D)) =
      Complex.exp (-(((u ⬝ᵥ D *ᵥ u : ℝ) : ℂ)) / 2) := by
  simpa [MeasureTheory.charFun_apply, neg_div] using
    (ProbabilityTheory.charFun_multivariateGaussian (μ := 0) hD u)

omit [DecidableEq ι] in
theorem quadratic_form_smul
    (D : Matrix ι ι ℝ) (u : EuclideanSpace ℝ ι) (a : ℝ) :
    (a • u) ⬝ᵥ D *ᵥ (a • u) = a ^ 2 * (u ⬝ᵥ D *ᵥ u) := by
  classical
  change (∑ i, (a * u i) * (∑ j, D i j * (a * u j))) =
    a ^ 2 * (∑ i, u i * (∑ j, D i j * u j))
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i hi
  have hinner : (∑ j, D i j * (a * u j)) = a * (∑ j, D i j * u j) := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j hj
    ring
  rw [hinner]
  ring

theorem centered_gaussian_linear_phase
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef)
    (u : EuclideanSpace ℝ ι) (a : ℝ) :
    (∫ y : EuclideanSpace ℝ ι,
      Complex.exp ((((a * ⟪y, u⟫ : ℝ)) : ℂ) * Complex.I)
      ∂(multivariateGaussian 0 D)) =
      Complex.exp (-(((a ^ 2 * (u ⬝ᵥ D *ᵥ u) : ℝ) : ℂ)) / 2) := by
  have h := centered_gaussian_characteristic D hD (a • u)
  have hq := quadratic_form_smul D u a
  simp only [WithLp.ofLp_smul] at h hq
  rw [hq] at h
  simpa only [inner_smul_right, smul_eq_mul] using h

end HomometricMotion

#print axioms HomometricMotion.centered_gaussian_characteristic
#print axioms HomometricMotion.quadratic_form_smul
#print axioms HomometricMotion.centered_gaussian_linear_phase


open scoped ComplexConjugate

namespace HomometricMotion

variable {ι : Type*} [Fintype ι] [DecidableEq ι]

omit [DecidableEq ι] in
theorem continuous_phase_integrable
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (f : EuclideanSpace ℝ ι → ℝ) (hf : Continuous f) :
    Integrable (fun y => Complex.exp ((f y : ℂ) * Complex.I)) μ := by
  refine (integrable_const (1 : ℝ)).mono' ?_ ?_
  · have hc : Continuous (fun y => Complex.exp ((f y : ℂ) * Complex.I)) := by
      fun_prop
    exact hc.aestronglyMeasurable
  · exact Filter.Eventually.of_forall (fun y => by simp)

theorem phase_mul_conj (x y : ℝ) :
    Complex.exp ((x : ℂ) * Complex.I) *
      conj (Complex.exp ((y : ℂ) * Complex.I)) =
      Complex.exp (((x - y : ℝ) : ℂ) * Complex.I) := by
  rw [← Complex.exp_conj, ← Complex.exp_add]
  congr 1
  simp only [map_mul, Complex.conj_ofReal, Complex.conj_I, Complex.ofReal_sub]
  ring

omit [DecidableEq ι] in
theorem finite_intensity_expansion
    (z : ι → ℂ) (a : ℝ) (y : EuclideanSpace ℝ ι) :
    ((‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2 : ℝ) : ℂ) =
    ∑ i, ∑ j, (z i * conj (z j)) *
      Complex.exp (((a * (y i - y j) : ℝ) : ℂ) * Complex.I) := by
  rw [Complex.ofReal_pow, ← Complex.mul_conj']
  simp only [map_sum, map_mul]
  rw [Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i hi
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro j hj
  calc
    (z i * Complex.exp ((↑(a * y i)) * Complex.I)) *
        (conj (z j) * conj (Complex.exp ((↑(a * y j)) * Complex.I))) =
        (z i * conj (z j)) *
          (Complex.exp ((↑(a * y i)) * Complex.I) *
            conj (Complex.exp ((↑(a * y j)) * Complex.I))) := by ring
    _ = _ := by rw [phase_mul_conj, mul_sub]

omit [DecidableEq ι] in
theorem pair_intensity_integrable
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (z : ι → ℂ) (a : ℝ) (i j : ι) :
    Integrable (fun y : EuclideanSpace ℝ ι =>
      (z i * conj (z j)) *
        Complex.exp (((a * (y i - y j) : ℝ) : ℂ) * Complex.I)) μ := by
  apply Integrable.const_mul
  exact continuous_phase_integrable μ (fun y => a * (y i - y j)) (by fun_prop)

omit [DecidableEq ι] in
theorem finite_intensity_complex_integrable
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (z : ι → ℂ) (a : ℝ) :
    Integrable (fun y : EuclideanSpace ℝ ι =>
      ((‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2 : ℝ) : ℂ)) μ := by
  have hs := integrable_finsetSum Finset.univ
    (fun i hi => integrable_finsetSum Finset.univ
      (fun j hj => pair_intensity_integrable μ z a i j))
  exact hs.congr (Filter.Eventually.of_forall
    (fun y => (finite_intensity_expansion z a y).symm))

omit [DecidableEq ι] in
theorem finite_intensity_integrable
    (μ : Measure (EuclideanSpace ℝ ι)) [IsFiniteMeasure μ]
    (z : ι → ℂ) (a : ℝ) :
    Integrable (fun y : EuclideanSpace ℝ ι =>
      ‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2) μ := by
  simpa only [RCLike.re_to_complex, Complex.ofReal_re] using
    (finite_intensity_complex_integrable μ z a).re

theorem coordinate_difference_quadratic
    (D : Matrix ι ι ℝ) (i j : ι) :
    (EuclideanSpace.single i (1 : ℝ) - EuclideanSpace.single j (1 : ℝ)) ⬝ᵥ
      D *ᵥ (EuclideanSpace.single i (1 : ℝ) - EuclideanSpace.single j (1 : ℝ)) =
      D i i + D j j - D i j - D j i := by
  simp only [WithLp.ofLp_sub, PiLp.ofLp_single, Matrix.mulVec_sub,
    sub_dotProduct, dotProduct_sub, Matrix.mulVec_single_one,
    single_dotProduct, one_mul, Matrix.col_apply]
  ring

theorem gaussian_coordinate_difference_phase
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef) (a : ℝ) (i j : ι) :
    (∫ y : EuclideanSpace ℝ ι,
      Complex.exp (((a * (y i - y j) : ℝ) : ℂ) * Complex.I)
      ∂(multivariateGaussian 0 D)) =
    (Real.exp (-(a ^ 2 * (D i i + D j j - D i j - D j i)) / 2) : ℂ) := by
  have h := centered_gaussian_linear_phase D hD
    (EuclideanSpace.single i (1 : ℝ) - EuclideanSpace.single j (1 : ℝ)) a
  have hq := coordinate_difference_quadratic D i j
  simp only [WithLp.ofLp_sub] at h hq
  rw [hq] at h
  simpa [inner_sub_right, EuclideanSpace.inner_single_right, Complex.ofReal_exp] using h

theorem finite_gaussian_intensity_complex_mean
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef) (z : ι → ℂ) (a : ℝ) :
    (∫ y : EuclideanSpace ℝ ι,
      ((‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2 : ℝ) : ℂ)
      ∂(multivariateGaussian 0 D)) =
    ∑ i, ∑ j, (z i * conj (z j)) *
      (Real.exp (-(a ^ 2 * (D i i + D j j - D i j - D j i)) / 2) : ℂ) := by
  let μ := multivariateGaussian (0 : EuclideanSpace ℝ ι) D
  have hint := pair_intensity_integrable μ z a
  calc
    _ = ∫ y, ∑ i, ∑ j, (z i * conj (z j)) *
        Complex.exp (((a * (y i - y j) : ℝ) : ℂ) * Complex.I) ∂μ := by
      apply integral_congr_ae
      exact Filter.Eventually.of_forall (finite_intensity_expansion z a)
    _ = ∑ i, ∑ j, ∫ y, (z i * conj (z j)) *
        Complex.exp (((a * (y i - y j) : ℝ) : ℂ) * Complex.I) ∂μ := by
      rw [integral_finsetSum Finset.univ
        (fun i hi => integrable_finsetSum Finset.univ (fun j hj => hint i j))]
      apply Finset.sum_congr rfl
      intro i hi
      exact integral_finsetSum Finset.univ (fun j hj => hint i j)
    _ = _ := by
      apply Finset.sum_congr rfl
      intro i hi
      apply Finset.sum_congr rfl
      intro j hj
      rw [integral_const_mul, gaussian_coordinate_difference_phase D hD a i j]

theorem finite_gaussian_intensity_mean
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef) (z : ι → ℂ) (a : ℝ) :
    (∫ y : EuclideanSpace ℝ ι,
      ‖∑ i, z i * Complex.exp (((a * y i : ℝ) : ℂ) * Complex.I)‖ ^ 2
      ∂(multivariateGaussian 0 D)) =
    ∑ i, ∑ j, (z i * conj (z j)).re *
      Real.exp (-(a ^ 2 * (D i i + D j j - D i j - D j i)) / 2) := by
  have h := congrArg Complex.re (finite_gaussian_intensity_complex_mean D hD z a)
  rw [integral_complex_ofReal] at h
  simpa only [Complex.re_sum, Complex.ofReal_re, Complex.mul_re,
    Complex.ofReal_im, mul_zero, sub_zero] using h

end HomometricMotion

#print axioms HomometricMotion.continuous_phase_integrable
#print axioms HomometricMotion.phase_mul_conj
#print axioms HomometricMotion.finite_intensity_expansion
#print axioms HomometricMotion.pair_intensity_integrable
#print axioms HomometricMotion.finite_intensity_complex_integrable
#print axioms HomometricMotion.finite_intensity_integrable
#print axioms HomometricMotion.coordinate_difference_quadratic
#print axioms HomometricMotion.gaussian_coordinate_difference_phase
#print axioms HomometricMotion.finite_gaussian_intensity_complex_mean
#print axioms HomometricMotion.finite_gaussian_intensity_mean
