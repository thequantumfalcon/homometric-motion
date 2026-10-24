import Mathlib.Probability.Moments.Variance
import Mathlib.MeasureTheory.Function.L2Space
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
An analytic robustness step for arbitrary real square-integrable random variables.
This file does not assume the desired inequality, Gaussianity, independence, or a
particular detector model. It does not formalize the complete certificate theorem.
-/

noncomputable section

open MeasureTheory ProbabilityTheory
open scoped MeasureTheory ProbabilityTheory

namespace AnalyticRobustness

variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
variable {X Y : Ω → ℝ}

/-- The Hilbert-space norm of an L² representative is its second raw moment. -/
theorem norm_toLp_sq_eq_integral_sq (hX : MemLp X 2 μ) :
    ‖hX.toLp X‖ ^ 2 = ∫ ω, X ω ^ 2 ∂μ := by
  rw [← real_inner_self_eq_norm_sq, L2.inner_def]
  apply integral_congr_ae
  filter_upwards [hX.coeFn_toLp] with ω hω
  simp [hω, Real.norm_eq_abs, sq_abs]

/-- Here `sqrt` is applied to a genuine finite second moment. -/
theorem sqrt_integral_sq_eq_norm_toLp (hX : MemLp X 2 μ) :
    Real.sqrt (∫ ω, X ω ^ 2 ∂μ) = ‖hX.toLp X‖ := by
  rw [← norm_toLp_sq_eq_integral_sq hX, Real.sqrt_sq (norm_nonneg _)]

variable [IsProbabilityMeasure μ]

/-- Standard deviation is the L² norm of the centered random variable. -/
theorem sqrt_variance_eq_centered_norm (hX : MemLp X 2 μ) :
    Real.sqrt (variance X μ) =
      ‖(hX.sub (memLp_const (μ[X]))).toLp (X - fun _ ↦ μ[X])‖ := by
  rw [variance_eq_integral hX.aemeasurable]
  exact sqrt_integral_sq_eq_norm_toLp (hX.sub (memLp_const (μ[X])))

/-- Centering is a contraction in L² on a probability space. -/
theorem centered_norm_le_norm (hX : MemLp X 2 μ) :
    ‖(hX.sub (memLp_const (μ[X]))).toLp (X - fun _ ↦ μ[X])‖ ≤ ‖hX.toLp X‖ := by
  have hv := variance_le_expectation_sq hX.aestronglyMeasurable
  have hc := norm_toLp_sq_eq_integral_sq (hX.sub (memLp_const (μ[X])))
  have hx := norm_toLp_sq_eq_integral_sq hX
  rw [variance_eq_integral hX.aemeasurable] at hv
  have hn1 := norm_nonneg ((hX.sub (memLp_const (μ[X]))).toLp (X - fun _ ↦ μ[X]))
  have hn2 := norm_nonneg (hX.toLp X)
  simp only [Pi.sub_apply, Pi.pow_apply] at *
  nlinarith

/-- The standard-deviation difference is bounded by the L² size of the change. -/
theorem abs_sqrt_variance_sub_le_l2 (hX : MemLp X 2 μ) (hY : MemLp Y 2 μ) :
    |Real.sqrt (variance X μ) - Real.sqrt (variance Y μ)| ≤
      Real.sqrt (∫ ω, (X ω - Y ω) ^ 2 ∂μ) := by
  let CX := X - fun _ ↦ μ[X]
  let CY := Y - fun _ ↦ μ[Y]
  have hCX : MemLp CX 2 μ := hX.sub (memLp_const (μ[X]))
  have hCY : MemLp CY 2 μ := hY.sub (memLp_const (μ[Y]))
  have hXY := hX.sub hY
  have hcenter : CX - CY = (X - Y) - fun _ ↦ μ[X - Y] := by
    ext ω
    simp only [CX, CY, Pi.sub_apply, integral_sub (hX.integrable one_le_two)
      (hY.integrable one_le_two)]
    ring
  have hLp :
      hCX.toLp CX - hCY.toLp CY =
        (hXY.sub (memLp_const (μ[X - Y]))).toLp ((X - Y) - fun _ ↦ μ[X - Y]) := by
    rw [← MemLp.toLp_sub]
    apply MemLp.toLp_congr
    exact Filter.EventuallyEq.of_eq hcenter
  calc
    |Real.sqrt (variance X μ) - Real.sqrt (variance Y μ)| =
        |‖hCX.toLp CX‖ - ‖hCY.toLp CY‖| := by
          rw [sqrt_variance_eq_centered_norm hX, sqrt_variance_eq_centered_norm hY]
    _ ≤ ‖hCX.toLp CX - hCY.toLp CY‖ := abs_norm_sub_norm_le _ _
    _ = ‖(hXY.sub (memLp_const (μ[X - Y]))).toLp ((X - Y) - fun _ ↦ μ[X - Y])‖ := by
          rw [hLp]
    _ ≤ ‖hXY.toLp (X - Y)‖ := centered_norm_le_norm hXY
    _ = Real.sqrt (∫ ω, (X ω - Y ω) ^ 2 ∂μ) :=
          (sqrt_integral_sq_eq_norm_toLp hXY).symm

