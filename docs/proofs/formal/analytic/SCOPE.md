# Statements, proof routes and application limits

The project contains thirty-one declarations in four files. The nine
standard-deviation declarations and four sensitivity statements are unchanged.
Five statements concern explicit nine-point polynomials. Thirteen further
declarations concern Gaussian phases, finite-intensity integrability and
the first raw intensity moment.

## Standard-deviation continuity

In `StandardDeviationContinuity.lean`, the variables `X,Y : Ω -> Real`
share a measure `μ` with an explicit `IsProbabilityMeasure μ` assumption.
The `L2` theorem requires `MemLp X 2 μ` and `MemLp Y 2 μ`; the `L3`
versions require `MemLp X 3 μ` and `MemLp Y 3 μ`. These hypotheses include
the relevant measurability and finite-moment conditions.

Mathlib's real-valued variance is a total definition even outside the
finite-variance domain. The explicit `MemLp` assumptions ensure that the
quantities in these theorems are genuine finite moments. No proof relies
on an infinite moment being converted to a finite default.

The proof:

1. Identifies the squared `L2` norm with the second raw moment.
2. Identifies standard deviation with the centered `L2` norm.
3. Proves centering contraction from `Var(X) <= E[X^2]`.
4. Applies the reverse norm triangle inequality and linearity of expectation.
5. Derives `max(0, sd(X)-delta)^2 <= Var(Y) <= (sd(X)+delta)^2`.
6. Uses the probability-space `L3 -> L2` comparison to obtain the same
   bounds from a finite `L3` perturbation budget.

For the variance enclosure, the premise is that the appropriate norm
of `X-Y` is at most `delta`. This premise already implies `delta >= 0`;
no extra nonnegativity premise is silently omitted.

The result allows different means. It therefore justifies the variance
step after a coupled frequency, position or exposure perturbation: once
the specified model provides a finite `L3` error budget, that budget
bounds the standard-deviation change. It does not itself establish that
error budget.

Centering contraction here is an `L2` result. The factor two used for a
general centered `L3` change in the third-central-moment argument is a
separate issue and is not removed by this theorem.

## Cumulant sensitivity statements

`CumulantSensitivity.lean` proves the following four declarations.

| Declaration | Exact mathematical role |
| --- | --- |
| `third_cumulant_perturbation_identity` | For arbitrary real `f1,f2,f3,d1,d2,d3`, expands the change of `f3-3f1 f2+2f1^3` into all linear, mixed, quadratic and cubic terms. |
| `third_cumulant_linear_coefficient` | Rewrites `6f1^2-3f2` as `3(f1^2-(f2-f1^2))`. |
| `third_cumulant_coefficient_interval_bound` | Given `0<=f1<=F1` and `amin<=a<=amax`, proves `abs(3(f1^2-a))<=3 max(amax,F1^2-amin)`. |
| `dropping_variance_upper_term_is_false` | Refutes the proposed shortened bound at the abstract real values `f1=F1=0`, `a=amin=amax=1`. |

The first two proofs are exact ring identities. The interval proof uses
the sign and endpoint assumptions shown in the table. The formal
coefficient theorem does not require `amin>0`; positivity is a separate
essential hypothesis for the subsequent statistical ratio.

The counterexample is an abstract order control. A nonnegative Poisson
mixing intensity cannot have zero mean and unit variance, so these
numbers must not be presented as a physically admissible detector law.
A separate realizable illustration is a mixing intensity equal to three
with probability `1/3` and zero otherwise. It has mean one and variance
two: the absolute coefficient is three, whereas the invalid shortened
expression `3(F1^2-amin)` is minus three when `F1=1, amin=2`.
This illustration is not an additional Lean theorem.

The application sets `a=f2-f1^2`, where `f_j` are population factorial
moments of a mixed-Poisson law. That interpretation, the triangle
inequalities producing the absolute polynomial error bounds, the
positive-denominator checks, the search for tolerances, the threshold and
the probability guarantee remain separate mathematical steps in the
[profiled count proof](../../profiled-counts.md).

## Nine-point polynomial statements

`NinePointBezout.lean` contains five theorems over real numbers.

| Declaration | Exact mathematical role |
| --- | --- |
| `bezout_identity` | Expands the complete fixed polynomials and proves `a(t)h(t)+b(t)d(t)=c` for every real `t`, with the explicit positive integer constant. |
| `no_common_zero` | Uses that identity to prove `h(t)` and `d(t)` cannot both vanish at any real `t`. |
| `mean_factorization` | Proves the complete coefficient identity `meanDifference(t)=cofactor(t)h(t)`. |
| `cofactor_positive` | Proves the explicit product `cofactor(t)>0` under `0<t<1`. |
| `joint_moment_noncoincidence` | Concludes that `meanDifference(t)` and `d(t)` cannot both vanish under `0<t<1`. |

These definitions contain all integer coefficients. The Bezout relation is
proved by expansion, not supplied as a hypothesis or custom axiom.
The generator and `mapping.json` connect the definitions to the installed
package's fresh first- and second-moment differences. Exact re-expansion
and full field comparison are executable checks outside Lean.

The generic Gaussian characteristic-function and first finite-intensity
formula are formalized separately below. Identifying the complete
nine-point moment polynomials with that modeled intensity, constructing
the graph covariance, and inferring different bounded intensity laws from
different moments remain outside these five statements.
The local independently uncertain-strength projection,
Sturm count, Bernstein sign statements, skewness crossings and Taylor
remainder certificate remain separately justified mathematics.
This checkpoint does not formalize the complete nine-point or 63-point theorem.

