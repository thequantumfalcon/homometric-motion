"""Fresh 63-point calibrated-iid check using native Arb and NB convolution."""

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

import flint
from flint import arb, arb_poly, ctx, fmpq, fmpq_mat

CUTOFF = 20000
NECESSARY = 9188577
SUFFICIENT = 35943631


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def ball(value):
    return arb(str(value))


def bounds(value):
    require(value.is_finite(), "finite enclosure")
    return F(str(value.lower().fmpq())), F(str(value.upper().fmpq()))


def record(value):
    lower, upper = bounds(value)
    return {"lower": str(lower), "upper": str(upper)}


def geometry(side):
    motif = sorted([3 * j + d for j in range(10) for d in (0, 1)] + [30])
    shifts = (0, 31, 63) if side == "A" else (0, 32, 63)
    points = sorted(x + y for x in motif for y in shifts)
    n = len(points)
    edges = [
        (i, j) for i in range(n) for j in range(i + 1, n) if 2 * abs(points[i] - points[j]) < 5
    ]
    lap = [[0] * n for _ in range(n)]
    visited = {0}
    for i, j in edges:
        lap[i][i] += 1
        lap[j][j] += 1
        lap[i][j] -= 1
        lap[j][i] -= 1
    for _ in range(n):
        visited |= {j for i in visited for j in range(n) if lap[i][j] == -1}
    require(len(visited) == n == 63, "connected fixed graph")
    identity = fmpq_mat([[int(i == j) for j in range(n)] for i in range(n)])
    projector = fmpq_mat([[fmpq(1, n)] * n for _ in range(n)])
    lap = fmpq_mat(lap)
    pinv = (lap + projector).inv() - projector
    require(
        lap * pinv == identity - projector == pinv * lap,
        "exact pseudoinverse identities",
    )
    trace = sum(pinv[i, i] for i in range(n))
    require(trace > 0, "positive trace")
    covariance = (fmpq(n) / trace) * pinv
    require(sum(covariance[i, i] for i in range(n)) == n, "trace-normalized covariance")
    require(
        all(sum(covariance[i, j] for j in range(n)) == 0 for i in range(n)),
        "zero translation mode",
    )
    root3 = arb(3).sqrt()
    ct, st = ball(F(74, 75)).sqrt(), 1 / arb(75).sqrt()
    cp, sp = ball(F(191, 192)).sqrt(), -1 / arb(192).sqrt()
    base = []
    for j in range(10):
        sign = (-1) ** j
        base.append((arb(sign), arb(0)) if j < 2 else (sign * cp, sp))
        base.append((sign * ct / 2 - root3 * st / 2, sign * root3 * ct / 2 + st / 2))
    base.append((arb(1), arb(0)))
    cosine, sine = ball(F(1 if side == "A" else -1, 2)), root3 / 2
    phase = (
        base
        + [(cosine * x - sine * y, cosine * y + sine * x) for x, y in base]
        + [(-x, -y) for x, y in base]
    )
    require(
        all((x * x + y * y).contains(1) for x, y in phase),
        "unit phase interval consistency",
    )
    require(
        sum((x for x, _ in phase), arb(0)).contains(0)
        and sum((y for _, y in phase), arb(0)).contains(0),
        "clean null interval consistency; exact identity is an analytic dependency",
    )
    xx = xy = yy = arb(0)
    for i in range(n):
        for j in range(n):
            weight = arb(covariance[i, j])
            xx += weight * phase[i][0] * phase[j][0]
            xy += weight * phase[i][0] * phase[j][1]
            yy += weight * phase[i][1] * phase[j][1]
    root = ((xx - yy) ** 2 + 4 * xy**2).sqrt()
    eigenvalues = [(xx + yy - root) / 2, (xx + yy + root) / 2]
    require(all(x > 0 for x in eigenvalues), "positive projected eigenvalues")
    return eigenvalues, {
        "n": n,
        "edge_count": len(edges),
        "trace_Lplus_exact": str(trace),
        "lambda": [record(x) for x in eigenvalues],
    }


