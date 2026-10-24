# Statements, proof routes and application limits

The project contains 101 proved declarations in nine files. The forty
earlier declarations are unchanged. Four new modules add seven
physical-parameter statements, five integer-charge histogram statements
and forty-nine covariance statements. The physical and histogram modules
preserve the accepted proof bodies behind new modular imports; the two
graph sources retain their accepted bytes. Definitions are listed below
and are not counted as proved declarations.

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

The generic Gaussian characteristic function and all natural finite-intensity
moments are formalized separately below. Identifying the complete
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
`a=omega*sqrt(beta)`. The next module proves generic higher raw moments;
the later physical and covariance modules supply some further application
steps. Executable enumeration and nine-point polynomial grouping remain separate.

## Every natural raw intensity moment

`GaussianMoments.lean` imports `GaussianIntensity` and adds two definitions
and nine proved declarations. The prior first-intensity source is unchanged.
For a finite index type and each natural `r`, let

\[
I(y)=\left|\sum_i z_i e^{ia y_i}\right|^2,\qquad
u_p=\sum_{k=0}^{r-1}(e_{p(k).1}-e_{p(k).2}),\qquad
w_p=\prod_{k=0}^{r-1}z_{p(k).1}\overline{z_{p(k).2}},
\]

where `p : Fin r -> (index x index)` is ordered. The definitions are
`moment_charge` and `moment_weight`. Repetition and multiplicity are retained.
For full real PSD `D`, arbitrary fixed complex weights and real `a`, the
final theorem proves

\[
\int I(y)^r\,dN(0,D)(y)
=\sum_p \operatorname{Re}(w_p)
  \exp[-a^2u_p^\mathsf{T}D u_p/2].
\]

| New declaration | Exact mathematical role |
| --- | --- |
| `inner_moment_charge` | The inner product with the charge is the selected sum of coordinate differences. |
| `tuple_phase_product` | The product of pair phases is the phase of the summed charge. |
| `finite_intensity_power_expansion` | Expands the complex embedding of the real intensity power into the complete ordered tuple sum. |
| `tuple_intensity_integrable` | Each weighted tuple phase is genuinely integrable under a finite measure. |
| `finite_intensity_power_complex_integrable` | Proves integrability of the complete complex-embedded intensity power. |
| `finite_intensity_power_integrable` | Proves integrability of the actual real nonnegative power. |
| `gaussian_tuple_phase` | Evaluates each charge phase using the full PSD covariance. |
| `finite_gaussian_intensity_complex_moment` | Interchanges the finite sum and integral and evaluates every term. |
| `finite_gaussian_intensity_moment` | Takes real parts to obtain the stated real moment formula. |

The finite-power expansion uses ordered tuples, not unordered sets of
pairs. The charge collects their phases; the coefficient remains the
full complex product. Taking a product of real parts or replacing the
coefficient by its absolute value would generally give a different
formula. Individual real coefficients may be negative.

The integrability statements hold for any finite measure on the Euclidean
space, since a finite sum of fixed weighted phases is bounded and continuous.
The evaluated expectation uses the centered Gaussian probability measure
and the explicit PSD premise. It never relies on non-PSD fallback behavior.
No invertibility, density, independent coordinates, clean null, nonempty
index, unit weights or positive phase scale is assumed.

At `r=0` there is one empty tuple, its charge is zero and its weight is one:
the probability integral is one, including for an empty coordinate type.
For empty coordinates and positive `r`, there are no tuples and both sides
vanish. Repeated coordinates and diagonal pairs are included.

A bounded wrong-power control changes only the final left-hand exponent
from `r` to `r+1`. It is false for a singleton with `D=0`, `z=2`, `a=0`
and `r=0`: the changed left-hand side is four while the empty-tuple sum is
one. This exact witness explains the failed variant; rejection of a proof
attempt alone would not show that a statement is false.

This closes a generic natural-moment identity. It does not identify a
graph-derived matrix with the formal covariance, establish its PSD or COM
support, make the substitution `a=omega*sqrt(beta)`, group ordered tuples
into occupation histograms, or identify a program's variogram and complete
polynomial coefficient tables. The existence of the abstract sum does not
formalize an executable enumeration, its resource bounds or its implementation.
The following modules supply physical substitution, mathematical charge
fibers and concrete PSD/COM results, with the remaining links stated below.
The generic theorem contains no temporal, detector or classifier conclusion.