## Gaussian first intensity moment

`GaussianIntensity.lean` contains thirteen declarations. The first three
give the centered Gaussian characteristic identity, quadratic-form scaling,
and the corresponding linear-phase identity. The remaining ten are:

| Declaration | Exact mathematical role |
| --- | --- |
| `continuous_phase_integrable` | A continuous real phase has a unit-modulus complex exponential, integrable under any finite measure. |
| `phase_mul_conj` | Multiplying two phase factors with the second conjugated gives the phase of their difference. |
| `finite_intensity_expansion` | The squared amplitude norm, embedded in the complex numbers, equals its finite ordered-pair expansion. |
| `pair_intensity_integrable` | Each pair term, including its fixed complex coefficient, is integrable. |
| `finite_intensity_complex_integrable` | The complex embedding of the finite intensity is integrable. |
| `finite_intensity_integrable` | The actual real squared-norm intensity is integrable. |
| `coordinate_difference_quadratic` | The charge `e_i-e_j` gives `D_ii+D_jj-D_ij-D_ji`, including when `i=j`. |
| `gaussian_coordinate_difference_phase` | Computes the expected pair phase under a centered Gaussian with explicit PSD covariance. |
| `finite_gaussian_intensity_complex_mean` | Exchanges the finite sums and integrals using proved summand integrability. |
| `finite_gaussian_intensity_mean` | Takes real parts to obtain the real first intensity moment. |

Let the index type be finite, `z_i` be arbitrary fixed complex weights,
`a` be real and `D` be a real positive-semidefinite matrix. For
`Y ~ N(0,D)` and `A(y)=sum_i z_i exp(i*a*y_i)`, the final identity is

\[
E|A(Y)|^2
=\sum_{i,j}\operatorname{Re}(z_i\overline{z_j})
 \exp[-a^2(D_{ii}+D_{jj}-D_{ij}-D_{ji})/2].
\]

The formal statement uses `EuclideanSpace Real index`,
`multivariateGaussian 0 D` and an explicit `D.PosSemidef` premise.
That predicate includes symmetry for real matrices. No positive-definite
density, matrix inverse, nonempty index, equal-modulus weights, zero
clean amplitude or independent-coordinate assumption is used.

The proof expands `A*conj(A)`, uses the real coordinate charge `e_i-e_j`,
and evaluates its characteristic function. Every pair phase is continuous
and bounded in modulus by one. Thus its fixed weighted term is integrable
under a finite measure, and finite summation gives genuine integrability
of the intensity. The proof does not rely on a totalized integral of a
nonintegrable observable. The final complex-to-real projection is valid
because the expected pair phase is real. Individual real pair coefficients
may be negative even though the full expectation is nonnegative.

For `i=j`, the difference variance is exactly zero and the term is `|z_i|^2`.
An empty index gives zero on both sides; zero scale or zero covariance gives
`|sum_i z_i|^2`. Singular covariances and negative real scales are included.
The integrability declarations are more general than the Gaussian result:
they apply to any finite measure on this Euclidean space.

Keeping off-diagonal covariance is essential. With
`D=[[1,1],[1,1]]`, weights `(1,-1)` and `a=1`, the coordinates agree almost
surely and the intensity is zero. An independence replacement on distinct
pairs would instead give `2-2 exp(-1)>0`. If that replacement also changes
diagonal pairs, a singleton with unit variance and weight already fails:
its intensity is one, not `exp(-1)`.

The result is centered. A nonzero mean requires additional deterministic
pair phases, or their absorption into the weights. The PSD premise is also
material: the pinned library constructor uses a Dirac fallback for a matrix
that fails its PSD predicate, rather than assigning that invalid covariance.

These statements establish a known generic first-moment identity. They do
not identify the concrete graph pseudoinverse with `D`, prove its PSD or
COM support, justify joint Gaussianity physically, or make the substitution
`a=omega*sqrt(beta)`. Higher raw moments, charge enumeration and complete
nine-point polynomial grouping remain separate.

## What remains unformalized

The following parts of the complete discovery argument are not
formalized by this project:

- Identification of the modeled graph observable with the generic finite
  intensity, and the required same-space couplings.
- The concrete graph covariance, COM support, motion-strength substitution,
  joint Gaussian model justification and stationary OU process, including
  finite exposure, signed kernel derivatives and their integral remainders.
- Higher raw intensity moments and their complete polynomial grouping.
- The amplitude, Taylor, increment, geometry and majorization estimates.
- A formal connection from graph/input certificates and outward numerical
  intervals to the abstract real or random variables.
- Third-central-moment perturbation and skewness separation.
- The factorial-cumulant identity for a Poisson mixture and its fixed-gain,
  fixed-background interpretation.
- The full absolute estimator-error bounds, their feasible numerical
  allocation, temporal concentration and the final classifier.

The four algebraic statements isolate useful pieces of the estimator
argument; they do not formalize its probabilistic conclusion. The nine
variance statements prove a general analytic step, not its numerical
model-specific inputs. The thirteen Gaussian declarations add a generic
first-intensity identity with explicit full covariance and integrability,
not its graph-specific application. Physical calibration, model adequacy,
novelty and human peer review remain outside the scope of all four files.
