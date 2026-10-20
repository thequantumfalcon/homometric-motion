"""Adversarial arithmetic cases and an alternative rational enclosure of pi."""

import sys
import unittest
from fractions import Fraction as F

from homometric_motion.arithmetic import (
    Interval,
    integer_root,
    pi_enclosure,
    rational_from_text,
    rational_text,
)


class ArithmeticTests(unittest.TestCase):
    def assert_encloses(self, interval, values):
        self.assertLessEqual(interval.lower, min(values))
        self.assertGreaterEqual(interval.upper, max(values))

    def test_signed_endpoint_products_and_divisions(self):
        """Extrema must include opposite-sign corners, not only matching ends."""
        bounds = [(F(-7, 3), F(-1, 11)), (F(-2), F(3)), (F(2, 7), F(13, 5))]
        for lo, hi in bounds:
            for other_lo, other_hi in bounds:
                with self.subTest(first=(lo, hi), second=(other_lo, other_hi)):
                    a, b = Interval.bounds(lo, hi), Interval.bounds(other_lo, other_hi)
                    self.assert_encloses(
                        a * b, [x * y for x in (lo, hi) for y in (other_lo, other_hi)]
                    )
                    if other_lo <= 0 <= other_hi:
                        with self.assertRaises(ZeroDivisionError):
                            _ = a / b
                    else:
                        self.assert_encloses(
                            a / b,
                            [x / y for x in (lo, hi) for y in (other_lo, other_hi)],
                        )

    def test_even_powers_include_interior_minimum(self):
        interval = Interval.bounds(F(-17, 7), F(9, 5))
        for power in (2, 4, 6):
            value = interval**power
            self.assertEqual(value.lower, 0)
            self.assertGreaterEqual(value.upper, F(17, 7) ** power)
        self.assert_encloses(interval**3, [F(-17, 7) ** 3, F(9, 5) ** 3])

    def test_integer_roots_at_adjacent_perfect_powers(self):
        """Check both sides of huge perfect powers and the exact boundary."""
        for degree in (2, 3, 4, 6, 12):
            for base in (1, 7, 10**35 + 37):
                with self.subTest(degree=degree, base=base):
                    exact = base**degree
                    self.assertEqual(integer_root(exact - 1, degree), base - 1)
                    self.assertEqual(integer_root(exact, degree), base)
                    self.assertEqual(integer_root(exact + 1, degree), base)
        self.assertEqual(integer_root(0, 12), 0)
        self.assertEqual(integer_root(123456789, 1), 123456789)

    def test_fractional_roots_have_exact_power_brackets(self):
        """Include sub-grid inputs, where rounding the radicand matters."""
        for value in (F(1, 10**100), F(74, 75), F(191, 192), F(10**70 + 1, 3)):
            for degree in (2, 3, 4, 6, 12):
                with self.subTest(value=value, degree=degree):
                    lower, upper = (
                        Interval(value).root(degree).lower,
                        Interval(value).root(degree).upper,
                    )
                    self.assertGreaterEqual(lower, 0)
                    self.assertLessEqual(lower**degree, value)
                    self.assertGreaterEqual(upper**degree, value)

    def test_invalid_domains_are_rejected(self):
        with self.assertRaises(ValueError):
            integer_root(-1, 2)
        with self.assertRaises(ValueError):
            integer_root(2, 0)
        with self.assertRaises(ValueError):
            Interval(-1).root(2)
        with self.assertRaises(ValueError):
            Interval.bounds(2, 1)
        with self.assertRaises(ValueError):
            Interval.bounds(F(1, 10**73), 0)
        with self.assertRaises(ValueError):
            _ = Interval(2) ** -1
        for degree in (0, -1, F(1, 2)):
            with self.assertRaises(ValueError):
                Interval(2).root(degree)

    def test_large_fraction_serialization_preserves_digit_guard(self):
        limit = sys.get_int_max_str_digits()
        numerator = 10**5000 + 1
        expected = "1" + "0" * 4999 + "1"
        self.assertEqual(rational_text(F(numerator, 7)), expected + "/7")
        self.assertEqual(rational_text(F(-numerator, 7)), "-" + expected + "/7")
        self.assertEqual(rational_text(F(0)), "0")
        self.assertEqual(rational_text(F(123)), "123")
        self.assertEqual(rational_from_text(expected + "/7"), F(numerator, 7))
        self.assertEqual(rational_from_text("-" + expected + "/7"), F(-numerator, 7))
        self.assertEqual(sys.get_int_max_str_digits(), limit)

    def test_saved_rational_parser_rejects_ambiguous_or_unbounded_text(self):
        for text in ("", "1/0", "1/-2", "1/2/3", "1e3", "+2", " 2", "٢", "1" * 100001):
            with self.subTest(text=text[:20]):
                with self.assertRaises(ValueError):
                    rational_from_text(text)
        with self.assertRaises(ValueError):
            rational_from_text(1)

    def test_pi_matches_alternative_arctangent_identity(self):
        """Use pi/4=atan(1/2)+atan(1/3), not the production Machin formula."""

        def atan_bounds(denominator):
            count = 180
            total = sum(
                (F((-1) ** k, (2 * k + 1) * denominator ** (2 * k + 1)) for k in range(count)),
                F(0),
            )
            remainder = F(1, (2 * count + 1) * denominator ** (2 * count + 1))
            return total, total + remainder

        first, second = atan_bounds(2), atan_bounds(3)
        independent_lower = 4 * (first[0] + second[0])
        independent_upper = 4 * (first[1] + second[1])
        production = pi_enclosure()
        self.assertLess(independent_upper - independent_lower, F(1, 10**100))
        self.assertLessEqual(production.lower, independent_lower)
        self.assertGreaterEqual(production.upper, independent_upper)
        self.assertLess(production.upper - production.lower, F(1, 10**69))


if __name__ == "__main__":
    unittest.main()
