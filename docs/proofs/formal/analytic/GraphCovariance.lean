module

public import GraphCommon

@[expose] public section

open MeasureTheory ProbabilityTheory Matrix
open scoped RealInnerProductSpace
set_option maxHeartbeats 4000000
set_option maxRecDepth 8192
noncomputable section
namespace HomometricMotion.GraphCovariance

def liftMatrix {m n : Type*} (M : Matrix m n ℚ) : Matrix m n ℝ :=
  M.map (Rat.castHom ℝ)

theorem liftMatrix_mul {m n k : Type*} [Fintype n]
    (M : Matrix m n ℚ) (N : Matrix n k ℚ) :
    liftMatrix (M * N) = liftMatrix M * liftMatrix N :=
  Matrix.map_mul

theorem liftMatrix_transpose {m n : Type*} (M : Matrix m n ℚ) :
    liftMatrix Mᵀ = (liftMatrix M)ᴴ := by
  ext i j
  simp [liftMatrix, Matrix.conjTranspose_apply]

def projectorQ : Matrix (Fin 9) (Fin 9) ℚ := fun i j =>
  if i = j then 8 / 9 else -(1 / 9)

theorem lift_projector : liftMatrix projectorQ = comProjector := by
  ext i j
  by_cases h : i = j <;> simp [liftMatrix, projectorQ, comProjector, h]

def EAQ : Matrix (Fin 12) (Fin 9) ℚ := fun i j =>
  match i.val, j.val with
  | 0, 0 => 1
  | 0, 1 => -1
  | 1, 0 => 1
  | 1, 2 => -1
  | 2, 1 => 1
  | 2, 2 => -1
  | 3, 2 => 1
  | 3, 3 => -1
  | 4, 2 => 1
  | 4, 4 => -1
  | 5, 3 => 1
  | 5, 4 => -1
  | 6, 3 => 1
  | 6, 5 => -1
  | 7, 4 => 1
  | 7, 5 => -1
  | 8, 5 => 1
  | 8, 6 => -1
  | 9, 6 => 1
  | 9, 7 => -1
  | 10, 6 => 1
  | 10, 8 => -1
  | 11, 7 => 1
  | 11, 8 => -1
  | _, _ => 0

def LAQ : Matrix (Fin 9) (Fin 9) ℚ := fun i j =>
  match i.val, j.val with
  | 0, 0 => 2
  | 0, 1 => -1
  | 0, 2 => -1
  | 1, 0 => -1
  | 1, 1 => 2
  | 1, 2 => -1
  | 2, 0 => -1
  | 2, 1 => -1
  | 2, 2 => 4
  | 2, 3 => -1
  | 2, 4 => -1
  | 3, 2 => -1
  | 3, 3 => 3
  | 3, 4 => -1
  | 3, 5 => -1
  | 4, 2 => -1
  | 4, 3 => -1
  | 4, 4 => 3
  | 4, 5 => -1
  | 5, 3 => -1
  | 5, 4 => -1
  | 5, 5 => 3
  | 5, 6 => -1
  | 6, 5 => -1
  | 6, 6 => 3
  | 6, 7 => -1
  | 6, 8 => -1
  | 7, 6 => -1
  | 7, 7 => 2
  | 7, 8 => -1
  | 8, 6 => -1
  | 8, 7 => -1
  | 8, 8 => 2
  | _, _ => 0

