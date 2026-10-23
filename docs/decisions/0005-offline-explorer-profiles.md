# 5. Extend the offline explorer with explicit certificate views

Date: 2026-10-22

Status: accepted; publication requires the verification gates below

## Context

The offline explorer originally displayed only the retained `verify`
common-tolerance certificate. The repository now leads with the stronger
`long-exposure-v1` exact-geometry result. A visitor should be able to inspect
that result visually without confusing its exposure domain and count with the
earlier certificate or the separate calibrated-iid model.

[ADR 3](0003-explicit-count-profiles.md) preserved the original demo while adding
explicit scientific profiles. This decision extends the presentation with a
second named view and retains the original view. It changes no certificate API,
schema, mathematical input, parameter contract or classifier.

## Decision

Keep the explorer self-contained and usable directly from disk. Use local
HTML, CSS, JavaScript and deterministic generated data; add no framework,
network dependency, tracking or scientific runtime dependency.

Present a short sequence: equal clean diffraction, different permanent spring
graphs, then certified statistical separation. Label browser diffraction
calculations as floating-point illustrations. Draw seeded pseudorandom Gaussian
snapshots using the nominal covariance, unit spring weights and strength B.
Magnify displayed displacements by 300,000 and label them as floating-point
illustrations of a one-time law, never as OU trajectories, exposures, photon
counts or measurements. Keep graph connectivity permanent. Frequency and
snapshot controls must not imply that they recompute or extend the fixed
certificate.

Add an explicit `long-exposure-v1` / `exact_geometry` view and keep the original
`verify` / `exact_geometry` view selectable. The long profile is the initial
view to match the repository introduction. This is an editorial selection;
the scientific command still requires an explicit profile and provides no
automatic best-profile selection.

Bind each view's count, population intervals, estimator allowances, threshold,
exposure cap and source provenance to its own record. Generate both views from
fresh installed-package output with the current package manifest. Never copy a
new count into the old bound panel or apply the calibrated-iid count to the OU
window model. Keep exact rationals in the display data; decimals and rendered
coordinates are for reading only.

Keep the assumptions and the distinction between sufficient and necessary
counts visible. The exact-geometry exposure cap 0.01 remains unresolved.
Physical feasibility, independent human review and scientific novelty remain
open. Preserve access to the research-process disclosure.

## Verification before publication

- Reproduce both certificates from the installed artifact in clean directories
  and compare the committed display data against those fresh records.
- Check both profile views, interval separation, threshold placement, geometry,
  clean-intensity agreement and controls in a real browser.
- Inspect desktop and narrow-screen screenshots, keyboard focus, reduced-motion
  behavior and browser errors. Check that the explorer requests no network
  resources and remains usable when opened directly from disk.
- Record visual and interaction findings separately from the exact-arithmetic
  certificate checks. A screenshot or passing browser check does not validate
  the mathematical theorem or the physical model.

## Consequences

The demo explains the construction and exposes two already defined results.
Its illustrative samples do not implement the temporal motion or detector
model. It is not a proof engine, a live experiment or an acquisition planner.
The optional Python virtual instrument remains a separate synthetic study with
its own dependencies, source manifest and limitations.

Publishing a hosted site is a separate deployment decision under
[ADR 2](0002-maintenance-and-security.md). This change requires no cloud
credentials, hosting service or deployment workflow.
