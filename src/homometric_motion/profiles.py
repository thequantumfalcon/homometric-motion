"""Explicit versioned theorem domains and fresh cancellation-aware counts.

An allocation is inseparable from its selected domain and classifier threshold.
The original three builders retain their original contracts.
"""

import json
from copy import deepcopy
from fractions import Fraction as F
from importlib.resources import files

from .allocation import allocate_shape_budget
from .certificate import SCENARIOS, CertificateError, build_certificate
from .coordinate import core_digest
from .exposure import linear_exposure_certificate
from .kernel import kernel_exposure_certificate
from .kernel_observation import kernel_observation_certificate
from .position import position_certificate
from .robustness import frequency_certificate

KIND = "profiled_count_certificate"
PROFILES = ("short-exposure-v1", "long-exposure-v1")
DIGEST_ENCODING = "UTF-8 canonical JSON: sorted keys, compact separators, no NaN"
EXPOSURE_CAPS = {
    "short-exposure-v1": {"exact_geometry": F(1, 100000), "position_uncertainty": F(1, 100000)},
    "long-exposure-v1": {"exact_geometry": F(1, 1000), "position_uncertainty": F(1, 100)},
}
DISCLOSURE = (
    "These named domains and the cancellation-aware allocation were selected "
    "after earlier bounds and exploratory calculations were known. Each profile "
    "recomputes its own feasible tolerances, threshold and sufficient count. "
    "No blind selection, optimality or necessary sample-size claim is made."
)
QUALIFICATION = (
    "Conditional finite-window mathematical certificate under the selected "
    "fixed acquisition settings. The embedded core is an earlier reference "
    "calculation. No physical validation, independent human peer review, "
    "established novelty, practical feasibility or full-theorem formal "
    "verification is claimed."
)


def _parameters(core, profile, check):
    """Check the reference contract and select an explicitly versioned domain."""
    if not isinstance(profile, str) or profile not in PROFILES:
        raise ValueError("unknown count profile; choose an explicit supported version")
    scenario = core["scenario"]
    check(isinstance(scenario, str) and scenario in SCENARIOS, "profile supported scenario")
    check(
        core["schema_version"] == 1
        and core["status"] == "PASS"
        and core["revision_kind"] == "release_adaptation"
        and "certificate_kind" not in core,
        "profile ordinary reference core",
    )
    inputs = json.loads(files("homometric_motion").joinpath("inputs.json").read_text("utf-8"))
    beta = F(inputs["beta_cap_exact"])
    expected = {
        "beta_cap_exact": str(beta),
        "beta_band_exact": {"lower": str(beta / 2), "upper": str(beta)},
        "epsilon_exact": "1/100000",
        "edge_weight_radius_exact": "1/100001",
        "exposure_cap_exact": "1/100000000000000000000",
        "frequency_error_cap_exact": str(F(1, 10 ** (14 if scenario == "exact_geometry" else 16))),
        "position_error_cap_exact": str(F(0) if scenario == "exact_geometry" else F(1, 10**14)),
        "lag_lower_exact": "1000",
        "h_interval_exact": ["9/10", "11/10"],
        "b_interval_exact": ["0", "1"],
        "eta_exact": "1/100000",
        "target_individual_class_error": "1/20",
    }
    check(core["parameters"] == expected, "profile fixed reference parameters")
    check(core["stages"]["nominal"]["beta_cap_exact"] == str(beta), "profile nominal strength")
    check(
        core["stages"]["covariance"]["epsilon_exact"] == expected["epsilon_exact"],
        "profile covariance radius",
    )
    selected = deepcopy(expected)
    del selected["eta_exact"]
    selected["exposure_cap_exact"] = str(EXPOSURE_CAPS[profile][scenario])
    selected["allocation"] = {
        "method": "cancellation_shape_budget_v2",
        "direction_root_decimal_places": 24,
        "shape_root_decimal_places": 80,
        "scale_bisection_steps": 128,
        "maximum_bracket_doublings": 32,
        "interior_scale_factor_exact": "9/10",
        "error_allowances": "separate computed relative variance and normalized third-cumulant errors",
    }
    if profile == "long-exposure-v1":
        selected["kernel"] = {"time_cells_per_class": 512, "interval_decimal_places": 96}
    return selected


