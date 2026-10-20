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

A separate [nine-point construction](docs/proofs/nine-point-moments.md)
studies exact instantaneous intensity without a detector channel. Its leading
intensity laws under Gaussian motion agree, yet its exact first two moments cannot both
agree at any shared finite positive motion strength. A further local bound
separates independently uncertain fixed strengths using calibrated raw
intensity. Neither result carries the 63-point photon-count guarantee.

After installation, reproduce this separate fixed model with:

```sh
python -m homometric_motion small-pair --output nine-point.json
python -m homometric_motion summary nine-point.json
```

The command reconstructs all polynomial witnesses from the fixed inputs.
The mean crosses once and skewness crosses at least twice, so neither
statistic has a single global ordering. Wider unresolved parameter bands
remain in the output. Saved-record inspection performs a fresh scientific
reconstruction; it does not authenticate the supplied record or validate
physical assumptions.

## What is certified

The package reconstructs a noncongruent pair of 63-point configurations,
their permanent spring graphs, Gaussian intensity moments and outward rational
bounds. For each stated fixed parameter contract, standardized third cumulants
occupy disjoint intervals after covariance uncertainty, positive exposure and
small frequency error. A count-based classifier has a conservative error bound
of at most **5% in either class** after the sufficient count associated with
that contract. The new `count` command requires an explicit profile; the three
earlier commands preserve their previous results.

| Profile | Scenario | Normalized exposure cap | Sufficient observation windows |
| --- | --- | ---: | ---: |
| `short-exposure-v1` | `exact_geometry` | 10⁻⁵ | 69,803,163,290,068 |
| `short-exposure-v1` | `position_uncertainty` | 10⁻⁵ | 5,362,340,030,851 |
| `long-exposure-v1` | `exact_geometry` | 0.001 | 36,938,105,282,195 |
| `long-exposure-v1` | `position_uncertainty` | 0.01 | 16,852,383,428,868 |

The [profile proof](docs/proofs/profiled-counts.md) derives fresh error
allowances, thresholds and counts. The short profile uses linear exposure
moments; the long profile uses [signed kernel bounds](docs/proofs/signed-kernel-exposure.md)
with all 512 time cells and independent class-wise unions.

The following assumptions describe the exact-geometry contracts; exposure is
selected by method or profile. The position scenario has the additional
calibration restrictions described below.

| Assumption | Certified domain |
| --- | --- |
| Mean positions | Exact, fixed configurations defined by the construction |
| Motion strength | Each normalized strength β lies in [B/2, B], B ≈ 1.3986078635588654 × 10⁻¹¹ |
| Springs | Permanent graph; each fixed edge weight lies in 1 ± 1/100001 |
| Dynamics | Stationary centered Gaussian weighted-spring Ornstein–Uhlenbeck process |
| Frequency | Fixed error from π/3 at most 10⁻¹⁴ |
| Exposure | Positive fixed rectangular duration within the selected method or profile cap |
| Window spacing | Start-to-start normalized time at least 1000 |
| Observation | Conditionally independent Poisson counts given the full trajectory |
| Channel | Fixed integrated normalized gain in [0.9, 1.1]; background in [0, 1] |

B is an exact rational in the packaged inputs; its displayed decimal is not a
replacement. Frequency error requires the positive strength floor. The model
handles dependence between observation windows through an OU covariance bound;
the windows are not assumed unconditionally independent.

Every stated window count is **sufficient**, not necessary or optimal.
The retained `exposure-count` result has a frequency-robust skewness gap greater
than 0.0004893221118044 before its estimator allowance; the new profiles
recompute their own shape bounds and thresholds. Parameter choices and
allocation searches are informed by earlier bounds, not blind selection or
preregistration.

Read the [proofs and assumptions](docs/proofs/README.md) before applying a result.
Known failure regimes and prior literature are part of the proof documentation.
The [claim ledger](docs/claims.md) separates assertions, evidence and open questions.

The optional `position_uncertainty` scenario also permits fixed mean-position
errors of at most **10⁻¹⁴** per coordinate, with a tighter frequency-error limit
of **10⁻¹⁶**. These geometry scenarios are not nested: adding a position-error
allowance also imposes a 100-fold tighter frequency tolerance. Their count
comparison does not show that position error improves discrimination.
The ideal configurations remain homometric; perturbed specimens need not be.
See the [position-uncertainty proof](docs/proofs/position-uncertainty.md).

The `exposure-count` method bounds the leading Gaussian moment changes linearly
in exposure and retains the finite-motion errors through Gaussian sign symmetry.
It allows a cap 10¹⁵ times larger than the original proof, then recomputes the
classification threshold, dependence allowance and sufficient count. All three
earlier commands and both new profiles rely on the stated motion and
observation assumptions. The retained method results are:

