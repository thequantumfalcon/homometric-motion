# Statements, proof routes and application limits

The project contains eighteen declarations in three files. The nine
standard-deviation declarations and four sensitivity statements are unchanged.
Five further statements concern explicit nine-point polynomials.

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

The Gaussian characteristic-function formula, finite phase sum and graph
covariance construction are not formalized here. The implication from
different moments to different bounded intensity laws is also outside
these five statements. The local independently uncertain-strength projection,
Sturm count, Bernstein sign statements, skewness crossings and Taylor
remainder certificate remain separately justified mathematics.
This checkpoint does not formalize the complete nine-point or 63-point theorem.

## What remains unformalized

The following parts of the complete discovery argument are not
formalized by this project:

- The exact finite-motion observable, its measurability, and a same-space
  coupling of the modeled variables.
- The Gaussian covariance and stationary OU process assumptions, including
  finite exposure, signed kernel derivatives and their integral remainders.
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
model-specific inputs. Physical calibration, model adequacy, novelty and
human peer review remain outside the scope of all three files.
