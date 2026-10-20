"""Exact outward arithmetic for the fixed mathematical certificate."""

from fractions import Fraction as F
from math import isqrt

SCALE = 10**72


def rational_text(value):
    """Serialize an exact fraction without changing Python's digit-limit setting.

    Some certified risk fractions exceed the default decimal conversion limit.
    Each conversion here handles at most nine digits; all arithmetic stays exact.
    """
    value = F(value)

    def decimal_integer(number):
        if number == 0:
            return "0"
        sign = "-" if number < 0 else ""
        number = abs(number)
        chunks = []
        while number:
            number, remainder = divmod(number, 10**9)
            chunks.append(remainder)
        return sign + str(chunks[-1]) + "".join(f"{chunk:09d}" for chunk in reversed(chunks[:-1]))

    numerator = decimal_integer(value.numerator)
    if value.denominator == 1:
        return numerator
    return numerator + "/" + decimal_integer(value.denominator)


def ceiling_fraction(x):
    return -(-x.numerator // x.denominator)


def integer_root(x, degree):
    """Floor of the nonnegative integer degree-th root, with an exact bracket."""
    if not isinstance(x, int) or not isinstance(degree, int) or x < 0 or degree < 1:
        raise ValueError("nonnegative integer and positive degree required")
    if degree == 1:
        return x
    if degree == 2:
        answer = isqrt(x)
    else:
        lo, hi = 0, 1 << ((x.bit_length() + degree - 1) // degree)
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if mid**degree <= x:
                lo = mid
            else:
                hi = mid
        answer = lo
    if not answer**degree <= x < (answer + 1) ** degree:
        raise ArithmeticError("integer root bracket")
    return answer


class Interval:
    """Integer endpoints on a fixed 10^-72 grid; every operation is outward."""

    def __init__(self, value=0):
        value = F(value)
        scaled = value * SCALE
        self.lo = scaled.numerator // scaled.denominator
        self.hi = ceiling_fraction(scaled)

    @classmethod
    def endpoints(cls, lo, hi):
        if not isinstance(lo, int) or not isinstance(hi, int):
            raise TypeError("integer grid endpoints required")
        if lo > hi:
            raise ValueError("reversed endpoints")
        obj = cls.__new__(cls)
        obj.lo, obj.hi = lo, hi
        return obj

    @classmethod
    def bounds(cls, lo, hi):
        lo, hi = F(lo), F(hi)
        if lo > hi:
            raise ValueError("reversed bounds")
        return cls.endpoints(cls(lo).lo, cls(hi).hi)

    @property
    def lower(self):
        return F(self.lo, SCALE)

    @property
    def upper(self):
        return F(self.hi, SCALE)

    def __add__(self, other):
        other = other if isinstance(other, Interval) else Interval(other)
        return self.endpoints(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return self.endpoints(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -(other if isinstance(other, Interval) else Interval(other))

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        other = other if isinstance(other, Interval) else Interval(other)
        products = [a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.endpoints(min(products) // SCALE, -(-max(products) // SCALE))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = other if isinstance(other, Interval) else Interval(other)
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError("interval denominator contains zero")
        ratios = [F(SCALE * a, b) for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        low, high = min(ratios), max(ratios)
        return self.endpoints(low.numerator // low.denominator, ceiling_fraction(high))

    def __rtruediv__(self, other):
        return Interval(other) / self

    def __pow__(self, degree):
        if not isinstance(degree, int) or degree < 0:
            raise ValueError("nonnegative integer power required")
        if degree == 0:
            return Interval(1)
        if degree % 2:
            low, high = self.lo**degree, self.hi**degree
        else:
            low = 0 if self.lo <= 0 <= self.hi else min(self.lo**degree, self.hi**degree)
            high = max(self.lo**degree, self.hi**degree)
        divisor = SCALE ** (degree - 1)
        return self.endpoints(low // divisor, -(-high // divisor))

    def root(self, degree):
        if not isinstance(degree, int) or degree < 1:
            raise ValueError("positive integer root degree required")
        if self.lo < 0:
            raise ValueError("root requires a nonnegative interval")
        low_arg = self.lo * SCALE ** (degree - 1)
        high_arg = self.hi * SCALE ** (degree - 1)
        low = integer_root(low_arg, degree)
        high = integer_root(high_arg, degree)
        if high**degree < high_arg:
            high += 1
        return self.endpoints(low, high)

    def contains(self, value):
        return self.lower <= value <= self.upper

    def record(self):
        return {
            "lower": str(self.lower),
            "upper": str(self.upper),
            "decimal_display_only": [float(self.lower), float(self.upper)],
        }


def arctangent_reciprocal(denominator, terms=120):
    total = sum(
        (F((-1) ** k, (2 * k + 1) * denominator ** (2 * k + 1)) for k in range(terms)),
        F(0),
    )
    next_term = F((-1) ** terms, (2 * terms + 1) * denominator ** (2 * terms + 1))
    return Interval.bounds(min(total, total + next_term), max(total, total + next_term))


def pi_enclosure():
    return 16 * arctangent_reciprocal(5) - 4 * arctangent_reciprocal(239)


def interval_controls(check):
    samples = (F(-7, 3), F(-1, 11), F(0), F(2, 7), F(13, 5))
    for a in samples:
        for b in samples:
            check((Interval(a) + b).contains(a + b), "signed interval addition")
            check((Interval(a) * b).contains(a * b), "signed interval multiplication")
            if b:
                check((Interval(a) / b).contains(a / b), "signed interval division")
        for degree in range(7):
            check((Interval(a) ** degree).contains(a**degree), "signed integer power")
    check((Interval.bounds(-2, 3) ** 2).contains(0), "even power crossing zero")
    for x in (F(0), F(1), F(2, 7), F(74), F(191), F(10**20, 3)):
        for degree in (2, 3, 4, 6, 12):
            root = Interval(x).root(degree)
            check(root.lower**degree <= x <= root.upper**degree, "root enclosure")
    pi = pi_enclosure()
    check(3 < pi.lower < pi.upper < F(22, 7), "Machin pi coarse enclosure")
    check(pi.upper - pi.lower < F(1, 10**69), "Machin pi resolution")
    return pi / 3
