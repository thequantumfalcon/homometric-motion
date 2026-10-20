# A smaller pair: equal leading laws, distinct exact finite-motion laws

This proof concerns a separate fixed nine-point model. The 63-point
calibration domains, count guarantees and exposure bounds do not transfer
to it. All strengths compared in the global result are the same calibrated
value in the two classes.

## Geometry and stochastic model

Let

```math
U=\{0,1,5\},\quad V=\{0,10,22\},\quad V'=22-V=\{0,12,22\},
\qquad A=U+V,\quad B=U+V'.
```

Thus

```text
A = {0,1,5,10,11,15,22,23,27}
B = {0,1,5,12,13,17,22,23,27}.
```

All nine sums in each construction are distinct. Their amplitudes factor
as `F_U F_V` and `F_U F_V'`. Reflection gives
`F_V'(w)=exp(22 i w) conjugate(F_V(w))` at real w, so clean intensities
agree for every common frequency. The configurations have minimum zero
and maximum 27. They differ and are not related by reflection about 27/2,
excluding the only possible congruences on the line with these endpoints.

Join two vertices permanently when their nominal distance is less than
15/2. Let L be the resulting unweighted graph Laplacian and

```math
D=\frac{9L^+}{\operatorname{tr}(L^+)},\qquad
Y\sim N(0,D),\qquad
\omega=\frac{2\pi}{3},\qquad s=\frac{\beta\omega^2}{2}>0.
```

The finite connected graphs and covariance identities are reconstructed
exactly. Both traces are 79/12, giving the same factor 108/79 multiplying
their respective pseudoinverses. D has full support on the zero-sum subspace.
It is singular only in the translation direction.

The observable is the instantaneous intensity

```math
I_G(\beta)=\left|\sum_{x_j\in G}
 \exp(i\omega x_j+i\omega\sqrt{\beta}Y_j)\right|^2,\qquad 0\le I_G\le81.
```

The graph remains fixed even when a Gaussian displacement changes the
ordering or apparent distance of vertices. This is an exact model assumption,
not a claim that a real assembly retains such springs at every temperature.
The frequency is an exact clean-amplitude null because `F_U(omega)=0`.

## The leading approximation does not distinguish this pair

The first nonzero intensity term is
`beta*omega^2*|sum_j exp(i omega x_j)Y_j|^2`.
The two real projected covariance matrices agree up to a reflection.
Consequently this leading quadratic intensity has the same distribution
in both classes. Noncongruence or different graphs alone does not guarantee
a leading skewness distinction.

For the temporal statement, additionally assume stationary OU dynamics with
lag covariance `D exp(-L |tau|)` and a common normalized time variable.
Exact projected powers and the common characteristic polynomial establish
the same reflected covariance relation at every lag by Cayley-Hamilton.
Centered Gaussian finite-dimensional distributions are determined by these
covariances. Applying the reflection-invariant squared norm gives equal
leading intensity-process laws and equal leading exposure laws.
Continuous OU paths allow the exposure integrals to be obtained as limits
of finite-time Riemann sums, preserving equality of their laws.
This argument concerns the leading approximation, not the exact intensity.

## Exact finite-motion moments

Write `z_j=exp(i omega x_j)`. Expanding an r-th power of intensity introduces
an ordered positive and negative index tuple and its integer count-difference
vector v. The centered Gaussian characteristic-function formula gives

```math
\mu_{G,r}(s)=E[I_G^r]
 =\sum_{\mathbf j,\mathbf k}
   \left(\prod_{\ell=1}^r z_{j_\ell}\overline{z_{k_\ell}}\right)
   \exp(-s\,v^\mathsf{T}D_Gv).
```

This analytic Gaussian identity is a dependency of the numerical certificate.
The finite sum can be grouped without approximation, using exact third-root
phase arithmetic and exact covariance entries.

For this pair and r=1,2,3, each exponent is an integer multiple of 9/158.
With `t=exp(-(9/158)s)`, the moments are rational polynomials of degrees
80, 320 and 720 on `0<t<1`. The certificate retains their complete
coefficients and reconstructs

```math
V_G=\mu_{G,2}-\mu_{G,1}^2,\qquad
C_G=\mu_{G,3}-3\mu_{G,1}\mu_{G,2}+2\mu_{G,1}^3.
```

## Why two moments work at every shared finite positive strength

The exact mean difference factors as `G(t) H(t)`, where

```math
G(t)=t^{39}(1-t)^2(t+1)^2(t^2+t+1)(t^2+1)^2(t^4+1)^2(t^8+1)>0
```

for `0<t<1`, and

```math
H(t)=2t^{15}-2t^{14}+2t^{12}-2t^{11}+2t^9-2t^8
 +2t^7-t^6-t^5+2t^4-t^3-t^2+2t-1.
```

Let `D2(t)=mu_B,2(t)-mu_A,2(t)`. Rational Euclidean division constructs
integer polynomials a, b and a positive integer c satisfying

```math
a(t)H(t)+b(t)D2(t)=c.
```

