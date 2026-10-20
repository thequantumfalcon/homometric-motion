"""A self-contained exact certificate for one fixed nine-point homometric pair."""

import json
from collections import Counter

from .smallpair_bounds import remainder_evidence
from .smallpair_geometry import derive_geometry, temporal_and_leading
from .smallpair_mean import derive_mean_and_joint
from .smallpair_moments import raw_moments, shape_evidence
from .smallpair_strength import strength_bands

KIND = "nine_point_finite_motion_v1"
MODEL = "fixed_nine_point_v1"
MAX_SAVED_NODES = 150000
MAX_SAVED_TEXT = 20_000_000
MAX_SAVED_DEPTH = 20
MAX_SAVED_LIST = 3000

DISCLOSURE = (
    "This fixed release adaptation follows known leading-law equality and finite-motion "
    "polynomial investigations. The pair, frequency, graph and declared grids are fixed; "
    "the computation is informed reproduction, not a blind experiment or search."
)
ASSUMPTIONS = [
    "A permanent graph is built from the exact mean positions, with unit positive edges for distances below 15/2; displaced positions do not change its topology.",
    "Centered Gaussian displacement Y with covariance D=9 Lplus/tr(Lplus), COM removed.",
    "Exact frequency omega=2*pi/3 and intensity |sum exp(i*omega*x_i+i*omega*sqrt(beta)*Y_i)|^2.",
    "The global first-two-moment and matched-strength remainder comparisons use the same finite positive strength s=beta*omega^2/2 in both classes.",
    "The separate local strength-band result permits independently chosen fixed class strengths only within a certified common t band, with common calibrated instantaneous intensity units.",
    "Only the separate leading-path equality additionally assumes stationary OU drift-L, covariance D and a common dimensionless time coordinate.",
]
LIMITATIONS = [
    "The global first-two-moment noncoincidence theorem requires common calibrated strength.",
    "Independent class strengths are covered only by the separate local strength-band certificate; arbitrary strengths, time-varying settings, positions, frequency, springs and unknown detector channels are not certified.",
    "The leading marginal and common-clock quadratic path laws are equal; they do not distinguish this pair.",
    "The mean has exactly one interior crossing; skewness has at least two, with no exact total root count claimed.",
    "The matched-strength remainder cap1/10 is unresolved; the smaller certified band is retained.",
    "There is no uniform positive global moment gap, classifier, finite-count guarantee or practical acquisition budget.",
    "No physical validation, novelty, minimality, optimality or complete proof-assistant formalization is claimed.",
]


class SmallPairError(ArithmeticError):
    """A declared exact identity or proof condition failed."""


def parameters():
    return {
        "n": 9,
        "motif": [0, 1, 5],
        "class_shifts": {"A": [0, 10, 22], "B": [0, 12, 22]},
        "graph_threshold_exact": "15/2",
        "frequency_exact": "2*pi/3",
        "covariance": "9*Lplus/tr(Lplus)",
        "s_definition": "beta*omega^2/2",
        "t_definition": "exp(-(9/158)*s)",
        "strength_domain": "same finite s>0 in both classes",
        "raw_moment_orders": [1, 2, 3],
        "mean_root_dyadic_bits": 80,
        "shape_diagnostic_t_values": [f"{j}/16" for j in range(1, 16)],
        "remainder_cap_denominators": [10**k for k in range(8, 0, -1)],
        "maximum_polynomial_degree": 2400,
        "maximum_coefficient_bits": 65536,
        "maximum_homogeneous_updates": 20_000_000,
        "primary_joint_moment_order": 2,
        "fallback_joint_moment_order": 3,
        "independent_strength_center_exact": "13/16",
        "independent_strength_radii_exact": ["1/16", "1/64", "1/256", "1/1024", "1/4096"],
        "independent_strength_projection_rule": "pooled mu2 derivative divided by pooled mu1 derivative at the fixed center",
        "independent_strength_maximum_degree": 320,
        "independent_strength_maximum_coefficient_bits": 131072,
        "independent_strength_maximum_transform_updates": 5_000_000,
    }


