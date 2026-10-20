# Analytic robustness, Gaussian intensity and polynomial witnesses

This separate Lean project proves nine general standard-deviation and variance
declarations, four deterministic cumulant-sensitivity statements, five
explicit polynomial statements for the nine-point construction, and thirteen
Gaussian phase, integrability and first-intensity declarations. A fifth
file adds nine proved natural-moment declarations and two definitions.
There are forty proved declarations in total. This project
**does not formalize the complete discrimination theorem or validate its
physical model**.

`StandardDeviationContinuity.lean` retains the nine original statements.
For real random variables on the same probability space, with explicit
finite second moments, its main theorem proves

```text
|sd(X) - sd(Y)| <= sqrt(E[(X-Y)^2]).
```

It also proves centering contraction, the probability-space `L3 -> L2`
comparison, and the variance interval obtained from an `L2` or `L3`
perturbation bound. No independence or equality of means is assumed.

`CumulantSensitivity.lean` adds four statements: the exact cubic
perturbation identity, the identity for its first-moment linear coefficient,
an absolute coefficient bound using both variance endpoints, and an abstract
counterexample to dropping the upper-variance branch. These are algebraic
and order statements over real numbers. They do not introduce a probability
model or prove the final sample-size bound.

[SCOPE.md](SCOPE.md) maps all five files to the larger argument and lists the
obligations left open.

`NinePointBezout.lean` proves a complete integer-coefficient Bezout identity,
its no-common-zero consequence, a mean-factorization identity, positivity
of its cofactor on `0<t<1`, and noncoincidence of the two resulting
polynomials on that interval. Its connection to Gaussian intensity moments
requires the separate [nine-point proof](../../nine-point-moments.md).
No equality-of-law, strength-band, root-count or detector theorem is formalized
by these five statements.

`GaussianIntensity.lean` proves the first intensity moment of a finite complex
amplitude under a centered joint Gaussian with explicit full PSD covariance.
For fixed complex weights, real `a`, and `Y ~ N(0,D)`, it gives

```text
E |sum_i z_i exp(i*a*Y_i)|^2
  = sum_i sum_j Re(z_i*conj(z_j))
      * exp(-a^2*(D_ii+D_jj-D_ij-D_ji)/2).
```

The file contains three Gaussian phase prerequisites and ten finite-intensity
declarations. It proves genuine intensity integrability, including under
any finite measure, before exchanging finite sums and integrals. Singular
covariance, diagonal pairs, an empty index type and arbitrary fixed complex
weights are included; independent coordinates and a clean-amplitude null
are not required. This is a known generic identity, not a novelty claim.
It does not identify the particular graph covariance or prove the Gaussian
physical model. The generic higher-moment extension is described below.

## Every natural raw intensity moment

`GaussianMoments.lean` imports the unchanged first-intensity module. For each
natural order `r`, it defines an ordered tuple of pairs
`p : Fin r -> (index x index)`, its charge and its complex weight:

```text
u_p = sum_k (e_(p(k).1) - e_(p(k).2))
w_p = product_k (z_(p(k).1) * conj(z_(p(k).2)))
E[I(Y)^r] = sum_p Re(w_p) * exp(-a^2 * u_p^T D u_p / 2).
```

Here `I(y)=|sum_i z_i exp(i*a*y_i)|^2`, the weights are fixed complex
numbers, `a` is real, and `Y` has a centered joint Gaussian law with an
explicit full PSD covariance `D`. Ordered tuples preserve multiplicities;
the real part is taken after the full complex product. Integrability of
the actual real power and its complex embedding is proved under every
finite measure before the Gaussian expectation is evaluated.

