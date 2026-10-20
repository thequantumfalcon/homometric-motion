"""Inspect synthetic output with hash checks and pickle-disabled array loading."""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ARRAY_FIELDS = {
    "synthetic",
    "class_label",
    "scenario",
    "seed_tuple",
    "dimensionless_time",
    "normalized_finite_intensity",
    "normalized_leading_intensity",
    "counts",
    "reference_rate",
    "actual_rate",
    "actual_gain_multiplier",
    "actual_background",
    "nominal_whitened_modes",
}
SCENARIO_NAMES = (
    "iid_nominal",
    "ou_short_lag",
    "ou_long_lag",
    "finite_beta_stress",
    "spring_misspecification",
    "nongaussian_same_covariance",
    "gain_background_drift",
    "correlated_channel_noise",
)


def inspect_run(directory: Path) -> dict:
    directory = directory.resolve()
    result = json.loads((directory / "result.json").read_text(encoding="utf-8"))
    if (
        result.get("status") != "COMPLETED_SYNTHETIC_PROTOTYPE"
        or result.get("synthetic") is not True
    ):
        raise ValueError("not a completed labelled synthetic run")
    rows = result["scenarios_and_classes"]
    if len(rows) != 16 or result["total_frames"] != 131072:
        raise ValueError("incomplete default scenario grid")
    manifest_path = directory / "source_manifest.json"
    if hashlib.sha256(manifest_path.read_bytes()).hexdigest() != result["source_manifest_sha256"]:
        raise ValueError("copied source manifest hash mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if {row["path"]: row["sha256"] for row in manifest["files"]} != result["bindings"]:
        raise ValueError("source manifest/result bindings disagree")
    for name in ["protocol.json", "reference.json"]:
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != result["bindings"][name]:
            raise ValueError("copied input hash mismatch")
    protocol = json.loads((directory / "protocol.json").read_text(encoding="utf-8"))
    reference = json.loads((directory / "reference.json").read_text(encoding="utf-8"))
    if result["reference_certificate_sha256"] != reference["source"]["certificate_sha256"]:
        raise ValueError("reference certificate binding mismatch")
    if (
        [row["name"] for row in protocol["scenarios"]] != list(SCENARIO_NAMES)
        or protocol["classes"] != ["A", "B"]
        or protocol["root_seed"] != 202610200920
        or protocol["frames_per_class_scenario"] != 8192
    ):
        raise ValueError("unexpected saved scenario protocol")
    expected_pairs = {(name, side) for name in SCENARIO_NAMES for side in ("A", "B")}
    if {(row["scenario"]["name"], row["class"]) for row in rows} != expected_pairs:
        raise ValueError("saved cells do not match the default scenario grid")
    seen = set()
    seeds = set()
    total = 0
    for row in rows:
        key = row["scenario"]["name"], row["class"]
        if key in seen or row["synthetic"] is not True or row["frames"] != 8192:
            raise ValueError("duplicate or malformed synthetic cell")
        seen.add(key)
        scenario_index = SCENARIO_NAMES.index(key[0])
        expected_seed = (202610200920, scenario_index, ("A", "B").index(key[1]))
        expected_scenario = protocol["scenarios"][scenario_index]
        if row["scenario"] != expected_scenario:
            raise ValueError("cell scenario disagrees with copied protocol")
        name = row["frame_artifact"]["path"]
        relative = Path(name)
        target = (directory / relative).resolve()
        if relative.is_absolute() or ".." in relative.parts or not target.is_relative_to(directory):
            raise ValueError("frame artifact escapes the selected run")
        if relative.parts[0] != "frames" or len(relative.parts) != 2:
            raise ValueError("unexpected frame artifact layout")
        if target.stat().st_size != row["frame_artifact"]["bytes"]:
            raise ValueError("frame size mismatch")
        if hashlib.sha256(target.read_bytes()).hexdigest() != row["frame_artifact"]["sha256"]:
            raise ValueError("frame hash mismatch")
        with np.load(target, allow_pickle=False) as saved:
            if set(saved.files) != ARRAY_FIELDS:
                raise ValueError("unexpected frame schema")
            arrays = {field: saved[field] for field in ARRAY_FIELDS}
            if any(value.dtype.hasobject for value in arrays.values()):
                raise ValueError("object arrays are forbidden")
            if not bool(arrays["synthetic"]):
                raise ValueError("missing synthetic label")
            if str(arrays["scenario"]) != key[0] or str(arrays["class_label"]) != key[1]:
                raise ValueError("frame labels disagree")
            seed = tuple(arrays["seed_tuple"].tolist())
            if seed in seeds or seed != tuple(row["seed_tuple"]) or seed != expected_seed:
                raise ValueError("duplicate or mismatched seed")
            seeds.add(seed)
            times = arrays["dimensionless_time"]
            expected_times = np.arange(8192) * expected_scenario["lag"]
            if times.shape != (8192,) or not np.array_equal(times, expected_times):
                raise ValueError("dimensionless sampling grid mismatch")
            counts = arrays["counts"]
            if counts.shape != (8192,) or not np.issubdtype(counts.dtype, np.integer):
                raise ValueError("count shape or type mismatch")
            if np.any(counts < 0):
                raise ValueError("negative count")
            for field in [
                "normalized_finite_intensity",
                "normalized_leading_intensity",
                "reference_rate",
                "actual_rate",
                "actual_gain_multiplier",
                "actual_background",
            ]:
                values = arrays[field]
                if values.shape != (8192,) or not np.all(np.isfinite(values)) or np.any(values < 0):
                    raise ValueError("invalid numerical frame field")
            modes = arrays["nominal_whitened_modes"]
            if modes.shape != (8192, 62) or not np.all(np.isfinite(modes)):
                raise ValueError("invalid stored modes")
            # Recompute every modal statistic from the retained complete trajectory.
            centered = modes - np.mean(modes, axis=0)
            covariance = centered.T @ centered / (len(modes) - 1)
            modal_variance = np.mean(centered**2, axis=0)
            if np.any(modal_variance <= 0):
                raise ValueError("degenerate stored modal trajectory")
            excess = np.mean(centered**4, axis=0) / modal_variance**2 - 3
            if not np.allclose(
                covariance, row["nominal_whitened_sample_covariance"], rtol=1e-12, atol=1e-12
            ):
                raise ValueError("stored covariance does not match complete modal trajectory")
            if not np.allclose(excess, row["modal_excess_kurtosis"], rtol=1e-12, atol=1e-12):
                raise ValueError("stored kurtosis does not match complete modal trajectory")
            diagnostic = row["diagnostics"]
            recomputed = {
                "nominal_whitened_covariance_frobenius_relative": (
                    np.sqrt(np.sum((covariance - np.eye(62)) ** 2) / 62)
                ),
                "mean_modal_excess_kurtosis": np.mean(excess),
                "first_nominal_mode_lag1_correlation": np.corrcoef(modes[:-1, 0], modes[1:, 0])[
                    0, 1
                ],
            }
            if any(
                not np.isclose(value, diagnostic[name], rtol=1e-12, atol=1e-12)
                for name, value in recomputed.items()
            ):
                raise ValueError("modal diagnostic summary mismatch")
            total += len(counts)
    return {
        "status": "INSPECTED_SYNTHETIC_OUTPUT",
        "synthetic": True,
        "cells": len(rows),
        "frames": total,
        "modal_coordinates_per_frame": 62,
        "complete_covariance_and_kurtosis_recomputed": True,
        "qualification": (
            "Saved-file consistency only. Hashes are compared with the selected saved record, "
            "not independently authenticated. No model-validation or error-guarantee claim."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(inspect_run(args.run), sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
        print(f"Inspection failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
