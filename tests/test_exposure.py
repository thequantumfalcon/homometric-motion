"""Installed-wheel contracts for the separate linear-exposure certificate."""

import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction
from functools import lru_cache
from importlib import metadata, resources
from math import comb
from pathlib import Path
from unittest import mock

import homometric_motion
from homometric_motion import (
    build_certificate,
    build_coordinate_certificate,
    build_exposure_certificate,
)
from homometric_motion.cli import MANIFEST_FILES, summary, verify_source_manifest
from homometric_motion.exposure import linear_exposure_certificate


def exact(value):
    """Independent bounded-chunk parsing without changing interpreter limits."""
    if isinstance(value, dict):
        value = value["exact"]
    if isinstance(value, int):
        return Fraction(value)
    pieces = value.split("/")

    def integer(text):
        sign = -1 if text.startswith("-") else 1
        text = text.removeprefix("-")
        result = 0
        for start in range(0, len(text), 7):
            group = text[start : start + 7]
            result = result * 10 ** len(group) + int(group)
        return sign * result

    return Fraction(integer(pieces[0]), integer(pieces[1]) if len(pieces) == 2 else 1)


def canonical_hash(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


@lru_cache(maxsize=2)
def exposure(scenario):
    return build_exposure_certificate(scenario)


class ExposureTests(unittest.TestCase):
    scenarios = {
        "exact_geometry": {
            "new": 26815183544609917,
            "common": 975322906947719258189,
            "old_coordinate": 26814048499063502,
            "old_common": 975281623024726766278,
        },
        "position_uncertainty": {
            "new": 26809378397093764,
            "common": 975069899450789037155,
            "old_coordinate": 26808243624540316,
            "old_common": 975028627229038193209,
        },
    }

    @classmethod
    def setUpClass(cls):
        package = Path(homometric_motion.__file__).resolve()
        source = Path(__file__).resolve().parents[1] / "src"
        if package.is_relative_to(source) or "site-packages" not in package.parts:
            raise AssertionError("exposure tests require an installed wheel")
        if metadata.version("homometric-motion") != homometric_motion.__version__:
            raise AssertionError("installed distribution mismatch")

    def test_fresh_reference_preserved_and_new_domain_is_explicit(self):
        guard = sys.get_int_max_str_digits()
        for scenario, expected in self.scenarios.items():
            with self.subTest(scenario=scenario):
                result = exposure(scenario)
                core = result["core_certificate"]
                extension = result["extension"]
                coordinate = result["coordinate_counts"]
                self.assertEqual(core, build_certificate(scenario))
                self.assertEqual(result["core_certificate_sha256"], canonical_hash(core))
                self.assertEqual(result["certificate_kind"], "linear_exposure_count_extension")
                self.assertEqual(
                    exact(core["parameters"]["exposure_cap_exact"]), Fraction(1, 10**20)
                )
                self.assertEqual(
                    exact(extension["parameters"]["exposure_cap_exact"]), Fraction(1, 10**5)
                )
                for key, value in core["parameters"].items():
                    if key != "exposure_cap_exact":
                        self.assertEqual(extension["parameters"][key], value)
                self.assertEqual(
                    core["stages"]["counts"]["sufficient_observation_windows"],
                    expected["old_common"],
                )
                self.assertEqual(
                    build_coordinate_certificate(scenario)["coordinate_counts"][
                        "sufficient_observation_windows"
                    ],
                    expected["old_coordinate"],
                )
                self.assertEqual(coordinate["sufficient_observation_windows"], expected["new"])
                self.assertEqual(
                    extension["stages"]["counts"]["sufficient_observation_windows"],
                    expected["common"],
                )
                self.assertEqual(
                    coordinate["previous_sufficient_observation_windows"], expected["common"]
                )
                self.assertEqual(coordinate["comparison_baseline"], "extension.stages.counts")
                self.assertEqual(
                    coordinate["classifier"]["unchanged_relative_to"], "extension.stages.counts"
                )
                self.assertNotIn("unchanged", coordinate["classifier"])
                self.assertEqual(
                    coordinate["parameters_shared_with_common_count"], extension["parameters"]
                )
                self.assertEqual(sys.get_int_max_str_digits(), guard)

    def test_new_inflation_and_complete_coordinate_error_budget(self):
        for scenario, expected in self.scenarios.items():
            with self.subTest(scenario=scenario):
                result = exposure(scenario)
                extension = result["extension"]
                stages = extension["stages"]
                selected = stages["position" if scenario == "position_uncertainty" else "frequency"]
                common = stages["counts"]
                witness = result["coordinate_counts"]
                gamma = exact(common["spectral_gap_lower_exact"])
                lag = exact(common["lag_lower_exact"])
                cap = exact(common["exposure_cap_exact"])
                H = 1 + 2 / (gamma * (lag - cap))
                self.assertEqual(cap, Fraction(1, 100000))
                self.assertGreater(lag, cap)
                self.assertEqual(H, exact(common["window_variance_inflation_upper_exact"]))
                self.assertGreater(
                    H,
                    exact(
                        result["core_certificate"]["stages"]["counts"][
                            "window_variance_inflation_upper_exact"
                        ]
                    ),
                )
                raw = [Fraction(1)] + [
                    max(
                        exact(
                            selected["classes"][side]["normalized_raw_moment_upper_bounds"][str(j)]
                        )
                        for side in ("A", "B")
                    )
                    for j in range(1, 7)
                ]
                factorial = {
                    j: sum(comb(j, k) * Fraction(11, 10) ** k * raw[k] for k in range(j + 1))
                    for j in range(1, 7)
                }
                second = {
                    1: factorial[2] + factorial[1],
                    2: factorial[4] + 4 * factorial[3] + 2 * factorial[2],
                    3: factorial[6] + 9 * factorial[5] + 18 * factorial[4] + 6 * factorial[3],
                }
                amin = Fraction(81, 100) * min(
                    exact(selected["classes"][side]["normalized_variance"]["lower"])
                    for side in ("A", "B")
                )
                eta = Fraction(1, 100000)
                t1, t2, t3 = (exact(witness["raw_mean_tolerances"][str(j)]) for j in (1, 2, 3))
                variance_error = t2 + 2 * factorial[1] * t1 + t1**2
                third_error = (
                    t3
                    + 3 * factorial[1] * t2
                    + (3 * factorial[2] + 6 * factorial[1] ** 2) * t1
                    + 3 * t1 * t2
                    + 6 * factorial[1] * t1**2
                    + 2 * t1**3
                )
                self.assertGreater(min(t1, t2, t3), 0)
                self.assertLessEqual(variance_error, eta * amin)
                self.assertLessEqual(third_error**2, eta**2 * amin**3)
                self.assertEqual(
                    variance_error, exact(witness["polynomial_error_bounds"]["variance"])
                )
                self.assertEqual(
                    third_error, exact(witness["polynomial_error_bounds"]["third_cumulant"])
                )
                numerator = H * sum(
                    second[j] / exact(witness["raw_mean_tolerances"][str(j)]) ** 2
                    for j in (1, 2, 3)
                )
                unrounded = 20 * numerator
                count = (unrounded.numerator + unrounded.denominator - 1) // unrounded.denominator
                self.assertEqual(count, expected["new"])
                self.assertLess(count - 1, unrounded)
                self.assertLessEqual(unrounded, count)
                self.assertEqual(
                    numerator / count, exact(witness["new_total_individual_class_error_upper"])
                )
                self.assertLessEqual(numerator / count, Fraction(1, 20))
                self.assertEqual(
                    sum(
                        exact(witness["coordinate_individual_error_upper"][str(j)])
                        for j in (1, 2, 3)
                    ),
                    numerator / count,
                )
                threshold = exact(common["threshold_exact"])
                self.assertEqual(exact(witness["classifier"]["threshold"]), threshold)
                self.assertLess(exact(common["expanded_shape_intervals_exact"]["A"][1]), threshold)
                self.assertLess(threshold, exact(common["expanded_shape_intervals_exact"]["B"][0]))
                self.assertNotEqual(
                    common["threshold_exact"],
                    result["core_certificate"]["stages"]["counts"]["threshold_exact"],
                )

    def test_zero_exposure_recovery_and_unresolved_cap_refusal(self):
        core = exposure("exact_geometry")["core_certificate"]
        nominal, covariance = core["stages"]["nominal"], core["stages"]["covariance"]

        def require(ok, label):
            if not ok:
                raise ValueError(label)

        zero = linear_exposure_certificate(nominal, covariance, Fraction(0), require)
        for side in ("A", "B"):
            for field in ("normalized_variance", "normalized_third_cumulant", "skewness"):
                self.assertEqual(zero["classes"][side][field], covariance["classes"][side][field])
        for cap in (Fraction(-1), Fraction(1, 10000)):
            with self.subTest(cap=cap), self.assertRaises(ValueError):
                linear_exposure_certificate(nominal, covariance, cap, require)

    def test_saved_scope_witness_and_provenance_tampering_rejected(self):
        for scenario in self.scenarios:
            original = exposure(scenario)
            text = summary(original)
            self.assertIn("UNVERIFIED DISPLAY", text)
            self.assertIn("do not authenticate or recompute", text)
            self.assertIn("exposure <= 1e-5", text)
            self.assertIn("1e-20 core is a reference", text)
            for change in (
                "digest",
                "scenario",
                "core_scope",
                "new_scope",
                "count",
                "common_count",
                "tolerance",
                "baseline",
                "checks",
                "source_hash",
                "source_binding",
            ):
                with self.subTest(scenario=scenario, change=change):
                    modified = copy.deepcopy(original)
                    if change == "digest":
                        modified["core_certificate_sha256"] = "0" * 64
                    elif change == "scenario":
                        modified["scenario"] = "unknown"
                    elif change == "core_scope":
                        modified["core_certificate"]["parameters"]["frequency_error_cap_exact"] = (
                            "1"
                        )
                        modified["core_certificate_sha256"] = canonical_hash(
                            modified["core_certificate"]
                        )
                    elif change == "new_scope":
                        modified["extension"]["parameters"]["exposure_cap_exact"] = "1"
                    elif change == "count":
                        modified["coordinate_counts"]["sufficient_observation_windows"] = 1
                    elif change == "common_count":
                        modified["extension"]["stages"]["counts"][
                            "sufficient_observation_windows"
                        ] = 1
                    elif change == "tolerance":
                        modified["coordinate_counts"]["raw_mean_tolerances"]["1"]["exact"] = "1"
                    elif change == "baseline":
                        modified["coordinate_counts"]["comparison_baseline"] = (
                            "core_certificate.stages.counts"
                        )
                    elif change == "checks":
                        modified["checks"]["count"] = 0
                    else:
                        modified["source_revision"] = copy.deepcopy(verify_source_manifest())
                        if change == "source_hash":
                            modified["source_revision"]["manifest_sha256"] = "0" * 64
                        else:
                            modified["source_revision"]["bindings"]["exposure.py"] = "0" * 64
                    with self.assertRaises((ValueError, ArithmeticError, KeyError)):
                        summary(modified)
            compatible = copy.deepcopy(original)
            compatible["source_revision"] = verify_source_manifest()
            self.assertIn("UNVERIFIED DISPLAY", summary(compatible))

    def test_api_accepts_only_named_scenarios(self):
        for invalid in ("unknown", "all", {}, {"core_certificate": {}}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                build_exposure_certificate(invalid)

    def test_manifest_covers_exposure_source_and_rejects_local_drift(self):
        self.assertIn("exposure.py", MANIFEST_FILES)
        resource = resources.files("homometric_motion")
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            for name in MANIFEST_FILES | {"source_manifest.json"}:
                (folder / name).write_bytes(resource.joinpath(name).read_bytes())
            with mock.patch("homometric_motion.cli.files", return_value=folder):
                verify_source_manifest()
                with (folder / "exposure.py").open("ab") as stream:
                    stream.write(b"\n# local altered-source test fixture\n")
                with self.assertRaisesRegex(ValueError, "exposure.py"):
                    verify_source_manifest()

    def test_fresh_cli_both_scenarios_exclusive_outputs_and_saved_display(self):
        executable = os.environ.get("HM_TEST_PYTHON", sys.executable)
        for scenario, expected in self.scenarios.items():
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                folder = Path(temporary)
                output = folder / "exposure.json"
                command = [
                    executable,
                    "-I",
                    "-B",
                    "-m",
                    "homometric_motion",
                    "exposure-count",
                    "--scenario",
                    scenario,
                    "--output",
                    str(output),
                ]
                result = subprocess.run(
                    command, cwd=folder, capture_output=True, text=True, timeout=120, check=False
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"{expected['new']:,}", result.stdout)
                self.assertIn("freshly recomputed", result.stdout)
                self.assertIn("exposure <= 1e-5", result.stdout)
                raw = output.read_bytes()
                saved = json.loads(raw)
                self.assertEqual(saved.pop("source_revision"), verify_source_manifest())
                self.assertEqual(saved, exposure(scenario))
                rejected = subprocess.run(
                    command, cwd=folder, capture_output=True, text=True, timeout=30, check=False
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("output exists", rejected.stderr)
                self.assertEqual(output.read_bytes(), raw)
                display = subprocess.run(
                    [executable, "-I", "-B", "-m", "homometric_motion", "summary", str(output)],
                    cwd=folder,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    check=False,
                )
                self.assertEqual(display.returncode, 0, display.stderr)
                self.assertIn("UNVERIFIED DISPLAY", display.stdout)
                self.assertIn(f"{expected['new']:,}", display.stdout)
                self.assertEqual(set(folder.iterdir()), {output})


if __name__ == "__main__":
    unittest.main()
