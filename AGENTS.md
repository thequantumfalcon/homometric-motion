# Repository instructions

This repository contains a conditional mathematical construction and a
reproducible certificate for distinguishing an explicit clean-homometric
pair under specified stochastic motion and observation models.

## Scientific boundaries

- Distinguish proved inequalities, computed checks, model assumptions and
  unexecuted experiments. Do not claim empirical validation, established
  novelty, optimal sample complexity or full-theorem proof-assistant verification.
  Formal checkpoints must name their exact statements and proof dependencies.
- Keep negative results and unresolved parameter cases visible.
- Use exact rational or outward interval arithmetic for certificate assertions.
  Floating-point simulations must be separately labelled and cannot certify
  the mathematical risk bound.
- The certificate runtime must use the Python standard library only. Do not read
  external workspace files, historical outputs, host settings or network
  resources to calculate a certificate.
- The optional `prototype/` uses its own hash-locked numerical dependencies.
  Keep its synthetic outputs outside the published source. Verify its separate
  source manifest and run the packaged scripts through the prototype task.
- Every published source revision needs a new manifest and fresh
  reproduction. Do not present adapted source as an unchanged old freeze.

## Development and verification

- Use the `src/homometric_motion/` package layout.
- Keep tests outside the package and run them against an installed wheel.
- The project command catalog is `python tools/project.py --help`;
  development and CI must call the same implementation.
- Package verification must execute the artifact users receive in a clean
  directory, inspect its output and compare its mathematical certificate.
- Preserve exact input/output semantics when refactoring interval
  arithmetic; independently check changed inequalities.
- Use Ruff formatting, type hints where useful, and focused tests of
  mathematical invariants, boundary failures and artifact isolation.

## Repository and security

- Public maintainer identity is The Quantum Falcon. Commits are signed
  locally using the configured repository identity. Do not create web/API
  merge commits.
- Do not include machine paths, private receipts, credentials, supplied
  attachments, unrelated research archives or tool bundles.
- Do not add coauthor trailers, generator credits or automated attribution
  banners to source, commits, documentation or releases.
- Keep the research-process disclosure in `review/PROVENANCE.md` accurate
  and visible, including its factual account of AI assistance.
- Keep workflows pinned to reviewed commit hashes, with read-only default
  permissions, timeouts and checkout credentials disabled.
- Never execute untrusted pull-request code with privileged credentials.
- Read `.github/CONTRIBUTING.md` and the records in `docs/decisions/` before
  changing the public certificate contract.
