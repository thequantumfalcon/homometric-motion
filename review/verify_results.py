"""Check serialized witnesses and compare two Arb precision runs; standard library only."""

import argparse
import json
from fractions import Fraction as F
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(path):
    require(path.stat().st_size < 8_000_000, "result size limit")
    return json.loads(path.read_text("utf-8"))


def interval(item):
    require(set(item) == {"lower", "upper"}, "exact endpoint schema")
    low, high = F(item["lower"]), F(item["upper"])
    require(low <= high, "ordered endpoints")
    return low, high


def multiply(a, b):
    c = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            c[i + j] += x * y
    return c


def add(a, b):
    c = [F(0)] * max(len(a), len(b))
    for i, x in enumerate(a):
        c[i] += x
    for i, x in enumerate(b):
        c[i] += x
    while len(c) > 1 and not c[-1]:
        c.pop()
    return c


def verify_sage(data):
    require(
        data["status"] == "PASS" and data["model"] == "nine_point_instantaneous_shared_strength",
        "Sage model/status",
    )
    h = list(map(F, data["mean_H"]))
    differences = {}
    for order, degree in ((1, 80), (2, 320), (3, 720)):
        arrays = {}
        for side in "AB":
            row = data["classes"][side]["moments"][str(order)]
            coeff = list(map(F, row["coefficients"]))
            require(
                row["degree"] == degree == len(coeff) - 1 and coeff[-1] != 0 and sum(coeff) == 0,
                "serialized moment degree/null",
            )
            require(all(x.denominator == 1 for x in coeff), "integer moment coefficients")
            require(row["ordered_tuples"] == 9 ** (2 * order), "serialized coverage")
            arrays[side] = coeff
        differences[order] = add(arrays["B"], [-x for x in arrays["A"]])
    g = [F(0)] * 39 + [F(1)]
    for factor, power in (
        ([1, -1], 2),
        ([1, 1], 2),
        ([1, 1, 1], 1),
        ([1, 0, 1], 2),
        ([1, 0, 0, 0, 1], 2),
        ([1] + [0] * 7 + [1], 1),
    ):
        for _ in range(power):
            g = multiply(g, list(map(F, factor)))
    require(multiply(g, h) == differences[1], "serialized mean factorization")
    left = list(map(F, data["bezout"]["left"]))
    right = list(map(F, data["bezout"]["right"]))
    require(
        data["bezout"]["rhs"] == "1"
        and add(multiply(left, h), multiply(right, differences[2])) == [F(1)],
        "serialized Bezout identity",
    )


def verify_arb(data):
    require(
        data["status"] == "PASS" and data["model"] == "63_point_calibrated_iid_selected_channel",
        "Arb model/status",
    )
    require(
        (data["mu"], data["background"], F(data["beta_cap"])) == ("100", "0", F(1, 10**16)),
        "fixed calibrated contract",
    )
    lower, upper = interval(data["affinity"])
    require(0 < lower <= upper < 1, "strict affinity bounds")
    gain_upper = interval(data["gain"])[1]
    delta = F(data["single_count_tv_upper"])
    require(
        delta == F(16, 9) * F(1, 10**16) * F(47, 4) * 63**2 * gain_upper,
        "exact transfer normalization",
    )
    n = data["necessary_iid_observations_at_least"] - 1
    require(type(n) is int and 0 < n < 2**63, "necessary count domain")
    base = 1 - ((2 * n + 31) // 32) * (1 - lower)
    allowance = F(9, 10) - 2 * n * delta
    require(
        base >= 0 and allowance > 0 and base**32 > 1 - allowance**2,
        "serialized necessary witness",
    )
    n = data["sufficient_iid_observations"]
    require(type(n) is int and 0 < n < 2**63, "sufficient count domain")
    x = n * (1 - upper)
    term = total = F(1)
    for j in range(1, 33):
        term = term * x / j
        total += term
    risk = 1 / total + n * delta
    require(risk <= F(1, 20), "serialized sufficient witness")
    rlo, rhi = interval(data["risk_upper_enclosure"])
    require(rlo <= risk <= rhi <= F(1, 20), "displayed risk encloses exact witness")
    for side in "AB":
        row = data["classes"][side]
        require(
            row["computed_terms"] == data["cutoff"] + 1 == 20001,
            "complete declared cutoff",
        )
        tail = interval(row["tail_bound"])
        require(0 <= tail[0] <= tail[1] < F(1, 10**35), "tail target")
        lo, hi = interval(row["partial_mass"])
        require(lo <= 1 <= hi + tail[1], "serialized normalization with tail")
        require(
            len(row["prefix"]) == 32
            and all(0 < interval(p)[0] <= interval(p)[1] < 1 for p in row["prefix"]),
            "PMF prefix",
        )


def compare_arb(a, b):
    verify_arb(a)
    verify_arb(b)
    require(a["precision_bits"] != b["precision_bits"], "two distinct precisions")
    for key in ("necessary_iid_observations_at_least", "sufficient_iid_observations"):
        require(a[key] == b[key], "count agreement across precisions")
    # Each risk witness uses that run's outward endpoints, so the two exact
    # upper bounds need not coincide. verify_arb checks each against 1/20.
    pairs = [(a[key], b[key]) for key in ("affinity", "gain")]
    for side in "AB":
        pairs += list(zip(a["geometry"][side]["lambda"], b["geometry"][side]["lambda"]))
        pairs += list(zip(a["classes"][side]["prefix"], b["classes"][side]["prefix"]))
    for x, y in pairs:
        xl, xh = interval(x)
        yl, yh = interval(y)
        require(max(xl, yl) <= min(xh, yh), "precision enclosures overlap")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sage", required=True, type=Path)
    parser.add_argument("--arb", required=True, nargs=2, type=Path)
    args = parser.parse_args()
    verify_sage(load(args.sage))
    compare_arb(*(load(p) for p in args.arb))
    print("PASS: exact serialized identities, statistical witnesses and two-precision agreement")
