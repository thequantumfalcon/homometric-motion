# Geometry and the finite-motion certificate

This is a conditional mathematical construction. The executable certificate
recomputes its graph algebra and outward interval bounds; it does not measure
an apparatus, establish novelty or constitute proof-assistant verification.
The complete observation claim additionally uses the assumptions and bounds
in [robustness and counts](robustness-and-counts.md).

The certified observation domain covers **very small motion**. In its strength
band $B/2\le\beta\le B$, the nominal equilibrium RMS displacement, averaged
over sites, is $\sqrt\beta$: about **2.64 to 3.74 millionths of the unshifted
motif's short spacing** (one coordinate unit). With the allowed covariance
uncertainty it is $\sqrt{\beta\operatorname{tr}D'/n}<4\times10^{-6}$ in the
same units. This is an RMS scale, not a bound on individual Gaussian
displacements. The result establishes conditional existence at very small
motion; the separate numerical study at larger strengths does not extend
this certified range.

## Explicit clean-homometric configurations

The spatial geometry is one-dimensional: all mean positions lie on the real
line, and each site's random displacement is a scalar along that same line.

Set $n=63$, $\omega=\pi/3$,
$\theta=\arcsin(1/(5\sqrt3))$ and
$\phi=-\arcsin(1/(8\sqrt3))$. Begin with
```math
 U_0=\{3j,3j+1:0\le j\le9\}\cup\{30\}.
```
Move each $3j+1$ by $(-1)^j\theta/\omega$. Keep $0,3,30$
fixed and move each $3j$, $2\le j\le9$, by
$(-1)^j\phi/\omega$. Call this 21-point set $U$, and define
```math
 A=U+\{0,31,63\},\qquad B=U+\{0,32,63\}.
```
These are ordinary Minkowski sums with no repeated points. If
$F_W(t)=\sum_{x\in W}e^{itx}$ and $V=\{0,31,63\}$, then the
second translation set is $63-V$. Therefore
```math
 F_A(t)=F_U(t)F_V(t),\qquad
 F_B(t)=F_U(t)e^{63it}\overline{F_V(t)}
```
and $|F_A(t)|^2=|F_B(t)|^2$ for every real $t$.
Clean homometry refers to this common-frequency identity.
This is the established convolution/reflection construction of
[Rosenblatt and Seymour (1982)](https://doi.org/10.1137/0603035),
specialized to unique point sums and a translated reflected factor.

Connect fixed mean positions at distance at most $5/2$. The inequality
$\arcsin s\le s/\sqrt{1-s^2}$ and $\omega>1$ bound the shifts
by $1/\sqrt{74}<1/8$ and $1/\sqrt{191}<1/8$.
Integer pair distances are at least $1/2$ from $5/2$, while moving
both endpoints changes a distance by less than $1/4$. Thus the shifts
preserve the graph and vertex order. The code independently enumerates
integer threshold edges: they form the ordered 63-vertex path plus chord
$(20,22)$ for A or $(41,43)$ for B. The triangle's attached path
lengths are respectively $\{20,40\}$ and $\{19,41\}$, so the graphs
are nonisomorphic. The configurations are consequently noncongruent.
These permanent graphs are not rebuilt after random displacement.

Write $\zeta=(1+i\sqrt3)/2$. The sorted unit-block phases at $\omega$
are $(-1)^j$ at $3j$, $j=0,1$;
$(-1)^j\cos\phi+i\sin\phi$ at $3j$, $j\ge2$;
$\zeta[(-1)^j\cos\theta+i\sin\theta]$ at $3j+1$; and $1$
at 30. Cosine terms cancel in even/odd pairs, leaving
```math
 \sum_{x\in U}e^{i\omega x}
   =1+8i\sin\phi+10i\zeta\sin\theta=0.
```
This is an exact algebraic cancellation: substituting
$\sin\theta=1/(5\sqrt3)$ and $\sin\phi=-1/(8\sqrt3)$
gives zero real and imaginary coefficients. Unit magnitudes follow from
$74/75+1/75=1$, $191/192+1/192=1$, and $1/4+3/4=1$.
The complete vectors are $(w,\zeta w,-w)$ and
$(w,\zeta^2w,-w)$. The program verifies exact coefficient identities
separately from interval consistency; merely enclosing zero would not
prove the required null.

## Exact graph covariance

For a unit-conductance chord $(r,r+2)$ added to a path, define for
$i\le j$
```math
 a_{ij}=\max(0,\min(j,r+2)-\max(i,r)),\qquad
 R_{ij}=j-i-a_{ij}^2/3.
```
The chord is a rank-one conductance update: its path voltage drop under
unit $i,j$ current is $a_{ij}$, and its update denominator is
$1+R_{\rm path}(r,r+2)=3$. Double centering gives
```math
 (L^+)_{ij}=(\overline R_i+\overline R_j-\overline R-R_{ij})/2.
```
The implementation verifies symmetry, zero row sums and
$LL^+=I-\mathbf1\mathbf1^\mathsf T/n$ entry by entry with exact
fractions. Connectedness then identifies the positive semidefinite
Laplacian pseudoinverse. The nominal covariance is
```math
 D=nL^+/\operatorname{tr}L^+,\qquad \operatorname{tr}D=n.
```
The pseudoinverse traces are $\operatorname{tr}L_A^+=121486/189$ and
$\operatorname{tr}L_B^+=121570/189$. The normalized covariances instead satisfy
$\operatorname{tr}D_A=\operatorname{tr}D_B=63$.

Let $Y\sim N(0,D)$, $z_i=e^{i\omega x_i}$, and
```math
 I_\beta=\left|\sum_i z_i e^{i\omega\sqrt\beta Y_i}\right|^2,\qquad
 J_\beta=I_\beta/\beta,\qquad Z=\sum_i z_iY_i.
```
The centered Gaussian may be singular in the translation direction.
For $q=E|Z|^2$, $p=EZ^2$, the leading variable
$J_0=\omega^2|Z|^2$ has
```math
 \begin{aligned}
 v_0&=\omega^4(q^2+|p|^2),\\
 k_{30}&=\omega^6(2q^3+6q|p|^2),\\
 m_{4,c}&=\omega^8(9q^4+42q^2|p|^2+9|p|^4).
 \end{aligned}
```
These follow by diagonalizing its two-dimensional real Gaussian
projection. More generally,
```math
 \kappa_r(|Z|^2)=(r-1)!
       \sum_{j=0}^{\lfloor r/2\rfloor}\binom r{2j}q^{r-2j}|p|^{2j}.
```
For $H=Y^\mathsf TY$,
$\kappa_r(H)=2^{r-1}(r-1)!\operatorname{tr}(D^r)$.
Both sets of moments follow from $m_0=1$ and
```math
 m_r=\sum_{j=1}^r\binom{r-1}{j-1}\kappa_jm_{r-j}.
```
Exact integer matrix powers through six suffice to obtain traces
through twelve because symmetric powers satisfy
$\operatorname{tr}(D^{a+b})=\sum_{ij}(D^a)_{ij}(D^b)_{ij}$.

## Global finite-strength remainder

Put $t_i=\omega\sqrt\beta Y_i$,
```math
 C=\sum_i z_i(\cos t_i-1),\quad S=\sum_i z_i\sin t_i,\quad
 S_1=\omega\sqrt\beta Z.
```
The null gives $I_\beta=E+O$, where
$E=|C|^2+|S|^2$ is even under $Y\mapsto-Y$ and
$O=2\operatorname{Re}(C\overline{iS})$ is odd.
The bounds $|\cos t-1|\le t^2/2$ and
$|\sin t-t|\le|t|^3/6$ hold on the entire real axis.
Minkowski therefore gives, for $r=4,6$,
```math
 \|S_1\|_r=s_r\sqrt\beta,\quad
 \|C\|_r\le c_r\beta,\quad
 \|S-S_1\|_r\le e_r\beta^{3/2},
```
where
```math
 \begin{aligned}
 s_4&=\omega(2q^2+|p|^2)^{1/4},&
 s_6&=\omega(6q^3+9q|p|^2)^{1/6},\\
 c_r&=(\omega^2/2)(EH^r)^{1/r},\\
 e_4&=(\omega^3/6)\,10395^{1/4}\sum_iD_{ii}^{3/2},&
 e_6&=(\omega^3/6)\,34459425^{1/6}\sum_iD_{ii}^{3/2}.
 \end{aligned}
```
The constants are the scalar Gaussian twelfth and eighteenth moments.
No truncation of Gaussian tails is made.

The bundled exact rational cap $B$, approximately
$1.3986078635588654\times10^{-11}$, is a specified input.
For all $0<\beta\le B$, set
```math
 \begin{aligned}
 e_2&=B(2s_4e_4+c_4^2)+B^2e_4^2,\\
 o_2&=4Bc_4^2(s_4+Be_4)^2.
 \end{aligned}
```
Centering is an $L^2$ contraction. Even and odd parts are orthogonal,
so forward and reverse triangle inequalities give
```math
 \max(0,\sqrt{v_0}-e_2)^2
 \le\operatorname{Var}J_\beta
 \le(\sqrt{v_0}+e_2)^2+o_2.
```

For third moments let $X=|S_1|^2-E|S_1|^2$ and
$R=(E-|S_1|^2)-E(E-|S_1|^2)$. Parity gives
```math
 \kappa_3(I_\beta)=E(X+R)^3+3E[(X+R)O^2].
```
Define
```math
 \begin{aligned}
 x_3&=(v_0m_{4,c})^{1/6},\\
 d_3&=2B(2s_6e_6+c_6^2)+2B^2e_6^2,\\
 o_3&=4Bc_6^2(s_6+Be_6)^2,\\
 E_3&=3x_3^2d_3+3x_3d_3^2+d_3^3+3(x_3+d_3)o_3.
 \end{aligned}
```
Interpolation gives $\|X\|_3/\beta\le x_3$.
The factor two in $d_3$ is essential: centering in $L^3$
is bounded by two, unlike its $L^2$ contraction. Hölder applied to
the displayed parity identity proves
```math
 |\kappa_3(J_\beta)-k_{30}|\le E_3.
```
All error coefficients are nonnegative and monotone in the cap, so the
enclosures cover the entire positive interval, independently in each class.
Strictly positive variance lower bounds justify division to enclose
$\kappa_3(J_\beta)/\operatorname{Var}(J_\beta)^{3/2}$.

The additional raw-moment bounds, for $1\le r\le6$, are
```math
 EJ_\beta^r\le\left[
 \omega(E|Z|^{2r})^{1/(2r)}
 +{\omega^2\sqrt B\over2}(EH^{2r})^{1/(2r)}
 \right]^{2r}.
```
They follow from the global first-order exponential remainder and
Minkowski for the amplitude.

## Arithmetic and what the certificate establishes

The code encloses radicals on a $10^{-72}$ integer grid with outward
rounding. Integer roots have exact bracketing checks. It encloses
$\pi=16\arctan(1/5)-4\arctan(1/239)$ using 120 terms of each
alternating series and the signed first omitted term. Fractions and
integer interval endpoints determine assertions; decimal displays do not.

The nominal skewness intervals are disjoint. Recomputing them verifies
this finite model calculation and its stated inequalities. It does not
show that an unknown apparatus obeys the Gaussian graph model. The code
and proof are a new release revision of previously examined parameters;
there is no blind-discovery or historical-freeze claim. Broader limitations
and prior work are in [scope and related work](scope-and-related-work.md).
