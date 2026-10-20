# Homometric motion

An exact-arithmetic certificate showing that **one explicit pair with identical
clean diffraction intensities can be distinguished under a specified model of
motion and photon counting**.

The construction is conditional mathematics. It has no experimental dataset,
established novelty claim or practical acquisition recommendation. The sufficient
sample bound is enormous; this is evidence of existence under the assumptions,
not an efficient measurement proposal.

## What is certified

The package reconstructs a noncongruent pair of 63-point configurations,
their permanent spring graphs, Gaussian intensity moments and outward rational
bounds. For the fixed parameter chain below, standardized third cumulants occupy
disjoint intervals, even after covariance uncertainty, positive exposure and
small frequency error. A count-based classifier has a conservative error bound
of at most **5% in either class** after
**975,281,623,024,726,766,278 observation windows**.

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

## Reproduce

Python 3.11 or later is required. The scientific runtime has **no third-party
dependencies**, makes no network requests and needs no private research files.
In a fresh virtual environment, from this repository:

```sh
python -m pip install .
python -I -m homometric_motion verify --output certificate.json
python -I -m homometric_motion summary certificate.json
```

Installation downloads the pinned build tools unless they are already available.
The installed verification itself runs offline. `verify` refuses to overwrite
an existing output: choose a new filename for another run. The JSON contains
exact fractions and check labels; decimal output is for reading only.
`summary` displays a saved file and does not independently reverify it.

To test the artifact, contributors and CI run these commands from a Git checkout:

```sh
python tools/project.py setup
python tools/project.py release
```

Use an isolated development environment. `release` builds an sdist and wheel,
tests the installed package, checks coverage, executes the CLI twice in a fresh
environment and compares the results. It does not publish anything.
See [contribution instructions](.github/CONTRIBUTING.md).

## What remains open

Physical covariance, stationarity, calibration, permanent connectivity and
conditional detector independence need validation against an actual system.
The finite-count theorem does not cover drifting parameters, arbitrary detector
noise or mean-position errors. Separate research extensions are not automatically
part of this package's certificate.

Computation and independent alternative arithmetic checks reduce the chance of
an error. They are not proof-assistant verification or independent human peer
review. Related work already studies homometry, fluctuation statistics and
factorial cumulants; this repository does not establish scientific priority.

The public interface is `build_certificate()`, the `verify` and `summary` CLI
commands, and the versioned JSON schema. All are experimental during 0.x.
The CLI binds its output to the packaged source manifest; hashes do not make an
untrusted source authentic. Cite the exact Git commit using [CITATION.cff](CITATION.cff).

Maintained by [The Quantum Falcon](https://github.com/thequantumfalcon).
Use [Discussions](https://github.com/thequantumfalcon/homometric-motion/discussions)
for questions and [Issues](https://github.com/thequantumfalcon/homometric-motion/issues)
for reproducible defects or proof gaps.

Code and original documentation are [MIT licensed](LICENSE.txt).
The adapted Contributor Covenant has its own CC BY-SA 4.0 attribution.
Repository maintenance decisions are recorded in [the ADRs](docs/decisions/0002-maintenance-and-security.md).
