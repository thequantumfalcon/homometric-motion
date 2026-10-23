# Finite-motion numerical study beyond the certified strength cap

This optional study uses **110-digit floating-point arithmetic**, not outward
interval arithmetic. It evaluates a fixed mathematical motion model outside
the package's certified strength range. Its observation counts are normal
approximations, not finite-sample risk guarantees. It provides no physical
validation, feasibility, novelty or independent human review.

## Model and question

The 63-site A/B configurations and their threshold-5/2 spring graphs are
reconstructed from [the geometry proof](../../docs/proofs/geometry-and-motion.md).
The graph is fixed by the clean geometry: it is not recomputed as sites move.
For each graph, `Y ~ N(0, D)` with `D = n L^+ / tr L^+`, site displacement
`sqrt(beta) Y`, frequency `w = pi/3`, and instantaneous intensity
`I = |sum_j exp(i w (x_j + sqrt(beta) Y_j))|^2`.

The package's small-strength certificates concern `beta <= B ~ 1.4e-11`.
Here a fixed grid from `1e-8` to `1` asks how the intensity skewness gap changes
when higher-order motion terms matter. There is no assertion of a nonzero gap
at every strength. As strength tends to infinity, the moments approach the
same independent uniform-phase moments for both configurations, so the
skewness gap tends to zero.

The count calculation assumes **independent instantaneous observations**, a
fixed selected `beta` shared by the classes, a common positive gain chosen so
class A averages six signal counts, and independent Poisson background of mean
one. Conditional counts are Poisson with mean `gain I + background`. Finite
exposure, temporal dependence, graph perturbations and uncertainty in strength
are not included. The package's robust certified thresholds and sample counts
do not apply to these calculations.

## Method

For nonnegative site multiplicities `a,b` of total order `k`, set `c=a-b` and
`z_j=exp(i w x_j)`. The Gaussian characteristic function gives

```text
E[I^k] = (k!)^2 sum_{|a|=|b|=k} prod_j z_j^(c_j)/(a_j! b_j!) exp(-mu c^T L^+ c),
mu = w^2 beta (n / tr L^+) / 2.
```

For zero-sum charges, the path energy is the sum of squared cumulative charges
`F_j`. The single chord `(r,r+2)` subtracts `(F_r+F_(r+1))^2/3` from this
energy. A transfer calculation sums the multiplicities along the ordered
graph, retaining both cumulative multiplicities and the flow at the chord's
first endpoint. The chord indices are `(20,22)` for A and `(41,43)` for B,
using zero-based indices; the traces are `121486/189` and `121570/189`.

Moments through order six determine the covariance of the first three count
factorial moments. Applying the delta method to factorial-cumulant skewness
gives standard deviation coefficients `s_A,s_B` and class skewnesses `g_A,g_B`.
The displayed count is `(1.645 (s_A+s_B)/|g_A-g_B|)^2`, the asymptotic normal
approximation targeting 5% error in each class with its model-specific
threshold. The statistic cancels fixed gain and Poisson background; the
predicted count still depends on their assumed values. No normal approximation
error is bounded.

## Reproduction and numerical checks

From the repository root in an isolated environment:

```sh
python -m pip install --require-hashes --only-binary=:all: -r studies/finite-motion/requirements.txt
python tools/project.py finite-motion
```

The project task builds the source archive, verifies this study's separate
[source manifest](source_manifest.json), extracts only the reviewed study
files into a clean directory, and runs the packaged `verify` command twice.
It compares fresh calculations with both published numerical summaries and
checks repeated output equality and overwrite refusal. This optional task is
separate from the standard-library certificate runtime.

`python studies/finite-motion/finite_motion.py validate` asserts:

- unrestricted charge-sum versus transfer results for raw moments one to three
  on four toy path-plus-chord graphs, with and without independent phase noise;
- both full graphs' trace, clean dark fringe and direct-covariance mean at
  `beta=0.001` and `0.1`;
- both small-beta skewnesses at `beta=1e-10` against the leading Gaussian
  formula `2(1+3 rho^2)/(1+rho^2)^(3/2)`, with `rho=|z^T D z|/(z* D z)`.

These are numerical regression checks, not certified rounding-error bounds.
`sweep`, `mixed` and `verify` require `--output FILE`; use a new path outside
this study directory. Existing outputs are never overwritten. Fresh receipts
and any exploratory output belong under `.build/` or another private output
directory, not in published source. The checked-in JSON files below are fixed
reference summaries, not simulated datasets or risk certificates.

## Fixed-grid results

[results.json](results.json) contains all ten grid rows. Selected rows are:

| beta | skewness A | skewness B | gap | normal-approximation observations |
| ---: | ---: | ---: | ---: | ---: |
| 1e-8 | 2.224759 | 2.227105 | 0.002345 | 3.21e8 |
| 1e-4 | 2.224668 | 2.227046 | 0.002378 | 3.12e8 |
| 1e-3 | 2.223853 | 2.226525 | 0.002672 | 2.47e8 |
| 1e-2 | 2.216497 | 2.221756 | 0.005259 | 6.30e7 |
| 3e-2 | 2.204787 | 2.213936 | 0.009149 | 2.03e7 |
| 0.1 | 2.195680 | 2.208063 | 0.012383 | 1.12e7 |
| 0.3 | 2.205086 | 2.215573 | 0.010487 | 1.67e7 |
| 1 | 2.093789 | 2.104194 | 0.010405 | 1.29e7 |

The best grid result misses the original exploratory target of `1e7`
observations. The grid and photon budget are selected study inputs, not
optimized or physically calibrated parameters. This reproduction validates
only the saved grid; it makes no preregistration claim and does not reuse
unrecorded exploratory runs as evidence.

## Independent phase disorder: a negative result

[mixed-results.json](mixed-results.json) holds total **mean-site** phase
variance `sigma2 = s + beta w^2` fixed, with phase covariance
`s I + beta w^2 D` and independent fraction `f=s/sigma2`. Individual sites can
have different variances because the diagonal of `D` is not constant. The
independent Gaussian site phases are resampled in every observation; they
do not represent fixed unknown coordinate defects in a single specimen.

| sigma2 | f = 0 | 0.01 | 0.03 | 0.1 | 0.3 | 0.5 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.0329 | 2.03e7 | 3.30e7 | 8.15e7 | 1.45e9 | 1.83e10 | 1.57e10 |
| 0.1097 | 1.12e7 | 1.68e7 | 3.64e7 | 4.06e8 | 1.28e10 | 4.97e9 |

These are normal-approximation observation counts. A 10% independent fraction
increases the estimated count by factors of about 36 and 72, missing the
original exploratory target of at most threefold. Even 3% increases it by
about three- to fourfold. The sampled skewness gaps reverse sign between
`f=0.1` and `0.3`, suggesting a zero between them; these floating-point samples
are not a certified root enclosure.

Independent phases alone give numerically equal first three raw intensity
moments for this pair, but a different fourth raw moment. The independent and
correlated intensities do not combine as independent additive random
intensities: interference cross terms remain. The tested skewness statistic
is consequently fragile under mixed disorder. No full count-law test was
studied.

Further work would require finite-sample error control, finite exposure and
time dependence, uncertain model parameters, other graphs and physical
systems, and a broader comparison with scattering theory. The
[research-process disclosure](../../review/PROVENANCE.md) applies: these checks
remain within the same AI-assisted workflow.
