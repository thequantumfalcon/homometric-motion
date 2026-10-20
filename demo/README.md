# Offline discovery explorer

Double-click `index.html` in a current browser. Keep `style.css`, `app.js`,
`data.js` and `data.json` beside it. The page uses local
scripts without a server, network request, external font or framework.

The clean diffraction plot and phase diagram are floating-point illustrations
of the exact geometry in the proof. The frequency slider does not recompute
or extend the separate certified motion bound. The bound panel displays
exact rational data from the released `exact_geometry` certificate, with approximate
decimal labels. No stochastic simulation or measured data is presented.

This explorer shows the `exact_geometry` certificate, with exact mean geometry
and frequency error at most 10^-14. Other package scenarios are outside this demonstration.
It retains the original common-tolerance count. The optional
`coordinate-count` command proves a smaller sufficient count under the same
assumptions; it does not change the displayed population intervals.
The sufficient count, model assumptions, positive strength floor and limits
are displayed with the plots.

To regenerate display data after producing a fresh installed-package certificate:

```sh
python tools/build_demo.py --certificate certificate.json
python tools/build_demo.py --certificate certificate.json --check
```

The generator verifies that the saved certificate binds the current package
source manifest. It creates deterministic `data.json` and `data.js` without
timestamps or machine paths. It does not replace the installed certificate
computation. The manifest and certificate hashes identify the inputs; they do
not authenticate an untrusted distributor.

For browser interaction checks, open `index.html#check` and inspect the hidden
`demo-check-results` element, or call `HomometricDemo.runChecks()` in the browser
console. These checks cover the rendered geometry, numerical clean-intensity
agreement, bound separation, controls and sweep pause. They verify the display,
not the mathematical theorem.
