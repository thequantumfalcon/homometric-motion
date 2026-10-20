"""Deterministic scientific orchestration from packaged mathematical inputs."""

import json
from fractions import Fraction as F
from importlib.resources import files

from .counts import count_certificate
from .motion import covariance_certificate, nominal_certificate
from .robustness import exposure_certificate, frequency_certificate


class CertificateError(ArithmeticError):
    """A required mathematical or input check failed."""


def build_certificate() -> dict:
    """Recompute the fixed theorem's complete chain using the standard library.

    This function reads only the two mathematical resources bundled with the
    package. Source-integrity verification is performed separately by the CLI.
    The returned object contains no execution time, host path or random value.
    """
    package = files("homometric_motion")
    inputs = json.loads(package.joinpath("inputs.json").read_text(encoding="utf-8"))
    protocol = json.loads(package.joinpath("protocol.json").read_text(encoding="utf-8"))
    checks = []

    def check(condition, label):
        if not condition:
            raise CertificateError(label)
        checks.append(label)

    check(inputs["schema_version"] == protocol["schema_version"] == 1, "input schema")
    check(protocol["revision_kind"] == "release_adaptation", "release revision scope")
    cap = F(inputs["beta_cap_exact"])
    eps = F(protocol["epsilon_exact"])
    exposure = F(protocol["exposure_cap_exact"])
    detuning = F(protocol["frequency_error_cap_exact"])
    check(eps == F(1, 10**5), "fixed covariance radius")
    check(exposure == F(1, 10**20), "fixed positive exposure cap")
    check(detuning == F(1, 10**14), "fixed frequency tolerance")
    check(F(protocol["lag_lower_exact"]) == 1000, "fixed minimum start lag")
    check(
        list(map(F, protocol["h_interval_exact"])) == [F(9, 10), F(11, 10)],
        "fixed integrated normalized gain interval",
    )
    check(
        list(map(F, protocol["b_interval_exact"])) == [F(0), F(1)],
        "fixed integrated background interval",
    )
    check(F(protocol["eta_exact"]) == F(1, 10**5), "fixed estimator tolerance")
    check(
        F(protocol["target_individual_class_error"]) == F(1, 20),
        "fixed per-class risk target",
    )
    nominal = nominal_certificate(cap, check)
    covariance = covariance_certificate(nominal, eps, check)
    check(covariance["separated"], "covariance-family shape separation")
    averaged = exposure_certificate(nominal, covariance, exposure, check)
    frequency = frequency_certificate(averaged, nominal, covariance, detuning, check)
    counts = count_certificate(frequency, nominal, protocol, check)
    return {
        "schema_version": 1,
        "status": "PASS",
        "revision_kind": "release_adaptation",
        "parameters": {
            "beta_cap_exact": str(cap),
            "beta_band_exact": frequency["beta_band_exact"],
            "epsilon_exact": str(eps),
            "edge_weight_radius_exact": str(eps / (1 + eps)),
            "exposure_cap_exact": str(exposure),
            "frequency_error_cap_exact": str(detuning),
            "lag_lower_exact": protocol["lag_lower_exact"],
            "h_interval_exact": protocol["h_interval_exact"],
            "b_interval_exact": protocol["b_interval_exact"],
            "eta_exact": protocol["eta_exact"],
            "target_individual_class_error": protocol["target_individual_class_error"],
        },
        "stages": {
            "nominal": nominal,
            "covariance": covariance,
            "exposure": averaged,
            "frequency": frequency,
            "counts": counts,
        },
        "checks": {"count": len(checks), "passed": checks},
        "selection_disclosure": protocol["selection_disclosure"],
        "assumptions": {
            "geometry": protocol["geometry"],
            "model": protocol["model"],
            "scope": protocol["scope"],
        },
        "limitations": protocol["limits"],
        "qualification": (
            "Conditional mathematical certificate, not physical validation, "
            "independent human peer review, proof-assistant verification, "
            "a novelty proof or a practical acquisition recommendation."
        ),
    }
