"use strict";

(() => {
  const data = window.HOMOMETRIC_DEMO_DATA;
  if (
    !data ||
    data.schema_version !== 1 ||
    data.scenario !== "exact_geometry" ||
    !data.profiles?.["long-exposure-v1"]
  ) {
    const message = document.createElement("p");
    message.className = "noscript";
    message.textContent =
      "The explorer data is missing or incompatible. Keep index.html, data.js, app.js and style.css together. The proof and data links remain available below.";
    message.setAttribute("role", "alert");
    document.body.appendChild(message);
    return;
  }
  const NS = "http://www.w3.org/2000/svg";
  const sides = ["A", "B"];
  const colors = { A: "#08766b", B: "#a74e24" };
  const light = { A: "#a9e3ca", B: "#ffc196" };
  const omega = Math.PI / 3,
    tau = 2 * Math.PI;
  const theta = Math.asin(1 / (5 * Math.sqrt(3)));
  const phi = -Math.asin(1 / (8 * Math.sqrt(3)));
  const positions = {};
  for (const side of sides) {
    positions[side] = data.geometry.translations[side]
      .flatMap((shift) =>
        data.geometry.motif.map(
          ([integer, a, b]) =>
            integer + shift + (a * theta) / omega + (b * phi) / omega,
        ),
      )
      .sort((a, b) => a - b);
  }
  const byId = (id) => document.getElementById(id);
  function element(parent, tag, attributes = {}, text = null) {
    const node = document.createElementNS(NS, tag);
    for (const [name, value] of Object.entries(attributes))
      node.setAttribute(name, String(value));
    if (text !== null) node.textContent = text;
    parent.appendChild(node);
    return node;
  }
  function cleanGroup(svg) {
    svg.querySelector(":scope > g")?.remove();
    return element(svg, "g");
  }
  function viewport(svg, height) {
    const width = Math.max(230, Math.round(svg.getBoundingClientRect().width));
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.style.height = `${height}px`;
    return width;
  }
  function amplitude(side, frequency) {
    let real = 0,
      imaginary = 0;
    for (const x of positions[side]) {
      real += Math.cos(frequency * x);
      imaginary += Math.sin(frequency * x);
    }
    return {
      real,
      imaginary,
      intensity: (real * real + imaginary * imaginary) / (63 * 63),
    };
  }
  const curves = Array.from({ length: 1201 }, (_, i) => {
    const frequency = (tau * i) / 1200;
    return {
      frequency,
      A: amplitude("A", frequency).intensity,
      B: amplitude("B", frequency).intensity,
    };
  });
  function graphEdges(side) {
    const result = [];
    for (let i = 0; i < 63; i++)
      for (let j = i + 1; j < 63; j++) {
        if (positions[side][j] - positions[side][i] <= 2.5) result.push([i, j]);
      }
    return result;
  }
  const edges = { A: graphEdges("A"), B: graphEdges("B") };
  let frequency = omega,
    boundMode = "latent",
    profile = "long-exposure-v1";
  let geometryView = window.innerWidth <= 760 ? "detail" : "full";
  let motionSampleIndex = 0,
    magnification = 300000;
  let displacements = { A: Array(63).fill(0), B: Array(63).fill(0) };
  const initialSeeds = { A: 0x39ac127d, B: 0x8e71ca9b };
  let seeds = { ...initialSeeds };
  let animation = null,
    lastFrame = null,
    marker = null,
    spectrumScale = null;
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  // Numerical illustration only: truncate the positive exact rational at 30
  // decimal places before conversion. No certificate assertion uses this value.
  const [betaNumerator, betaDenominator] =
    data.certificate.parameters.beta_cap_exact.split("/");
  const beta =
    Number((BigInt(betaNumerator) * 10n ** 30n) / BigInt(betaDenominator)) /
    1e30;
  const traces = { A: 121486 / 189, B: 121570 / 189 };
  function uniform(side) {
    // Mulberry32, with separate reproducible streams for the two configurations.
    seeds[side] = (seeds[side] + 0x6d2b79f5) >>> 0;
    let value = seeds[side];
    value = Math.imul(value ^ (value >>> 15), value | 1);
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61);
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296;
  }
  function gaussian(side) {
    return (
      Math.sqrt(-2 * Math.log(1 - uniform(side))) *
      Math.cos(tau * uniform(side))
    );
  }
  function nominalTransform(side, independent) {
    // The path increments have precision I + vv^T, with v supported on the
    // two increments spanned by the extra chord. T*T^T = I - vv^T/3.
    const increments = independent.slice();
    const r = data.geometry.chords_zero_based[side][0];
    const adjustment =
      ((1 - 1 / Math.sqrt(3)) / 2) * (increments[r] + increments[r + 1]);
    increments[r] -= adjustment;
    increments[r + 1] -= adjustment;
    const integrated = [0];
    for (const value of increments) integrated.push(integrated.at(-1) + value);
    const mean = integrated.reduce((sum, value) => sum + value, 0) / 63;
    const scale = Math.sqrt(63 / traces[side]);
    return integrated.map((value) => (value - mean) * scale);
  }
  function sampleMotion() {
    motionSampleIndex++;
    for (const side of sides) {
      displacements[side] = nominalTransform(
        side,
        Array.from({ length: 62 }, () => gaussian(side)),
      ).map((value) => Math.sqrt(beta) * value);
    }
    updateMotion();
  }
  function resetMotion() {
    motionSampleIndex = 0;
    seeds = { ...initialSeeds };
    displacements = { A: Array(63).fill(0), B: Array(63).fill(0) };
    updateMotion();
  }
  function updateMotion() {
    byId("motion-status").textContent = motionSampleIndex
      ? `Snapshot ${String(motionSampleIndex).padStart(2, "0")} · nominal Gaussian draw · ${magnification.toLocaleString("en-US")}× visual magnification`
      : "Mean positions · draw a snapshot to reveal the displacement.";
    byId("magnification-value").textContent =
      `${magnification.toLocaleString("en-US")}×`;
    drawGeometry();
  }
  function drawGeometry() {
    const svg = byId("geometry"),
      width = viewport(svg, 295),
      group = cleanGroup(svg);
    const detail = geometryView === "detail",
      narrow = width < 500;
    // Gaussian draws have no hard displacement cap. Fit every rendered point;
    // the full-pair view always uses one shared coordinate scale for A and B.
    const displayed = Object.fromEntries(
      sides.map((side) => [
        side,
        positions[side].map(
          (value, i) => value + magnification * displacements[side][i],
        ),
      ]),
    );
    const fullMin = Math.min(0, ...displayed.A, ...displayed.B) - 3.5;
    const fullMax = Math.max(93, ...displayed.A, ...displayed.B) + 3.5;
    for (const [side, y] of [
      ["A", 104],
      ["B", 239],
    ]) {
      const chord = data.geometry.chords_zero_based[side];
      const first = detail ? chord[0] - 4 : 0,
        last = detail ? chord[1] + 4 : 62;
      const local = displayed[side].slice(first, last + 1);
      const min = detail
        ? Math.min(positions[side][first], ...local) - 2.5
        : fullMin;
      const max = detail
        ? Math.max(positions[side][last], ...local) + 2.5
        : fullMax;
      const x = (value) => 19 + ((value - min) / (max - min)) * (width - 38);
      const current = (index) =>
        x(positions[side][index] + magnification * displacements[side][index]);
      element(
        group,
        "text",
        {
          x: 0,
          y: y - 76,
          "font-size": 15,
          "font-weight": 650,
          style: `fill:${light[side]}`,
        },
        `${side}  /  link ${chord[0]}—${chord[1]}`,
      );
      element(
        group,
        "text",
        {
          x: width,
          y: y - 76,
          "text-anchor": "end",
          "font-size": narrow ? 11 : 12,
        },
        detail
          ? "Local detail · vertex indices"
          : motionSampleIndex
            ? narrow
              ? "Displaced · mean marks"
              : "63 sites · mean marks shown"
            : "63 mean positions",
      );
      element(group, "line", {
        x1: 18,
        x2: width - 18,
        y1: y,
        y2: y,
        stroke: "#41665a",
        "stroke-width": 1,
      });
      for (let i = first; i <= last; i++) {
        const meanX = x(positions[side][i]);
        if (motionSampleIndex) {
          element(group, "line", {
            x1: meanX,
            x2: meanX,
            y1: y - 6,
            y2: y + 6,
            stroke: "#a9c5b6",
            opacity: 0.5,
          });
          element(group, "line", {
            x1: meanX,
            x2: current(i),
            y1: y + 13,
            y2: y + 13,
            stroke: light[side],
            opacity: 0.6,
            "stroke-width": 1,
          });
        }
      }
      for (const [i, j] of edges[side]) {
        if (i < first || j > last) continue;
        const extra = j !== i + 1,
          left = current(i),
          right = current(j);
        element(group, "path", {
          d: `M${left},${y} Q${(left + right) / 2},${y - (extra ? 67 : 18)} ${right},${y}`,
          fill: "none",
          stroke: extra ? light[side] : "#7a9f8d",
          "stroke-width": extra ? 2.5 : 1.1,
        });
      }
      for (let i = first; i <= last; i++) {
        const special = i >= chord[0] && i <= chord[1];
        const dot = element(group, "circle", {
          cx: current(i),
          cy: y,
          r: detail ? (special ? 5 : 3.5) : special ? 4 : narrow ? 1.8 : 2.7,
          fill: special ? light[side] : "#c9ded0",
          stroke: "#163b37",
          "stroke-width": 0.7,
        });
        element(
          dot,
          "title",
          {},
          `${side} vertex ${i}; mean position ≈ ${positions[side][i].toFixed(6)}; displacement ≈ ${displacements[side][i].toExponential(3)}`,
        );
        if (detail && (!narrow || i % 2 === chord[0] % 2))
          element(
            group,
            "text",
            {
              x: x(positions[side][i]),
              y: y + 31,
              "text-anchor": "middle",
              "font-size": 12,
            },
            String(i),
          );
      }
      if (!detail)
        for (const value of [0, 31, 63, 93])
          element(
            group,
            "text",
            {
              x: x(value),
              y: y + 31,
              "text-anchor": "middle",
              "font-size": 12,
            },
            String(value),
          );
    }
  }
  function drawSpectrum() {
    const svg = byId("spectrum"),
      width = viewport(svg, 280),
      group = cleanGroup(svg);
    const logarithmic = byId("log-scale").checked,
      bottom = 233;
    const x = (value) => 43 + (value / tau) * (width - 60);
    const y = (value) =>
      bottom -
      194 *
        (logarithmic
          ? Math.log10(1 + 1000 * Math.max(0, value)) / Math.log10(1001)
          : value);
    spectrumScale = { x, y };
    const ticks = logarithmic
      ? [0, 0.001, 0.01, 0.1, 1]
      : [0, 0.25, 0.5, 0.75, 1];
    for (const value of ticks) {
      element(group, "line", {
        x1: 43,
        x2: width - 17,
        y1: y(value),
        y2: y(value),
        stroke: "#e0e6dc",
      });
      element(
        group,
        "text",
        { x: 35, y: y(value) + 4, "text-anchor": "end", "font-size": 12 },
        String(value),
      );
    }
    for (const [value, label] of [
      [0, "0"],
      [omega, "π/3"],
      [Math.PI, "π"],
      [tau, "2π"],
    ]) {
      element(
        group,
        "text",
        { x: x(value), y: 258, "text-anchor": "middle", "font-size": 13 },
        label,
      );
    }
    element(
      group,
      "text",
      { x: 43, y: 17, "font-size": 12 },
      logarithmic
        ? "Intensity / 63² · log display"
        : "Intensity / 63² · linear display",
    );
    for (const side of sides) {
      if (!byId(`show-${side.toLowerCase()}`).checked) continue;
      const path = curves
        .map(
          (row, i) =>
            `${i ? "L" : "M"}${x(row.frequency).toFixed(3)},${y(row[side]).toFixed(3)}`,
        )
        .join(" ");
      const attributes = {
        d: path,
        fill: "none",
        stroke: colors[side],
        "stroke-width": side === "A" ? 2.8 : 1.6,
        "stroke-linejoin": "round",
        "data-curve": side,
      };
      if (side === "B") attributes["stroke-dasharray"] = "6 5";
      element(group, "path", attributes);
    }
    marker = element(group, "g");
    drawMarker();
  }
  function drawMarker() {
    if (!marker) return;
    marker.replaceChildren();
    const { x, y } = spectrumScale;
    element(marker, "line", {
      x1: x(frequency),
      x2: x(frequency),
      y1: 32,
      y2: 233,
      stroke: "#526b5d",
      "stroke-dasharray": "3 4",
    });
    for (const side of sides) {
      if (!byId(`show-${side.toLowerCase()}`).checked) continue;
      element(marker, "circle", {
        cx: x(frequency),
        cy: y(amplitude(side, frequency).intensity),
        r: side === "A" ? 5 : 2.7,
        fill: side === "A" ? "#fffefa" : colors.B,
        stroke: colors[side],
        "stroke-width": 1.5,
      });
    }
  }
  function drawPhases() {
    const group = cleanGroup(byId("phases"));
    element(group, "circle", {
      cx: 130,
      cy: 120,
      r: 88,
      fill: "none",
      stroke: "#d7dfd3",
    });
    element(group, "line", {
      x1: 30,
      x2: 230,
      y1: 120,
      y2: 120,
      stroke: "#e3e7df",
    });
    element(group, "line", {
      x1: 130,
      x2: 130,
      y1: 20,
      y2: 220,
      stroke: "#e3e7df",
    });
    for (const side of sides) {
      for (const point of positions[side]) {
        const angle = frequency * point;
        element(group, "circle", {
          cx: 130 + 88 * Math.cos(angle),
          cy: 120 - 88 * Math.sin(angle),
          r: side === "A" ? 3.8 : 2.2,
          fill: side === "A" ? colors.A : "#fffefa",
          stroke: colors[side],
          "stroke-width": 1.1,
          opacity: 0.9,
        });
      }
      const total = amplitude(side, frequency);
      element(group, "line", {
        x1: 130,
        y1: 120,
        x2: 130 + (88 * total.real) / 63,
        y2: 120 - (88 * total.imaginary) / 63,
        stroke: colors[side],
        "stroke-width": side === "A" ? 2.5 : 1.5,
        "stroke-dasharray": side === "B" ? "4 3" : "none",
      });
    }
    element(group, "circle", { cx: 130, cy: 120, r: 2.5, fill: "#536b5d" });
  }
  function setFrequency(value) {
    const requested = Number(value);
    if (!Number.isFinite(requested)) return;
    frequency = Math.min(tau, Math.max(0, requested));
    byId("frequency").value = String(frequency);
    const atNull = Math.abs(frequency - omega) < 1e-13;
    byId("frequency-value").textContent = atNull
      ? "π/3 ≈ 1.047198"
      : frequency.toFixed(6);
    byId("frequency").setAttribute(
      "aria-valuetext",
      atNull ? "pi over three, exact clean null" : frequency.toFixed(6),
    );
    for (const side of sides)
      byId(`intensity-${side.toLowerCase()}`).textContent = amplitude(
        side,
        frequency,
      ).intensity.toExponential(4);
    drawMarker();
    drawPhases();
  }
  function selected() {
    return profile === "original-verify" ? data : data.profiles[profile];
  }
  function drawBounds() {
    const certificate = selected().certificate;
    const svg = byId("bounds"),
      width = viewport(svg, 245),
      group = cleanGroup(svg);
    const low = certificate.classes.A.expanded_skewness_display[0];
    const high = certificate.classes.B.expanded_skewness_display[1];
    const padding = (high - low) * 0.07;
    const range = [low - padding, high + padding];
    const x = (value) =>
      31 + ((value - range[0]) / (range[1] - range[0])) * (width - 48);
    const tickCount = width < 420 ? 3 : 5;
    for (let i = 0; i < tickCount; i++) {
      const value = range[0] + (i / (tickCount - 1)) * (range[1] - range[0]);
      element(group, "line", {
        x1: x(value),
        x2: x(value),
        y1: 31,
        y2: 193,
        stroke: "#e0e6dc",
      });
      element(
        group,
        "text",
        {
          x: x(value),
          y: 218,
          "text-anchor":
            i === 0 ? "start" : i === tickCount - 1 ? "end" : "middle",
          "font-size": 12,
        },
        value.toFixed(4),
      );
    }
    for (const [side, y] of [
      ["A", 77],
      ["B", 158],
    ]) {
      const interval =
        certificate.classes[side][
          boundMode === "expanded"
            ? "expanded_skewness_display"
            : "skewness_display"
        ];
      element(
        group,
        "text",
        {
          x: 0,
          y: y + 5,
          style: `fill:${colors[side]}`,
          "font-size": 17,
          "font-weight": 650,
        },
        side,
      );
      element(group, "rect", {
        x: x(interval[0]),
        y: y - 17,
        width: x(interval[1]) - x(interval[0]),
        height: 34,
        rx: 3,
        fill: side === "A" ? "#d9eee6" : "#f4dfcc",
      });
      element(group, "line", {
        x1: x(interval[0]),
        x2: x(interval[1]),
        y1: y,
        y2: y,
        stroke: colors[side],
        "stroke-width": 3,
      });
      for (const value of interval)
        element(group, "line", {
          x1: x(value),
          x2: x(value),
          y1: y - 10,
          y2: y + 10,
          stroke: colors[side],
          "stroke-width": 2,
        });
      byId(`bound-${side.toLowerCase()}`).textContent =
        `≈ [${interval[0].toFixed(10)}, ${interval[1].toFixed(10)}]`;
    }
    if (boundMode === "expanded") {
      const threshold = x(certificate.threshold_display);
      element(group, "line", {
        x1: threshold,
        x2: threshold,
        y1: 28,
        y2: 193,
        stroke: "#64745b",
        "stroke-width": 1.5,
        "stroke-dasharray": "4 4",
      });
      element(
        group,
        "text",
        { x: threshold, y: 16, "text-anchor": "middle", "font-size": 11 },
        "Fixed decision threshold",
      );
    }
    byId("bound-caption").textContent =
      boundMode === "expanded"
        ? "Estimator allowance included. On the controlled moment-error event, the ranges stay on opposite sides of the selected fixed threshold. Decimal endpoints are approximate."
        : "Uniform bounds for the selected finite-exposure intensity laws. Decimal endpoints are approximate; data.json contains the exact rational endpoints.";
  }
  function selectProfile(value) {
    if (!["original-verify", "long-exposure-v1"].includes(value)) return;
    profile = value;
    byId("profile").value = profile;
    const item = selected(),
      isLong = profile === "long-exposure-v1";
    const count = item.certificate.sufficient_observation_windows;
    byId("window-count").textContent = count.replace(
      /\B(?=(\d{3})+(?!\d))/g,
      ",",
    );
    byId("count-short").textContent = isLong
      ? "≈ 36.9 trillion"
      : "≈ 9.75 × 10²⁰";
    byId("count-profile").textContent = `${profile} / exact_geometry`;
    const cap = isLong ? "0.001" : "10⁻²⁰";
    byId("exposure-cap").textContent = `≤ ${cap}`;
    byId("profile-summary").textContent =
      `Exposure ≤ ${cap} · fixed frequency tolerance 10⁻¹⁴`;
    byId("certificate-hash").textContent = item.source.certificate_sha256;
    byId("check-count").textContent = String(item.source.mathematical_checks);
    drawBounds();
  }
  function stopSweep() {
    if (animation !== null) cancelAnimationFrame(animation);
    animation = null;
    lastFrame = null;
    byId("sweep").setAttribute("aria-pressed", "false");
    byId("sweep").textContent = "Sweep frequency ▶";
  }
  function sweepFrame(time) {
    if (lastFrame !== null)
      setFrequency(
        (frequency + (Math.min(time - lastFrame, 100) * tau) / 20000) % tau,
      );
    lastFrame = time;
    animation = requestAnimationFrame(sweepFrame);
  }
  byId("frequency").addEventListener("input", (event) => {
    stopSweep();
    setFrequency(event.target.value);
  });
  for (const id of ["log-scale", "show-a", "show-b"])
    byId(id).addEventListener("change", drawSpectrum);
  byId("null-frequency").addEventListener("click", () => {
    stopSweep();
    setFrequency(omega);
  });
  byId("sweep").addEventListener("click", () => {
    if (animation !== null) {
      stopSweep();
      return;
    }
    byId("sweep").setAttribute("aria-pressed", "true");
    byId("sweep").textContent = "Pause sweep ❚❚";
    animation = requestAnimationFrame(sweepFrame);
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) stopSweep();
  });
  window.addEventListener("pagehide", stopSweep);
  reducedMotion.addEventListener("change", stopSweep);
  byId("sample-motion").addEventListener("click", sampleMotion);
  byId("reset-motion").addEventListener("click", resetMotion);
  byId("magnification").addEventListener("input", (event) => {
    magnification = Number(event.target.value);
    updateMotion();
  });
  byId("profile").addEventListener("change", (event) =>
    selectProfile(event.target.value),
  );
  for (const radio of document.querySelectorAll('input[name="bound-mode"]'))
    radio.addEventListener("change", (event) => {
      boundMode = event.target.value;
      drawBounds();
    });
  for (const radio of document.querySelectorAll('input[name="geometry-view"]'))
    radio.addEventListener("change", (event) => {
      geometryView = event.target.value;
      drawGeometry();
    });
  document.querySelector(
    `input[name="geometry-view"][value="${geometryView}"]`,
  ).checked = true;
  let resizeFrame = null;
  window.addEventListener("resize", () => {
    if (resizeFrame !== null) cancelAnimationFrame(resizeFrame);
    resizeFrame = requestAnimationFrame(() => {
      drawGeometry();
      drawSpectrum();
      drawBounds();
      resizeFrame = null;
    });
  });
  drawGeometry();
  drawSpectrum();
  selectProfile(profile);
  setFrequency(omega);

  function inspectState() {
    return {
      frequency,
      profile,
      boundMode,
      motionSampleIndex,
      magnification,
      geometryView,
      displacements: { A: displacements.A.slice(), B: displacements.B.slice() },
    };
  }
  function covarianceResidual(side) {
    // Independently construct resistance double-centering; compare every
    // covariance entry with the sampler's linear transformation columns.
    const columns = Array.from({ length: 62 }, (_, k) =>
      nominalTransform(
        side,
        Array.from({ length: 62 }, (__, j) => (j === k ? 1 : 0)),
      ),
    );
    const r = data.geometry.chords_zero_based[side][0];
    const resistance = Array.from({ length: 63 }, (_, i) =>
      Array.from({ length: 63 }, (__, j) => {
        const left = Math.min(i, j),
          right = Math.max(i, j);
        const overlap = Math.max(0, Math.min(right, r + 2) - Math.max(left, r));
        return right - left - (overlap * overlap) / 3;
      }),
    );
    const means = resistance.map(
      (row) => row.reduce((sum, value) => sum + value, 0) / 63,
    );
    const mean = means.reduce((sum, value) => sum + value, 0) / 63;
    let residual = 0,
      trace = 0;
    for (let i = 0; i < 63; i++)
      for (let j = 0; j < 63; j++) {
        const actual = columns.reduce((sum, col) => sum + col[i] * col[j], 0);
        const expected =
          (((means[i] + means[j] - mean - resistance[i][j]) / 2) * 63) /
          traces[side];
        residual = Math.max(residual, Math.abs(actual - expected));
        if (i === j) trace += actual;
      }
    return { residual, trace };
  }
  function runChecks() {
    const checks = {};
    function check(name, value) {
      checks[name] = Boolean(value);
      if (!value) throw new Error(name);
    }
    check(
      "two distinct 63-point configurations",
      sides.every(
        (side) =>
          positions[side].length === 63 && new Set(positions[side]).size === 63,
      ),
    );
    for (const side of sides) {
      const chord = data.geometry.chords_zero_based[side];
      check(
        `${side} permanent path plus declared chord`,
        edges[side].length === 63 &&
          edges[side].filter(([i, j]) => j !== i + 1).length === 1 &&
          edges[side].some(([i, j]) => i === chord[0] && j === chord[1]),
      );
    }
    const residual = Math.max(...curves.map((row) => Math.abs(row.A - row.B)));
    check("illustrative clean-intensity agreement", residual < 1e-11);
    check(
      "numeric null consistency",
      sides.every((side) => amplitude(side, omega).intensity < 1e-25),
    );
    const covariance = {};
    for (const side of sides) {
      covariance[side] = covarianceResidual(side);
      check(
        `${side} sampler matches resistance covariance`,
        covariance[side].residual < 1e-12 &&
          Math.abs(covariance[side].trace - 63) < 1e-10,
      );
    }
    check(
      "display beta agrees with nominal strength",
      Math.abs(beta / 1.3986078635588654e-11 - 1) < 1e-14,
    );
    for (const [name, item] of [
      ["original-verify", data],
      ["long-exposure-v1", data.profiles["long-exposure-v1"]],
    ]) {
      const c = item.certificate;
      check(
        `${name} population intervals separate`,
        c.classes.A.skewness_display[1] < c.classes.B.skewness_display[0],
      );
      check(
        `${name} estimator intervals straddle selected threshold`,
        c.classes.A.expanded_skewness_display[1] < c.threshold_display &&
          c.threshold_display < c.classes.B.expanded_skewness_display[0],
      );
      check(
        `${name} count is an intact decimal string`,
        typeof c.sufficient_observation_windows === "string" &&
          /^\d+$/.test(c.sufficient_observation_windows),
      );
    }
    check(
      "current count retained",
      data.profiles["long-exposure-v1"].certificate
        .sufficient_observation_windows === "36938105282195",
    );
    check(
      "original count retained",
      data.certificate.sufficient_observation_windows ===
        "975281623024726766278",
    );
    check(
      "selected count rendered without rounding",
      byId("window-count").textContent.replaceAll(",", "") ===
        selected().certificate.sufficient_observation_windows,
    );
    check(
      "nominal snapshots are centered",
      sides.every(
        (side) =>
          Math.abs(displacements[side].reduce((sum, value) => sum + value, 0)) <
          1e-16,
      ),
    );
    return {
      status: "PASS",
      checks,
      maximum_numeric_clean_residual: residual,
      nominal_covariance: covariance,
      scope:
        "Numerical display checks only; no physical or theorem validation. Browser interactions are checked separately.",
    };
  }
  window.HomometricDemo = Object.freeze({ runChecks, inspectState });
  if (window.location.hash === "#check") {
    const output = document.createElement("pre");
    output.id = "demo-check-results";
    output.hidden = true;
    try {
      output.textContent = JSON.stringify(runChecks());
    } catch (error) {
      output.textContent = JSON.stringify({
        status: "FAIL",
        error: error.message,
      });
    }
    document.body.appendChild(output);
  }
})();
