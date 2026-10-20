# Signed kernel bounds for positive exposure

This proof supplies the moment route for the explicit `long-exposure-v1`
count profile. The selected exposure caps are `0.001` for `exact_geometry`
and `0.01` for `position_uncertainty`. The classifier and sufficient count
are then recomputed by the [profiled count proof](profiled-counts.md).
The earlier `verify`, `coordinate-count` and `exposure-count` contracts
remain separate.

## Model and projected covariance

Use the exact nominal geometry and phases from
[geometry and motion](geometry-and-motion.md). Write `n=63`,
`omega=pi/3`, `P=I-11^T/n`, and `c=n/tr(L^+)`. Each spring has an
unknown but fixed weight in `[1-delta,1+delta]`, where
`delta=epsilon/(1+epsilon)=1/100001`. Its weighted Laplacian is `L_w`.
On the centered subspace assume the stationary process

```math
dY_s=-L_wY_s\,ds+\sqrt{2c}\,P\,dW_s,\qquad
D'=\operatorname{Cov}(Y_s)=cL_w^+.
```

The center of mass is fixed. The covariance and drift are specified
together; marginal covariance closeness alone does not establish this
temporal model. Loewner inversion gives
`(1-epsilon)D<=D'<=(1+epsilon)D`, where `D=cL^+`.

Define the `n` by `2` real matrix `A=omega[Re z,Im z]` and the leading
quadratic intensity `Q_s=||A^T Y_s||^2`. Its two-component covariance
kernel is

```math
K(t)=A^TD'e^{-L_w|t|}A.
```

For an exposure `T>0`, let `bar Q=T^(-1) integral_0^T Q_s ds`.
The positive trace-class covariance operator on
`L^2([0,T];R^2)` with kernel `K(t-s)` is denoted by `K_T`.
Gaussian quadratic-form cumulants give

```math
\kappa_r(\bar Q)=
2^{r-1}(r-1)!\,\operatorname{Tr}(K_T^r)/T^r.
```

The trace-class version follows from finite covariance projections and
their Gaussian expansion. The finite trace identity is classical; see the
source discussion in the [linear exposure proof](linear-exposure.md).
In particular,

```math
v(T)=\frac4{T^2}\int_0^T(T-t)\operatorname{tr}[K(t)^2]\,dt,
```

```math
k_3(T)=\frac{48}{T^3}
\int_{\substack{a,b\ge0\\a+b\le T}}
(T-a-b)\operatorname{tr}[K(a)K(b)K(a+b)]\,da\,db.
```

The factors are `2*2` and `8*6`. Cyclicity and transpose invariance justify
the third-order ordering reduction for symmetric factors. Longer
noncommuting products require their own argument. Spatial rank two does
not make the time-averaged Gaussian quadratic form rank two: its temporal
rank is generally infinite.

## Derivatives for one fixed generator

Set `K0=K(0)` and

```math
G=cA^TPA,\quad g=\operatorname{tr}G,\quad
m\ge\|G\|_{\rm op},\quad k\ge\|K_0\|_{\rm op}.
```

For `t>=0`, spectral calculus of the **same** fixed `L_w` gives

```math
K'(t)=-cA^Te^{-L_wt}PA,\qquad
K''(t)=cA^TL_we^{-L_wt}A.
```

Thus `0<=K(t)<=K0`, `0<=-K'(t)<=G`, and `K''(t)>=0`.
A uniform trace bound is

```math
\operatorname{tr}K''(t)\le
c\operatorname{tr}(A^TL_wA)
\le h:=c(1+\delta)\operatorname{tr}(A^TLA).
```

Only the linear generators are compared in the last inequality.
No operator monotonicity of the exponential across different generators
is asserted.

For `f(t)=tr[K(t)^2]`,

```math
f'(0)=-2\operatorname{tr}(K_0G),\qquad
f''(t)=2\operatorname{tr}\{K'(t)^2+K(t)K''(t)\}.
```

Since `tr[K'(t)^2]<=mg` and
`tr[K(t)K''(t)]<=kh`,
`0<=f''(t)<=2(mg+kh)`. Scalar Taylor's theorem followed by the
triangular time integral yields

```math
0\le v(T)-v_0+\frac43\operatorname{tr}(K_0G)T
\le \frac{mg+kh}{3}T^2,\qquad
v_0=2\operatorname{tr}(K_0^2).
```

This retains the signed first derivative.

For the third cumulant, take independent uniform times `U1,U2,U3` on
`[0,1]` and let `d_ij=|Ui-Uj|`. Then

