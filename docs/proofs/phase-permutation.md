# When a phase permutation makes motion uninformative

The observation model and interaction rule determine whether motion can
distinguish a pair. This note gives a sufficient condition for **equal exact
intensity-path laws**, followed by one example with nonzero relative motion.
It uses the same nine-point configurations as the
[finite-motion construction](nine-point-moments.md), but connects every pair
of vertices. This changes the permanent graph from threshold `15/2` to
threshold `28`; the two results concern different models.

## A criterion for the complete nonlinear observable

Fix a real observation frequency `omega`. For each class `G` let the
nominal phases be `z_G,j=exp(i omega x_G,j)` and the physical displacement
path be `xi_G`. The amplitude and intensity are

```math
F_G(t)=\sum_{j=1}^{n}z_{G,j}e^{i\omega \xi_{G,j}(t)},
\qquad I_G(t)=|F_G(t)|^2.
```

Work on continuous path space over a compact observation interval. Suppose
there are a permutation matrix `P`, a fixed real `phi`, and a joint path
law of `(xi_A,r)` such that

```math
z_B=e^{i\phi}Pz_A,\qquad
\xi_B\ \overset{\mathrm{law}}{=}\ P\xi_A+r\,\mathbf1.
```

Here `r(t)` is a real common translation, possibly dependent on `xi_A`.
The second hypothesis is equality of whole path laws, including temporal
dependencies. Equality of marginal displacement laws at individual times
would not suffice for a path conclusion.

Use the convention `(Pv)_i=v_{p(i)}`. On the coupled representative,

```math
\begin{aligned}
F_B(t)
 &=e^{i(\phi+\omega r(t))}
   \sum_i z_{A,p(i)}e^{i\omega \xi_{A,p(i)}(t)}\\
 &=e^{i(\phi+\omega r(t))}F_A(t).
\end{aligned}
```

The scalar factor has modulus one, so the intensities agree at every time.
Their path laws therefore agree. This argument is exact and uses neither
a small-motion expansion nor a Gaussian assumption. The same frequency
must multiply the physical displacements in both classes. In the
normalization `xi_G=sqrt(beta)Y_G`, the corresponding hypothesis on the
`Y` paths requires a shared `beta`.

### Exposure and observation channels

Every common measurable functional of the intensity paths has the same
law. This includes common point-observation schedules and exposure
integrals with the same durations and integration rule.

More generally, let `K(i,E)` be the conditional probability of an
observation event `E` given intensity path `i`. If the same kernel `K`
is used in both classes and their common intensity-path law is `mu`, then

```math
\Pr_A(O\in E)=\int K(i,E)\,d\mu(i)=\Pr_B(O\in E).
```

For example, this applies to conditionally Poisson records with the same
gain, background, exposure schedule and conditional joint law. It does
not assert equivalence of class-dependent channels or measurements that
also reveal positions, displacements or another unverified frequency.

For any binary decision rule using these identical observation laws,
including a randomized rule, let `p` be its probability of choosing B.
The class-A error is `p` and the class-B error is `1-p`. Thus

```math
\operatorname{error}_A+\operatorname{error}_B=1,\qquad
\frac{\operatorname{error}_A+\operatorname{error}_B}{2}=\frac12,\qquad
\max(\operatorname{error}_A,\operatorname{error}_B)\ge\frac12.
```

This concerns the specified identical observation laws, regardless of the
number of their observations. It is not a limitation on every possible
measurement or interaction model.

## A fixed nine-point example

Let `U={0,1,5}`, `V={0,10,22}`, and `V'=22-V={0,12,22}`. The
collision-free sums are

```text
A = {0,1,5,10,11,15,22,23,27}
B = {0,1,5,12,13,17,22,23,27}.
```

The Fourier sums factor as `F_A=F_U F_V` and
`F_B=F_U exp(22 i omega) conjugate(F_V)`. Their clean intensities
therefore agree at every common real frequency. They are noncongruent:
their endpoints force any line congruence to be either identity or
reflection about `27/2`, and neither identifies the sets.

The motion example now fixes **exactly** `omega=2*pi/3`. In ascending
coordinate order the residues modulo three are

```text
A: 0,1,2,1,2,0,1,2,0
B: 0,1,2,0,1,2,1,2,0.
```

Each phase vector contains three copies of `1,zeta,zeta^2`, where
`zeta=exp(2*pi*i/3)` and `1+zeta+zeta^2=0`. Match the first ascending
point of each residue in B to the first of that residue in A, and
likewise for the second and third. The resulting zero-based permutation is

