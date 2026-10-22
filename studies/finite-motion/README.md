# Finite-motion study: the skewness gap at realistic motion strength

This is a separately labelled **numerical study**. It uses multiprecision
floating point (110 digits), not outward interval arithmetic, and it does not
change, extend or certify the package's count theorems. Its sample sizes are
normal approximations, not finite-sample guarantees. No physical measurement,
novelty or practical feasibility is claimed.

## Question

The package certificates cover normalized motion strength
`beta <= B ~ 1.4e-11`, where the leading-order skewness depends only on
`rho = |z^T D z| / (z* D z)`. Physical thermal motion is many orders of
magnitude larger. Does the A/B skewness gap survive, shrink or grow when the
finite-motion terms are no longer small?

## Method

For `Y ~ N(0, D)` with `D = n L^+ / tr L^+` and site charges `c = a - b`,

```text
E[I^k] = (k!)^2 sum_{|a|=|b|=k} prod_j z_j^(c_j) / (a_j! b_j!) * exp(-mu c^T L^+ c),
mu = w^2 beta (n / tr L^+) / 2.
```

For a zero-sum charge vector, `c^T L^+ c` is the minimum flow energy
(Thomson's principle). Each path edge carries the cumulative charge `F`; the
single chord `(r, r+2)` lowers the energy by `(F_r + F_{r+1})^2 / 3`. A transfer
matrix along the sorted path, with state `(sum a, sum b)`, therefore evaluates
each moment exactly up to working precision. The script rebuilds the
threshold-5/2 graphs (path plus chord `(20,22)` for A and `(41,43)` for B) and
their traces `121486/189` and `121570/189`.

## Validation

`python finite_motion.py validate` (needs `numpy` as well as `mpmath`) checks:

- the transfer-matrix mean against the direct `O(n^2)` covariance formula at
  `beta = 1e-3` and `0.1`; they agree to 20 printed digits;
- the small-beta limit against the leading-order skewness
  (2.2247594 and 2.2271045);
- a 10^7-draw Monte Carlo at `beta = 0.1`: mean 0.57570 (exact 0.57575) and
  mean batch skewness 2.1998 +- 0.0036 (exact 2.1957) for A; 0.57557
  (0.57529) and 2.2077 +- 0.0029 (2.2081) for B.

## Results

`python finite_motion.py sweep --output results.json` reproduces
[results.json](results.json). Windows use the package's gain- and
background-free factorial-cumulant skewness statistic, independent windows,
class-A mean 6 signal counts per window and Poisson background 1.

| beta | skewness A | skewness B | gap | normal-approximation windows |
| ---: | ---: | ---: | ---: | ---: |
| 1e-8 | 2.224759 | 2.227105 | 0.002345 | 3.21e8 |
| 1e-4 | 2.224668 | 2.227046 | 0.002378 | 3.12e8 |
| 1e-3 | 2.223853 | 2.226525 | 0.002672 | 2.47e8 |
| 1e-2 | 2.216497 | 2.221756 | 0.005259 | 6.30e7 |
| 3e-2 | 2.204787 | 2.213936 | 0.009149 | 2.03e7 |
| 0.1 | 2.195680 | 2.208063 | 0.012383 | 1.12e7 |
| 0.3 | 2.205086 | 2.215573 | 0.010487 | 1.67e7 |
| 1 | 2.093789 | 2.104194 | 0.010405 | 1.29e7 |

The gap grows by about a factor of five between the certified regime and
`beta ~ 0.1`, and the normal-approximation window count falls from about
3.2e8 to 1.1e7. The bond-length RMS displacement is `sqrt(0.098 beta)` unit
spacings: about 5% at `beta = 0.03` and 10% at `beta = 0.1`.

Two derived estimates, also not certificates:

- At `beta = 0.1` the clean dark-fringe leakage stays below 1% of the mean
  signal for a frequency error up to about 0.5% (`|F'(w)| = 14.82`), compared
  with the certified `1e-14` to `1e-16` tolerances.
- At `beta = 0.1`, 20 to 100 signal counts per window give 8.9e6 to 8.3e6
  windows; 1 count with background 0.1 gives 3.8e7.

## Selection disclosure and limits

The beta grid, photon budget and a pass line of 1e7 windows were written down
before the first run. The best grid value (1.12e7) missed that line. The finer
points (0.05, 0.07, 0.15, 0.2) and the photon-budget variations were run
afterwards and are exploratory.

Open items before any broader claim:

- comparison with thermal-diffuse-scattering and fluctuation-scattering
  theory, which may already contain this observable;
- a three-dimensional or non-constructed pair, and other interaction rules
  (the complete-graph counterexample shows the result depends on them);
- temporal dependence between windows (the package bound inflates variance
  by at most about 2.3 at the stated spacing);
- a rigorous finite-sample bound in place of the normal approximation.

The study was developed with AI assistance under the maintainer's direction;
its checks are same-workflow reproductions, not independent review.
