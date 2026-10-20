"""Independent endpoint and risk checks for explicit versioned profiles."""

import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial
from pathlib import Path

from test_certificate import certificate, fraction

from homometric_motion import build_count_certificate
from homometric_motion.allocation import allocate_shape_budget
from homometric_motion.cli import summary, verify_source_manifest
from homometric_motion.kernel import kernel_exposure_certificate
from homometric_motion.kernel_arithmetic import KernelInterval
from homometric_motion.kernel_observation import kernel_observation_certificate
from homometric_motion.profiles import validate_saved_count

EXPECTED = {
    ("short-exposure-v1", "exact_geometry"): (69803163290068, F(1, 100000)),
    ("short-exposure-v1", "position_uncertainty"): (5362340030851, F(1, 100000)),
    ("long-exposure-v1", "exact_geometry"): (36938105282195, F(1, 1000)),
    ("long-exposure-v1", "position_uncertainty"): (16852383428868, F(1, 100)),
}


@lru_cache(maxsize=4)
def profile_result(profile, scenario):
    guard = sys.get_int_max_str_digits()
    result = build_count_certificate(profile=profile, scenario=scenario)
    if sys.get_int_max_str_digits() != guard:
        raise AssertionError("profile changed the interpreter's integer digit guard")
    return result


def exact(record):
    return fraction(record["exact"])


