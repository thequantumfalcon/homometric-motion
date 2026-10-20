# Statement, proof route and application limits

The variables `X,Y : Ω -> Real` share a measure `μ` with an explicit `IsProbabilityMeasure μ` assumption. The `L2` theorem requires `MemLp X 2 μ` and `MemLp Y 2 μ`; the `L3` versions require `MemLp X 3 μ` and `MemLp Y 3 μ`. These hypotheses include the relevant measurability and finite-moment conditions.

Mathlib's real-valued variance is a total definition even outside the finite-variance domain. The explicit `MemLp` assumptions ensure that the quantities in these theorems are genuine finite moments. No proof relies on an infinite moment being converted to a finite default.

The proof:

1. Identifies the squared `L2` norm with the second raw moment.
2. Identifies standard deviation with the centered `L2` norm.
3. Proves centering contraction from `Var(X) <= E[X^2]`.
4. Applies the reverse norm triangle inequality and linearity of expectation.
5. Derives
   `max(0, sd(X)-delta)^2 <= Var(Y) <= (sd(X)+delta)^2`.
6. Uses the probability-space `L3 -> L2` comparison to obtain the same bounds from a finite `L3` perturbation budget.

For the variance enclosure, the premise is that the appropriate norm of `X-Y` is at most `delta`. This premise already implies `delta >= 0`; no extra nonnegativity premise is silently omitted.

The result allows different means. It therefore justifies the variance step after a coupled frequency, position or exposure perturbation: once the specified model provides a finite `L3` error budget, that budget bounds the standard-deviation change. It does not itself establish that error budget.

Centering contraction here is an `L2` result. The factor two used for a general centered `L3` change in the third-central-moment argument is a separate issue and is not removed by this theorem.

The following parts of a complete discovery proof remain unformalized by this project:

- The exact finite-beta observable, its measurability, and a same-space coupling of the modeled variables.
- The Gaussian covariance and stationary OU process assumptions, including finite exposure.
- The amplitude, Taylor, increment and geometry estimates supplying the `L3` error bound.
- A formal connection from graph/input certificates and outward numerical intervals to these abstract variables.
- Third-central-moment perturbation, skewness separation, factorial-cumulant cancellation, temporal concentration and the final classifier.

Physical calibration, model adequacy, novelty and human peer review are outside the scope of a kernel proof of this general analytic lemma.
