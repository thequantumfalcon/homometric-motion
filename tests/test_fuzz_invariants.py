"""Exercise fuzzing oracles without adding Atheris to the stdlib test environment."""

import importlib.util
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "fuzz_invariants", Path(__file__).resolve().parents[1] / "tools" / "fuzz_invariants.py"
)
ORACLES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ORACLES)


class FuzzInvariantTests(unittest.TestCase):
    def test_corpus_creation_and_saved_input_replay_preserve_existing_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            corpus = root / "corpus"
            ORACLES.prepare_corpus(corpus)
            self.assertEqual(
                {path.name: path.read_bytes() for path in corpus.iterdir()}, ORACLES.seed_inputs()
            )
            discovered = corpus / "discovered-input"
            discovered.write_bytes(b"\0-7/3")
            (corpus / "rational-00").write_bytes(b"preserve an existing corpus entry")
            ORACLES.prepare_corpus(corpus)
            self.assertEqual(discovered.read_bytes(), b"\0-7/3")
            self.assertEqual(
                (corpus / "rational-00").read_bytes(), b"preserve an existing corpus entry"
            )
            crash = root / "crash-input"
            crash.write_bytes(b"\0\xff/2")
            ORACLES.prepare_corpus(crash)
            self.assertEqual(crash.read_bytes(), b"\0\xff/2")

    def test_seed_corpus_passes_independent_oracles(self):
        for name, payload in ORACLES.seed_inputs().items():
            with self.subTest(seed=name):
                ORACLES.check_input(payload)

    def test_incomplete_and_overlong_inputs_are_bounded(self):
        for payload in (b"", b"\0", b"\1", b"\2", b"\1\xff", b"\2\xff"):
            ORACLES.check_input(payload)
        with patch.object(ORACLES, "check_rational") as parser:
            ORACLES.check_input(b"\0" * (ORACLES.MAX_INPUT_BYTES + 1))
            parser.assert_not_called()

    def test_oracle_detects_parser_value_corruption_and_invalid_acceptance(self):
        with patch.object(ORACLES, "rational_from_text", return_value=Fraction(1)):
            with self.assertRaisesRegex(AssertionError, "exact value"):
                ORACLES.check_rational(b"1/2")
            with self.assertRaisesRegex(AssertionError, "invalid rational"):
                ORACLES.check_rational(b"1/0")

    def test_oracle_detects_inward_multiplication(self):
        with patch.object(ORACLES.Interval, "__mul__", return_value=ORACLES.Interval(0)):
            with self.assertRaisesRegex(AssertionError, "rounded inward"):
                ORACLES.check_input(ORACLES.seed_inputs()["interval-0"])

    def test_oracle_detects_wrong_integer_root(self):
        with patch.object(ORACLES, "integer_root", return_value=0):
            with self.assertRaisesRegex(AssertionError, "integer root bracket"):
                ORACLES.check_input(ORACLES.seed_inputs()["root-2-0"])


if __name__ == "__main__":
    unittest.main()
