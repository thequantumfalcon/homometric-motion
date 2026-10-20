"""Check the finite algebra for the fixed phase-permutation proof."""

import argparse
import json
from collections import Counter
from fractions import Fraction as F
from pathlib import Path

Matrix = list[list[F]]
Phase = tuple[int, int]


def multiply(a: Matrix, b: Matrix) -> Matrix:
    return [[sum((x * y for x, y in zip(row, column)), F(0)) for column in zip(*b)] for row in a]


def scale(k: F, a: Matrix) -> Matrix:
    return [[k * x for x in row] for row in a]


def add(a: Matrix, b: Matrix) -> Matrix:
    return [[x + y for x, y in zip(row, other)] for row, other in zip(a, b)]


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def trace(a: Matrix) -> F:
    return sum((a[i][i] for i in range(len(a))), F(0))


def conjugated(a: Matrix, permutation: list[int]) -> Matrix:
    return [[a[i][j] for j in permutation] for i in permutation]


def laplacian(points: list[int], radius: F) -> tuple[Matrix, list[tuple[int, int]]]:
    n = len(points)
    edges = [
        (i, j) for i in range(n) for j in range(i + 1, n) if abs(points[i] - points[j]) < radius
    ]
    matrix = [[F(0) for _ in points] for _ in points]
    for i, j in edges:
        matrix[i][i] += 1
        matrix[j][j] += 1
        matrix[i][j] -= 1
        matrix[j][i] -= 1
    return matrix, edges


def phase_product(x: Phase, y: Phase) -> Phase:
    """Coordinates in Q(zeta), with zeta squared equal to -1-zeta."""
    a, b = x
    c, d = y
    return a * c - b * d, a * d + b * c - b * d


def phase_conjugate(x: Phase) -> Phase:
    a, b = x
    return a - b, -b


