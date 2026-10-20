"""Signed small-time kernel bounds with a complete fixed time cover."""

from fractions import Fraction as F

from .arithmetic import Interval as I72
from .arithmetic import rational_text
from .geometry import exact_covariance
from .kernel_arithmetic import KernelInterval as I
from .kernel_arithmetic import fraction
from .robustness import interval as interval72

TIME_CELLS = 512


def _product(a, b):
    return [
        [sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))]
        for i in range(len(a))
    ]


def _trace(a):
    return sum(a[i][i] for i in range(len(a)))


def _trace_product(*matrices):
    result = matrices[0]
    for matrix in matrices[1:]:
        result = _product(result, matrix)
    return _trace(result)


def _complex_product(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def _phases(check):
    root3 = I(3).root(2)
    ct, st = I(74).root(2) / (5 * root3), 1 / (5 * root3)
    cp, sp = I(191).root(2) / (8 * root3), -1 / (8 * root3)
    motif = []
    zeta = I(F(1, 2)), root3 / 2
    for index in range(10):
        motif.append((I((-1) ** index), I(0)) if index < 2 else (((-1) ** index) * cp, sp))
        motif.append(_complex_product(zeta, (((-1) ** index) * ct, st)))
    motif.append((I(1), I(0)))
    check(
        F(74, 75) + F(1, 75) == 1 and F(191, 192) + F(1, 192) == 1,
        "kernel exact phase unit identities",
    )
    check(
        1 - 5 * F(1, 5) == 0 and 5 * F(1, 5) - 8 * F(1, 8) == 0,
        "kernel exact motif null coefficients",
    )
    return {
        side: motif + [_complex_product(factor, z) for z in motif] + [(-x, -y) for x, y in motif]
        for side, factor in (("A", zeta), ("B", (I(F(-1, 2)), root3 / 2)))
    }


def _parity_constants(nominal, covariance, check):
    """Recompute the original 72-place parity constants, including odd L2."""
    omega = interval72(nominal["omega"])
    beta = I72(fraction(nominal["beta_cap_exact"]))
    epsilon = fraction(covariance["epsilon_exact"])
    result = {}
    for side in ("A", "B"):
        base, marginal = nominal["classes"][side], covariance["classes"][side]
        matrix, trace = exact_covariance(side, check)
        check(trace == fraction(base["trace_Lplus_exact"]), side + " kernel exact trace")
        q = interval72(marginal["q_enclosure"])
        p2 = interval72(marginal["abs_p_squared_enclosure"])
        energy = {
            k: I72(fraction(base["energy_raw_moments_exact"][str(k)])) * (1 + epsilon) ** k
            for k in (4, 6)
        }
        diagonal = sum(I72(matrix[i][i]) * I72(matrix[i][i]).root(2) for i in range(63))
        diagonal = diagonal * (I72(1 + epsilon) ** 3).root(2)
        v0 = omega**4 * (q**2 + p2)
        k30 = omega**6 * (2 * q**3 + 6 * q * p2)
        m4c = omega**8 * (9 * q**4 + 42 * q**2 * p2 + 9 * p2**2)
        s4 = omega * (2 * q**2 + p2).root(4)
        s6 = omega * (6 * q**3 + 9 * q * p2).root(6)
        c4 = omega**2 * energy[4].root(4) / 2
        c6 = omega**2 * energy[6].root(6) / 2
        e4 = omega**3 * I72(10395).root(4) * diagonal / 6
        e6 = omega**3 * I72(34459425).root(6) * diagonal / 6
        even2 = beta * (2 * s4 * e4 + c4**2) + beta**2 * e4**2
        odd2 = 4 * beta * c4**2 * (s4 + beta * e4) ** 2
        sd0 = v0.root(2)
        check(sd0.lower > even2.upper, side + " kernel positive marginal variance")
        variance = I72.bounds((sd0.lower - even2.upper) ** 2, ((sd0 + even2) ** 2 + odd2).upper)
        even3 = 2 * beta * (2 * s6 * e6 + c6**2) + 2 * beta**2 * e6**2
        odd3 = 4 * beta * c6**2 * (s6 + beta * e6) ** 2
        x3 = (v0 * m4c).root(6)
        err3 = 3 * x3**2 * even3 + 3 * x3 * even3**2 + even3**3 + 3 * (x3 + even3) * odd3
        third = I72.bounds(k30.lower - err3.upper, k30.upper + err3.upper)
        check(
            variance.record() == marginal["normalized_variance"],
            side + " kernel fresh marginal variance agreement",
        )
        check(
            third.record() == marginal["normalized_third_cumulant"],
            side + " kernel fresh marginal third agreement",
        )
        check(
            fraction(marginal["third_cumulant_error_upper"]) == err3.upper,
            side + " kernel fresh parity error agreement",
        )
        result[side] = {
            "leading_variance": v0.record(),
            "leading_third_cumulant": k30.record(),
            "even_L2_upper_exact": rational_text(even2.upper),
            "odd_L2_squared_upper_exact": rational_text(odd2.upper),
            "finite_motion_third_error_upper_exact": rational_text(err3.upper),
        }
    return result


def kernel_constants(nominal, covariance, check):
    """Fresh projected matrices, derivative and uniform remainder bounds."""
    omega = I.from_record(nominal["omega"])
    epsilon = fraction(covariance["epsilon_exact"])
    check(epsilon == F(1, 100000), "kernel fixed covariance radius")
    delta = epsilon / (1 + epsilon)
    phase = _phases(check)
    parity = _parity_constants(nominal, covariance, check)
    result = {}
    for side in ("A", "B"):
        base = nominal["classes"][side]
        q0, rp, ip = (I.from_record(base[key]) for key in ("q", "real_p", "imag_p"))
        k_nominal = [
            [omega**2 * (q0 + rp) / 2, omega**2 * ip / 2],
            [omega**2 * ip / 2, omega**2 * (q0 - rp) / 2],
        ]
        c = F(63) / fraction(base["trace_Lplus_exact"])
        gram = [
            [c * omega**2 * sum(z[i] * z[j] for z in phase[side]) for j in range(2)]
            for i in range(2)
        ]
        g = _trace(gram)
        m = (g + ((gram[0][0] - gram[1][1]) ** 2 + 4 * gram[0][1] ** 2).root(2)) / 2
        k_nom = omega**2 * (q0 + I.from_record(base["abs_p_squared"]).root(2)) / 2
        k_upper = (1 + epsilon) * k_nom.hi
        edges = [(j, j + 1) for j in range(62)] + [(20, 22) if side == "A" else (41, 43)]
        energy = sum(
            (phase[side][i][0] - phase[side][j][0]) ** 2
            + (phase[side][i][1] - phase[side][j][1]) ** 2
            for i, j in edges
        )
        h = c * (1 + delta) * omega**2 * energy
        d2nom = _trace_product(k_nominal, gram)
        d3nom = _trace_product(k_nominal, k_nominal, gram)
        check(
            d2nom.lo > 0 and d3nom.lo > 0,
            side + " kernel positive projected contractions",
        )
        d2 = I((1 - epsilon) * d2nom.lo, (1 + epsilon) * d2nom.hi)
        coarse_radius = epsilon * k_nom.hi * g.root(2).hi
        factored_radius = epsilon * I(k_nom.hi * d2nom.hi).root(2).hi
        radius = min(coarse_radius, factored_radius)
        root_d3 = d3nom.root(2)
        d3 = I(max(F(0), root_d3.lo - radius) ** 2, (root_d3.hi + radius) ** 2)
        cv = (m.hi * g.hi + k_upper * h.hi) / 3
        ck = 2 * k_upper**2 * h.hi + F(14, 5) * k_upper * m.hi * g.hi
        check(
            g.lo <= 63 * c * omega.lo**2 <= g.hi,
            side + " kernel phase Gram trace",
        )
        retained = parity[side]
        result[side] = {
            "nominal_K": [[x.record() for x in row] for row in k_nominal],
            "G": [[x.record() for x in row] for row in gram],
            "g": g.record(),
            "m": m.record(),
            "h": h.record(),
            "k_upper": rational_text(k_upper),
            "d2": d2.record(),
            "d3": d3.record(),
            "d3_square_root_perturbation_upper": rational_text(radius),
            "d3_coarse_square_root_perturbation_upper": rational_text(coarse_radius),
            "variance_remainder_coefficient": rational_text(cv),
            "third_remainder_coefficient": rational_text(ck),
            "v0": I.from_record(retained["leading_variance"]).record(),
            "k30": I.from_record(retained["leading_third_cumulant"]).record(),
            "e2": retained["even_L2_upper_exact"],
            "o2": retained["odd_L2_squared_upper_exact"],
            "err3": retained["finite_motion_third_error_upper_exact"],
            "instantaneous_variance_upper": covariance["classes"][side]["normalized_variance"][
                "upper"
            ],
        }
    return result


def enclose_kernel_time(constants, lower, upper):
    """Enclose one actual time interval before any nuisance perturbation."""
    lower, upper = fraction(lower), fraction(upper)
    if not 0 <= lower <= upper:
        raise ValueError("ordered nonnegative kernel time interval required")
    v0, k30, d2, d3 = (I.from_record(constants[name]) for name in ("v0", "k30", "d2", "d3"))
    cv = fraction(constants["variance_remainder_coefficient"])
    ck = fraction(constants["third_remainder_coefficient"])
    v_leading = I(
        max(F(0), v0.lo - F(4, 3) * d2.hi * upper),
        min(v0.hi, v0.hi - F(4, 3) * d2.lo * lower + cv * upper**2),
    )
    k_leading = I(
        k30.lo - 8 * d3.hi * upper - ck * upper**2,
        min(k30.hi, k30.hi - 8 * d3.lo * lower + ck * upper**2),
    )
    sd = v_leading.root(2)
    e2, o2, err3 = (fraction(constants[name]) for name in ("e2", "o2", "err3"))
    variance = I(
        max(F(0), sd.lo - e2) ** 2,
        min((sd.hi + e2) ** 2 + o2, fraction(constants["instantaneous_variance_upper"])),
    )
    third = I(k_leading.lo - err3, k_leading.hi + err3)
    output = {
        "time_interval": list(map(rational_text, (lower, upper))),
        "leading_variance": v_leading.record(),
        "leading_third": k_leading.record(),
        "leading_sd": sd.record(),
    }
    if variance.lo <= 0:
        return {**output, "status": "UNRESOLVED_NONPOSITIVE_VARIANCE"}
    variance_sd = variance.root(2)
    skew = third / (variance * variance_sd)
    return {
        **output,
        "variance": variance.record(),
        "third": third.record(),
        "variance_sd": variance_sd.record(),
        "skewness": skew.record(),
        "status": "ENCLOSED",
    }


def kernel_exposure_certificate(nominal, covariance, exposure_cap, check):
    """Reconstruct signed bounds and all 512 cells on one selected domain.

    This low-level helper also supports an unresolved-cap control. The public
    profile dispatcher separately restricts the admitted published domains.
    """
    cap = fraction(exposure_cap)
    check(0 < cap <= F(1, 10), "kernel supported positive exploration domain")
    constants = kernel_constants(nominal, covariance, check)
    classes = {}
    for side in ("A", "B"):
        cells = [
            enclose_kernel_time(constants[side], cap * j / TIME_CELLS, cap * (j + 1) / TIME_CELLS)
            for j in range(TIME_CELLS)
        ]
        check(len(cells) == TIME_CELLS, side + " kernel complete time cover")
        for j, cell in enumerate(cells):
            check(
                list(map(fraction, cell["time_interval"]))
                == [cap * j / TIME_CELLS, cap * (j + 1) / TIME_CELLS],
                side + " kernel contiguous time cell " + str(j),
            )
        if all(cell["status"] == "ENCLOSED" for cell in cells):
            lows = [fraction(cell["skewness"]["lower"]) for cell in cells]
            highs = [fraction(cell["skewness"]["upper"]) for cell in cells]
            minimum, maximum = min(lows), max(highs)
            classes[side] = {
                "status": "UNIFORMLY_ENCLOSED",
                "skewness": {"lower": rational_text(minimum), "upper": rational_text(maximum)},
                "lower_witness_cell": lows.index(minimum),
                "upper_witness_cell": highs.index(maximum),
                "cells": cells,
            }
        else:
            classes[side] = {"status": "UNRESOLVED_NONPOSITIVE_VARIANCE", "cells": cells}
    complete = all(classes[side]["status"] == "UNIFORMLY_ENCLOSED" for side in ("A", "B"))
    gap = (
        fraction(classes["B"]["skewness"]["lower"]) - fraction(classes["A"]["skewness"]["upper"])
        if complete
        else None
    )
    return {
        "status": "SEPARATED_BY_THIS_BOUND"
        if gap is not None and gap > 0
        else "UNRESOLVED_BY_THIS_BOUND",
        "exposure_cap_exact": rational_text(cap),
        "beta_cap_exact": nominal["beta_cap_exact"],
        "epsilon_exact": covariance["epsilon_exact"],
        "time_cells_per_class": TIME_CELLS,
        "interval_decimal_places": 96,
        "constants": constants,
        "classes": classes,
        "gap_exact": rational_text(gap) if gap is not None else None,
        "scope": (
            "Exact-null stationary weighted OU kernel, signed derivative and remainder "
            "bounds, uniform finite-beta parity transfer and full time-cell cover. "
            "Nuisance propagation and counts are separate stages."
        ),
    }
