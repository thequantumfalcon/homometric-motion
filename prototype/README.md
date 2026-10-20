# Optional synthetic virtual instrument

This CPU-only prototype generates finite-beta graph-motion intensities and Poisson counts, then reports descriptive diagnostics. **Its data are synthetic. It does not validate a physical system or demonstrate a classification error guarantee.** The mathematical certificate remains a separate standard-library program.

The fixed demonstration has eight scenarios for each of two classes, with 8,192 frames per cell: IID Gaussian motion, short- and long-lag stationary OU motion, a finite-beta stress case, altered spring weights, same-covariance non-Gaussian motion, gain/background drift and correlated gain noise. All 16 cells are retained.

This source is a **portable release adaptation of previously explored scenarios**, not a new blind or preregistered validation. [reference.json](reference.json) packages exact fields extracted from a freshly reproduced public core certificate, identified by its complete certificate and source-manifest hashes. The simulator checks these packaged inputs and numerical invariants; it does not recompute or authenticate the complete certificate at runtime. The reference records the separate core reproduction command. No private workspace input is needed.

## Install and run

Supported: conventional **CPython 3.11-3.13** on platforms with compatible official NumPy/SciPy wheels. Local validation used Windows x64, CPython 3.11.9. CI runs the prototype separately from the core package on Windows and Linux with Python 3.11. Cross-platform bitwise equality is not required. Free-threaded builds, source builds and Python 3.14 or later are not supported by this lock.

From the repository root, create a separate optional environment:

```sh
python -m venv .prototype-venv
# Windows:
.prototype-venv/Scripts/python -m pip install --require-hashes --only-binary=:all: -r prototype/requirements.txt
.prototype-venv/Scripts/python -I -B prototype/run_instrument.py --output synthetic-run
.prototype-venv/Scripts/python -I -B prototype/inspect_run.py --run synthetic-run
# POSIX: replace .prototype-venv/Scripts/python with .prototype-venv/bin/python.
```

The parent of the output directory must exist. The program exclusively creates the new output directory and refuses an existing path, even an empty directory. It first verifies the package's exact source manifest. Changing source, protocol or reference is a new revision requiring an intentional manifest update and fresh review/replay.

The optional lock pins NumPy 2.2.6 and SciPy 1.16.3 to official binary-wheel SHA-256 values. No GPU, compiler, cloud service or change to the core package dependencies is required. [NumPy release](https://pypi.org/project/numpy/2.2.6/), [SciPy release](https://pypi.org/project/scipy/1.16.3/)

## Outputs and reproducibility

`summary.csv` reports every cell. `result.json` includes the numerical controls, full covariance diagnostics, dependency versions and source/reference hashes. `frames/*.npz` contains synthetic-labelled arrays, seed tuples, dimensionless times, intensities, counts, actual/reference detector rates and all 62 nominally standardized motion modes. These modes retain the full COM-zero latent trajectory in the nominal orthonormal basis. The inspector recomputes the complete sample covariance and modal kurtosis diagnostics from them.

Each run copies its protocol, reference and source manifest. Output summaries contain no wall-clock timestamps or host paths. Repeated runs in the same pinned numerical environment are checked for deterministic outputs. Different native BLAS/LAPACK builds or platforms can change eigenvector conventions or floating rounding; cross-platform bitwise equivalence is not promised.

Load arrays with pickle disabled:

```python
import numpy as np

with np.load("synthetic-run/frames/gain_background_drift_A.npz", allow_pickle=False) as data:
    assert bool(data["synthetic"])
    counts = data["counts"]
```

The inspector checks saved-file structure, labels and hashes against the chosen saved record, and recomputes covariance and kurtosis from all retained modes. It does not independently authenticate a run or certify its mathematics.

## Interpret diagnostics carefully

Threshold flags are descriptive, without calibrated false-alarm coverage. A short, correlated trajectory can have unusual empirical covariance or kurtosis **even when its stationary Gaussian generating law is correct**. A flag is not a causal diagnosis, and absence of a flag is not model acceptance. The long-lag OU scenario also retains nonzero temporal correlation.

There is one trajectory per cell; independent replication has not calibrated sampling uncertainty. This prototype does not implement finite exposure, a classifier, apparatus calibration, detector saturation or an optimal statistical test. The stress scenarios and signal-derived gains can lie outside the certified theorem domain.

[MODEL_AND_LIMITS.md](MODEL_AND_LIMITS.md) gives the equations, hardware distinction and limitations. In particular, passive RC Johnson noise does not automatically produce the target Laplacian-pseudoinverse covariance. No apparatus has been built or calibrated with this package, and a practical acquisition time is not established.
