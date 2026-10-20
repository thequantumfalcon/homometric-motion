# Claim ledger

This ledger describes the `exact_geometry` and `position_uncertainty` scenarios.
A successful
test or repository score does not establish a broader claim. See the
[proof index](proofs/README.md) for definitions and derivations.

| Claim | Evidence and scope | What this does not establish |
| --- | --- | --- |
| The explicit A and B have equal clean Fourier intensities at every common real frequency. | The factorization and reflection identity in [geometry and motion](proofs/geometry-and-motion.md); exact difference-multiplicity tests. | Equality of measurements made with different frequencies, moving configurations or different observation models. |
| The pair is noncongruent. | Different attached-arm invariants of their distance-threshold graphs. | Uniqueness among all configurations compatible with a measurement. |
| The selected frequency is an exact clean-amplitude null. | Algebraic cancellation of the specified phases, checked separately from intervals. | A null at an imperfectly calibrated frequency. |
| Finite positive Gaussian motion gives disjoint standardized third-cumulant intervals. | Global Taylor remainder inequalities and rational moment enclosures for the stated strength domain. | Non-Gaussian motion, arbitrary covariance, or a physical measurement. |
| The public fixed chain tolerates specified spring, exposure and frequency errors. | [Robustness derivation](proofs/robustness-and-counts.md) and the executable certificate. Frequency error requires the positive strength floor. | Arbitrary mean-position error, drifting settings or all noise levels. |
| A second joint domain permits bounded fixed mean-position error. | [Position-uncertainty derivation](proofs/position-uncertainty.md): coordinate error at most 10⁻¹⁴ and frequency error at most 10⁻¹⁶, with separately recomputed count bounds. | Homometry of imperfect specimens, weaker calibration requirements overall, or transfer of either scenario's count to the other. |
| Fixed gain and fixed Poisson background cancel from the population factorial-cumulant ratio. | Mixed-Poisson cumulant identity and finite latent-law calibration tests. | An unbiased finite-sample ratio, arbitrary detector noise or random background. |
| The stated count is sufficient for error at most 5% in each class. | Whole-window OU dependence bound, factorial-moment bounds, estimator allowance, Chebyshev inequality and union bound. | A necessary or optimal count, a zero-error classifier, or a practical laboratory budget. |
| The installed package reproduces its numerical assertions. | `python tools/project.py release`: exact checks, installed-wheel tests, source manifest and deterministic CLI replay. | Correctness of every untested code path or formal verification of the analytic proof. |
| Selected arithmetic and factorial identities have Lean proofs. | [Formal checkpoints](proofs/formal/README.md), statement mapping and pinned toolchain. | Formalization of the Gaussian, integration, covariance or Markov arguments, or physical validation. |
| The demo displays the default certificate and clean geometry. | Deterministic generation from a recomputed installed certificate; explicit separation of exact fractions and floating-point rendering. | Measurement data, a browser proof checker or an extension of the certified frequency domain. |
| The optional prototype generates and inspects declared synthetic processes. | [Model and limits](../prototype/MODEL_AND_LIMITS.md), source/reference bindings, repeated runs and recomputed covariance diagnostics. | A validated apparatus, calibrated diagnostic false-alarm rates, a test of the finite-window classifier or a guarantee for stress cases outside the theorem. |

## Evidence boundaries

- The repository contains a mathematical model and computations, not experimental
  measurements. No apparatus has been validated by these files.
- The complete theorem is not formally verified in a proof assistant.
  The formal checkpoints identify their exact statements; checking those
  statements does not formalize the Gaussian, integration or Markov arguments.
- Separate implementations and alternative arithmetic checks are useful error
  controls. They are not independent human peer review.
- No novelty, priority, patentability or discovery-of-a-new-physical-law claim is made.
  [Related work and failure regimes](proofs/scope-and-related-work.md) are essential
  context.
- Security tools report findings within their rules, databases and scan scope.
  A clean scan does not prove that software has no vulnerabilities. Community
  scores measure selected maintenance signals, not scientific truth.
- Development and demonstration results apply to the exact revision and model
  they identify. An extension is not covered merely because an earlier theorem passed.

## Correction policy

Report a missing assumption, false inequality, invalid inference or failing
reproduction as an issue with a minimal argument. Corrections must update the
proof, implementation, tests, manifest and this ledger as applicable. Preserve
the public history and explain which earlier claims are affected. Do not silently
replace published evidence or turn an inconclusive bound into a positive result.
