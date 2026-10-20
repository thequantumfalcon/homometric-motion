"""Independent witnesses and installed-interface tests for the fixed nine-point pair."""

import copy
import hashlib
import inspect
import io
import itertools
import json
import os
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stderr
from fractions import Fraction as F
from functools import lru_cache
from math import comb, factorial, lcm
from pathlib import Path
from unittest.mock import patch

import homometric_motion
from homometric_motion import build_small_pair_certificate
from homometric_motion.cli import main, summary, verify_source_manifest
from homometric_motion.smallpair import validate_saved_small_pair

MODULES = {
    "smallpair.py",
    "smallpair_algebra.py",
    "smallpair_bounds.py",
    "smallpair_geometry.py",
    "smallpair_mean.py",
    "smallpair_moments.py",
    "smallpair_strength.py",
}


def fraction(text):
    """Read exact decimal chunks locally, without using runtime arithmetic helpers."""
    if not isinstance(text, str):
        return F(text)

    def integer(value):
        sign = -1 if value.startswith("-") else 1
        digits = value.removeprefix("-")
        if not digits or not digits.isascii() or not digits.isdigit():
            raise ValueError("expected an exact integer")
        result = 0
        for start in range(0, len(digits), 9):
            part = digits[start : start + 9]
            result = result * 10 ** len(part) + int(part)
        return sign * result

    parts = text.split("/")
    if len(parts) not in (1, 2):
        raise ValueError("expected an exact rational")
    return F(integer(parts[0]), integer(parts[1]) if len(parts) == 2 else 1)


@lru_cache(maxsize=1)
def certificate():
    guard = sys.get_int_max_str_digits()
    result = build_small_pair_certificate()
    if sys.get_int_max_str_digits() != guard:
        raise AssertionError("certificate construction changed the integer conversion guard")
    return result


def trim(values):
    out = list(values)
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def add(a, b, scale=1):
    return trim(
        [
            (a[k] if k < len(a) else 0) + scale * (b[k] if k < len(b) else 0)
            for k in range(max(len(a), len(b)))
        ]
    )


def multiply(a, b):
    # Coefficient-wise antidiagonal sums, independent of runtime convolution.
    return trim(
        [
            sum(a[i] * b[k - i] for i in range(max(0, k - len(b) + 1), min(k, len(a) - 1) + 1))
            for k in range(len(a) + len(b) - 1)
        ]
    )


def power(poly, exponent):
    result = [1]
    for _ in range(exponent):
        result = multiply(result, poly)
    return result


def evaluate(poly, value):
    result = F(0)
    for coefficient in reversed(poly):
        result = result * value + coefficient
    return result


def divide(a, b):
    remainder = list(map(F, a))
    divisor = trim(list(map(F, b)))
    if divisor == [0]:
        raise ZeroDivisionError("zero polynomial divisor")
    if len(remainder) < len(divisor):
        return [F(0)], trim(remainder)
    quotient = [F(0)] * (len(remainder) - len(divisor) + 1)
    for index in reversed(range(len(quotient))):
        quotient[index] = remainder[index + len(divisor) - 1] / divisor[-1]
        for j, value in enumerate(divisor):
            remainder[index + j] -= quotient[index] * value
    return trim(quotient), trim(remainder)


def inverse(matrix):
    size = len(matrix)
    rows = [list(map(F, row)) + [F(i == j) for j in range(size)] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = next(i for i in range(col, size) if rows[i][col])
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [value / scale for value in rows[col]]
        for i in range(size):
            if i != col:
                multiple = rows[i][col]
                rows[i] = [x - multiple * y for x, y in zip(rows[i], rows[col])]
    return [row[size:] for row in rows]


def covariance_from_bordered_inverse(points):
    n = len(points)
    laplacian = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i):
            if 2 * abs(points[i] - points[j]) < 15:
                laplacian[i][i] += 1
                laplacian[j][j] += 1
                laplacian[i][j] = laplacian[j][i] = -1
    shifted = [[F(value) + F(1, n) for value in row] for row in laplacian]
    plus = [[value - F(1, n) for value in row] for row in inverse(shifted)]
    trace = sum(plus[i][i] for i in range(n))
    covariance = [[n * value / trace for value in row] for row in plus]
    return laplacian, plus, trace, covariance