def KAQ : Matrix (Fin 9) (Fin 9) ℚ := fun i j =>
  match i.val, j.val with
  | 0, 0 => (25 / 27)
  | 0, 1 => (16 / 27)
  | 0, 2 => (10 / 27)
  | 0, 3 => (1 / 27)
  | 0, 4 => (1 / 27)
  | 0, 5 => (-5 / 27)
  | 0, 6 => (-14 / 27)
  | 0, 7 => (-17 / 27)
  | 0, 8 => (-17 / 27)
  | 1, 0 => (16 / 27)
  | 1, 1 => (25 / 27)
  | 1, 2 => (10 / 27)
  | 1, 3 => (1 / 27)
  | 1, 4 => (1 / 27)
  | 1, 5 => (-5 / 27)
  | 1, 6 => (-14 / 27)
  | 1, 7 => (-17 / 27)
  | 1, 8 => (-17 / 27)
  | 2, 0 => (10 / 27)
  | 2, 1 => (10 / 27)
  | 2, 2 => (13 / 27)
  | 2, 3 => (4 / 27)
  | 2, 4 => (4 / 27)
  | 2, 5 => (-2 / 27)
  | 2, 6 => (-11 / 27)
  | 2, 7 => (-14 / 27)
  | 2, 8 => (-14 / 27)
  | 3, 0 => (1 / 27)
  | 3, 1 => (1 / 27)
  | 3, 2 => (4 / 27)
  | 3, 3 => (95 / 216)
  | 3, 4 => (41 / 216)
  | 3, 5 => (5 / 54)
  | 3, 6 => (-13 / 54)
  | 3, 7 => (-19 / 54)
  | 3, 8 => (-19 / 54)
  | 4, 0 => (1 / 27)
  | 4, 1 => (1 / 27)
  | 4, 2 => (4 / 27)
  | 4, 3 => (41 / 216)
  | 4, 4 => (95 / 216)
  | 4, 5 => (5 / 54)
  | 4, 6 => (-13 / 54)
  | 4, 7 => (-19 / 54)
  | 4, 8 => (-19 / 54)
  | 5, 0 => (-5 / 27)
  | 5, 1 => (-5 / 27)
  | 5, 2 => (-2 / 27)
  | 5, 3 => (5 / 54)
  | 5, 4 => (5 / 54)
  | 5, 5 => (10 / 27)
  | 5, 6 => (1 / 27)
  | 5, 7 => (-2 / 27)
  | 5, 8 => (-2 / 27)
  | 6, 0 => (-14 / 27)
  | 6, 1 => (-14 / 27)
  | 6, 2 => (-11 / 27)
  | 6, 3 => (-13 / 54)
  | 6, 4 => (-13 / 54)
  | 6, 5 => (1 / 27)
  | 6, 6 => (19 / 27)
  | 6, 7 => (16 / 27)
  | 6, 8 => (16 / 27)
  | 7, 0 => (-17 / 27)
  | 7, 1 => (-17 / 27)
  | 7, 2 => (-14 / 27)
  | 7, 3 => (-19 / 54)
  | 7, 4 => (-19 / 54)
  | 7, 5 => (-2 / 27)
  | 7, 6 => (16 / 27)
  | 7, 7 => (31 / 27)
  | 7, 8 => (22 / 27)
  | 8, 0 => (-17 / 27)
  | 8, 1 => (-17 / 27)
  | 8, 2 => (-14 / 27)
  | 8, 3 => (-19 / 54)
  | 8, 4 => (-19 / 54)
  | 8, 5 => (-2 / 27)
  | 8, 6 => (16 / 27)
  | 8, 7 => (22 / 27)
  | 8, 8 => (31 / 27)
  | _, _ => 0

def xA (i : Fin 9) : ℚ :=
  match i.val with
  | 0 => 0
  | 1 => 1
  | 2 => 5
  | 3 => 10
  | 4 => 11
  | 5 => 15
  | 6 => 22
  | 7 => 23
  | 8 => 27
  | _ => 0

def adjA (i j : Fin 9) : ℚ :=
  if i ≠ j ∧ |xA i - xA j| < (15 / 2 : ℚ) then 1 else 0


theorem rationalA_threshold :
    ∀ i j, LAQ i j =
      if i = j then ∑ k, adjA i k else -adjA i j := by
  let target : Matrix (Fin 9) (Fin 9) ℚ :=
    fun i j => if i = j then ∑ k, adjA i k else -adjA i j
  have h : LAQ = target :=
    @of_decide_eq_true (LAQ = target) (Matrix.decidableEq LAQ target)
      (by decide +kernel)
  intro i j
  exact congrFun (congrFun h i) j