def probabilities(eigenvalues, gain):
    qs = [2 * gain * value / (1 + 2 * gain * value) for value in eigenvalues]
    require(all(0 < q < 1 for q in qs), "negative-binomial parameters in (0,1)")
    sequences = []
    for q in qs:
        seq = [(1 - q).sqrt()]
        for n in range(1, CUTOFF + 1):
            seq.append(seq[-1] * q * ball(F(2 * n - 1, 2 * n)))
        sequences.append(seq)
    # Each factor is an NB(shape=1/2) probability series. Arb's polynomial
    # multiplication supplies the complete convolution, not a production import.
    product = arb_poly(sequences[0]) * arb_poly(sequences[1])
    values = [product[n] for n in range(CUTOFF + 1)]
    require(all(p > 0 for p in values), "all retained probabilities strictly positive")
    for n in range(32):
        direct = sum((sequences[0][j] * sequences[1][n - j] for j in range(n + 1)), arb(0))
        require(direct.overlaps(values[n]), "direct-convolution prefix control")
    s = 1 + ball(F(1, 202))
    denominators = [1 + 2 * gain * v * (1 - s) for v in eigenvalues]
    require(all(x > 0 for x in denominators), "Chernoff point below both PGF poles")
    pgf = 1 / (denominators[0] * denominators[1]).sqrt()
    tail = pgf / s ** (CUTOFF + 1)
    require(tail < ball(F(1, 10**35)), "predeclared omitted-mass target")
    d1 = sum((gain * v / d for v, d in zip(eigenvalues, denominators)), arb(0))
    d2 = sum((2 * (gain * v / d) ** 2 for v, d in zip(eigenvalues, denominators)), arb(0))
    tails = [tail, tail * s * d1, tail * ((s * d1) ** 2 + s * d1 + s * s * d2)]
    mass = sum(values, arb(0))
    m1 = sum((n * p for n, p in enumerate(values)), arb(0))
    m2 = sum((n * n * p for n, p in enumerate(values)), arb(0))
    mean = gain * sum(eigenvalues, arb(0))
    second = mean + 2 * gain**2 * sum((v * v for v in eigenvalues), arb(0)) + mean**2
    for partial, remainder, expected in zip((mass, m1, m2), tails, (arb(1), mean, second)):
        lo, hi = bounds(partial)
        elo, ehi = bounds(expected)
        require(
            lo <= ehi and hi + bounds(remainder)[1] >= elo,
            "normalization/moment enclosure with analytical tail",
        )
    digest = hashlib.sha256()
    for n, p in enumerate(values):
        lower, upper = bounds(p)
        digest.update((str(n) + ":" + str(lower) + ":" + str(upper) + "\n").encode("ascii"))
    return (
        values,
        tail,
        {
            "computed_terms": len(values),
            "q": [record(q) for q in qs],
            "prefix": [record(p) for p in values[:32]],
            "partial_mass": record(mass),
            "tail_bound": record(tail),
            "partial_first_moment": record(m1),
            "partial_second_moment": record(m2),
            "mean": record(mean),
            "complete_pmf_interval_sha256": digest.hexdigest(),
        },
    )


def necessary_gate(n, deficit, delta):
    k = (2 * n + 31) // 32
    base, allowance = 1 - k * deficit, F(9, 10) - 2 * n * delta
    if base < 0 or allowance <= 0:
        return False
    return base**32 > 1 - allowance**2


def sufficient_risk(n, deficit, delta):
    total = term = F(1)
    for j in range(1, 33):
        term *= n * deficit / j
        total += term
    return 1 / total + n * delta


