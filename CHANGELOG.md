# Changelog

All notable changes are recorded here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html);
the 0.x certificate schema and Python API remain experimental.

## [Unreleased]

### Added

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

### Fixed

- Pull-request commit-policy checks inspect the submitted head rather than
  GitHub's temporary merge commit.
- Source archives retain community and security configuration files.
- GitHub language detection includes the executable demo JavaScript, enabling
  its selection in default CodeQL setup.

[Unreleased]: https://github.com/thequantumfalcon/homometric-motion/commits/main
