"""Exact nine-point reproduction using Sage; no project-package imports."""

import argparse
import json
from collections import Counter
from itertools import combinations_with_replacement
from math import factorial
from pathlib import Path

from sage.all import QQ, ZZ, CyclotomicField, Graph, PolynomialRing, matrix, vector
from sage.env import SAGE_VERSION

POINTS = {
    "A": (0, 1, 5, 10, 11, 15, 22, 23, 27),
    "B": (0, 1, 5, 12, 13, 17, 22, 23, 27),
}


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def differences(points):
    return Counter(x - y for x in points for y in points)


def covariance(points):
    n = len(points)
    edges = [
        (i, j) for i in range(n) for j in range(i + 1, n) if 2 * abs(points[i] - points[j]) < 15
    ]
    graph = Graph([list(range(n)), edges], format="vertices_and_edges")
    require(graph.is_connected(), "connected fixed graph")
    lap = matrix(QQ, graph.laplacian_matrix(vertices=list(range(n))))
    ones = matrix(QQ, n, n, [QQ(1) / n] * (n * n))
    identity = matrix.identity(QQ, n)
    # Invert the translation mode after adding its orthogonal projector.
    pinv = (lap + ones).inverse() - ones
    require(lap * pinv == identity - ones == pinv * lap, "pseudoinverse identity")
    require(pinv * vector(QQ, [1] * n) == 0, "zero center-of-mass mode")
    require(pinv.trace() == QQ(79) / 12, "exact trace")
    d = n * pinv / pinv.trace()
    require(d.trace() == n and d.is_symmetric(), "covariance normalization")
    basis = matrix(QQ, n, n - 1, lambda i, j: (1 if i == j else 0) - (1 if i == n - 1 else 0))
    reduced = basis.transpose() * d * basis
    require(
        all(reduced[:j, :j].det() > 0 for j in range(1, n)),
        "positive definite on zero-sum subspace",
    )
    delta = QQ(9) / 158
    require(
        all(reduced[i, i] / delta in ZZ for i in range(n - 1)),
        "integer diagonal lattice",
    )
    require(
        all(2 * reduced[i, j] / delta in ZZ for i in range(n - 1) for j in range(i)),
        "integer doubled cross lattice",
    )
    charges = [
        vector(QQ, [int(k == i) - int(k == j) for k in range(n)])
        for i in range(n)
        for j in range(n)
    ]
    cross = [u * d * v / delta for u in charges for v in charges]
    require(min(cross) == -80 and max(cross) == 80, "all pair-charge cross bounds")
    require(d[0, 0] / delta not in ZZ, "zero-sum hypothesis negative control")
    return graph, d, pinv.trace()


