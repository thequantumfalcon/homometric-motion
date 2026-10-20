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
5. [Scope and related work](scope-and-related-work.md) states the essential
   strength floor, unresolved directions, finite-error limitations and close
   prior work.
6. [Formal checkpoints](formal/README.md) distinguishes six mapped finite
   arithmetic statements, six universal polynomial identities and general
   analytic variance-stability lemmas from the full probabilistic theorem.

The package recomputes two explicitly named parameter chains from its own mathematical
resources. Its exact rational outputs and integer interval checks support the
stated conditional inequalities. They are not physical measurements,
independent human peer review or a formalization of the full theorem.
