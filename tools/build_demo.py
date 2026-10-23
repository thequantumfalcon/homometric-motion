"""Build deterministic offline display data from freshly reproduced certificates."""

import argparse
import hashlib
import json
import runpy
from fractions import Fraction
from pathlib import Path

from homometric_motion.arithmetic import rational_from_text as exact

ROOT = Path(__file__).resolve().parents[1]
build_display_manifest = runpy.run_path(str(ROOT / "tools" / "demo_manifest.py"))["build_manifest"]


def digest(content):
    return hashlib.sha256(content).hexdigest()


def shape_classes(population, expanded, threshold_text, gap_text):
    """Check the display's exact ordering before converting labels to floats."""
    classes = {}
    for side in ("A", "B"):
        lower, upper = (exact(population[side][key]) for key in ("lower", "upper"))
        expanded_lower, expanded_upper = map(exact, expanded[side])
        if not 0 < expanded_lower <= lower <= upper <= expanded_upper:
            raise ValueError(f"invalid population or estimator interval for class {side}")
        classes[side] = {
            "skewness_exact": {key: population[side][key] for key in ("lower", "upper")},
            "skewness_display": [float(lower), float(upper)],
            "expanded_skewness_exact": expanded[side],
            "expanded_skewness_display": [float(expanded_lower), float(expanded_upper)],
        }
    if exact(population["B"]["lower"]) - exact(population["A"]["upper"]) != exact(gap_text):
        raise ValueError("population gap differs from the displayed intervals")
    if not exact(expanded["A"][1]) < exact(threshold_text) < exact(expanded["B"][0]):
        raise ValueError("classifier threshold must lie strictly inside the estimator gap")
    return classes


