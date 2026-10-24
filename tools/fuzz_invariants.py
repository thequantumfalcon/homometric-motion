"""Independent, bounded oracles for the optional arithmetic fuzzer."""

import re
import struct
from fractions import Fraction

from homometric_motion.arithmetic import (
    Interval,
    integer_root,
    rational_from_text,
    rational_text,
)

MAX_INPUT_BYTES = 2048
RATIONAL_GRAMMAR = re.compile(r"-?[0-9]+(?:/[0-9]+)?")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check_rational(payload):
    """Compare accepted text to an ASCII grammar and the stdlib Fraction parser."""
    text = payload.decode("utf-8", errors="surrogateescape")
    valid = RATIONAL_GRAMMAR.fullmatch(text) is not None
    if valid and "/" in text:
        valid = int(text.split("/")[1]) > 0
    if not valid:
        try:
            rational_from_text(text)
        except ValueError:
            return
        raise AssertionError("invalid rational text was accepted")
    expected = Fraction(text)
    actual = rational_from_text(text)
    require(actual == expected, "rational parser changed the exact value")
    require(rational_text(actual) == str(expected), "rational serialization is not canonical")
    require(rational_from_text(rational_text(actual)) == expected, "rational round trip")


def fraction_from_bytes(payload):
    numerator, denominator, exponent = struct.unpack(">iHB", payload[:7].ljust(7, b"\0"))
    return Fraction(numerator, (denominator + 1) * 10 ** (exponent % 101))


def check_enclosure(interval, candidates):
    require(interval.lower <= min(candidates), "lower endpoint rounded inward")
    require(interval.upper >= max(candidates), "upper endpoint rounded inward")


def check_intervals(payload):
    values = [fraction_from_bytes(payload[start : start + 7]) for start in range(0, 28, 7)]
    lo, hi = sorted(values[:2])
    other_lo, other_hi = sorted(values[2:])
    first, second = Interval.bounds(lo, hi), Interval.bounds(other_lo, other_hi)
    check_enclosure(first, (lo, hi))
    check_enclosure(second, (other_lo, other_hi))
    lo, hi = first.lower, first.upper
    other_lo, other_hi = second.lower, second.upper
    corners = [(a, b) for a in (lo, hi) for b in (other_lo, other_hi)]
    check_enclosure(first + second, [a + b for a, b in corners])
    check_enclosure(first - second, [a - b for a, b in corners])
    check_enclosure(first * second, [a * b for a, b in corners])
    check_enclosure(-first, (-lo, -hi))
    # The rounded denominator may contain zero even when the input endpoints do not.
    if second.lower <= 0 <= second.upper:
        try:
            first / second
        except ZeroDivisionError:
            pass
        else:
            raise AssertionError("division by a zero-containing interval was accepted")
    else:
        check_enclosure(first / second, [a / b for a, b in corners])
    degree = payload[28] % 7 if len(payload) > 28 else 0
    candidates = [lo**degree, hi**degree]
    if degree > 0 and degree % 2 == 0 and lo <= 0 <= hi:
        candidates.append(Fraction(0))
    check_enclosure(first**degree, candidates)


def check_roots(payload):
    value = abs(fraction_from_bytes(payload))
    degree = 1 + (payload[7] % 6 if len(payload) > 7 else 0)
    radicand = Interval(value)
    check_enclosure(radicand, (value,))
    root = radicand.root(degree)
    require(root.lower >= 0, "negative root lower bound")
    require(root.lower**degree <= radicand.lower, "root lower power bracket")
    require(root.upper**degree >= radicand.upper, "root upper power bracket")
    integer = int.from_bytes(payload[8:24], "big")
    floor = integer_root(integer, degree)
    require(floor >= 0, "negative integer root")
    require(floor**degree <= integer < (floor + 1) ** degree, "integer root bracket")


def check_input(data):
    """Keep arithmetic costs bounded independently of fuzzer command-line flags."""
    if len(data) > MAX_INPUT_BYTES:
        return
    mode = data[0] % 3 if data else 0
    payload = data[1:]
    if mode == 0:
        check_rational(payload)
    elif mode == 1:
        check_intervals(payload)
    else:
        check_roots(payload)


def seed_inputs():
    """Readable seed definitions; binary corpus and discoveries stay under .build."""
    seeds = {
        f"rational-{index:02d}": b"\0" + text.encode("utf-8")
        for index, text in enumerate(
            (
                "",
                "0",
                "-0",
                "1/2",
                "-0002/0003",
                "1234567890/37",
                "1/0",
                "1/-2",
                "1/2/3",
                "+2",
                " 2",
                "2\n",
                "٢",
                "1e3",
                "0" * 100,
                "9" * 1024 + "/7",
            )
        )
    }
    seeds["invalid-utf8"] = b"\0\xff/2"
    interval_cases = (
        ((-7, 2, 0), (-1, 10, 0), (2, 6, 0), (13, 4, 0), 3),
        ((-2, 0, 0), (3, 0, 0), (-1, 0, 0), (1, 0, 0), 2),
        ((1, 0, 100), (2, 0, 100), (1, 0, 100), (2, 0, 100), 6),
        ((0, 0, 0), (0, 0, 0), (-3, 0, 0), (-1, 0, 0), 0),
        ((-(2**31), 65535, 0), (2**31 - 1, 0, 0), (1, 1, 72), (2, 2, 72), 4),
    )
    for index, case in enumerate(interval_cases):
        seeds[f"interval-{index}"] = (
            b"\1" + b"".join(struct.pack(">iHB", *value) for value in case[:4]) + bytes([case[4]])
        )
    for degree in range(1, 7):
        for offset in (-1, 0, 1):
            integer = 37**degree + offset
            seeds[f"root-{degree}-{offset}"] = (
                b"\2"
                + struct.pack(">iHB", 1, 0, 100)
                + bytes([degree - 1])
                + integer.to_bytes(16, "big")
            )
    seeds["root-zero"] = b"\2" + b"\0" * 24
    return seeds


def prepare_corpus(path):
    """Seed a new corpus; leave an existing corpus or crash-replay file untouched."""
    if not path.exists():
        path.mkdir(parents=True)
        for name, payload in seed_inputs().items():
            (path / name).write_bytes(payload)
