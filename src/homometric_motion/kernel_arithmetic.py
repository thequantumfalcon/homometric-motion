"""Separate 96-place outward arithmetic for the signed kernel bounds.

The original certificate's 72-place Interval and its behavior are unchanged.
These fractional endpoints reproduce the kernel method's operation order.
"""

from fractions import Fraction as F

from .arithmetic import integer_root, rational_from_text, rational_text

SCALE = 10**96


def fraction(value):
    return rational_from_text(value) if isinstance(value, str) else F(value)


class KernelInterval:
    """Closed rational interval rounded outward after every operation."""

    def __init__(self, lower=0, upper=None):
        lower = fraction(lower)
        upper = lower if upper is None else fraction(upper)
        if lower > upper:
            raise ValueError("reversed kernel interval")
        a, b = lower * SCALE, upper * SCALE
        self.lo = F(a.numerator // a.denominator, SCALE)
        self.hi = F(-(-b.numerator // b.denominator), SCALE)

    @classmethod
    def coerce(cls, value):
        return value if isinstance(value, cls) else cls(value)

    @classmethod
    def from_record(cls, record):
        return cls(record["lower"], record["upper"])

    def record(self):
        return {"lower": rational_text(self.lo), "upper": rational_text(self.hi)}

    def __add__(self, other):
        other = self.coerce(other)
        return self.__class__(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self):
        return self.__class__(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        other = self.coerce(other)
        values = [a * b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.__class__(min(values), max(values))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = self.coerce(other)
        if other.lo <= 0 <= other.hi:
            raise ZeroDivisionError("kernel interval denominator meets zero")
        values = [a / b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return self.__class__(min(values), max(values))

    def __rtruediv__(self, other):
        return self.coerce(other) / self

    def __pow__(self, degree):
        if not isinstance(degree, int) or degree < 0:
            raise ValueError("nonnegative integer power required")
        values = [self.lo**degree, self.hi**degree]
        if degree and degree % 2 == 0 and self.lo <= 0 <= self.hi:
            values.append(F(0))
        return self.__class__(min(values), max(values))

    def root(self, degree):
        if not isinstance(degree, int) or degree < 1 or self.lo < 0:
            raise ValueError("positive integer root on a nonnegative interval required")
        arguments = [endpoint * SCALE**degree for endpoint in (self.lo, self.hi)]
        floors = [integer_root(x.numerator // x.denominator, degree) for x in arguments]
        lower, upper = F(floors[0], SCALE), F(floors[1], SCALE)
        if upper**degree < self.hi:
            upper += F(1, SCALE)
        if not lower**degree <= self.lo <= self.hi <= upper**degree:
            raise ArithmeticError("kernel radical enclosure")
        return self.__class__(lower, upper)
