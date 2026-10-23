# Offline discovery explorer

Open `index.html` in a current browser. Keep `style.css`, `app.js`,
`data.js` and `data.json` beside it. The explorer works directly from disk,
without a server, network request, external font or framework.

The presentation follows the result in three steps: two distinct configurations
have the same clean diffraction intensity; their permanent spring graphs differ;
under the stated motion and observation model, their certified statistical
intervals separate. The sufficient count and assumptions are displayed together.

## What the graphics mean

The clean diffraction curves and phase diagram are floating-point illustrations
of the exact geometry in the proof. The frequency control explores clean
diffraction. It does not recompute or extend the certificate, whose fixed
frequency error is at most 10^-14 from pi/3.

The motion illustration draws seeded pseudorandom nominal Gaussian snapshots
using floating-point arithmetic. It uses unit spring weights and the upper
certified motion strength B; displayed displacements are magnified 300,000 times by default. The visual
scale is adjustable without changing the sampled displacement.
It illustrates the one-time covariance, not an OU time trajectory, an exposure,
photon counts or experimental motion. Connections remain fixed when a new
snapshot is drawn. At nominal covariance, the model's site-averaged RMS
displacement is only about 2.64 to 3.74 millionths of a coordinate unit over the
certified strength band. Individual Gaussian displacements are unbounded.

The interval panel displays stored exact rational bounds with approximate
decimal labels. It is separate from the snapshot illustration. Its population
bounds and estimator allowances come from the selected certificate; the browser
does not derive a new risk guarantee from a snapshot or floating-point plot.

## Two explicit certificate views

Both views use `exact_geometry`. Each view keeps its own exposure domain,
population intervals, estimator allowances, threshold and sufficient count.

| View | Normalized exposure cap | Sufficient observation windows |
| --- | ---: | ---: |
| `long-exposure-v1` | 0.001 | 36,938,105,282,195 |
| Original `verify` | 10^-20 | 975,281,623,024,726,766,278 |

The long profile is the initial display because it is the result featured in
the repository introduction. This is a presentation choice, not an automatic
search for a best profile. The original common-tolerance result remains
selectable, as recorded in the [demo decision](../docs/decisions/0005-offline-explorer-profiles.md).

Each count is sufficient to bound the specified classifier's error by 5% in
either class, conditional on its complete model. It is not a necessary count,
an optimum, a physical acquisition budget or evidence of practical feasibility.
The exact-geometry exposure cap 0.01 remains unresolved. Position-uncertainty
scenarios, other count methods, the nine-point construction and the separate
calibrated-iid count bounds are outside this explorer. In particular, the iid
bounds do not apply to the displayed dependent OU observation windows.

The [proofs](../docs/proofs/README.md), [claim ledger](../docs/claims.md) and
[research provenance](../review/PROVENANCE.md) state the scientific scope and
verification limits. There is no experimental dataset or claim of novelty,
independent human peer review or a fully formalized theorem.

## Reproduce the displayed data

Install the package in an isolated environment, then produce both records using
fresh output paths:

```sh
python -I -m homometric_motion verify --output certificate.json
python -I -m homometric_motion count --profile long-exposure-v1 --scenario exact_geometry --output long.json
python tools/build_demo.py --certificate certificate.json --profile-certificate long.json
python tools/build_demo.py --certificate certificate.json --profile-certificate long.json --check
```

The generator checks the input records against the current package source
manifest and requires the two named methods and scenario. It creates
deterministic `data.json` and `data.js` without timestamps or machine paths.
`SOURCE_MANIFEST.json` binds those data and the four remaining demo assets
(HTML, CSS, application JavaScript and this guide) to a display-source revision.
The package certificate retains its separate mathematical source manifest.
It does not replace the installed certificate computation. Manifest and
certificate hashes identify the inputs; they do not authenticate an untrusted
distributor.

`python tools/project.py release` recomputes the installed-package certificates
in clean directories and checks that the committed demo data match both fresh
records. These exact-arithmetic and artifact checks are separate from browser
and visual checks.

For built-in numerical display checks, open `index.html#check` and inspect the
hidden `demo-check-results` element, or call `HomometricDemo.runChecks()` in the
browser console. These checks cover the geometry, numerical clean-intensity
agreement, interval separation and the nominal snapshot covariance. They check the display,
not the mathematical theorem.

For the optional automated browser audit, use a separate developer environment
with Playwright and its Chromium browser installed:

```sh
python tools/project.py demo-browser
```

The task opens the local page at desktop, tablet and two phone widths, exercises
controls and checks offline loading. It writes screenshots and a `report.json`
under `.build/demo-audit/current/`, recording browser/tool versions, source
hashes and assertions. Screenshots still need a separate visual inspection;
passing DOM checks alone does not establish a readable or usable presentation.
These optional tools are not package or certificate dependencies.

To request all three browser engines, with those engines installed:

```sh
python tools/check_demo_browser.py --browsers chromium,firefox,webkit --output-dir .build/demo-audit/cross-browser
```

Requested missing engines fail the audit unless explicitly allowed by
`--allow-missing-browsers`; a skipped engine is not evidence that it passed.

## Nominal snapshot construction

Each nominal graph is a 63-node path with one additional edge connecting nodes
two path steps apart. Write `v` for the 62-entry vector with ones on those two
steps and zeros elsewhere. For independent standard normal increments `z`,
the transformation

```text
T = I - (1 - 1/sqrt(3)) vv^T / 2
T T^T = I - vv^T / 3 = (I + vv^T)^-1
```

gives the increment covariance for the path-plus-chord energy. Integrating
those increments and subtracting the 63-node mean yields covariance `L+`, the
graph Laplacian pseudoinverse on the zero-center-of-mass subspace. Its exact
trace is `121486/189` for A and `121570/189` for B. Scaling by
`sqrt(B * 63 / trace(L+))` gives the nominal displacement covariance `B C0`.
The factor 300,000 changes only the rendered displacement.

The browser evaluates this construction using seeded pseudorandom numbers and
floating-point operations. Those illustrative draws are not exact Gaussian
arithmetic or an additional certificate. The finite-count result comes from
the separately reproduced rational bounds.