def ordered_moment(points, covariance, order):
    phases = ((1, 0), (0, 1), (-1, -1))  # Z[zeta], zeta^2=-1-zeta
    coefficients = {}
    for indices in itertools.product(range(9), repeat=2 * order):
        signs = [1 if i % 2 == 0 else -1 for i in range(2 * order)]
        variogram = sum(
            signs[i] * signs[j] * covariance[indices[i]][indices[j]]
            for i in range(2 * order)
            for j in range(2 * order)
        )
        exponent = variogram / F(9, 158)
        if exponent.denominator != 1 or exponent < 0:
            raise AssertionError("nonnegative exact exponent lattice")
        residue = sum(sign * points[index] for sign, index in zip(signs, indices)) % 3
        pair = coefficients.setdefault(int(exponent), [0, 0])
        pair[0] += phases[residue][0]
        pair[1] += phases[residue][1]
    if any(pair[1] for pair in coefficients.values()):
        raise AssertionError("uncancelled root-of-unity coefficient")
    return trim([coefficients.get(k, [0, 0])[0] for k in range(max(coefficients) + 1)])


def variations(chain, point):
    values = [evaluate(poly, point) for poly in chain]
    signs = [(value > 0) - (value < 0) for value in values if value]
    return sum(a != b for a, b in itertools.pairwise(signs))


def homogeneous_affine(poly, left, right):
    """Integer Horner coefficients for a common-denominator affine substitution."""
    degree = len(poly) - 1
    coefficient_denominator = lcm(*(x.denominator for x in poly))
    integers = [int(x * coefficient_denominator) for x in poly]
    endpoint_denominator = lcm(left.denominator, right.denominator)
    origin = int(left * endpoint_denominator)
    width = int((right - left) * endpoint_denominator)
    transformed = [integers[-1]]
    for k in reversed(range(degree)):
        transformed = add(
            [origin * x for x in transformed],
            [0] + [width * x for x in transformed],
        )
        transformed[0] += integers[k] * endpoint_denominator ** (degree - k)
    return transformed, coefficient_denominator * endpoint_denominator**degree


class SmallPairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = certificate()

    def test_geometry_and_ordered_first_two_moments(self):
        points = {
            side: sorted(x + y for x in (0, 1, 5) for y in shifts)
            for side, shifts in (("A", (0, 10, 22)), ("B", (0, 12, 22)))
        }
        self.assertNotEqual(points["A"], points["B"])
        self.assertNotEqual(points["A"], sorted(27 - x for x in points["B"]))
        self.assertEqual(
            Counter(x - y for x in points["A"] for y in points["A"]),
            Counter(x - y for x in points["B"] for y in points["B"]),
        )
        for side in ("A", "B"):
            with self.subTest(side=side):
                self.assertEqual(len(set(points[side])), 9)
                record = self.result["geometry"]["classes"][side]
                laplacian, plus, trace, covariance = covariance_from_bordered_inverse(points[side])
                self.assertEqual(record["points"], points[side])
                self.assertEqual(record["laplacian"], laplacian)
                self.assertEqual(trace, F(79, 12))
                self.assertEqual(trace, fraction(record["trace_laplacian_pseudoinverse"]))
                self.assertEqual(
                    covariance,
                    [[fraction(x) for x in row] for row in record["covariance"]],
                )
                for i in range(9):
                    self.assertEqual(sum(plus[i]), 0)
                    for j in range(9):
                        self.assertEqual(
                            sum(laplacian[i][k] * plus[k][j] for k in range(9)),
                            F(i == j) - F(1, 9),
                        )
                for order in (1, 2):
                    expected = [
                        fraction(value)
                        for value in self.result["raw_moments"]["classes"][side][str(order)][
                            "coefficients"
                        ]
                    ]
                    self.assertEqual(ordered_moment(points[side], covariance, order), expected)

    def test_full_mean_factorization_and_bezout_identity(self):
        raw = self.result["raw_moments"]["classes"]
        difference = add(
            list(map(fraction, raw["B"]["1"]["coefficients"])),
            list(map(fraction, raw["A"]["1"]["coefficients"])),
            -1,
        )
        factor = self.result["mean_difference"]["factorization"]
        h = list(map(fraction, factor["H_coefficients"]))
        rebuilt = [fraction(factor["positive_content"])]
        self.assertGreater(rebuilt[0], 0)
        rebuilt = multiply(rebuilt, [0] * factor["t_zero_multiplicity"] + [1])
        rebuilt = multiply(rebuilt, power([1, -1], factor["one_minus_t_multiplicity"]))
        for row in factor["positive_simple_factors"]:
            coefficients = list(map(fraction, row["coefficients"]))
            self.assertGreater(coefficients[0], 0)
            self.assertTrue(all(value >= 0 for value in coefficients))
            rebuilt = multiply(rebuilt, power(coefficients, row["multiplicity"]))
        self.assertEqual(multiply(rebuilt, h), difference)
        attempt = self.result["joint_moments"]["attempts"][0]
        second = add(
            list(map(fraction, raw["B"]["2"]["coefficients"])),
            list(map(fraction, raw["A"]["2"]["coefficients"])),
            -1,
        )
        self.assertEqual(second, list(map(fraction, attempt["difference"])))
        self.assertEqual(h, list(map(fraction, attempt["H"])))
        witness = attempt["integer_bezout"]
        a, b = (list(map(fraction, witness[key])) for key in ("A_for_H", "B_for_difference"))
        constant = fraction(witness["positive_constant"])
        self.assertGreater(constant, 0)
        self.assertEqual(add(multiply(a, h), multiply(b, second)), [constant])
        self.assertEqual(self.result["joint_moments"]["third_moment_fallback"], "NOT_NEEDED")

    def test_sturm_chain_and_unique_mean_root(self):
        record = self.result["mean_difference"]
        h = list(map(fraction, record["factorization"]["H_coefficients"]))
        chain = [list(map(fraction, row)) for row in record["sturm_chain"]]
        self.assertEqual(chain[0], h)
        derivative = [i * h[i] for i in range(1, len(h))]
        self.assertGreater(chain[1][-1] / derivative[-1], 0)
        self.assertEqual(
            [value / chain[1][-1] for value in chain[1]],
            [value / derivative[-1] for value in derivative],
        )
        for a, b, following in zip(chain, chain[1:], chain[2:]):
            remainder = divide(a, b)[1]
            multiplier = -following[-1] / remainder[-1]
            self.assertGreater(multiplier, 0)
            self.assertEqual(following, [-multiplier * value for value in remainder])
        self.assertEqual(len(chain[-1]), 1)
        self.assertEqual(variations(chain, F(0)) - variations(chain, F(1)), 1)
        lo, hi = map(
            fraction,
            (record["root_interval"]["lower"], record["root_interval"]["upper"]),
        )
        self.assertTrue(0 < lo < hi < 1)
        self.assertLessEqual(hi - lo, F(1, 2**80))
        self.assertLess(evaluate(h, lo), 0)
        self.assertGreater(evaluate(h, hi), 0)
        self.assertEqual(variations(chain, lo) - variations(chain, hi), 1)

    def test_positive_shape_certificates_and_actual_crossovers(self):
        polynomials = self.result["shape_ordering"]["polynomials"]
        for side in ("A", "B"):
            raw = {
                order: list(
                    map(
                        fraction,
                        self.result["raw_moments"]["classes"][side][str(order)]["coefficients"],
                    )
                )
                for order in (1, 2, 3)
            }
            expected = {
                "variance": add(raw[2], power(raw[1], 2), -1),
                "third": add(add(raw[3], multiply(raw[1], raw[2]), -3), power(raw[1], 3), 2),
            }
            for name in ("variance", "third"):
                record = polynomials[f"{side}_{name}"]
                self.assertEqual(
                    list(map(fraction, record["numerator_coefficients"])),
                    expected[name],
                )
                endpoint = record["endpoint_reduction"]
                residual = list(map(fraction, endpoint["residual_coefficients"]))
                bernstein = list(map(fraction, record["bernstein_scaled_coefficients"]))
                self.assertTrue(all(value > 0 for value in bernstein))
                degree = len(residual) - 1
                # These stored coefficients are binom(n,k)*b_k.
                inverse_coefficients = [
                    sum(
                        (-1) ** (i - k) * comb(degree - k, i - k) * bernstein[k]
                        for k in range(i + 1)
                    )
                    for i in range(degree + 1)
                ]
                self.assertEqual(inverse_coefficients, residual)
                rebuilt = multiply(
                    [fraction(endpoint["positive_content"])],
                    [0] * endpoint["t_zero_multiplicity"] + [1],
                )
                rebuilt = multiply(rebuilt, power([1, -1], endpoint["one_minus_t_multiplicity"]))
                self.assertEqual(multiply(rebuilt, residual), expected[name])
        va, vb = (
            list(map(fraction, polynomials[f"{side}_variance"]["numerator_coefficients"]))
            for side in ("A", "B")
        )
        ca, cb = (
            list(map(fraction, polynomials[f"{side}_third"]["numerator_coefficients"]))
            for side in ("A", "B")
        )
        cross = add(
            multiply(power(cb, 2), power(va, 3)),
            multiply(power(ca, 2), power(vb, 3)),
            -1,
        )
        self.assertEqual(
            cross, list(map(fraction, polynomials["cross_P"]["numerator_coefficients"]))
        )
        self.assertGreater(evaluate(cross, F(13, 16)), 0)
        self.assertLess(evaluate(cross, F(7, 8)), 0)
        self.assertLess(evaluate(cross, F(15, 16)), 0)
        residual = list(
            map(
                fraction,
                polynomials["cross_P"]["endpoint_reduction"]["residual_coefficients"],
            )
        )
        endpoint = polynomials["cross_P"]["endpoint_reduction"]
        reconstructed = multiply(
            [0] * endpoint["t_zero_multiplicity"] + [fraction(endpoint["positive_content"])],
            multiply(power([1, -1], endpoint["one_minus_t_multiplicity"]), residual),
        )
        self.assertEqual(reconstructed, cross)
        self.assertGreater(sum(residual), 0)

    def test_eight_taylor_caps_with_independent_product_error(self):
        record = self.result["matched_strength_remainder"]
        prepared = {}
        for side in ("A", "B"):
            normalized, error_constants = {}, {}
            for order in (1, 2, 3):
                coefficients = list(
                    map(
                        fraction,
                        self.result["raw_moments"]["classes"][side][str(order)]["coefficients"],
                    )
                )
                jet = [
                    sum(value * (-F(9, 158) * k) ** j for k, value in enumerate(coefficients))
                    / factorial(j)
                    for j in range(17)
                ]
                self.assertTrue(all(value == 0 for value in jet[:order]))
                self.assertEqual(
                    jet,
                    list(
                        map(
                            fraction,
                            record["raw_taylor_coefficients_through16"][side][str(order)],
                        )
                    ),
                )
                normalized[order] = jet[order:]
                error_constants[order] = sum(
                    abs(value) * (F(9, 158) * k) ** 17 for k, value in enumerate(coefficients)
                ) / factorial(17)
            variance = add(normalized[2], power(normalized[1], 2), -1)
            third = add(
                add(normalized[3], multiply(normalized[1], normalized[2]), -3),
                power(normalized[1], 3),
                2,
            )
            prepared[side] = normalized, error_constants, variance, third
        cross = add(
            multiply(power(prepared["B"][3], 2), power(prepared["A"][2], 3)),
            multiply(power(prepared["A"][3], 2), power(prepared["B"][2], 3)),
            -1,
        )
        self.assertEqual(cross, list(map(fraction, record["normalized_cross_proxy_coefficients"])))
        self.assertEqual(cross[0], 0)
        self.assertGreater(cross[1], 0)
        self.assertEqual(
            [fraction(row["cap"]) for row in record["rows"]],
            [F(1, 10**k) for k in range(8, 0, -1)],
        )
        for row in record["rows"]:
            cap = fraction(row["cap"])
            bounds = {}
            for side in ("A", "B"):
                normalized, constants, variance, third = prepared[side]
                m = {
                    r: sum(abs(x) * cap**k for k, x in enumerate(normalized[r])) for r in (1, 2, 3)
                }
                e = {r: constants[r] * cap ** (17 - r) for r in (1, 2, 3)}
                ev = e[2] + (m[1] + e[1]) ** 2 - m[1] ** 2
                ec = (
                    e[3]
                    + 3 * ((m[1] + e[1]) * (m[2] + e[2]) - m[1] * m[2])
                    + 2 * ((m[1] + e[1]) ** 3 - m[1] ** 3)
                )
                vtail = sum(abs(x) * cap**k for k, x in enumerate(variance) if k)
                ctail = sum(abs(x) * cap**k for k, x in enumerate(third) if k)
                saved = row["classes"][side]
                for name, expected in (
                    ("variance_error", ev),
                    ("third_error", ec),
                    ("variance_polynomial_absolute_bound", abs(variance[0]) + vtail),
                    ("third_polynomial_absolute_bound", abs(third[0]) + ctail),
                ):
                    self.assertTrue(fraction(saved[name]) == expected, (side, str(cap), name))
                self.assertEqual(
                    [fraction(saved["normalized_variance"][k]) for k in ("lower", "upper")],
                    [variance[0] - vtail - ev, variance[0] + vtail + ev],
                )
                self.assertEqual(
                    [fraction(saved["normalized_third"][k]) for k in ("lower", "upper")],
                    [third[0] - ctail - ec, third[0] + ctail + ec],
                )
                bounds[side] = abs(variance[0]) + vtail, abs(third[0]) + ctail, ev, ec
            product_error = F(0)
            for cs, vs in (("B", "A"), ("A", "B")):
                v, _, ev, _ = bounds[vs]
                _, c, _, ec = bounds[cs]
                error = ((c + ec) ** 2 * (v + ev) ** 3 - c**2 * v**3) / cap
                self.assertTrue(
                    error == fraction(row[f"product_{cs}{vs}_error_divided_by_s"]["sum"])
                )
                product_error += error
            tail = sum(abs(x) * cap ** (k - 1) for k, x in enumerate(cross) if k >= 2)
            h = cross[1] - tail - product_error
            self.assertTrue(h == fraction(row["normalized_cross_over_s_lower"]))
            positive = h > 0
            self.assertEqual(positive, cap <= F(1, 100))
            self.assertEqual(row["band_certificate"] is not None, positive)
            self.assertTrue(
                all(
                    v
                    for k, v in row["conditions"].items()
                    if k != "positive_normalized_cross_over_s_lower"
                )
            )
        self.assertIsNone(record["rows"][-1]["band_certificate"])
        self.assertEqual(record["rows"][-1]["status"], "UNRESOLVED_BY_THIS_BOUND")

    def test_independent_strength_ranges_and_separate_same_strength_bound(self):
        record = self.result["independent_strength_bands"]
        center = F(13, 16)
        self.assertEqual(fraction(record["center"]), center)
        raw = self.result["raw_moments"]["classes"]
        polys = {
            side: {
                "mu" + str(order): list(map(fraction, raw[side][str(order)]["coefficients"]))
                for order in (1, 2)
            }
            for side in ("A", "B")
        }
        derivatives = {
            side: {
                name: evaluate([i * p[i] for i in range(1, len(p))], center)
                for name, p in group.items()
            }
            for side, group in polys.items()
        }
        numerator = sum(derivatives[side]["mu2"] for side in ("A", "B"))
        denominator = sum(derivatives[side]["mu1"] for side in ("A", "B"))
        self.assertNotEqual(denominator, 0)
        coefficient = numerator / denominator
        self.assertEqual(fraction(record["projection_coefficient"]), coefficient)
        for name, value in (("numerator", numerator), ("denominator", denominator)):
            self.assertEqual(fraction(record["coefficient_rule_values"][name]), value)
        for side in ("A", "B"):
            polys[side]["projection"] = add(polys[side]["mu2"], polys[side]["mu1"], -coefficient)
            derivatives[side]["projection"] = (
                derivatives[side]["mu2"] - coefficient * derivatives[side]["mu1"]
            )
            self.assertNotEqual(derivatives[side]["projection"], 0)
            for name, poly in polys[side].items():
                self.assertEqual(
                    list(map(fraction, record["polynomials_ascending"][side][name])),
                    poly,
                )
                self.assertEqual(
                    fraction(record["class_specific_center_derivatives"][side][name]),
                    derivatives[side][name],
                )
        self.assertEqual(derivatives["A"]["projection"] + derivatives["B"]["projection"], 0)
        self.assertEqual(
            [fraction(row["radius"]) for row in record["rows"]],
            [F(1, k) for k in (16, 64, 256, 1024, 4096)],
        )
        witness = self.result["joint_moments"]["attempts"][0]["integer_bezout"]
        a = list(map(fraction, witness["A_for_H"]))
        b = list(map(fraction, witness["B_for_difference"]))
        constant = fraction(witness["positive_constant"])
        for row in record["rows"]:
            radius = fraction(row["radius"])
            left, right = center - radius, center + radius
            self.assertEqual(
                [fraction(row["t_interval"][key]) for key in ("lower", "upper")],
                [left, right],
            )
            ranges = {}
            for side in ("A", "B"):
                ranges[side] = {}
                for name, poly in polys[side].items():
                    saved = row["classes"][side][name]
                    degree = len(poly) - 1
                    self.assertEqual(saved["degree"], degree)
                    self.assertEqual(
                        [fraction(saved["interval"][key]) for key in ("lower", "upper")],
                        [left, right],
                    )
                    nums = list(map(fraction, saved["bernstein_numerators"]))
                    scale = fraction(saved["positive_common_denominator"])
                    self.assertGreater(scale, 0)
                    self.assertEqual(scale.denominator, 1)
                    self.assertEqual(len(nums), degree + 1)
                    self.assertTrue(all(x.denominator == 1 for x in nums))
                    # Invert Bernstein coefficients by finite differences, then
                    # compare against an independently homogenized Horner shift.
                    differences = [int(x) for x in nums]
                    inverse_coefficients = []
                    for i in range(degree + 1):
                        inverse_coefficients.append(comb(degree, i) * differences[0])
                        differences = [y - x for x, y in itertools.pairwise(differences)]
                    transformed, common = homogeneous_affine(poly, left, right)
                    self.assertTrue(
                        all(
                            x * common == y * scale
                            for x, y in zip(inverse_coefficients, transformed)
                        ),
                        (str(radius), side, name),
                    )
                    self.assertEqual(len(inverse_coefficients), len(transformed))
                    bounds = min(nums) / scale, max(nums) / scale
                    self.assertEqual(
                        [fraction(saved["range"][key]) for key in ("lower", "upper")],
                        list(bounds),
                    )
                    self.assertEqual(
                        saved["extremal_coefficient_indices"],
                        {
                            "minimum": nums.index(min(nums)),
                            "maximum": nums.index(max(nums)),
                        },
                    )
                    self.assertEqual(nums[0] / scale, evaluate(poly, left))
                    self.assertEqual(nums[-1] / scale, evaluate(poly, right))
                    ranges[side][name] = bounds
            for name in ("mu1", "mu2", "projection"):
                test = row["independent_strength_range_tests"][name]
                a_below = ranges["B"][name][0] - ranges["A"][name][1]
                b_below = ranges["A"][name][0] - ranges["B"][name][1]
                passing = name == "projection" and radius <= F(1, 1024)
                self.assertEqual(max(a_below, b_below) > 0, passing)
                if passing:
                    self.assertEqual(test["status"], "CERTIFIED_B_BELOW_A")
                    self.assertEqual(fraction(test["positive_gap"]), b_below)
                    if radius == F(1, 1024):
                        self.assertGreater(b_below, F(7, 100000))
                else:
                    self.assertEqual(test["status"], "UNRESOLVED_RANGE_OVERLAP")
                    self.assertIsNone(test["positive_gap"])
                    self.assertEqual(fraction(test["A_below_B_signed_gap"]), a_below)
                    self.assertEqual(fraction(test["B_below_A_signed_gap"]), b_below)
            # This separate common-t lower bound does not imply the class-range
            # disjointness above. It comes from the already checked Bezout identity.
            fmin = (
                left**39
                * (1 - right) ** 2
                * (1 + left) ** 2
                * (1 + left + left**2)
                * (1 + left**2) ** 2
                * (1 + left**4) ** 2
                * (1 + left**8)
            )
            amax = evaluate(list(map(abs, a)), right)
            bmax = evaluate(list(map(abs, b)), right)
            gap = constant / (amax / fmin + bmax)
            saved_gap = row["matched_strength_joint_gap"]
            self.assertGreater(gap, 0)
            for name, value in (
                ("F_lower", fmin),
                ("A_absolute_upper", amax),
                ("B_absolute_upper", bmax),
                ("max_absolute_joint_moment_gap_lower", gap),
            ):
                self.assertEqual(fraction(saved_gap[name]), value)
            self.assertIn("Same t only", saved_gap["scope"])
            self.assertEqual(
                row["strength_interval_exact"],
                {
                    "s_lower": f"-(158/9)*log({right})",
                    "s_upper": f"-(158/9)*log({left})",
                    "beta_lower": f"-(79/pi^2)*log({right})",
                    "beta_upper": f"-(79/pi^2)*log({left})",
                },
            )
        self.assertEqual(
            list(map(fraction, record["passing_projection_radii"])),
            [F(1, 1024), F(1, 4096)],
        )
        self.assertEqual(fraction(record["largest_declared_passing_radius"]), F(1, 1024))
        self.assertIn("calibrated", record["observable"])
        self.assertTrue(any("fixed strength independently" in text for text in record["scope"]))
        self.assertTrue(any("No unknown gain/background" in text for text in record["scope"]))
        self.assertIn("not a new blind", record["selection_disclosure"])

    def test_parameter_free_api_and_early_parser_refusals(self):
        self.assertEqual(len(inspect.signature(build_small_pair_certificate).parameters), 0)
        with self.assertRaises(TypeError):
            build_small_pair_certificate(scenario="exact_geometry")
        with patch("homometric_motion.cli.build_small_pair_certificate") as builder:
            for args in (
                ["small-pair"],
                [
                    "small-pair",
                    "--scenario",
                    "exact_geometry",
                    "--output",
                    "unused.json",
                ],
                [
                    "small-pair",
                    "--profile",
                    "short-exposure-v1",
                    "--output",
                    "unused.json",
                ],
            ):
                with self.subTest(args=args), redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as error:
                        main(args)
                    self.assertEqual(error.exception.code, 2)
            builder.assert_not_called()

    def test_saved_record_cheap_refusals_precede_reconstruction(self):
        cases = [None, [], "not a certificate", {}]
        changed = copy.deepcopy(self.result)
        changed["parameters"]["n"] = 10
        cases.append(changed)
        changed = copy.deepcopy(self.result)
        changed["extra"] = None
        cases.append(changed)
        changed = copy.deepcopy(self.result)
        changed["schema_version"] = True
        cases.append(changed)
        for bad_value in (
            float("nan"),
            1 << 64,
            "x" * 100001,
            [0] * 3001,
            {1: "bad key"},
        ):
            changed = copy.deepcopy(self.result)
            changed["checks"]["extra"] = bad_value
            cases.append(changed)
        nested = None
        for _ in range(25):
            nested = [nested]
        changed = copy.deepcopy(self.result)
        changed["checks"]["extra"] = nested
        cases.append(changed)
        with patch("homometric_motion.smallpair.build_small_pair_certificate") as builder:
            for index, value in enumerate(cases):
                with self.subTest(case=index), self.assertRaises(ValueError):
                    validate_saved_small_pair(value)
            builder.assert_not_called()

    def test_full_tampered_witness_rejected_by_fresh_reconstruction(self):
        changed = copy.deepcopy(self.result)
        witness = changed["joint_moments"]["attempts"][0]["integer_bezout"]
        witness["A_for_H"][0] = str(fraction(witness["A_for_H"][0]) + 1)
        guard = sys.get_int_max_str_digits()
        # Deliberately not mocked: this must compare against a new full calculation.
        with self.assertRaisesRegex(ValueError, "fresh exact reconstruction"):
            validate_saved_small_pair(changed)
        self.assertEqual(sys.get_int_max_str_digits(), guard)

    def test_installed_manifest_covers_all_seven_modules(self):
        provenance = verify_source_manifest()
        self.assertTrue(MODULES <= provenance["bindings"].keys())
        package = Path(homometric_motion.__file__).resolve().parent
        for name in MODULES:
            self.assertEqual(
                hashlib.sha256((package / name).read_bytes()).hexdigest(),
                provenance["bindings"][name],
            )
        changed = copy.deepcopy(self.result)
        changed["source_revision"] = {"schema_version": 1, "manifest_sha256": "0" * 64}
        with patch("homometric_motion.cli.validate_saved_small_pair") as validator:
            with self.assertRaisesRegex(ValueError, "provenance"):
                summary(changed)
            validator.assert_not_called()

    def test_cli_fresh_output_saved_comparison_and_exclusive_path(self):
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            output = cwd / "small-pair.json"
            executable = os.environ.get("HM_TEST_PYTHON", sys.executable)
            command = [executable, "-I", "-m", "homometric_motion"]
            run = subprocess.run(
                [*command, "small-pair", "--output", str(output)],
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=180,
                check=False,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn("PASS:", run.stdout)
            payload = output.read_bytes()
            saved = json.loads(payload)
            self.assertEqual(saved.pop("source_revision"), verify_source_manifest())
            self.assertEqual(saved, self.result)
            displayed = subprocess.run(
                [*command, "summary", str(output)],
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=180,
                check=False,
            )
            self.assertEqual(displayed.returncode, 0, displayed.stderr)
            self.assertIn("UNVERIFIED SAVED RECORD", displayed.stdout)
            self.assertIn("fresh installed-model reconstruction", displayed.stdout)
            self.assertIn("does not authenticate", displayed.stdout)
            self.assertNotIn("not recomputed", displayed.stdout)
            duplicate = subprocess.run(
                [*command, "small-pair", "--output", str(output)],
                cwd=cwd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=30,
                check=False,
            )
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertIn("output exists", duplicate.stderr)
            self.assertEqual(output.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
