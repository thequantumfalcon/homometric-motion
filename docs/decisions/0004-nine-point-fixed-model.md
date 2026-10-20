# 4. Publish a separate fixed nine-point moment certificate

Date: 2026-10-20

Status: accepted; publication requires the verification gates below

## Context

A smaller clean-homometric pair has equal leading quadratic intensity-process
laws under a common clock. Its exact finite-motion laws nevertheless differ
at every common calibrated finite positive strength. Individual mean and
skewness orderings reverse, so neither statistic alone has one global ordering.
These statements have different assumptions from the 63-point count theorem.

## Decision

Provide a parameter-free `build_small_pair_certificate()` and a separate
`small-pair --output PATH` command. Reconstruct the fixed geometry, permanent
graphs, covariance matrices and exact moment polynomials using standard-library
arithmetic. Generate the full polynomial witnesses at runtime; do not load
private results, stored successful coefficients or historical receipts.

The versioned `nine_point_finite_motion_v1` envelope contains the model,
geometry, equal-leading-law evidence, complete finite-motion moments,
mean-root certificate, joint-moment Bezout identity, shape sign certificates,
declared finite-motion remainder bounds and a separate local projection
certificate for independently uncertain fixed strengths. Retain all five
projection bands, unresolved bounds and all predeclared sign evaluations.
It contains no embedded 63-point count
certificate and no nine-point observation budget.

Preserve the earlier APIs, commands, parameters and complete scientific
outputs. Adding package modules changes source provenance, not those earlier
numeric results. The existing demo and synthetic instrument keep their stated
reference models; this extension does not silently change either.

Saved-record display compares the scientific record with a fresh reconstruction
under the installed model and checks source compatibility when provenance is
present. Its label must distinguish that calculation from authentication of
the supplied record, independent validation of the source and physical
validation. It must not say that no computation occurred.

## Acceptance

- Reconstruct every claimed polynomial, sign and identity from the fixed inputs.
- Independently compare the full witnesses, permitting equivalent exact
  normalizations only when the resulting identities are rechecked.
- Test the mean and skewness crossovers, the noncoincidence certificate and
  corrupted-witness rejection. Keep the interpreter's integer digit limit.
- Bound polynomial degree, coefficient size and saved-record validation; expose no
  arbitrary geometry search or mixed parameter interface.
- Exercise an installed wheel in an empty directory, replay the new command
  twice, inspect its output and verify the earlier scientific outputs.
- Review proof/source mappings separately from execution and packaging.

## Scope

The all-strength conclusion compares the same calibrated strength in both
classes. A distinct local theorem separates independently uncertain fixed
strengths using calibrated raw intensity. It gives no global unknown-strength
separation, detector model, exposure robustness, finite-count guarantee or
physical feasibility. Large motion does not authorize replacing the permanent graph
with an instantaneous distance graph. No novelty or complete formalization
claim follows from publication.
