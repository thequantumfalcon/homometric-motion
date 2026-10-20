# Model and limitations

For a connected weighted graph, omit the translational mode and let `lambda_j` be its positive Laplacian eigenvalues. Keep nominal scaling `c=63/tr(L_nominal^+)`. The Gaussian mode variance is `c/lambda_j`; the exact stationary OU transition across dimensionless lag `u` is

```text
a_j(t+u) = exp(-lambda_j*u)*a_j(t)
         + sqrt[(c/lambda_j)*(1-exp(-2*lambda_j*u))]*Z_j.
```

Independent standard Gaussian draws are scaled to obtain the stationary initial modes and transition innovations. This avoids Euler discretization for this linear process. Eigensystems and observable evaluations use ordinary floating arithmetic, not outward intervals. The same-covariance Rademacher case deliberately changes the distribution.

The nominal algebraic phase vector satisfies `sum z_i=0`. The finite-beta intensity is evaluated by

```text
J = |sum z_i*expm1(i*omega*sqrt(beta)*Y_i)|^2 / beta,
omega = pi/3.
```

This is equivalent to the exact-null exponential expression and reduces cancellation. Direct exponential sums and leading quadratic intensities provide numerical controls. Gaussian finite means use the pair characteristic-function formula; this Gaussian reference is not labelled as the true mean of the non-Gaussian control.

A common nominal gain gives pooled leading signal mean 10 and background 1. Drift and correlated-channel cases alter the actual conditional rate while diagnostics retain fixed reference calibration. Counts remain conditionally Poisson given the full generating state. Thus a reference-calibration diagnostic can fail while the truth-rate Poisson diagnostic remains near its nominal value; knowledge of that truth is available only because this is synthetic data.

The prototype uses instantaneous snapshots and one generated trajectory per cell. Short-lag dependence can make empirical covariance/kurtosis deviate substantially even for the correct stationary Gaussian law. Descriptive flags do not have calibrated coverage and do not identify a unique physical cause. There is no classification-performance or physical-validation claim.

## Hardware distinction

A passive RC network does not automatically realize covariance proportional to `L^+`. With identical node capacitance `C`, conductance scale `G` and projected Johnson noise, an idealized voltage equation is

```text
dV = -(G/C)*L*V dt + sqrt(2*k_B*T*G)/C * B dW,   B*B^T=L.
```

Its stationary Lyapunov equation gives covariance `(k_B*T/C)*P` on the COM-zero subspace, where `P = I - 11^T/63` projects onto that subspace and removes the uniform mode. Capacitor energy is proportional to the squared node voltages, so the covariance is proportional to identity on that subspace.

To synthesize `c*L^+` with the same drift, forcing covariance must instead be `Q=2*(G/C)*c*P`, for example through calibrated projected isotropic node-current injection. A mechanical spring network coupled to a suitable bath has a different energy/fluctuation-dissipation relation. Both candidates require measurement and experimental design; neither has been assembled or validated here.

Noisy-circuit experiments demonstrate that controlled stochastic electronic systems are possible and that noise correlation/feedback details matter. They do not validate this 63-node model or readout. [Pesce et al., Nature Communications 4, 2733 (2013)](https://www.nature.com/articles/ncomms3733)

An experimentalist must establish the actual covariance, timing, phase/coordinate calibration, noise injection, stationarity and detector response before proposing a physical discrimination study. CPU speed or a successful simulation does not establish these facts.