```math
k_3(T)=8\,\mathbb E\operatorname{tr}
[K(Td_{12})K(Td_{23})K(Td_{31})].
```

At zero, cyclicity makes the first derivative
`-8 tr(K0^2 G)` because the mean sum of the three distances is one.
For the second derivative, a term containing one second derivative has
absolute trace at most `k^2 h`; a term containing two first derivatives
has absolute trace at most `kmg`. For the latter, the Hilbert–Schmidt
inequality bounds the trace by
`k sqrt(tr[K'(s)^2] tr[K'(t)^2])`. The factors need not commute.
The exact distance integrals are

```math
\mathbb E\sum d_{ij}^2=\frac12,\qquad
\mathbb E\sum_{\text{three pairs}}d_i d_j=\frac7{20}.
```

For example, each shared-vertex product has integral
`integral_0^1 (u^2-u+1/2)^2 du=7/60`.
Taylor's factor `1/2` therefore gives

```math
\left|k_3(T)-k_{30}+8\operatorname{tr}(K_0^2G)T\right|
\le \left(2k^2h+\frac{14}{5}kmg\right)T^2,\qquad
k_{30}=8\operatorname{tr}(K_0^3).
```

This is an absolute remainder bound. Individual spectral triple
coefficients can be negative.

## A rank-two majorization bound

Let `C=K_T/T` and `q=tr K0`. The positive eigenvalues of `C` sum to `q`.
For a deterministic two-component function `f`, covariance
Cauchy–Schwarz followed by time Cauchy–Schwarz gives

```math
\langle f,Cf\rangle
\le\frac1T\left(\int_0^T
\sqrt{f(t)^TK_0f(t)}\,dt\right)^2
\le\lambda_{\max}(K_0)\int_0^T\|f(t)\|^2dt.
```

Hence `||C||<=lambda_max(K0)`. The eigenvalue sequence of `C` is
majorized by
`(lambda_max(K0),q-lambda_max(K0),0,...)`: the first partial sum
is bounded by the operator norm, and every partial sum from the second
onward is at most the common total trace. Convexity of the cube, followed
by trace-class approximation, implies

```math
\operatorname{Tr}(C^3)\le\operatorname{tr}(K_0^3),
\qquad k_3(T)\le k_{30}.
```

The special fact is that the instantaneous covariance has two spatial
eigenvalues. This proof neither assumes a two-eigenvalue averaged law nor
requires every projected spectral triple coefficient to be nonnegative.

## Uniform contractions from nominal matrices

Let `K_n=A^TDA`. The covariance family gives
`(1-epsilon)K_n<=K0<=(1+epsilon)K_n`, so

```math
(1-\epsilon)\operatorname{tr}(K_nG)
\le\operatorname{tr}(K_0G)
\le(1+\epsilon)\operatorname{tr}(K_nG),
\qquad
k=(1+\epsilon)\lambda_{\max}(K_n)
```

is a valid common operator bound.

For `E=K0-K_n`, the identity
`tr(K0^2 G)=||K0 G^(1/2)||_F^2` and the norm triangle inequality give

```math
\left|\sqrt{\operatorname{tr}(K_0^2G)}
-\sqrt{\operatorname{tr}(K_n^2G)}\right|
\le\|EG^{1/2}\|_F.
```

Two valid upper bounds for the right-hand side are

```math
\epsilon\lambda_{\max}(K_n)\sqrt g,
\qquad
\epsilon\sqrt{\lambda_{\max}(K_n)\operatorname{tr}(K_nG)}.
```

The second follows by writing
`E=K_n^(1/2) R K_n^(1/2)` with `||R||<=epsilon` on the support of
`K_n`; the Loewner bounds force zero action on its nullspace. Take the
smaller outward upper bound, subtract it from the nominal square root,
truncate the lower endpoint at zero, and square. This gives a rigorous
interval for `tr(K0^2 G)` without treating matrix squaring as operator
monotone.

For a symmetric two-by-two matrix, eigenvalue bounds can use the explicit
radical expression
`(K11+K22+sqrt((K11-K22)^2+4K12^2))/2`.
All certificate calculations use rational outward root bounds, not
floating-point eigenvalue approximations.

## Finite motion survives averaging

At the nominal exact null, split the normalized amplitude into an odd
sine part `S` and an even cosine-minus-one part `C`, and write
`S0=i omega sum z_iY_i`. Then

```math
J_\beta=Q+E+O,\quad
E=|S|^2+|C|^2-|S_0|^2,\quad O=2\operatorname{Re}(S\overline C).
```