The complete coefficient identity is re-expanded exactly. If the means
agree at an interior t, positivity of G forces H(t)=0; the identity forces
D2(t) to be nonzero. Otherwise the means already differ. Thus the first
two moments cannot both agree at any common finite positive strength.
Equal intensity laws would have equal moments because intensity is bounded.
Therefore the exact model laws differ at every such strength.

The optional [polynomial checkpoint](formal/analytic/README.md) checks the
complete Bezout and mean-factorization identities, cofactor positivity and
polynomial noncoincidence in Lean. Its portable generator reconstructs the
installed model and maps every coefficient. The Gaussian moment formula and
the inference about intensity laws remain separate analytic arguments.

This is pointwise distinction of laws with a shared calibrated parameter. By
itself it does not exclude intersections between the curves evaluated at
different strengths. The separate local result below handles independently
varying fixed strengths on one restricted band.

## Individual statistics cross

A rational Sturm chain shows H has exactly one root in `(0,1)`.
The mean difference changes sign there. This is equality of a mean, not
equality of the intensity laws.

After removing their endpoint factors, V and C have strictly positive
Bernstein coefficients in both classes. They therefore remain positive
throughout `(0,1)`. Define

```math
P(t)=C_B(t)^2 V_A(t)^3-C_A(t)^2 V_B(t)^3.
```

Its sign agrees with `skew_B-skew_A`, since both
variances and third cumulants are positive. Exact evaluation gives
`P(13/16)>0`, `P(7/8)<0` and `P(15/16)<0`. The exact factorization
`P=t^39(1-t)^13 R` has `R(1)>0`. Continuity gives a zero in each of
`(13/16,7/8)` and `(15/16,1)`. These prove at least two distinct interior
skewness crossovers; they do not count all roots or establish equal laws.
The residual value at one is essential; the trivial zero `P(1)=0` would
not prove the second sign change.

## A separate band with independently uncertain fixed strengths

Use the same fixed geometries, exact covariance and exact frequency, and
calibrated instantaneous intensity units. Let `t0=13/16` and fix the exact
rational coefficient

```math
c=\frac{\mu'_{A,2}(t_0)+\mu'_{B,2}(t_0)}
        {\mu'_{A,1}(t_0)+\mu'_{B,1}(t_0)},\qquad
f_G(t)=\mu_{G,2}(t)-c\mu_{G,1}(t).
```

The denominator is checked to be nonzero. Numerically, `c` is about 31.0784;
the certificate uses its complete rational value. This choice cancels the
sum of the two class derivatives at the center. It does not make each
derivative vanish and is not a proof of optimality.

For each of the five fixed radii `1/16`, `1/64`, `1/256`, `1/1024` and
`1/4096`, transform the full polynomials to the Bernstein basis on
`[t0-radius,t0+radius]`. On a closed interval, the Bernstein basis is
nonnegative and sums to one, so the minimum and maximum coefficients
give exact lower and upper bounds. Retain every coefficient and compare
the class ranges independently.

The last two radii pass this test. For the larger passing band,

```math
t_A,t_B\in[831/1024,833/1024]
\quad\Longrightarrow\quad
f_A(t_A)-f_B(t_B)>7/100000.
```

The two parameters need not be equal. Each is fixed within its class;
no statistical independence of observations is asserted. Since
`f_G=E[I_G^2-c I_G]`, no admissible class A intensity law equals an admissible
class B law within this band. This does not assert disjoint supports or
zero-error classification. The bound requires calibrated raw intensity; it
is not a gain/background-invariant skewness statement.

The three wider projection bands remain unresolved. Separate tests using
only the mean or only the second raw moment have overlapping enclosures
at all five radii. An overlapping enclosure does not prove that the
actual class ranges overlap. The certificate also retains separate
compact same-parameter Bezout bounds; those are not used as evidence
of independent-parameter separation.

This center and projection were chosen with knowledge of preceding
moment calculations. The band does not contain the isolated mean
crossover near `t=0.81515661`. No global unknown-strength separation,
detector channel, exposure tolerance or finite-sample guarantee follows.

## Restricted small-strength bounds and limitations

The separate Taylor remainder calculation uses
`|exp(-x)-sum_{k=0}^16 (-x)^k/k!| <= x^17/17!` for `x>=0`.
Exact zero coefficients are removed before normalizing moments by their
leading powers of s. Remainders are propagated through the complete
variance, third-cumulant and cross-product polynomials.

For the same s in `[1/200,1/100]`, that calculation proves
`skew_B-skew_A > 403302035/10^12`. Its declared larger cap
`s<=1/10` remains unresolved by that bound; the global crossover results
do not invalidate the restricted interval. All evaluated caps and their
outcomes remain visible in the certificate.

The first two moment differences tend to zero at both endpoint limits,
so the pointwise result supplies no uniform positive moment gap over all
positive strengths. It gives no detector-gain/background robustness,
exposure theorem, observation budget or practical measurement protocol.
The selected examples and follow-up calculations were informed by earlier
results. They were not blind selection or prospective preregistration.
No scientific priority, physical validation, independent human peer review
or complete proof-assistant verification is claimed.
