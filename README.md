# Homometric motion

An explicit pair of noncongruent one-dimensional 63-point configurations has
identical clean diffraction intensity at every real frequency, but distinguishable
intensity statistics under a specified scalar stochastic motion model. The
[proofs](docs/proofs/README.md) and exact-arithmetic certificate establish a
conditional finite-sample classification bound.

**This is an existence result under restrictive assumptions.** The certified
motion is tiny: the nominal site-averaged RMS displacement is **2.64–3.74
millionths of the unshifted motif's short spacing**, and remains below four
millionths with the allowed covariance uncertainty. This is an RMS measure,
not a maximum displacement; Gaussian displacements are unbounded.
The sufficient observation count is enormous. No physical experiment,
practical acquisition scheme or established novelty is claimed.

**Relation to established scattering theory.** Thermal diffuse scattering
already probes atomic displacement correlations. This repository adds a
specific quantitative certificate for a constructed pair: population separation
carried through finite exposure, stated parameter uncertainty and a Poisson
observation model to a finite-sample risk bound. It does not establish a new
scattering mechanism or an advantage over conventional TDS analysis. See the
[classical references and comparison](docs/proofs/scope-and-related-work.md#thermal-diffuse-scattering).
The [statistical-optics and moment-method precedents](docs/proofs/scope-and-related-work.md#statistical-optics-and-the-count-statistic)
explain the established ingredients behind the statistic.

## The certified result

For `long-exposure-v1` / `exact_geometry`, a classifier based on empirical
second and third factorial cumulants has error at most **5% in either class**
with **36,938,105,282,195 observation windows**, allowing normalized exposure
up to **0.001**.

The model fixes the [constructed pair and permanent spring graphs](docs/proofs/geometry-and-motion.md)
and assumes stationary centered Gaussian Ornstein–Uhlenbeck motion and conditionally
independent Poisson counts given the full trajectory. Its exact-geometry domain is:

| Parameter | Certified restriction |
| --- | --- |
| Motion strength | β ∈ [B/2, B], with exact rational B ≈ 1.3986078635588654 × 10⁻¹¹ |
| Spring weights | Each fixed weight lies in 1 ± 1/100001 |
| Frequency | Fixed error from π/3 at most 10⁻¹⁴ |
| Exposure and spacing | Positive fixed rectangular exposure within the profile cap; normalized start spacing at least 1000 |
| Detector channel | Fixed integrated normalized gain in [0.9, 1.1] and Poisson background in [0, 1] |

All nuisance parameters stay fixed during an acquisition. Window dependence
is bounded through the OU model; unconditional independence is not assumed.
The count is sufficient, not necessary or optimal, and supplies no physical
time, flux or dose without additional calibration.

**Physical units.** Let ℓ₀ be the short spacing in metres and t₀ the common
OU base time in seconds. Nominal RMS displacement is ℓ₀√β; angular
wavenumber is q = ω/ℓ₀ in rad/m, with nominal q = π/(3ℓ₀). Physical exposure
is at most 0.001t₀ and window-start spacing is at least 1000t₀. For scale
only, ℓ₀ = 1 nm gives nominal RMS
**2.64–3.74 fm** (1 fm = 10⁻¹⁵ m). This is a unit conversion, not a material
calibration. In the [overdamped interpretation](docs/proofs/robustness-and-counts.md#covariance-uncertainty-and-compatible-dynamics),
t₀ = ζ/κ for drag ζ and reference spring stiffness κ; neither is specified.

Other [profiles and their counts](docs/proofs/profiled-counts.md) have different
contracts. In particular, `position_uncertainty` allows coordinate errors up to
10⁻¹⁴ only with a tighter frequency tolerance of 10⁻¹⁶; its count does not show
that position error improves discrimination. **Exact geometry at exposure
0.01 remains unresolved.** Earlier methods retain their own results; see the
[command guide and FAQ](docs/FAQ.md), [claim ledger](docs/claims.md) and
[scope and related work](docs/proofs/scope-and-related-work.md).

## Reproduce

Use Python 3.11 or later in a fresh virtual environment:

```sh
python -m pip install .
python -I -m homometric_motion count --profile long-exposure-v1 --scenario exact_geometry --output certificate.json
python -I -m homometric_motion summary certificate.json
```

The scientific runtime uses only the Python standard library and runs offline.
Installation may download pinned build tools. Computing commands refuse to
overwrite existing output. Certificate assertions use exact rational or outward
interval arithmetic; displayed decimals are for reading only. `summary` inspects
a saved record but does not authenticate it or replace fresh computation.

Contributors and CI use the same artifact verification:

```sh
python tools/project.py setup
python tools/project.py release
```

`release` builds the source archive and wheel, tests the installed package,
and reproduces all package CLI certificate contracts twice in clean directories.
It also checks the demo data and packaged review witnesses; it publishes
nothing. See the [contribution instructions](.github/CONTRIBUTING.md) and
`python tools/project.py --help` for the full command catalog.

## Explore and inspect

- **[Offline explorer](demo/index.html):** open locally to compare clean
  diffraction, spring graphs and the original and long-exposure certificates.
  Floating-point motion snapshots are illustrations, separate from exact data.
- **[Synthetic instrument](prototype/README.md):** simulated motion and photon
  counts, including deliberate model failures, in a separate NumPy/SciPy
  environment. It does not validate the count theorem.
- **[Finite-motion study](studies/finite-motion/README.md):** numerical moments
  at larger motion, with separately locked dependencies. The selected grid
  misses its window target and independent site disorder worsens the statistic.
  It does not extend the certified motion range or supply a finite-sample bound.
- **[Nine-point construction](docs/proofs/nine-point-moments.md):** exact
  instantaneous-intensity results with no detector/count guarantee. A separate
  [complete-graph counterexample](docs/proofs/phase-permutation.md) shows why
  the interaction rule matters.
- **[Reviewer kit](review/README.md):** SageMath/Arb cross-checks and a separate
  calibrated iid channel whose assumptions and counts do not transfer to the
  robust OU-window result.
- **[Lean checkpoints](docs/proofs/formal/README.md):** variance continuity,
  Gaussian moment formulas and specified nine-point polynomial/covariance
  results. These are partial proofs with explicit dependencies, not a
  formalization of the full classifier. The separate `lean-setup` and `lean`
  project tasks reproduce these checkpoints; CI requires the Lean replay.

The [research roadmap](docs/research-roadmap.md) records open work. Physical
model validation, broader parameter domains and independent mathematical review
remain open. The existing results do not cover arbitrary drift, detector noise
or motion laws.

## Research provenance and limitations

This project grew out of AI-assisted exploration. AI systems proposed and
developed substantial portions of the mathematical arguments, code, and
documentation. My role was to direct the investigation, ask for repeated
challenges and validation, and decide what to document and share. I did not
independently derive or manually verify every mathematical step.

The repository records the resulting arguments and computational checks,
along with their assumptions, limitations, and negative findings. The checks
described here were conducted within the same AI-assisted workflow.
Alternative implementations and successful reproductions provide useful
evidence, but they do not amount to independent human review.

I am sharing this work so others can inspect, reproduce, challenge, and improve
it. The results concern the stated mathematical models; physical applicability
and scientific novelty remain open. Corrections, counterexamples, and
independent mathematical review are welcome. The full disclosure is also in
[PROVENANCE.md](review/PROVENANCE.md).

Maintained by [Thomas Albrecht](https://github.com/thequantumfalcon).
Use [Discussions](https://github.com/thequantumfalcon/homometric-motion/discussions)
for questions and [Issues](https://github.com/thequantumfalcon/homometric-motion/issues)
for defects or proof gaps. Cite the exact commit using [CITATION.cff](CITATION.cff);
the APIs and versioned JSON schemas remain experimental during 0.x.

Code and original documentation are [MIT licensed](LICENSE.txt).
The adapted Contributor Covenant retains its CC BY-SA 4.0 attribution.
