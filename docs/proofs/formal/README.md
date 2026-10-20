# Bounded formal checkpoints

These files cover three bounded parts of the argument. They do not formalize
the Gaussian model, covariance bounds, exposure estimates, concentration
inequalities, physical assumptions or the complete conditional theorem.
They are not experimental validation or independent human peer review.

| File | Statement scope | Proof dependencies |
| --- | --- | --- |
| `position_uncertainty/DiscoveryCheckpoint.lean` | Six closed integer inequalities mapped from the public position-uncertainty certificate: two gaps, both ceiling directions, risk bound and positive contact margin | `Init`, `decide +kernel`; inspect the six `#print axioms` outputs |
| `FactorialIdentities.lean` | Six polynomial identities for falling-factorial products, for every integer | `Std`, `grind`; standard logical axioms may appear in `#print axioms` |
| [Analytic robustness](analytic/README.md) | Nine declarations proving standard-deviation continuity, centering contraction, the L3-to-L2 comparison and variance enclosures under explicit probability and finite-moment hypotheses | Lean 4.35.0 and pinned mathlib; `--trust=0` and explicit axiom inspection |

The polynomial identities alone do not establish a covariance formula.
Taking expectations and using the mixed-Poisson model are separate
mathematical steps described in the count proof. The closed arithmetic
statements alone do not establish that their numerical inputs bound
the intended random variables.

The analytic project proves a general norm-to-variance step. Its
[scope](analytic/SCOPE.md) separates that theorem from the construction of
the modeled random variables and the derivation of their perturbation bounds.
It has its own pinned optional dependencies and replay instructions.

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

The local `lean-toolchain` pins the intended Lean version for installations
using a toolchain manager. No Lean executable, library bundle or installer
is included. The ordinary Python certificate does not require Lean.
No `sorry`, `native_decide` or added custom axiom is used. The finite
statements are expected to report no axioms; the symbolic proofs use
Lean's standard logical foundation (`propext`, `Classical.choice` and
`Quot.sound`). These are different assurance scopes and should not be
described as a formal proof of the complete scientific result.
