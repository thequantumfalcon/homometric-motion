# Questions about the certificates

## Which command should I use?

Choose the contract you want to reproduce. `verify`, `coordinate-count`
and `exposure-count` preserve the earlier certificates. The additive
`count` command requires an explicit profile:

| Profile | Exact-geometry exposure cap | Position-uncertainty exposure cap |
| --- | ---: | ---: |
| `short-exposure-v1` | `1e-5` | `1e-5` |
| `long-exposure-v1` | `0.001` | `0.01` |

Both new profiles use a fresh cancellation-aware estimator allocation.
The short profile retains linear exposure-moment bounds; the long
profile propagates signed kernel bounds over all 512 exposure cells.
Neither is silently selected as a best method. See the
[full parameter contracts](proofs/profiled-counts.md).

## Do smaller sufficient counts prove that an experiment is practical?

No. These are conservative upper bounds on the observations sufficient
for one classifier under a fixed conditional model. They are neither
necessary counts nor measured performance. Exposure and spacing are
dimensionless; translating them to seconds also needs a common physical
time scale, detector rates and calibration. An integrated gain range does
not imply that a fixed photon flux achieves it at every exposure duration.

## Why can the longer profile require more observations?

A wider exposure domain must cover more possible latent laws. For
position uncertainty, the selected long cap is `0.01`; an extra evaluated
cap of `0.001` has a smaller sufficient count but a stricter exposure
contract. The profile name identifies its domain, not a monotone ranking
of count efficiency.

The two geometry scenarios also have different calibration requirements:
the position-uncertainty scenario permits offsets only with a frequency
cap 100 times tighter. A comparison between their counts does not show
that adding position error improves discrimination.

## What does the 5% bound mean?

Under either class, and for every fixed allowed parameter choice, the
specified classifier has misclassification probability at most `0.05`
after its stated sufficient number of windows. This is a finite-sample
probability bound, not a percentage confidence that the proof is correct.
It does not promise zero errors or certify every possible classifier.

## Are the observation windows independent?

The latent trajectory is temporally correlated. The bound uses a
whole-window reversible-OU covariance contraction and the stipulated
start spacing. Detector draws are assumed independent conditional on
the full latent path. Neither unconditional window independence nor
independence of the three estimated factorial means is required.

## Which unknown parameters are covered?

The stated intervals allow unknown but fixed springs, strength,
frequency, exposure duration, channel settings and, in the second
scenario, mean positions. They may differ between classes but stay fixed
during an acquisition. The theorem does not cover arbitrary per-window
drift, mixtures of parameter settings, arbitrary detector noise or
unbounded calibration error.

The fixed gain and fixed Poisson background cancel from a population
factorial-cumulant ratio. They do not make its finite-sample estimator
unbiased or remove the channel assumptions used for concentration.

## Are imperfect specimens still homometric?

The two ideal configurations have equal clean Fourier intensity at every
common real frequency. Arbitrary permitted position offsets need not
preserve that identity. The position theorem bounds the changed
measurement law; it does not relabel imperfect specimens as exactly
homometric.

## Is the exact-geometry cap `0.01` impossible?

No. The current nuisance-propagated bounds are unresolved there, so
there is no certified allocation for that domain. Failure of this
particular enclosure to separate classes is not proof that the laws
coincide or that other analyses cannot distinguish them.

## What does Lean check?

The optional sources check six finite integer statements mapped to the
original `verify` position certificate, six universal factorial-product
identities, nine analytic variance declarations, four deterministic
cumulant-sensitivity statements, five explicit nine-point polynomial
statements, thirteen Gaussian phase, integrability and first-intensity
declarations, nine natural-moment, seven physical-parameter, five
charge-histogram and forty-nine concrete covariance declarations.
The analytic project has 101 proved declarations in nine files.
Generic Gaussian formulas retain full PSD covariance and singular cases;
the physical unit-phase specialization has exact mathematical charge
multiplicities. The two literal nine-point covariance matrices have
formal threshold, centered-inverse, PSD, trace and zero-COM support
proofs. Executable convolution/polynomial identification, temporal
concentration, the classifier and physical validation remain outside
these statements. See
[formal scope](proofs/formal/README.md).

## Does a saved summary verify a certificate?

It does not authenticate the supplied record. `summary` remains labelled
**UNVERIFIED** even when it rejects inconsistent parameters, digests or
witnesses. For the nine-point record it additionally reconstructs and compares
all scientific values using the installed fixed model. Earlier summaries
retain their consistency checks without recomputing the reference motion
model. None of these operations validates physical assumptions.

Run the corresponding computing command from the installed artifact to obtain
fresh output. Source hashes bind bytes but do not establish that an untrusted
source is genuine.

## Is this a claim of a new physical law or a completed experiment?

No. It is a reproducible mathematical construction with explicit model
assumptions and bounded computational evidence. Related work already
studies homometry, fluctuation statistics and factorial cumulants.
Novelty, experimental adequacy, practical advantage and independent
human peer review remain unestablished.
