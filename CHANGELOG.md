# Changelog

All notable changes are recorded here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html);
the 0.x certificate schema and Python API remain experimental.

## [Unreleased]

### Changed

- Use standard requirements filenames so dependency monitors can discover the
  development and optional prototype pins. Updates still require explicit
  source-manifest review and fresh artifact verification.

### Added

- A research roadmap distinguishing existing imaging methods, open mathematical
  questions, statistical targets and the calibration required before hardware
  development. Potential applications are not presented as achieved results.
- An additive `count` command and fresh API with explicit versioned profiles.
  `short-exposure-v1` keeps the 10⁻⁵ exposure cap; `long-exposure-v1`
  permits 0.001 for exact geometry and 0.01 for position uncertainty.
  Both recompute complete nonlinear shape-error allocations, thresholds
  and sufficient counts. All three earlier commands preserve their contracts.
- Signed kernel derivative/remainder bounds, a rank-two majorization bound,
  all 512 exposure cells and independent class-wise nuisance-propagated
  skewness unions for the long profile. The unresolved exact-geometry
  cap 0.01 and separately evaluated position cap 0.001 remain visible.
- Four optional real-variable sensitivity statements in the pinned analytic
  Lean project, alongside its nine unchanged variance declarations.
  These bounded statements do not formalize the full probabilistic theorem.
- An explicit profile decision record and FAQ separating sufficient counts,
  exposure domains, fixed settings and physical calibration requirements.

- An additive `exposure-count` command and API with a linear exposure-moment
  bound and Gaussian parity transfer. Both scenarios permit normalized exposure
  up to 10⁻⁵, with freshly recomputed sufficient counts and classifiers.
  The original commands and parameter contracts remain available.
- An optional `coordinate-count` command and API that recompute the full
  core and a separate exact coordinate-tolerance witness. Sufficient counts
  fall to 26,814,048,499,063,502 and 26,808,243,624,540,316 for the two
  scenarios, with all model assumptions and the classifier unchanged.

- A portable, standard-library certificate for one fixed chain of geometry,
  Gaussian motion, covariance uncertainty, exposure, frequency error and
  dependent photon-count discrimination.
- Exact rational inputs, source integrity manifest, installed-artifact tests,
  proof documentation and explicit limitations.
- A new release implementation and fresh verification workflow. Historical
  execution records are not included or represented as this release.
- A separately verified position-uncertainty scenario with its own joint
  frequency domain and finite-window count.
- An offline interactive geometry and certificate demo, checked against fresh
  installed-package output.
- Six finite arithmetic Lean checkpoints and six symbolic falling-factorial
  identities, with explicit limits on their formal coverage.
- A separate pinned Lean/mathlib project for general standard-deviation
  continuity and variance enclosures, with explicit finite-moment assumptions
  and limits on its connection to the full theorem.
- An optional synthetic instrument with eight scenarios per class, complete
  simulated motion records, a saved-output inspector and separate numerical
  dependencies. It does not claim physical validation or classifier performance.

### Fixed

- Pull-request commit-policy checks inspect the submitted head rather than
  GitHub's temporary merge commit.
- Source archives retain community and security configuration files.
- GitHub language detection includes the executable demo JavaScript, enabling
  its selection in default CodeQL setup.

[Unreleased]: https://github.com/thequantumfalcon/homometric-motion/commits/main
