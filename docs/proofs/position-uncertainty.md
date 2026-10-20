# A separate certificate for fixed mean-position errors

For the original `verify` and `coordinate-count` methods, the
`position_uncertainty` scenario keeps the same nominal templates,
motion-strength band $B/2\le\beta_G\le B$, covariance radius $10^{-5}$,
spring-weight radius $1/100001$, exposure cap $10^{-20}$, minimum start
lag $1000$, integrated normalized gain range $[0.9,1.1]$, and integrated
Poisson background range $[0,1]$. It changes the frequency cap to
$d=10^{-16}$ and allows fixed mean offsets
$x_i'=x_i+\Delta x_i$ with $|\Delta x_i|\le\rho=10^{-14}$.
The two classes may use different fixed admissible settings.
The [linear exposure extension](linear-exposure.md) reuses the perturbation
inequalities below with its own newly bounded exposure baseline and recomputes
the finite-window guarantee at exposure cap $10^{-5}$.

These values were selected after earlier bounds were examined. This is a
new release calculation at declared parameters, not prospective validation.
The `exact_geometry` default remains a separate scenario with frequency
cap $10^{-14}$ and zero position error.

## Mean topology and displacement coordinates

The [nominal construction](geometry-and-motion.md) places each vertex at
an integer plus a shift of magnitude strictly less than $1/8$. An integer
pair distance is at least $1/2$ from the contact threshold $5/2$.
The two nominal shifts change it by strictly less than $1/4$. Every
nominal mean pair distance is therefore strictly more than $1/4$ from
that threshold.

The additional mean errors change any pair distance by at most $2\rho$.
The contact graph is unchanged whenever $2\rho<1/4$, with remaining
strict margin $1/4-2\rho>0$. Nominal adjacent spacings exceed $3/4$,
so order and distinctness also persist. Preserved nonisomorphic contact
graphs imply that the two imperfect mean-configuration families remain
noncongruent.

The permanent spring links are imposed about the imperfect means. Keeping
the contact graph does not establish a real spring constant or a Gaussian
motion law. Both remain model assumptions. The normalization is still
$D'=c_GL_w^+$, $c_G=63/\operatorname{tr}L_G^+$, based on the nominal
unweighted graph, and the displacement covariance is $\beta_GD'$.
Vertex indices and the zero-sum displacement projection are unchanged.
A shift of the mean centroid is allowed; it does not redefine beta or
reintroduce the center-of-mass displacement mode. Links are not rebuilt
after every Gaussian displacement.

## Combining amplitude errors before intensity errors

Write $n=63$, $\beta_{\min}=B/2$,
```math
 A_t(x,y)=\sum_i e^{it(x_i+\sqrt\beta y_i)},\qquad
 J_t(x,y)=|A_t(x,y)|^2/\beta.
```
The pointwise Lipschitz bound for complex phases gives
```math
 \frac{|A_t(x+\Delta x,y)-A_t(x,y)|}{\sqrt\beta}
 \le\frac{(\omega+d)n\rho}{\sqrt{\beta_{\min}}}
 =Q_{\rm pos}.
```
This deterministic estimate holds in every finite $L^p$ norm. The factor
$\omega+d$ includes the interaction between frequency and position errors.
Decompose the total amplitude error as
```math
 A_t(x+\Delta x,y)-A_\omega(x,y)
 =[A_t(x+\Delta x,y)-A_t(x,y)]
  +[A_t(x,y)-A_\omega(x,y)].
```
The second term is the nominal-position frequency error already bounded
in [the frequency proof](robustness-and-counts.md). There is no need to
replace its nominal coordinate sum by an enlarged coordinate sum.

