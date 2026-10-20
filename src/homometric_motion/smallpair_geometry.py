"""Fresh geometry, covariance and leading-process identities for nine points."""

from collections import Counter
from fractions import Fraction as F

from .smallpair_algebra import exact, inverse, matrix_multiply, multiply, texts

SHIFTS = {"A": (0, 10, 22), "B": (0, 12, 22)}
PHASES = ((F(1), F(0)), (F(-1, 2), F(1, 2)), (F(-1, 2), F(-1, 2)))


def project(matrix, phases):
    n = len(phases)
    rr = sum(phases[i][0] * matrix[i][j] * phases[j][0] for i in range(n) for j in range(n))
    cc = sum(phases[i][1] * matrix[i][j] * phases[j][1] for i in range(n) for j in range(n))
    rc = sum(phases[i][0] * matrix[i][j] * phases[j][1] for i in range(n) for j in range(n))
    return rr, 3 * cc, rc


def projected_record(values):
    return exact(dict(zip(("real_real", "imag_imag", "real_imag_sqrt3_coefficient"), values)))


def derive_geometry(check):
    classes, records = {}, {}
    for side, shifts in SHIFTS.items():
        points = sorted(x + y for x in (0, 1, 5) for y in shifts)
        check(len(points) == len(set(points)) == 9, "fixed nine distinct sites")
        n = len(points)
        adjacency = [
            [int(i != j and 2 * abs(points[i] - points[j]) < 15) for j in range(n)]
            for i in range(n)
        ]
        degrees = [sum(row) for row in adjacency]
        lap = [[degrees[i] if i == j else -adjacency[i][j] for j in range(n)] for i in range(n)]
        reached = {0}
        while True:
            following = reached | {
                j for i in reached for j, edge in enumerate(adjacency[i]) if edge
            }
            if following == reached:
                break
            reached = following
        check(len(reached) == n, "connected permanent graph")
        ground = inverse([row[:-1] for row in lap[:-1]])
        check(
            matrix_multiply([row[:-1] for row in lap[:-1]], ground)
            == [[F(i == j) for j in range(n - 1)] for i in range(n - 1)],
            "grounded inverse identity",
        )
        g = [row + [F(0)] for row in ground] + [[F(0)] * n]
        resistances = [[g[i][i] + g[j][j] - 2 * g[i][j] for j in range(n)] for i in range(n)]
        means = [sum(row) / n for row in resistances]
        grand = sum(means) / n
        plus = [
            [-(resistances[i][j] - means[i] - means[j] + grand) / 2 for j in range(n)]
            for i in range(n)
        ]
        center = [[F(i == j) - F(1, n) for j in range(n)] for i in range(n)]
        check(
            matrix_multiply(lap, plus) == center and matrix_multiply(plus, lap) == center,
            "centered pseudoinverse equations",
        )
        check(all(sum(row) == 0 for row in plus), "pseudoinverse COM normalization")
        trace = sum(plus[i][i] for i in range(n))
        check(trace > 0, "positive covariance normalization")
        d = [[n * x / trace for x in row] for row in plus]
        check(sum(d[i][i] for i in range(n)) == n, "trace-normalized covariance")
        phases = [PHASES[x % 3] for x in points]
        check(sum(x for x, _ in phases) == sum(y for _, y in phases) == 0, "exact clean phase null")
        unique = [i for i, degree in enumerate(degrees) if degree == 4]
        check(len(unique) == 1, "unique degree-four graph vertex")
        neighbors = sorted(degrees[j] for j, edge in enumerate(adjacency[unique[0]]) if edge)
        differences = sorted(Counter(x - y for x in points for y in points).items())
        item = {
            "points": points,
            "laplacian": lap,
            "plus": plus,
            "D": d,
            "trace": trace,
            "phases": phases,
        }
        classes[side] = item
        records[side] = {
            "points": points,
            "signed_difference_multiplicities": [list(pair) for pair in differences],
            "edges": [[i, j] for i in range(n) for j in range(i + 1, n) if adjacency[i][j]],
            "degrees": degrees,
            "degree_four_neighbor_degrees": neighbors,
            "laplacian": lap,
            "grounded_inverse": exact(ground),
            "effective_resistances": exact(resistances),
            "laplacian_pseudoinverse": exact(plus),
            "covariance": exact(d),
            "trace_laplacian_pseudoinverse": str(trace),
            "phase_real": texts([x for x, _ in phases]),
            "phase_imaginary_sqrt3_coefficients": texts([y for _, y in phases]),
        }
    a, b = classes["A"], classes["B"]
    check(
        records["A"]["signed_difference_multiplicities"]
        == records["B"]["signed_difference_multiplicities"],
        "complete clean homometry",
    )
    check(
        a["points"] != b["points"]
        and a["points"] != sorted(max(b["points"]) - x for x in b["points"]),
        "noncongruence under translation/reflection",
    )
    check(
        records["A"]["degree_four_neighbor_degrees"]
        != records["B"]["degree_four_neighbor_degrees"],
        "nonisomorphic graph witness",
    )
    return classes, {
        "classes": records,
        "clean_homometry": True,
        "noncongruent": True,
        "graphs_nonisomorphic": True,
    }


