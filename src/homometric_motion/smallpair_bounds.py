"""All eight exact Taylor-remainder caps for matched-strength skew separation."""

from fractions import Fraction as F
from math import comb, factorial

from .smallpair_algebra import add, exact, multiply, power
from .smallpair_moments import DELTA


def absolute(poly, cap, minimum=0):
    return sum((abs(value) * cap**k for k, value in enumerate(poly) if k >= minimum), F(0))


def class_bounds(prepared, cap):
    polynomials, constants = prepared["raw_polynomials"], prepared["A"]
    m = {r: absolute(polynomials[r], cap) for r in (1, 2, 3)}
    errors = {r: constants[r] * cap ** (17 - r) for r in (1, 2, 3)}
    e1, e2, e3 = (errors[r] for r in (1, 2, 3))
    ev = e2 + e1 * (2 * m[1] + e1)
    ec = (
        e3
        + 3 * (m[1] * e2 + m[2] * e1 + e1 * e2)
        + 6 * m[1] ** 2 * e1
        + 6 * m[1] * e1**2
        + 2 * e1**3
    )
    variance, third = prepared["variance_polynomial"], prepared["third_polynomial"]
    vt, ct = absolute(variance, cap, 1), absolute(third, cap, 1)
    return {
        "raw_polynomial_absolute_bounds": m,
        "raw_error_bounds": errors,
        "raw_error_divided_by_s_bounds": {r: errors[r] / cap for r in (1, 2, 3)},
        "variance_error": ev,
        "third_error": ec,
        "variance_error_divided_by_s": ev / cap,
        "third_error_divided_by_s": ec / cap,
        "variance_polynomial_absolute_bound": absolute(variance, cap),
        "third_polynomial_absolute_bound": absolute(third, cap),
        "normalized_variance": {"lower": variance[0] - vt - ev, "upper": variance[0] + vt + ev},
        "normalized_third": {"lower": third[0] - ct - ec, "upper": third[0] + ct + ec},
    }


def product_error(c_record, v_record, cap):
    ch, ec = c_record["third_polynomial_absolute_bound"], c_record["third_error"]
    vh, ev = v_record["variance_polynomial_absolute_bound"], v_record["variance_error"]
    square, cube = F(0), F(0)
    for i in range(3):
        for j in range(4):
            if i == j == 0:
                continue
            term = F(comb(2, i) * comb(3, j)) * ch ** (2 - i) * vh ** (3 - j) * ec**i * ev**j / cap
            if i:
                square += term
            else:
                cube += term
    return {
        "cumulant_square_error_term": square,
        "variance_cube_error_term": cube,
        "sum": square + cube,
    }


