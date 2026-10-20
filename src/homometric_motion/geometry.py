"""Construct the exact graph, phase and Gaussian energy data."""

from fractions import Fraction as F
from math import comb, factorial, lcm

from .arithmetic import Interval


def complex_product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def direct_phases(check):
    root3 = Interval(3).root(2)
    ct, st = Interval(74).root(2) / (5 * root3), 1 / (5 * root3)
    cp, sp = Interval(191).root(2) / (8 * root3), -1 / (8 * root3)
    zeta = Interval(F(1, 2)), root3 / 2
    zeta2 = Interval(F(-1, 2)), root3 / 2
    unit = []
    for j in range(10):
        even_phase = (Interval((-1) ** j), Interval(0)) if j < 2 else (((-1) ** j) * cp, sp)
        odd_phase = complex_product(zeta, (((-1) ** j) * ct, st))
        unit.extend((even_phase, odd_phase))
    unit.append((Interval(1), Interval(0)))
    # These are exact algebraic identities, not inferences from small intervals.
    check(F(74, 75) + F(1, 75) == 1, "theta exact unit phase")
    check(F(191, 192) + F(1, 192) == 1, "phi exact unit phase")
    check(F(1, 4) + F(3, 4) == 1, "zeta exact unit phase")
    check(sum((-1) ** j for j in range(10)) == 0, "theta cosine cancellation")
    check(sum((-1) ** j for j in range(2, 10)) == 0, "phi cosine cancellation")
    check(1 - 5 * F(1, 5) == 0, "exact null real coefficient")
    check(5 * F(1, 5) + 8 * F(-1, 8) == 0, "exact null imaginary coefficient")
    check(
        sum(z[0] for z in unit).contains(0) and sum(z[1] for z in unit).contains(0),
        "direct phase null consistency",
    )
    check(
        F(1, 74) < F(1, 64) and F(1, 191) < F(1, 64),
        "shift bounds strictly below one eighth",
    )
    phases = {}
    for side, factor in (("A", zeta), ("B", zeta2)):
        phases[side] = (
            unit + [complex_product(factor, z) for z in unit] + [(-z[0], -z[1]) for z in unit]
        )
        check(len(phases[side]) == 63, side + " phase count")
        check(
            all((x * x + y * y).contains(1) for x, y in phases[side]),
            side + " interval unit-phase consistency",
        )
    return phases


def exact_covariance(side, check):
    if side not in ("A", "B"):
        raise ValueError("class must be A or B")
    base = sorted([3 * j + d for j in range(10) for d in (0, 1)] + [30])
    translations = (0, 31, 63) if side == "A" else (0, 32, 63)
    positions = sorted(x + t for t in translations for x in base)
    n = len(positions)
    edges = {
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if F(positions[j] - positions[i]) <= F(5, 2)
    }
    start = 20 if side == "A" else 41
    expected = {(i, i + 1) for i in range(n - 1)} | {(start, start + 2)}
    check(n == 63 and len(set(positions)) == n, side + " sorted geometry")
    check(edges == expected, side + " independently enumerated threshold graph")
    check(
        all(
            F(abs(F(positions[j] - positions[i]) - F(5, 2))) >= F(1, 2)
            for i in range(n)
            for j in range(i + 1, n)
        ),
        side + " integer threshold margin",
    )
    # Adding one unit-conductance chord to the path is a rank-one update.
    # The overlap is the path voltage drop across the new chord for unit i-j flow.
    resistance = []
    for i in range(n):
        row = []
        for j in range(n):
            lo, hi = min(i, j), max(i, j)
            overlap = max(0, min(hi, start + 2) - max(lo, start))
            row.append(F(hi - lo) - F(overlap**2, 3))
        resistance.append(row)
    row_mean = [sum(row, F(0)) / n for row in resistance]
    grand_mean = sum(row_mean, F(0)) / n
    lp = [
        [(row_mean[i] + row_mean[j] - grand_mean - resistance[i][j]) / 2 for j in range(n)]
        for i in range(n)
    ]
    neighbors = [
        {j for a, b in edges for j in (([b] if a == i else []) + ([a] if b == i else []))}
        for i in range(n)
    ]
    check(all(sum(row) == 0 for row in lp), side + " centered pseudoinverse")
    check(
        all(lp[i][j] == lp[j][i] for i in range(n) for j in range(n)),
        side + " symmetric pseudoinverse",
    )
    check(
        all(
            len(neighbors[i]) * lp[i][j] - sum(lp[k][j] for k in neighbors[i])
            == F(i == j) - F(1, n)
            for i in range(n)
            for j in range(n)
        ),
        side + " exact Laplacian pseudoinverse identity",
    )
    trace = sum(lp[i][i] for i in range(n))
    check(
        trace == sum(resistance[i][j] for i in range(n) for j in range(i + 1, n)) / n,
        side + " resistance trace identity",
    )
    covariance = [[n * x / trace for x in row] for row in lp]
    check(sum(covariance[i][i] for i in range(n)) == n, side + " exact covariance trace")
    check(all(covariance[i][i] > 0 for i in range(n)), side + " positive diagonal")
    return covariance, trace


