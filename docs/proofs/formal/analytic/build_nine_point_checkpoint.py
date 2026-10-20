"""Build or check a partial Lean checkpoint from the freshly installed model."""

import argparse
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path

MAX_DEGREE = 400
MAX_INTEGER_DIGITS = 20000
MAX_INTEGER_BITS = 65536
MAX_SOURCE_BYTES = 100000
MAX_MAPPING_BYTES = 1000000
OUTPUT_NAMES = ("NinePointBezout.lean", "mapping.json")
THEOREMS = (
    "bezout_identity",
    "no_common_zero",
    "mean_factorization",
    "cofactor_positive",
    "joint_moment_noncoincidence",
)
POINTERS = {
    "a": "/joint_moments/attempts/0/integer_bezout/A_for_H",
    "h": "/joint_moments/attempts/0/H",
    "b": "/joint_moments/attempts/0/integer_bezout/B_for_difference",
    "d": "/joint_moments/attempts/0/difference",
    "meanDifference": "/mean_difference/difference_coefficients",
}
CONSTANT_POINTER = "/joint_moments/attempts/0/integer_bezout/positive_constant"

HEADER = """import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

/- Only explicit real polynomial identities and their logical consequence.
   The mapping from Gaussian intensity moments is a separate argument. -/

set_option maxHeartbeats 2000000
set_option maxRecDepth 8192

namespace HomometricMotion.NinePoint

"""

THEOREM_TEMPLATE = """def cofactor (t : ℝ) : ℝ :=
  t^39 * (1-t)^2 * (t+1)^2 * (t^2+t+1) *
  (t^2+1)^2 * (t^4+1)^2 * (t^8+1)

theorem bezout_identity (t : ℝ) :
    a t * h t + b t * d t = constant := by
  unfold a h b d constant
  ring

theorem no_common_zero (t : ℝ) : h t ≠ 0 ∨ d t ≠ 0 := by
  by_cases hh : h t = 0
  · right
    intro hd
    have identity := bezout_identity t
    rw [hh, hd] at identity
    norm_num [constant] at identity
  · exact Or.inl hh

theorem mean_factorization (t : ℝ) :
    meanDifference t = cofactor t * h t := by
  unfold meanDifference cofactor h
  ring

theorem cofactor_positive (t : ℝ) (ht : 0 < t) (hupper : t < 1) :
    0 < cofactor t := by
  have ht1 : 0 < 1-t := by linarith
  unfold cofactor
  positivity

theorem joint_moment_noncoincidence (t : ℝ) (ht : 0 < t) (hupper : t < 1) :
    meanDifference t ≠ 0 ∨ d t ≠ 0 := by
  rcases no_common_zero t with hh | hd
  · left
    rw [mean_factorization]
    exact mul_ne_zero (ne_of_gt (cofactor_positive t ht hupper)) hh
  · exact Or.inr hd

end HomometricMotion.NinePoint

#print axioms HomometricMotion.NinePoint.bezout_identity
#print axioms HomometricMotion.NinePoint.no_common_zero
#print axioms HomometricMotion.NinePoint.mean_factorization
#print axioms HomometricMotion.NinePoint.cofactor_positive
#print axioms HomometricMotion.NinePoint.joint_moment_noncoincidence
"""


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def integer(text):
    """Parse bounded canonical decimal integers without changing Python limits."""
    if type(text) is not str or not 1 <= len(text) <= MAX_INTEGER_DIGITS + 1:
        raise ValueError("bounded integer coefficient text required")
    negative = text.startswith("-")
    digits = text[1:] if negative else text
    if (
        not digits
        or len(digits) > MAX_INTEGER_DIGITS
        or not digits.isascii()
        or not digits.isdigit()
        or (len(digits) > 1 and digits[0] == "0")
        or (negative and digits == "0")
    ):
        raise ValueError("canonical signed integer coefficient required")
    value = 0
    for start in range(0, len(digits), 9):
        chunk = digits[start : start + 9]
        value = value * 10 ** len(chunk) + int(chunk)
    if value.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("integer coefficient bit bound")
    return -value if negative else value


