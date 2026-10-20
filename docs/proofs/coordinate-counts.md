# Optional coordinate-tolerance count proof

The optional `coordinate-count` command freshly recomputes the complete
core and then constructs a separate exact feasible allocation for the three
raw factorial-mean errors. The original `verify` command and
`build_certificate()` retain their common-tolerance proof and output.

```sh
python -m homometric_motion coordinate-count --scenario exact_geometry --output coordinate.json
python -m homometric_motion coordinate-count --scenario position_uncertainty --output position-coordinate.json
```

The API is `build_coordinate_certificate(scenario="exact_geometry")`.
Neither computing interface accepts a saved core certificate. The output
embeds the unmodified freshly computed core and a separate `coordinate_counts`
witness, with a canonical-content hash linking the two. The source manifest
is checked by the CLI. A saved `summary` is explicitly unverified: its
consistency checks do not authenticate or recompute the saved core model.

The assumptions and existing finite-window bounds are derived in
[geometry and motion](geometry-and-motion.md),
[robustness and counts](robustness-and-counts.md), and, for that scenario,
[position uncertainty](position-uncertainty.md). This extension changes
only the proof's coordinate error allocation. It preserves the classifier,
`eta=1e-5`, temporal inflation and all physical/statistical restrictions.

## Conditional inputs from the freshly computed core

For each scenario the core motion certificate supplies positive and
disjoint intervals for standardized third cumulants of the integrated
intensity `J`, raw moment upper bounds through order six, and a positive
variance lower bound. Counts satisfy the existing stationary weighted-OU
window model and, conditionally on the full trajectory, independent Poisson
observations with means `h J+b`, fixed `h in [0.9,1.1]` and `b in [0,1]`.
The gain/background and admissible motion settings can differ between
classes but are fixed during acquisition.

Let `fj=E(K)_j`, `a=f2-f1^2`, and
`c=f3-3 f1 f2+2 f1^3`. Mixed-Poisson factorial cumulants give
`a=h^2 Var(J)>0` and `c=h^3 kappa3(J)`. Hence
`c/a^(3/2)` equals latent skewness. All original restrictions, including
the positive strength floor, frequency/position tolerances, finite
exposure, stationary preparation and weighted-spring dynamics remain.

Let `Fj` be the core upper bounds for `fj`, and define

```math
 S_{jj}=\sum_{r=0}^j {j\choose r}^2r!F_{2j-r},\qquad j=1,2,3.
```

The core dependent-window proof bounds each empirical mean by
`Var(fhat_j)<=H Sjj/N`. This follows from stationary window covariance
contraction and conditional shot-noise independence; no finite-lag
independence is assumed. The core `H` is reused exactly.

## Complete coordinate perturbation inequalities

Write `ej=fhat_j-fj` and suppose `|ej|<=tj`, where all `tj>0`.
Since `0<=fj<=Fj`,

```math
 |\widehat a-a|\le
 B_2(t)=t_2+2F_1t_1+t_1^2.
```

Expanding the cubic polynomial gives

```math
 \widehat c-c
 =e_3-3f_1e_2-3f_2e_1-3e_1e_2
   +6f_1^2e_1+6f_1e_1^2+2e_1^3,
```

and therefore

```math
 |\widehat c-c|\le B_3(t)
 =t_3+3F_1t_2+(3F_2+6F_1^2)t_1
   +3t_1t_2+6F_1t_1^2+2t_1^3.
```

No unbiasedness of the cumulant or ratio estimators is used. Cross terms
are retained explicitly. The inequalities hold for any positive tolerances;
the former common constraint `tau<=1` is unnecessary here.

Let `a_-=0.9^2 min_G v_{G,-}>0`, and let
`q_-<=sqrt(a_-)` be the same exact rational lower enclosure used by the
core scenario. Choose tolerances satisfying

```math
 B_2(t)\le\eta a_-,\qquad
 B_3(t)\le\eta a_-q_-.
```

For every admissible law, `a>=a_-`, so these imply
`|ahat-a|<=eta a` and `|chat-c|<=eta a^(3/2)`.
In particular `ahat>0`, because `eta<1`. If the true skewness lies in
`[r_-,r_+]` with `r_->eta`, then `chat>0` and

```math
 {\widehat c\over\widehat a^{3/2}}
 \in\left[
 {r_- -\eta\over(1+\eta)^{3/2}},
 {r_+ +\eta\over(1-\eta)^{3/2}}
 \right].
```

The core outward intervals enclose these endpoints and are disjoint.
The core midpoint threshold therefore classifies correctly on the
simultaneous good event. Its implementation compares `chat^2` against
`threshold^2 ahat^3`, with class A fallback when `ahat<=0` or `chat<0`.
The fallback cannot occur on the good event.

## Finite-window risk

Chebyshev on each empirical raw mean and a union bound give, under either
class and uniformly over its fixed admissible nuisance parameters,

```math
 P(\text{misclassification})\le
 {H\over N}\sum_{j=1}^3 {S_{jj}\over t_j^2}.
```

No equal split of the 5% target is assumed. The exact risks assigned to
the three events are retained separately, and their sum is bounded.
Consequently

```math
 N=\left\lceil 20H\sum_{j=1}^3{S_{jj}\over t_j^2}\right\rceil
```

is sufficient for a maximum individual-class error of at most 5%.
This is a finite-`N` bound, not an asymptotic normal approximation.

## Deterministic feasible construction

The positive linear sensitivities in `B3` are

```math
 \ell=(3F_2+6F_1^2,\;3F_1,\;1).
```

For the linear relaxation of minimizing `sum Sjj/tj^2` subject to
`sum lj tj<=C`, the Lagrange equations give
`tj` proportional to `(Sjj/lj)^(1/3)`. This observation selects a
direction only; it does not establish optimality for the actual problem.

For each coordinate, choose the exact 24-place lower cube-root enclosure
`dj` of `Sjj/lj`, and verify that it is positive. Set `tj=s dj`.
Both `B2(s d)` and `B3(s d)` are strictly increasing polynomials for
`s>=0`, with nonnegative coefficients. Define

```math
 s_{\rm hi}=\min\left\{
 {\eta a_-\over d_2+2F_1d_1},
 {\eta a_-q_-\over\sum_j\ell_jd_j}
 \right\}.
```

At least one linear part reaches its budget at this positive endpoint;
its positive higher-degree part makes the full endpoint infeasible.
Zero is feasible. Perform 128 exact rational bisections, retaining a
feasible lower endpoint and an infeasible upper endpoint. The final
positive lower endpoint gives rational tolerances that satisfy both full
constraints. The executable verifies these facts, the final bracket,
the risk sum, and the exact ceiling.

The algorithm was chosen with knowledge of previous diagnostics.
No blind selection, global optimum, necessary count, or practical
acquisition recommendation is claimed. The common-tolerance count remains valid and available; the optional
command adds a separate sufficient certificate.
