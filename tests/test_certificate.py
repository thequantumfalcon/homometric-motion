"""Recreate the count bound from its scientific inputs, with exact arithmetic."""

import sys
import unittest
from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial

from homometric_motion import build_certificate
from homometric_motion.counts import classify
from homometric_motion.position import position_certificate


def fraction(text):
    """Read long exact fractions without changing the interpreter's digit guard."""
    if not isinstance(text, str):
        return F(text)

    def integer(value):
        sign = -1 if value.startswith("-") else 1
        digits = value.removeprefix("-")
        if not digits or not digits.isascii() or not digits.isdigit():
            raise ValueError("expected an integer")
        answer = 0
        for start in range(0, len(digits), 9):
            chunk = digits[start : start + 9]
            answer = answer * 10 ** len(chunk) + int(chunk)
        return sign * answer

    parts = text.split("/")
    if len(parts) == 1:
        return F(integer(parts[0]))
    if len(parts) == 2:
        return F(integer(parts[0]), integer(parts[1]))
    raise ValueError("expected an exact rational")


@lru_cache(maxsize=2)
def certificate(scenario="exact_geometry"):
    guard_before = sys.get_int_max_str_digits()
    result = build_certificate(scenario=scenario)
    if sys.get_int_max_str_digits() != guard_before:
        raise AssertionError("building a certificate changed the interpreter digit guard")
    return result


def independent_sqrt_lower(value, places=60):
    """Binary integer comparisons, independent of the runtime square-root helper."""
    scale = 10**places
    target = value.numerator * scale**2
    low, high = 0, 1
    while high**2 * value.denominator <= target:
        high *= 2
    while high - low > 1:
        middle = (low + high) // 2
        if middle**2 * value.denominator <= target:
            low = middle
        else:
            high = middle
    return F(low, scale)


class CertificateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = certificate()

    def test_exact_count_budget_from_detuned_moments(self):
        self.assert_count_budget(self.result, "frequency", 60, 975281623024726766278)

    def test_position_count_budget_from_its_own_moments(self):
        result = certificate("position_uncertainty")
        self.assert_count_budget(result, "position", 80, 975028627229038193209)
        counts = result["stages"]["counts"]
        self.assertEqual(counts["root_decimal_places"], 80)
        for record in counts["root_certificates"]:
            value = fraction(record["radicand"])
            lower = independent_sqrt_lower(value, places=80)
            upper = lower if lower**2 == value else lower + F(1, 10**80)
            self.assertEqual(fraction(record["lower"]), lower)
            self.assertEqual(fraction(record["upper"]), upper)
        eta = fraction(counts["eta_exact"])
        plus_lower = independent_sqrt_lower(1 + eta, places=80)
        plus_upper = plus_lower + F(1, 10**80)
        minus_lower = independent_sqrt_lower(1 - eta, places=80)
        for side in ("A", "B"):
            shape = result["stages"]["position"]["classes"][side]["skewness"]
            expected = [
                (fraction(shape["lower"]) - eta) / ((1 + eta) * plus_upper),
                (fraction(shape["upper"]) + eta) / ((1 - eta) * minus_lower),
            ]
            self.assertEqual(
                list(map(fraction, counts["expanded_shape_intervals_exact"][side])), expected
            )

    def assert_count_budget(self, result, observation_stage, places, expected_windows):
        stages = result["stages"]
        counts, frequency, nominal = (
            stages["counts"],
            stages[observation_stage],
            stages["nominal"],
        )
        classes = frequency["classes"]
        raw = {0: F(1)}
        raw.update(
            {
                order: max(
                    fraction(classes[side]["normalized_raw_moment_upper_bounds"][str(order)])
                    for side in ("A", "B")
                )
                for order in range(1, 7)
            }
        )
        hlow, hhigh = map(fraction, counts["h_interval_exact"])
        _, background = map(fraction, counts["b_interval_exact"])
        bounds = {
            order: sum(
                (
                    comb(order, k) * hhigh**k * background ** (order - k) * raw[k]
                    for k in range(order + 1)
                ),
                F(0),
            )
            for order in range(1, 7)
        }
        for order, value in bounds.items():
            self.assertEqual(fraction(counts["factorial_moment_upper_exact"][str(order)]), value)
        # (x)_j^2 = sum_k binom(j,k)^2 k! (x)_(2j-k).
        seconds = {
            order: sum(
                (
                    comb(order, k) ** 2 * factorial(k) * bounds[2 * order - k]
                    for k in range(order + 1)
                ),
                F(0),
            )
            for order in range(1, 4)
        }
        self.assertEqual(
            {
                int(k): fraction(v)
                for k, v in counts["raw_factorial_second_moment_upper_exact"].items()
            },
            seconds,
        )
        amin = hlow**2 * min(
            fraction(classes[side]["normalized_variance"]["lower"]) for side in ("A", "B")
        )
        self.assertEqual(fraction(counts["factorial_variance_lower_exact"]), amin)
        eta = fraction(counts["eta_exact"])
        l2 = 2 + 2 * bounds[1]
        l3 = 6 + 9 * bounds[1] + 3 * bounds[2] + 6 * bounds[1] ** 2
        tolerance = min(
            F(1), eta * amin / l2, eta * amin * independent_sqrt_lower(amin, places) / l3
        )
        self.assertEqual(fraction(counts["L2_exact"]), l2)
        self.assertEqual(fraction(counts["L3_exact"]), l3)
        self.assertEqual(fraction(counts["raw_moment_tolerance_exact"]), tolerance)
        self.assertLessEqual(l2 * tolerance, eta * amin)
        self.assertLessEqual((l3 * tolerance) ** 2, eta**2 * amin**3)
        epsilon = fraction(counts["epsilon_exact"])
        radius = epsilon / (1 + epsilon)
        trace = max(fraction(nominal["classes"][s]["trace_Lplus_exact"]) for s in ("A", "B"))
        gap = (1 - radius) / trace
        lag, exposure = map(fraction, (counts["lag_lower_exact"], counts["exposure_cap_exact"]))
        self.assertGreater(lag, exposure)
        inflation = 1 + 2 / (gap * (lag - exposure))
        self.assertEqual(fraction(counts["spectral_gap_lower_exact"]), gap)
        self.assertEqual(fraction(counts["window_variance_inflation_upper_exact"]), inflation)
        numerator = inflation * sum(seconds.values()) / tolerance**2
        target = fraction(result["parameters"]["target_individual_class_error"])
        real_budget = numerator / target
        windows = -(-real_budget.numerator // real_budget.denominator)
        self.assertEqual(counts["sufficient_observation_windows"], windows)
        self.assertEqual(fraction(counts["unrounded_window_budget_exact"]), real_budget)
        self.assertLess(windows - 1, real_budget)
        self.assertGreaterEqual(windows, real_budget)
        self.assertEqual(
            fraction(counts["individual_class_error_upper_exact"]), numerator / windows
        )
        self.assertLessEqual(numerator / windows, F(1, 20))
        # Regression target for this explicitly fixed theorem, not an optimal cost.
        self.assertEqual(windows, expected_windows)

    def test_expanded_shape_enclosures_and_class_ordering(self):
        for scenario, stage in (
            ("exact_geometry", "frequency"),
            ("position_uncertainty", "position"),
        ):
            with self.subTest(scenario=scenario):
                self.assert_expanded_shape(certificate(scenario), stage)

    def assert_expanded_shape(self, result, observation_stage):
        counts = result["stages"]["counts"]
        classes = result["stages"][observation_stage]["classes"]
        eta = fraction(counts["eta_exact"])
        expanded = {}
        for side in ("A", "B"):
            lo, hi = map(fraction, counts["expanded_shape_intervals_exact"][side])
            rlo = fraction(classes[side]["skewness"]["lower"])
            rhi = fraction(classes[side]["skewness"]["upper"])
            self.assertGreater(rlo - eta, 0)
            self.assertGreater(lo, 0)
            # Square positive quantities to check fractional powers exactly.
            self.assertLessEqual(lo**2 * (1 + eta) ** 3, (rlo - eta) ** 2)
            self.assertGreaterEqual(hi**2 * (1 - eta) ** 3, (rhi + eta) ** 2)
            expanded[side] = lo, hi
        self.assertLess(expanded["A"][1], expanded["B"][0])
        threshold = fraction(counts["threshold_exact"])
        self.assertEqual(threshold, (expanded["A"][1] + expanded["B"][0]) / 2)

    def test_positive_strength_floor_and_fixed_parameter_contract(self):
        parameters = self.result["parameters"]
        cap = fraction(parameters["beta_cap_exact"])
        band = parameters["beta_band_exact"]
        self.assertEqual(fraction(band["lower"]), cap / 2)
        self.assertEqual(fraction(band["upper"]), cap)
        self.assertGreater(cap, 0)
        self.assertEqual(fraction(parameters["frequency_error_cap_exact"]), F(1, 10**14))
        self.assertEqual(fraction(parameters["edge_weight_radius_exact"]), F(1, 100001))
        self.assertEqual(self.result["revision_kind"], "release_adaptation")
        self.assertEqual(self.result["checks"]["count"], len(self.result["checks"]["passed"]))
        self.assertTrue(self.result["limitations"])
        self.assertEqual(self.result["scenario"], "exact_geometry")
        self.assertEqual(fraction(parameters["position_error_cap_exact"]), 0)

    def test_position_zero_limit_topology_and_changed_mean_bound(self):
        result = certificate("position_uncertainty")
        stages = result["stages"]
        parameters = result["parameters"]
        rho = fraction(parameters["position_error_cap_exact"])
        self.assertEqual(rho, F(1, 10**14))
        self.assertEqual(fraction(parameters["frequency_error_cap_exact"]), F(1, 10**16))
        self.assertEqual(
            parameters["beta_band_exact"], self.result["parameters"]["beta_band_exact"]
        )
        row = stages["position"]
        self.assertEqual(fraction(row["mean_contact_threshold_exact"]), F(5, 2))
        margin = fraction(row["mean_contact_remaining_margin_strict_lower_exact"])
        self.assertEqual(margin, F(1, 4) - 2 * rho)
        self.assertGreater(margin, 0)
        self.assertIn("need not remain clean-homometric", row["scope"])
        messages = []

        def check(condition, label):
            self.assertTrue(condition, label)
            messages.append(label)

        zero = position_certificate(
            stages["exposure"], stages["nominal"], stages["frequency"], F(0), check
        )
        self.assertTrue(messages)
        for side in ("A", "B"):
            for name in (
                "normalized_variance",
                "normalized_third_cumulant",
                "skewness",
                "normalized_raw_moment_upper_bounds",
            ):
                self.assertEqual(
                    zero["classes"][side][name], stages["frequency"]["classes"][side][name]
                )
            saved = row["classes"][side]
            qpos = fraction(row["position_amplitude_error_coefficient_upper_exact"]) * rho
            qtotal = fraction(saved["frequency_amplitude_L6_error_upper_exact"]) + qpos
            p = fraction(saved["nominal_amplitude_L6_upper_exact"])
            delta = 2 * p * qtotal + qtotal**2
            self.assertEqual(fraction(saved["position_amplitude_error_upper_exact"]), qpos)
            self.assertEqual(fraction(saved["total_intensity_L3_error_upper_exact"]), delta)
            self.assertEqual(fraction(saved["centered_L3_error_upper_exact"]), 2 * delta)
            # Changed means require the L3 centering factor two.
            m = fraction(saved["baseline_centered_L3_upper_exact"])
            error = 3 * m**2 * (2 * delta) + 3 * m * (2 * delta) ** 2 + (2 * delta) ** 3
            self.assertEqual(fraction(saved["third_cumulant_change_upper_exact"]), error)
        with self.assertRaises(ValueError):
            build_certificate(scenario="all")

    def test_exact_classifier_threshold_and_fallbacks(self):
        threshold = fraction(self.result["stages"]["counts"]["threshold_exact"])
        tiny = F(1, 10**80)
        # a=scale^2 and c=shape*scale^3 model gain transformations exactly.
        for mean in (F(1), F(1000)):
            for scale in (F(1, 7), F(3)):
                variance = scale**2
                f2 = mean**2 + variance
                for shape, expected in (
                    (threshold - tiny, "A"),
                    (threshold, "B"),
                    (threshold + tiny, "B"),
                    (-threshold, "A"),
                ):
                    f3 = shape * scale**3 + 3 * mean * f2 - 2 * mean**3
                    self.assertEqual(classify(mean, f2, f3, threshold), expected)
        self.assertEqual(classify(F(1), F(1), F(100), threshold), "A")
        self.assertEqual(classify(F(2), F(1), F(100), threshold), "A")

    def test_population_poisson_mixture_gain_background_invariance(self):
        """Finite latent laws verify the invariant, not a finite-sample budget."""
        threshold = fraction(self.result["stages"]["counts"]["threshold_exact"])
        models = (
            ([(F(0), F(1, 2)), (F(1), F(1, 3)), (F(4), F(1, 6))], "A"),
            ([(F(0), F(99, 100)), (F(1), F(1, 100))], "B"),
        )
        for support, expected in models:
            raw = {k: sum(probability * x**k for x, probability in support) for k in (1, 2, 3)}
            variance = raw[2] - raw[1] ** 2
            third = raw[3] - 3 * raw[1] * raw[2] + 2 * raw[1] ** 3
            for gain in (F(1, 10), F(1), F(10)):
                for background in (F(0), F(1), F(100)):
                    # A conditional Poisson law has factorial moments lambda^k.
                    moments = {
                        k: sum(
                            probability * (gain * x + background) ** k for x, probability in support
                        )
                        for k in (1, 2, 3)
                    }
                    a = moments[2] - moments[1] ** 2
                    c = moments[3] - 3 * moments[1] * moments[2] + 2 * moments[1] ** 3
                    self.assertEqual(a, gain**2 * variance)
                    self.assertEqual(c, gain**3 * third)
                    self.assertEqual(
                        classify(moments[1], moments[2], moments[3], threshold), expected
                    )


if __name__ == "__main__":
    unittest.main()