def integer_matrix_product(a, b):
    columns = list(zip(*b))
    return [[sum(x * y for x, y in zip(row, column)) for column in columns] for row in a]


def energy_moments(covariance, check):
    n = len(covariance)
    denominator = lcm(*(x.denominator for row in covariance for x in row))
    integer_matrix = [[int(x * denominator) for x in row] for row in covariance]
    powers = {1: integer_matrix}
    for power in range(2, 7):
        powers[power] = integer_matrix_product(powers[power - 1], integer_matrix)
    traces = {1: F(sum(integer_matrix[i][i] for i in range(n)), denominator)}
    for power in range(2, 13):
        a, b = powers[power // 2], powers[power - power // 2]
        traces[power] = F(
            sum(a[i][j] * b[i][j] for i in range(n) for j in range(n)),
            denominator**power,
        )
    cumulants = {k: 2 ** (k - 1) * factorial(k - 1) * traces[k] for k in range(1, 13)}
    moments = {0: F(1)}
    for k in range(1, 13):
        moments[k] = sum(
            (comb(k - 1, j - 1) * cumulants[j] * moments[k - j] for j in range(1, k + 1)),
            F(0),
        )
        rank_one = factorial(2 * k) // (2**k * factorial(k)) * n**k
        check(0 < moments[k] <= rank_one, "exact energy moment bound")
    check(moments[2] == traces[1] ** 2 + 2 * traces[2], "energy second moment")
    check(
        moments[4]
        == traces[1] ** 4
        + 12 * traces[1] ** 2 * traces[2]
        + 12 * traces[2] ** 2
        + 32 * traces[1] * traces[3]
        + 48 * traces[4],
        "energy fourth moment",
    )
    return traces, moments


def full_contractions(z, covariance, check):
    xx, yy, xy = Interval(0), Interval(0), Interval(0)
    for i, (x, y) in enumerate(z):
        for j, (u, v) in enumerate(z):
            weight = covariance[i][j]
            xx += weight * x * u
            yy += weight * y * v
            xy += weight * x * v
    q, real_p, imag_p = xx + yy, xx - yy, 2 * xy
    p_squared = real_p**2 + imag_p**2
    check(
        xx.lower > 0 and yy.lower > 0 and (xx * yy - xy**2).lower > 0,
        "positive projected two dimensional covariance",
    )
    check((q**2 - p_squared).lower > 0, "strict complex covariance inequality")
    return q, p_squared, real_p, imag_p


def moment_recursion(cumulants, order):
    moments = {0: Interval(1)}
    for k in range(1, order + 1):
        moments[k] = sum(
            comb(k - 1, j - 1) * cumulants[j] * moments[k - j] for j in range(1, k + 1)
        )
    return moments
