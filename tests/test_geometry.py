"""Independent symbolic homometry and Gaussian calibration models."""

import unittest
from collections import Counter
from fractions import Fraction as F
from math import comb, factorial

from homometric_motion.geometry import energy_moments, exact_covariance


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def symbolic_positions(translation):
    """Coordinates in the formal basis (1, theta/omega, phi/omega)."""
    motif = []
    for j in range(10):
        motif.append((3 * j, 0, (-1) ** j if j >= 2 else 0))
        motif.append((3 * j + 1, (-1) ** j, 0))
    motif.append((30, 0, 0))
    return sorted((x + t, a, b) for t in translation for x, a, b in motif)


def differences(positions):
    return Counter(
        tuple(a - b for a, b in zip(left, right)) for left in positions for right in positions
    )


def chi_square_moments(eigenvalues, order):
    """Convolve explicit moments of independent scaled squared Gaussians."""
    moments = [F(1)] + [F(0)] * order
    for eigenvalue in eigenvalues:
        component = [
            eigenvalue**r * F(factorial(2 * r), 2**r * factorial(r)) for r in range(order + 1)
        ]
        moments = [
            sum(
                (comb(r, j) * moments[j] * component[r - j] for j in range(r + 1)),
                F(0),
            )
            for r in range(order + 1)
        ]
    return moments


class GeometryTests(unittest.TestCase):
    def test_exact_symbolic_homometry_and_noncongruence(self):
        """Equal difference multiplicities imply equal clean Fourier intensity."""
        a = symbolic_positions((0, 31, 63))
        b = symbolic_positions((0, 32, 63))
        self.assertEqual(len(set(a)), 63)
        self.assertEqual(len(set(b)), 63)
        self.assertEqual(differences(a), differences(b))
        self.assertNotEqual(a, b)
        # Shifts have magnitude below 1/8, so different integer parts cannot
        # become equal through the fixed small phase shifts.
        self.assertNotEqual([row[0] for row in a], [row[0] for row in b])
        # Both sets have minimum 0 and maximum 93. Any isometry of the line
        # carrying one to the other must be identity or reflection about 93/2.
        reflected = sorted((93 - x, -theta, -phi) for x, theta, phi in a)
        self.assertNotEqual(reflected, b)
        self.assertNotEqual([row[0] for row in reflected], [row[0] for row in b])

    def test_graph_and_covariance_normalization(self):
        for side, translation, chord, trace in (
            ("A", (0, 31, 63), 20, F(121486, 189)),
            ("B", (0, 32, 63), 41, F(121570, 189)),
        ):
            with self.subTest(side=side):
                positions = symbolic_positions(translation)
                edges = {
                    (i, j)
                    for i in range(63)
                    for j in range(i + 1, 63)
                    if positions[j][0] - positions[i][0] < F(5, 2)
                }
                self.assertEqual(edges, {(i, i + 1) for i in range(62)} | {(chord, chord + 2)})
                covariance, actual_trace = exact_covariance(side, require)
                self.assertEqual(actual_trace, trace)
                self.assertEqual(sum(covariance[i][i] for i in range(63)), 63)
                # Voltage for unit current between the two terminal vertices.
                lp = [[value * trace / 63 for value in row] for row in covariance]
                voltage = [row[0] - row[62] for row in lp]
                energy = sum((voltage[i] - voltage[j]) ** 2 for i, j in edges)
                # 60 series unit resistors plus the triangle's 2/3 resistor.
                self.assertEqual(energy, F(182, 3))
                self.assertEqual(voltage[0] - voltage[62], energy)
                self.assertEqual(sum(voltage), 0)
        with self.assertRaises(ValueError):
            exact_covariance("unknown", require)

    def test_energy_moments_against_known_gaussian_eigenvalues(self):
        """Non-diagonal and singular matrices exercise trace contraction."""
        models = [
            ([[F(1), F(1, 2)], [F(1, 2), F(1)]], [F(1, 2), F(3, 2)]),
            ([[F(1), F(-1)], [F(-1), F(1)]], [F(0), F(2)]),
        ]
        for covariance, eigenvalues in models:
            with self.subTest(eigenvalues=eigenvalues):
                traces, moments = energy_moments(covariance, require)
                independent = chi_square_moments(eigenvalues, 12)
                for order in range(1, 13):
                    self.assertEqual(traces[order], sum(x**order for x in eigenvalues))
                    self.assertEqual(moments[order], independent[order])


if __name__ == "__main__":
    unittest.main()