class ProfileTests(unittest.TestCase):
    def test_evaluated_extra_domain_and_unresolved_refusal(self):
        def require(ok, label):
            if not ok:
                raise ValueError(label)

        for scenario, cap in (
            ("position_uncertainty", F(1, 1000)),
            ("exact_geometry", F(1, 100)),
        ):
            with self.subTest(scenario=scenario, cap=cap):
                core = certificate(scenario)
                nominal, covariance = core["stages"]["nominal"], core["stages"]["covariance"]
                parameters = copy.deepcopy(core["parameters"])
                parameters.pop("eta_exact")
                parameters.update(scenario=scenario, exposure_cap_exact=str(cap))
                moment = kernel_exposure_certificate(nominal, covariance, cap, require)
                evidence = kernel_observation_certificate(
                    moment, nominal, covariance, parameters, require
                )
                observed = evidence["observation_union"]
                if scenario == "position_uncertainty":
                    self.assertEqual(evidence["status"], "CERTIFIED_SEPARATED")
                    allocation = allocate_shape_budget(observed, nominal, parameters, require)
                    self.assertEqual(allocation["sufficient_observation_windows"], 4404373875964)
                    self.assertLessEqual(
                        exact(allocation["individual_class_error_upper"]), F(1, 20)
                    )
                else:
                    self.assertEqual(evidence["status"], "UNRESOLVED_BY_THIS_BOUND")
                    self.assertEqual(len(evidence["deferred_terminal_gates"]), 89)
                    self.assertLessEqual(fraction(observed["signed_gap_exact"]), 0)
                    self.assertNotIn("allocation", evidence)
                    with self.assertRaisesRegex(ValueError, "separated observation"):
                        allocate_shape_budget(observed, nominal, parameters, require)

    def test_independent_polynomial_shape_threshold_and_risk_reconstruction(self):
        for (profile, scenario), (expected, cap) in EXPECTED.items():
            with self.subTest(profile=profile, scenario=scenario):
                result = profile_result(profile, scenario)
                self.assertEqual(result["core_certificate"], certificate(scenario))
                params, observed = result["parameters"], result["observation_bounds"]
                allocation = result["allocation"]
                self.assertNotIn("eta_exact", params)
                self.assertEqual(F(params["exposure_cap_exact"]), cap)
                self.assertEqual(F(observed["exposure_cap_exact"]), cap)
                self.assertEqual(allocation["sufficient_observation_windows"], expected)
                self.assertEqual(result["checks"]["count"], len(result["checks"]["passed"]))
                raw = {0: F(1)}
                raw.update(
                    {
                        k: max(
                            fraction(
                                observed["classes"][side]["normalized_raw_moment_upper_bounds"][
                                    str(k)
                                ]
                            )
                            for side in ("A", "B")
                        )
                        for k in range(1, 7)
                    }
                )
                fm = {
                    k: sum(comb(k, j) * F(11, 10) ** j * raw[j] for j in range(k + 1))
                    for k in range(1, 7)
                }
                second = {
                    k: sum(comb(k, j) ** 2 * factorial(j) * fm[2 * k - j] for j in range(k + 1))
                    for k in (1, 2, 3)
                }
                amin = F(9, 10) ** 2 * min(
                    fraction(observed["classes"][side]["normalized_variance"]["lower"])
                    for side in ("A", "B")
                )
                amax = F(11, 10) ** 2 * max(
                    fraction(observed["classes"][side]["normalized_variance"]["upper"])
                    for side in ("A", "B")
                )
                self.assertGreater(amin, 0)
                self.assertLessEqual(amin, amax)
                coefficient = 3 * max(amax, fm[1] ** 2 - amin)
                self.assertEqual(
                    coefficient,
                    exact(allocation["cancellation_sensitivity"]["new_linear_coefficient"]),
                )
                t1, t2, t3 = (exact(allocation["raw_mean_tolerances"][str(k)]) for k in (1, 2, 3))
                self.assertGreater(min(t1, t2, t3), 0)
                e2 = t2 + 2 * fm[1] * t1 + t1**2
                e3 = (
                    t3
                    + 3 * fm[1] * t2
                    + coefficient * t1
                    + 3 * t1 * t2
                    + 6 * fm[1] * t1**2
                    + 2 * t1**3
                )
                u, v = (
                    exact(allocation["relative_variance_error"]),
                    exact(allocation["relative_third_error"]),
                )
                self.assertEqual(e2, exact(allocation["polynomial_errors"]["variance"]))
                self.assertEqual(e3, exact(allocation["polynomial_errors"]["third"]))
                self.assertEqual(e2, u * amin)
                self.assertLessEqual(e3**2, v**2 * amin**3)
                self.assertTrue(0 < u < 1 and v > 0)
                threshold = fraction(allocation["threshold_exact"])
                self.assertEqual(threshold, fraction(allocation["classifier"]["threshold_exact"]))
                endpoints = {}
                for side in ("A", "B"):
                    lower, upper = map(fraction, allocation["expanded_shapes"][side])
                    shape = observed["classes"][side]["skewness"]
                    sl, su = fraction(shape["lower"]), fraction(shape["upper"])
                    self.assertTrue(0 < lower <= upper and v < sl)
                    self.assertLessEqual(lower**2 * (1 + u) ** 3, (sl - v) ** 2)
                    self.assertGreaterEqual(upper**2 * (1 - u) ** 3, (su + v) ** 2)
                    endpoints[side] = (lower, upper)
                self.assertLess(endpoints["A"][1], threshold)
                self.assertLess(threshold, endpoints["B"][0])
                self.assertEqual(threshold, (endpoints["A"][1] + endpoints["B"][0]) / 2)
                trace = max(
                    fraction(
                        result["core_certificate"]["stages"]["nominal"]["classes"][side][
                            "trace_Lplus_exact"
                        ]
                    )
                    for side in ("A", "B")
                )
                gamma = 1 / ((1 + F(1, 100000)) * trace)
                inflation = 1 + 2 / (gamma * (1000 - cap))
                numerator = inflation * sum(
                    second[k] / exact(allocation["raw_mean_tolerances"][str(k)]) ** 2
                    for k in (1, 2, 3)
                )
                budget = 20 * numerator
                self.assertLess(expected - 1, budget)
                self.assertLessEqual(budget, expected)
                self.assertEqual(budget, fraction(allocation["unrounded_count_exact"]))
                self.assertEqual(
                    numerator / expected, exact(allocation["individual_class_error_upper"])
                )
                self.assertLessEqual(numerator / expected, F(1, 20))
                for root in allocation["root_certificates"]:
                    degree = root["degree"]
                    value = fraction(root["radicand"])
                    lo, hi = fraction(root["lower"]), fraction(root["upper"])
                    self.assertLessEqual(lo**degree, value)
                    self.assertLessEqual(value, hi**degree)

    def test_long_profile_complete_cells_and_independent_class_extrema(self):
        for scenario in ("exact_geometry", "position_uncertainty"):
            result = profile_result("long-exposure-v1", scenario)
            cap = F(result["parameters"]["exposure_cap_exact"])
            nuisance = result["nuisance_evidence"]
            self.assertEqual(nuisance["status"], "CERTIFIED_SEPARATED")
            self.assertEqual(nuisance["deferred_terminal_gates"], [])
            cells = nuisance["time_cells"]
            self.assertEqual(len(cells), 512)
            kind = "frequency" if scenario == "exact_geometry" else "position"
            for index, cell in enumerate(cells):
                self.assertEqual(cell["index"], index)
                self.assertEqual(
                    list(map(fraction, cell["time_interval_exact"])),
                    [cap * index / 512, cap * (index + 1) / 512],
                )
            for side in ("A", "B"):
                lower = min(
                    fraction(cell[kind]["classes"][side]["skewness"]["lower"]) for cell in cells
                )
                upper = max(
                    fraction(cell[kind]["classes"][side]["skewness"]["upper"]) for cell in cells
                )
                union = result["observation_bounds"]["classes"][side]["skewness"]
                self.assertEqual(
                    [fraction(union["lower"]), fraction(union["upper"])], [lower, upper]
                )
            # The class extrema may occur in different cells; no paired-index
            # classification assertion is used to obtain this global gap.
            global_gap = fraction(
                result["observation_bounds"]["classes"]["B"]["skewness"]["lower"]
            ) - fraction(result["observation_bounds"]["classes"]["A"]["skewness"]["upper"])
            self.assertGreater(global_gap, 0)

    def test_explicit_profile_api_and_no_arbitrary_parameter_hybrids(self):
        for invalid in ("best", "", {}, None, "long-exposure-v2"):
            with self.subTest(profile=invalid), self.assertRaises(ValueError):
                build_count_certificate(profile=invalid)
        for invalid in ("unknown", {}, None):
            with self.subTest(scenario=invalid), self.assertRaises(ValueError):
                build_count_certificate(profile="long-exposure-v1", scenario=invalid)
        with self.assertRaises(TypeError):
            build_count_certificate()
        with self.assertRaises(TypeError):
            build_count_certificate(profile="long-exposure-v1", exposure_cap=F(1, 100))

    def test_saved_profile_contract_and_witness_tampering(self):
        original = profile_result("short-exposure-v1", "exact_geometry")
        for field in (
            "schema",
            "profile",
            "scenario",
            "digest",
            "encoding",
            "parameters",
            "eta",
            "count",
            "threshold",
            "disclosure",
        ):
            changed = copy.deepcopy(original)
            if field == "schema":
                changed["schema_version"] = 2
            elif field == "profile":
                changed["profile"] = "best"
            elif field == "scenario":
                changed["scenario"] = "position_uncertainty"
            elif field == "digest":
                changed["core_certificate_sha256"] = "0" * 64
            elif field == "encoding":
                changed["core_digest_encoding"] = "not canonical"
            elif field == "parameters":
                changed["parameters"]["exposure_cap_exact"] = "1/100"
            elif field == "eta":
                changed["parameters"]["eta_exact"] = "1/100000"
            elif field == "count":
                changed["allocation"]["sufficient_observation_windows"] = 1
            elif field == "threshold":
                changed["allocation"]["threshold_exact"] = "1"
            else:
                changed["qualification"] = "physical proof"
            with self.subTest(field=field), self.assertRaises((ValueError, ArithmeticError)):
                validate_saved_count(changed)
        display = summary(original)
        self.assertIn("UNVERIFIED DISPLAY", display)
        self.assertIn("do not authenticate", display)
        drifted = copy.deepcopy(original)
        drifted["source_revision"] = copy.deepcopy(verify_source_manifest())
        drifted["source_revision"]["bindings"]["profiles.py"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "provenance"):
            summary(drifted)

    def test_cli_requires_profile_and_preserves_exclusive_output(self):
        executable = os.environ.get("HM_TEST_PYTHON", sys.executable)
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            target = directory / "count.json"
            base = [
                executable,
                "-I",
                "-B",
                "-m",
                "homometric_motion",
                "count",
                "--output",
                str(target),
            ]
            missing = subprocess.run(
                base, cwd=directory, capture_output=True, text=True, timeout=30, check=False
            )
            self.assertNotEqual(missing.returncode, 0)
            self.assertFalse(target.exists())
            command = base + ["--profile", "short-exposure-v1"]
            created = subprocess.run(
                command, cwd=directory, capture_output=True, text=True, timeout=180, check=False
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.assertIn("69,803,163,290,068", created.stdout)
            self.assertIn("freshly recomputed", created.stdout)
            raw = target.read_bytes()
            saved = json.loads(raw)
            self.assertEqual(saved.pop("source_revision"), verify_source_manifest())
            self.assertEqual(saved, profile_result("short-exposure-v1", "exact_geometry"))
            again = subprocess.run(
                command, cwd=directory, capture_output=True, text=True, timeout=30, check=False
            )
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(target.read_bytes(), raw)
            self.assertEqual(set(directory.iterdir()), {target})

    def test_kernel_interval_outward_signs_roots_and_domain_failures(self):
        for a, b, c, d in ((-3, 2, 1, 4), (-3, -1, -5, -2), (F(1, 7), F(2, 3), -2, 3)):
            x, y = KernelInterval(a, b), KernelInterval(c, d)
            product = x * y
            for exact_product in (a * c, a * d, b * c, b * d):
                self.assertLessEqual(product.lo, exact_product)
                self.assertLessEqual(exact_product, product.hi)
            square = x**2
            self.assertLessEqual(square.lo, min(a * a, b * b, F(0) if a <= 0 <= b else a * a))
            self.assertGreaterEqual(square.hi, max(a * a, b * b))
        for degree in (2, 3, 4, 6):
            radicand = KernelInterval(F(1, 7), F(11, 3))
            root = radicand.root(degree)
            self.assertLessEqual(root.lo**degree, F(1, 7))
            self.assertGreaterEqual(root.hi**degree, F(11, 3))
        with self.assertRaises(ValueError):
            KernelInterval(2, 1)
        with self.assertRaises(ZeroDivisionError):
            KernelInterval(1) / KernelInterval(-1, 1)
        for degree in (0, -1, F(1, 2)):
            with self.subTest(degree=degree), self.assertRaises(ValueError):
                KernelInterval(1).root(degree)
        with self.assertRaises(ValueError):
            KernelInterval(-1).root(2)


if __name__ == "__main__":
    unittest.main()