def integer_text(value):
    if type(value) is not int or value.bit_length() > MAX_INTEGER_BITS:
        raise ValueError("bounded exact integer required")
    sign = "-" if value < 0 else ""
    value = abs(value)
    chunks = []
    while value:
        value, part = divmod(value, 10**9)
        chunks.append(part)
    digits = str(chunks[-1]) + "".join(f"{x:09d}" for x in reversed(chunks[:-1])) if chunks else "0"
    if len(digits) > MAX_INTEGER_DIGITS:
        raise ValueError("decimal output bound")
    return sign + digits


def pointer(document, path):
    value = document
    for key in path.strip("/").split("/"):
        value = value[int(key)] if type(value) is list else value[key]
    return value


def coefficients(value, length):
    if type(value) is not list or len(value) != length or length > MAX_DEGREE + 1:
        raise ValueError("fixed polynomial length required")
    result = [integer(x) for x in value]
    if result[-1] == 0:
        raise ValueError("complete polynomial degree required")
    return result


def trim(values):
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return values


def multiply(left, right):
    if not left or not right or len(left) + len(right) - 2 > MAX_DEGREE:
        raise ValueError("bounded polynomial product required")
    result = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            result[i + j] += x * y
    if any(value.bit_length() > MAX_INTEGER_BITS for value in result):
        raise ValueError("polynomial product coefficient bound")
    return trim(result)


def add(left, right):
    return trim(
        [
            (left[i] if i < len(left) else 0) + (right[i] if i < len(right) else 0)
            for i in range(max(len(left), len(right)))
        ]
    )


def expression(values):
    terms = [
        f"({integer_text(value)} : ℝ)" + (f" * t^{index}" if index else "")
        for index, value in enumerate(values)
        if value
    ]
    return " +\n    ".join(terms) if terms else "(0 : ℝ)"


