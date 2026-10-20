# Analytic robustness, cumulant sensitivity and polynomial witnesses

This separate Lean project proves nine general standard-deviation and variance
declarations, four deterministic cumulant-sensitivity statements and five
explicit polynomial statements for the nine-point construction. It
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

[SCOPE.md](SCOPE.md) maps all three files to the larger argument and lists the
obligations left open.

`NinePointBezout.lean` proves a complete integer-coefficient Bezout identity,
its no-common-zero consequence, a mean-factorization identity, positivity
of its cofactor on `0<t<1`, and noncoincidence of the two resulting
polynomials on that interval. Its connection to Gaussian intensity moments
requires the separate [nine-point proof](../../nine-point-moments.md).
No equality-of-law, strength-band, root-count or detector theorem is formalized
by these five statements.

## Replay

Use **Lean 4.35.0** and its matching Lake. The included `lean-toolchain`,
`lakefile.toml` and `lake-manifest.json` pin the toolchain, mathlib commit
and all eight transitive dependency commits. From this directory:

```text
lake exe cache get Mathlib.Probability.Moments.Variance Mathlib.MeasureTheory.Function.L2Space Mathlib.Basic.Real.Basic Mathlib.Tactic.Linarith Mathlib.Tactic.Ring Mathlib.Tactic.NormNum Mathlib.Tactic.Positivity
lake env lean --trust=0 StandardDeviationContinuity.lean
lake env lean --trust=0 CumulantSensitivity.lean
lake env lean --trust=0 NinePointBezout.lean
```

The first command obtains the pinned source dependencies and the relevant
official mathlib cache. It requires network access on an uncached machine.
The next commands check the three source files; `--trust=0` requests type
checking of imported modules as well. A successful run exits zero and prints
nine axiom lists for the first file, four for the second and five for the
third, each exactly:

```text
[propext, Classical.choice, Quot.sound]
```

The sources include no `sorry`, `native_decide`, or new axiom asserting a
desired result. Do not treat a nonzero exit, an unresolved goal, or an
unexpected axiom as an accepted proof. The source declarations identify the
explicit hypotheses.

All three modules are listed as default targets in `lakefile.toml`, so
`lake build` includes all three. That build command does not replace the explicit
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
statement was rejected. The four sensitivity statements and five nine-point
polynomial statements have separate replay commands above.
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
