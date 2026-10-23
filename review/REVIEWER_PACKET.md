# Internal cross-checks for external review

**Review status: internal cross-checks; external mathematical review pending.**
Publication of this packet implies no endorsement. The results concern
specified stochastic models. Scientific novelty and physical realizability
remain open. The [research provenance statement](PROVENANCE.md) explains
how the work was developed and the limits of its verification.

## The questions

Can exact motion statistics distinguish configurations whose clean static
diffraction agrees? For the fixed models below, does the mathematical argument
and its implementation justify the stated conditional conclusions?

There are two separate constructions. The nine-point construction gives exact
moment identities and a pointwise distinction of laws. The selected 63-point
construction gives conditional statistical bounds with a detector model.
Their strengths, frequencies, covariance matrices and observation assumptions
must not be interchanged.

## Claims, assumptions and evidence

| Claim | Essential assumptions | Evidence in this kit | Review boundary |
| --- | --- | --- | --- |
| The nine-point configurations are homometric and noncongruent. | Exact listed positions; identical scatterers; scalar coherent amplitude. | Sage compares full signed-difference multisets and rules out translation/reflection. | Static equality follows from the elementary Fourier expansion, not a measurement. |
| Their exact first two intensity moments cannot both agree at any shared finite positive strength. | Permanent threshold-15/2 graph; centered Gaussian motion with `D=9 L+/tr(L+)`; exact frequency `2*pi/3`; same strength and intensity units. | All six moment polynomials are rebuilt. Sage checks the mean factorization and a Bezout identity. | The Gaussian moment identity and implication from moments to laws must be reviewed; no nine-point sample bound is supplied. |
| The covariance exponent is a nonnegative integer multiple of `9/158` on every zero-sum integer charge, with bound `80*r^2` for order r. | The same nine-point covariance; charges are sums of r ordered pair charges. | Exact reduced quadratic coefficients, positive principal minors and all pair-charge cross terms. | The all-order conclusion uses the short algebraic argument in MATHEMATICS.md; it is not a new Lean proof. |
| In the selected 63-point channel, at least 9,188,577 iid observations are necessary and 35,943,631 are sufficient for both class errors at most 5%. | Exact shifted geometry and Gaussian covariance; known shared gain; zero background; `0<beta<=10^-16`; instantaneous iid normalized counts; independent conditional Poisson observations. | Fresh Arb geometry, complete count convolution through 20,000, analytical tail bound, affinity enclosure, and exact rational testing gates. | The finite-motion transfer and testing inequalities are analytic dependencies, stated and derived in MATHEMATICS.md. These integers do not identify the optimum. |
| The public project contains broader nuisance/OU/exposure certificates and partial formal proofs. | Each public theorem's own stated domain. | Links below, pinned to a specific revision. | Those full calculations and the Lean project are not rerun by this compact kit. |

## What a PASS means

The program's finite identities, numerical enclosures and declared controls
passed in the recorded environment. A reviewer should separately check that
the mathematical statements match the intended observable and that every
analytic implication is sound. The programs contain no physical measurements.

The reconstructions are informed by existing results. The mean-100 channel,
the strength cap and the candidate sample counts were known before this check.
This is a reproduction, not blinded discovery or parameter selection. Counts
are checked as fixed witnesses; no global optimization claim is made.

## Known limitations and negative evidence

- The nine-point mean crosses once in the open strength parameter interval;
  it cannot supply a fixed global ordering. The public work also retains
  skewness crossovers.
- A different complete-graph motion model makes the same nine-point pair's
  exact intensity-path laws identical at the selected frequency. Motion does
  not universally resolve homometry.
- The selected 63-point bound does not cover unknown calibration, frequency or
  covariance errors, finite exposure, temporal dependence, or drift.
- The normalized observation uses `I/(beta*omega^2)`. Keeping its gain fixed
  while beta decreases changes the corresponding gain on raw intensity.
- No acquisition time, photon dose, apparatus feasibility, optimal estimator,
  universal uniqueness theorem or established novelty follows.

## Focused review requests

1. Check the Gaussian expansion and all normalization factors, especially the
   different frequencies and the factor `beta*omega^2/2` in the nine-point model.
2. Inspect multiplicities, diagonal terms and phase cancellation in the Sage
   reconstruction. Compare with the production charge-convolution method.
3. Check the zero-sum lattice argument and the inference from a Bezout identity
   to noncoincidence for every `0<t<1`.
4. Check the Poisson-mixture curvature bound at zero mean, the finite-motion
   transfer, the omitted affinity tail, and the necessary/sufficient gates.
5. Identify related prior results and determine what, if anything, is new.
6. Explain which assumptions could be calibrated and tested in a physical system.

## Reference revision

All repository links below are fixed at the same commit:

- [Claim ledger](https://github.com/thequantumfalcon/homometric-motion/blob/509db87a5a8fe1f6562590133eff9d7db142b227/docs/claims.md)
- [Nine-point proof](https://github.com/thequantumfalcon/homometric-motion/blob/509db87a5a8fe1f6562590133eff9d7db142b227/docs/proofs/nine-point-moments.md)
- [63-point geometry and motion](https://github.com/thequantumfalcon/homometric-motion/blob/509db87a5a8fe1f6562590133eff9d7db142b227/docs/proofs/geometry-and-motion.md)
- [Complete-graph counterexample](https://github.com/thequantumfalcon/homometric-motion/blob/509db87a5a8fe1f6562590133eff9d7db142b227/docs/proofs/phase-permutation.md)
- [Formalization scope](https://github.com/thequantumfalcon/homometric-motion/blob/509db87a5a8fe1f6562590133eff9d7db142b227/docs/proofs/formal/analytic/SCOPE.md)

Tool references: [SageMath](https://doc.sagemath.org/html/en/tutorial/),
[Python-FLINT](https://python-flint.readthedocs.io/en/latest/),
[Arb real-ball arithmetic](https://python-flint.readthedocs.io/en/latest/arb.html).
