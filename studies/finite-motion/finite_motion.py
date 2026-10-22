"""Numerical study: exact finite-strength moments of the 63-point pair under graph OU motion.

This is a multiprecision floating-point study, not an outward-interval certificate.
It reconstructs the A/B configurations and their threshold-5/2 spring graphs from the
construction in docs/proofs/geometry-and-motion.md and evaluates the instantaneous
intensity moments E[I^k] for any normalized strength beta, not only the small-beta cap.

For Y ~ N(0, D), D = n L^+ / tr L^+, and site charges c = a - b,
    E[I^k] = (k!)^2 sum_{|a|=|b|=k} prod_j z_j^(c_j) / (a_j! b_j!) exp(-mu c^T L^+ c),
with mu = w^2 beta (n / tr L^+) / 2. For zero-sum c, c^T L^+ c is the minimum flow energy
(Thomson's principle): each path edge carries the cumulative charge F, and the single chord
(r, r+2) lowers the energy by (F_r + F_{r+1})^2 / 3. A transfer matrix along the sorted
path with state (sum a, sum b) therefore evaluates every moment exactly up to working
precision.

Commands:
    sweep --output FILE      skewness gap and normal-approximation window counts over beta
    validate                 direct-mean and Monte Carlo checks of the transfer matrix
    mixed                    add independent site phases at fixed total variance
"""

import argparse
import json
from math import comb, factorial
from pathlib import Path

import mpmath as mp

mp.mp.dps = 110
W = mp.pi / 3
THETA = mp.asin(1 / (5 * mp.sqrt(3)))
PHI = -mp.asin(1 / (8 * mp.sqrt(3)))
BETAS = ("1e-8", "1e-6", "1e-4", "1e-3", "3e-3", "1e-2", "3e-2", "1e-1", "0.3", "1")


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
        out.append(mp.re(factorial(k) ** 2 * state[(k, k, None)]))
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
        stats.append((c / a**1.5, mp.sqrt((grad.T * sigma * grad)[0])))
    (ra, sa), (rb, sb) = stats
    return (mp.mpf("1.645") * (sa + sb) / abs(ra - rb)) ** 2


def sweep(output: Path) -> None:
    if output.exists():
        raise SystemExit(f"refusing to overwrite {output}")
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
    record = {
        "kind": "numerical study (multiprecision floating point), not a certificate",
        "precision_digits": mp.mp.dps,
        "photon_budget": "class-A mean 6 signal counts per window, Poisson background 1",
        "trace_L_plus": {"A": mp.nstr(a["trace"], 15), "B": mp.nstr(b["trace"], 15)},
        "rows": rows,
    }
    output.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")


def validate() -> None:
    import numpy as np

    a, b = build((0, 31, 63)), build((0, 32, 63))
    print("exact traces:", mp.nstr(a["trace"] * 189, 12), mp.nstr(b["trace"] * 189, 12), "/ 189")
    for beta in (mp.mpf("1e-3"), mp.mpf("0.1")):
        print(
            f"beta={mp.nstr(beta, 3)} mean: transfer={mp.nstr(moments(a, beta, 1)[0], 20)} "
            f"direct={mp.nstr(direct_mean(a, beta), 20)}"
        )
    rng = np.random.default_rng(7)
    beta = 0.1
    for name, graph in (("A", a), ("B", b)):
        exact = moments(graph, mp.mpf(beta), 3)
        n = graph["n"]
        cov = np.array([[float(graph["cov"][i, j]) for j in range(n)] for i in range(n)])
        vals, vecs = np.linalg.eigh(cov)
        root = vecs * np.sqrt(np.clip(vals, 0, None))
        x = np.array([float(v) for v in graph["x"]])
        batches = []
        for _ in range(40):
            y = rng.standard_normal((250_000, n)) @ root.T
            amp = np.exp(1j * float(W) * (x + np.sqrt(beta) * y)).sum(1)
            batches.append(np.abs(amp) ** 2)
        sk = []
        for s in batches:
            m1, m2, m3 = s.mean(), (s**2).mean(), (s**3).mean()
            sk.append((m3 - 3 * m1 * m2 + 2 * m1**3) / (m2 - m1**2) ** 1.5)
        allv = np.concatenate(batches)
        print(
            f"Monte Carlo {name}, beta=0.1, 1e7 draws: mean={allv.mean():.5f} "
            f"(exact {float(exact[0]):.5f}); skewness={np.mean(sk):.4f} "
            f"+- {np.std(sk) / np.sqrt(len(sk)):.4f} (exact {float(skewness(exact)):.4f})"
        )


def mixed() -> None:
    """Spring-correlated motion plus independent site phases at fixed total phase variance."""
    a, b = build((0, 31, 63)), build((0, 32, 63))
    print("check: iid only (t = 1/2) gives D_1..D_3 = 0 and D_4 = 162.45375...")
    ia = moments(a, 0, 4, 2 * mp.log(2))
    ib = moments(b, 0, 4, 2 * mp.log(2))
    print("   ", [mp.nstr(x - y, 8) for x, y in zip(ia, ib)])
    print("sigma2  uncorrelated  mean I (A)  skewness gap  windows  vs f=0")
    for sigma2 in (mp.mpf("0.0329"), mp.mpf("0.1097")):
        base = None
        for text in ("0", "0.01", "0.03", "0.1", "0.3", "0.5"):
            f = mp.mpf(text)
            beta = (1 - f) * sigma2 / W**2
            ma = moments(a, beta, 6, f * sigma2)
            mb = moments(b, beta, 6, f * sigma2)
            n_win = windows(ma, mb)
            base = n_win if base is None else base
            print(
                f"{mp.nstr(sigma2, 4):>6} {text:>12} {mp.nstr(ma[0], 6):>11} "
                f"{mp.nstr(skewness(mb) - skewness(ma), 5):>13} {mp.nstr(n_win, 3):>8} "
                f"{mp.nstr(n_win / base, 3):>7}",
                flush=True,
            )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("sweep")
    run.add_argument("--output", type=Path, required=True)
    sub.add_parser("validate")
    sub.add_parser("mixed")
    args = parser.parse_args()
    if args.command == "sweep":
        sweep(args.output)
    elif args.command == "mixed":
        mixed()
    else:
        validate()


if __name__ == "__main__":
    main()
