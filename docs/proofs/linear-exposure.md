# A separate linear-exposure count certificate

The optional `exposure-count` command recomputes a new conditional certificate
with dimensionless exposure cap `1e-5`. The existing `verify` and
`coordinate-count` commands retain their original `1e-20` cap and mathematical
outputs. The new envelope embeds a freshly recomputed original core as a
reference and places the selected new chain under `extension`.

```sh
python -m homometric_motion exposure-count --output exposure.json
python -m homometric_motion exposure-count --scenario position_uncertainty --output position-exposure.json
```

The corresponding fresh-only API is `build_exposure_certificate(scenario)`.
It accepts a named scenario, not a saved certificate. All runtime mathematics
uses the Python standard library and packaged inputs.

This is a mathematical extension, not an experiment, an established novelty
claim, independent human peer review or full-theorem formal verification.
The permitted dimensionless exposure cap increases by a factor of `10^15`
relative to the original route. That is a change in a sufficient proof bound,
not a measured speedup or a claim of practical acquisition feasibility.

## Model and fixed domains

Use the 63-node nominal geometries and exact-null phases proved in
[geometry and motion](geometry-and-motion.md). Let `L` be a nominal
Laplacian, `P=I-11^T/63`, `c=63/tr(L^+)`, and `D=c L^+`.
The center of mass is fixed. Every edge has an unknown but fixed positive
weight in `[1-delta,1+delta]`, with
`delta=epsilon/(1+epsilon)=1/100001`, `epsilon=1e-5`.
For that weighted Laplacian `L_w`, assume stationary motion

```
dY_s = -L_w Y_s ds + sqrt(2c) P dW_s,
Cov(Y_s) = D' = c L_w^+.
```

This specifies a compatible covariance and drift. It does not follow from
covariance closeness alone. Loewner inversion on the centered subspace yields
`(1-epsilon)D <= D' <= (1+epsilon)D`.

The initial linear-exposure theorem applies to exact nominal phases at
`omega=pi/3`, strengths `0<beta_A,beta_B<=B` and independently chosen exposure
durations `0<T_A,T_B<=1e-5`. The completed count chains additionally impose
the positive strength floor `B/2<=beta<=B`, as required for nonzero frequency
tolerance. Their fixed observation domains are:

| Scenario | Frequency error cap | Fixed mean-position error cap |
| --- | --- | --- |
| `exact_geometry` | `1e-14` | zero |
| `position_uncertainty` | `1e-16` | `1e-14` per point |

The position scenario preserves the graph under the proved contact margin.
Clean homometry applies to the nominal templates, not to arbitrary
independently perturbed mean positions.

For both count scenarios the start lag is at least `1000` in the same OU
time units, the fixed integrated normalized gain is in `[0.9,1.1]`, and the
fixed integrated Poisson background is in `[0,1]`. The count channel is
conditionally Poisson given each exposure's averaged intensity, with the
conditional detector draws independent between windows.
The channel parameters are fixed, not arbitrary mixtures over nuisance values.
For each acquisition, the exposure duration, strength, frequency, spring
weights and mean-position settings are also fixed. Allowed values may differ
between the two classes. The uniform parameter bounds do not establish a
count theorem for arbitrarily varying settings or mixtures between windows.

## Exact averaged quadratic law

Write the exact-null normalized intensity as

```
J_beta(Y) = |sum_i z_i exp(i omega sqrt(beta)Y_i)|^2 / beta,
bar J = (1/T) integral_0^T J_beta(Y_s) ds.
```

Its leading term is `Q_s=||A^T Y_s||^2`, with
`A=omega[Re z,Im z]`. The real 2 by 2 covariance kernel is

`K(t)=A^T D' exp(-L_w |t|) A`.

The covariance operator `K_T` on `L^2([0,T];R^2)` is positive and trace class.
For `bar Q=(1/T) integral Q_s ds`, Gaussian quadratic-form cumulants give

