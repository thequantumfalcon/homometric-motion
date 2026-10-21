"""Mutation checks for the saved mathematical witness validator."""

import json
import unittest
from copy import deepcopy
from pathlib import Path

from verify_results import compare_arb, verify_arb, verify_sage

ROOT = Path(__file__).resolve().parent


class WitnessControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sage = json.loads((ROOT / "results/sage.json").read_text("utf-8"))
        cls.arb = json.loads((ROOT / "results/arb_384.json").read_text("utf-8"))
        cls.other = json.loads((ROOT / "results/arb_512.json").read_text("utf-8"))

    def test_original_witnesses(self):
        verify_sage(self.sage)
        compare_arb(self.arb, self.other)

    def test_changed_second_moment(self):
        data = deepcopy(self.sage)
        coefficients = data["classes"]["B"]["moments"]["2"]["coefficients"]
        coefficients[0] = str(int(coefficients[0]) + 1)
        coefficients[1] = str(int(coefficients[1]) - 1)
        with self.assertRaisesRegex(ValueError, "Bezout"):
            verify_sage(data)

    def test_impossible_sufficient_count(self):
        data = deepcopy(self.arb)
        data["sufficient_iid_observations"] = 1
        with self.assertRaisesRegex(ValueError, "sufficient witness"):
            verify_arb(data)

    def test_overstated_necessary_count(self):
        data = deepcopy(self.arb)
        data["necessary_iid_observations_at_least"] = 10**12
        with self.assertRaisesRegex(ValueError, "necessary witness"):
            verify_arb(data)

    def test_changed_strength_contract(self):
        data = deepcopy(self.arb)
        data["beta_cap"] = "1/1000000"
        with self.assertRaisesRegex(ValueError, "contract"):
            verify_arb(data)

    def test_omitted_mass(self):
        data = deepcopy(self.arb)
        data["classes"]["A"]["partial_mass"] = {"lower": "0", "upper": "1/2"}
        with self.assertRaisesRegex(ValueError, "normalization"):
            verify_arb(data)

    def test_reversed_interval(self):
        data = deepcopy(self.arb)
        data["affinity"]["lower"], data["affinity"]["upper"] = (
            data["affinity"]["upper"],
            data["affinity"]["lower"],
        )
        with self.assertRaisesRegex(ValueError, "ordered endpoints"):
            verify_arb(data)

    def test_duplicate_precision_not_second_run(self):
        with self.assertRaisesRegex(ValueError, "distinct precisions"):
            compare_arb(self.arb, self.arb)


if __name__ == "__main__":
    unittest.main()