theorem rationalA_gram : LAQ = (EAQ)ᵀ * EAQ := by decide +kernel
theorem rationalA_symmetric : (KAQ)ᵀ = KAQ := by decide +kernel
theorem rationalA_inverse : LAQ * KAQ = projectorQ := by decide +kernel
theorem rationalA_centered : KAQ * projectorQ = KAQ := by decide +kernel
theorem rationalA_projector : projectorQ * LAQ = LAQ := by decide +kernel
theorem rationalA_zero_com : KAQ *ᵥ (fun _ => (1 : ℚ)) = 0 := by decide +kernel
theorem rationalA_trace : Matrix.trace KAQ = (79 / 12 : ℚ) := by decide +kernel

def EA : Matrix (Fin 12) (Fin 9) ℝ := liftMatrix EAQ
def LA : Matrix (Fin 9) (Fin 9) ℝ := liftMatrix LAQ
def KA : Matrix (Fin 9) (Fin 9) ℝ := liftMatrix KAQ
def DA : Matrix (Fin 9) (Fin 9) ℝ := (108 / 79 : ℝ) • KA

theorem laplacianA_gram : LA = (EA)ᴴ * EA := by
  change liftMatrix LAQ = (liftMatrix EAQ)ᴴ * liftMatrix EAQ
  rw [← liftMatrix_transpose, ← liftMatrix_mul, ← rationalA_gram]

theorem inverseA_selfadjoint : (KA)ᴴ = KA := by
  change (liftMatrix KAQ)ᴴ = liftMatrix KAQ
  rw [← liftMatrix_transpose, rationalA_symmetric]

theorem inverseA_laplacian_right : LA * KA = comProjector := by
  change liftMatrix LAQ * liftMatrix KAQ = comProjector
  rw [← liftMatrix_mul, rationalA_inverse, lift_projector]

theorem inverseA_projector : KA * comProjector = KA := by
  rw [← lift_projector]
  change liftMatrix KAQ * liftMatrix projectorQ = liftMatrix KAQ
  rw [← liftMatrix_mul, rationalA_centered]

theorem projector_laplacianA : comProjector * LA = LA := by
  rw [← lift_projector]
  change liftMatrix projectorQ * liftMatrix LAQ = liftMatrix LAQ
  rw [← liftMatrix_mul, rationalA_projector]

theorem inverseA_zero_com : KA *ᵥ (fun _ => (1 : ℝ)) = 0 := by
  ext i
  have h := congrFun rationalA_zero_com i
  have hc := congrArg (Rat.castHom ℝ) h
  simpa [KA, liftMatrix, Matrix.mulVec, dotProduct] using hc

theorem inverseA_psd : (KA).PosSemidef :=
  inverse_gram_certificate_psd EA LA KA comProjector
    laplacianA_gram inverseA_selfadjoint
    inverseA_laplacian_right inverseA_projector

theorem covarianceA_psd : (DA).PosSemidef := by
  exact inverseA_psd.smul (by norm_num : (0 : ℝ) ≤ 108 / 79)

theorem inverseA_trace : Matrix.trace KA = (79 / 12 : ℝ) := by
  have h := congrArg (Rat.castHom ℝ) rationalA_trace
  simpa [KA, liftMatrix, Matrix.trace, Matrix.diag] using h

theorem covarianceA_normalization :
    DA = (9 / Matrix.trace KA) • KA := by
  rw [inverseA_trace]
  norm_num [DA]

theorem covarianceA_trace : Matrix.trace DA = (9 : ℝ) := by
  rw [DA, Matrix.trace_smul, inverseA_trace]
  norm_num