def fresh_outputs():
    """Require the installed API and freshly reconstruct every scientific input."""
    import homometric_motion
    from homometric_motion import build_small_pair_certificate
    from homometric_motion.cli import verify_source_manifest

    distribution = importlib.metadata.distribution("homometric-motion")
    expected_package = Path(distribution.locate_file("homometric_motion/__init__.py")).resolve()
    if Path(homometric_motion.__file__).resolve() != expected_package:
        raise ValueError("run with the wheel-installed package, not a source checkout")
    provenance = verify_source_manifest()
    guard = sys.get_int_max_str_digits()
    certificate = build_small_pair_certificate()
    if (
        certificate["schema_version"] != 1
        or certificate["certificate_kind"] != "nine_point_finite_motion_v1"
        or certificate["model"] != "fixed_nine_point_v1"
        or certificate["status"] != "PASS"
    ):
        raise ValueError("fixed fresh nine-point certificate contract required")
    if (
        len(certificate["joint_moments"]["attempts"]) != 1
        or certificate["joint_moments"]["attempts"][0]["raw_moment_order"] != 2
        or certificate["joint_moments"]["attempts"][0]["unit_gcd"] is not True
        or certificate["joint_moments"]["attempts"][0]["positive_difference_denominator"] != "1"
    ):
        raise ValueError("unscaled first-two-moment Bezout contract required")
    lengths = {"a": 320, "h": 16, "b": 15, "d": 321, "meanDifference": 81}
    polys = {
        name: coefficients(pointer(certificate, path), lengths[name])
        for name, path in POINTERS.items()
    }
    constant = integer(pointer(certificate, CONSTANT_POINTER))
    if constant <= 0:
        raise ValueError("strictly positive Bezout constant required")
    if add(multiply(polys["a"], polys["h"]), multiply(polys["b"], polys["d"])) != [constant]:
        raise ValueError("complete integer Bezout expansion failed")
    factor_h = coefficients(certificate["mean_difference"]["factorization"]["H_coefficients"], 16)
    if polys["h"] != factor_h:
        raise ValueError("mean and joint residual mismatch")
    cofactor = [0] * 39 + [1]
    for factor in (
        [1, -1],
        [1, -1],
        [1, 1],
        [1, 1],
        [1, 1, 1],
        [1, 0, 1],
        [1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1] + [0] * 7 + [1],
    ):
        cofactor = multiply(cofactor, factor)
    if multiply(cofactor, polys["h"]) != polys["meanDifference"]:
        raise ValueError("complete fixed positive-cofactor expansion failed")
    for order, name, length in ((1, "meanDifference", 81), (2, "d", 321)):
        raw = certificate["raw_moments"]["classes"]
        first = coefficients(raw["A"][str(order)]["coefficients"], length)
        second = coefficients(raw["B"][str(order)]["coefficients"], length)
        if raw["A"][str(order)]["denominator"] != "1" or raw["B"][str(order)]["denominator"] != "1":
            raise ValueError("raw moment denominator mismatch")
        if [y - x for x, y in zip(first, second)] != polys[name]:
            raise ValueError("full raw-moment difference mapping failed")
    source = HEADER
    for name, values in polys.items():
        source += f"def {name} (t : ℝ) : ℝ :=\n    {expression(values)}\n\n"
    source += f"def constant : ℝ := {integer_text(constant)}\n\n" + THEOREM_TEMPLATE
    lean = source.encode("utf-8")
    if len(lean) > MAX_SOURCE_BYTES:
        raise ValueError("Lean source byte bound")
    mapping = {
        "schema_version": 1,
        "certificate_kind": certificate["certificate_kind"],
        "source_revision": provenance,
        "fresh_certificate_canonical_sha256": digest(canonical(certificate)),
        "generator_sha256": digest(Path(__file__).read_bytes()),
        "lean_source": {"path": OUTPUT_NAMES[0], "bytes": len(lean), "sha256": digest(lean)},
        "polynomials": {
            name: {
                "source_json_pointer": POINTERS[name],
                "degree": len(values) - 1,
                "coefficients_ascending": [integer_text(value) for value in values],
                "coefficients_canonical_sha256": digest(
                    canonical([integer_text(value) for value in values])
                ),
            }
            for name, values in polys.items()
        },
        "constant": {
            "source_json_pointer": CONSTANT_POINTER,
            "strictly_positive_integer": integer_text(constant),
        },
        "theorems": ["HomometricMotion.NinePoint." + name for name in THEOREMS],
        "verification": {
            "complete_integer_bezout_reexpansion": True,
            "complete_positive_cofactor_reexpansion": True,
            "complete_first_two_raw_moment_difference_mapping": True,
            "installed_source_manifest_rechecked_after_computation": True,
            "integer_conversion_guard_before_and_after": guard,
        },
        "scope": [
            "Five explicit real-polynomial identities or consequences, including no common zero on 0<t<1.",
            "This generator does not execute Lean; Lean compilation is a separate verification step.",
            "The Gaussian-moment mapping, graph/covariance construction and probability-law implication remain separate proof obligations.",
            "The independent-strength bands, Sturm root count, skewness reversals and Taylor bounds are not formalized here.",
            "No physical assumption, detector model, count guarantee or complete-theorem formalization is authenticated.",
        ],
    }
    if verify_source_manifest() != provenance or sys.get_int_max_str_digits() != guard:
        raise ValueError("installed source binding or integer guard changed")
    payload = (json.dumps(mapping, indent=2, sort_keys=True, ensure_ascii=True) + "\n").encode()
    if len(payload) > MAX_MAPPING_BYTES:
        raise ValueError("mapping byte bound")
    return {OUTPUT_NAMES[0]: lean, OUTPUT_NAMES[1]: payload}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output-dir", type=Path, help="new directory; existing paths are refused")
    mode.add_argument("--check", type=Path, help="rebuild and compare both files without writing")
    args = parser.parse_args()
    if args.output_dir is not None and (args.output_dir.exists() or args.output_dir.is_symlink()):
        raise FileExistsError("output directory must be new")
    if args.check is not None and (not args.check.is_dir() or args.check.is_symlink()):
        raise ValueError("check requires an existing ordinary directory")
    outputs = fresh_outputs()
    if args.check is not None:
        for name, expected in outputs.items():
            path = args.check / name
            if path.is_symlink() or path.read_bytes() != expected:
                raise ValueError("checkpoint differs from fresh installed reconstruction: " + name)
        print("PASS: both checkpoint files match a fresh installed-model reconstruction.")
    else:
        args.output_dir.mkdir()
        for name, payload in outputs.items():
            with (args.output_dir / name).open("xb") as stream:
                stream.write(payload)
        print("PASS: five polynomial statements and full coefficient mapping written.")
        print("Lean compilation and the Gaussian-model interpretation are separate checks.")


if __name__ == "__main__":
    main()
