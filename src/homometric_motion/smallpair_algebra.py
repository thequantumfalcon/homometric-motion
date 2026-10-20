"""Bounded exact polynomial and matrix arithmetic for the fixed nine-point model."""

from fractions import Fraction as F
from functools import reduce
from math import comb, gcd, lcm

from .arithmetic import rational_text

MAX_DEGREE = 2400
MAX_BITS = 65536
MAX_TRANSFORM_UPDATES = 20_000_000


def exact(value):
    """Encode exact fractions without changing Python's conversion guard."""
    if isinstance(value, F):
        return rational_text(value)
    if isinstance(value, dict):
        return {str(k): exact(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [exact(v) for v in value]
    return value


def texts(values):
    return [rational_text(x) for x in values]


def bounded(poly):
    if not isinstance(poly, (list, tuple)) or not 1 <= len(poly) <= MAX_DEGREE + 1:
        raise ValueError("bounded nonempty polynomial required")
    for value in poly:
        if not isinstance(value, (int, F)) or isinstance(value, bool):
            raise ValueError("exact polynomial coefficient required")
        numerator, denominator = (
            (value.numerator, value.denominator) if isinstance(value, F) else (value, 1)
        )
        if max(abs(numerator).bit_length(), denominator.bit_length()) > MAX_BITS:
            raise ValueError("polynomial coefficient bit limit")
    return poly


def trim(poly):
    bounded(poly)
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def add(a, b, scale=1):
    bounded(a)
    bounded(b)
    return trim(
        [
            (a[i] if i < len(a) else 0) + scale * (b[i] if i < len(b) else 0)
            for i in range(max(len(a), len(b)))
        ]
    )


def multiply(a, b):
    bounded(a)
    bounded(b)
    if len(a) + len(b) - 2 > MAX_DEGREE:
        raise ValueError("product degree limit before multiplication")
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    result[i + j] += x * y
    return trim(result)


def power(a, degree):
    if type(degree) is not int or not 0 <= degree <= 18:
        raise ValueError("bounded polynomial power required")
    bounded(a)
    if (len(a) - 1) * degree > MAX_DEGREE:
        raise ValueError("power degree limit before multiplication")
    result = [1]
    for _ in range(degree):
        result = multiply(result, a)
    return result


def divide(a, b):
    a, b = trim(list(map(F, a))), trim(list(map(F, b)))
    if b == [0]:
        raise ZeroDivisionError("zero polynomial divisor")
    q = [F(0)] * max(1, len(a) - len(b) + 1)
    while a != [0] and len(a) >= len(b):
        offset, factor = len(a) - len(b), a[-1] / b[-1]
        q[offset] = factor
        for j, x in enumerate(b):
            a[offset + j] -= factor * x
        a = trim(a)
    return trim(q), a


def evaluate(poly, x):
    bounded(poly)
    result = F(0)
    for coefficient in reversed(poly):
        result = result * x + coefficient
    return result


def endpoint_reduce(poly, check):
    bounded(poly)
    if not any(poly):
        raise ValueError("endpoint reduction needs a nonzero polynomial")
    zero = next(i for i, value in enumerate(poly) if value)
    residual, one = list(poly[zero:]), 0
    while len(residual) > 1 and sum(residual) == 0:
        quotient = [0] * (len(residual) - 1)
        quotient[-1] = residual[-1]
        for i in range(len(residual) - 2, 0, -1):
            quotient[i - 1] = residual[i] + quotient[i]
        check(residual[0] + quotient[0] == 0, "exact endpoint division")
        residual = [-x for x in quotient]
        one += 1
    content = reduce(gcd, map(abs, residual))
    residual = [x // content for x in residual]
    restored = [0] * zero + [
        content * x for x in multiply(residual, [(-1) ** j * comb(one, j) for j in range(one + 1)])
    ]
    check(restored == list(poly), "entire endpoint-factor re-expansion")
    check(residual[0] != 0 and sum(residual) != 0, "all endpoint factors removed")
    return zero, one, content, residual


def homogeneous_transform(poly, sign, budget):
    bounded(poly)
    if sign not in (-1, 1):
        raise ValueError("homogeneous transform sign")
    cost = len(poly) * (len(poly) - 1) // 2
    if budget[0] + cost > MAX_TRANSFORM_UPDATES:
        raise ValueError("cumulative transform budget before calculation")
    budget[0] += cost
    out, pascal = [poly[-1]], [1]
    for value in reversed(poly[:-1]):
        pascal = (
            [pascal[0]]
            + [pascal[j] + sign * pascal[j - 1] for j in range(1, len(pascal))]
            + [sign * pascal[-1]]
        )
        out = [x + value * y for x, y in zip([0] + out, pascal)]
        bounded(out)
    return out


def coefficient_sign(values):
    positive, negative = sum(x > 0 for x in values), sum(x < 0 for x in values)
    verdict = (
        "POSITIVE"
        if positive and not negative
        else "NEGATIVE"
        if negative and not positive
        else "IDENTICALLY_ZERO"
        if not positive and not negative
        else "UNRESOLVED"
    )
    return {
        "verdict": verdict,
        "positive": positive,
        "negative": negative,
        "zero": len(values) - positive - negative,
    }


def sturm(poly):
    if len(poly) > 81 or len(poly) < 2:
        raise ValueError("Sturm degree must be between one and eighty")
    chain = [list(map(F, poly)), [F(i) * poly[i] for i in range(1, len(poly))]]
    while len(chain) <= 81:
        remainder = divide(chain[-2], chain[-1])[1]
        if remainder == [0]:
            return chain
        scale = abs(remainder[-1])
        chain.append([-x / scale for x in remainder])
    raise ValueError("Sturm chain length limit")


def variations(chain, x):
    signs = [(1 if y > 0 else -1) for p in chain if (y := evaluate(p, x))]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def bezout(h, difference, check):
    if len(h) > 16 or len(difference) > 721:
        raise ValueError("fixed Bezout input degree limit")
    quotient, remainder = divide(difference, h)
    check(add(multiply(quotient, h), remainder) == difference, "initial Bezout division")
    old_r, r = list(map(F, h)), remainder
    old_u, u, old_v, v = [F(1)], [F(0)], [F(0)], [F(1)]
    steps = []
    while r != [0]:
        if len(steps) >= 32:
            raise ValueError("Euclidean division count limit")
        q, following = divide(old_r, r)
        check(add(multiply(q, r), following) == old_r, "Euclidean division identity")
        steps.append(
            {
                "dividend": texts(old_r),
                "divisor": texts(r),
                "quotient": texts(q),
                "remainder": texts(following),
            }
        )
        old_r, r = r, following
        old_u, u = u, add(old_u, multiply(q, u), -1)
        old_v, v = v, add(old_v, multiply(q, v), -1)
    leading = old_r[-1]
    monic = [x / leading for x in old_r]
    b = [x / leading for x in old_v]
    a = add([x / leading for x in old_u], multiply(b, quotient), -1)
    check(add(multiply(a, h), multiply(b, difference)) == monic, "full rational Bezout identity")
    check(
        divide(h, monic)[1] == [0] and divide(difference, monic)[1] == [0],
        "gcd divides both inputs",
    )
    integer = None
    if monic == [1]:
        constant = lcm(*(x.denominator for x in a + b))
        ia, ib = [int(x * constant) for x in a], [int(x * constant) for x in b]
        content = reduce(gcd, [constant] + list(map(abs, ia + ib)))
        ia, ib, constant = (
            [x // content for x in ia],
            [x // content for x in ib],
            constant // content,
        )
        bounded(ia)
        bounded(ib)
        bounded([constant])
        # This independent sparse integer expansion does not reuse rational convolution.
        expansion = {}
        for left, right in ((ia, h), (ib, difference)):
            for i, x in enumerate(left):
                if x:
                    for j, y in enumerate(right):
                        if y:
                            expansion[i + j] = expansion.get(i + j, 0) + x * y
        check(
            {k: v for k, v in expansion.items() if v} == {0: constant} and constant > 0,
            "full integer Bezout identity",
        )
        integer = {
            "A_for_H": texts(ia),
            "B_for_difference": texts(ib),
            "positive_constant": rational_text(constant),
        }
    return {
        "H": texts(h),
        "difference": texts(difference),
        "initial_quotient": texts(quotient),
        "initial_remainder": texts(remainder),
        "euclidean_steps": steps,
        "monic_gcd": texts(monic),
        "unit_gcd": monic == [1],
        "rational_A": texts(a),
        "rational_B": texts(b),
        "integer_bezout": integer,
    }


def matrix_multiply(a, b):
    return [[sum(x * y for x, y in zip(row, column)) for column in zip(*b)] for row in a]


def inverse(matrix):
    n = len(matrix)
    if not 1 <= n <= 9 or any(len(row) != n for row in matrix):
        raise ValueError("bounded square matrix required")
    a = [[F(x) for x in row] + [F(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        k = next((i for i in range(j, n) if a[i][j]), None)
        if k is None:
            raise ValueError("singular grounded graph matrix")
        a[k], a[j] = a[j], a[k]
        divisor = a[j][j]
        a[j] = [x / divisor for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [x - factor * y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]