`kappa_r(bar Q)=2^(r-1)(r-1)! Tr(K_T^r)/T^r`.

This follows by diagonalizing finite covariance projections and passing to
the trace-class Gaussian expansion. In particular,

```
Var(bar Q) = (4/T^2) integral_0^T (T-u) tr[K(u)^2] du,

kappa3(bar Q) = (48/T^3)
  integral_{a,b>=0,a+b<=T} (T-a-b) tr[K(a)K(b)K(a+b)] da db.
```

The factors are `2*2` and `8*6`. The second ordering reduction uses cyclicity
and transpose invariance for products of three symmetric matrices.
It cannot be transferred without proof to arbitrary permutations of longer
noncommuting products. The time-averaged quadratic law generally has infinite
temporal rank; the instantaneous two-eigenvalue law is insufficient.

The finite Gaussian trace/cumulant identity is classical; see Lancaster,
[Traces and Cumulants of Quadratic Forms in Normal Variables](https://doi.org/10.1111/j.2517-6161.1954.tb00167.x),
JRSS B 16(2), 247–254 (1954). This application does not claim novelty for that
identity or for Gaussian OU covariance kernels.

## Uniform errors proportional to exposure time

For one fixed weighted generator, spectral calculus gives

`0 <= K(0)-K(t) <= c t A^T P A`.

Thus `tr[K(0)-K(t)]<=g t`, with `g=c*63*omega^2`.
No Loewner comparison between matrix exponentials of different generators
is used. Put `q_I=tr K(0)`, `v0=2 tr[K(0)^2]`, and
`k30=8 tr[K(0)^3]`.

All kernel factors have operator norm at most `q_I`. For
`Delta=K(0)-K(t)>=0`,

`0 <= tr[K(0)^2-K(t)^2]
   = tr[Delta(K(0)+K(t))] <= 2 q_I g t`.

Integrating the variance kernel yields

`0 <= v0-Var(bar Q) <= (4/3) q_I g T`.

Telescoping the product of three covariance factors bounds each term by
`q_I^2 g` times its pairwise time distance. The cube average of the sum of
the three pair distances is `T`, hence

`|kappa3(bar Q)-k30| <= 8 q_I^2 g T`.

This is an absolute third-cumulant error, not a claim that all spectral
triple coefficients have one sign.

## Finite-motion parity survives time averaging

Split the normalized complex amplitude into its odd sine part `S` and even
cosine-minus-one part `C`. Let `S0=i omega sum z_i Y_i`.
The amplitude remainder inequalities
`|sin t-t|<=|t|^3/6` and `|cos t-1|<=t^2/2` give

```
J_beta = Q + E + O,
E = |S|^2 + |C|^2 - |S0|^2,       an even function of Y,
O = 2 Re(S conjugate(C)),          an odd function of Y.
```

The Gaussian energy and diagonal moments in the original motion proof bound
`||S0||4<=s4`, `||S-S0||4<=beta e4`,
`||C||4<=sqrt(beta)c4`, and the analogous sixth norms.
Writing `q=E|sum z_iY_i|^2`, `p=E(sum z_iY_i)^2`,
`E_k=E(||Y||^2)^k`, `d=sum_i(D'ii)^(3/2)`, the constants are

```
s4 = omega (2q^2+|p|^2)^(1/4),
s6 = omega (6q^3+9q|p|^2)^(1/6),
c4 = omega^2 E_4^(1/4)/2,       c6 = omega^2 E_6^(1/6)/2,
e4 = omega^3 10395^(1/4)d/6,    e6 = omega^3 34459425^(1/6)d/6.
```

At the strength cap `B`, set

```
e2 = B(2s4 e4+c4^2)+B^2 e4^2,
d3 = 2B(2s6 e6+c6^2)+2B^2 e6^2,
o3 = 4B c6^2(s6+B e6)^2.
```

These bound `||E||2`, `||E-E E||3`, and `||O||3^2`, respectively.
The `L3` centering factor two is essential. Stationarity and Minkowski give
the same bounds for their time averages. The full centered Gaussian path
law is invariant under sign reversal, so odd/even orthogonality still holds.

The retained bound `x3` on the instantaneous centered leading `L3` norm also
bounds the averaged centered leading norm. Explicitly,

```
v0 = omega^4(q^2+|p|^2),
m4c = omega^8(9q^4+42q^2|p|^2+9|p|^4),
x3 = (v0 m4c)^(1/6).
```

The finite-motion third-cumulant error is therefore still bounded by

`err3=3x3^2 d3+3x3 d3^2+d3^3+3(x3+d3)o3`.

This follows from expanding the centered cubic and eliminating the terms
with one or three odd factors. Independence between observation times is
not needed.

The implementation reconstructs these constants and verifies equality with
the freshly computed marginal variance and third-cumulant bounds. It uses

```
variance_lower =
  max(0, sqrt(max(0,v0_lower-(4/3)q_I_upper g_upper T))_lower - e2_upper)^2,

third_interval =
  instantaneous_third_interval + [-8q_I_upper^2 g_upper T,
                                   8q_I_upper^2 g_upper T].
```

Stationary Jensen supplies the instantaneous finite-motion variance upper
bound and preserves all six raw-moment bounds:
`E[(bar J)^r]<=E[J_0^r]<=U_r`.
A strictly positive variance denominator is checked before dividing by
variance to the power `3/2`. The skewness division handles a signed numerator.

All cap-dependent errors are monotone. Each certified cap therefore covers
all smaller positive exposures and independent allowed strengths. In the
exploratory baseline grid, `1e-5` separated while `1e-4` and `1e-3` were
unresolved. Those unresolved bounds are not impossibility results.

## New nuisance bounds, threshold and counts

The completed extension recomputes the existing frequency proof and, for the
position scenario, the position/frequency interaction proof starting from
these new averaged moments. The positive strength floor is retained.
It then recomputes the
[count-channel and dependent-window proof](robustness-and-counts.md) and
[coordinate-tolerance witness](coordinate-counts.md).

The stationary reversible OU window bound uses
`gamma=(1-delta)/max_G tr(L_G^+)` and
`H=1+2/[gamma(lag-T)]`. The window gap is positive because
`lag>=1000>T`. The current raw moments, variance lower bound and `H`
enter a fresh count calculation. The sufficient count is an exact ceiling
of the new union-risk expression. It guarantees at most 5% error separately
in either class under the stated model.

The new common-tolerance and coordinate-tolerance routes share the newly
computed threshold. They do not borrow the original core's threshold,
sample count or exposure guarantee. In `coordinate_counts`, the explicit
comparison baseline is `extension.stages.counts`.
The exact rational tolerance witness satisfies every nonlinear
variance/third-cumulant error constraint; it is not globally optimal.

## Output and provenance contract

The envelope contains:

- `core_certificate` and its canonical content digest: the unchanged fresh
  reference computation at exposure cap `1e-20`;
- `extension.parameters`: the new complete fixed parameter contract;
- `extension.stages`: nominal and covariance inputs, `linear_exposure`,
  frequency, optional position, and newly computed common-tolerance counts;
- `coordinate_counts`: the newly computed coordinate witness and count;
- `checks`: checks of the new chain and coordinate witness.

Source integrity is a separate CLI check against the installed source
manifest. A new release revision requires a fresh manifest and artifact
reproduction; historical execution receipts are not shipped as release proof.

Saved-file `summary` remains prominently **UNVERIFIED**. It checks the fixed
reference contract, content digest, new scope and exact witness construction,
but does not recompute or authenticate the reference motion model. If an
outer CLI `source_revision` is present, it must match the current installed
manifest; this is a compatibility check, not authentication of a saved file.
API envelopes may omit that optional CLI provenance.

The certificates are large sufficient bounds for a particular conditional
classifier. They are not necessary sample counts, practical acquisition
recommendations, measurement claims, or a proof that competing methods
cannot do better.
