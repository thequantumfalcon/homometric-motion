# Explicit count profiles with fresh shape-error budgets

The `count` interface requires an explicit versioned profile:

```sh
python -I -m homometric_motion count --profile short-exposure-v1 --scenario exact_geometry --output short.json
python -I -m homometric_motion count --profile long-exposure-v1 --scenario position_uncertainty --output long-position.json
```

The corresponding fresh-only API is
`build_count_certificate(*, profile, scenario="exact_geometry")`.
It does not accept a saved certificate or an arbitrary hybrid parameter
box. There is no implicit best-profile selection. The three earlier
computing commands and APIs retain their existing defaults, parameter
domains, thresholds and mathematical outputs.

## Fixed profile domains

| Profile | Scenario | Exposure cap | Frequency error cap | Position error cap |
| --- | --- | ---: | ---: | ---: |
| `short-exposure-v1` | `exact_geometry` | `1e-5` | `1e-14` | zero |
| `short-exposure-v1` | `position_uncertainty` | `1e-5` | `1e-16` | `1e-14` |
| `long-exposure-v1` | `exact_geometry` | `0.001` | `1e-14` | zero |
| `long-exposure-v1` | `position_uncertainty` | `0.01` | `1e-16` | `1e-14` |

All durations are dimensionless OU times. Both profiles retain
`B/2<=beta<=B`, fixed positive spring weights in `1±1/100001`, the
compatible stationary centered weighted Gaussian OU process, start lag
at least `1000`, fixed integrated gain in `[0.9,1.1]`, and fixed integrated
Poisson background in `[0,1]`. Conditional detector draws are independent
given the full latent trajectory. Exposure duration, strength, frequency,
weights, mean positions and channel settings stay fixed throughout each
acquisition. Allowed settings may differ by class; arbitrary mixtures
or drifting settings between windows are not covered.

The two scenarios are not nested: position uncertainty is permitted only
with a frequency-error cap 100 times tighter than the exact-geometry cap.
A smaller count for that scenario does not show that position error helps.
The integrated channel domain is also not a physical rate or dose
calibration. With a fixed signal-rate coefficient and a fixed physical
exposure duration, `h` scales with their product and with `beta`;
the integrated background scales with duration. Changing the permitted
dimensionless exposure does not by itself preserve these channel bounds.

The short profile uses the [linear exposure moments](linear-exposure.md).
The long profile uses [signed kernel bounds](signed-kernel-exposure.md),
all 512 time cells, per-cell frequency/position propagation and independent
class-wise skew unions. Both use the new estimator allocation below.
The old `eta=1e-5` estimator constraint is not imposed on this selected
allocation: its two actual error allowances are computed separately.

## Shape and moment inputs have different roles

For each class, the selected moment route supplies a positive variance
bound and a proved population shape interval `[s_l,s_h]`.
In the long profile the shape interval is the union of the per-cell
skewness intervals, not a quotient of independently pooled global
variance and third-cumulant endpoints.

Separately, let `v_-` and `v_+` be common lower and upper variance bounds
across both classes, and let `U_r` be common nonnegative raw-moment upper
bounds through order six. These pooled bounds are valid for concentration
and deterministic error estimates even when the underlying moments are
strongly coupled. They do not replace the proved shape interval.

For an exposure-averaged normalized intensity `J`, counts have conditional
mean `hJ+b`. Write `f_j=E[(C)_j]`. Factorial cumulants give

```math
a=f_2-f_1^2=h^2\operatorname{Var}(J)>0,\qquad
c=f_3-3f_1f_2+2f_1^3=h^3\kappa_3(J).
```

Thus `s=c/a^(3/2)` removes the fixed gain and background.
This is a population identity, not a claim that the finite-sample ratio
is unbiased.

With `U_0=1`, define

```math
F_k=\sum_{r=0}^k {k\choose r}h_{\max}^r b_{\max}^{k-r}U_r,\qquad
S_{jj}=\sum_{r=0}^j {j\choose r}^2r!F_{2j-r},\quad j=1,2,3.
```

These bound the raw factorial means and their second moments. Also set
`a_min=h_min^2 v_-` and `a_max=h_max^2 v_+`.
They concern factorial variance, not ordinary count variance: the latter
also contains the shot-noise term.

## The cancellation-aware polynomial bound

For estimation errors `e_j=hat f_j-f_j`, exact algebra gives

```math
\widehat a-a=e_2-2f_1e_1-e_1^2,
```

```math
\widehat c-c=e_3-3f_1e_2+(6f_1^2-3f_2)e_1
-3e_1e_2+6f_1e_1^2+2e_1^3.
```

The linear coefficient satisfies
`6f1^2-3f2=3(f1^2-a)`. Since
`-a_max<=f1^2-a<=F1^2-a_min`,

```math
|6f_1^2-3f_2|\le L_1:=3\max(a_{\max},F_1^2-a_{\min}).
```

If the upper endpoint is negative, its absolute value is still at most
`a_max`. Both branches of the maximum matter. The full error bounds for
positive tolerances `t_j` are

```math
E_2=t_2+2F_1t_1+t_1^2,
```

```math
E_3=t_3+3F_1t_2+L_1t_1+3t_1t_2+6F_1t_1^2+2t_1^3.
```