## Physical-parameter substitution

`GaussianChargeApplication.lean` imports `GaussianMoments`. Its definition
`nominal_phase x omega i` is `exp(i*omega*x_i)`. For `Y~N(0,D)`,
full real PSD `D`, real `omega`, `beta>=0` and any natural order `r`, set

\[
I_{x,\omega,\beta}(y)=
\left|\sum_i e^{i\omega(x_i+\sqrt{\beta}y_i)}\right|^2.
\]

The module proves

\[
E[I_{x,\omega,\beta}(Y)^r]
=\sum_p\cos(\omega\langle x,u_p\rangle)
  \exp[-(\beta\omega^2/2)u_p^\mathsf{T}D u_p].
\]

| Declaration | Exact role |
| --- | --- |
| `moment_charge_total_zero` | Every ordered-tuple charge has coordinate sum zero. |
| `nominal_moment_weight` | The full unit-weight product equals the nominal phase of the summed charge. |
| `nominal_moment_weight_real` | Its real part is the cosine of the nominal charge phase. |
| `physical_amplitude_factorization` | Separates nominal and displacement phases, with scale `omega*sqrt(beta)`. |
| `physical_strength_exponent` | For `beta>=0`, the squared scale is `beta*omega^2`, not `beta^2*omega^2`. |
| `physical_intensity_power_integrable` | Proves genuine integrability of every natural real intensity power under any finite measure. |
| `finite_physical_gaussian_intensity_moment` | Combines the factorization, nominal weight and full Gaussian charge formula. |

The nonnegative-strength premise is needed for the squared-square-root
identity. Integrability itself does not need that premise: all real phase
terms remain bounded. The evaluated Gaussian moment uses both PSD and
nonnegative strength. Singular covariance, empty indices, order zero,
zero strength, and negative or zero frequency remain included.

The wrong replacement `beta^2` is already false for two unit weights,
zero nominal positions, `D=identity`, `omega=1`, `beta=4`, `r=1`:
the correct mean is `2+2 exp(-4)` rather than `2+2 exp(-16)`.
This explicit evaluation explains the failed variant; the separate
formal scalar inequality is not a formal instantiation of that entire
two-index integral.

## Integer-charge histogram

`ChargeHistogram.lean` imports the physical-parameter module and defines:

| Definition | Meaning |
| --- | --- |
| `integer_charge` | Sum of integer basis differences for an ordered tuple. |
| `charge_vector` | Coordinatewise real embedding into Euclidean space. |
| `charge_support r` | Finite image of all order-`r` tuple charges. |
| `charge_multiplicity r u` | Cardinality of the exact fiber over `u`. |

The five statements are `charge_vector_of_tuple`,
`integer_charge_total_zero`, `charge_histogram_sum`,
`charge_histogram_mass` and `finite_physical_gaussian_intensity_histogram`.
They identify the real charge, prove its conservation, regroup any
real-valued function over the finite fibers, count the entire tuple
domain, and apply the regrouping to the physical moment:

\[
E[I_{x,\omega,\beta}(Y)^r]
=\sum_{u\in\mathcal U_r}m_r(u)
 \cos(\omega\langle x,u\rangle)
 \exp[-(\beta\omega^2/2)u^\mathsf{T}D u],\qquad
\sum_{u\in\mathcal U_r}m_r(u)=n^{2r}.
\]

The fiber theorem requires no positivity of the function being summed.
The phase and attenuation depend only on charge; their nominal unit
weights make each coefficient the fiber cardinality. Arbitrary non-unit
complex weights would need weighted fibers instead.

At order zero there is one empty tuple and zero charge, even for an
empty index type, so the mass is `0^0=1` in that boundary case. Empty
indices at positive order give no tuples and zero mass. At two indices
and order one, zero charge has multiplicity two and the two opposite
nonzero charges have multiplicity one. At zero frequency the correct
intensity moment is four, whereas discarding multiplicities gives three.
That finite evaluation is a mapping control; the scalar `4!=3` statement
alone is not a formal proof of the complete two-index evaluation.

The source specifies a mathematical finite image and fiber cardinality.
It does not verify dictionary convolution, resource limits, phase-residue
or quadratic-exponent grouping, or a program's complete polynomial table.

