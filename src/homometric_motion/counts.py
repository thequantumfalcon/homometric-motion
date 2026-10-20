"""Exact finite-window classifier bound for the declared count channel."""

from fractions import Fraction as F
from math import comb, isqrt

from .arithmetic import Interval as I
from .arithmetic import rational_text


def ceil(value):
    return -(-value.numerator // value.denominator)


def root_lower(value, check, places=60):
    scale = 10**places
    k = isqrt(value.numerator * scale**2 // value.denominator)
    root = F(k, scale)
    check(root**2 <= value < (root + F(1, scale)) ** 2, "rational root bracket")
    return root


def classify(f1, f2, f3, threshold):
    a = f2 - f1**2
    c = f3 - 3 * f1 * f2 + 2 * f1**3
    return "B" if a > 0 and c >= 0 and c**2 >= threshold**2 * a**3 else "A"


def count_certificate(frequency, nominal, protocol, check):
    """Compute a new sufficient bound using the detuned raw-moment inputs."""
    joint = frequency
    eps = F(joint["epsilon_exact"])
    exposure = F(joint["exposure_cap_exact"])
    detuning = F(joint["frequency_error_cap_exact"])
    check(joint["status"] == "CERTIFIED_SEPARATED", "detuned shape input separates")
    check(
        0 < F(joint["beta_band_exact"]["lower"]) < F(joint["beta_band_exact"]["upper"]),
        "positive frequency-robust strength band",
    )
    cell = joint
    eta = F(protocol["eta_exact"])
    position_scenario = protocol.get("scenario", "exact_geometry") == "position_uncertainty"
    check(0 < eta < 1, "eta domain")
    classes = cell["classes"]
    expanded = {}
    roots = []

    def root80(value, label):
        value = F(value)
        check(value >= 0, "nonnegative count root " + label)
        scale = 10**80
        k = isqrt(value.numerator * scale**2 // value.denominator)
        lo = F(k, scale)
        hi = lo if lo * lo == value else F(k + 1, scale)
        check(lo * lo <= value <= hi * hi, "count root bracket " + label)
        roots.append({"label": label, "radicand": str(value), "lower": str(lo), "upper": str(hi)})
        return lo, hi

    if position_scenario:
        plus_upper = root80(1 + eta, "expanded denominator plus")[1]
        minus_lower = root80(1 - eta, "expanded denominator minus")[0]
        check(minus_lower > 0, "positive expanded denominator")
    for side in ("A", "B"):
        row = classes[side]["skewness"]
        if position_scenario:
            sl, su = F(row["lower"]), F(row["upper"])
            check(eta < sl <= su, side + " positive shape before estimation")
            lo = (sl - eta) / ((1 + eta) * plus_upper)
            hi = (su + eta) / ((1 - eta) * minus_lower)
        else:
            lower = (I(F(row["lower"])) - eta) / ((I(1 + eta) ** 3).root(2))
            upper = (I(F(row["upper"])) + eta) / ((I(1 - eta) ** 3).root(2))
            lo, hi = lower.lower, upper.upper
        expanded[side] = [lo, hi]
        check(0 < lo <= hi, side + " expanded positive shape")
    check(expanded["A"][1] < expanded["B"][0], "expanded intervals separated")
    threshold = (expanded["A"][1] + expanded["B"][0]) / 2
    hlow, hhigh = map(F, protocol["h_interval_exact"])
    blow, bhigh = map(F, protocol["b_interval_exact"])
    check(0 < hlow <= hhigh and 0 <= blow <= bhigh, "compact channel domain")
    upper = {0: F(1)}
    upper.update(
        {
            j: max(F(classes[s]["normalized_raw_moment_upper_bounds"][str(j)]) for s in ("A", "B"))
            for j in range(1, 7)
        }
    )
    factorial = {
        j: sum(comb(j, k) * hhigh**k * bhigh ** (j - k) * upper[k] for k in range(j + 1))
        for j in range(1, 7)
    }
    amin = hlow**2 * min(F(classes[s]["normalized_variance"]["lower"]) for s in ("A", "B"))
    check(amin > 0, "positive factorial variance lower bound")
    f1, f2 = factorial[1], factorial[2]
    L2, L3 = 2 + 2 * f1, 6 + 9 * f1 + 3 * f2 + 6 * f1**2
    amin_root = (
        root80(amin, "factorial variance lower bound")[0]
        if position_scenario
        else root_lower(amin, check)
    )
    tolerance = min(F(1), eta * amin / L2, eta * amin * amin_root / L3)
    check(0 < tolerance <= 1, "raw moment tolerance")
    check(L2 * tolerance <= eta * amin, "second cumulant error")
    check((L3 * tolerance) ** 2 <= eta**2 * amin**3, "third cumulant error")
    seconds = {
        1: factorial[2] + factorial[1],
        2: factorial[4] + 4 * factorial[3] + 2 * factorial[2],
        3: factorial[6] + 9 * factorial[5] + 18 * factorial[4] + 6 * factorial[3],
    }
    radius = eps / (1 + eps)
    check(F(joint["edge_weight_radius_exact"]) == radius, "spring radius relation")
    max_trace = max(F(nominal["classes"][s]["trace_Lplus_exact"]) for s in ("A", "B"))
    gamma = (1 - radius) / max_trace
    lag = F(protocol["lag_lower_exact"])
    check(lag > exposure > 0 and gamma > 0, "positive window gap and mixing bound")
    inflation = 1 + 2 / (gamma * (lag - exposure))
    check(inflation > 1, "conservative window variance inflation")
    numerator = inflation * sum(seconds.values()) / tolerance**2
    target = F(protocol["target_individual_class_error"])
    check(0 < target < F(1, 2), "target error domain")
    raw = numerator / target
    windows = ceil(raw)
    error = numerator / windows
    check(windows - 1 < raw <= windows, "exact ceiling bracket")
    check(error <= target, "exact per-class error certificate")
    check(classify(F(1), F(1), F(1), threshold) == "A", "nonpositive variance fallback")
    check(classify(F(1), F(2), F(0), threshold) == "A", "negative third cumulant fallback")
    for side in ("A", "B"):
        shape = sum(expanded[side]) / 2
        check(
            classify(F(1), F(2), shape + 4, threshold) == side,
            side + " exact threshold control",
        )
    result = {
        "status": "PASS",
        "beta_band_exact": joint["beta_band_exact"],
        "epsilon_exact": rational_text(eps),
        "frequency_error_cap_exact": rational_text(detuning),
        "edge_weight_radius_exact": rational_text(radius),
        "exposure_cap_exact": rational_text(exposure),
        "lag_lower_exact": rational_text(lag),
        "spectral_gap_lower_exact": rational_text(gamma),
        "h_interval_exact": [rational_text(hlow), rational_text(hhigh)],
        "b_interval_exact": [rational_text(blow), rational_text(bhigh)],
        "eta_exact": rational_text(eta),
        "expanded_shape_intervals_exact": {s: list(map(str, row)) for s, row in expanded.items()},
        "threshold_exact": rational_text(threshold),
        "factorial_moment_upper_exact": {str(j): rational_text(x) for j, x in factorial.items()},
        "factorial_variance_lower_exact": rational_text(amin),
        "raw_factorial_second_moment_upper_exact": {
            str(j): rational_text(x) for j, x in seconds.items()
        },
        "L2_exact": rational_text(L2),
        "L3_exact": rational_text(L3),
        "raw_moment_tolerance_exact": rational_text(tolerance),
        "window_variance_inflation_upper_exact": rational_text(inflation),
        "unrounded_window_budget_exact": rational_text(raw),
        "sufficient_observation_windows": windows,
        "individual_class_error_upper_exact": rational_text(error),
        "individual_class_error_upper_display": float(error),
        "scope": "Conditional joint bound for uncertain positive springs, positive strength band, bounded fixed frequency detuning, Gaussian OU covariance, positive exposure, unknown fixed compact gain/background, and dependent count windows.",
        "selection_disclosure": protocol["selection_disclosure"],
        "qualification": "Extremely conservative sufficient existence bound, not practical feasibility or required cost. No physical measurements supplied.",
    }
    if position_scenario:
        check(
            F(joint["position_error_cap_exact"]) == F(protocol["position_error_cap_exact"]),
            "selected position cap agrees",
        )
        result.update(
            {
                "position_error_cap_exact": joint["position_error_cap_exact"],
                "common_alpha_band_exact": joint["common_alpha_band_exact"],
                "target_individual_class_error_exact": rational_text(target),
                "expanded_shape_gap_lower_exact": rational_text(
                    expanded["B"][0] - expanded["A"][1]
                ),
                "intensity_raw_moment_upper_exact": {
                    str(j): rational_text(x) for j, x in upper.items()
                },
                "root_certificates": roots,
                "root_decimal_places": 80,
                "scope": (
                    "Conditional bound with fixed mean-position offsets, preserved permanent "
                    "graphs, bounded fixed frequency error, uncertain positive springs, "
                    "stationary Gaussian OU motion, positive exposure and compact fixed "
                    "gain/background. Actual configurations need not be clean-homometric."
                ),
            }
        )
    return result
