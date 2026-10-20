import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/- These are deterministic algebraic lemmas only.
   They do not formalize the stochastic model or the final risk theorem. -/

namespace HomometricMotion

theorem third_cumulant_perturbation_identity
    (f1 f2 f3 d1 d2 d3 : ℝ) :
    ((f3 + d3) - 3 * (f1 + d1) * (f2 + d2) + 2 * (f1 + d1)^3)
      - (f3 - 3 * f1 * f2 + 2 * f1^3)
      = d3 - 3 * f1 * d2 + (6 * f1^2 - 3 * f2) * d1
        - 3 * d1 * d2 + 6 * f1 * d1^2 + 2 * d1^3 := by
  ring

theorem third_cumulant_linear_coefficient (f1 f2 : ℝ) :
    6 * f1^2 - 3 * f2 = 3 * (f1^2 - (f2 - f1^2)) := by
  ring

theorem third_cumulant_coefficient_interval_bound
    (f1 F1 a amin amax : ℝ)
    (hf1 : 0 ≤ f1) (hf1max : f1 ≤ F1)
    (hmin : amin ≤ a) (hmax : a ≤ amax) :
    |3 * (f1^2 - a)| ≤ 3 * max amax (F1^2 - amin) := by
  have hF1 : 0 ≤ F1 := le_trans hf1 hf1max
  have hsq : f1^2 ≤ F1^2 := by
    nlinarith [mul_nonneg (sub_nonneg.mpr hf1max) (add_nonneg hf1 hF1)]
  have hleft : amax ≤ max amax (F1^2 - amin) := le_max_left _ _
  have hright : F1^2 - amin ≤ max amax (F1^2 - amin) := le_max_right _ _
  have hbound : |f1^2 - a| ≤ max amax (F1^2 - amin) := by
    apply abs_le.mpr
    constructor
    · nlinarith [sq_nonneg f1]
    · nlinarith
  rw [abs_mul, abs_of_pos (by norm_num : (0 : ℝ) < 3)]
  exact mul_le_mul_of_nonneg_left hbound (by norm_num)

theorem dropping_variance_upper_term_is_false :
    ¬ (|3 * ((0 : ℝ)^2 - 1)| ≤ 3 * ((0 : ℝ)^2 - 1)) := by
  norm_num

end HomometricMotion

#print axioms HomometricMotion.third_cumulant_perturbation_identity
#print axioms HomometricMotion.third_cumulant_linear_coefficient
#print axioms HomometricMotion.third_cumulant_coefficient_interval_bound
#print axioms HomometricMotion.dropping_variance_upper_term_is_false