## Concrete nine-point covariance

The accepted modules are `GraphCommon.lean` and `GraphCovariance.lean`,
in namespace `HomometricMotion.GraphCovariance`. Their literal node orders are

```text
A = [0,1,5,10,11,15,22,23,27]
B = [0,1,5,12,13,17,22,23,27].
```

Distinct mean-position nodes are adjacent exactly when their distance is
strictly less than `15/2`. These are permanent nominal graphs; displacement does not
recompute topology. Each has twelve unoriented edges, whose chosen
orientation defines a rational incidence matrix `E_Q`. The finite
threshold checks link those exact coordinates to degree-minus-adjacency
entries in `L_Q`, and the incidence check proves `L_Q=E_Q^T E_Q`.

Let `P_Q` have diagonal `8/9` and off-diagonal `-1/9`. For each literal
rational matrix `K_Q`, the module checks symmetry and

```text
L_Q K_Q = P_Q,   K_Q P_Q = K_Q,   P_Q L_Q = L_Q,
K_Q 1 = 0,      trace(K_Q) = 79/12.
```

The rational-to-real map transports multiplication and transpose.
The generic Gram/congruence theorem derives PSD from
`K^T L K = K`: a congruence of the PSD Gram matrix is PSD. Define
`D=(108/79)K=9K/trace(K)`. The real proofs establish PSD, trace nine and
`D 1=0`. For any centered joint Gaussian with PSD covariance and a
null direction `D u=0`, the general support lemma uses genuine finite
second moments, zero variance and zero mean to prove `<u,Y>=0` almost
everywhere. Instantiation gives `sum_i Y_i=0` almost surely for both
concrete covariances, without assuming coordinate independence.

The forty-nine declarations are organized as follows:

| Group | Count and role |
| --- | --- |
| `GraphCommon` | Three: `inverse_gram_certificate_psd`, `centered_gaussian_kernel_direction_ae_zero`, and `inner_comOnes_eq_sum`. |
| Rational-to-real transport | Three: `liftMatrix_mul`, `liftMatrix_transpose`, `lift_projector`. |
| Each of classes A and B | Twenty-one each: eight rational threshold/Gram/symmetry/centered-inverse/zero-COM/trace identities and thirteen real Gram/inverse/PSD/normalization/trace/zero-COM/Gaussian-support consequences. |
| Sign boundary | One: `negative_covarianceA_not_psd`, proving that the negative of the nonzero covariance is not PSD. |

The concrete rational checks use ordinary `decide +kernel`, not
`native_decide` or an external numerical oracle. The generic proofs and
casts use the same pinned mathlib as the other analytic modules.
The supporting definitions are literal matrices, coordinates, adjacency,
real lifts, covariances and the COM vector/projector; they are not
additional theorem declarations.

These statements formally provide concrete PSD covariances with the
normalization used by this nine-point model. They establish the stated
centered inverse identities, not an equality to a named library
Moore-Penrose pseudoinverse. They also do not prove a generic theorem for
all connected graphs, exact full support on the COM subspace, homometry,
the Gaussian/Gibbs/OU preparation mechanism or empirical covariance adequacy.

The PSD lemmas can be substituted into the generic physical-moment and
histogram formulas. This revision does not include that combined
instantiation as an additional named theorem or identify its finite
charges with the executable histogram and complete polynomial tables.
Those remaining links must be reviewed and proved separately.

## What remains unformalized

The following parts of the complete certificate argument are not
formalized by this project:

- Identification of the modeled graph observable with the generic finite
  intensity, and the required same-space couplings.
- Physical justification of joint Gaussian motion and stationary OU
  dynamics, including finite exposure, signed kernel derivatives and
  their integral remainders. The two literal covariance/COM results
  and generic motion-strength substitution are now included above.
- A combined concrete-graph moment instantiation, and the connection
  from the mathematical charge histogram to executable convolution,
  variogram tables and complete polynomial grouping.
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
first-intensity identity with explicit full covariance and integrability;
nine further declarations extend it to every natural raw moment. The new
physical, histogram and literal covariance modules supply additional
links without proving the remaining executable identification or full
scientific theorem. Physical calibration, model adequacy, novelty and
human peer review remain outside all nine files.