Let $P$ bound $\|A_\omega(x,Y)/\sqrt\beta\|_6$ and let
$Q_{{\rm freq},r}$ bound the frequency amplitude error in $L^{2r}$.
For the third-moment bound use
```math
 Q=Q_{{\rm freq},3}+Q_{\rm pos},\qquad
 \|J_t(x+\Delta x,Y)-J_\omega(x,Y)\|_3
 \le 2PQ+Q^2=\delta.
```
Stationarity makes this bound uniform in time. Minkowski's inequality
for the rectangular integral gives the same bound for exposure averages.

The baseline in this calculation is the original exact-frequency,
covariance-uncertain exposure law. The total amplitude perturbation is
converted to an intensity error once. The already propagated frequency
intensity error is not added again.

## Centered and raw moments

Let the baseline exposure variance and third cumulant lie in
$[v_-,v_+]$ and $[k_-,k_+]$, and let its centered $L^3$ norm be at
most $M$. Position and frequency changes can change the mean.
Centering contracts the $L^2$ norm, while its $L^3$ norm is at most
twice the uncentered error. Consequently
```math
 v_{\rm actual}\in
 [\max(0,\sqrt{v_-}-\delta)^2,(\sqrt{v_+}+\delta)^2],
```
and, with $e=2\delta$,
```math
 k_{\rm actual}\in[k_--E_3,k_++E_3],\qquad
 E_3=3M^2e+3Me^2+e^3.
```
The calculation verifies a positive variance lower bound and divides
the signed third-cumulant interval by the positive variance-to-the-$3/2$
interval. The resulting class skewness intervals are strictly disjoint.

For each $r=1,\ldots,6$, let $U_r$ be the original instantaneous
covariance-robust raw-moment bound. Then
```math
 E J_{\rm actual}^r
 \le [U_r^{1/(2r)}+Q_{{\rm freq},r}+Q_{\rm pos}]^{2r}.
```
Stationarity and Jensen give the same bound for the exposure average.
The executable checks that setting $\rho=0$ recovers the frequency
variance, third cumulant, skewness and all six raw-moment bounds exactly.

Offsets do not change the graph constants, so the common physical
scale band remains $(B/2)\max_Gc_G\le\alpha\le B\min_Gc_G$.
Fixed gain and fixed Poisson background still cancel from factorial
skewness. The whole-window OU contraction and the count-channel proof
apply to the altered observation functional on the same stationary
process.

## A fresh finite-count bound

All six count factorial moments, second-moment bounds, polynomial error
constants, mean-estimation tolerance and the classifier threshold are
recomputed from the position-uncertain moments. The count proof uses the
same inequalities as [the default scenario](robustness-and-counts.md).
No earlier numerical count is an input.

For this scenario the denominator roots $\sqrt{1\pm\eta}$ and
$\sqrt{a_{\min}}$ have exact outward decimal brackets of width at most
$10^{-80}$. Expansion uses $(1\pm\eta)\sqrt{1\pm\eta}$.
The default preserves its original $10^{-72}$ interval expansion and
$10^{-60}$ lower root for $a_{\min}$. Both choices are verified by exact
root powers; these arithmetic choices are not experimental precision.

The exact ceiling is $975028627229038193209$ observation windows for
individual-class risk at most $1/20$. This sufficient count is extremely
conservative. Its being smaller than the default count does not imply
that position error improves distinguishability: the two scenarios use
different frequency caps, and sufficient bounds are not necessary costs.

## What the robustness statement does not preserve

The nominal templates are clean-homometric at every frequency. Independent
fixed position errors need not preserve that equality or the exact phase
null. The new result separates stochastic shape laws in two neighborhoods
of the nominal templates; it does not assert clean ambiguity for every
imperfect pair. Some imperfect specimens may already differ in clean
diffraction.

The positive strength floor is essential to this bound, which contains
$1/\sqrt{\beta_{\min}}$. Arbitrary drift, mixtures over nuisance settings,
changing contacts, non-Gaussian forcing, nonstationary preparation,
non-Poisson response and apparatus calibration remain outside the theorem.
The result supplies no physical validation or practical acquisition claim.
