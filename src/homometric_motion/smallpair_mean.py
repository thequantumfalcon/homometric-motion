"""Fresh mean factorization, bounded Sturm isolation and joint-moment identity."""

from fractions import Fraction as F

from .smallpair_algebra import (
    add,
    bezout,
    divide,
    endpoint_reduce,
    evaluate,
    multiply,
    power,
    sturm,
    texts,
    variations,
)


def derive_mean_and_joint(raw, check):
    difference = add(raw["B_mu1"], raw["A_mu1"], -1)
    zero, one, content, residual = endpoint_reduce(difference, check)
    simple_factors = ([1, 1], [1, 1, 1], [1, 0, 1], [1, 0, 0, 0, 1], [1] + [0] * 7 + [1])
    factors, native_factors = [], []
    for factor in simple_factors:
        multiplicity = 0
        while len(residual) >= len(factor):
            quotient, remainder = divide(residual, factor)
            if remainder != [0]:
                break
            check(all(x.denominator == 1 for x in quotient), "integer simple-factor quotient")
            residual = [int(x) for x in quotient]
            multiplicity += 1
            if multiplicity > 80:
                raise ValueError("fixed mean factor multiplicity bound")
        if multiplicity:
            check(
                all(x >= 0 for x in factor) and factor[0] > 0,
                "positive mean cofactor on open interval",
            )
            factors.append({"coefficients": texts(factor), "multiplicity": multiplicity})
            native_factors.append((factor, multiplicity))
    h = residual
    rebuilt = [content]
    rebuilt = multiply(rebuilt, [0] * zero + [1])
    rebuilt = multiply(rebuilt, power([1, -1], one))
    for factor, multiplicity in native_factors:
        rebuilt = multiply(rebuilt, power(factor, multiplicity))
    rebuilt = multiply(rebuilt, h)
    check(
        rebuilt == difference and len(h) == 16,
        "complete fresh degree-fifteen mean residual identity",
    )
    check(content > 0, "positive scalar mean cofactor")
    chain = sturm(h)
    v0, v1 = variations(chain, F(0)), variations(chain, F(1))
    check(
        v0 - v1 == 1 and evaluate(h, F(0)) < 0 < evaluate(h, F(1)),
        "exactly one interior mean root with endpoint orientation",
    )
    lo, hi = F(0), F(1)
    divisions = []
    for _ in range(80):
        mid = (lo + hi) / 2
        if evaluate(h, mid) == 0:
            lo = hi = mid
            break
        left_count = variations(chain, lo) - variations(chain, mid)
        check(left_count in (0, 1), "single-root dyadic decision")
        divisions.append(
            {
                "lower": str(lo),
                "upper": str(hi),
                "midpoint": str(mid),
                "left_root_count": left_count,
            }
        )
        if left_count:
            hi = mid
        else:
            lo = mid
    check(hi - lo <= F(1, 2**80), "fixed exact root enclosure width")
    check(
        (lo == hi and evaluate(h, lo) == 0)
        or (
            evaluate(h, lo) < 0 < evaluate(h, hi)
            and variations(chain, lo) - variations(chain, hi) == 1
        ),
        "isolated unique mean root",
    )
    # These fixed controls guard both successful and nonconstant gcd paths.
    check(bezout([1, 0, 1], [0, 1], check)["unit_gcd"], "known coprime polynomial control")
    check(
        not bezout([-1, 0, 1], [-1, 1], check)["unit_gcd"], "known common-factor negative control"
    )
    attempts = []
    for order in (2, 3):
        moment_difference = add(raw["B_mu" + str(order)], raw["A_mu" + str(order)], -1)
        witness = bezout(h, moment_difference, check)
        witness["raw_moment_order"] = order
        witness["positive_difference_denominator"] = "1"
        attempts.append(witness)
        if witness["unit_gcd"]:
            break
    primary = attempts[0]["unit_gcd"]
    check(primary, "all-common-strength distinction by first two raw moments")
    check(
        difference[0] == sum(difference) == 0
        and attempts[0]["difference"][0] == "0"
        and sum(F(x) for x in attempts[0]["difference"]) == 0,
        "no uniform gap inferred from endpoint limits",
    )
    mean = {
        "status": "EXACTLY_ONE_INTERIOR_MEAN_CROSSING",
        "difference_orientation": "B_minus_A",
        "difference_coefficients": texts(difference),
        "factorization": {
            "positive_content": str(content),
            "t_zero_multiplicity": zero,
            "one_minus_t_multiplicity": one,
            "positive_simple_factors": factors,
            "H_coefficients": texts(h),
            "full_reexpansion_exact": True,
        },
        "sturm_chain": [texts(row) for row in chain],
        "variations_at_zero": v0,
        "variations_at_one": v1,
        "root_interval": {"lower": str(lo), "upper": str(hi)},
        "root_bisection": divisions,
        "sign_for_t_below_root": -1,
        "sign_for_t_above_root": 1,
        "strength_crossing": "s_star=-(158/9)*log(t_star); positive mean difference below s_star, negative above.",
        "endpoint_mean_differences": {"t_zero": "0", "t_one": "0"},
    }
    joint = {
        "status": "FIRST_TWO_RAW_MOMENTS_NEVER_AGREE_SIMULTANEOUSLY_AT_COMMON_STRENGTH",
        "attempts": attempts,
        "third_moment_fallback": "NOT_NEEDED" if primary else "EXECUTED",
        "law_conclusion": "For every finite positive common s, the two bounded intensity laws differ in their first or second raw moment.",
        "scope": "Same calibrated strength only; not uniqueness across independently varying strengths, no uniform margin and no detector/count claim.",
    }
    return mean, joint
