# Contributing

Start with the [README](../README.md), [proofs](../docs/proofs/README.md)
and [design decisions](../docs/decisions/0001-certificate-boundary.md).
Questions belong in Discussions; reproducible defects and proof gaps belong
in Issues. A counterexample is a useful contribution.

From a Git checkout, use Python 3.11 or later and an isolated development environment:

```sh
python -m venv .venv
# Activate .venv using your platform's activation command.
python tools/project.py setup
python tools/project.py lint
python tools/project.py test
```

The command catalog is `python tools/project.py --help`; Make targets are
thin wrappers. `test` builds and installs a wheel in a fresh environment.
Do not add `src` to the test import path. `verify` also executes the shipped
CLI twice for each scenario and each of the three earlier computation methods
plus both explicitly selected count profiles
in an isolated directory and
checks deterministic output, including equality of the embedded core.
It also executes the separate fixed `small-pair` construction twice, then
reconstructs its saved scientific record for comparison. This is 22 computing
CLI invocations and 11 summary invocations; the nine-point summary performs
one additional full model reconstruction. The nine-point model
has no embedded 63-point core or detector/count guarantee.
`verify` also extracts the separate phase-permutation proof and checker from
the built source archive, runs the checker twice in distinct isolated
directories with site imports disabled, and checks deterministic output and
overwrite refusal. Run `python tools/project.py phase-permutation` for this
bounded documentation-artifact check alone. Its finite algebra checks support
the separate analytic path-law proof; they add no package API or count claim.
`release` runs the local lint, tests and artifact checks; it publishes nothing.

`python tools/project.py fuzz` runs a separate 60-second Atheris campaign on
Linux x86_64 with Python 3.12. It tests the installed wheel's rational parser
and outward arithmetic against exact independent oracles. The fuzzer has its
own hash-locked dependency; the scientific package and ordinary tests still
use only the standard library. See [fuzzing scope and reproduction](../docs/fuzzing.md).

`python tools/project.py reviewer-kit` checks the optional reviewer kit from
the built source archive: inventory, saved exact witnesses and eight witness
tests. This task is included in `release` and CI. It uses the standard library
and does not rerun SageMath or Arb. The separate fresh calculation commands and
dependency records are in [review/README.md](../review/README.md).

The optional instrument has separate dependencies. In an environment with the
development lock and `prototype/requirements.txt` installed, run
`python tools/project.py prototype`. It builds the source archive, copies only
the manifest-listed prototype files into a fresh directory, runs and inspects
two synthetic datasets, and compares all output hashes. CI runs this separate
task on Windows and Linux. It is not included in the dependency-free core tests.

The separate numerical study uses the development lock and
`studies/finite-motion/requirements.txt`. Run
`python tools/project.py finite-motion` to check its source manifest, replay
the packaged study twice in clean directories and compare its numerical
reference records. CI runs this task on Windows and Linux. These are
multiprecision floating-point checks, not certificate assertions or physical
validation; see [the study](../studies/finite-motion/README.md).

After an intentional package source or input change, run
`python tools/project.py manifest`, then run `release` again. Manifest
regeneration acknowledges a new source revision; it is never a fix for an
unexplained mismatch. Include proof changes and parameter-selection disclosures.

Contributors are responsible for understanding and validating every submitted
line, regardless of which tools they use. Explain the mathematics, cite sources,
provide reproducible evidence and avoid unverified generated output. Do not add
generator-credit banners or coauthor trailers. Preserve the factual
[research-process disclosure](../review/PROVENANCE.md), including its
description of AI assistance. Never describe computation as
an experiment or as independent human peer review.

Use Conventional Commit subjects, for example `fix: bound negative endpoints`.
Sign off contributions with `git commit -s` to certify the
[Developer Certificate of Origin 1.1](https://developercertificate.org/).
Use an email you are willing to publish; GitHub's noreply identity is suitable.
The maintainer signs and creates merge commits locally using the configured
repository signing identity.
Web/API merges and automatic merges are not used.

Run `python tools/project.py hooks` to check all files with the pinned hooks.
The `.githooks/pre-commit` delegate is compatible with the maintainer's existing
guard hooks. Installing hooks is optional; do not replace organization or personal
guard hooks. CI runs the same checks. Changes to source, manifests, workflow
permissions and scientific claims require focused review.