theorem covarianceA_zero_com : DA *ᵥ (fun _ => (1 : ℝ)) = 0 := by
  rw [DA, Matrix.smul_mulVec, inverseA_zero_com]
  simp

theorem gaussianA_zero_com :
    ∀ᵐ y : EuclideanSpace ℝ (Fin 9) ∂multivariateGaussian 0 DA,
      ∑ i, y i = 0 := by
  have h := centered_gaussian_kernel_direction_ae_zero DA covarianceA_psd
    comOnes (by simpa [comOnes] using covarianceA_zero_com)
  simpa only [inner_comOnes_eq_sum] using h

def EBQ : Matrix (Fin 12) (Fin 9) ℚ := fun i j =>
  match i.val, j.val with
  | 0, 0 => 1
  | 0, 1 => -1
  | 1, 0 => 1
  | 1, 2 => -1
  | 2, 1 => 1
  | 2, 2 => -1
  | 3, 2 => 1
  | 3, 3 => -1
  | 4, 3 => 1
  | 4, 4 => -1
  | 5, 3 => 1
  | 5, 5 => -1
  | 6, 4 => 1
  | 6, 5 => -1
  | 7, 5 => 1
  | 7, 6 => -1
  | 8, 5 => 1
  | 8, 7 => -1
  | 9, 6 => 1
  | 9, 7 => -1
  | 10, 6 => 1
  | 10, 8 => -1
  | 11, 7 => 1
  | 11, 8 => -1
  | _, _ => 0

def LBQ : Matrix (Fin 9) (Fin 9) ℚ := fun i j =>
  match i.val, j.val with
  | 0, 0 => 2
  | 0, 1 => -1
  | 0, 2 => -1
  | 1, 0 => -1
  | 1, 1 => 2
  | 1, 2 => -1
  | 2, 0 => -1
  | 2, 1 => -1
  | 2, 2 => 3
  | 2, 3 => -1
  | 3, 2 => -1
  | 3, 3 => 3
  | 3, 4 => -1
  | 3, 5 => -1
  | 4, 3 => -1
  | 4, 4 => 2
  | 4, 5 => -1
  | 5, 3 => -1
  | 5, 4 => -1
  | 5, 5 => 4
  | 5, 6 => -1
  | 5, 7 => -1
  | 6, 5 => -1
  | 6, 6 => 3
  | 6, 7 => -1
  | 6, 8 => -1
  | 7, 5 => -1
  | 7, 6 => -1
  | 7, 7 => 3
  | 7, 8 => -1
  | 8, 6 => -1
  | 8, 7 => -1
  | 8, 8 => 2
  | _, _ => 0

