"use strict";

(() => {
  const data = window.HOMOMETRIC_DEMO_DATA;
  if (!data || data.schema_version !== 1 || data.scenario !== "exact_geometry") {
    document.body.textContent = "Display data is missing. Keep index.html, data.js, app.js and style.css together.";
    return;
  }
  const NS = "http://www.w3.org/2000/svg";
  const colors = { A: "#087a7e", B: "#ad5818" };
  const omega = Math.PI / 3;
  const theta = Math.asin(1 / (5 * Math.sqrt(3)));
  const phi = -Math.asin(1 / (8 * Math.sqrt(3)));
  const tau = 2 * Math.PI;
  const positions = {};
  for (const side of ["A", "B"]) {
    positions[side] = data.geometry.translations[side].flatMap(shift =>
      data.geometry.motif.map(([integer, a, b]) =>
        integer + shift + a * theta / omega + b * phi / omega
      )
    ).sort((a, b) => a - b);
  }
  const byId = id => document.getElementById(id);
  function element(parent, tag, attributes = {}, text = null) {
    const node = document.createElementNS(NS, tag);
    for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, String(value));
    if (text !== null) node.textContent = text;
    parent.appendChild(node);
    return node;
  }
  function cleanGroup(svg) {
    const existing = svg.querySelector(":scope > g");
    if (existing) existing.remove();
    return element(svg, "g");
  }
  function amplitude(side, frequency) {
    let real = 0, imaginary = 0;
    for (const x of positions[side]) {
      real += Math.cos(frequency * x);
      imaginary += Math.sin(frequency * x);
    }
    return { real, imaginary, intensity: (real * real + imaginary * imaginary) / (63 * 63) };
  }
  const curves = Array.from({ length: 1001 }, (_, index) => {
    const frequency = tau * index / 1000;
    return { frequency, A: amplitude("A", frequency).intensity, B: amplitude("B", frequency).intensity };
  });
  let frequency = omega;
  let boundMode = "latent";
  let marker = null;
  let animation = null;
  let lastFrame = null;

  function drawSpectrum() {
    const svg = byId("spectrum"), group = cleanGroup(svg);
    const logarithmic = byId("log-scale").checked;
    const x = value => 54 + value / tau * 842;
    const y = value => 258 - 218 * (logarithmic ? Math.log10(1 + 1000 * Math.max(0, value)) / Math.log10(1001) : value);
    const ticks = logarithmic ? [0, 0.001, 0.01, 0.1, 1] : [0, 0.25, 0.5, 0.75, 1];
    for (const value of ticks) {
      element(group, "line", { x1: 54, x2: 896, y1: y(value), y2: y(value), stroke: "#e5eae5", "stroke-width": 1 });
      element(group, "text", { x: 44, y: y(value) + 4, "text-anchor": "end", "font-size": 10 }, String(value));
    }
    for (const [value, label] of [[0, "0"], [omega, "π/3"], [Math.PI, "π"], [tau, "2π"]]) {
      element(group, "line", { x1: x(value), x2: x(value), y1: 258, y2: 263, stroke: "#98aaa6" });
      element(group, "text", { x: x(value), y: 280, "text-anchor": "middle" }, label);
    }
    element(group, "text", { x: 54, y: 18, "font-size": 10 }, logarithmic ? "Clean intensity / 63² · log display" : "Clean intensity / 63² · linear display");
    element(group, "text", { x: 896, y: 303, "text-anchor": "end", "font-size": 10 }, "Common frequency t");
    for (const side of ["A", "B"]) {
      const path = curves.map((row, index) => `${index ? "L" : "M"}${x(row.frequency).toFixed(3)},${y(row[side]).toFixed(3)}`).join(" ");
      const attributes = { d: path, fill: "none", stroke: colors[side], "stroke-width": side === "A" ? 2.5 : 1.5, "stroke-linejoin": "round" };
      if (side === "B") attributes["stroke-dasharray"] = "6 5";
      element(group, "path", attributes);
    }
    marker = element(group, "g");
    drawMarker();
  }
  function drawMarker() {
    if (!marker) return;
    marker.replaceChildren();
    const x = 54 + frequency / tau * 842;
    element(marker, "line", { x1: x, x2: x, y1: 33, y2: 258, stroke: "#53656e", "stroke-width": 1, "stroke-dasharray": "3 4" });
    for (const side of ["A", "B"]) {
      const value = amplitude(side, frequency).intensity;
      const scaled = byId("log-scale").checked ? Math.log10(1 + 1000 * value) / Math.log10(1001) : value;
      element(marker, "circle", { cx: x, cy: 258 - 218 * scaled, r: side === "A" ? 5 : 3, fill: side === "A" ? "white" : colors.B, stroke: colors[side], "stroke-width": 1.5 });
    }
  }
  function drawPhases() {
    const group = cleanGroup(byId("phases"));
    element(group, "circle", { cx: 130, cy: 126, r: 88, fill: "none", stroke: "#d8e2dc" });
    element(group, "line", { x1: 32, x2: 228, y1: 126, y2: 126, stroke: "#e5eae5" });
    element(group, "line", { x1: 130, x2: 130, y1: 28, y2: 224, stroke: "#e5eae5" });
    for (const side of ["A", "B"]) {
      for (const point of positions[side]) {
        const angle = frequency * point;
        element(group, "circle", {
          cx: 130 + 88 * Math.cos(angle), cy: 126 - 88 * Math.sin(angle),
          r: side === "A" ? 3.4 : 2.1, fill: side === "A" ? colors.A : "white",
          stroke: colors[side], "stroke-width": 1.1, opacity: 0.85
        });
      }
      const total = amplitude(side, frequency);
      element(group, "line", {
        x1: 130, y1: 126, x2: 130 + 88 * total.real / 63, y2: 126 - 88 * total.imaginary / 63,
        stroke: colors[side], "stroke-width": side === "A" ? 2.5 : 1.4,
        "stroke-dasharray": side === "B" ? "4 3" : "none"
      });
    }
    element(group, "circle", { cx: 130, cy: 126, r: 2, fill: "#657b80" });
    element(group, "text", { x: 130, y: 250, "text-anchor": "middle", "font-size": 10 }, "Dots: unit phases · lines: mean phasor");
  }
  function setFrequency(value) {
    frequency = Math.min(tau, Math.max(0, Number(value)));
    byId("frequency").value = String(frequency);
    byId("frequency-value").textContent = Math.abs(frequency - omega) < 1e-13 ? "π / 3 ≈ 1.047198" : frequency.toFixed(6);
    for (const side of ["A", "B"]) byId(`intensity-${side.toLowerCase()}`).textContent = amplitude(side, frequency).intensity.toExponential(4);
    drawMarker();
    drawPhases();
  }
  function graphEdges(side) {
    const result = [];
    for (let i = 0; i < 63; i++) for (let j = i + 1; j < 63; j++) {
      if (positions[side][j] - positions[side][i] <= 2.5) result.push([i, j]);
    }
    return result;
  }
  function drawGeometry() {
    const group = cleanGroup(byId("geometry"));
    const x = value => 65 + value / 93 * 963;
    for (const [side, y] of [["A", 77], ["B", 160]]) {
      const chord = data.geometry.chords_zero_based[side];
      element(group, "text", { x: 18, y: y + 5, fill: colors[side], "font-size": 17, "font-weight": 700 }, side);
      for (const [i, j] of graphEdges(side)) {
        const extra = j !== i + 1;
        const left = x(positions[side][i]), right = x(positions[side][j]);
        element(group, "path", {
          d: `M${left},${y} Q${(left + right) / 2},${y - (extra ? 62 : 8)} ${right},${y}`,
          fill: "none", stroke: extra ? colors[side] : "#adbfbb", "stroke-width": extra ? 2.3 : 1.1
        });
      }
      positions[side].forEach((value, index) => {
        const inTriangle = index >= chord[0] && index <= chord[1];
        const dot = element(group, "circle", { cx: x(value), cy: y, r: inTriangle ? 4.3 : 2.6, fill: inTriangle ? colors[side] : "#6f9693" });
        element(dot, "title", {}, `${side} vertex ${index}, mean position approximately ${value.toFixed(6)}`);
      });
      element(group, "text", { x: x(positions[side][chord[0]]) + 11, y: y - 38, "text-anchor": "middle", fill: colors[side], "font-size": 11 }, `${chord[0]} ↔ ${chord[1]}`);
    }
    for (const value of [0, 30, 63, 93]) element(group, "text", { x: x(value), y: 196, "text-anchor": "middle", "font-size": 10 }, String(value));
    element(group, "text", { x: 1030, y: 210, "text-anchor": "end", "font-size": 9 }, "Mean position · numeric rendering of exact symbolic coordinates");
  }
  function drawBounds() {
    const certificate = data.certificate;
    const group = cleanGroup(byId("bounds"));
    const range = [
      certificate.classes.A.expanded_skewness_display[0] - 0.00016,
      certificate.classes.B.expanded_skewness_display[1] + 0.00016
    ];
    const x = value => 65 + (value - range[0]) / (range[1] - range[0]) * 663;
    const records = {};
    for (let i = 0; i < 6; i++) {
      const value = range[0] + i / 5 * (range[1] - range[0]);
      element(group, "line", { x1: x(value), x2: x(value), y1: 38, y2: 203, stroke: "#e5eae5" });
      element(group, "text", { x: x(value), y: 226, "text-anchor": "middle", "font-size": 11 }, value.toFixed(4));
    }
    for (const [side, y] of [["A", 82], ["B", 158]]) {
      const interval = certificate.classes[side][boundMode === "expanded" ? "expanded_skewness_display" : "skewness_display"];
      records[side] = interval;
      element(group, "text", { x: 25, y: y + 5, fill: colors[side], "font-size": 18, "font-weight": 600 }, side);
      element(group, "rect", { x: x(interval[0]), y: y - 16, width: x(interval[1]) - x(interval[0]), height: 32, rx: 5, fill: side === "A" ? "#d9eeea" : "#fce7d0" });
      element(group, "line", { x1: x(interval[0]), x2: x(interval[1]), y1: y, y2: y, stroke: colors[side], "stroke-width": 2 });
      for (const value of interval) element(group, "line", { x1: x(value), x2: x(value), y1: y - 9, y2: y + 9, stroke: colors[side], "stroke-width": 2 });
      byId(`bound-${side.toLowerCase()}`).textContent = `≈ [${interval[0].toFixed(10)}, ${interval[1].toFixed(10)}]`;
    }
    const left = x(records.A[1]), right = x(records.B[0]);
    element(group, "line", { x1: left, x2: right, y1: 119, y2: 119, stroke: "#506b70", "stroke-width": 1.2 });
    for (const end of [left, right]) element(group, "line", { x1: end, x2: end, y1: 114, y2: 124, stroke: "#506b70" });
    element(group, "text", { x: (left + right) / 2, y: 107, "text-anchor": "middle", "font-size": 10 }, "positive gap");
    if (boundMode === "expanded") {
      const threshold = x(certificate.threshold_display);
      element(group, "line", { x1: threshold, x2: threshold, y1: 33, y2: 204, stroke: "#6b697c", "stroke-dasharray": "4 4" });
      element(group, "text", { x: threshold, y: 23, "text-anchor": "middle", "font-size": 10 }, "fixed decision threshold");
    }
    element(group, "text", { x: 395, y: 259, "text-anchor": "middle", "font-size": 11 }, "Standardized third cumulant (skewness)");
    byId("bound-caption").textContent = boundMode === "expanded"
      ? "Estimator allowance η = 10⁻⁵. The dashed line is the fixed threshold; the intervals separate on the controlled moment-error event. Decimal labels are approximate."
      : "Uniform finite-exposure bounds at the stated frequency tolerance. Decimal labels are approximate; exact rational endpoints are included in data.json.";
  }
  function stopSweep() {
    if (animation !== null) cancelAnimationFrame(animation);
    animation = null;
    lastFrame = null;
    byId("sweep").setAttribute("aria-pressed", "false");
    byId("sweep").textContent = "Sweep frequency ▶";
  }
  function sweepFrame(time) {
    if (lastFrame !== null) setFrequency((frequency + (time - lastFrame) * tau / 16000) % tau);
    lastFrame = time;
    animation = requestAnimationFrame(sweepFrame);
  }
  byId("frequency").addEventListener("input", event => { stopSweep(); setFrequency(event.target.value); });
  byId("log-scale").addEventListener("change", drawSpectrum);
  byId("null-frequency").addEventListener("click", () => { stopSweep(); setFrequency(omega); });
  byId("sweep").addEventListener("click", () => {
    if (animation !== null) { stopSweep(); return; }
    byId("sweep").setAttribute("aria-pressed", "true");
    byId("sweep").textContent = "Pause sweep ❚❚";
    animation = requestAnimationFrame(sweepFrame);
  });
  document.addEventListener("visibilitychange", () => { if (document.hidden) stopSweep(); });
  for (const radio of document.querySelectorAll('input[name="bound-mode"]')) radio.addEventListener("change", event => { boundMode = event.target.value; drawBounds(); });
  byId("check-count").textContent = String(data.source.mathematical_checks);
  const countGroups = data.certificate.sufficient_observation_windows.replace(/\B(?=(\d{3})+(?!\d))/g, ",").split(",");
  byId("window-count").replaceChildren();
  for (const [index, digits] of countGroups.entries()) {
    const group = document.createElement("span");
    group.style.whiteSpace = "nowrap";
    group.textContent = digits + (index < countGroups.length - 1 ? "," : "");
    byId("window-count").appendChild(group);
    if (index < countGroups.length - 1) byId("window-count").appendChild(document.createElement("wbr"));
  }
  byId("certificate-hash").textContent = data.source.certificate_sha256;
  drawSpectrum();
  drawGeometry();
  drawBounds();
  setFrequency(omega);

  function runChecks() {
    const checks = {};
    function check(name, value) { checks[name] = Boolean(value); if (!value) throw new Error(name); }
    check("two distinct 63-point configurations", ["A", "B"].every(s => positions[s].length === 63 && new Set(positions[s]).size === 63));
    for (const side of ["A", "B"]) {
      const edges = graphEdges(side), chord = data.geometry.chords_zero_based[side];
      check(`${side} path plus declared chord`, edges.length === 63 && edges.filter(([i, j]) => j !== i + 1).length === 1 && edges.some(([i, j]) => i === chord[0] && j === chord[1]));
    }
    const residual = Math.max(...curves.map(row => Math.abs(row.A - row.B)));
    check("illustrative clean-intensity agreement", residual < 1e-11);
    check("numeric null consistency", amplitude("A", omega).intensity < 1e-25 && amplitude("B", omega).intensity < 1e-25);
    check("certificate intervals separate", data.certificate.classes.A.skewness_display[1] < data.certificate.classes.B.skewness_display[0]);
    check("estimator intervals separate", data.certificate.classes.A.expanded_skewness_display[1] < data.certificate.classes.B.expanded_skewness_display[0]);
    check("published count retained as a decimal string", data.certificate.sufficient_observation_windows === "975281623024726766278");
    check("count display preserves every digit", byId("window-count").textContent.replaceAll(",", "") === data.certificate.sufficient_observation_windows);
    const logScale = byId("log-scale");
    logScale.checked = false;
    logScale.dispatchEvent(new Event("change", { bubbles: true }));
    check("linear intensity scale can be selected", byId("spectrum").textContent.includes("linear display"));
    logScale.checked = true;
    logScale.dispatchEvent(new Event("change", { bubbles: true }));
    check("log intensity scale can be restored", byId("spectrum").textContent.includes("log display"));
    byId("frequency").value = "2.345";
    byId("frequency").dispatchEvent(new Event("input", { bubbles: true }));
    check("frequency control updates displayed value", byId("frequency-value").textContent === "2.345000");
    byId("null-frequency").click();
    check("null preset restores frequency", Math.abs(frequency - omega) < 1e-15);
    const expanded = document.querySelector('input[name="bound-mode"][value="expanded"]');
    expanded.checked = true;
    expanded.dispatchEvent(new Event("change", { bubbles: true }));
    check("estimator mode updates chart", byId("bound-caption").textContent.includes("Estimator allowance") && byId("bounds").textContent.includes("fixed decision threshold"));
    const latent = document.querySelector('input[name="bound-mode"][value="latent"]');
    latent.checked = true;
    latent.dispatchEvent(new Event("change", { bubbles: true }));
    byId("sweep").click();
    check("sweep starts on explicit action", byId("sweep").getAttribute("aria-pressed") === "true");
    byId("sweep").click();
    check("sweep can be paused", byId("sweep").getAttribute("aria-pressed") === "false");
    return { status: "PASS", checks, maximum_numeric_clean_residual: residual, scope: "Display and interaction checks only; not a proof or stochastic experiment." };
  }
  window.HomometricDemo = Object.freeze({ runChecks });
  if (window.location.hash === "#check") {
    const output = document.createElement("pre");
    output.id = "demo-check-results";
    output.hidden = true;
    try { output.textContent = JSON.stringify(runChecks()); }
    catch (error) { output.textContent = JSON.stringify({ status: "FAIL", error: error.message }); }
    document.body.appendChild(output);
  }
})();
