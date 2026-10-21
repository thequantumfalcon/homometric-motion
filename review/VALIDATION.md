# Local validation record

The source calculations, notebook and witness tests below were executed
locally. This is a preparation for external review, not an external review
report. The initial kit was prepared and tested locally. Repository publication
does not imply endorsement, external review or hosted mathematical computation.
See [research provenance](PROVENANCE.md) for the role of AI assistance.

## Actual executions

| Check | Observed result | Scope |
| --- | --- | --- |
| SageMath 10.8, Python 3.14.8, Linux x86-64 under WSL | PASS | Exact nine-point geometry, covariance, all six moment polynomials, lattice controls, mean factorization, Bezout identity and Sturm root count. |
| SageMath notebook kernel | PASS | All cells executed in order; the notebook source is bound to the tested script by SHA256. |
| Python-FLINT 0.9.0, Python 3.11 on Windows, 384 bits | PASS | Fresh selected 63-point channel; 20,001 retained probabilities per class, direct-prefix control, analytical tails and exact sample-count gates. |
| The same Arb calculation at 512 bits | PASS | The same necessary and sufficient counts; affinity, gain, eigenvalue and prefix enclosures overlap across precisions. |
| Standard-library serialized witness validator | PASS | Rechecks the full saved mean factorization and Bezout identity, exact risk gates and selected enclosure consistency checks. It does not regenerate moments or all probabilities. |
| Eight focused witness tests | PASS | Original witnesses accepted; altered moment coefficients, invalid counts, changed strength contract, lost probability mass, reversed endpoints and duplicate precision rejected. |
| Fresh calculation from the installed reference project wheel | PASS | All six complete Sage coefficient arrays and both full covariance matrices agree exactly. |
| Comparison with the earlier likelihood certificate | PASS | Both fresh Arb affinity, gain and eigenvalue intervals lie inside its recorded outward intervals. The earlier result is a comparison target, never an input to the new calculation. |

The selected calibrated channel reproduces the necessary bound **9,188,577**
and sufficient bound **35,943,631** iid observations for both class errors at
most 5%, subject to the analytic dependencies and assumptions in
`MATHEMATICS.md`. These bounds are neither an optimum nor a physical
acquisition budget. The notebook concerns the separate nine-point model.

`results/comparisons.json` binds the calculation sources and saved results
by SHA256. `results/notebook.json` records the executed notebook's source
binding and actual summary output. The distributed notebook is intentionally
unexecuted, so a reviewer can start a clean run. Recorded outputs are comparison
material; the calculation scripts do not read them.

## Environment and correction history

SageMath 10.8 supports the required exact operations and passed both script
and notebook execution. A version upgrade was not needed. Its 386 dependency
archives were SHA256-verified before installation on the native Linux
filesystem. A prior Windows-filesystem environment encountered case collisions
and was not used for accepted results.

Earlier local trials exposed an unavailable temporary environment, missing
helper programs on PATH, an unsupported legacy command-line option, and an
unavailable polynomial Sturm helper. These were corrected by the persistent
native environment, its activated PATH, its Python interpreter and an explicit
exact polynomial-remainder Sturm sequence. Failed trials are retained privately;
only completed successful calculation outputs are included here.

An initial comparison harness incorrectly required the two precision-specific
risk upper bounds to overlap. Those are different rational bounds computed
from different outward endpoints, so equality or overlap is not required.
The corrected validator recomputes each exact risk bound and checks it against
1/20. It still requires overlap for quantities enclosing the same underlying
affinity, gain, eigenvalues and prefix probabilities.

Notebook execution emitted a dependency deprecation warning about date
parsing under Python 3.14. Execution completed successfully; no date parsing
is used in the mathematical calculation.

## Artifact verification

`SOURCE_MANIFEST.json` covers the distributed files except itself. Run
`python verify_manifest.py` after extraction. Its purpose is change detection;
it provides neither a signature nor a mathematical proof.

The initial local ZIP passed fresh-extraction checks. This repository edition
uses the project's import ordering and formatting, a standard requirements
filename, and publication wording. Its calculation sources are treated as a
new revision and rerun; the recorded scientific outputs remain identical.

`python tools/project.py reviewer-kit` extracts this directory from the built
source archive and checks the manifest, saved mathematical witnesses and eight
witness tests with site imports disabled. `release` and CI include that task.
This automated task does not install or run SageMath or Arb. The separate
fresh calculation commands remain in `README.md`. Private execution logs and
machine-specific environment paths are excluded from the source archive.

## Remaining review boundaries

These are same-author reconstructions using different algorithms and arithmetic
interfaces. SageMath also uses FLINT internally; shared implementations and
shared conceptual mistakes remain possible. The recorded outputs and integrity
checks do not remove the need for an independent mathematician to inspect the
statements, analytic estimates and code.

This kit does not rerun the entire public calculation catalog, the broader
OU/windowed certificate, or the Lean project. It supplies no physical
measurement, calibrated apparatus, experimental independence test, established
novelty, optimal sample complexity or complete proof-assistant verification.