def _derive_profile(core, profile):
    """Reconstruct the selected chain conditional on the recorded core claims."""
    labels = []

    def check(ok, label):
        if not ok:
            raise CertificateError(label)
        labels.append(label)

    parameters = _parameters(core, profile, check)
    scenario = core["scenario"]
    nominal, covariance = core["stages"]["nominal"], core["stages"]["covariance"]
    cap = F(parameters["exposure_cap_exact"])
    if profile == "short-exposure-v1":
        moment = linear_exposure_certificate(nominal, covariance, cap, check)
        frequency = frequency_certificate(
            moment, nominal, covariance, F(parameters["frequency_error_cap_exact"]), check
        )
        nuisance = {"frequency": frequency}
        observed = frequency
        if scenario == "position_uncertainty":
            position_certificate(moment, nominal, frequency, F(0), check)
            observed = position_certificate(
                moment, nominal, frequency, F(parameters["position_error_cap_exact"]), check
            )
            nuisance["position"] = observed
    else:
        moment = kernel_exposure_certificate(nominal, covariance, cap, check)
        nuisance = kernel_observation_certificate(
            moment, nominal, covariance, {**parameters, "scenario": scenario}, check
        )
        observed = nuisance["observation_union"]
    check(observed["status"] == "CERTIFIED_SEPARATED", "profile separated observation union")
    allocation = allocate_shape_budget(observed, nominal, parameters, check)
    return {
        "parameters": parameters,
        "moment_evidence": moment,
        "nuisance_evidence": nuisance,
        "observation_bounds": observed,
        "allocation": allocation,
        "checks": {"count": len(labels), "passed": labels},
    }


def build_count_certificate(*, profile, scenario="exact_geometry"):
    """Recompute one explicit profile from bundled mathematical inputs only."""
    if not isinstance(profile, str) or profile not in PROFILES:
        raise ValueError("unknown count profile; choose an explicit supported version")
    if not isinstance(scenario, str) or scenario not in SCENARIOS:
        raise ValueError("unknown count scenario")
    core = build_certificate(scenario=scenario)
    digest = core_digest(core)
    selected = _derive_profile(core, profile)
    if core_digest(core) != digest:
        raise CertificateError("profile derivation mutated the reference core")
    return {
        "schema_version": 1,
        "certificate_kind": KIND,
        "revision_kind": "release_adaptation",
        "status": "PASS",
        "profile": profile,
        "scenario": scenario,
        "core_certificate": core,
        "core_certificate_sha256": digest,
        "core_digest_encoding": DIGEST_ENCODING,
        **selected,
        "selection_disclosure": DISCLOSURE,
        "qualification": QUALIFICATION,
    }


def validate_saved_count(envelope):
    """Check a saved construction; do not authenticate its upstream core claims."""
    if (
        envelope.get("schema_version") != 1
        or envelope.get("certificate_kind") != KIND
        or envelope.get("revision_kind") != "release_adaptation"
        or envelope.get("status") != "PASS"
    ):
        raise ValueError("unsupported profiled count certificate")
    core = envelope["core_certificate"]
    if not isinstance(core, dict) or "certificate_kind" in core:
        raise ValueError("profile requires an ordinary reference core")
    if envelope["scenario"] != core["scenario"]:
        raise ValueError("profile/reference scenario mismatch")
    if envelope["core_certificate_sha256"] != core_digest(core):
        raise ValueError("recorded profile reference content digest mismatch")
    if envelope["core_digest_encoding"] != DIGEST_ENCODING:
        raise ValueError("recorded profile reference digest encoding mismatch")
    if envelope["selection_disclosure"] != DISCLOSURE or envelope["qualification"] != QUALIFICATION:
        raise ValueError("recorded profile scope disclosure mismatch")

    # Validate the allowlist and contract before the more expensive cell proof.
    def check(ok, label):
        if not ok:
            raise CertificateError(label)

    expected = _parameters(core, envelope["profile"], check)
    if envelope["parameters"] != expected:
        raise ValueError("recorded parameters differ from the selected profile")
    selected = _derive_profile(core, envelope["profile"])
    for key, value in selected.items():
        if envelope[key] != value:
            raise ValueError("recorded profile differs from its exact construction: " + key)
    return selected["allocation"]
