# Covariance, exposure, frequency and finite-count bounds

The construction and instantaneous moment proof are in
[geometry and motion](geometry-and-motion.md). This document derives the
additional steps used by the package's fixed parameter chain. All quantities
are dimensionless unless a physical conversion is explicitly supplied.

## Covariance uncertainty and compatible dynamics

For each class assume a centered Gaussian covariance satisfying
\[
 (1-\epsilon)D\preceq D'\preceq(1+\epsilon)D,\qquad
 \epsilon=10^{-5}.
\]
The translation vector is annihilated. This is a relative quadratic-form
bound, not an entrywise matrix error bound; \(\operatorname{tr}D'\)
need not equal \(n\). Write \(q=z^*Dz\), \(p=z^\mathsf TDz\).
On the nontranslation subspace,
\(D'-D=D^{1/2}ED^{1/2}\), \(\|E\|_{\rm op}\le\epsilon\), so
\[
 (1-\epsilon)q\le q'\le(1+\epsilon)q,\qquad
 \max(0,|p|-\epsilon q)\le |p'|\le |p|+\epsilon q.
\]
For the complex bilinear bound, diagonalize the real symmetric \(E\)
and apply \(|\sum_j\lambda_jw_j^2|\le\epsilon\sum_j|w_j|^2\)
to \(w=D^{1/2}z\).

Eigenvalue monotonicity and a coupling of Gaussian norm squares give
\[
 E(Y'^\mathsf TY')^r\le(1+\epsilon)^r E(Y^\mathsf TY)^r,\qquad
 \sum_i(D'_{ii})^{3/2}\le(1+\epsilon)^{3/2}\sum_iD_{ii}^{3/2}.
\]
Substitute these enclosures into the preceding finite-motion formulas.
Their moment polynomials have nonnegative coefficients in \(q'\) and
\(|p'|^2\). Independent interval extremes need not occur simultaneously:
enclosing a larger rectangular parameter set is conservative.
This supplies uniform variance, third-cumulant and raw-moment bounds
\([v_-,v_+]\), \([k_-,k_+]\), \(U_1,\ldots,U_6\).

A concrete family realizes this covariance uncertainty without leaving
the drift unchanged. Put \(c_G=n/\operatorname{tr}L_G^+\) and
\[
 \delta_w={\epsilon\over1+\epsilon}={1\over100001},\quad
 1-\delta_w\le w_e\le1+\delta_w,\quad D'_G=c_GL_w^+.
\]
On the center-of-mass subspace,
\((1-\delta_w)L\preceq L_w\preceq(1+\delta_w)L\).
Inverting gives the required covariance family because
\[
 {1\over1-\delta_w}=1+\epsilon,\qquad
 {1\over1+\delta_w}={1+\epsilon\over1+2\epsilon}\ge1-\epsilon.
\]
The stationary process
\[
 dY_s=-L_wY_s\,ds+\sqrt{2c_G}\,P\,dW_s,\qquad
 P=I-\mathbf1\mathbf1^\mathsf T/n
\]
has covariance \(D'_G\), since \(L_wD'_G=c_GP\).
In particular,
\[
 \operatorname{tr}D'_G\le T_D=n(1+\epsilon),\qquad
 E\|Y_s-Y_0\|^2
 =2\operatorname{tr}\{D'_G(I-e^{-sL_w})\}
 \le a_Gs,\quad a_G=2c_G(n-1).
\]
The weights and model parameters are fixed during acquisition.
The physical overdamped interpretation uses \(s=\kappa t/\zeta\).
Actual mean per-node displacement variance is
\(\beta\operatorname{tr}D'_G/n\); beta is a nominal scale.

## Finite exposure

For \(\bar J_{\omega,u}=u^{-1}\int_0^u J_\omega(Y_s)\,ds\),
use the exact null and \(|e^{it}-e^{iv}|\le|t-v|\) to obtain
\[
 |J_\omega(y)-J_\omega(x)|
 \le\omega^2 n(\|y\|+\|x\|)\|y-x\|.
\]
A centered Gaussian vector of covariance trace \(T\) obeys
\(\|\|V\|\|_6\le15^{1/6}\sqrt T\), by Minkowski applied to its
norm square in a covariance eigenbasis. Hölder and integration of
\(\sqrt s\) therefore yield
\[
 \|\bar J_{\omega,u}-J_\omega(Y_0)\|_3
 \le d_u={4\over3}\omega^2n15^{1/3}\sqrt{T_Da_Gu}.
\]
Stationarity makes this difference have mean zero. Unlike a general
perturbation, it incurs no extra centering factor.

For a nonnegative baseline variable with raw moments bounded by \(U_r\),
\[
 \|J-EJ\|_3\le M:=
 \min\{2U_3^{1/3},[v_+(U_4+6U_1^2U_2)]^{1/6}\}.
\]
Indeed \(E(J-EJ)^4\le U_4+6U_1^2U_2\): the omitted terms
\(-4(EJ)EJ^3-3(EJ)^4\) are nonpositive. Cauchy-Schwarz
interpolates the second and fourth centered moments.
Consequently the exposure bounds are
\[
 \begin{aligned}
 \operatorname{Var}\bar J_{\omega,u}
 &\in[\max(0,\sqrt{v_-}-d_u)^2,\ v_+],\\
 \kappa_3(\bar J_{\omega,u})
 &\in[k_--E_u,k_++E_u],\\
 E_u&=3M^2d_u+3Md_u^2+d_u^3.
 \end{aligned}
\]
The variance upper cap and \(E\bar J_{\omega,u}^r\le U_r\)
follow from Jensen and stationarity. The package uses
\(0<u\le10^{-20}\). Gaussian stationarity alone would not imply
ergodicity; the later temporal bound specifically uses the weighted OU law.

## Frequency uncertainty with a positive strength floor

Hold the real mean positions fixed and change both frequency-dependent
phases:
\[
 A_t(y)=\sum_i e^{it(x_i+\sqrt\beta y_i)},\qquad
 J_t(y)=|A_t(y)|^2/\beta.
\]
Restrict \(B/2\le\beta\le B\) and \(|t-\omega|\le d=10^{-14}\).
All mean positions have \(|x_i|<94\), so
\(M_x=\sum_i|x_i|\le63\cdot94\). Define
\[
 H_r=((2r-1)!!)^{1/(2r)}\sqrt{T_D},\quad
 Q_r=d\left({M_x\over\sqrt{B/2}}+\sqrt n H_r\right).
\]
The amplitude difference has \(L^{2r}\) norm at most \(Q_r\)
after division by \(\sqrt\beta\). For the intensity difference put
\[
 P_6=\min\{\omega\sqrt nH_3,U_3^{1/6}\},\qquad
 d_f=2P_6Q_3+Q_3^2.
\]
Here \(U_r\) are the instantaneous covariance-robust bounds; the exposure
step retains the same values by Jensen. Hölder applied to
\(\big||a+b|^2-|a|^2\big|\le2|a||b|+|b|^2\) gives
\(\|J_t-J_\omega\|_3\le d_f\), and Minkowski gives the same
bound after exposure averaging.

The frequency change can change the mean. For the baseline exposure
variance \([v_-,v_+]\), use \(L^2\) centering contraction:
\[
 \operatorname{Var}\bar J_{t,u}\in
 [\max(0,\sqrt{v_-}-d_f)^2,\;(\sqrt{v_+}+d_f)^2].
\]
In \(L^3\), the centered error is at most \(e=2d_f\). With \(M\)
computed from the baseline exposure bounds,
\[
 |\kappa_3(\bar J_{t,u})-\kappa_3(\bar J_{\omega,u})|
 \le3M^2e+3Me^2+e^3.
\]
The code checks positive variance lower endpoints and performs signed
interval division. The raw moment bounds become
\[
 E\bar J_{t,u}^r\le
 [U_r^{1/(2r)}+Q_r]^{2r},\qquad 1\le r\le6.
\]
Both classes may have independently fixed admissible parameters.
A common physical covariance scale \(\alpha=c_G\beta_G\) is possible
on the nonempty interval
\[
 (B/2)\max_Gc_G\le\alpha\le B\min_Gc_G.
\]
The exact nominal traces verify this inclusion. The positive floor is
essential to this bound; it is not robustness over arbitrarily small beta.

## Mixed-Poisson invariant and dependent-window estimation

Conditional on the complete latent trajectory, counts in disjoint
windows are independent with
\[
 K_k\mid Y\sim\operatorname{Poisson}(h\bar J_{t,u,k}+b),\qquad
 h\in[0.9,1.1],\quad b\in[0,1].
\]
Gain and background are fixed, unknown, and may differ between classes.
They are integrated quantities. At fixed photon rates, shrinking the
physical exposure also shrinks them; keeping this gain band at tiny
exposure may require enormous rates.

The factorial-cumulant generating function gives, for \(j\ge2\),
\(\kappa_j^{(F)}(K)=h^j\kappa_j(\bar J)\).
Thus the standardized ratio equals latent skewness and cancels fixed
positive gain and fixed Poisson background. This does not apply to
arbitrary random or drifting backgrounds.

Let \(d_0=1000\) be the minimum dimensionless window-start lag and
\(u_{\max}=10^{-20}\). The OU spectral contraction rate is at least
\[
 \gamma={1-\delta_w\over\max_G\operatorname{tr}L_G^+},
\]
because \(\lambda_2(L)\ge1/\operatorname{tr}L^+\).
For centered observables of windows separated by \(kd_0-u\),
conditional expectation onto the bordering states and the Markov
property give covariance at most
\(e^{-\gamma(kd_0-u)}\) times their variance. Conditional shot
residuals contribute no cross-window covariance. Since
\(kd_0-u\ge k(d_0-u_{\max})\), geometric summation gives the
conservative variance inflation
\[
 H\le1+{2\over e^{\gamma(d_0-u_{\max})}-1}
 \le1+{2\over\gamma(d_0-u_{\max})}.
\]
This bounds dependence; it does not declare finite-lag windows independent.

Write \(f_j=E(K)_j\), with \((K)_j\) the falling factorial, and let
\(\widehat f_j\) be its sample mean. If \(V_r\) are the detuned raw
moment bounds and \(V_0=1\), then
\[
 f_j\le F_j=\sum_{r=0}^j\binom jr(1.1)^r1^{j-r}V_r.
\]
The elementary falling-factorial product identities give second-moment
bounds
\[
 S_{11}=F_2+F_1,\quad S_{22}=F_4+4F_3+2F_2,\quad
 S_{33}=F_6+9F_5+18F_4+6F_3.
\]
Thus \(\operatorname{Var}\widehat f_j\le HS_{jj}/N\).

Set \(a=f_2-f_1^2\), \(c=f_3-3f_1f_2+2f_1^3\) and
\(a_{\min}=0.9^2\min_G v_{G,-}>0\).
If all three raw-mean errors are at most \(\tau\le1\), elementary
polynomial expansion gives
\[
 |\widehat a-a|\le L_2\tau,\quad
 |\widehat c-c|\le L_3\tau,\quad
 L_2=2+2F_1,\quad L_3=6+9F_1+3F_2+6F_1^2.
\]
Choose \(\eta=10^{-5}\) and
\[
 \tau=\min\{1,\eta a_{\min}/L_2,\;
          \eta a_{\min}\sqrt{a_{\min}}_{\rm lower}/L_3\},
\]
using an exact lower square-root enclosure. For each latent skewness
interval \([r_-,r_+]\), the estimated ratio then lies in
\[
 \left[{r_--\eta\over(1+\eta)^{3/2}},
       {r_++\eta\over(1-\eta)^{3/2}}\right].
\]
The computed expanded intervals remain positive and disjoint.
Use the midpoint of A's upper endpoint and B's lower endpoint as threshold.
The implementation compares \(\widehat c^2\) with
threshold squared times \(\widehat a^3\), using class A as fallback
when \(\widehat a\le0\) or \(\widehat c<0\).
On the good raw-mean event, the fallback cannot invalidate the guarantee.
Neither estimated cumulants nor their ratio are claimed to be unbiased.

Chebyshev and the union bound imply per-class risk at most
\[
 {H(S_{11}+S_{22}+S_{33})\over N\tau^2}.
\]
The executable chooses the exact ceiling
\[
 N=\left\lceil {20H(S_{11}+S_{22}+S_{33})\over\tau^2}\right\rceil
   =975281623024726766278.
\]
The result is a sufficient 5%-risk existence bound for this fixed model
family. It is not a lower bound, a practical acquisition cost, or a
zero-error theorem. The package recomputes this detuned result from its
moment bounds; it does not transfer a count from an exact-null calculation.
