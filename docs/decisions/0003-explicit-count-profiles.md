# 3. Add explicit count profiles without replacing earlier certificates

Date: 2026-10-20

Status: accepted

## Context

Two new proof ingredients change different parts of the certificate.
Signed covariance-kernel derivatives and rank-two majorization tighten
the leading exposure-moment bounds. A cancellation-aware polynomial bound
then allocates separate variance and standardized third-cumulant errors
using the available shape gap. Each combination requires a new threshold
and sufficient count.

The existing `verify`, `coordinate-count` and `exposure-count` commands
already identify distinct, reproducible parameter and estimator contracts.
Silently changing their count, threshold or exposure domain would make
earlier outputs and the original demo ambiguous.

## Decision

Add the fresh-only API
`build_count_certificate(*, profile, scenario="exact_geometry")`
and the CLI
`count --profile PROFILE --scenario SCENARIO --output PATH`.
Require a versioned profile from a fixed allowlist. Do not select a
default "best" profile or accept arbitrary combinations of parameter caps.

| Profile | Exact-geometry exposure cap | Position-uncertainty exposure cap | Moment route |
| --- | ---: | ---: | --- |
| `short-exposure-v1` | `1e-5` | `1e-5` | Existing linear exposure theorem |
| `long-exposure-v1` | `0.001` | `0.01` | Signed kernel bounds, all 512 time cells and cell-wise nuisance propagation |

Both profiles use the complete cancellation-aware estimator polynomial
and fresh shape allowances, threshold, dependence factor and risk sum.
Their physical models and finite-sample claims are described in the
[profile proof](../proofs/profiled-counts.md).

Preserve all three earlier computing commands and fresh APIs, including
their defaults, parameters, numerical stages and classifier thresholds.
A new release manifest may change provenance hashes; it does not change
those earlier scientific outputs. The offline demo continues to display
the original `verify` certificate.

## Envelope and numerical contract

The new envelope identifies `profile` and `scenario`, complete selected
parameters, a freshly recomputed original reference core and its content
digest, the selected moment evidence, observation bounds and the new
allocation. The reference core is provenance and baseline evidence; its
old threshold and count are not the selected result.

For the long profile, retain complete evidence for all 512 cells in each
class, including their rational cover and nuisance propagation. Unite
class A and class B independently. Retain the resulting skewness union
separately from pooled variance and raw-moment bounds; do not reconstruct
shape separation by dividing a global independent moment rectangle.

Use standard-library runtime code, bundled mathematical inputs and bounded
exact rational parsing/serialization. Preserve the earlier 72-place
arithmetic semantics and use a separate fixed 96-place kernel helper.
No private research output, historical execution receipt or network
lookup is a runtime dependency.

The recorded search is a deterministic feasible-witness construction,
informed by preceding bounds. It is not a global optimizer, a blind
experiment or a preregistered selection.

Saved-file `summary` must remain prominently **UNVERIFIED**. Internal
consistency, source compatibility and witness checks do not authenticate
an externally supplied result or validate its physical assumptions.
Computing commands continue to refuse existing output paths.

## Evaluated domains that are not selected profiles

The exact-geometry exposure cap `0.01` is unresolved after nuisance
propagation and receives no threshold or count. This is not an
impossibility result.

Position uncertainty at cap `0.001` has a separately evaluated smaller
sufficient count than the selected `0.01` profile. The selected profile
permits a wider exposure range; it is not chosen by minimizing count.
The extra evaluated domain is documented without becoming an implicit
runtime choice.

The geometry scenarios are also not nested. Permitting position error
requires a 100-fold tighter frequency cap. Counts from different
scenarios do not isolate the effect of position uncertainty.

## Acceptance and consequences

Before publication, build a fresh installed artifact and reproduce all four
profile/scenario combinations from bundled inputs. Check the complete
new witnesses against independently reviewed reference calculations or
justify any outward precision difference. Preserve the complete earlier
scientific outputs, test unknown profiles and tampered summaries, and
verify all cell coverage, sign, denominator and risk conditions.

Replay both optional analytic Lean files with the pinned dependencies.
Their nine original analytic declarations and four new deterministic
sensitivity statements remain narrower than the full theorem.

The new counts remain conditional sufficient bounds for a particular
classifier. They establish no necessary sample size, practical acquisition
budget, apparatus validation, scientific priority, independent human peer
review or formal proof of the complete analytic argument.
