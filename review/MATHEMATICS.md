# Mathematical dependencies of the reviewer scripts

These derivations are supplied for human review. Program acceptance does not
formalize them automatically.

## Nine-point construction

Let U={0,1,5}, V={0,10,22}, and V'=22-V. The sets A=U+V and B=U+V'
have nine distinct points each. Reflection conjugates the Fourier amplitude
of V up to a unit-modulus factor, so the product amplitudes give equal static
intensities at every common real frequency. Their endpoints are 0 and 27;
the listed sets differ and do not reflect into one another.

Build the fixed Laplacian L using distances strictly below 15/2. With
P=11^T/9 and H=I-P, connectedness gives
`L+=(L+P)^(-1)-P`. The script checks `LL+=L+L=H`, the trace 79/12, and
positivity of the normalized covariance D on the zero-sum subspace.

For Y~N(0,D), omega=2*pi/3, beta>0, and s=beta*omega^2/2, the Gaussian
characteristic function gives

```math
E[I^r]=\sum_{\mathbf j,\mathbf k}
 \zeta^{\sum_\ell(x_{j_\ell}-x_{k_\ell})}
 e^{-s u^T D u},\qquad
 u=\sum_\ell(e_{j_\ell}-e_{k_\ell}),\quad \zeta=e^{2\pi i/3}.
```

Grouping the positive and negative tuples by their occupation counts gives
weights `r!/prod a_i!` and `r!/prod b_i!`. The Sage script enumerates both
occupation vectors, including repeated indices and diagonal pairs. It works
in the exact cyclotomic field to check cancellation at each exponent.

For u with integer entries and sum zero, write u=T v, where T has columns
`e_i-e_8`. Let R=T^T D T and delta=9/158. The script checks that each
`R_ii/delta` and each `2 R_ij/delta` is an integer. Hence

```math
u^T D u/\delta=
\sum_i(R_{ii}/\delta)v_i^2+
\sum_{i<j}(2R_{ij}/\delta)v_i v_j
```

is an integer for every such charge. Positivity gives nonnegativity. Every
pair-charge cross term is at most 80 after division by delta. Expanding the
quadratic form of a sum of r pair charges therefore gives at most `80*r^2`.
This argument covers all orders; enumerating only small charges would not.

Put t=exp(-delta*s), so 0<t<1. The first three moments become exact integer
polynomials of degrees 80, 320 and 720. The script checks
`mu_B,1-mu_A,1=G H`, with G the explicit product in its source, strictly
positive on (0,1). It computes rational polynomials a,b satisfying
`a H+b(mu_B,2-mu_A,2)=1`. Thus the first two differences cannot both
vanish at an interior t. Since intensity is bounded by 81, equal laws would
have equal moments. This proves model-law distinction, without a uniform gap
or a finite-observation guarantee. A Sturm sequence also checks that H has
one root in (0,1), retaining the failure of a global mean ordering.

## Selected 63-point channel

The base integer motif is `{3j,3j+1: j=0,...,9} union {30}`. Its calibrated
phase perturbations use
`sin(theta)=1/sqrt(75)`, `cos(theta)=sqrt(74/75)`,
`sin(phi)=-1/sqrt(192)`, `cos(phi)=sqrt(191/192)`.
At omega=pi/3, the even phase is `((-1)^j cos(phi),sin(phi))` for j>=2,
with the unperturbed even phases for j=0,1 and the terminal phase (1,0).
The odd phase is
`(((-1)^j cos(theta)-sqrt(3) sin(theta))/2,
  ((-1)^j sqrt(3) cos(theta)+sin(theta))/2)`.

Each phase has unit modulus. Summing the even/odd/terminal terms gives zero:
the real odd sum is -1 and the terminal is +1; the imaginary even and odd
sums are -1/sqrt(3) and +1/sqrt(3). The three motif translations are
(0,31,63) for A and (0,32,63) for B. Their phases are the base, a rotation
with cosine +1/2 or -1/2 and sine sqrt(3)/2, and the negated base.

The actual position perturbations are smaller than 1/8: for example
`theta<=1/sqrt(74)<1/8` and omega>1. Pair distances change by less than
1/4, preserving the threshold-5/2 graph obtained from integer positions.
Use the permanent graph and `D=63 L+/tr(L+)`, with center of mass removed.
The script checks the rational inverse identities and reconstructs the two
positive eigenvalues lambda_1,lambda_2 of the real projected covariance.