| Method | Exposure cap | Exact-geometry sufficient windows | Position-uncertainty sufficient windows |
| --- | ---: | ---: | ---: |
| `verify` | 10⁻²⁰ | 975,281,623,024,726,766,278 | 975,028,627,229,038,193,209 |
| `coordinate-count` | 10⁻²⁰ | 26,814,048,499,063,502 | 26,808,243,624,540,316 |
| `exposure-count` | 10⁻⁵ | 26,815,183,544,609,917 | 26,809,378,397,093,764 |

The coordinate proof allocates separate error tolerances to three estimated
factorial moments. The exposure extension applies it to a newly computed
classifier. The new profiles refine the sensitivity bound and use separate
actual variance and standardized third-cumulant errors, including every
nonlinear term. They require new thresholds; no earlier threshold or count
is transferred.

Exact geometry at exposure cap `0.01` remains unresolved and has no allocated
count. A separately evaluated position domain at cap `0.001` gives
4,404,373,875,964 sufficient windows; it is a stricter domain than the
selected long position profile, not an automatically selected optimum.
The demo still displays the original `verify` method.

All settings, including exposure and channel values, are fixed during an
acquisition. Allowed values may differ by class; arbitrary mixtures or drift
are not covered. The integrated gain/background range does not establish a
fixed physical rate or dose. No global optimum or practical feasibility is
claimed. See the [FAQ](docs/FAQ.md) and
[profile decision record](docs/decisions/0003-explicit-count-profiles.md).

## Reproduce

Python 3.11 or later is required. The scientific runtime has **no third-party
dependencies**, makes no network requests and needs no private research files.
In a fresh virtual environment, from this repository:

```sh
python -m pip install .
python -I -m homometric_motion count --profile short-exposure-v1 --scenario exact_geometry --output short.json
python -I -m homometric_motion count --profile long-exposure-v1 --scenario position_uncertainty --output long-position.json
python -I -m homometric_motion summary long-position.json
python -I -m homometric_motion exposure-count --output certificate.json
python -I -m homometric_motion exposure-count --scenario position_uncertainty --output position-exposure.json
python -I -m homometric_motion coordinate-count --output coordinate.json
python -I -m homometric_motion coordinate-count --scenario position_uncertainty --output position-coordinate.json
python -I -m homometric_motion verify --output original-certificate.json
python -I -m homometric_motion verify --scenario position_uncertainty --output position.json
```

Installation downloads the pinned build tools unless they are already available.
The installed verification itself runs offline. All computing commands refuse to overwrite
an existing output: choose a new filename for another run. The JSON contains
exact fractions and check labels; decimal output is for reading only.
`summary` does not authenticate a saved file or its provenance. For a nine-point
record it additionally reconstructs and compares all fixed scientific values
using the installed model. Earlier certificate summaries retain their stated
consistency checks without recomputing the reference motion model.

To test the artifact, contributors and CI run these commands from a Git checkout:

```sh
python tools/project.py setup
python tools/project.py release
```

Use an isolated development environment. `release` builds an sdist and wheel,
tests the installed package, checks coverage, executes each scenario and
each of the three earlier methods plus both explicit profiles twice in a fresh
environment, and compares the results. It separately replays `small-pair` twice
and reconstructs its saved record. It also checks that the committed
demo data match a newly computed original `verify` certificate. It does not publish anything.
See [contribution instructions](.github/CONTRIBUTING.md).

Optional [Lean checkpoints](docs/proofs/formal/README.md) verify six finite
arithmetic statements, six general falling-factorial identities, nine
analytic variance declarations, four deterministic cumulant-sensitivity
statements and five explicit nine-point polynomial statements. The eighteen
analytic-project declarations occupy three source files;
the original nine are unchanged. The finite arithmetic mapping remains bound
to the original `verify` position-uncertainty certificate, not to the new
profile counts. The separate nine-point mapping rebuilds its installed model
and binds every coefficient of the two-moment noncoincidence checkpoint.
These bounded proofs do not formalize the complete theorem,
and Lean is not required to run the package.

## What remains open

The [research roadmap](docs/research-roadmap.md) sets evidence requirements
for broader uniqueness theorems, better estimators, motion-informed imaging
and physical feasibility. These are open directions, not established applications.

Physical covariance, stationarity, calibration, permanent connectivity and
conditional detector independence need validation against an actual system.
The finite-count theorems do not cover drifting parameters, arbitrary detector
noise or position errors beyond their stated domains. Separate research
extensions are not automatically part of this package's certificate.

Computation and independent alternative arithmetic checks reduce the chance of
an error. They are not independent human peer review or formal verification of
the full theorem. Related work already studies homometry, fluctuation statistics and
factorial cumulants; this repository does not establish scientific priority.

The public interface comprises `build_certificate()`,
`build_coordinate_certificate()`, `build_exposure_certificate()` and
`build_count_certificate(*, profile, scenario="exact_geometry")` and the
parameter-free `build_small_pair_certificate()`,
the `verify`, `coordinate-count`, `exposure-count`, `count`, `small-pair` and `summary`
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
