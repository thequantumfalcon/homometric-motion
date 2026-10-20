# Analytic standard-deviation robustness

This separate Lean project proves a general analytic step used in variance robustness arguments. It goes beyond finite arithmetic checkpoints, but it **does not formalize the complete discrimination theorem or validate its physical model**.

For real random variables on the same probability space, with explicit finite second moments, the main theorem proves

```text
|sd(X) - sd(Y)| <= sqrt(E[(X-Y)^2]).
```

It also proves centering contraction, the probability-space `L3 -> L2` comparison, and the variance interval obtained from an `L2` or `L3` perturbation bound. No independence or equality of means is assumed. [SCOPE.md](SCOPE.md) maps this result to the larger argument and lists the obligations left open.

## Replay

Use **Lean 4.35.0** and its matching Lake. The included `lean-toolchain`, `lakefile.toml` and `lake-manifest.json` pin the toolchain, mathlib commit and all eight transitive dependency commits. From this directory:

```text
lake exe cache get Mathlib.Probability.Moments.Variance Mathlib.MeasureTheory.Function.L2Space Mathlib.Tactic.Linarith Mathlib.Tactic.Ring
lake env lean --trust=0 StandardDeviationContinuity.lean
```

The first command obtains the pinned source dependencies and the relevant official mathlib cache. It requires network access on an uncached machine. The second checks the source; `--trust=0` requests type checking of imported modules as well. A successful run exits zero and prints nine axiom lists, each exactly:

```text
[propext, Classical.choice, Quot.sound]
```

The source includes no `sorry`, `native_decide`, or new axiom asserting the desired bound. Do not treat a nonzero exit, an unresolved goal, or an unexpected axiom as an accepted proof. `#check` commands print the principal statements and their explicit probability/moment assumptions.

The source manifest binds this small project. Dependencies and generated `.lake` files are not distributed with it. Updating the toolchain, dependency lock or source creates a new revision requiring replay.

## What the check establishes

The nine declarations were accepted by Lean 4.35.0 with `--trust=0`; a separately altered, intentionally overstrong zero-bound statement was rejected. This is verification by **Lean's own kernel**, using mathlib at commit `56a005855ea17e0b0958f73ec801ae140b0a1679`. It is not a successful replay by an independently implemented proof checker.

An optional bundled Lean4Lean probe reported incompatible headers when reading bundled standard-library `.olean` files, so it provided no additional target verification. No alternate-checker success is included in this claim. The upstream [Lean4Lean description](https://github.com/digama0/lean4lean) also explains that its implementation is derived from Lean's C++ kernel, so even successful checks should not be described as wholly independent implementations.

The audited axioms are standard Lean foundations, not assumptions about Gaussian motion, calibration or experimental accuracy. Formal correctness is conditional on the formal statement, those foundations and the checker/runtime behaving as specified. It does not establish novelty, empirical model adequacy, optimal sample size, or independent human peer review.

Mathlib is obtained from its [official pinned release](https://github.com/leanprover-community/mathlib4/tree/56a005855ea17e0b0958f73ec801ae140b0a1679) and retains its own Apache-2.0 license and dependency notices. This project distributes no toolchain or library binaries.