def remainder_evidence(raw, full_polynomials, check):
    prepared, jets = {}, {}
    for side in ("A", "B"):
        p, constants, raw_jets = {}, {}, {}
        for order in (1, 2, 3):
            coefficients = raw[side + "_mu" + str(order)]
            jet = [
                sum(
                    (F(value) * (-DELTA * k) ** j for k, value in enumerate(coefficients) if value),
                    F(0),
                )
                / factorial(j)
                for j in range(17)
            ]
            check(all(x == 0 for x in jet[:order]), "exact zeros before strength normalization")
            p[order] = jet[order:]
            constants[order] = sum(
                (
                    F(abs(value)) * (DELTA * k) ** 17
                    for k, value in enumerate(coefficients)
                    if value
                ),
                F(0),
            ) / factorial(17)
            raw_jets[order] = jet
        variance = add(p[2], power(p[1], 2), -1)
        third = add(add(p[3], multiply(p[1], p[2]), -3), power(p[1], 3), 2)
        check(variance[0] > 0 and third[0] > 0, "positive leading variance and third cumulant")
        prepared[side] = {
            "raw_polynomials": p,
            "A": constants,
            "variance_polynomial": variance,
            "third_polynomial": third,
        }
        jets[side] = raw_jets
    cross = add(
        multiply(
            power(prepared["B"]["third_polynomial"], 2),
            power(prepared["A"]["variance_polynomial"], 3),
        ),
        multiply(
            power(prepared["A"]["third_polynomial"], 2),
            power(prepared["B"]["variance_polynomial"], 3),
        ),
        -1,
    )
    check(
        cross[0] == 0 and cross[1] > 0,
        "shared leading cancellation and positive next cross coefficient",
    )
    direct_leading = sum(
        (
            F(value) * (-DELTA * k) ** 13
            for k, value in enumerate(full_polynomials["cross_P"])
            if value
        ),
        F(0),
    ) / factorial(13)
    check(
        direct_leading == cross[1],
        "full exact cross polynomial agrees with local remainder normalization",
    )
    rows, passing = [], []
    for exponent in range(8, 0, -1):
        cap = F(1, 10**exponent)
        classes = {side: class_bounds(prepared[side], cap) for side in ("A", "B")}
        ba, ab = (
            product_error(classes["B"], classes["A"], cap),
            product_error(classes["A"], classes["B"], cap),
        )
        tail = sum((abs(value) * cap ** (j - 1) for j, value in enumerate(cross) if j >= 2), F(0))
        h = cross[1] - tail - ba["sum"] - ab["sum"]
        conditions = {
            "positive_normalized_variance_A": classes["A"]["normalized_variance"]["lower"] > 0,
            "positive_normalized_variance_B": classes["B"]["normalized_variance"]["lower"] > 0,
            "positive_normalized_third_A": classes["A"]["normalized_third"]["lower"] > 0,
            "positive_normalized_third_B": classes["B"]["normalized_third"]["lower"] > 0,
            "positive_normalized_cross_over_s_lower": h > 0,
        }
        certified, band = all(conditions.values()), None
        if certified:
            passing.append(cap)
            squared = (
                cap
                * h
                / (
                    2
                    * classes["A"]["normalized_variance"]["upper"] ** 3
                    * classes["B"]["normalized_variance"]["upper"] ** 3
                )
            )
            upper = {}
            for side in ("A", "B"):
                q = (
                    classes[side]["normalized_third"]["upper"] ** 2
                    / classes[side]["normalized_variance"]["lower"] ** 3
                )
                check(
                    (1 + q) ** 2 - 4 * q == (q - 1) ** 2 >= 0, "root-free positive skew upper bound"
                )
                upper[side] = (1 + q) / 2
            band = {
                "common_s_interval": {"lower": cap / 2, "upper": cap},
                "squared_skewness_gap_B_minus_A_lower": squared,
                "skewness_gap_B_minus_A_lower": squared / sum(upper.values()),
                "positive_skew_upper_bounds": upper,
                "beta_interval_formula": "[S/omega^2,2S/omega^2], omega=2*pi/3",
            }
        rows.append(
            {
                "cap": cap,
                "status": "CERTIFIED_POSITIVE_SHAPE_GAP"
                if certified
                else "UNRESOLVED_BY_THIS_BOUND",
                "conditions": conditions,
                "classes": classes,
                "proxy_higher_terms_over_s_upper": tail,
                "product_BA_error_divided_by_s": ba,
                "product_AB_error_divided_by_s": ab,
                "normalized_cross_over_s_lower": h,
                "band_certificate": band,
            }
        )
    check(
        len(passing) == 7 and max(passing) == F(1, 100) and rows[-1]["band_certificate"] is None,
        "all declared remainder outcomes including unresolved cap",
    )
    selected = next(row for row in rows if row["cap"] == F(1, 100))
    check(
        selected["band_certificate"]["squared_skewness_gap_B_minus_A_lower"] > F(2112604491, 10**12)
        and selected["band_certificate"]["skewness_gap_B_minus_A_lower"] > F(403302035, 10**12),
        "exact weaker readable gap bounds",
    )
    return exact(
        {
            "raw_taylor_coefficients_through16": jets,
            "prepared_polynomials_and_remainder_constants": prepared,
            "normalized_cross_proxy_coefficients": cross,
            "positive_linear_coefficient": cross[1],
            "rows": rows,
            "passing_count": len(passing),
            "largest_passing_predeclared_cap": max(passing),
            "readable_exact_lower_bounds_at_S_1_over_100": {
                "squared_skew_gap": F(2112604491, 10**12),
                "skew_gap": F(403302035, 10**12),
            },
            "comparison_contract": "Pointwise SAME calibrated s; the uniform band gap is not separation of independently selected class-strength intervals.",
            "method": "Degree16 signed exponential Taylor polynomials with exact seventeenth-order remainder, normalized only after exact zeros.",
        }
    )
