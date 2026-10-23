"""Numerical study: finite-strength moments of the 63-point pair under graph OU motion.

This is a multiprecision floating-point study, not an outward-interval certificate.
It reconstructs the A/B configurations and their threshold-5/2 spring graphs from the
construction in docs/proofs/geometry-and-motion.md and evaluates the instantaneous
intensity moments E[I^k] for any normalized strength beta, not only the small-beta cap.

For Y ~ N(0, D), D = n L^+ / tr L^+, and site charges c = a - b,
    E[I^k] = (k!)^2 sum_{|a|=|b|=k} prod_j z_j^(c_j) / (a_j! b_j!) exp(-mu c^T L^+ c),
with mu = w^2 beta (n / tr L^+) / 2. For zero-sum c, c^T L^+ c is the minimum flow energy
(Thomson's principle): each path edge carries the cumulative charge F, and the single chord
(r, r+2) lowers the energy by (F_r + F_{r+1})^2 / 3. A transfer matrix along the sorted
path with state (sum a, sum b, saved chord flow) evaluates this finite moment
formula using multiprecision floating-point arithmetic, without an error enclosure.

Commands:
    sweep --output FILE      skewness gap and normal-approximation window counts over beta
    validate                 assert deterministic numerical cross-checks
    mixed --output FILE      add independent site phases at fixed total mean-site variance
    verify --output FILE     reproduce both references and assert numerical cross-checks
"""

import argparse
import json
from itertools import product
from math import comb, factorial
from pathlib import Path

import mpmath as mp

mp.mp.dps = 110
W = mp.pi / 3
THETA = mp.asin(1 / (5 * mp.sqrt(3)))
PHI = -mp.asin(1 / (8 * mp.sqrt(3)))
BETAS = ("1e-8", "1e-6", "1e-4", "1e-3", "3e-3", "1e-2", "3e-2", "1e-1", "0.3", "1")
SOURCE = Path(__file__).resolve().parent


def base_block() -> list:
    block = []
    for j in range(10):
        block.append(3 * j + 1 + (-1) ** j * THETA / W)
        block.append(3 * j + (0 if j < 2 else (-1) ** j * PHI / W))
    block.append(mp.mpf(30))
    return block


def build(shifts: tuple[int, int, int]) -> dict:
    xs = sorted(u + s for u in base_block() for s in shifts)
    n = len(xs)
    edges = [
        (i, j) for i in range(n) for j in range(i + 1, n) if abs(xs[i] - xs[j]) <= mp.mpf(5) / 2
    ]
    chords = [(i, j) for (i, j) in edges if j != i + 1]
    if len(chords) != 1 or chords[0][1] != chords[0][0] + 2:
        raise RuntimeError("expected the ordered path plus one (r, r+2) chord")
    if any((i, i + 1) not in edges for i in range(n - 1)):
        raise RuntimeError("expected every consecutive path edge")
    lap = mp.zeros(n)
    for i, j in edges:
        lap[i, j] -= 1
        lap[j, i] -= 1
        lap[i, i] += 1
        lap[j, j] += 1
    ones = mp.ones(n) / n
    pinv = mp.inverse(lap + ones) - ones
    trace = sum(pinv[i, i] for i in range(n))
    return {
        "x": xs,
        "n": n,
        "r": chords[0][0],
        "scale": n / trace,
        "trace": trace,
        "cov": pinv * (n / trace),
        "z": [mp.expj(W * x) for x in xs],
    }