def occupations(n, order):
    # Group positive and negative tuples separately, using multinomial weights.
    # This does not use the production program's repeated charge convolution.
    result = []
    for indices in combinations_with_replacement(range(n), order):
        counts = tuple(indices.count(i) for i in range(n))
        denominator = 1
        for count in counts:
            denominator *= factorial(count)
        result.append((counts, factorial(order) // denominator))
    require(sum(weight for _, weight in result) == n**order, "multinomial coverage")
    return result


def moments(points, d):
    field = CyclotomicField(3)
    zeta = field.gen()
    ring = PolynomialRing(QQ, "t")
    result, records = {}, {}
    for order in (1, 2, 3):
        bins, total = {}, 0
        occ = occupations(len(points), order)
        for a, wa in occ:
            for b, wb in occ:
                u = vector(ZZ, [x - y for x, y in zip(a, b)])
                exponent = (u * d * u) / (QQ(9) / 158)
                require(exponent in ZZ and 0 <= exponent <= 80 * order**2, "moment exponent")
                residue = sum(u[i] * points[i] for i in range(len(points))) % 3
                index = int(exponent)
                bins[index] = bins.get(index, field(0)) + wa * wb * zeta**residue
                total += wa * wb
        require(total == 9 ** (2 * order), "all ordered tuples including diagonals")
        require(all(c in QQ for c in bins.values()), "phase cancellation at every exponent")
        poly = ring([QQ(bins.get(k, 0)) for k in range(max(bins) + 1)])
        require(poly.degree() == 80 * order**2 and poly(1) == 0, "degree and clean null")
        result[order] = poly
        records[str(order)] = {
            "degree": int(poly.degree()),
            "coefficients": [str(c) for c in poly.list()],
            "ordered_tuples": total,
        }
    return result, records


def variations(chain, point):
    signs = [1 if p(point) > 0 else -1 for p in chain if p(point) != 0]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def build():
    require(occupations(9, 0) == [((0,) * 9, 1)], "zero-order counting control")
    require(occupations(0, 1) == [], "empty positive-order counting control")
    require(
        differences(POINTS["A"]) == differences(POINTS["B"]),
        "homometric difference multisets",
    )
    require(
        POINTS["A"] != POINTS["B"] and tuple(sorted(27 - x for x in POINTS["A"])) != POINTS["B"],
        "not congruent on the line",
    )
    changed = list(POINTS["B"])
    changed[-1] += 1
    require(
        differences(POINTS["A"]) != differences(changed),
        "perturbed geometry negative control",
    )
    polys, classes, graphs = {}, {}, {}
    for side, points in POINTS.items():
        graph, d, trace = covariance(points)
        graphs[side] = graph
        polys[side], rows = moments(points, d)
        classes[side] = {
            "points": list(points),
            "edges": [list(e[:2]) for e in graph.edges(sort=True)],
            "trace_Lplus": str(trace),
            "D": [[str(c) for c in row] for row in d.rows()],
            "moments": rows,
        }
    require(not graphs["A"].is_isomorphic(graphs["B"]), "graphs not isomorphic")
    ring = PolynomialRing(QQ, "t")
    t = ring.gen()
    g = (
        t**39
        * (1 - t) ** 2
        * (1 + t) ** 2
        * (t * t + t + 1)
        * (t * t + 1) ** 2
        * (t**4 + 1) ** 2
        * (t**8 + 1)
    )
    h = (
        2 * t**15
        - 2 * t**14
        + 2 * t**12
        - 2 * t**11
        + 2 * t**9
        - 2 * t**8
        + 2 * t**7
        - t**6
        - t**5
        + 2 * t**4
        - t**3
        - t**2
        + 2 * t
        - 1
    )
    d1, d2 = (polys["B"][r] - polys["A"][r] for r in (1, 2))
    require(d1 == g * h, "complete mean factorization")
    gcd, left, right = h.xgcd(d2)
    require(
        gcd == 1 and left * h + right * d2 == 1,
        "Bezout identity: no common interior first-two-moment zero",
    )
    chain = [h, h.derivative()]
    while True:
        remainder = -(chain[-2] % chain[-1])
        if remainder == 0:
            break
        require(len(chain) <= 16, "bounded exact Sturm chain")
        chain.append(remainder)
    require(
        variations(chain, QQ(0)) - variations(chain, QQ(1)) == 1,
        "one interior mean crossing",
    )
    require((t * t - 1).gcd(t - 1).degree() == 1, "common-factor negative control")
    require(
        (t - t * t)(1) == 0 and (t - t * t)[1] == 1,
        "one evaluation cannot prove polynomial cancellation",
    )
    return {
        "status": "PASS",
        "model": "nine_point_instantaneous_shared_strength",
        "sage_version": SAGE_VERSION,
        "classes": classes,
        "mean_H": [str(c) for c in h.list()],
        "bezout": {
            "left": [str(c) for c in left.list()],
            "right": [str(c) for c in right.list()],
            "rhs": "1",
        },
        "conclusion": "Under the stated Gaussian model the first two moments cannot both coincide for any shared finite positive strength.",
        "limits": [
            "Gaussian characteristic-function formula is an analytic dependency",
            "No detector or finite-sample bound for this nine-point model",
            "No physical validation",
            "Same-author reconstruction, not independent human review",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Use a new output file")
    result = build()
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print(
        json.dumps(
            {
                "status": result["status"],
                "sage_version": SAGE_VERSION,
                "degrees": [80, 320, 720],
                "bezout": "PASS",
            }
        )
    )
