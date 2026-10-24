module

public import Mathlib.Probability.Distributions.Gaussian.Multivariate
public import Mathlib.Probability.Distributions.Gaussian.Fernique
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.FinCases

@[expose] public section

open MeasureTheory ProbabilityTheory Matrix
open scoped RealInnerProductSpace

set_option maxHeartbeats 4000000
set_option maxRecDepth 8192

noncomputable section

namespace HomometricMotion.GraphCovariance

theorem inverse_gram_certificate_psd
    {n m : Type*} [Fintype n] [Fintype m]
    (E : Matrix m n ℝ) (L K P : Matrix n n ℝ)
    (hL : L = Eᴴ * E) (hK : Kᴴ = K)
    (hLK : L * K = P) (hKP : K * P = K) :
    K.PosSemidef := by
  have hLpos : L.PosSemidef := by
    rw [hL]
    exact Matrix.posSemidef_conjTranspose_mul_self E
  have h := hLpos.conjTranspose_mul_mul_same K
  simpa only [Matrix.mul_assoc, hLK, hK, hKP] using h

theorem centered_gaussian_kernel_direction_ae_zero
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (D : Matrix ι ι ℝ) (hD : D.PosSemidef)
    (u : EuclideanSpace ℝ ι) (hu : D *ᵥ u = 0) :
    ∀ᵐ y ∂multivariateGaussian 0 D, ⟪u, y⟫ = 0 := by
  have hmem : MemLp id 2 (multivariateGaussian (0 : EuclideanSpace ℝ ι) D) :=
    IsGaussian.memLp_two_id
  have hv : Var[fun y : EuclideanSpace ℝ ι ↦ ⟪u, y⟫;
      multivariateGaussian 0 D] = 0 := by
    rw [← covarianceBilin_self hmem u, covarianceBilin_multivariateGaussian hD]
    simp [hu]
  have hi : (∫ y : EuclideanSpace ℝ ι, ⟪u, y⟫
      ∂multivariateGaussian 0 D) = 0 := by
    rw [integral_inner IsGaussian.integrable_fun_id]
    simp
  have h := ae_eq_integral_of_variance_eq_zero (hmem.const_inner u) hv
  simpa only [id_eq, hi] using h

noncomputable def comOnes : EuclideanSpace ℝ (Fin 9) :=
  WithLp.toLp 2 (fun _ ↦ (1 : ℝ))

theorem inner_comOnes_eq_sum (y : EuclideanSpace ℝ (Fin 9)) :
    ⟪comOnes, y⟫ = ∑ i, y i := by
  simp [comOnes, PiLp.inner_apply]

def comProjector : Matrix (Fin 9) (Fin 9) ℝ := fun i j =>
  if i = j then 8 / 9 else -(1 / 9)



end HomometricMotion.GraphCovariance
