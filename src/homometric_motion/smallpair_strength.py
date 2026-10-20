"""Exact local bands for independently fixed strengths and calibrated intensity."""

from fractions import Fraction as F
from math import comb, factorial, lcm

from .arithmetic import rational_from_text, rational_text
from .smallpair_algebra import add, bounded, evaluate, exact, trim

CENTER = F(13, 16)
RADII = (F(1, 16), F(1, 64), F(1, 256), F(1, 1024), F(1, 4096))
MAX_DEGREE = 320
MAX_BITS = 131072
MAX_UPDATES = 5_000_000


def _bound(values):
    for value in values:
        value = F(value)
        if max(abs(value.numerator).bit_length(), value.denominator.bit_length()) > MAX_BITS:
            raise ValueError("strength-band coefficient bit limit")


def _derivative(poly):
    bounded(poly)
    return [i * poly[i] for i in range(1, len(poly))] or [F(0)]


def _inverse_identity(numerators, transformed, degree, scale):
    return [
        comb(degree, i) * sum((-1) ** (i - k) * comb(i, k) * numerators[k] for k in range(i + 1))
        == transformed[i] * scale
        for i in range(degree + 1)
    ]


def _bernstein(poly, left, right, budget, check):
    poly = trim(list(map(F, poly)))
    degree = len(poly) - 1
    if not 0 <= degree <= MAX_DEGREE or not 0 <= left < right <= 1:
        raise ValueError("bounded degree and ordered unit interval required")
    cost = 3 * (degree + 1) * (degree + 2) // 2
    if budget[0] + cost > MAX_UPDATES:
        raise ValueError("strength-band cumulative transform budget before calculation")
    budget[0] += cost
    denominator = lcm(*(x.denominator for x in poly))
    integer_coefficients = [int(x * denominator) for x in poly]
    endpoint_denominator = lcm(left.denominator, right.denominator)
    origin = int(left * endpoint_denominator)
    width = int((right - left) * endpoint_denominator)
    origin_powers = [origin**j for j in range(degree + 1)]
    denominator_powers = [endpoint_denominator**j for j in range(degree + 1)]
    width_powers = [width**j for j in range(degree + 1)]
    transformed = [
        width_powers[k]
        * sum(
            integer_coefficients[j]
            * comb(j, k)
            * origin_powers[j - k]
            * denominator_powers[degree - j]
            for j in range(k, degree + 1)
        )
        for k in range(degree + 1)
    ]
    factorials = [factorial(j) for j in range(degree + 1)]
    numerators = [
        sum(
            transformed[i] * comb(k, i) * factorials[i] * factorials[degree - i]
            for i in range(k + 1)
        )
        for k in range(degree + 1)
    ]
    scale = denominator * endpoint_denominator**degree * factorials[degree]
    _bound(transformed + numerators + [scale])
    for identity in _inverse_identity(numerators, transformed, degree, factorials[degree]):
        check(identity, "strength-band exact inverse Bernstein coefficient")
    check(F(numerators[0], scale) == evaluate(poly, left), "strength-band left endpoint")
    check(F(numerators[-1], scale) == evaluate(poly, right), "strength-band right endpoint")
    low, high = min(numerators), max(numerators)
    return (
        {
            "degree": degree,
            "interval": {"lower": left, "upper": right},
            "bernstein_numerators": [rational_text(x) for x in numerators],
            "positive_common_denominator": rational_text(scale),
            "range": {"lower": F(low, scale), "upper": F(high, scale)},
            "extremal_coefficient_indices": {
                "minimum": numerators.index(low),
                "maximum": numerators.index(high),
            },
            "inverse_conversion_checked": True,
        },
        numerators,
        transformed,
        factorials[degree],
    )


