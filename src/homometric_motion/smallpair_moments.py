"""Complete finite Gaussian moment polynomials and bounded global sign evidence."""

from collections import defaultdict
from fractions import Fraction as F
from math import lcm

from .arithmetic import rational_text
from .smallpair_algebra import (
    add,
    bounded,
    coefficient_sign,
    endpoint_reduce,
    evaluate,
    homogeneous_transform,
    multiply,
    power,
    texts,
)

DELTA = F(9, 158)


def raw_moments(classes, check):
    raw, records = {}, {}
    for side, item in classes.items():
        points, covariance = item["points"], item["D"]
        denominator = lcm(*(x.denominator for row in covariance for x in row))
        matrix = [[int(x * denominator) for x in row] for row in covariance]
        base = defaultdict(int)
        for i in range(9):
            for j in range(9):
                vector = [0] * 9
                vector[i] += 1
                vector[j] -= 1
                base[tuple(vector)] += 1
        states = {(0,) * 9: 1}
        rows = {}
        for order in (1, 2, 3):
            if len(states) > 1405 or len(base) != 73:
                raise ValueError("fixed ordered-index state bound before convolution")
            following = defaultdict(int)
            for a, x in states.items():
                for b, y in base.items():
                    following[tuple(i + j for i, j in zip(a, b))] += x * y
            states = following
            check(
                len(states) <= 13237 and sum(states.values()) == 9 ** (2 * order),
                "complete bounded ordered moment expansion",
            )
            real, imaginary = defaultdict(int), defaultdict(int)
            for vector, multiplicity in states.items():
                active = [(i, x) for i, x in enumerate(vector) if x]
                numerator = sum(x * matrix[i][j] * y for i, x in active for j, y in active)
                exponent = F(numerator, denominator) / DELTA
                check(
                    exponent.denominator == 1 and 0 <= exponent <= 80 * order**2,
                    "nonnegative exact moment exponent lattice",
                )
                residue = sum(x * point for x, point in zip(vector, points)) % 3
                a, b = ((1, 0), (0, 1), (-1, -1))[residue]
                real[int(exponent)] += multiplicity * a
                imaginary[int(exponent)] += multiplicity * b
            check(
                all(x == 0 for x in imaginary.values()),
                "exact phase-ring cancellation at every exponent",
            )
            coefficients = bounded([real[k] for k in range(max(real) + 1)])
            check(
                coefficients[-1] != 0 and sum(coefficients) == 0,
                "complete raw moment degree and clean null",
            )
            raw[side + "_mu" + str(order)] = coefficients
            rows[str(order)] = {
                "degree": len(coefficients) - 1,
                "denominator": "1",
                "coefficients": texts(coefficients),
                "exponential_sum": [
                    {"variogram": rational_text(DELTA * k), "coefficient": rational_text(value)}
                    for k, value in enumerate(coefficients)
                    if value
                ],
                "ordered_tuple_count": 9 ** (2 * order),
                "difference_vector_count": len(states),
            }
        records[side] = rows
    return raw, {"delta": str(DELTA), "classes": records}


def fraction_record(value):
    return {
        "numerator": rational_text(value.numerator),
        "denominator": rational_text(value.denominator),
        "sign": (value > 0) - (value < 0),
    }


