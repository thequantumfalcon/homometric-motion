"""Fresh cancellation-aware shape allowance and finite-window count witness."""

from fractions import Fraction as F
from math import comb, factorial

from .arithmetic import integer_root, rational_from_text, rational_text

METHOD = "cancellation_shape_budget_v2"


def _fraction(value):
    return rational_from_text(value) if isinstance(value, str) else F(value)


def _record(value):
    return {"exact": rational_text(value), "display_only": float(value)}


def allocate_shape_budget(observed, nominal, parameters, check):
    """Construct a feasible witness from freshly computed mathematical records.

    This helper does not authenticate supplied records. The public builder must
    obtain them from its fresh, allowlisted theorem chain. No old scale, count
    or threshold is an input to this calculation.
    """
    hlow, hhigh = map(_fraction, parameters["h_interval_exact"])
    blow, bhigh = map(_fraction, parameters["b_interval_exact"])
    check(
        (hlow, hhigh, blow, bhigh) == (F(9, 10), F(11, 10), F(0), F(1)),
        "shape budget fixed channel box",
    )
    check(observed["status"] == "CERTIFIED_SEPARATED", "shape budget separated observation")
    raw = {0: F(1)} | {
        k: max(
            _fraction(observed["classes"][side]["normalized_raw_moment_upper_bounds"][str(k)])
            for side in ("A", "B")
        )
        for k in range(1, 7)
    }
    fm = {
        k: sum(comb(k, j) * hhigh**j * bhigh ** (k - j) * raw[j] for j in range(k + 1))
        for k in range(1, 7)
    }
    second = {
        k: sum(comb(k, j) ** 2 * factorial(j) * fm[2 * k - j] for j in range(k + 1))
        for k in range(1, 4)
    }
    amin = hlow**2 * min(
        _fraction(observed["classes"][side]["normalized_variance"]["lower"]) for side in ("A", "B")
    )
    amax = hhigh**2 * max(
        _fraction(observed["classes"][side]["normalized_variance"]["upper"]) for side in ("A", "B")
    )
    check(0 < amin <= amax, "shape budget positive factorial variance interval")
    roots = []

    def root(value, degree, label, places=80):
        scale = 10**places
        argument = value.numerator * scale**degree // value.denominator
        lower_integer = integer_root(argument, degree)
        lower = F(lower_integer, scale)
        upper = lower if lower**degree == value else F(lower_integer + 1, scale)
        check(lower**degree <= value <= upper**degree, "shape budget root " + label)
        roots.append(
            {
                "label": label,
                "degree": degree,
                "decimal_places": places,
                "radicand": rational_text(value),
                "lower": rational_text(lower),
                "upper": rational_text(upper),
            }
        )
        return lower, upper

    sqrtamin = root(amin, 2, "factorial variance lower")[0]
    check(sqrtamin > 0, "shape budget positive normalization root")
    old_linear1 = 3 * fm[2] + 6 * fm[1] ** 2
    linear = {1: 3 * max(amax, fm[1] ** 2 - amin), 2: 3 * fm[1], 3: F(1)}
    check(all(value > 0 for value in linear.values()), "shape budget positive sensitivities")
    radicands = {k: second[k] / linear[k] for k in (1, 2, 3)}
    direction = {
        k: root(radicands[k], 3, "coordinate direction " + str(k), 24)[0] for k in (1, 2, 3)
    }
    check(all(value > 0 for value in direction.values()), "shape budget positive directions")
    shape = {
        side: [_fraction(observed["classes"][side]["skewness"][end]) for end in ("lower", "upper")]
        for side in ("A", "B")
    }
    check(
        0 < shape["A"][0] <= shape["A"][1] < shape["B"][0] <= shape["B"][1],
        "shape budget independent-class ordering",
    )

    def errors(scale):
        t1, t2, t3 = (scale * direction[k] for k in (1, 2, 3))
        e2 = t2 + 2 * fm[1] * t1 + t1 * t1
        e3 = t3 + 3 * fm[1] * t2 + linear[1] * t1 + 3 * t1 * t2 + 6 * fm[1] * t1 * t1 + 2 * t1**3
        return e2, e3

    def relatives(scale):
        e2, e3 = errors(scale)
        return e2 / amin, e3 / (amin * sqrtamin)

    def feasible(scale):
        e2, e3 = relatives(scale)
        if not (0 <= e2 < 1 and 0 <= e3 < min(shape["A"][0], shape["B"][0])):
            return False
        return (shape["A"][1] + e3) ** 2 * (1 + e2) ** 3 < (shape["B"][0] - e3) ** 2 * (1 - e2) ** 3

    low, high = F(0), F(1)
    check(feasible(low), "shape budget zero-origin feasible bracket")
    doublings = 0
    while feasible(high) and doublings < 32:
        low, high = high, 2 * high
        doublings += 1
    check(feasible(low) and not feasible(high), "shape budget initial bracket")
    initial_low, initial_high = low, high
    for _ in range(128):
        mid = (low + high) / 2
        if feasible(mid):
            low = mid
        else:
            high = mid
    check(feasible(low) and not feasible(high), "shape budget final bracket")
    check(high - low == (initial_high - initial_low) / 2**128, "shape budget bracket width")
    scale = F(9, 10) * low
    check(0 < scale < low and feasible(scale), "shape budget strictly interior scale")
    rel2, rel3 = relatives(scale)
    rp = root(1 + rel2, 2, "expanded positive variance")
    rm = root(1 - rel2, 2, "expanded negative variance")
    check(rm[0] > 0, "shape budget positive denominator root")
    expanded = {
        side: [
            (shape[side][0] - rel3) / ((1 + rel2) * rp[1]),
            (shape[side][1] + rel3) / ((1 - rel2) * rm[0]),
        ]
        for side in ("A", "B")
    }
    threshold = (expanded["A"][1] + expanded["B"][0]) / 2
    check(
        0 < expanded["A"][0] <= expanded["A"][1] < threshold < expanded["B"][0] <= expanded["B"][1],
        "shape budget fresh strict classifier threshold",
    )
    for side in ("A", "B"):
        lo, hi = expanded[side]
        check(
            lo**2 * (1 + rel2) ** 3 <= (shape[side][0] - rel3) ** 2,
            side + " shape budget lower endpoint",
        )
        check(
            hi**2 * (1 - rel2) ** 3 >= (shape[side][1] + rel3) ** 2,
            side + " shape budget upper endpoint",
        )
    epsilon = _fraction(parameters["epsilon_exact"])
    trace = max(_fraction(nominal["classes"][side]["trace_Lplus_exact"]) for side in ("A", "B"))
    gamma = 1 / ((1 + epsilon) * trace)
    lag = _fraction(parameters["lag_lower_exact"])
    exposure = _fraction(parameters["exposure_cap_exact"])
    check(lag > exposure > 0, "shape budget positive window gap")
    check(
        _fraction(observed["exposure_cap_exact"]) == exposure,
        "shape budget observation exposure agrees",
    )
    inflation = 1 + 2 / (gamma * (lag - exposure))
    target = _fraction(parameters["target_individual_class_error"])
    check(target == F(1, 20), "shape budget fixed per-class risk")
    tolerances = {k: scale * direction[k] for k in direction}
    risk_numerators = {k: inflation * second[k] / tolerances[k] ** 2 for k in direction}
    numerator = sum(risk_numerators.values())
    unrounded = numerator / target
    windows = -(-unrounded.numerator // unrounded.denominator)
    check(windows - 1 < unrounded <= windows, "shape budget exact ceiling")
    check(windows > 0 and numerator / windows <= target, "shape budget per-class risk")
    e2, e3 = errors(scale)
    check(
        e2 == rel2 * amin and e3**2 <= rel3**2 * amin**3,
        "shape budget normalized polynomial errors",
    )
    return {
        "status": "PASS",
        "allocation_method": METHOD,
        "sufficient_observation_windows": windows,
        "relative_variance_error": _record(rel2),
        "relative_third_error": _record(rel3),
        "cancellation_sensitivity": {
            "factorial_variance_lower": _record(amin),
            "factorial_variance_upper": _record(amax),
            "mean_upper": _record(fm[1]),
            "old_triangle_coefficient": _record(old_linear1),
            "new_linear_coefficient": _record(linear[1]),
            "new_over_old_coefficient": _record(linear[1] / old_linear1),
            "coefficient_improved": linear[1] < old_linear1,
        },
        "direction_radicands": {str(k): rational_text(v) for k, v in radicands.items()},
        "direction": {str(k): _record(v) for k, v in direction.items()},
        "raw_mean_tolerances": {str(k): _record(v) for k, v in tolerances.items()},
        "polynomial_errors": {"variance": _record(e2), "third": _record(e3)},
        "scale": _record(scale),
        "original_shapes": {side: list(map(rational_text, value)) for side, value in shape.items()},
        "expanded_shapes": {
            side: list(map(rational_text, value)) for side, value in expanded.items()
        },
        "threshold_exact": rational_text(threshold),
        "shape_gap": _record(expanded["B"][0] - expanded["A"][1]),
        "risk_numerators": {str(k): _record(v) for k, v in risk_numerators.items()},
        "individual_class_error_upper": _record(numerator / windows),
        "unrounded_count_exact": rational_text(unrounded),
        "inputs": {
            "amin": _record(amin),
            "amax": _record(amax),
            "sqrtamin_lower": _record(sqrtamin),
            "H": _record(inflation),
            "spectral_gap_lower": _record(gamma),
            "factorial_moments": {str(k): _record(v) for k, v in fm.items()},
            "second_moments": {str(k): _record(v) for k, v in second.items()},
        },
        "bracket": {
            "initial": list(map(rational_text, (initial_low, initial_high))),
            "final": list(map(rational_text, (low, high))),
            "doublings": doublings,
            "steps": 128,
            "margin_factor": "9/10",
        },
        "root_certificates": roots,
        "classifier": {
            "threshold_exact": rational_text(threshold),
            "fallback": "A when empirical factorial variance is nonpositive or third cumulant is negative",
            "rule": "Otherwise B iff empirical_third^2 >= threshold^2 * empirical_variance^3",
        },
        "scope": (
            "Fresh feasible cancellation-aware allocation and threshold under fixed "
            "acquisition settings; sufficient per-class bound, not an optimum or a "
            "necessary count. No old classifier or count is transferred."
        ),
    }
