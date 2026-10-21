# Homometric motion: reviewer kit

Prepared for mathematical review. Start with
[REVIEWER_PACKET.md](REVIEWER_PACKET.md). Execution results and their limits are
in [VALIDATION.md](VALIDATION.md). Read the
[research provenance](PROVENANCE.md) for how the work was developed and
the limits of its AI-assisted validation.

This kit contains two distinct reproductions:

- `sage_reproduction.py` rebuilds the **nine-point** exact moment construction
  with SageMath. It uses multinomial occupation counts, cyclotomic arithmetic,
  matrix inversion and polynomial gcd/Bezout operations.
- `arb_reproduction.py` rebuilds one **63-point calibrated-iid** count channel
  with Python-FLINT/Arb. It uses exact rational matrices and native ball
  arithmetic, with a complete negative-binomial convolution and a bounded tail.

Neither script imports the discovery package or reads saved scientific results
as calculation inputs. Both implementations were prepared by the same author
as this kit; different software does not constitute independent human review.
SageMath itself uses FLINT for some operations, so these backends should not be
described as wholly independent software stacks.

## Run the exact reproduction

Use SageMath 10.8, or create an isolated environment with the supplied
`environment-sage.yml`. Activate that Sage environment, then from this
extracted directory run its Python interpreter:

```sh
python sage_reproduction.py --output sage_result.json
```

The tested environment is Linux under WSL, installed on its native Linux
filesystem. Put the environment's `bin` directory on `PATH` by activating it;
Sage also needs its bundled helper programs. `sage-linux-64-packages.json`
records the exact 386 package builds and archive hashes tested here. The YAML
pins Sage itself; a future dependency solve need not select those same builds.

`sage_review.ipynb` contains the same computation for a SageMath notebook kernel,
including in CoCalc. Its cells must be run in order. A hosted execution is
optional and has not been requested or performed for this kit.
The notebook omits the script's command-line entry point and its two imports.

## Run the Arb reproduction

Use a separate Python environment. The tested Windows interpreter is Python
3.11; the dependency is Python-FLINT 0.9.0.

```sh
python -m venv .venv
# Activate that environment using your shell's usual command.
python -m pip install --only-binary=:all: --require-hashes -r requirements.txt
python arb_reproduction.py --bits 384 --output arb_384.json
python arb_reproduction.py --bits 512 --output arb_512.json
python verify_results.py --sage sage_result.json --arb arb_384.json arb_512.json
python -B test_witnesses.py
```

The dependency lock includes official release wheel hashes for supported
platforms. Installation must fail if no matching wheel is available; it does
not silently compile a different dependency. Use new output names for each
run. The scripts refuse to overwrite results.

The 63-point check covers **only** `mu=100`, zero background, known common
calibration, instantaneous independent observations and `0<beta<=10^-16`.
It does not run the full ten-channel grid, a detector simulation, the public
finite-exposure certificate, or a practical acquisition experiment.

## What to inspect

1. Read the model assumptions and claim-to-evidence table in the reviewer packet.
2. Examine the self-contained derivations in `MATHEMATICS.md`.
3. Verify the source manifest with `python verify_manifest.py`.
4. Run the scripts and inspect their exact outputs, including the controls.
5. Check the mapping between the intended model and each encoded statement.

Recorded outputs under `results/` are supplied for comparison. Their `PASS`
status is a report of bounded software checks, not a substitute for rerunning
or reviewing the reasoning. `SOURCE_MANIFEST.json` detects changed files; it
is not a digital signature or proof of mathematical correctness.

From a development checkout, `python tools/project.py reviewer-kit` builds
the source archive, extracts this directory, verifies its inventory and
rechecks the saved exact witnesses and eight witness tests, including seven
deliberate corruptions. The same bounded
task runs in `release` and CI. It does not install or run SageMath or Arb;
fresh calculations use the separate commands above.

The original public repository is
<https://github.com/thequantumfalcon/homometric-motion>, with the reference
revision fixed at `509db87a5a8fe1f6562590133eff9d7db142b227`. No accounts,
network calls, telemetry or remote execution
are used by the mathematical scripts.