The formula includes order zero, repeated or diagonal pairs, an empty
index type, correlated or singular covariance, and non-unit weights.
It does not identify the graph covariance or the executable histogram and
polynomial enumeration. The [detailed scope](SCOPE.md#every-natural-raw-intensity-moment)
maps all nine declarations and those application gaps. This is a generic
identity, with no novelty or physical-validation claim.

## Replay

Use **Lean 4.35.0** and its matching Lake. The included `lean-toolchain`,
`lakefile.toml` and `lake-manifest.json` pin the toolchain, mathlib commit
and all eight transitive dependency commits. From this directory:

```text
lake exe cache get Mathlib.Probability.Moments.Variance Mathlib.MeasureTheory.Function.L2Space Mathlib.Basic.Real.Basic Mathlib.Probability.Distributions.Gaussian.Multivariate Mathlib.Tactic.Linarith Mathlib.Tactic.Ring Mathlib.Tactic.NormNum Mathlib.Tactic.Positivity
lake build GaussianIntensity
lake env lean --trust=0 StandardDeviationContinuity.lean
lake env lean --trust=0 CumulantSensitivity.lean
lake env lean --trust=0 NinePointBezout.lean
lake env lean --trust=0 -o .lake/build/lib/lean/GaussianIntensity.olean GaussianIntensity.lean
lake env lean --trust=0 GaussianMoments.lean
```

The first command obtains the pinned source dependencies and the relevant
official mathlib cache. It requires network access on an uncached machine.
`lake build GaussianIntensity` prepares the local module and its build
directory. The following five source replays use `--trust=0`, which requests
type checking of imported modules as well. The explicit `-o` replaces the
first-intensity object in Lake's library search path with the freshly checked
one before the final import. Run these commands in the stated order from
this directory. Each replay exits zero and prints nine axiom lists for the
first file, four for the second, five for the third, thirteen for the fourth
and nine for the fifth, each exactly:

```text
[propext, Classical.choice, Quot.sound]
```

The sources include no `sorry`, `native_decide`, or new axiom asserting a
desired result. Do not treat a nonzero exit, an unresolved goal, or an
unexpected axiom as an accepted proof. The source declarations identify the
explicit hypotheses.

All five modules are listed as default targets in `lakefile.toml`, so
`lake build` includes all five. That build command does not replace the explicit
`--trust=0` replay and axiom inspection above.

The source manifest binds this small project. Dependencies and generated
`.lake` files are not distributed with it. Updating the toolchain,
dependency lock, source or documentation creates a new revision requiring
review and the applicable proof replay.

## Reconstruct the nine-point coefficient mapping

With this revision's wheel installed, run the following from an empty
working directory, substituting the checkout path:

```sh
python -I /path/to/checkout/docs/proofs/formal/analytic/build_nine_point_checkpoint.py --output-dir new-nine-point-checkpoint
python -I /path/to/checkout/docs/proofs/formal/analytic/build_nine_point_checkpoint.py --check /path/to/checkout/docs/proofs/formal/analytic
```

Each command checks the installed source manifest and freshly rebuilds
the complete fixed nine-point certificate. It maps every polynomial
coefficient, re-expands the identities in Python, and emits or compares
`NinePointBezout.lean` and `mapping.json`. It reads no private workspace
record or supplied saved certificate. The first command refuses existing
output paths; the second writes nothing.

The mapping includes the generator, installed-source and full-certificate
hashes, complete coefficient vectors and field pointers. A source revision
may change these bindings even when the mathematical coefficients are
unchanged. A failed comparison requires investigation and a reviewed new
mapping; it must not be explained away by regenerating a manifest.
The generator does not run Lean. Execute the separate kernel replay above
and inspect its exit code and five axiom reports.

## What the check establishes

The original nine declarations were accepted by Lean 4.35.0 with
`--trust=0`; a separately altered, intentionally overstrong zero-bound
statement was rejected. The four sensitivity statements, five nine-point
polynomial statements, thirteen first-intensity declarations and nine
natural-moment declarations have separate replay commands above.
All are checked by **Lean's own kernel**, using
mathlib at commit `56a005855ea17e0b0958f73ec801ae140b0a1679`.
This is not a successful replay by an independently implemented proof checker.

An optional bundled Lean4Lean probe reported incompatible headers when
reading bundled standard-library `.olean` files, so it provided no
additional target verification. No alternate-checker success is included
in this claim. The upstream
[Lean4Lean description](https://github.com/digama0/lean4lean) also explains
that its implementation is derived from Lean's C++ kernel, so even
successful checks should not be described as wholly independent
implementations.

The audited axioms are standard Lean foundations, not assumptions about
Gaussian motion, calibration or experimental accuracy. Formal correctness
is conditional on the formal statement, those foundations and the
checker/runtime behaving as specified. It does not establish novelty,
empirical model adequacy, optimal sample size or independent human peer
review.

Mathlib is obtained from its
[official pinned release](https://github.com/leanprover-community/mathlib4/tree/56a005855ea17e0b0958f73ec801ae140b0a1679)
and retains its own Apache-2.0 license and dependency notices. This project
distributes no toolchain or library binaries.