def moments(graph: dict, beta, kmax: int, iid_variance=0) -> list:
    """Raw moments E[I^k], k = 1..kmax, by the transfer matrix.

    `iid_variance` adds independent site phases of that variance on top of the spring-graph
    motion; each charge c at a site then gains the factor exp(-iid_variance c^2 / 2).
    """
    if not mp.isfinite(beta) or beta < 0 or not mp.isfinite(iid_variance) or iid_variance < 0:
        raise ValueError("phase variances must be finite and nonnegative")
    if not isinstance(kmax, int) or not 1 <= kmax <= 6:
        raise ValueError("the study supports moment orders 1 through 6")
    z, n, r = graph["z"], graph["n"], graph["r"]
    mu = W**2 * beta * graph["scale"] / 2
    out = []
    for k in range(1, kmax + 1):
        inv_fact = [mp.mpf(1) / factorial(i) for i in range(k + 1)]
        site = {c: mp.exp(-iid_variance * c * c / 2) for c in range(-k, k + 1)}
        state = {(0, 0, None): mp.mpc(1)}
        for j in range(n):
            powers = {c: z[j] ** c * site[c] for c in range(-k, k + 1)}
            nxt = {}
            for (sa, sb, fr), value in state.items():
                for a in range(k - sa + 1):
                    va = value * inv_fact[a]
                    for b in range(k - sb + 1):
                        key = (sa + a, sb + b, fr)
                        nxt[key] = nxt.get(key, 0) + va * inv_fact[b] * powers[a - b]
            if j < n - 1:
                edged = {}
                for (sa, sb, fr), value in nxt.items():
                    flow = sa - sb
                    energy = flow * flow
                    keep = fr
                    if j == r:
                        keep = flow
                    if j == r + 1:
                        energy = energy - mp.mpf((fr + flow) ** 2) / 3
                        keep = None
                    key = (sa, sb, keep)
                    edged[key] = edged.get(key, 0) + value * mp.exp(-mu * energy)
                nxt = edged
            state = nxt
        raw = factorial(k) ** 2 * state[(k, k, None)]
        require_close(mp.im(raw), 0, "imaginary part of raw moment", mp.mpf("1e-75"))
        out.append(mp.re(raw))
    return out


def direct_mean(graph: dict, beta):
    z, cov, n = graph["z"], graph["cov"], graph["n"]
    c = W**2 * beta / 2
    return mp.re(
        mp.fsum(
            z[j] * mp.conj(z[m]) * mp.exp(-c * (cov[j, j] + cov[m, m] - 2 * cov[j, m]))
            for j in range(n)
            for m in range(n)
        )
    )


def skewness(raw: list):
    m1, m2, m3 = raw[0], raw[1], raw[2]
    return (m3 - 3 * m1 * m2 + 2 * m1**3) / (m2 - m1**2) ** 1.5


def windows(raw_a: list, raw_b: list, mean_counts=6, background=1) -> mp.mpf:
    """Normal-approximation windows for the factorial-cumulant skewness test (5%/5%).

    Independent windows, common gain fixed so class A has `mean_counts` signal counts,
    fixed Poisson background. A heuristic, not a finite-sample guarantee.
    """
    if mean_counts <= 0 or background < 0:
        raise ValueError("signal mean must be positive and background nonnegative")
    gain = mean_counts / raw_a[0]
    stats = []
    for raw in (raw_a, raw_b):
        lam = [mp.mpf(1)]
        for order in range(1, 7):
            lam.append(
                mp.fsum(
                    comb(order, i)
                    * gain**i
                    * (raw[i - 1] if i else 1)
                    * mp.mpf(background) ** (order - i)
                    for i in range(order + 1)
                )
            )
        f = lam
        a = f[2] - f[1] ** 2
        c = f[3] - 3 * f[1] * f[2] + 2 * f[1] ** 3
        if a <= 0:
            raise ValueError("factorial skewness requires positive latent variance")

        def cov(i, j):
            total = mp.fsum(
                comb(i, m) * comb(j, m) * factorial(m) * f[i + j - m] for m in range(min(i, j) + 1)
            )
            return total - f[i] * f[j]

        sigma = mp.matrix(3, 3)
        for i in range(3):
            for j in range(3):
                sigma[i, j] = cov(i + 1, j + 1)
        da = mp.matrix([-2 * f[1], 1, 0])
        dc = mp.matrix([-3 * f[2] + 6 * f[1] ** 2, -3 * f[1], 1])
        grad = dc / a**1.5 - mp.mpf(1.5) * c * da / a**2.5
        variance = (grad.T * sigma * grad)[0]
        if variance <= 0:
            raise ValueError("delta-method variance must be positive")
        stats.append((c / a**1.5, mp.sqrt(variance)))
    (ra, sa), (rb, sb) = stats
    if ra == rb:
        raise ValueError("zero skewness gap has no finite normal-approximation count")
    return (mp.mpf("1.645") * (sa + sb) / abs(ra - rb)) ** 2