def build_small_pair_certificate():
    """Reconstruct the fixed certificate from exact small mathematical inputs."""
    checks = Counter()

    def check(ok, label):
        if not ok:
            raise SmallPairError(label)
        checks[label] += 1

    classes, geometry = derive_geometry(check)
    leading = temporal_and_leading(classes, check)
    raw, raw_record = raw_moments(classes, check)
    mean, joint = derive_mean_and_joint(raw, check)
    polynomials, shape = shape_evidence(raw, check)
    remainder = remainder_evidence(raw, polynomials, check)
    independent_strength = strength_bands(raw, mean, joint, check)
    return {
        "schema_version": 1,
        "certificate_kind": KIND,
        "revision_kind": "release_adaptation",
        "status": "PASS",
        "model": MODEL,
        "parameters": parameters(),
        "geometry": geometry,
        "leading_law": leading,
        "raw_moments": raw_record,
        "mean_difference": mean,
        "joint_moments": joint,
        "shape_ordering": shape,
        "matched_strength_remainder": remainder,
        "independent_strength_bands": independent_strength,
        "checks": {
            "count": sum(checks.values()),
            "passed": sorted(checks),
            "by_label": dict(sorted(checks.items())),
        },
        "selection_disclosure": DISCLOSURE,
        "assumptions": list(ASSUMPTIONS),
        "limitations": list(LIMITATIONS),
    }


_SCIENTIFIC_KEYS = {
    "schema_version",
    "certificate_kind",
    "revision_kind",
    "status",
    "model",
    "parameters",
    "geometry",
    "leading_law",
    "raw_moments",
    "mean_difference",
    "joint_moments",
    "shape_ordering",
    "matched_strength_remainder",
    "independent_strength_bands",
    "checks",
    "selection_disclosure",
    "assumptions",
    "limitations",
}


def _bounded_saved_record(record):
    """Reject unbounded/non-JSON input before any certificate reconstruction."""
    totals = [0, 0]

    def visit(value, depth):
        totals[0] += 1
        if depth > MAX_SAVED_DEPTH or totals[0] > MAX_SAVED_NODES:
            raise ValueError("saved certificate nesting/node limit")
        if isinstance(value, dict):
            if len(value) > 1000:
                raise ValueError("saved mapping size limit")
            for key, child in value.items():
                if type(key) is not str or not 0 < len(key) <= 200:
                    raise ValueError("bounded string key required")
                totals[1] += len(key)
                visit(child, depth + 1)
        elif isinstance(value, list):
            if len(value) > MAX_SAVED_LIST:
                raise ValueError("saved coefficient/list length limit")
            for child in value:
                visit(child, depth + 1)
        elif type(value) is str:
            if len(value) > 100000:
                raise ValueError("saved rational/text length limit")
            totals[1] += len(value)
        elif type(value) is int:
            if value.bit_length() > 63:
                raise ValueError("large exact coefficients must use bounded decimal text")
        elif value is not None and type(value) is not bool:
            raise ValueError("saved certificate must contain exact JSON values")
        if totals[1] > MAX_SAVED_TEXT:
            raise ValueError("saved certificate text budget")

    visit(record, 0)


def validate_saved_small_pair(envelope):
    """Rebuild fixed scientific values; saved provenance remains unauthenticated.

    The CLI separately checks any ``source_revision`` against its installed
    manifest. This function does not authenticate the supplied record or model.
    """
    if type(envelope) is not dict:
        raise ValueError("small-pair certificate must be an object")
    _bounded_saved_record(envelope)
    keys = set(envelope)
    if keys not in (_SCIENTIFIC_KEYS, _SCIENTIFIC_KEYS | {"source_revision"}):
        raise ValueError("small-pair certificate field allowlist")
    if (
        type(envelope["schema_version"]) is not int
        or envelope["schema_version"] != 1
        or envelope["certificate_kind"] != KIND
        or envelope["revision_kind"] != "release_adaptation"
        or envelope["status"] != "PASS"
        or envelope["model"] != MODEL
    ):
        raise ValueError("unsupported small-pair certificate contract")
    if envelope["parameters"] != parameters():
        raise ValueError("saved small-pair parameters differ from fixed model")
    scientific = {key: envelope[key] for key in _SCIENTIFIC_KEYS}
    expected = build_small_pair_certificate()

    def canonical(value):
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    if canonical(scientific) != canonical(expected):
        raise ValueError("saved small-pair science differs from fresh exact reconstruction")
    return expected