def profile_display(profile, certificate_sha256, original, manifest_sha256):
    """Extract one explicit contract; the embedded old core is not its result."""
    if (
        profile.get("status") != "PASS"
        or profile.get("schema_version") != 1
        or profile.get("certificate_kind") != "profiled_count_certificate"
        or profile.get("profile") != "long-exposure-v1"
        or profile.get("scenario") != "exact_geometry"
    ):
        raise ValueError("a successful long-exposure-v1 / exact_geometry profile is required")
    core = {key: value for key, value in original.items() if key != "source_revision"}
    core_hash = digest(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    if (
        profile["source_revision"] != original["source_revision"]
        or profile["core_certificate"] != core
        or profile["core_certificate_sha256"] != core_hash
    ):
        raise ValueError("profile and original certificate must bind the same source and core")
    parameters = profile["parameters"]
    if parameters["exposure_cap_exact"] != "1/1000" or "eta_exact" in parameters:
        raise ValueError("the profile requires its own exposure and separate estimator allowances")
    for name, value in original["parameters"].items():
        if name not in ("exposure_cap_exact", "eta_exact") and parameters.get(name) != value:
            raise ValueError(f"profile changed the fixed model parameter: {name}")
    allocation = profile["allocation"]
    windows = allocation["sufficient_observation_windows"]
    risk = exact(allocation["individual_class_error_upper"]["exact"])
    budget = exact(allocation["unrounded_count_exact"])
    if (
        allocation["status"] != "PASS"
        or windows != 36938105282195
        or not 0 < risk <= Fraction(1, 20)
        or windows != -(-budget.numerator // budget.denominator)
        or risk != budget / (20 * windows)
    ):
        raise ValueError("profile count and risk must match the selected finite-window bound")
    union = profile["nuisance_evidence"]["observation_union"]
    if union["time_cell_count_per_class"] != 512 or union["exposure_cap_exact"] != "1/1000":
        raise ValueError("long-profile display requires the complete 512-cell exposure union")
    population = {
        side: profile["observation_bounds"]["classes"][side]["skewness"] for side in ("A", "B")
    }
    if any(
        allocation["original_shapes"][side] != [population[side][key] for key in ("lower", "upper")]
        for side in ("A", "B")
    ):
        raise ValueError("estimator allocation must use the selected profile's population shapes")
    threshold = allocation["threshold_exact"]
    if allocation["classifier"]["threshold_exact"] != threshold:
        raise ValueError("classifier threshold differs from the selected allocation")
    classes = shape_classes(
        population, allocation["expanded_shapes"], threshold, union["signed_gap_exact"]
    )
    return {
        "profile": "long-exposure-v1",
        "scenario": "exact_geometry",
        "label": "Long exposure · v1",
        "source": {
            "certificate_sha256": certificate_sha256,
            "package_manifest_sha256": manifest_sha256,
            "mathematical_checks": profile["checks"]["count"],
            "revision_kind": "release_adaptation",
        },
        "certificate": {
            "classes": classes,
            "parameters": parameters,
            "gap_lower_exact": union["signed_gap_exact"],
            "gap_display": float(exact(union["signed_gap_exact"])),
            "threshold_exact": threshold,
            "threshold_display": float(exact(threshold)),
            "sufficient_observation_windows": str(windows),
            "per_class_error_target_exact": "1/20",
            "individual_class_error_upper_exact": allocation["individual_class_error_upper"][
                "exact"
            ],
            "selection_disclosure": profile["selection_disclosure"],
        },
        "display_scope": {
            "bounds": "Exact-arithmetic long-exposure-v1 / exact_geometry certificate; controls do not recompute or extend it.",
            "limitations": original["limitations"],
            "qualification": profile["qualification"],
        },
    }


def generate(certificate_path, profile_path):
    raw = certificate_path.read_bytes()
    certificate = json.loads(raw)
    if certificate.get("status") != "PASS" or certificate.get("schema_version") != 1:
        raise ValueError("a successful schema-1 certificate is required")
    if certificate.get("scenario") != "exact_geometry":
        raise ValueError("the explorer requires the exact_geometry scenario")
    package = ROOT / "src" / "homometric_motion"
    manifest_raw = (package / "source_manifest.json").read_bytes()
    manifest = json.loads(manifest_raw)
    bindings = {}
    for record in manifest["files"]:
        name = record["path"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("source manifest must use package basenames")
        actual = digest((package / name).read_bytes())
        if actual != record["sha256"]:
            raise ValueError(f"source manifest is stale: {name}")
        bindings[name] = actual
    source = certificate["source_revision"]
    if (
        source["manifest_sha256"] != digest(manifest_raw)
        or source["bindings"] != bindings
        or source["revision_kind"] != "release_adaptation"
    ):
        raise ValueError("certificate does not bind the current reviewed source revision")
    frequency = certificate["stages"]["frequency"]
    counts = certificate["stages"]["counts"]
    if counts["sufficient_observation_windows"] != 975281623024726766278:
        raise ValueError("the demonstration is for the fixed released count certificate")
    if exact(frequency["signed_gap_exact"]) <= 0:
        raise ValueError("the selected class intervals must separate")
    classes = shape_classes(
        {side: frequency["classes"][side]["skewness"] for side in ("A", "B")},
        counts["expanded_shape_intervals_exact"],
        counts["threshold_exact"],
        frequency["signed_gap_exact"],
    )
    profile_raw = profile_path.read_bytes()
    selected_profile = profile_display(
        json.loads(profile_raw), digest(profile_raw), certificate, digest(manifest_raw)
    )
    return {
        "schema_version": 1,
        "scenario": "exact_geometry",
        "title": "Homometric motion: an offline explorer",
        "source": {
            "certificate_sha256": digest(raw),
            "package_manifest_sha256": digest(manifest_raw),
            "mathematical_checks": certificate["checks"]["count"],
            "revision_kind": "release_adaptation",
        },
        "geometry": {
            "count": 63,
            "motif": [
                row
                for j in range(10)
                for row in (
                    [3 * j, 0, (-1) ** j if j >= 2 else 0],
                    [3 * j + 1, (-1) ** j, 0],
                )
            ]
            + [[30, 0, 0]],
            "coordinate_basis": ["1", "theta/omega", "phi/omega"],
            "omega": "pi/3",
            "theta": "asin(1/(5*sqrt(3)))",
            "phi": "-asin(1/(8*sqrt(3)))",
            "translations": {"A": [0, 31, 63], "B": [0, 32, 63]},
            "chords_zero_based": {"A": [20, 22], "B": [41, 43]},
            "contact_threshold_exact": "5/2",
        },
        "certificate": {
            "classes": classes,
            "parameters": certificate["parameters"],
            "gap_lower_exact": frequency["signed_gap_exact"],
            "gap_display": float(exact(frequency["signed_gap_exact"])),
            "threshold_exact": counts["threshold_exact"],
            "threshold_display": float(exact(counts["threshold_exact"])),
            "sufficient_observation_windows": str(counts["sufficient_observation_windows"]),
            "per_class_error_target_exact": "1/20",
            "selection_disclosure": certificate["selection_disclosure"],
        },
        "display_scope": {
            "geometry": "Floating-point illustration of exact symbolic positions and clean intensities.",
            "bounds": "Display values from a saved exact-arithmetic certificate; slider settings do not recompute or extend it.",
            "limitations": certificate["limitations"],
        },
        "profiles": {"long-exposure-v1": selected_profile},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", required=True, type=Path)
    parser.add_argument("--profile-certificate", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "demo")
    parser.add_argument(
        "--check", action="store_true", help="compare generated data without writing"
    )
    args = parser.parse_args()
    data = generate(args.certificate, args.profile_certificate)
    encoded = json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
    javascript = (
        "// Deterministic local display data; exact fractions accompany approximate labels.\n"
    )
    javascript += "window.HOMOMETRIC_DEMO_DATA = " + encoded.rstrip() + ";\n"
    outputs = {"data.json": encoded, "data.js": javascript}
    display_manifest = build_display_manifest(
        args.output_dir, {name: content.encode("utf-8") for name, content in outputs.items()}
    )
    outputs["SOURCE_MANIFEST.json"] = json.dumps(display_manifest, indent=2, sort_keys=True) + "\n"
    if args.check:
        for name, content in outputs.items():
            if (args.output_dir / name).read_text(encoding="utf-8") != content:
                raise SystemExit(f"demonstration data differs: {name}")
        print("PASS: demonstration data and display manifest match the certificates and source")
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (args.output_dir / name).write_text(content, encoding="utf-8", newline="\n")
        print("Wrote deterministic data.json, data.js and SOURCE_MANIFEST.json")


if __name__ == "__main__":
    main()