def KBQ : Matrix (Fin 9) (Fin 9) ℚ := fun i j =>
  match i.val, j.val with
  | 0, 0 => (31 / 27)
  | 0, 1 => (22 / 27)
  | 0, 2 => (16 / 27)
  | 0, 3 => (-2 / 27)
  | 0, 4 => (-8 / 27)
  | 0, 5 => (-11 / 27)
  | 0, 6 => (-31 / 54)
  | 0, 7 => (-31 / 54)
  | 0, 8 => (-17 / 27)
  | 1, 0 => (22 / 27)
  | 1, 1 => (31 / 27)
  | 1, 2 => (16 / 27)
  | 1, 3 => (-2 / 27)
  | 1, 4 => (-8 / 27)
  | 1, 5 => (-11 / 27)
  | 1, 6 => (-31 / 54)
  | 1, 7 => (-31 / 54)
  | 1, 8 => (-17 / 27)
  | 2, 0 => (16 / 27)
  | 2, 1 => (16 / 27)
  | 2, 2 => (19 / 27)
  | 2, 3 => (1 / 27)
  | 2, 4 => (-5 / 27)
  | 2, 5 => (-8 / 27)
  | 2, 6 => (-25 / 54)
  | 2, 7 => (-25 / 54)
  | 2, 8 => (-14 / 27)
  | 3, 0 => (-2 / 27)
  | 3, 1 => (-2 / 27)
  | 3, 2 => (1 / 27)
  | 3, 3 => (10 / 27)
  | 3, 4 => (4 / 27)
  | 3, 5 => (1 / 27)
  | 3, 6 => (-7 / 54)
  | 3, 7 => (-7 / 54)
  | 3, 8 => (-5 / 27)
  | 4, 0 => (-8 / 27)
  | 4, 1 => (-8 / 27)
  | 4, 2 => (-5 / 27)
  | 4, 3 => (4 / 27)
  | 4, 4 => (16 / 27)
  | 4, 5 => (4 / 27)
  | 4, 6 => (-1 / 54)
  | 4, 7 => (-1 / 54)
  | 4, 8 => (-2 / 27)
  | 5, 0 => (-11 / 27)
  | 5, 1 => (-11 / 27)
  | 5, 2 => (-8 / 27)
  | 5, 3 => (1 / 27)
  | 5, 4 => (4 / 27)
  | 5, 5 => (10 / 27)
  | 5, 6 => (11 / 54)
  | 5, 7 => (11 / 54)
  | 5, 8 => (4 / 27)
  | 6, 0 => (-31 / 54)
  | 6, 1 => (-31 / 54)
  | 6, 2 => (-25 / 54)
  | 6, 3 => (-7 / 54)
  | 6, 4 => (-1 / 54)
  | 6, 5 => (11 / 54)
  | 6, 6 => (143 / 216)
  | 6, 7 => (89 / 216)
  | 6, 8 => (13 / 27)
  | 7, 0 => (-31 / 54)
  | 7, 1 => (-31 / 54)
  | 7, 2 => (-25 / 54)
  | 7, 3 => (-7 / 54)
  | 7, 4 => (-1 / 54)
  | 7, 5 => (11 / 54)
  | 7, 6 => (89 / 216)
  | 7, 7 => (143 / 216)
  | 7, 8 => (13 / 27)
  | 8, 0 => (-17 / 27)
  | 8, 1 => (-17 / 27)
  | 8, 2 => (-14 / 27)
  | 8, 3 => (-5 / 27)
  | 8, 4 => (-2 / 27)
  | 8, 5 => (4 / 27)
  | 8, 6 => (13 / 27)
  | 8, 7 => (13 / 27)
  | 8, 8 => (25 / 27)
  | _, _ => 0

def xB (i : Fin 9) : ℚ :=
  match i.val with
  | 0 => 0
  | 1 => 1
  | 2 => 5
  | 3 => 12
  | 4 => 13
  | 5 => 17
  | 6 => 22
  | 7 => 23
  | 8 => 27
  | _ => 0

def adjB (i j : Fin 9) : ℚ :=
  if i ≠ j ∧ |xB i - xB j| < (15 / 2 : ℚ) then 1 else 0


theorem rationalB_threshold :
    ∀ i j, LBQ i j =
      if i = j then ∑ k, adjB i k else -adjB i j := by
  let target : Matrix (Fin 9) (Fin 9) ℚ :=
    fun i j => if i = j then ∑ k, adjB i k else -adjB i j
  have h : LBQ = target :=
    @of_decide_eq_true (LBQ = target) (Matrix.decidableEq LBQ target)
      (by decide +kernel)
  intro i j
  exact congrFun (congrFun h i) j
theorem rationalB_gram : LBQ = (EBQ)ᵀ * EBQ := by decide +kernel
theorem rationalB_symmetric : (KBQ)ᵀ = KBQ := by decide +kernel
theorem rationalB_inverse : LBQ * KBQ = projectorQ := by decide +kernel
theorem rationalB_centered : KBQ * projectorQ = KBQ := by decide +kernel
theorem rationalB_projector : projectorQ * LBQ = LBQ := by decide +kernel
theorem rationalB_zero_com : KBQ *ᵥ (fun _ => (1 : ℚ)) = 0 := by decide +kernel
theorem rationalB_trace : Matrix.trace KBQ = (79 / 12 : ℚ) := by decide +kernel

