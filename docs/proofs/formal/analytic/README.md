# Analytic robustness and cumulant sensitivity

This separate Lean project proves nine general standard-deviation and variance
declarations and four deterministic cumulant-sensitivity statements. It
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

[SCOPE.md](SCOPE.md) maps both files to the larger argument and lists the
obligations left open.

## Replay

Use **Lean 4.35.0** and its matching Lake. The included `lean-toolchain`,
`lakefile.toml` and `lake-manifest.json` pin the toolchain, mathlib commit
and all eight transitive dependency commits. From this directory:

```text
lake exe cache get Mathlib.Probability.Moments.Variance Mathlib.MeasureTheory.Function.L2Space Mathlib.Basic.Real.Basic Mathlib.Tactic.Linarith Mathlib.Tactic.Ring
lake env lean --trust=0 StandardDeviationContinuity.lean
lake env lean --trust=0 CumulantSensitivity.lean
```

The first command obtains the pinned source dependencies and the relevant
official mathlib cache. It requires network access on an uncached machine.
The next commands check the two source files; `--trust=0` requests type
checking of imported modules as well. A successful run exits zero and prints
nine axiom lists for the first file and four for the second, each exactly:

```text
[propext, Classical.choice, Quot.sound]
```

The sources include no `sorry`, `native_decide`, or new axiom asserting a
desired result. Do not treat a nonzero exit, an unresolved goal, or an
unexpected axiom as an accepted proof. The source declarations identify the
explicit hypotheses.

Both modules are also listed as default targets in `lakefile.toml`, so
`lake build` includes both. That build command does not replace the explicit
`--trust=0` replay and axiom inspection above.

The source manifest binds this small project. Dependencies and generated
`.lake` files are not distributed with it. Updating the toolchain,
dependency lock, source or documentation creates a new revision requiring
review and the applicable proof replay.

## What the check establishes

The original nine declarations were accepted by Lean 4.35.0 with
`--trust=0`; a separately altered, intentionally overstrong zero-bound
statement was rejected. The four additional statements have the separate
replay command above. All are checked by **Lean's own kernel**, using
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