`E` is even and `O` is odd under simultaneous sign reversal of the
Gaussian path. The uniform Gaussian energy/diagonal constants
`s4,s6,c4,c6,e4,e6` are defined in the
[finite-motion transfer](linear-exposure.md#finite-motion-parity-survives-time-averaging).
They bound `||S0||p`, `||S-S0||p/beta` and
`||C||p/sqrt(beta)` for `p=4,6`. At the upper strength `B`, define

```math
e_2=B(2s_4e_4+c_4^2)+B^2e_4^2,\quad
o_2=4Bc_4^2(s_4+Be_4)^2,
```

```math
d_3=2B(2s_6e_6+c_6^2)+2B^2e_6^2,\quad
o_3=4Bc_6^2(s_6+Be_6)^2.
```

These bound `||E||2`, `||O||2^2`, `||E-mathbb E[E]||3`, and
`||O||3^2`, respectively.
Stationarity and Minkowski preserve the same bounds after exposure
averaging. The factor two in `d3` comes from centering in `L3`.
Even/odd orthogonality follows from the full path's Gaussian sign
symmetry, without independence between times.

If a leading variance interval is `[v_l,v_u]`, first truncate its lower
endpoint at zero. The finite-motion variance then belongs to

```math
\left[
\max(0,\sqrt{v_l}-e_2)^2,\,
(\sqrt{v_u}+e_2)^2+o_2
\right].
```

Stationary Jensen allows the upper endpoint to be intersected with the
instantaneous finite-motion variance bound. If `x3` bounds the centered
instantaneous leading `L3` norm, it also bounds the averaged one.
Expanding the centered cubic, with odd terms removed by sign symmetry,
gives the third-cumulant error

```math
\mathrm{err}_3=
3x_3^2d_3+3x_3d_3^2+d_3^3+3(x_3+d_3)o_3.
```

The leading third interval expands by `[-err3,err3]`.
Stationary Jensen also preserves the six raw-moment bounds:
`E[(bar J)^r]<=E[J_0^r]<=U_r`. These finite-motion bounds cover
`0<beta<=B`; the completed frequency-robust count profiles additionally
require `beta>=B/2`.

## Cells, nuisance propagation and independent class unions

Divide each declared `[0,Tcap]` into exactly 512 closed rational intervals.
On each cell, enclose the signed linear terms and quadratic remainders
above, then transfer finite motion. Zero is a limiting endpoint for the
proof, not a physical exposure duration.

Frequency and position errors must then be propagated from that same cell.
For the position scenario, combine frequency and position amplitude
errors before converting to intensity error, including the frequency–
position interaction. This is the construction in the
[position proof](position-uncertainty.md), applied to each cell's actual
baseline.

In particular, if the normalized amplitude's `L6` norm is at most `P6`
and the combined amplitude error is at most `Q6`, then the uncentered
intensity `L3` error is at most
`Delta=2P6 Q6+Q6^2`. Its centered `L3` error is at most `2Delta`.
For baseline variance `[v_l,v_u]`, third cumulant `[k_l,k_u]`, and
centered `L3` bound `M`, use

```math
v'\in[\max(0,\sqrt{v_l}-\Delta)^2,(\sqrt{v_u}+\Delta)^2],
```

```math
k_3'\in[k_l-R,k_u+R],\qquad
R=3M^2(2\Delta)+3M(2\Delta)^2+(2\Delta)^3.
```

Raw moments receive the separately derived amplitude perturbations through
order six. Check a strictly positive variance lower endpoint before each
signed skewness division.

For each class, take the minimum lower and maximum upper skewness
endpoints over **all** its propagated cells. Compare the worst class A
upper endpoint with the worst class B lower endpoint. This covers
independently chosen fixed class exposures; checking only matching cell
indices would not.

The final shape interval is this union. Independently aggregated global
variance and third-cumulant intervals are only separate moment bounds.
Their rectangle must not be used to recreate a weaker or unjustified
shape claim. The count proof uses the proved skew union and separately
pooled variance/raw bounds.

The exact-geometry cap `0.01` remains unresolved after nuisance propagation;
it is not a selected profile domain and receives no count. The position
domain at `0.001` was also evaluated and has a smaller sufficient count
than its selected `0.01` profile. That is a separate, more restricted
exposure domain, not an automatically selected optimum.

All these statements are conditional on fixed settings and the specified
stationary model. There is no arbitrary nuisance-mixture guarantee,
experimental validation, practical acquisition claim, established novelty
or formal verification of this complete analytic argument.