/-- The variance enclosure used after an L² perturbation bound. -/
theorem variance_enclosure_of_l2_bound (hX : MemLp X 2 μ) (hY : MemLp Y 2 μ)
    {δ : ℝ} (hδ : Real.sqrt (∫ ω, (X ω - Y ω) ^ 2 ∂μ) ≤ δ) :
    (max 0 (Real.sqrt (variance X μ) - δ)) ^ 2 ≤ variance Y μ ∧
      variance Y μ ≤ (Real.sqrt (variance X μ) + δ) ^ 2 := by
  have h := (abs_sqrt_variance_sub_le_l2 hX hY).trans hδ
  have hl := (abs_le.mp h).2
  have hu := (abs_le.mp h).1
  have hy := Real.sqrt_nonneg (variance Y μ)
  have hx := Real.sqrt_nonneg (variance X μ)
  have hy_sq := Real.sq_sqrt (variance_nonneg Y μ)
  have h_lower : max 0 (Real.sqrt (variance X μ) - δ) ≤ Real.sqrt (variance Y μ) :=
    max_le hy (by linarith)
  have h_upper : Real.sqrt (variance Y μ) ≤ Real.sqrt (variance X μ) + δ := by
    linarith
  have hmax : 0 ≤ max 0 (Real.sqrt (variance X μ) - δ) := le_max_left _ _
  constructor
  · nlinarith
  · nlinarith

/-- The L³ perturbation bound dominates its L² norm on a probability space. -/
theorem sqrt_integral_sq_le_l3 (hX : MemLp X 3 μ) :
    Real.sqrt (∫ ω, X ω ^ 2 ∂μ) ≤ (eLpNorm X 3 μ).toReal := by
  have h23 : (2 : ENNReal) ≤ 3 := by norm_num
  have h2 := hX.mono_exponent h23
  rw [sqrt_integral_sq_eq_norm_toLp h2, Lp.norm_toLp]
  exact ENNReal.toReal_mono hX.eLpNorm_ne_top
    (eLpNorm_le_eLpNorm_of_exponent_le h23)

/-- Direct connection to a finite L³ coupling-error bound. -/
theorem abs_sqrt_variance_sub_le_l3 (hX : MemLp X 3 μ) (hY : MemLp Y 3 μ) :
    |Real.sqrt (variance X μ) - Real.sqrt (variance Y μ)| ≤
      (eLpNorm (X - Y) 3 μ).toReal := by
  have h23 : (2 : ENNReal) ≤ 3 := by norm_num
  exact (abs_sqrt_variance_sub_le_l2 (hX.mono_exponent h23) (hY.mono_exponent h23)).trans
    (sqrt_integral_sq_le_l3 (hX.sub hY))

/-- Variance bounds certified from an explicit L³ perturbation size. -/
theorem variance_enclosure_of_l3_bound (hX : MemLp X 3 μ) (hY : MemLp Y 3 μ)
    {δ : ℝ} (hδ : (eLpNorm (X - Y) 3 μ).toReal ≤ δ) :
    (max 0 (Real.sqrt (variance X μ) - δ)) ^ 2 ≤ variance Y μ ∧
      variance Y μ ≤ (Real.sqrt (variance X μ) + δ) ^ 2 := by
  have h23 : (2 : ENNReal) ≤ 3 := by norm_num
  exact variance_enclosure_of_l2_bound (hX.mono_exponent h23) (hY.mono_exponent h23)
    ((sqrt_integral_sq_le_l3 (hX.sub hY)).trans hδ)

#print axioms norm_toLp_sq_eq_integral_sq
#print axioms sqrt_integral_sq_eq_norm_toLp
#print axioms sqrt_variance_eq_centered_norm
#print axioms centered_norm_le_norm
#print axioms abs_sqrt_variance_sub_le_l2
#print axioms variance_enclosure_of_l2_bound
#print axioms sqrt_integral_sq_le_l3
#print axioms abs_sqrt_variance_sub_le_l3
#print axioms variance_enclosure_of_l3_bound

#check @abs_sqrt_variance_sub_le_l2
#check @variance_enclosure_of_l2_bound
#check @abs_sqrt_variance_sub_le_l3
#check @variance_enclosure_of_l3_bound

end AnalyticRobustness