All mixed, quadratic and cubic terms remain. No `t_j<=1` assumption is
required. For example, `f1=1`, `a=1`, `e1=1`, `e2=e3=0` gives zero
linear contribution but a third-cumulant change of eight, so the linear
coefficient refinement cannot justify deleting the nonlinear terms.
The [four optional Lean statements](formal/analytic/SCOPE.md#cumulant-sensitivity-statements)
cover only specified deterministic parts of this argument.

Let `r>0` be a rational lower enclosure of `sqrt(a_min)` and put

```math
u=E_2/a_{\min},\qquad v=E_3/(a_{\min}r).
```

Then `|hat a/a-1|<=u` and `|hat c-c|/a^(3/2)<=v` on the simultaneous
raw-mean error event. The third error is standardized by `a^(3/2)`;
it is not divided by `c`.

If `u<1` and `v<min(s_A,l,s_B,l)`, the estimated variance and third
cumulant are positive. The empirical class shape lies in

```math
\left[
\frac{s_l-v}{(1+u)^{3/2}},
\frac{s_h+v}{(1-u)^{3/2}}
\right].
```

The separate values `u,v` use the available shape gap directly rather than
requiring both to stay below a common preassigned `eta`.

## Deterministic search and new threshold

Choose the exact 24-place lower cube-root enclosure of
`S_jj/L_j` as the positive direction `d_j`, where
`L=(L1,3F1,1)`. This direction is motivated by a linear relaxation,
not by a proof that it is globally optimal for the nonlinear problem.
Set `t_j=lambda d_j`.

The resulting `E2,E3` are increasing polynomials with nonnegative
coefficients for `lambda>=0`. Within the positive sign guards,
strict separation is equivalent to

```math
(s_{A,h}+v)^2(1+u)^3
<(s_{B,l}-v)^2(1-u)^3.
```

Both numerator terms are positive before squaring. The left side
increases and the right side decreases, so feasibility is an initial
interval. Zero is feasible when the population shape gap is strict.

The declared algorithm starts a fresh bracket at `[0,1]`, doubles the
upper endpoint if necessary within a fixed bound, performs 128 exact
bisections, and selects `9/10` of the positive feasible lower endpoint.
It verifies both bracket signs and the selected scale. A missing finite
bracket is a failure, not permission to return a count.

Use outward square roots to enclose the empirical-shape endpoints:
an upper square-root bound in the positive lower-endpoint denominator
and a strictly positive lower bound in the upper-endpoint denominator.
Let `tau` be the rational midpoint of the resulting gap. Return class B
exactly when

```math
\widehat a>0,\qquad\widehat c\ge0,\qquad
\widehat c^2\ge\tau^2\widehat a^3,
```

and class A otherwise. On the closed good event, the strict interval gap
makes the rule correct; the fallback and threshold-equality branches
cannot create ambiguity there. A count is bound to this newly computed
threshold, not to any threshold in the embedded original core.

## Dependent-window risk

For the selected profile cap `Tcap`, recompute

```math
\gamma=\frac{1-\delta}{\max_G\operatorname{tr}(L_G^+)},\qquad
H=1+\frac2{\gamma(1000-T_{\rm cap})}.
```

For whole-window observables `Z_i=(C_i)_j`, endpoint conditional
expectations and the Markov property reduce the covariance of separated
windows to the centered reversible-OU contraction. The bound is
`|Cov(Z_0,Z_k)|<=exp[-gamma(k lag-T)] S_jj`; independent detector
draws given the latent path introduce no additional cross-window
covariance. Since `k lag-T>=k(lag-T)` and
`sum_{k>=1} exp[-gamma k(lag-T)]<=1/[gamma(lag-T)]`, summing the
covariances gives `Var(hat f_j)<=H S_jj/N`. The
[whole-window count proof](robustness-and-counts.md) supplies the model
and spectral-gap construction.

This already accounts for temporal dependence; neither independent
windows nor independent estimated means are assumed. Conditional detector
independence remains a model hypothesis.
Chebyshev and the union bound give, separately under either class,

```math
\Pr(\text{misclassification})\le
\frac HN\sum_{j=1}^3\frac{S_{jj}}{t_j^2}.
```

Therefore

```math
N=\left\lceil20H\sum_{j=1}^3S_{jj}/t_j^2\right\rceil
```

is sufficient for at most 5% error in each class. No equal split of the
risk target is required. The exact ceiling and full risk sum are checked.
The bound is finite-sample, not an asymptotic normal approximation.

## Profiles, evaluated extras and output contract

The selected profile witnesses are:

| Profile | Exact-geometry sufficient windows | Position-uncertainty sufficient windows |
| --- | ---: | ---: |
| `short-exposure-v1` | 69,803,163,290,068 | 5,362,340,030,851 |
| `long-exposure-v1` | 36,938,105,282,195 | 16,852,383,428,868 |

An additional evaluated position domain with cap `0.001` gives
4,404,373,875,964 sufficient windows. It is a more restricted exposure
domain than the selected long position profile; it is reported as an
evaluated extra, not an implicit automatic choice. Exact geometry at
cap `0.01` is unresolved and has no allocated count.
The installed-package [extra-domain test](../../tests/test_profiles.py)
recomputes both this unresolved case and the additional position domain
from the bundled inputs, including refusal to allocate an unresolved bound.

The profile envelope distinguishes the required profile and scenario,
complete selected parameters, freshly computed original reference core,
selected moment evidence, independently proved shape/concentration bounds,
and the new allocation witness. The reference core does not supply the
selected profile's threshold or count.

Runtime calculations use only the standard library and bundled mathematical
inputs. Each release needs a new manifest and fresh installed-artifact
reproduction. Saved `summary` output remains explicitly **UNVERIFIED**;
consistency or manifest checks do not authenticate an externally supplied
file or reconstruct its physical model.

Parameter choices and search construction are informed by earlier bounds.
No blind selection, global optimum, necessary sample size, practical
experiment, established novelty, independent human peer review, or
formal verification of the complete theorem is claimed.
