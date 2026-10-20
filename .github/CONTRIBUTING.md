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
CLI twice in an isolated directory and checks deterministic output.
`release` runs the local lint, tests and artifact checks; it publishes nothing.

After an intentional package source or input change, run
`python tools/project.py manifest`, then run `release` again. Manifest
regeneration acknowledges a new source revision; it is never a fix for an
unexplained mismatch. Include proof changes and parameter-selection disclosures.

Contributors are responsible for understanding and validating every submitted
line, regardless of which tools they use. Explain the mathematics, cite sources,
provide reproducible evidence and avoid unverified generated output. Do not add
generator-credit banners or coauthor trailers. Never describe computation as
an experiment or as independent human peer review.

Use Conventional Commit subjects, for example `fix: bound negative endpoints`.
Sign off contributions with `git commit -s` to certify the
[Developer Certificate of Origin 1.1](https://developercertificate.org/).
Use an email you are willing to publish; GitHub's noreply identity is suitable.
The maintainer signs and creates merge commits locally using the project persona.
Web/API merges and automatic merges are not used.

Run `python tools/project.py hooks` to check all files with the pinned hooks.
The `.githooks/pre-commit` delegate is compatible with the maintainer's existing
guard hooks. Installing hooks is optional; do not replace organization or personal
guard hooks. CI runs the same checks. Changes to source, manifests, workflow
permissions and scientific claims require focused review.