def sweep_record() -> dict:
    a, b = build((0, 31, 63)), build((0, 32, 63))
    rows = []
    for text in BETAS:
        beta = mp.mpf(text)
        ma, mb = moments(a, beta, 6), moments(b, beta, 6)
        ga, gb = skewness(ma), skewness(mb)
        rows.append(
            {
                "beta": text,
                "mean_intensity_A": mp.nstr(ma[0], 12),
                "mean_intensity_B": mp.nstr(mb[0], 12),
                "skewness_A": mp.nstr(ga, 12),
                "skewness_B": mp.nstr(gb, 12),
                "skewness_gap": mp.nstr(gb - ga, 8),
                "normal_approx_windows": mp.nstr(windows(ma, mb), 4),
            }
        )
        print(rows[-1], flush=True)
    return {
        "kind": "numerical study (multiprecision floating point), not a certificate",
        "precision_digits": mp.mp.dps,
        "photon_budget": "class-A mean 6 signal counts per window, Poisson background 1",
        "trace_L_plus": {"A": mp.nstr(a["trace"], 15), "B": mp.nstr(b["trace"], 15)},
        "rows": rows,
    }


def require_close(left, right, label: str, tolerance=mp.mpf("1e-80")) -> None:
    """A floating-point regression assertion, never an outward error bound."""
    if not mp.isfinite(left) or not mp.isfinite(right):
        raise RuntimeError(f"nonfinite numerical cross-check: {label}")
    if abs(left - right) > tolerance * max(mp.mpf(1), abs(right)):
        raise RuntimeError(f"numerical cross-check failed: {label}")


def compositions(n: int, total: int):
    if n == 1:
        yield (total,)
    else:
        for first in range(total + 1):
            for rest in compositions(n - 1, total - first):
                yield (first, *rest)


def direct_raw(graph: dict, beta, order: int, iid=0):
    """Independent unrestricted multinomial sum with full covariance, for toy graphs."""
    n, z, covariance = graph["n"], graph["z"], graph["cov"]
    result = mp.mpc(0)
    for aa, bb in product(list(compositions(n, order)), repeat=2):
        charges = [a - b for a, b in zip(aa, bb)]
        phase = mp.fprod(z[j] ** charges[j] for j in range(n))
        denom = mp.fprod(factorial(a) * factorial(b) for a, b in zip(aa, bb))
        energy = mp.fsum(
            charges[i] * covariance[i, j] * charges[j] for i in range(n) for j in range(n)
        )
        result += (
            phase / denom * mp.exp(-(W**2 * beta * energy + iid * sum(c * c for c in charges)) / 2)
        )
    return mp.re(factorial(order) ** 2 * result)


def toy_graph(n: int, r: int) -> dict:
    lap = mp.zeros(n)
    for i, j in [(i, i + 1) for i in range(n - 1)] + [(r, r + 2)]:
        lap[i, i] += 1
        lap[j, j] += 1
        lap[i, j] -= 1
        lap[j, i] -= 1
    ones = mp.ones(n) / n
    pinv = mp.inverse(lap + ones) - ones
    trace = sum(pinv[i, i] for i in range(n))
    return {
        "n": n,
        "r": r,
        "scale": n / trace,
        "cov": pinv * n / trace,
        "z": [mp.expj(W * (mp.mpf(j) / 3 + j * j)) for j in range(n)],
    }