def _separation(first, second):
    a_below = second["lower"] - first["upper"]
    b_below = first["lower"] - second["upper"]
    if a_below > 0:
        return {
            "status": "CERTIFIED_A_BELOW_B",
            "positive_gap": a_below,
            "orientation": "B_minus_A",
        }
    if b_below > 0:
        return {
            "status": "CERTIFIED_B_BELOW_A",
            "positive_gap": b_below,
            "orientation": "A_minus_B",
        }
    return {
        "status": "UNRESOLVED_RANGE_OVERLAP",
        "positive_gap": None,
        "A_below_B_signed_gap": a_below,
        "B_below_A_signed_gap": b_below,
    }


def _compact_matched_bound(mean, attempt, left, right, check):
    """Use freshly generated identity and positive factors, at the same t only."""
    witness = attempt["integer_bezout"]
    a = [rational_from_text(x) for x in witness["A_for_H"]]
    b = [rational_from_text(x) for x in witness["B_for_difference"]]
    constant = rational_from_text(witness["positive_constant"])
    raw_denominator = rational_from_text(attempt["positive_difference_denominator"])
    check(
        constant > 0
        and raw_denominator > 0
        and all(x.denominator == 1 for x in a + b + [constant, raw_denominator]),
        "strength-band positive integer Bezout witness",
    )
    factors = mean["factorization"]
    fmin = (
        rational_from_text(factors["positive_content"])
        * left ** factors["t_zero_multiplicity"]
        * (1 - right) ** factors["one_minus_t_multiplicity"]
    )
    for factor in factors["positive_simple_factors"]:
        coefficients = [rational_from_text(x) for x in factor["coefficients"]]
        check(
            coefficients[0] > 0 and all(x >= 0 for x in coefficients),
            "strength-band increasing positive cofactor",
        )
        fmin *= evaluate(coefficients, left) ** factor["multiplicity"]
    amax = evaluate(list(map(abs, a)), right)
    bmax = evaluate(list(map(abs, b)), right)
    denominator = amax / fmin + raw_denominator * bmax
    gap = constant / denominator
    check(
        fmin > 0 and amax >= 0 and bmax >= 0 and denominator > 0 and gap > 0,
        "positive compact same-strength joint-moment gap",
    )
    check(gap * denominator == constant, "compact same-strength exact identity")
    _bound([fmin, amax, bmax, denominator, gap])
    return {
        "scope": "Same t only; not independent-strength separation",
        "F_lower": fmin,
        "A_absolute_upper": amax,
        "B_absolute_upper": bmax,
        "positive_raw_difference_denominator": rational_text(raw_denominator),
        "positive_constant": rational_text(constant),
        "max_absolute_joint_moment_gap_lower": gap,
    }