def EB : Matrix (Fin 12) (Fin 9) ℝ := liftMatrix EBQ
def LB : Matrix (Fin 9) (Fin 9) ℝ := liftMatrix LBQ
def KB : Matrix (Fin 9) (Fin 9) ℝ := liftMatrix KBQ
def DB : Matrix (Fin 9) (Fin 9) ℝ := (108 / 79 : ℝ) • KB

theorem laplacianB_gram : LB = (EB)ᴴ * EB := by
  change liftMatrix LBQ = (liftMatrix EBQ)ᴴ * liftMatrix EBQ
  rw [← liftMatrix_transpose, ← liftMatrix_mul, ← rationalB_gram]

theorem inverseB_selfadjoint : (KB)ᴴ = KB := by
  change (liftMatrix KBQ)ᴴ = liftMatrix KBQ
  rw [← liftMatrix_transpose, rationalB_symmetric]

theorem inverseB_laplacian_right : LB * KB = comProjector := by
  change liftMatrix LBQ * liftMatrix KBQ = comProjector
  rw [← liftMatrix_mul, rationalB_inverse, lift_projector]

theorem inverseB_projector : KB * comProjector = KB := by
  rw [← lift_projector]
  change liftMatrix KBQ * liftMatrix projectorQ = liftMatrix KBQ
  rw [← liftMatrix_mul, rationalB_centered]

theorem projector_laplacianB : comProjector * LB = LB := by
  rw [← lift_projector]
  change liftMatrix projectorQ * liftMatrix LBQ = liftMatrix LBQ
  rw [← liftMatrix_mul, rationalB_projector]

theorem inverseB_zero_com : KB *ᵥ (fun _ => (1 : ℝ)) = 0 := by
  ext i
  have h := congrFun rationalB_zero_com i
  have hc := congrArg (Rat.castHom ℝ) h
  simpa [KB, liftMatrix, Matrix.mulVec, dotProduct] using hc

theorem inverseB_psd : (KB).PosSemidef :=
  inverse_gram_certificate_psd EB LB KB comProjector
    laplacianB_gram inverseB_selfadjoint
    inverseB_laplacian_right inverseB_projector

theorem covarianceB_psd : (DB).PosSemidef := by
  exact inverseB_psd.smul (by norm_num : (0 : ℝ) ≤ 108 / 79)

theorem inverseB_trace : Matrix.trace KB = (79 / 12 : ℝ) := by
  have h := congrArg (Rat.castHom ℝ) rationalB_trace
  simpa [KB, liftMatrix, Matrix.trace, Matrix.diag] using h

theorem covarianceB_normalization :
    DB = (9 / Matrix.trace KB) • KB := by
  rw [inverseB_trace]
  norm_num [DB]

theorem covarianceB_trace : Matrix.trace DB = (9 : ℝ) := by
  rw [DB, Matrix.trace_smul, inverseB_trace]
  norm_num

theorem covarianceB_zero_com : DB *ᵥ (fun _ => (1 : ℝ)) = 0 := by
  rw [DB, Matrix.smul_mulVec, inverseB_zero_com]
  simp

theorem gaussianB_zero_com :
    ∀ᵐ y : EuclideanSpace ℝ (Fin 9) ∂multivariateGaussian 0 DB,
      ∑ i, y i = 0 := by
  have h := centered_gaussian_kernel_direction_ae_zero DB covarianceB_psd
    comOnes (by simpa [comOnes] using covarianceB_zero_com)
  simpa only [inner_comOnes_eq_sum] using h

theorem negative_covarianceA_not_psd : ¬ (-DA).PosSemidef := by
  intro h
  have h0 := h.diag_nonneg (i := (0 : Fin 9))
  norm_num [DA, KA, liftMatrix, KAQ, Matrix.neg_apply, Matrix.smul_apply] at h0