def temporal_and_leading(classes, check):
    derived, records = {}, {}
    for side, item in classes.items():
        lap, phases, plus = item["laplacian"], item["phases"], item["plus"]
        powers = [[[int(i == j) for j in range(9)] for i in range(9)]]
        for _ in range(18):
            powers.append(matrix_multiply(powers[-1], lap))
        traces = [sum(powers[k][i][i] for i in range(9)) for k in range(1, 10)]
        descending = [F(1)]
        for k in range(1, 10):
            coefficient = -sum(descending[k - i] * traces[i - 1] for i in range(1, k + 1)) / k
            check(coefficient.denominator == 1, "integer Newton characteristic coefficient")
            descending.append(coefficient)
        characteristic = [int(x) for x in reversed(descending)]
        check(
            all(
                sum(characteristic[k] * powers[k][i][j] for k in range(10)) == 0
                for i in range(9)
                for j in range(9)
            ),
            "full characteristic matrix annihilation",
        )
        projected = [project(matrix, phases) for matrix in powers]
        plus_projected = project(plus, phases)
        instantaneous = project(item["D"], phases)
        rr, ii, rc = instantaneous
        q, p_real, p_imag = rr + ii, rr - ii, 2 * rc
        variance = 2 * (rr**2 + ii**2 + 6 * rc**2)
        third = 8 * (rr**3 + ii**3 + 9 * rc**2 * (rr + ii))
        check(rr > 0 and ii > 0 and rr * ii > 3 * rc**2, "positive leading projected covariance")
        derived[side] = {
            "powers": powers,
            "characteristic": characteristic,
            "projected": projected,
            "plus_projected": plus_projected,
            "normalizer": F(9) / item["trace"],
            "instantaneous": instantaneous,
        }
        records[side] = {
            "matrix_powers_0_to_18": [[texts(row) for row in matrix] for matrix in powers],
            "characteristic_coefficients_ascending": texts(characteristic),
            "projected_powers_0_to_18": [projected_record(row) for row in projected],
            "projected_pseudoinverse": projected_record(plus_projected),
            "covariance_normalizer": str(derived[side]["normalizer"]),
            "projected_covariance": projected_record(instantaneous),
            "q": str(q),
            "p_real": str(p_real),
            "p_imaginary_sqrt3_coefficient": str(p_imag),
            "leading_Q_variance": str(variance),
            "leading_Q_third_cumulant": str(third),
            "leading_Q_squared_skewness": str(third**2 / variance**3),
        }
    a, b = derived["A"], derived["B"]

    def reflected(row):
        return row[0], row[1], -row[2]

    shared_normalization = a["normalizer"] == b["normalizer"]
    plus_equal = a["plus_projected"] == reflected(b["plus_projected"])
    equal_powers = [x == reflected(y) for x, y in zip(a["projected"], b["projected"])]
    product = multiply(a["characteristic"], b["characteristic"])
    for item in derived.values():
        check(
            all(
                sum(product[k] * item["powers"][k][i][j] for k in range(19)) == 0
                for i in range(9)
                for j in range(9)
            ),
            "common degree-eighteen annihilator",
        )
    shared_characteristic = a["characteristic"] == b["characteristic"]
    criterion9 = shared_characteristic and all(equal_powers[:9])
    criterion18 = all(equal_powers[:18])
    proved = shared_normalization and plus_equal and (criterion9 or criterion18)
    check(proved and all(equal_powers), "fixed-reflection leading temporal equality")
    check(a["instantaneous"] == reflected(b["instantaneous"]), "equal leading marginal laws")
    return {
        "status": "EQUAL_LEADING_MARGINAL_AND_COMMON_CLOCK_PATH_LAWS",
        "leading_separation_attempt": "DOES_NOT_SEPARATE",
        "classes": records,
        "fixed_reflection": [[1, 0], [0, -1]],
        "shared_normalizer": shared_normalization,
        "projected_pseudoinverses_equal": plus_equal,
        "projected_power_equalities_0_to_18": equal_powers,
        "shared_characteristic_polynomial": shared_characteristic,
        "common_annihilator": texts(product),
        "degree9_criterion": criterion9,
        "degree18_criterion": criterion18,
        "temporal_assumption": "Stationary centered OU dY=-L Y dt+sqrt(2c)P dW, c=9/tr(Lplus), same dimensionless clock and matched positive scale.",
        "temporal_conclusion": "The projected Gaussian process agrees under the fixed reflection; hence the leading quadratic intensity path law agrees. This is not the finite-positive-strength nonlinear law.",
    }
