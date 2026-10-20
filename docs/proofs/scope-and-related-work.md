# Scope, boundaries and related work

The release presents an explicit conditional mathematical construction and
an executable certificate. It is not an empirical discovery about an
identified material or apparatus. No independent human peer review,
optimality or literature-priority claim is made. The complete theorem is
not formalized. The [Lean checkpoints](formal/README.md) cover only specified
finite arithmetic statements and universal polynomial identities.
Repeating a computation and checking its source bindings are different
from measuring whether a physical model holds.

## Parameter domain and unresolved directions

The default `exact_geometry` count certificate requires fixed exact mean geometry,
permanent positive spring links in the declared interval, centered Gaussian
stationary weighted OU motion, a positive nominal motion-strength band,
bounded fixed frequency error, rectangular exposure, and the specified
conditionally Poisson channel. Each class may have different fixed
admissible nuisance settings. Unknown drifting settings or mixtures over
settings are not covered by that statement. The separate `position_uncertainty`
scenario adds fixed mean errors of magnitude at most $10^{-14}$ while reducing
the frequency cap from $10^{-14}$ to $10^{-16}$. Its
[proof](position-uncertainty.md) preserves contact topology and recomputes every
count bound. Clean homometry is guaranteed for the nominal templates, not every
imperfect specimen.

Frequency uncertainty requires $B/2\le\beta_G\le B$. The underlying
exact-null moment theorem covers $0<\beta_G\le B$, but that larger
domain must not be silently attached to the detuned result. The public
implementation computes these two selected chains. It does not reproduce every
previously examined grid or demonstrate a sharp tolerance. Larger covariance
or exposure bounds that overlapped in earlier calculations were unresolved,
not proofs of equality or impossibility.

Position errors outside the stated fixed bounds, changing contacts, nonlinear or quantum dynamics,
non-Gaussian forcing, nonstationary preparation, drifting source intensity,
readout noise and non-Poisson detectors require additional arguments or
measurements. The release does not certify them. Its numerical exposure and
lag are dimensionless; conversion to seconds requires physical calibration.
The enormous sufficient count and the photon-rate demand at tiny exposures
do not establish practical feasibility.

## Why a strength floor matters away from the null

Fix a nonzero frequency $t$, with phases $z_j=e^{itx_j}$, clean
amplitude $A_0=\sum_jz_j\ne0$, and centered Gaussian $Y$.
Put $Z=\sum_jz_jY_j$, $Z_2=\sum_jz_jY_j^2$. If
```math
 L=2\operatorname{Re}(\overline{A_0}\,itZ),\qquad
 \sigma_L^2=\operatorname{Var}L>0,
```
then
```math
 I_\beta=|A_0|^2+\sqrt\beta L+\beta Q+R_\beta,\quad
 Q=t^2(|Z|^2-\operatorname{Re}(\overline{A_0}Z_2)),
 \quad\|R_\beta\|_p=O(\beta^{3/2})
```
for every finite $p$. This is a global Gaussian norm bound: apply
$|e^{ix}-1-ix+x^2/2|\le|x|^3/6$ to the pair expansion of intensity.
The finite sum of Gaussian third-power norms bounds the remainder.

The linear term is odd and the quadratic term is even under $Y\mapsto-Y$.
Centering and Hölder consequently give
```math
 \operatorname{Var}I_\beta=\beta\sigma_L^2+O(\beta^2),\qquad
 \kappa_3(I_\beta)=3\beta^2E[L^2(Q-EQ)]+O(\beta^{5/2}).
```
Its skewness therefore tends to zero. The coefficient may vanish without
altering that conclusion.

For this construction, the zero of $F_U$ at $\omega$ is isolated:
$F_U$ is an entire nonzero exponential sum and $F_U(0)=21$.
The translation factors are nonzero at $\omega$. The projected covariance
of $(\operatorname{Re}Z,\operatorname{Im}Z)$ has determinant
$(q^2-|p|^2)/4>0$ there, as the exact certificate verifies.
Continuity preserves positive definiteness nearby. Thus every sufficiently
small fixed nonzero detuning gives nonzero $A_0$ and nondegenerate $L$
for both nominal classes.

At each such fixed detuning, the closures of both skewness families over
$0<\beta_G\le B$ contain zero. There is no strictly positive uniform
skewness gap over that full independent-strength domain. The same limit
holds when the strengths are fixed positive multiples of a common scale
tending to zero. Detuning is fixed first; the expansion constants need not
be uniform as detuning tends to zero.

This boundary does not prove equality of distributions, failure of all
statistics, or failure at a fixed positive strength. It does not contradict
the certified positive-floor domain.

## Finite error is different from proof confidence

The 5% quantity is a classifier's risk under its model, not a confidence
rating for mathematical truth. The same concentration argument can target
any positive risk by increasing its sufficient sample size. Zero error at
finite sample size is not promised: for a finite number of Poisson windows,
the all-zero count record has positive probability in both classes.
No deterministic or randomized rule can classify that shared event with
zero error in both classes.

Likewise, the population factorial-cumulant invariant can remove a fixed
positive gain without a universal finite-sample budget over gains tending
to zero. For a fixed finite observation count, coupling to the common
pure-background process bounds the probability of any signal photon by
the expected total signal, which tends to zero with gain. The count theorem
therefore states its positive lower gain bound and finite upper channel
bounds explicitly.

## Established ingredients and close precedents

Homometry and information beyond ordinary diffraction intensity are
established subjects. Ravy examines how coherent measurements and
higher-order speckle statistics can distinguish some forms of homometry,
while other clean finite-basis homometries remain unresolved by coherence
alone. This is close conceptual precedent, not this graph-Gaussian
construction or its quantitative robustness certificate.
[Ravy, “Homometry in the light of coherent beams”](https://arxiv.org/pdf/1303.3792).

Photon-count factorial cumulants, their relation to integrated random
intensity, and the effect of finite observation bins have an extensive
prior literature. Wu and Müller develop such cumulant methods for
fluorescence, including statistical effects of binning and temporal
correlations. Their application differs from a clean-homometric point pair.
[Wu and Müller, primary fluorescence cumulant study](https://pmc.ncbi.nlm.nih.gov/articles/PMC1366773/).

Mixed-Poisson factorial moments and cumulants are standard probability
identities. This release uses them to cancel the stated fixed gain and
Poisson background; it does not claim to invent that identity.
[Kuba and Panholzer, mixed-Poisson moment identities](https://arxiv.org/pdf/1403.2712v5).

Scales and Swain also use photon statistics with temporal information and
discuss the effect of constant Poisson background on factorial cumulants.
That is a close precedent for the statistical ingredients, in a different
measurement setting.
[Scales and Swain, primary study](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0226063).
The linked article has a
[published correction](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0320511).

These targeted comparisons are not an exhaustive search for the exact
combined claim. The warranted framing is a concrete construction with a
conditional quantitative certificate built from established ingredients,
not an assertion that fluctuation-based disambiguation or cumulant
invariants are new.

## Release revision and reproducibility

The package is a new adaptation of previously examined mathematical
parameters. The frequency cap was selected after earlier bounds were known.
Its exact strength cap is a declared input; the proof recomputes the bounds
at that value and does not rely on a prior output to establish validity.

The release's own source manifest identifies its code and mathematical
resources. Its CLI validates that manifest and creates a fresh certificate.
No old execution receipt, historical source freeze or external witnessing
is implied. Deterministic outputs contain no machine paths or timestamps.
Source-hash agreement detects changes relative to the included manifest;
it is not itself a cryptographic guarantee about an untrusted distributor,
a formal proof of software correctness, or physical validation.
