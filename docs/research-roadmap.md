# Research roadmap and evidence requirements

These are open research directions, not achieved applications or predictions
of a breakthrough. Current results include the conditional photon-count
certificate for an explicit 63-point pair and a separate exact nine-point
moment construction described in the [claim ledger](claims.md) and
[proofs](proofs/README.md). They do not establish a general reconstruction
algorithm, physical feasibility, optimal sample complexity or scientific priority.

## Current quantitative starting point

The original `verify` bounds are about 9.75 × 10²⁰ observation windows.
The newer [explicit profiles](proofs/profiled-counts.md) give sufficient
counts from 5,362,340,030,851 to 69,803,163,290,068 across their four
selected contracts. A separately evaluated position domain at exposure
cap 0.001 gives 4,404,373,875,964 windows. These remain enormous.

Each count has its own stated exposure, calibration and classifier contract.
In particular, the geometry scenarios have different frequency tolerances
and are not nested. Counts cannot be compared as a controlled experiment
in which only geometry uncertainty changes. They are sufficient upper
bounds for at most 5% error in each class, not measured performance or
lower bounds on what any method must require.

## 1. Motion-informed imaging and crystallography

A useful question is whether a calibrated motion model supplies information
that resolves a specified clean-homometric ambiguity in a real scattering
experiment. This is a possible connection to established methods.
X-ray photon correlation spectroscopy (XPCS) already measures structural
fluctuations driven by thermal motion or external stimuli; see the
[Advanced Photon Source XPCS beamline description](https://www.aps.anl.gov/Beamlines/Beamline-Directory/243).
Ravy's
[Homometry in the light of coherent beams](https://arxiv.org/abs/1303.3792)
also studies homometry, coherent diffraction and higher-order speckle statistics.

The next contribution would need to specify which additional information
our motion model provides beyond those precedents. It would need a
measurement observable, an independently calibrated covariance and time
scale, and a reconstruction or discrimination statement for that observable.
Resolving this pair does not solve the general crystallographic phase problem.

A separate [finite-motion numerical study](../studies/finite-motion/README.md)
evaluates the same pair beyond the certified strength cap. Its skewness gap
grows about fivefold near `beta = 0.1`, where bond displacements are about 10%
of a unit spacing. That study is not a certificate, and its comparison with
thermal-diffuse-scattering theory remains open.

Structural biology is a possible future setting, with no biological conclusion
established here. A connection would require new analysis for three-dimensional
geometry, heterogeneous scattering strengths, realistic interactions, sample
stability and a justified photon-dose budget.

## 2. Better statistics and usable observation budgets

The most direct quantitative target is a smaller, valid error bound for a
fully specified observation model. Candidate work includes sharper moment
enclosures, covariance-aware error allocation, likelihood-based comparisons
and sequential procedures with proved stopping-time error control.
Existing factorial-cumulant methods are part of the
[related literature](proofs/scope-and-related-work.md).

Thousands or millions of frames would be a research target, not a forecast.
Conservative concentration bounds are only one possible source of the present
cost. Weak motion, the observable's gap, photon noise, temporal dependence and
nuisance calibration also matter. Higher-order moments can carry additional
information while being difficult to estimate; higher order is not automatically
more efficient.

Compare proposed estimators under the same parameter domains and photon/time
budget. Retain exact or outward bounds where a guarantee is asserted, and
label simulation results separately. Obtain lower bounds on discrimination
error or required information, where possible, to distinguish loose analysis
from intrinsic statistical difficulty. A fixed-size synthetic study cannot
validate a tiny error claim or an astronomical-window guarantee merely by
observing no mistakes.

## 3. Detector feasibility before detector design

The current theorem specifies normalized exposures and integrated count
parameters. It does not determine a detector's required physical frame rate,
timestamp resolution or incident flux. Those require calibration of lengths,
motion amplitudes, relaxation times, efficiency, background and exposure.

Fast photon-recording technology already exists. The ESRF reports
[nanosecond-resolved XPCS using event-driven detection](https://www.esrf.fr/home/news/tech-talk/content-news/tech-talk/new-data-acquisition-scheme-allows-nanosecond-resolved-xpcs-at-id10.html),
including limitations from pixel dead time and reduced cross-correlation
contrast. This does not show that its apparatus satisfies our model.

A sensible feasibility study would compare a calibrated requirement with
existing detectors and account for dead time, afterpulsing, saturation,
timing errors, cross-talk, acquisition duration and dose. Detector speed
alone cannot validate the motion assumptions or remove a photon-budget
obstacle. Specialized hardware is a later option only if a specific,
achievable measurement requirement and an unmet hardware need are established.

## 4. Classification of motion-resolvable homometry

A broader theorem must state both its allowed dynamics and its observables.
For example, fix a common rule assigning a permanent spring graph and
stationary Gaussian dynamics to each geometry, then ask which homometric
pairs have different intensity-process laws under that rule.

The separate [phase-permutation criterion](proofs/phase-permutation.md)
gives one exact counterexample: the same nine-point pair under a common
complete-graph rule has identical nonlinear intensity-path laws at the
selected frequency and shared strength and clock. It deliberately changes
the graph from the positive threshold-`15/2` construction. Thus nonzero
relative motion alone does not guarantee discrimination; this is not an
indistinguishability claim for all dynamics or frequencies.

Several claims must remain distinct: different finite moments, different
one-time distributions, different temporal laws, and uniformly separated
observation laws across unknown nuisance parameters. Equality of a chosen
moment does not establish equality of laws. A pointwise distinction at the
same known motion strength does not establish classification when each
class may have an independently unknown strength.

A claim about indistinguishability "regardless of dynamics" needs a defined
admissible class and explicit quantifiers. Arbitrary class-dependent driving
could itself encode the class label. Useful progress would include both
additional exact examples and counterexamples, followed by sufficient or
necessary conditions under a stated common physical rule. No such general
classification theorem is supplied by the current certificate.

## Working order and gates

1. Reconstruct additional examples with alternative exact arithmetic, retain
   failed cases, and identify parameter ranges where distinctions disappear
   or reverse. Publish a new result only with its reproducible evidence.
2. Prove robustness across the actual nuisance domains needed for a classifier.
   Common-parameter pointwise results must not be promoted to independent
   nuisance-set separation. The separate [nine-point result](proofs/nine-point-moments.md)
   supplies one local independent-strength projection bound in calibrated
   intensity units; its wider bands and unmodeled detector uncertainties remain open.
3. Compare statistical procedures under matched contracts and quantify both
   sufficient budgets and any information-based limitations.
4. Extend synthetic benchmarks with calibrated failure cases and uncertainty
   reporting. The existing [virtual instrument](../prototype/README.md) is
   synthetic and does not test the final count theorem.
5. Specify a concrete physical system and test covariance, stationarity,
   calibration and conditional detector independence. Only then assess
   whether a feasible experiment tests the certified claim or a different one.

Independent reimplementations and partial proof-assistant checks can reduce
mathematical error risk. Independent human review and physical measurements
remain separate evidence requirements. This roadmap sets no completion date
or promise that practical discrimination will be achievable.
