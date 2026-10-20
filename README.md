# Homometric motion

An exact-arithmetic certificate showing that **one explicit pair with identical
clean diffraction intensities can be distinguished under a specified model of
motion and photon counting**.

The construction is conditional mathematics. It has no experimental dataset,
established novelty claim or practical acquisition recommendation. The sufficient
sample bound is enormous; this is evidence of existence under the assumptions,
not an efficient measurement proposal.

The [interactive demo](demo/index.html) shows the two configurations, their
coincident clean diffraction curves and the certified statistical intervals.
Open `demo/index.html` from a local checkout in a browser; it works offline.
Its graphics are illustrations, not experimental observations or a proof engine.

An optional [virtual instrument](prototype/README.md) generates synthetic motion
and photon-count records with deliberate model failures. It runs on the CPU,
uses a separate NumPy/SciPy environment, and retains the full simulated motion
for inspection. It does not implement or validate the final count theorem.
Its reference remains bound to the explicitly hashed earlier core certificate;
it does not automatically track new package revisions.

## What is certified

The package reconstructs a noncongruent pair of 63-point configurations,
their permanent spring graphs, Gaussian intensity moments and outward rational
bounds. For the fixed parameter chain below, standardized third cumulants occupy
disjoint intervals, even after covariance uncertainty, positive exposure and
small frequency error. A count-based classifier has a conservative error bound
of at most **5% in either class** after
**26,814,048,499,063,502 observation windows**, using the
[coordinate-tolerance count proof](docs/proofs/coordinate-counts.md).

| Assumption | Certified domain |
| --- | --- |
| Mean positions | Exact, fixed configurations defined by the construction |
| Motion strength | Each normalized strength β lies in [B/2, B], B ≈ 1.3986078635588654 × 10⁻¹¹ |
| Springs | Permanent graph; each fixed edge weight lies in 1 ± 1/100001 |
| Dynamics | Stationary centered Gaussian weighted-spring Ornstein–Uhlenbeck process |
| Frequency | Fixed error from π/3 at most 10⁻¹⁴ |
| Exposure | Positive rectangular exposure, normalized duration at most 10⁻²⁰ |
| Window spacing | Start-to-start normalized time at least 1000 |
| Observation | Conditionally independent Poisson counts given the full trajectory |
| Channel | Fixed integrated normalized gain in [0.9, 1.1]; background in [0, 1] |

B is an exact rational in the packaged inputs; its displayed decimal is not a
replacement. Frequency error requires the positive strength floor. The model
handles dependence between observation windows through an OU covariance bound;
the windows are not assumed unconditionally independent.

The frequency-robust skewness gap is greater than 0.0006992277239323 before the
finite-sample estimator allowance. The stated window count is **sufficient**,
not necessary or optimal. The frequency tolerance was selected after earlier
bounds were inspected; no blind selection or preregistration is claimed.

Read the [proofs and assumptions](docs/proofs/README.md) before applying a result.
Known failure regimes and prior literature are part of the proof documentation.
The [claim ledger](docs/claims.md) separates assertions, evidence and open questions.

The optional `position_uncertainty` scenario also permits fixed mean-position
errors of at most **10⁻¹⁴** per coordinate, with a tighter frequency-error limit
of **10⁻¹⁶**. Its separately recomputed coordinate-tolerance sufficient count is
**26,808,243,624,540,316 windows**. These are different joint domains:
the new count does not show that adding position error improves discrimination.
The ideal configurations remain homometric; perturbed specimens need not be.
See the [position-uncertainty proof](docs/proofs/position-uncertainty.md).

The coordinate proof allocates different error tolerances to the three estimated
factorial moments. It retains the original classifier, parameter domains and
5% target. The original common-tolerance certificates remain available through
`verify`, and the demo displays that original method.

| Scenario | Original common-tolerance sufficient windows | Coordinate-tolerance sufficient windows |
| --- | ---: | ---: |
| Exact geometry | 975,281,623,024,726,766,278 | 26,814,048,499,063,502 |
| Position uncertainty | 975,028,627,229,038,193,209 | 26,808,243,624,540,316 |

The new allocation was selected after inspecting the earlier bounds. It is an
exact feasible witness, with no claim of global optimality or practical feasibility.

## Reproduce

Python 3.11 or later is required. The scientific runtime has **no third-party
dependencies**, makes no network requests and needs no private research files.
In a fresh virtual environment, from this repository:

```sh
python -m pip install .
python -I -m homometric_motion coordinate-count --output certificate.json
python -I -m homometric_motion summary certificate.json
python -I -m homometric_motion coordinate-count --scenario position_uncertainty --output position-coordinate.json
python -I -m homometric_motion verify --output original-certificate.json
python -I -m homometric_motion verify --scenario position_uncertainty --output position.json
```

Installation downloads the pinned build tools unless they are already available.
The installed verification itself runs offline. Both computing commands refuse to overwrite
an existing output: choose a new filename for another run. The JSON contains
exact fractions and check labels; decimal output is for reading only.
`summary` displays a saved file and does not independently reverify it.

To test the artifact, contributors and CI run these commands from a Git checkout:

```sh
python tools/project.py setup
python tools/project.py release
```

Use an isolated development environment. `release` builds an sdist and wheel,
tests the installed package, checks coverage, executes each scenario and count method twice in a
fresh environment and compares the results. It also checks that the committed
demo data match the newly computed default certificate. It does not publish anything.
See [contribution instructions](.github/CONTRIBUTING.md).

Optional [Lean checkpoints](docs/proofs/formal/README.md) verify six finite
arithmetic statements, six general falling-factorial identities and general
standard-deviation/variance stability lemmas. The finite arithmetic mapping
is bound to the position-uncertainty certificate; the analytic lemmas have
explicit probability and finite-moment assumptions. They do not formalize
the complete theorem, and Lean is not required to run the package.

## What remains open

Physical covariance, stationarity, calibration, permanent connectivity and
conditional detector independence need validation against an actual system.
The finite-count theorems do not cover drifting parameters, arbitrary detector
noise or position errors beyond their stated domains. Separate research
extensions are not automatically part of this package's certificate.

Computation and independent alternative arithmetic checks reduce the chance of
an error. They are not independent human peer review or formal verification of
the full theorem. Related work already studies homometry, fluctuation statistics and
factorial cumulants; this repository does not establish scientific priority.

The public interface comprises `build_certificate()` and
`build_coordinate_certificate()`, the `verify`, `coordinate-count` and `summary`
CLI commands, and their versioned JSON schemas. All are experimental during 0.x.
The CLI binds its output to the packaged source manifest; hashes do not make an
untrusted source authentic. Cite the exact Git commit using [CITATION.cff](CITATION.cff).

Maintained by [The Quantum Falcon](https://github.com/thequantumfalcon).
Use [Discussions](https://github.com/thequantumfalcon/homometric-motion/discussions)
for questions and [Issues](https://github.com/thequantumfalcon/homometric-motion/issues)
for reproducible defects or proof gaps.

Code and original documentation are [MIT licensed](LICENSE.txt).
The adapted Contributor Covenant has its own CC BY-SA 4.0 attribution.
Repository maintenance decisions are recorded in [the ADRs](docs/decisions/0002-maintenance-and-security.md).