def strength_bands(raw, mean, joint, check):
    """Retain full class ranges for all five fixed independent-strength bands."""
    budget = [0]
    control, numerators, transformed, scale = _bernstein(
        [F(1), F(-1), F(1)], F(0), F(1), budget, check
    )
    check(
        control["range"] == {"lower": F(1, 2), "upper": F(1)},
        "strength-band mixed-power Bernstein control",
    )
    corrupt = numerators.copy()
    corrupt[1] += 1
    check(
        not all(_inverse_identity(corrupt, transformed, 2, scale)),
        "strength-band corrupted Bernstein coefficient rejected",
    )
    affine, _, _, _ = _bernstein([F(2), F(-3)], F(1, 4), F(3, 4), budget, check)
    check(
        affine["range"] == {"lower": F(-1, 4), "upper": F(5, 4)},
        "strength-band affine exact range",
    )
    check(
        rational_from_text(rational_text(10**5000 + 9)) == 10**5000 + 9,
        "strength-band long integer conversion control",
    )
    check(
        len(joint["attempts"]) == 1
        and joint["attempts"][0]["raw_moment_order"] == 2
        and joint["attempts"][0]["unit_gcd"],
        "strength-band fresh primary joint identity",
    )
    attempt = joint["attempts"][0]
    polynomials = {
        side: {"mu" + str(order): list(map(F, raw[side + "_mu" + str(order)])) for order in (1, 2)}
        for side in ("A", "B")
    }
    derivatives = {
        side: {name: evaluate(_derivative(poly), CENTER) for name, poly in group.items()}
        for side, group in polynomials.items()
    }
    numerator = derivatives["A"]["mu2"] + derivatives["B"]["mu2"]
    denominator = derivatives["A"]["mu1"] + derivatives["B"]["mu1"]
    coefficient = numerator / denominator if denominator else None
    if coefficient is not None:
        for side in ("A", "B"):
            polynomials[side]["projection"] = add(
                polynomials[side]["mu2"], polynomials[side]["mu1"], -coefficient
            )
            derivatives[side]["projection"] = evaluate(
                _derivative(polynomials[side]["projection"]), CENTER
            )
        check(
            derivatives["A"]["projection"] + derivatives["B"]["projection"] == 0,
            "one common projection cancels only pooled derivative",
        )
    rows = []
    for radius in RADII:
        left, right = CENTER - radius, CENTER + radius
        check(0 < left < right < 1, "fixed strength band strictly inside unit interval")
        classes = {}
        for side in ("A", "B"):
            classes[side] = {}
            for name, poly in polynomials[side].items():
                witness, _, _, _ = _bernstein(poly, left, right, budget, check)
                classes[side][name] = witness
        tests = {
            name: _separation(classes["A"][name]["range"], classes["B"][name]["range"])
            for name in polynomials["A"]
        }
        if coefficient is None:
            tests["projection"] = {
                "status": "UNRESOLVED_PROJECTION_DENOMINATOR_ZERO",
                "positive_gap": None,
            }
        rows.append(
            {
                "radius": radius,
                "t_interval": {"lower": left, "upper": right},
                "strength_interval_exact": {
                    "s_lower": f"-(158/9)*log({right})",
                    "s_upper": f"-(158/9)*log({left})",
                    "beta_lower": f"-(79/pi^2)*log({right})",
                    "beta_upper": f"-(79/pi^2)*log({left})",
                },
                "classes": classes,
                "independent_strength_range_tests": tests,
                "matched_strength_joint_gap": _compact_matched_bound(
                    mean, attempt, left, right, check
                ),
            }
        )
    passing = [
        row
        for row in rows
        if row["independent_strength_range_tests"]["projection"]["status"].startswith("CERTIFIED_")
    ]
    check(len(rows) == 5, "all five fixed strength bands retained")
    return exact(
        {
            "status": "CERTIFIED_INDEPENDENT_STRENGTH_SEPARATION"
            if passing
            else "INDEPENDENT_STRENGTH_SEPARATION_UNRESOLVED",
            "center": CENTER,
            "projection_coefficient": coefficient,
            "coefficient_rule_values": {"numerator": numerator, "denominator": denominator},
            "class_specific_center_derivatives": derivatives,
            "polynomials_ascending": polynomials,
            "rows": rows,
            "passing_projection_radii": [row["radius"] for row in passing],
            "largest_declared_passing_radius": max(
                (row["radius"] for row in passing), default=None
            ),
            "transform_updates": budget[0],
            "observable": "One common calibrated raw-intensity observable f(I)=I^2-c*I.",
            "scope": [
                "Each class may choose its fixed strength independently within the same passing band.",
                "The entire two class expectation ranges of one common observable must be disjoint.",
                "Settings remain fixed within each acquisition; no arbitrary mixtures or drift.",
                "Overlapping enclosing ranges are unresolved, not evidence of equal laws or intersecting curves.",
                "The separate compact Bezout bounds apply only at the same strength.",
                "No unknown gain/background, exposure, covariance/frequency error, classifier or finite-count guarantee.",
            ],
            "selection_disclosure": (
                "The fixed center 13/16 follows known mean-crossover evidence. This release "
                "reproduces the already reviewed pooled-tangent rule and all five bands; "
                "it is informed construction, not a new blind selection or preregistration."
            ),
        }
    )
