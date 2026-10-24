# Claim ledger

This ledger describes the 63-point `exact_geometry` and `position_uncertainty`
scenarios, the separately identified nine-point instantaneous-intensity model,
a separate calibrated iid count channel, and a complete-graph counterexample
with a different interaction rule.
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
| Separate coordinate tolerances reduce the sufficient counts under the same assumptions. | [Coordinate-count proof](proofs/coordinate-counts.md): complete nonlinear error bounds and a rational feasible allocation, freshly recomputed with the full core. | Global optimality, a lower bound on required observations or a less restrictive physical domain. |
| A separate method permits normalized exposure up to 10⁻⁵ in both scenarios. | [Linear exposure proof](proofs/linear-exposure.md): weighted-OU quadratic kernel bounds, stationary Gaussian parity transfer, and newly computed frequency/position, classifier and count witnesses. | Arbitrary exposure, a temporal model inferred from marginal covariance alone, or practical hardware validation. |
| Explicit profiles provide new sufficient counts without replacing earlier contracts. | [Profile proof](proofs/profiled-counts.md): the complete cancellation-aware estimator polynomial, separate actual variance/third errors, fresh thresholds and exact union-risk ceilings. | Global optimality, an implicit best profile, a necessary sample size or transfer of an earlier threshold. |
| The selected long profiles permit exposure caps 0.001 and 0.01 in their respective scenarios. | [Signed kernel proof](proofs/signed-kernel-exposure.md): same-generator signed derivatives, absolute remainders, rank-two majorization, finite-motion parity, all 512 cells and independent class-wise nuisance-propagated shape unions. | A two-eigenvalue time-averaged law, exponential monotonicity across different generators, an independent global moment-rectangle shape argument or arbitrary temporal models. |
| Four deterministic sensitivity statements have optional Lean proofs. | [Analytic-project scope](proofs/formal/analytic/SCOPE.md#cumulant-sensitivity-statements): two exact identities, an absolute interval coefficient bound and an abstract counterexample to dropping its upper-variance branch. | Formalization of the full error-budget inequalities, the Poisson interpretation, the numerical allocation, concentration or the classifier. |
| The installed package reproduces its numerical assertions. | `python tools/project.py release`: exact checks, installed-wheel tests, source manifest and deterministic CLI replay. | Correctness of every untested code path or formal verification of the analytic proof. |
| Selected arithmetic and factorial identities have Lean proofs. | [Formal checkpoints](proofs/formal/README.md), statement mapping and pinned toolchain. | Those algebraic checkpoints alone do not establish Gaussian, integration, covariance or Markov arguments, or physical validation. |
| A finite complex phase sum has a formalized first intensity moment under a centered joint Gaussian law. | [Gaussian first-moment scope](proofs/formal/analytic/SCOPE.md#gaussian-first-intensity-moment): explicit full PSD covariance, arbitrary fixed complex weights, real phase scale, proved integrability and finite ordered-pair expansion. Singular covariance and an empty index type are included. | Concrete graph covariance/COM identification, physical Gaussian adequacy, executable moment-polynomial identification, temporal/observation laws or the classifier theorem. |
| Every natural raw intensity moment has a formalized full-covariance charge formula. | [Natural-moment scope](proofs/formal/analytic/SCOPE.md#every-natural-raw-intensity-moment): nine declarations and two definitions retain ordered tuple multiplicities, take the real part after the complex product and prove finite-measure integrability. Order zero and empty/singular cases are included. | Identification of graph covariance, executable occupation histograms/variogram tables or complete polynomial coefficients, temporal laws or the classifier. |
| Standard deviation changes by at most the L2 size of a coupled perturbation. | [Analytic Lean proof](proofs/formal/analytic/README.md), with explicit finite moments on a common probability space; also derives L3-based variance enclosures. | Construction of the coupling, numerical perturbation bounds, third-cumulant separation or the full classifier theorem. |
| The demo displays the original `verify` and `long-exposure-v1` exact-geometry certificates and clean geometry. | Deterministic generation from those recomputed installed certificates; explicit separation of exact fractions and floating-point rendering. | Measurement data, a browser proof checker, or a certificate for its illustrative motion snapshots. |
| The optional prototype generates and inspects declared synthetic processes. | [Model and limits](../prototype/MODEL_AND_LIMITS.md), source/reference bindings, repeated runs and recomputed covariance diagnostics. | A validated apparatus, calibrated diagnostic false-alarm rates, a test of the finite-window classifier or a guarantee for stress cases outside the theorem. |

| Additional formal claim | Evidence and scope | What this does not establish |
| --- | --- | --- |
| Every natural physical intensity moment has an exact mathematical charge histogram. | [Physical substitution and finite fibers](proofs/formal/analytic/SCOPE.md#physical-parameter-substitution): nonnegative strength, full PSD covariance, nominal unit phases and exact fiber multiplicities with mass `n^(2r)`. | Correctness of executable convolution, phase-residue/exponent grouping or complete polynomial coefficients. |
| The two literal nine-point covariance matrices are PSD, trace-normalized and give almost-sure zero COM. | [Concrete covariance proofs](proofs/formal/analytic/SCOPE.md#concrete-nine-point-covariance): threshold `15/2`, incidence Gram and centered inverse identities, real transport and a Gaussian null-direction lemma. | A named library pseudoinverse identification, generic all-graph/full-support result, physical covariance/OU preparation or the full classifier. |

## Evidence boundaries

- The exact-geometry exposure cap 0.01 remains unresolved after nuisance
  propagation and has no allocated count. Position uncertainty at cap 0.001
  is an evaluated stricter domain with a smaller sufficient count than the
  selected 0.01 profile; it is not an implicit runtime choice.
- The geometry scenarios are not nested because their frequency tolerances
  differ. All nuisance settings remain fixed during each acquisition.
  Neither arbitrary parameter mixtures nor physical rate calibration follow
  from a bound on integrated gain and background.
- The repository contains a mathematical model and computations, not experimental
  measurements. No apparatus has been validated by these files.
- The complete theorem is not formally verified in a proof assistant.
  The formal checkpoints identify their exact statements. The generic
  Gaussian characteristic, first-intensity integral and generic natural
  raw moments, physical strength substitution, mathematical charge fibers
  and the two literal nine-point PSD/COM covariances are included.
  Combined executable histogram/polynomial identification, Markov
  dynamics and their application to the full classifier remain separate.
- Separate implementations and alternative arithmetic checks are useful error
  controls. They are not independent human peer review.
- No claim of novelty, priority, patentability or a new physical law is made.
  [Related work and failure regimes](proofs/scope-and-related-work.md) are essential
  context.
- Security tools report findings within their rules, databases and scan scope.
  A clean scan does not prove that software has no vulnerabilities. Community
  scores measure selected maintenance signals, not scientific truth.
- Development and demonstration results apply to the exact revision and model
  they identify. An extension is not covered merely because an earlier theorem passed.

## Separate calibrated iid channel

The [calibrated count derivation](../review/MATHEMATICS.md#selected-63-point-channel)
uses the 63-point geometry with exact covariance and frequency, instantaneous
iid snapshots, 0 < β ≤ 10⁻¹⁶, known shared mean-100 reference calibration,
zero background and independent conditional Poisson observations of I/(βω²).
These assumptions differ from the robust OU-window contracts above.

| Claim | Evidence and scope | What this does not establish |
| --- | --- | --- |
| At least 9,188,577 observations are necessary for both class errors at most 5%. | Outward affinity enclosure, analytic finite-motion transfer, product-law total-variation bound and exact rational exclusion gate through N = 9,188,576. | Achievability at the lower bound, an optimal count or a lower bound for the robust OU-window contracts. |
| 35,943,631 observations suffice for both class errors at most 5%. | The fixed product-surrogate-likelihood rule, affinity upper bound, finite-motion transfer and exact rational risk gate. | A numerical classifier implementation, finite-exposure or temporal-dependence robustness, unknown calibration, practical acquisition budget or experimental validation. |

The [internal cross-check kit](../review/README.md) contains the separate Arb
calculation and saved-witness validator. Changing β at fixed normalized gain
changes the raw-intensity gain. All counts remain conditional on the stated
model and analytic dependencies.

## Separate nine-point model

The [nine-point proof](proofs/nine-point-moments.md) and `small-pair` command
use fixed permanent nominal graphs, centered Gaussian displacement, exact
frequency and calibrated intensity. Their claims do not inherit the
63-point count theorem's detector or robustness allowances.

| Claim | Evidence and scope | What this does not establish |
| --- | --- | --- |
| The two leading intensity laws agree, including their common-clock OU path laws. | Exact projected covariance powers, a shared characteristic polynomial and Gaussian covariance determination. | Equality of the exact nonlinear intensity laws. |
| The first two exact intensity moments cannot both agree at any shared finite positive strength. | Generated complete Bezout identity and strictly positive mean cofactor on `0<t<1`. | A uniform global gap or separation across arbitrary different strengths. |
| The mean crosses exactly once; skewness crosses at least twice. | Rational Sturm chain, positive variance/cumulant Bernstein coefficients and exact cross-product signs. | The exact total number of skewness roots or equality of laws at a single-statistic crossing. |
| A fixed combination of the first two raw moments separates independently uncertain fixed strengths in a restricted band. | Full Bernstein enclosures give `E_A[I²-cI]-E_B[I²-cI]>7/100000` for `t_A,t_B` in `[831/1024,833/1024]`. All five radii and three wider unresolved tests remain visible. | Unknown gain/background invariance, global unknown-strength separation, exposure robustness or finite-sample error control. |
| A small shared-strength interval has a positive skewness gap. | Degree-16 Taylor expansion with a global exponential remainder and complete polynomial propagation. | Arbitrary strength; the larger cap `1/10` remains unresolved. |

## Separate complete-graph counterexample

The [phase-permutation proof](proofs/phase-permutation.md) uses the same
nine-point geometries with a different permanent graph: threshold `28`
connects every pair, whereas the positive finite-motion result uses `15/2`.
At exact frequency `2*pi/3`, complete-graph OU motion with shared strength
and clock gives identical exact intensity-path laws, despite nonzero relative
motion. A common conditional observation kernel preserves this equality.
Every binary rule on those identical observation laws has equal-prior error
`1/2` and maximum class error at least `1/2`.

The standalone source-documentation checker verifies finite phase and matrix
identities; the analytic argument supplies the whole-path conclusion.
This is neither an arbitrary-frequency assertion nor equality for every
choice of dynamics, strengths, clocks or observation channels. It does not
alter the threshold-`15/2` or 63-point certificates.

## Correction policy

Report a missing assumption, false inequality, invalid inference or failing
reproduction as an issue with a minimal argument. Corrections must update the
proof, implementation, tests, manifest and this ledger as applicable. Preserve
the public history and explain which earlier claims are affected. Do not silently
replace published evidence or turn an inconclusive bound into a positive result.