def validate() -> dict:
    """Deterministic independent numerical checks; no Monte Carlo or certificate."""
    toy_checks = 0
    for n, r in ((3, 0), (4, 0), (4, 1), (5, 2)):
        graph = toy_graph(n, r)
        for beta, iid in ((mp.mpf("0.17"), 0), (mp.mpf("0.03"), mp.mpf("0.07"))):
            for k, observed in enumerate(moments(graph, beta, 3, iid), 1):
                require_close(observed, direct_raw(graph, beta, k, iid), "toy charge sum")
                toy_checks += 1
    for name, shifts, trace, chord in (
        ("A", (0, 31, 63), 121486, 20),
        ("B", (0, 32, 63), 121570, 41),
    ):
        graph = build(shifts)
        if graph["r"] != chord:
            raise RuntimeError(f"unexpected {name} graph chord")
        require_close(graph["trace"], mp.mpf(trace) / 189, f"{name} trace")
        require_close(mp.fsum(graph["z"]), 0, f"{name} dark fringe")
        for beta in map(mp.mpf, ("0.001", "0.1")):
            require_close(moments(graph, beta, 1)[0], direct_mean(graph, beta), "direct mean")
        z, cov, n = graph["z"], graph["cov"], graph["n"]
        hermitian = mp.re(
            mp.fsum(mp.conj(z[i]) * cov[i, j] * z[j] for i in range(n) for j in range(n))
        )
        pseudo = mp.fsum(z[i] * cov[i, j] * z[j] for i in range(n) for j in range(n))
        rho2 = abs(pseudo / hermitian) ** 2
        leading = 2 * (1 + 3 * rho2) / (1 + rho2) ** mp.mpf("1.5")
        require_close(
            skewness(moments(graph, mp.mpf("1e-10"), 3)),
            leading,
            "small-beta leading Gaussian skewness",
            mp.mpf("1e-9"),
        )
    return {
        "kind": "multiprecision numerical cross-checks, not certification",
        "toy_charge_sum_checks": toy_checks,
        "full_graph_direct_mean_checks": 4,
        "full_graph_trace_and_dark_fringe_checks": 4,
        "small_beta_skewness_checks": 2,
    }


def mixed_record() -> dict:
    """Spring-correlated motion plus independent phases at fixed mean-site variance."""
    a, b = build((0, 31, 63)), build((0, 32, 63))
    ia = moments(a, 0, 4, 2 * mp.log(2))
    ib = moments(b, 0, 4, 2 * mp.log(2))
    for x, y in zip(ia[:3], ib[:3]):
        require_close(x, y, "iid first three raw moments")
    rows = []
    for sigma2 in (mp.mpf("0.0329"), mp.mpf("0.1097")):
        base = None
        for text in ("0", "0.01", "0.03", "0.1", "0.3", "0.5"):
            f = mp.mpf(text)
            beta = (1 - f) * sigma2 / W**2
            ma = moments(a, beta, 6, f * sigma2)
            mb = moments(b, beta, 6, f * sigma2)
            n_win = windows(ma, mb)
            base = n_win if base is None else base
            rows.append(
                {
                    "mean_site_phase_variance": mp.nstr(sigma2, 4),
                    "uncorrelated_fraction": text,
                    "mean_intensity_A": mp.nstr(ma[0], 12),
                    "skewness_gap": mp.nstr(skewness(mb) - skewness(ma), 8),
                    "normal_approx_windows": mp.nstr(n_win, 4),
                    "relative_to_correlated_only": mp.nstr(n_win / base, 4),
                }
            )
            print(rows[-1], flush=True)
    return {
        "kind": "numerical study (multiprecision floating point), not a certificate",
        "precision_digits": mp.mp.dps,
        "photon_budget": "class-A mean 6 signal counts per window, Poisson background 1",
        "iid_first_three_raw_moments_agree_numerically": True,
        "iid_fourth_raw_moment_A_minus_B": mp.nstr(ia[3] - ib[3], 12),
        "rows": rows,
    }


def output_path(path: Path) -> Path:
    path = path.resolve()
    if path.is_relative_to(SOURCE):
        raise SystemExit("write fresh numerical outputs outside the study source directory")
    if path.exists():
        raise SystemExit(f"refusing to overwrite {path}")
    return path


def verify() -> dict:
    checks = validate()
    for filename, calculate in (
        ("results.json", sweep_record),
        ("mixed-results.json", mixed_record),
    ):
        expected = json.loads((SOURCE / filename).read_text(encoding="utf-8"))
        if calculate() != expected:
            raise RuntimeError(f"fresh numerical calculation differs from {filename}")
    return {
        "status": "PASS",
        "kind": "numerical reproduction only; no mathematical risk certificate",
        "precision_digits": mp.mp.dps,
        "sweep_rows": len(BETAS),
        "mixed_rows": 12,
        "checks": checks,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("sweep", "mixed", "verify"):
        run = sub.add_parser(command)
        run.add_argument("--output", type=Path, required=True)
    sub.add_parser("validate")
    args = parser.parse_args()
    if args.command == "validate":
        print(json.dumps(validate(), indent=2))
        return
    output = output_path(args.output)
    record = {"sweep": sweep_record, "mixed": mixed_record, "verify": verify}[args.command]()
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(record, indent=1) + "\n")


if __name__ == "__main__":
    main()