def shape_evidence(raw, check):
    polynomials = dict(raw)
    for side in ("A", "B"):
        m1, m2, m3 = (raw[side + "_mu" + str(order)] for order in (1, 2, 3))
        polynomials[side + "_variance"] = add(m2, power(m1, 2), -1)
        polynomials[side + "_third"] = add(add(m3, multiply(m1, m2), -3), power(m1, 3), 2)
    polynomials["cross_P"] = add(
        multiply(power(polynomials["B_third"], 2), power(polynomials["A_variance"], 3)),
        multiply(power(polynomials["A_third"], 2), power(polynomials["B_variance"], 3)),
        -1,
    )
    records, reductions, verdicts = {}, {}, {}
    budget, retained = [0], 0
    check(homogeneous_transform([1, -1, 1], 1, budget) == [1, 1, 1], "fixed Bernstein control")
    for label, poly in polynomials.items():
        zero, one, content, residual = endpoint_reduce(poly, check)
        bernstein = homogeneous_transform(residual, 1, budget)
        check(
            homogeneous_transform(bernstein, -1, budget) == residual,
            "entire homogeneous Bernstein inverse",
        )
        mono, bern = coefficient_sign(residual), coefficient_sign(bernstein)
        known = {x["verdict"] for x in (mono, bern) if x["verdict"] in ("POSITIVE", "NEGATIVE")}
        check(len(known) <= 1, "compatible global sufficient sign tests")
        verdict = next(iter(known)) if known else "UNRESOLVED"
        verdicts[label] = verdict
        reductions[label] = (zero, one, content, residual)
        retained += len(poly) + len(residual) + len(bernstein)
        if retained > 100000:
            raise ValueError("retained polynomial coefficient limit")
        records[label] = {
            "degree": len(poly) - 1,
            "denominator": "1",
            "numerator_coefficients": texts(poly),
            "endpoint_reduction": {
                "t_zero_multiplicity": zero,
                "one_minus_t_multiplicity": one,
                "positive_content": rational_text(content),
                "residual_coefficients": texts(residual),
                "residual_at_zero": rational_text(residual[0]),
                "residual_at_one": rational_text(sum(residual)),
            },
            "leading_s_coefficient": fraction_record(F(content * sum(residual)) * DELTA**one),
            "monomial_sign_test": mono,
            "bernstein_sign_test": bern,
            "bernstein_scaled_coefficients": texts(bernstein),
            "global_sign_certificate": verdict,
        }
    diagnostics, signs = [], {}
    for j in range(1, 16):
        values = {label: evaluate(poly, F(j, 16)) for label, poly in polynomials.items()}
        for label, verdict in verdicts.items():
            if verdict in ("POSITIVE", "NEGATIVE"):
                check(
                    (values[label] > 0) if verdict == "POSITIVE" else (values[label] < 0),
                    "global sign agrees at declared rational point",
                )
        variances = all(values[s + "_variance"] > 0 for s in ("A", "B"))
        thirds = all(values[s + "_third"] > 0 for s in ("A", "B"))
        cross = values["cross_P"]
        sign = (cross > 0) - (cross < 0)
        signs[j] = sign
        diagnostics.append(
            {
                "t_numerator": j,
                "t_denominator": 16,
                "values": {label: fraction_record(value) for label, value in values.items()},
                "both_variances_positive": variances,
                "both_third_cumulants_positive": thirds,
                "squared_shape_difference_B_minus_A_sign": sign,
                "unsquared_shape_difference_B_minus_A_sign_if_positive_thirds": sign
                if thirds
                else None,
            }
        )
    residual = reductions["cross_P"][3]
    nodes = [
        (0, (residual[0] > 0) - (residual[0] < 0)),
        *sorted(signs.items()),
        (16, (sum(residual) > 0) - (sum(residual) < 0)),
    ]
    nonzero = [(j, value) for j, value in nodes if value]
    changes = [
        {
            "left_t": str(F(a, 16)),
            "right_t": str(F(b, 16)),
            "left_residual_sign": sa,
            "right_residual_sign": sb,
        }
        for (a, sa), (b, sb) in zip(nonzero, nonzero[1:])
        if sa * sb < 0
    ]
    globally_positive = all(
        verdicts[s + kind] == "POSITIVE" for s in ("A", "B") for kind in ("_variance", "_third")
    )
    check(globally_positive, "positive variances and third cumulants throughout open interval")
    check(len(changes) >= 2, "at least two matched-strength shape reversals")
    return polynomials, {
        "status": "EXACT_CROSS_PRODUCT_SIGN_CHANGE",
        "polynomials": records,
        "diagnostics": diagnostics,
        "global_sign_certificates": verdicts,
        "cross_product_sign_change_witnesses": changes,
        "declared_interior_cross_zeros": [
            str(F(j, 16)) for j, value in signs.items() if value == 0
        ],
        "globally_positive_variances_and_third_cumulants": globally_positive,
        "number_of_interior_cross_roots": "AT_LEAST_TWO; exact total not asserted",
        "global_shape_order": "FALSE_IN_EITHER_DIRECTION",
        "retained_coefficient_count": retained,
        "homogeneous_transform_updates": budget[0],
        "scope": "Same strength in both classes. Residual endpoint signs, not trivial original endpoint zeros, justify the two interior brackets.",
    }