def verify() -> dict:
    checks: list[str] = []

    def require(condition: bool, label: str) -> None:
        if not condition:
            raise ValueError(label)
        checks.append(label)

    u, va, vb = (0, 1, 5), (0, 10, 22), (0, 12, 22)
    a = sorted(x + y for x in u for y in va)
    b = sorted(x + y for x in u for y in vb)
    n = 9
    require(len(a) == len(set(a)) == n and len(b) == len(set(b)) == n, "distinct sums")
    require(vb == tuple(sorted(22 - x for x in va)), "reflected factor")
    require(
        Counter(x - y for x in a for y in a) == Counter(x - y for x in b for y in b),
        "complete signed difference multiplicities",
    )
    require(a[0] == b[0] == 0 and a[-1] == b[-1] == 27, "common endpoints")
    require(a != b and sorted(27 - x for x in a) != b, "noncongruent configurations")
    residues = {"A": [x % 3 for x in a], "B": [x % 3 for x in b]}
    for side in ("A", "B"):
        require(Counter(residues[side]) == Counter({0: 3, 1: 3, 2: 3}), "phase counts " + side)
    available = {r: iter([i for i, x in enumerate(a) if x % 3 == r]) for r in range(3)}
    permutation = [next(available[x % 3]) for x in b]
    require(sorted(permutation) == list(range(n)), "phase matching is a permutation")
    phase_table = ((1, 0), (0, 1), (-1, -1))
    za = [phase_table[x % 3] for x in a]
    zb = [phase_table[x % 3] for x in b]
    require(zb == [za[i] for i in permutation], "zB equals P zA")
    for side, phases in (("A", za), ("B", zb)):
        require(tuple(map(sum, zip(*phases))) == (0, 0), "clean phase null " + side)
        for i, phase in enumerate(phases):
            require(phase_product(phase, phase_conjugate(phase)) == (1, 0), f"unit {side}/{i}")
    formal_a = {
        (i, j): phase_product(za[i], phase_conjugate(za[j])) for i in range(n) for j in range(n)
    }
    formal_b = {
        (permutation[i], permutation[j]): phase_product(zb[i], phase_conjugate(zb[j]))
        for i in range(n)
        for j in range(n)
    }
    for key in formal_a:
        require(formal_a[key] == formal_b[key], "intensity coefficient " + str(key))

    identity = [[F(i == j) for j in range(n)] for i in range(n)]
    zero = scale(F(0), identity)
    jmatrix = [[F(1, n) for _ in range(n)] for _ in range(n)]
    h = add(identity, scale(F(-1), jmatrix))
    p = [[F(permutation[i] == j) for j in range(n)] for i in range(n)]
    require(multiply(p, transpose(p)) == identity, "orthogonal permutation")
    require(all(sum(row) == 1 for row in p), "permutation fixes constants")
    require(h == transpose(h) and multiply(h, h) == h, "orthogonal centered projection")
    require(trace(h) == 8 and multiply(h, jmatrix) == zero, "rank eight and constant null")
    la, ea = laplacian(a, F(28))
    lb, eb = laplacian(b, F(28))
    require(ea == eb and len(ea) == 36, "common complete graph")
    require(la == lb == scale(F(9), h), "L equals 9H")
    lplus = scale(F(1, 9), h)
    require(multiply(la, lplus) == multiply(lplus, la) == h, "pseudoinverse")
    require(all(sum(row) == 0 for row in lplus), "centered pseudoinverse")
    require(trace(lplus) == F(8, 9), "pseudoinverse trace")
    c = F(n) / trace(lplus)
    d = scale(c, lplus)
    require(c == F(81, 8) and d == scale(F(9, 8), h), "normalized covariance")
    require(trace(d) == 9 and all(sum(row) == 0 for row in d), "trace and centered covariance")
    require(
        all(d[i][j] == (1 if i == j else F(-1, 8)) for i in range(n) for j in range(n)),
        "covariance entries",
    )
    for label, matrix in (("H", h), ("L", la), ("Lplus", lplus), ("D", d)):
        require(conjugated(matrix, permutation) == matrix, "invariant " + label)
        require(multiply(p, matrix) == multiply(matrix, p), "commuting " + label)
    diffusion = scale(F(9, 2), h)
    require(
        add(multiply(la, d), multiply(d, la))
        == multiply(diffusion, transpose(diffusion))
        == scale(2 * c, h),
        "OU stationary Lyapunov identity",
    )
    require(multiply(d, h) == d and multiply(d, jmatrix) == zero, "kernel projector factors")
    require(
        {d[i][i] + d[j][j] - 2 * d[i][j] for i in range(n) for j in range(i)} == {F(9, 4)},
        "nonzero relative-motion variance",
    )
    cross_phase = tuple(
        sum(formal_a[i, j][k] for i in range(n) for j in range(n) if i != j) for k in (0, 1)
    )
    require(cross_phase == (-9, 0), "mean off-diagonal coefficient")

    bad_p = permutation.copy()
    bad_p[0], bad_p[1] = bad_p[1], bad_p[0]
    require(zb != [za[i] for i in bad_p], "cross-residue phase control rejected")
    v = [F(i == 3) - F(i == 4) for i in range(n)]
    perturbed = add(d, [[v[i] * v[j] / 100 for j in range(n)] for i in range(n)])
    perturbed = scale(F(9) / trace(perturbed), perturbed)
    require(trace(perturbed) == 9 and all(sum(row) == 0 for row in perturbed), "control trace")
    require(conjugated(perturbed, permutation) != perturbed, "covariance control rejected")
    old_la, old_ea = laplacian(a, F(15, 2))
    old_lb, old_eb = laplacian(b, F(15, 2))
    require(old_lb != conjugated(old_la, permutation), "different threshold-15/2 model")
    require(len(old_ea) < 36 and len(old_eb) < 36, "changed interaction rule")

    return {
        "schema_version": 1,
        "kind": "phase_permutation_k9_algebra_v1",
        "status": "PASS",
        "checks": {"count": len(checks), "passed": checks},
        "geometry": {"A": a, "B": b, "phase_residues": residues},
        "phase_permutation": {
            "row_to_column_zero_based": permutation,
            "convention": "(Pv)_i=v_{p(i)}",
            "global_phase": "0",
            "phases_A_Q_zeta": za,
            "phases_B_Q_zeta": zb,
            "all_81_formal_intensity_coefficients_identical": True,
        },
        "common_graph": {
            "nominal_threshold_exact": "28",
            "edges_zero_based": ea,
            "laplacian": la,
            "pseudoinverse": lplus,
            "H": h,
            "trace_Lplus_exact": trace(lplus),
            "c_exact": c,
            "D": d,
            "diffusion_matrix": diffusion,
            "relative_pair_variance_exact": F(9, 4),
        },
        "negative_controls": {
            "cross_residue_permutation_phase_match": False,
            "perturbed_covariance_permutation_invariant": False,
            "threshold_15_over_2_full_graph_conjugacy_under_fixed_P": False,
            "failed_criterion_caveat": "Failure of a sufficient criterion does not prove unequal laws.",
        },
        "scope": (
            "Finite algebra for phase-permutation.md. The analytic proof supplies the exact "
            "path-law and common-channel consequences at the fixed frequency and shared "
            "strength/clock. No simulation, physical validation or full formalization."
        ),
    }


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {key: encode(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [encode(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="new JSON file only")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("output exists; choose a new file")
    result = verify()
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(encode(result), stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(f"PASS: {result['checks']['count']} finite algebra checks; see the proof for path laws.")


if __name__ == "__main__":
    main()