#print axioms HomometricMotion.GraphCovariance.liftMatrix_mul
#print axioms HomometricMotion.GraphCovariance.liftMatrix_transpose
#print axioms HomometricMotion.GraphCovariance.lift_projector
#print axioms HomometricMotion.GraphCovariance.rationalA_threshold
#print axioms HomometricMotion.GraphCovariance.rationalA_gram
#print axioms HomometricMotion.GraphCovariance.rationalA_symmetric
#print axioms HomometricMotion.GraphCovariance.rationalA_inverse
#print axioms HomometricMotion.GraphCovariance.rationalA_centered
#print axioms HomometricMotion.GraphCovariance.rationalA_projector
#print axioms HomometricMotion.GraphCovariance.rationalA_zero_com
#print axioms HomometricMotion.GraphCovariance.rationalA_trace
#print axioms HomometricMotion.GraphCovariance.laplacianA_gram
#print axioms HomometricMotion.GraphCovariance.inverseA_selfadjoint
#print axioms HomometricMotion.GraphCovariance.inverseA_laplacian_right
#print axioms HomometricMotion.GraphCovariance.inverseA_projector
#print axioms HomometricMotion.GraphCovariance.projector_laplacianA
#print axioms HomometricMotion.GraphCovariance.inverseA_zero_com
#print axioms HomometricMotion.GraphCovariance.inverseA_psd
#print axioms HomometricMotion.GraphCovariance.covarianceA_psd
#print axioms HomometricMotion.GraphCovariance.inverseA_trace
#print axioms HomometricMotion.GraphCovariance.covarianceA_normalization
#print axioms HomometricMotion.GraphCovariance.covarianceA_trace
#print axioms HomometricMotion.GraphCovariance.covarianceA_zero_com
#print axioms HomometricMotion.GraphCovariance.gaussianA_zero_com
#print axioms HomometricMotion.GraphCovariance.rationalB_threshold
#print axioms HomometricMotion.GraphCovariance.rationalB_gram
#print axioms HomometricMotion.GraphCovariance.rationalB_symmetric
#print axioms HomometricMotion.GraphCovariance.rationalB_inverse
#print axioms HomometricMotion.GraphCovariance.rationalB_centered
#print axioms HomometricMotion.GraphCovariance.rationalB_projector
#print axioms HomometricMotion.GraphCovariance.rationalB_zero_com
#print axioms HomometricMotion.GraphCovariance.rationalB_trace
#print axioms HomometricMotion.GraphCovariance.laplacianB_gram
#print axioms HomometricMotion.GraphCovariance.inverseB_selfadjoint
#print axioms HomometricMotion.GraphCovariance.inverseB_laplacian_right
#print axioms HomometricMotion.GraphCovariance.inverseB_projector
#print axioms HomometricMotion.GraphCovariance.projector_laplacianB
#print axioms HomometricMotion.GraphCovariance.inverseB_zero_com
#print axioms HomometricMotion.GraphCovariance.inverseB_psd
#print axioms HomometricMotion.GraphCovariance.covarianceB_psd
#print axioms HomometricMotion.GraphCovariance.inverseB_trace
#print axioms HomometricMotion.GraphCovariance.covarianceB_normalization
#print axioms HomometricMotion.GraphCovariance.covarianceB_trace
#print axioms HomometricMotion.GraphCovariance.covarianceB_zero_com
#print axioms HomometricMotion.GraphCovariance.gaussianB_zero_com
#print axioms HomometricMotion.GraphCovariance.negative_covarianceA_not_psd
#print axioms HomometricMotion.GraphCovariance.inverse_gram_certificate_psd
#print axioms HomometricMotion.GraphCovariance.centered_gaussian_kernel_direction_ae_zero
#print axioms HomometricMotion.GraphCovariance.inner_comOnes_eq_sum
end HomometricMotion.GraphCovariance
