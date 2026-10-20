# Mathematical certificate

Read the proofs in this order:

1. [Geometry and motion](geometry-and-motion.md) defines the two configurations,
   proves clean homometry and noncongruence, constructs the exact covariance,
   and derives uniform finite-motion moment bounds.
2. [Robustness and counts](robustness-and-counts.md) adds covariance uncertainty,
   compatible weighted OU dynamics, finite exposure, bounded fixed frequency
   error and the finite-window classifier bound.
3. [Position uncertainty](position-uncertainty.md) proves a separate scenario
   for fixed imperfect mean positions, with a smaller frequency cap and a
   freshly computed finite-window bound.
4. [Coordinate-count extension](coordinate-counts.md) reduces the sufficient
   count by allocating separate error tolerances to the estimated moments,
   with the classifier and physical assumptions unchanged.
5. [Linear exposure extension](linear-exposure.md) allows longer exposures by
   bounding averaged quadratic moments directly, retaining finite-motion
   parity errors and recomputing nuisance and count bounds.
6. [Signed kernel exposure bounds](signed-kernel-exposure.md) retains signed
   derivatives, bounds their remainders, proves a rank-two majorization
   inequality, and propagates all 512 time cells through nuisance bounds.
7. [Explicit count profiles](profiled-counts.md) combines the selected moment
   route with a cancellation-aware full estimator polynomial, separate actual
   shape errors, a new threshold and an exact finite-window risk witness.
8. [Scope and related work](scope-and-related-work.md) states the essential
   strength floor, unresolved directions, finite-error limitations and close
   prior work.
9. [Formal checkpoints](formal/README.md) distinguishes six mapped finite
   arithmetic statements, six universal factorial identities, nine analytic
   variance declarations, four deterministic sensitivity statements, five
   explicit nine-point polynomial statements and thirteen generic Gaussian
   phase, integrability and first-intensity declarations, plus nine
   natural-moment declarations, seven physical-parameter statements,
   five charge-histogram statements and forty-nine concrete covariance
   statements, from the full probabilistic theorem.

The separate [nine-point moment construction](nine-point-moments.md) uses
exact instantaneous intensity with fixed nominal covariance and frequency.
It proves equality of leading intensity-process laws, noncoincidence of the
first two exact moments at every shared finite positive strength, individual
statistic crossovers, and a local projection gap across independently uncertain
fixed strengths. It has no detector channel or count guarantee. It is not
another parameter profile of the 63-point certificate.

The [phase-permutation counterexample](phase-permutation.md) changes the same
nine-point pair to a common complete-graph interaction rule. Its exact nonlinear
intensity paths agree at the selected frequency under shared strength, clock
and observation settings. It identifies a limitation of unrestricted dynamics
claims without changing the threshold-`15/2` theorem.

The package recomputes two geometry/calibration scenarios with explicitly named
count methods and versioned profiles from its own mathematical resources.
The three earlier commands retain their parameter, threshold and numerical
contracts; neither new profile is selected implicitly.
Its exact rational outputs and integer interval checks support the
stated conditional inequalities. They are not physical measurements,
independent human peer review or a formalization of the full theorem.
