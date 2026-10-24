# Scope, boundaries and related work

The release presents an explicit conditional mathematical construction and
an executable certificate. It is not an empirical finding about an
identified material or apparatus. No independent human peer review,
optimality or literature-priority claim is made. The complete theorem is
not formalized. The [Lean checkpoints](formal/README.md) cover specified
Gaussian-moment, variance, polynomial and covariance statements, with their
exact hypotheses and proof dependencies recorded separately.
Repeating a computation and checking its source bindings are different
from measuring whether a physical model holds.

## Parameter domain and unresolved directions

The model is one-dimensional: mean positions and scalar displacements lie on
the same real line. The `exact_geometry` count certificate requires fixed exact
mean geometry,
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
implementation computes both scenarios under named count/exposure methods.
The [linear exposure method](linear-exposure.md) has its own wider exposure
cap and recomputed classifier; the earlier commands retain their domains.
The package does not reproduce every
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

Patterson's diffraction analysis relates measured Fourier intensities to
interatomic difference vectors. Homometry belongs to this established
autocorrelation framework.
[A. L. Patterson, "A Fourier Series Method for the Determination of the Components
of Interatomic Distances in Crystals," *Physical Review* **46**, 372–376 (1934)](https://doi.org/10.1103/PhysRev.46.372).
Patterson later treated the structural ambiguity directly in
["Ambiguities in the X-Ray Analysis of Crystal Structures," *Physical Review*
**65**, 195–201 (1944)](https://doi.org/10.1103/PhysRev.65.195).

The clean pair uses the classical convolution/reflection mechanism studied by
Rosenblatt and Seymour: a counting measure of the form $C*D$ has the same
autocorrelation as $C*D^*$, where $D^*(x)=D(-x)$. Here the unique sums
$A=U+V$ and $B=U+(63-V)$ realize that mechanism, followed by a translation.
The homometric construction itself is an established ingredient.
[J. Rosenblatt and P. D. Seymour, "The Structure of Homometric Sets,"
*SIAM Journal on Algebraic Discrete Methods* **3**(3), 343–350 (1982)](https://doi.org/10.1137/0603035).

### Thermal diffuse scattering

Thermal diffuse scattering (TDS) already uses information carried by atomic
displacements and their correlations. The influence of thermal motion on
diffraction is classical: Debye and Waller developed the temperature-factor
theory, and Born explicitly connected diffuse scattering to thermal vibrations.
Relevant primary references are:

- P. Debye, ["Interferenz von Röntgenstrahlen und Wärmebewegung,"
  *Annalen der Physik* **348**(1), 49–92 (1913)](https://doi.org/10.1002/andp.19133480105).
- I. Waller, ["Zur Frage der Einwirkung der Wärmebewegung auf die Interferenz
  von Röntgenstrahlen," *Zeitschrift für Physik* **17**, 398–408 (1923)](https://doi.org/10.1007/BF01328696).
- M. Born, ["Diffuse Reflexion of X-Rays," *Nature* **147**, 674 (1941)](https://doi.org/10.1038/147674a0).

For this finite scalar model the connection is explicit. In dimensionless
model coordinates, put
$F(q)=\sum_j e^{iq(x_j+u_j)}$, where $q\in\mathbb R$ and the centered Gaussian
displacements have covariance $\Sigma$. Applying the Gaussian characteristic
function to each difference $u_j-u_k$ gives
```math
 \mathbb E|F(q)|^2
 =\sum_{j,k}e^{iq(x_j-x_k)}
   \exp\!\left[-\frac{q^2}{2}
   (\Sigma_{jj}+\Sigma_{kk}-2\Sigma_{jk})\right].
```
The diffuse component is $\mathbb E|F|^2-|\mathbb EF|^2$; it depends on
displacement correlations. Clean homometry equates the unweighted difference
sum, not the sum with these covariance-dependent factors. Thus clean homometry
does not imply equal motion-averaged diffraction for the two graph covariances.

Here $\Sigma=\beta D$, with $D=nL^+/\operatorname{tr}L^+$ and the center-of-mass
mode removed. This trace normalization and the overdamped OU time law are
stipulated model choices requiring physical calibration. The normalized
strength $\beta$ is not a calibrated temperature. The construction is not a
three-dimensional lattice-dynamical model of an identified material.

### Statistical optics and the count statistic

The passage from random intensity to photon counts is classical. Mandel's
photodetection model conditions a Poisson law on integrated intensity and
then averages over that intensity.
[L. Mandel, "Fluctuations of Photon Beams and their Correlations,"
*Proceedings of the Physical Society* **72**(6), 1037–1048 (1958),
Eq. (3)](https://doi.org/10.1088/0370-1328/72/6/312).
For the stipulated channel here, $K\mid\bar J\sim\operatorname{Poisson}(h\bar J+b)$,
so its factorial-cumulant generating function is
```math
 \log\mathbb E(1+s)^K=bs+\log\mathbb E e^{hs\bar J}.
```
Consequently $\kappa_r^{(F)}(K)=h^r\kappa_r(\bar J)$ for $r\ge2$, and
```math
 \frac{\kappa_3^{(F)}(K)}{[\kappa_2^{(F)}(K)]^{3/2}}
 =\frac{\kappa_3(\bar J)}{[\operatorname{Var}\bar J]^{3/2}}
```
when $h>0$ and the variance is positive. This is ordinary intensity skewness
expressed through count factorial cumulants; cancellation of fixed gain and
constant Poisson background follows from that identity. It does not hold for
arbitrary detector noise or drifting backgrounds. Mandel's model motivates
this established ingredient, not the physical validity of our channel or the
particular finite-sample certificate.

Goodman's analysis of speckle supplies the statistical-optics context for
Gaussian amplitudes and their intensity distributions.
[J. W. Goodman, "Some fundamental properties of speckle," *Journal of the
Optical Society of America* **66**(11), 1145–1150 (1976)](https://doi.org/10.1364/JOSA.66.001145).
At the clean null, the small-motion limit of the normalized intensity
$I_\beta/\beta$ is $\omega^2|Z|^2$, where
$Z=\sum_j e^{i\omega x_j}Y_j$ is complex Gaussian. The joint law of its real
and imaginary parts need not have the circular symmetry of fully developed speckle:
$p=\mathbb E Z^2$ generally does not vanish. Our moment calculation retains
that dependence and bounds the finite-motion remainder; it does not simply
assume an exponential intensity law.

Intensity distributions also have a classical crystallographic precedent in
[A. J. C. Wilson, "The probability distribution of X-ray intensities,"
*Acta Crystallographica* **2**, 318–321 (1949)](https://doi.org/10.1107/S0365110X49000813).
Wilson's symmetry-dependent intensity statistics concern a different ensemble
from the temporal OU motion of this fixed pair. They establish prior use of
intensity distributions in crystallography, not this pair's separation or a
new scattering mechanism.

### Fluctuation correlations and invariant moments

Kam's fluctuation-scattering method extracts structural information from
angular correlations of scattering fluctuations in randomly oriented molecular
ensembles. It is an established example of recovering information that an
average scattering profile suppresses.
[Z. Kam, "Determination of Macromolecular Structure in Solution by Spatial
Correlation of Scattering Fluctuations," *Macromolecules* **10**(5),
927–934 (1977)](https://doi.org/10.1021/ma60059a009).
Here the latent randomness is internal scalar displacement on a fixed spring
graph; the observable is a count statistic at one frequency. The construction
does not implement Kam's angular-correlation reconstruction.

Multi-reference alignment (MRA) is another relevant moment-method precedent:
noisy, randomly shifted copies of a signal are used to recover that signal
up to a shift. Its power spectrum and bispectrum are invariant features;
third-order information can retain phase relationships lost by the power
spectrum. Identifiability and statistical cost depend on the signal, shift
distribution and noise assumptions:

- T. Bendory, N. Boumal, C. Ma, Z. Zhao and A. Singer,
  ["Bispectrum Inversion with Application to Multireference Alignment,"
  *IEEE Transactions on Signal Processing* **66**(4), 1037–1050 (2018)](https://doi.org/10.1109/TSP.2017.2775591)
  develops invariant-feature recovery and bispectrum inversion.
- A. Perry, J. Weed, A. S. Bandeira, P. Rigollet and A. Singer,
  ["The Sample Complexity of Multireference Alignment," *SIAM Journal on
  Mathematics of Data Science* **1**(3), 497–517 (2019)](https://doi.org/10.1137/18M1214317)
  analyzes statistical cost for uniform cyclic shifts with additive Gaussian noise.
- E. Abbe, T. Bendory, W. Leeb, J. M. Pereira, N. Sharon and A. Singer,
  ["Multireference Alignment Is Easier with an Aperiodic Translation
  Distribution," *IEEE Transactions on Information Theory* **65**(6),
  3565–3584 (2019)](https://doi.org/10.1109/TIT.2018.2889674)
  shows how changing the shift distribution can make the first two moments
  sufficient under its stated signal assumptions.

The scalar intensity skewness used here is not an MRA bispectrum. Neither
those recovery guarantees nor their optimality results transfer to the present
dependent OU-window, Poisson-count classification problem.

### Coherent homometry and fluorescence counting

Diffuse scattering and coherent speckle statistics also have an established
role in studying correlations beyond average Bragg structure. Ravy distinguishes
Bragg, diffuse-scattering and coherent-diffraction homometry, and demonstrates
how higher-order speckle statistics can distinguish specific diffuse-homometric
examples. Coherence alone does not resolve an exactly homometric finite basis.
This is close conceptual precedent for statistical discrimination.
[S. Ravy, "Homometry in the light of coherent beams," *Acta Crystallographica A*
**69**, 543–548 (2013)](https://doi.org/10.1107/S0108767313022733).

Photon-count factorial cumulants, their relation to integrated random
intensity, and the effect of finite observation bins have an extensive
prior literature. Wu and Müller develop such cumulant methods for
fluorescence, including statistical effects of binning and temporal
correlations. Their application differs from a clean-homometric point pair.
[B. Wu and J. D. Müller, "Time-Integrated Fluorescence Cumulant Analysis in
Fluorescence Fluctuation Spectroscopy," *Biophysical Journal* **89**(4),
2721–2735 (2005)](https://doi.org/10.1529/biophysj.105.063685).

Mixed-Poisson factorial moments and cumulants are standard probability
identities. This release uses them to cancel the stated fixed gain and
Poisson background; it does not claim to invent that identity.
[M. Kuba and A. Panholzer, "On moment sequences and mixed Poisson
distributions," arXiv:1403.2712v5 (2014)](https://arxiv.org/abs/1403.2712v5).

Scales and Swain also use photon statistics with temporal information and
discuss the effect of constant Poisson background on factorial cumulants.
That is a close precedent for the statistical ingredients, in a different
measurement setting.
[N. Scales and P. S. Swain, "Resolving fluorescent species by their brightness
and diffusion using correlated photon-counting histograms," *PLOS ONE*
**14**(12), e0226063 (2019)](https://doi.org/10.1371/journal.pone.0226063).
See also the [2025 correction to "Resolving fluorescent species by their
brightness and diffusion using correlated photon-counting histograms,"
*PLOS ONE* **20**(3), e0320511](https://doi.org/10.1371/journal.pone.0320511),
which includes the omitted implementation supplement.

The additional deliverable here is a conditional quantitative certificate for
an explicit one-dimensional finite pair with a permanent-spring Gaussian model.
Outward-arithmetic bounds carry population separation through finite motion,
declared parameter uncertainty, finite exposure and OU window dependence to a
conditionally Poisson finite-sample classification guarantee. The result does
not establish that higher-order statistics are necessary for this pair or
that this classifier improves on conventional mean-TDS analysis.
These targeted comparisons are not an exhaustive search for that combination.
The result is a conditional quantitative certificate built from established
ingredients; it establishes no novelty or priority for homometry,
fluctuation-based discrimination or cumulant invariants.

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
