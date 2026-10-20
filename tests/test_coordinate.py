"""Installed-artifact checks for the separate coordinate-tolerance proof."""

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
from homometric_motion import build_certificate, build_coordinate_certificate
from homometric_motion.cli import MANIFEST_FILES, summary, verify_source_manifest


def exact(value):
    """Parse arbitrary-size decimal fractions independently of the package."""
    if isinstance(value, dict):
        value = value["exact"]
    if isinstance(value, int):
        return Fraction(value)

    def integer(part):
        sign = -1 if part.startswith("-") else 1
        part = part.removeprefix("-")
        result = 0
        for start in range(0, len(part), 7):
            group = part[start : start + 7]
            result = result * 10 ** len(group) + int(group)
        return sign * result

    pieces = value.split("/")
    return Fraction(integer(pieces[0]), integer(pieces[1]) if len(pieces) == 2 else 1)


def canonical_hash(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()


@lru_cache(maxsize=2)
def extension(scenario):
    return build_coordinate_certificate(scenario)


class CoordinateTests(unittest.TestCase):
    scenarios = {
        "exact_geometry": (26814048499063502, 975281623024726766278),
        "position_uncertainty": (26808243624540316, 975028627229038193209),
    }

    @classmethod
    def setUpClass(cls):
        source = Path(__file__).resolve().parents[1] / "src"
        package = Path(homometric_motion.__file__).resolve()
        if package.is_relative_to(source) or "site-packages" not in package.parts:
            raise AssertionError("coordinate tests must run against an installed wheel")
        if metadata.version("homometric-motion") != homometric_motion.__version__:
            raise AssertionError("installed distribution version mismatch")

    def test_separate_envelope_preserves_fresh_core(self):
        guard = sys.get_int_max_str_digits()
        for scenario, (expected, previous) in self.scenarios.items():
            with self.subTest(scenario=scenario):
                result = extension(scenario)
                core = result["core_certificate"]
                witness = result["coordinate_counts"]
                self.assertEqual(core, build_certificate(scenario))
                self.assertNotIn("certificate_kind", core)
                self.assertEqual(result["certificate_kind"], "coordinate_count_extension")
                self.assertEqual(result["core_certificate_sha256"], canonical_hash(core))
                self.assertEqual(witness["parameters_unchanged"], core["parameters"])
                self.assertEqual(witness["sufficient_observation_windows"], expected)
                self.assertEqual(
                    core["stages"]["counts"]["sufficient_observation_windows"], previous
                )
                self.assertEqual(witness["previous_sufficient_observation_windows"], previous)
                self.assertIn("No blind selection", result["selection_disclosure"])
                self.assertEqual(sys.get_int_max_str_digits(), guard)

    def test_full_polynomial_constraints_and_exact_coordinate_union_risk(self):
        for scenario, (expected, _) in self.scenarios.items():
            with self.subTest(scenario=scenario):
                result = extension(scenario)
                core, witness = result["core_certificate"], result["coordinate_counts"]
                selected = core["stages"][
                    "position" if scenario == "position_uncertainty" else "frequency"
                ]
                raw = [Fraction(1)] + [
                    max(
                        exact(
                            selected["classes"][side]["normalized_raw_moment_upper_bounds"][str(j)]
                        )
                        for side in ("A", "B")
                    )
                    for j in range(1, 7)
                ]
                moments = {
                    j: sum(comb(j, k) * Fraction(11, 10) ** k * raw[k] for k in range(j + 1))
                    for j in range(1, 7)
                }
                seconds = {
                    1: moments[2] + moments[1],
                    2: moments[4] + 4 * moments[3] + 2 * moments[2],
                    3: moments[6] + 9 * moments[5] + 18 * moments[4] + 6 * moments[3],
                }
                amin = Fraction(81, 100) * min(
                    exact(selected["classes"][side]["normalized_variance"]["lower"])
                    for side in ("A", "B")
                )
                eta = Fraction(1, 100000)
                t1, t2, t3 = (exact(witness["raw_mean_tolerances"][str(j)]) for j in (1, 2, 3))
                variance_error = t2 + 2 * moments[1] * t1 + t1 * t1
                third_error = (
                    t3
                    + 3 * moments[1] * t2
                    + (3 * moments[2] + 6 * moments[1] ** 2) * t1
                    + 3 * t1 * t2
                    + 6 * moments[1] * t1 * t1
                    + 2 * t1**3
                )
                self.assertGreater(min(t1, t2, t3), 0)
                self.assertLessEqual(variance_error, eta * amin)
                self.assertLessEqual(third_error**2, eta**2 * amin**3)
                self.assertEqual(
                    third_error, exact(witness["polynomial_error_bounds"]["third_cumulant"])
                )
                lower_root = exact(witness["inputs"]["sqrt_variance_lower"])
                step = Fraction(1, 10 ** (80 if scenario == "position_uncertainty" else 60))
                self.assertLessEqual(lower_root**2, amin)
                self.assertLess(amin, (lower_root + step) ** 2)
                H = exact(core["stages"]["counts"]["window_variance_inflation_upper_exact"])
                numerator = H * sum(
                    seconds[j] / exact(witness["raw_mean_tolerances"][str(j)]) ** 2
                    for j in (1, 2, 3)
                )
                budget = 20 * numerator
                count = (budget.numerator + budget.denominator - 1) // budget.denominator
                self.assertEqual(count, expected)
                self.assertLess(count - 1, budget)
                self.assertLessEqual(budget, count)
                self.assertLessEqual(numerator / count, Fraction(1, 20))
                self.assertEqual(
                    numerator / count, exact(witness["new_total_individual_class_error_upper"])
                )
                self.assertEqual(
                    sum(
                        exact(witness["coordinate_individual_error_upper"][str(j)])
                        for j in (1, 2, 3)
                    ),
                    numerator / count,
                )
                threshold = exact(core["stages"]["counts"]["threshold_exact"])
                self.assertEqual(exact(witness["classifier"]["threshold"]), threshold)
                self.assertLess(
                    exact(witness["classifier"]["shape_endpoints"]["A"]["expanded"][1]),
                    threshold,
                )
                self.assertGreater(
                    exact(witness["classifier"]["shape_endpoints"]["B"]["expanded"][0]),
                    threshold,
                )

    def test_saved_display_rejects_tampering_and_remains_unverified(self):
        for scenario in self.scenarios:
            original = extension(scenario)
            text = summary(original)
            self.assertIn("UNVERIFIED DISPLAY", text)
            self.assertIn("do not authenticate or recompute the core model", text)
            for change in ("digest", "count", "tolerance", "scenario", "core_scope", "checks"):
                with self.subTest(scenario=scenario, change=change):
                    modified = copy.deepcopy(original)
                    if change == "digest":
                        modified["core_certificate_sha256"] = "0" * 64
                    elif change == "count":
                        modified["coordinate_counts"]["sufficient_observation_windows"] = 1
                    elif change == "tolerance":
                        modified["coordinate_counts"]["raw_mean_tolerances"]["3"]["exact"] = "1"
                    elif change == "scenario":
                        modified["scenario"] = "unknown"
                    elif change == "core_scope":
                        modified["core_certificate"]["parameters"]["frequency_error_cap_exact"] = (
                            "1"
                        )
                        modified["core_certificate_sha256"] = canonical_hash(
                            modified["core_certificate"]
                        )
                    else:
                        modified["checks"]["count"] = 0
                    with self.assertRaises((ValueError, ArithmeticError, KeyError)):
                        summary(modified)

    def test_computing_api_accepts_only_named_scenarios(self):
        for invalid in ("unknown", "all", {}, {"core_certificate": {}}):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                build_coordinate_certificate(invalid)

    def test_manifest_covers_new_coordinate_source(self):
        self.assertIn("coordinate.py", MANIFEST_FILES)
        resource = resources.files("homometric_motion")
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            for name in MANIFEST_FILES | {"source_manifest.json"}:
                (directory / name).write_bytes(resource.joinpath(name).read_bytes())
            with mock.patch("homometric_motion.cli.files", return_value=directory):
                verify_source_manifest()
                with (directory / "coordinate.py").open("ab") as stream:
                    stream.write(b"\n# changed local test fixture\n")
                with self.assertRaisesRegex(ValueError, "coordinate.py"):
                    verify_source_manifest()

    def test_fresh_cli_replays_both_scenarios_and_refuses_existing_output(self):
        executable = os.environ.get("HM_TEST_PYTHON", sys.executable)
        for scenario, (expected, _) in self.scenarios.items():
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temporary:
                directory = Path(temporary)
                output = directory / "coordinate.json"
                command = [
                    executable,
                    "-I",
                    "-B",
                    "-m",
                    "homometric_motion",
                    "coordinate-count",
                    "--scenario",
                    scenario,
                    "--output",
                    str(output),
                ]
                result = subprocess.run(
                    command, cwd=directory, capture_output=True, text=True, timeout=120, check=False
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"{expected:,}", result.stdout)
                self.assertIn("freshly recomputed", result.stdout)
                raw = output.read_bytes()
                saved = json.loads(raw)
                self.assertEqual(saved.pop("source_revision"), verify_source_manifest())
                self.assertEqual(saved, extension(scenario))
                rejected = subprocess.run(
                    command, cwd=directory, capture_output=True, text=True, timeout=30, check=False
                )
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("output exists", rejected.stderr)
                self.assertEqual(output.read_bytes(), raw)
                displayed = subprocess.run(
                    [executable, "-I", "-B", "-m", "homometric_motion", "summary", str(output)],
                    cwd=directory,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                )
                self.assertEqual(displayed.returncode, 0, displayed.stderr)
                self.assertIn("UNVERIFIED DISPLAY", displayed.stdout)
                self.assertIn(f"{expected:,}", displayed.stdout)
                self.assertEqual(set(directory.iterdir()), {output})


if __name__ == "__main__":
    unittest.main()