```text
p = [0,1,2,5,3,4,6,7,8],    (Pv)_i = v_{p(i)}.
```

It satisfies `z_B=Pz_A`, so the criterion uses `phi=0`. This phase
identity is asserted at the selected frequency; clean homometry at all
frequencies does not extend the motion conclusion to all frequencies.

## A common complete-graph motion model

Permanently join every pair of vertices with a unit scalar spring. Both
configurations have diameter 27, so the same nominal distance rule
`distance < 28` gives this complete graph. This is a change of interaction
rule, not a claim that displacement changes the contacts of the
threshold-`15/2` model.

Write `J=11^T/9` and `H=I-J`. The complete-graph Laplacian and its
centered pseudoinverse are

```math
L=9H,\qquad L^+=H/9,\qquad \operatorname{tr}(L^+)=8/9.
```

With the same trace normalization as the other graph models,

```math
c=\frac{9}{\operatorname{tr}(L^+)}=\frac{81}{8},
\qquad D=cL^+=\frac98H.
```

The covariance `D` has trace nine, diagonal entries one, and
off-diagonal entries `-1/8`. Because `H` is the orthogonal projection
onto the zero-sum subspace, `D` is positive definite on that
eight-dimensional subspace. In particular,
`Var(Y_i-Y_j)=9/4` for distinct indices. The motion is not rigid.

In a common dimensionless clock, take the stationary centered OU process

```math
dY=-9HY\,dt+\frac92H\,dW,\qquad Y(0)\sim N(0,D),
```

where the stationary initial state is independent of future Brownian
increments. The matrix `(9/2)H` is the diffusion coefficient; its
covariance is `(81/4)H`. The Lyapunov equation holds:

```math
LD+DL=\frac{81}{4}H=2cH.
```

On the zero-sum subspace the drift rate is nine. The explicit OU solution
or its covariance integral gives

```math
\operatorname{Cov}(Y(t),Y(u))=e^{-9|t-u|}D.
```

Every permutation fixes `J` and commutes with `H`, so `PDP^T=D`.
All covariance blocks of `PY` and `Y` agree. Their centered Gaussian
finite-dimensional distributions agree, and continuity gives equality
of their path laws. Equivalently, permuting the SDE and its Brownian
motion leaves its law unchanged.

For every shared `beta>=0`, set `xi_G=sqrt(beta)Y_G`. The path
criterion holds with common translation zero. Hence the complete
nonlinear intensity paths, and the common observation channels described
above, have identical laws.

The preparation also admits a common physical covariance scale
`alpha L^+`, since `alpha=c beta=81 beta/8` in both classes. No
class-dependent calibration is needed within this complete-graph pair.
Arbitrarily unequal strengths or clocks are not covered by this equality
statement. If strength is unknown, the two model families already
intersect at every shared strength.

As a subordinate check, put `s=beta*omega^2/2`. The uniform pair variance
and the clean phase null give

```math
E[I_G]=9+\sum_{i\ne j}z_{G,i}\overline{z_{G,j}}e^{-(9/4)s}
      =9(1-e^{-(9/4)s}).
```

Equality of this mean alone would be insufficient; the path argument
establishes the stronger result.

## Reproduce the finite algebra

From a source checkout or extracted source archive, with Python 3.11 or later:

```sh
python -I docs/proofs/check_phase_permutation.py --output phase-permutation.json
```

The standalone checker uses only the standard library and its fixed
mathematical inputs. It does not load package certificates, historical
results or private data. It refuses to overwrite an output file.
The ordinary installed-package API and count certificates are unchanged.

Exact rational and `Q(zeta)` arithmetic checks the geometry, phase
permutation, all 81 reindexed formal intensity coefficients, complete-graph
projectors, pseudoinverse, covariance and Lyapunov identities. It also
checks that the retained threshold-`15/2` graphs fail this particular
full-coordinate conjugacy.

Two deliberate controls use a cross-residue permutation and a centered
rank-one covariance perturbation. Each fails the corresponding
sufficient-criterion check. Such a failure does not by itself prove
unequal intensity laws: another relation could exist.

The finite checks support the algebraic inputs. The analytic argument
above supplies the all-time, all-shared-strength and observation-kernel
conclusions; no time grid or simulation is used as a substitute.

This example refutes a universal assertion that nonzero Gaussian graph
motion always distinguishes the two configurations regardless of the
interaction rule. It leaves the threshold-`15/2` finite-motion theorem
and the 63-point results intact. It establishes no scientific priority,
physical validation, independent human peer review or complete
proof-assistant verification.
