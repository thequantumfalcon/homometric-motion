# Bounded formal checkpoints

These files cover four bounded parts of the argument. They do not formalize
the Gaussian model, covariance bounds, exposure estimates, concentration
inequalities, physical assumptions or the complete conditional theorem.
They are not experimental validation or independent human peer review.

| File | Statement scope | Proof dependencies |
| --- | --- | --- |
| `position_uncertainty/DiscoveryCheckpoint.lean` | Six closed integer inequalities mapped from the original `verify` position-uncertainty certificate: two gaps, both ceiling directions, risk bound and positive contact margin | `Init`, `decide +kernel`; inspect the six `#print axioms` outputs |
| `FactorialIdentities.lean` | Six polynomial identities for falling-factorial products, for every integer | `Std`, `grind`; standard logical axioms may appear in `#print axioms` |
| [Standard-deviation continuity](analytic/README.md) | Nine declarations proving standard-deviation continuity, centering contraction, the L3-to-L2 comparison and variance enclosures under explicit probability and finite-moment hypotheses | Lean 4.35.0 and pinned mathlib; `--trust=0` and explicit axiom inspection |
| [Cumulant sensitivity](analytic/SCOPE.md#cumulant-sensitivity-statements) | Four real-variable declarations: a full cubic perturbation identity, a coefficient identity, a two-endpoint coefficient bound and a counterexample to dropping one branch | The same pinned analytic project and standard logical foundations; no probability interpretation is formalized |

There are thirteen declarations across the two analytic source files.
The nine original standard-deviation declarations are unchanged.
The six factorial identities alone do not establish a covariance formula.
Taking expectations and using the mixed-Poisson model are separate
mathematical steps described in the count proof. The four sensitivity
statements likewise do not prove the complete estimator-error or risk bound.

The six closed arithmetic statements alone do not establish that their
numerical inputs bound the intended random variables. Their mapping remains
bound to the original `verify` method: they do not certify
`coordinate-count`, `exposure-count` or either `count` profile's values.

The analytic project's [scope](analytic/SCOPE.md) separates its statements
from construction of the modeled random variables, the derivation of
numerical perturbation budgets and the final classifier. It has its own
pinned optional dependencies and replay instructions.

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
for its two files. The local `lean-toolchain` pins the intended Lean version
for installations using a toolchain manager. No Lean executable, library
bundle or installer is included. The ordinary Python certificate does not
require Lean.

No `sorry`, `native_decide` or added custom axiom is used. The finite
statements are expected to report no axioms; the symbolic and analytic
proofs use Lean's standard logical foundation (`propext`,
`Classical.choice` and `Quot.sound`). These are different assurance scopes
and should not be described as a formal proof of the complete scientific
result.
