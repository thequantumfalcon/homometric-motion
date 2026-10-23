# Bounded formal checkpoints

The substantive checkpoints prove the statements below. They do not connect
all of the executable moment tables, temporal model and classifier into a
formal proof of the complete theorem. They are not physical validation or
independent human review.

| Checkpoint | Mathematical statement and boundary |
| --- | --- |
| [Variance continuity](analytic/SCOPE.md#standard-deviation-continuity) | On a common probability space with explicit finite moments, `abs_sqrt_variance_sub_le_l2` bounds the change in standard deviation by the L2 norm of a coupled perturbation; L3 variants give variance enclosures. Constructing the coupling and its numerical error budget remains separate. |
| [Gaussian intensity moments](analytic/SCOPE.md#every-natural-raw-intensity-moment) | `finite_gaussian_intensity_moment` gives every natural raw moment of the squared modulus of a finite complex phase sum under a centered joint Gaussian law with full PSD covariance, including integrability. Physical-parameter substitution and exact mathematical charge histograms are also covered; executable histogram and polynomial identification remain outside Lean. |
| [Nine-point polynomial noncoincidence](analytic/SCOPE.md#nine-point-polynomial-statements) | An explicit Bezout identity proves no common zero for two supplied polynomials; `joint_moment_noncoincidence` concludes that the supplied moment differences cannot both vanish on `0<t<1`. Identifying those complete polynomials with the modeled intensity is an executable check outside Lean. |
| [Concrete nine-point covariance](analytic/SCOPE.md#concrete-nine-point-covariance) | For the two literal matrices, exact threshold, Gram and centered-inverse identities establish PSD and trace normalization, with almost-sure zero center of mass for centered Gaussian laws having those covariances. This is not a generic graph theorem or a proof of physical covariance or OU preparation. |

These proofs use the [optional analytic project](analytic/README.md), with
Lean 4.35.0 and pinned mathlib. Its [statement mapping and scope](analytic/SCOPE.md)
record exact hypotheses, source dependencies and application limits.
Replay uses `--trust=0` and explicit axiom inspection. The standard logical
foundations are `propext`, `Classical.choice` and `Quot.sound`; no `sorry`,
`native_decide` or custom axiom is added.

Supporting algebra includes the [full cubic cumulant perturbation identity
and coefficient bound](analytic/SCOPE.md#cumulant-sensitivity-statements) and
[falling-factorial product identities](FactorialIdentities.lean). The latter
use `Std` and `grind`. These identities do not themselves prove the
mixed-Poisson interpretation, estimator-error bound or classifier risk.

The separate `position_uncertainty/DiscoveryCheckpoint.lean` checks mapped
integer gaps, ceiling directions, risk and contact-margin inequalities using
`Init` and `decide +kernel`. Its closed statements are expected to report no
axioms. Their inputs are bound to the original `verify` position certificate,
not the later count methods or profiles. Checking these integers does not
prove that they bound the intended random variables.

Exposure estimates, concentration and the complete probabilistic classifier
remain outside the formalization. Detailed declarations and reproduction
mappings are retained for inspection rather than counted as a measure of
proof coverage.

## Reproduce the finite arithmetic mapping

Use an installed wheel and an empty working directory. Substitute the
checkout path in the generator command:

```sh
python -I -m homometric_motion verify --scenario position_uncertainty --output position.json
python -I /path/to/checkout/docs/proofs/formal/generate_checkpoint.py position.json --output-dir new-checkpoint
```

The generator validates the installed source manifest and recomputes the
entire public scenario before accepting the supplied certificate. It uses
only that installed package and certificate, and refuses an existing output
directory. Its statement mapping records the certificate and manifest
hashes, exact field names, integer expressions and Lean source hash.
These are fresh release bindings, not historical execution receipts.

With Lean 4.35.0 installed separately:

```sh
lean new-checkpoint/DiscoveryCheckpoint.lean
lean /path/to/checkout/docs/proofs/formal/FactorialIdentities.lean
```

The separate [analytic project](analytic/README.md#replay) supplies commands
for its nine files and a portable fresh nine-point coefficient mapping.
The local `lean-toolchain` pins the intended Lean version
for installations using a toolchain manager. No Lean executable, library
bundle or installer is included. The ordinary Python certificate does not
require Lean.

No `sorry`, `native_decide` or added custom axiom is used. The finite
statements are expected to report no axioms; the symbolic and analytic
proofs use Lean's standard logical foundation (`propext`,
`Classical.choice` and `Quot.sound`). These are different assurance scopes
and should not be described as a formal proof of the complete scientific
result.
