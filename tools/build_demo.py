"""Build deterministic offline demonstration data from a verified certificate."""

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(content):
    return hashlib.sha256(content).hexdigest()


def generate(certificate_path):
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
    if Fraction(frequency["signed_gap_exact"]) <= 0:
        raise ValueError("the selected class intervals must separate")
    classes = {}
    for side in ("A", "B"):
        exact = frequency["classes"][side]["skewness"]
        expanded = counts["expanded_shape_intervals_exact"][side]
        classes[side] = {
            "skewness_exact": {key: exact[key] for key in ("lower", "upper")},
            "skewness_display": [float(Fraction(exact[key])) for key in ("lower", "upper")],
            "expanded_skewness_exact": expanded,
            "expanded_skewness_display": [float(Fraction(value)) for value in expanded],
        }
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
            "gap_display": float(Fraction(frequency["signed_gap_exact"])),
            "threshold_exact": counts["threshold_exact"],
            "threshold_display": float(Fraction(counts["threshold_exact"])),
            "sufficient_observation_windows": str(counts["sufficient_observation_windows"]),
            "per_class_error_target_exact": "1/20",
            "selection_disclosure": certificate["selection_disclosure"],
        },
        "display_scope": {
            "geometry": "Floating-point illustration of exact symbolic positions and clean intensities.",
            "bounds": "Display values from a saved exact-arithmetic certificate; slider settings do not recompute or extend it.",
            "limitations": certificate["limitations"],
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "demo")
    parser.add_argument(
        "--check", action="store_true", help="compare generated data without writing"
    )
    args = parser.parse_args()
    data = generate(args.certificate)
    encoded = json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n"
    javascript = (
        "// Deterministic local display data; exact fractions accompany approximate labels.\n"
    )
    javascript += "window.HOMOMETRIC_DEMO_DATA = " + encoded.rstrip() + ";\n"
    outputs = {"data.json": encoded, "data.js": javascript}
    if args.check:
        for name, content in outputs.items():
            if (args.output_dir / name).read_text(encoding="utf-8") != content:
                raise SystemExit(f"demonstration data differs: {name}")
        print("PASS: demonstration data matches the saved certificate and current source manifest")
    else:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        for name, content in outputs.items():
            (args.output_dir / name).write_text(content, encoding="utf-8", newline="\n")
        print("Wrote deterministic data.json and data.js; no timestamps or machine paths included")


if __name__ == "__main__":
    main()