For the quadratic surrogate `J0=|sum z_j Y_j|^2`, diagonalization gives
`J0=lambda_1 Z_1^2+lambda_2 Z_2^2` with independent standard Gaussians.
Set the common gain `g=100/((E_A J0+E_B J0)/2)` and background zero.
Conditional Poisson counting has probability-generating function

```math
G(s)=\prod_{i=1}^2(1+2g\lambda_i(1-s))^{-1/2}.
```

Its PMF is the convolution of two negative-binomial sequences of shape 1/2,
with `q_i=2g lambda_i/(1+2g lambda_i)` and coefficients
`sqrt(1-q_i) binomial(2k,k) q_i^k/4^k`. Arb encloses these sequences and
their polynomial product through K=20,000. A direct prefix convolution is
checked separately.

At s=1+1/202, below both poles, the omitted mass is at most
`G(s)/s^(K+1)`. If rho is the full affinity `sum sqrt(p_A p_B)`, its
omitted contribution is at most the square root of the two mass-tail bounds
multiplied together, by Cauchy-Schwarz. The interval sum plus this tail
encloses rho. Numerical normalization and moment checks also include tails.

## Finite-motion transfer

Let a=omega sqrt(beta), W=sum z_j Y_j, S=sum Y_j^2,
B=sum z_j(cos(aY_j)-1), and C=sum z_j sin(aY_j). The exact normalized
intensities for Y and -Y are `J_+=|B+iC|^2/a^2` and
`J_-=|B-iC|^2/a^2`. Write M=(J_++J_-)/2 and Delta=(J_+-J_-)/2.

The global inequalities `|cos x-1|<=x^2/2` and
`|sin x-x|<=|x|^3/6` yield
`|B|<=a^2 S/2`, `|C/a-W|<=a^2 S^(3/2)/6`, and
`|C/a|,|W|<=sqrt(63 S)`. Since sqrt(63)<8 and E[S^2]<=3*63^2,

```math
g E|M-J_0|\le g a^2(\sqrt{63}/3+1/4) E[S^2]
\le (35/4) g 63^2 a^2.
```

For a Poisson mass p_k(m), m>0,
`sum |p_k''(m)| <= 2/m`. The integral Taylor remainder therefore gives
`TV((Pois(m+d)+Pois(m-d))/2,Pois(m)) <= d^2/m` for 0<=d<=m.
At d=m the integrand has an integrable constant bound; if m=0 then d=0
and the distance is zero. No division by a zero mean is required.

Because `Delta^2/M <= 4|B|^2/a^2 <= a^2 S^2` when M>0, symmetry of Y
and the Poisson coupling inequality give

```math
TV(P_{G,\beta},P_{G,0})\le (47/4)g63^2 a^2
\le \delta_*=(16/9)10^{-16}(47/4)g_u63^2
```

uniformly for 0<beta<=10^-16, using omega=pi/3<4/3 and an outward upper
gain endpoint g_u. The product-law bound is N delta_*; it requires iid
snapshots and independent conditional counts.

## Necessary and sufficient sample witnesses

The threshold-one product surrogate likelihood rule has each class error
at most rho^N. Apply that same fixed rule to exact finite-motion data to get
an upper bound `rho^N+N delta_*`. For d=1-rho_upper and x=N d,
`rho^N<=exp(-x)<=1/T32(x)`, where `T32(x)=sum_{j=0}^32 x^j/j!`.
The script checks `1/T32(Nd)+N delta_* <= 1/20` at N=35,943,631.
It specifies a rule mathematically; it does not implement a numerical classifier.

Conversely, product affinity is rho^N and TV is at most sqrt(1-rho^(2N)).
Equal-prior optimal error is at least
`(1-sqrt(1-rho^(2N)))/2-N delta_*`. For d=1-rho_lower and
k=ceil(2N/32), Bernoulli's inequality gives
`rho^(2N)>=(1-k d)^32` when the base is nonnegative. The exact gate

```math
(1-kd)^{32}>1-(9/10-2N\delta_*)^2,\qquad 9/10-2N\delta_*>0
```

excludes both class errors being at most 1/20. It holds at N=9,188,576.
All smaller N are also excluded: the lower affinity-power bound is
nonincreasing, while the required squared-TV threshold is nondecreasing in
the domain with positive allowance. Thus at least 9,188,577 observations
are necessary. Failing the gate at the next integer proves no achievability.
The sufficient bound is a fixed witness, not a globally optimal sample count.

Holding g fixed in normalized units changes the raw intensity gain as beta
changes. These bounds provide no physical duration, flux, dose, independence
mechanism or apparatus validation.