def build(bits):
    require(256 <= bits <= 1024, "bounded precision")
    ctx.prec = bits
    parameters, geometry_rows = {}, {}
    for side in "AB":
        parameters[side], geometry_rows[side] = geometry(side)
    pooled = sum((v for pair in parameters.values() for v in pair), arb(0)) / 2
    gain = 100 / pooled
    values, tails, rows = {}, {}, {}
    for side in "AB":
        values[side], tails[side], rows[side] = probabilities(parameters[side], gain)
    partial = sum(((a * b).sqrt() for a, b in zip(values["A"], values["B"])), arb(0))
    omitted = (tails["A"] * tails["B"]).sqrt()
    lower, upper = bounds(partial)[0], min(F(1), bounds(partial + omitted)[1])
    require(0 < lower <= upper < 1, "strict complete affinity enclosure")
    # The finite-motion TV inequality is an explicit analytic dependency.
    delta = F(16, 9) * F(1, 10**16) * F(47, 4) * 63**2 * bounds(gain)[1]
    require(
        necessary_gate(NECESSARY - 1, 1 - lower, delta),
        "all counts below reported necessary bound excluded",
    )
    require(
        not necessary_gate(NECESSARY, 1 - lower, delta),
        "next necessary gate fails; no achievability inference",
    )
    risk = sufficient_risk(SUFFICIENT, 1 - upper, delta)
    require(
        risk <= F(1, 20),
        "reported sufficient count has each-class risk at most 5 percent",
    )
    require(
        sufficient_risk(SUFFICIENT - 1, 1 - upper, delta) > F(1, 20),
        "preceding sufficient gate fails; no optimality inference",
    )
    require(sufficient_risk(0, 1 - upper, delta) > F(1, 20), "zero-sample negative control")
    require(not necessary_gate(100, F(1, 100), F(1)), "invalid TV allowance control")
    require(not necessary_gate(10000, F(1, 2), F(0)), "negative Bernoulli base control")
    # Deliberately removing the n=0 term loses nonzero mass, beyond the tail bound.
    require(
        bounds(sum(values["A"][1:], arb(0)) + tails["A"])[1] < 1,
        "truncated-PMF mutation detected",
    )
    return {
        "status": "PASS",
        "model": "63_point_calibrated_iid_selected_channel",
        "python_flint_version": flint.__version__,
        "precision_bits": bits,
        "mu": "100",
        "background": "0",
        "beta_cap": "1/10000000000000000",
        "cutoff": CUTOFF,
        "geometry": geometry_rows,
        "gain": record(gain),
        "classes": rows,
        "affinity": {"lower": str(lower), "upper": str(upper)},
        "omitted_affinity_bound": record(omitted),
        "single_count_tv_upper": str(delta),
        "necessary_iid_observations_at_least": NECESSARY,
        "sufficient_iid_observations": SUFFICIENT,
        "risk_upper_enclosure": record(
            ball(1)
            / sum(
                (ball(SUFFICIENT * (1 - upper)) ** j / factorial_int(j) for j in range(33)),
                arb(0),
            )
            + ball(SUFFICIENT * delta)
        ),
        "exact_risk_gate_passed": risk <= F(1, 20),
        "analytic_dependencies": [
            "Exact phases and fixed graph from the shifted-motif construction",
            "Centered Gaussian quadratic surrogate",
            "PGF and Chernoff/affinity inequalities",
            "Finite-motion TV <= (16/9)*beta*(47/4)*g*63^2",
            "Product-TV and testing inequalities",
        ],
        "limits": [
            "One selected channel, not the ten-channel grid",
            "Known common calibration; instantaneous iid normalized counts",
            "No robust finite-exposure claim",
            "Same-author alternative arithmetic, not independent human review",
            "No measured apparatus, acquisition time, dose or numerical classifier",
        ],
    }


def factorial_int(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, default=384)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a new output file")
    result = build(args.bits)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                k: result[k]
                for k in (
                    "status",
                    "precision_bits",
                    "necessary_iid_observations_at_least",
                    "sufficient_iid_observations",
                )
            }
        )
    )
