"""A separate linear-exposure theorem and freshly recomputed count chain.

The public builder accepts only a named scenario. Saved-record validation is
conditional on the recorded core claims and never authenticates those claims.
"""

from copy import deepcopy
from fractions import Fraction as F

from .arithmetic import Interval as I
from .certificate import SCENARIOS, CertificateError, build_certificate
from .coordinate import _derive_counts, core_digest
from .counts import count_certificate
from .geometry import exact_covariance
from .position import position_certificate
from .robustness import frequency_certificate, interval

KIND = "linear_exposure_count_extension"
EXPOSURE_CAP = F(1, 100000)
DISCLOSURE = (
    "The exposure cap was selected after an exploratory declared-grid analysis "
    "of a linear-in-time moment bound, then checked with the full nuisance and "
    "count proofs. The coordinate allocation is an exact feasible witness. "
    "No blind selection, optimality, necessary count or practical acquisition "
    "claim is made."
)
QUALIFICATION = (
    "A new conditional finite-window certificate under the extension's own "
    "fixed acquisition settings and classifier. The embedded core is a reference calculation, "
    "not the selected exposure/count chain. No physical validation, independent "
    "human peer review or full-theorem proof-assistant verification is claimed."
)


def linear_exposure_certificate(nominal, covariance, exposure, check):
    """Bound averaged moments by O(T) kernel losses and uniform parity errors.

    Zero exposure is supported only as a limiting regression control. This
    function consumes mathematical records; only the public builder below
    obtains them by freshly recomputing the full core.
    """
    exposure = F(exposure)
    eps = F(covariance["epsilon_exact"])
    check(exposure >= 0 and 0 <= eps < 1, "linear exposure parameter domain")
    omega = interval(nominal["omega"])
    beta = I(F(nominal["beta_cap_exact"]))
    classes, constants = {}, {}
    for side in ("A", "B"):
        base = nominal["classes"][side]
        marginal = covariance["classes"][side]
        matrix, trace = exact_covariance(side, check)
        check(str(trace) == base["trace_Lplus_exact"], side + " linear exact trace")
        q, p2 = interval(marginal["q_enclosure"]), interval(marginal["abs_p_squared_enclosure"])
        energy = {
            k: I(F(base["energy_raw_moments_exact"][str(k)])) * (1 + eps) ** k for k in (4, 6)
        }
        diagonal = sum(I(matrix[i][i]) * I(matrix[i][i]).root(2) for i in range(63))
        diagonal = diagonal * (I(1 + eps) ** 3).root(2)
        v0 = omega**4 * (q**2 + p2)
        k30 = omega**6 * (2 * q**3 + 6 * q * p2)
        m4c = omega**8 * (9 * q**4 + 42 * q**2 * p2 + 9 * p2**2)
        s4 = omega * (2 * q**2 + p2).root(4)
        s6 = omega * (6 * q**3 + 9 * q * p2).root(6)
        c4, c6 = omega**2 * energy[4].root(4) / 2, omega**2 * energy[6].root(6) / 2
        e4 = omega**3 * I(10395).root(4) * diagonal / 6
        e6 = omega**3 * I(34459425).root(6) * diagonal / 6
        even2 = beta * (2 * s4 * e4 + c4**2) + beta**2 * e4**2
        odd2 = 4 * beta * c4**2 * (s4 + beta * e4) ** 2
        sd0 = v0.root(2)
        check(sd0.lower > even2.upper, side + " linear positive marginal variance")
        marginal_variance = I.bounds(
            (sd0.lower - even2.upper) ** 2, ((sd0 + even2) ** 2 + odd2).upper
        )
        even3 = 2 * beta * (2 * s6 * e6 + c6**2) + 2 * beta**2 * e6**2
        odd3 = 4 * beta * c6**2 * (s6 + beta * e6) ** 2
        x3 = (v0 * m4c).root(6)
        err3 = 3 * x3**2 * even3 + 3 * x3 * even3**2 + even3**3 + 3 * (x3 + even3) * odd3
        marginal_third = I.bounds(k30.lower - err3.upper, k30.upper + err3.upper)
        check(
            marginal_variance.record() == marginal["normalized_variance"],
            side + " linear reconstruct marginal variance",
        )
        check(
            marginal_third.record() == marginal["normalized_third_cumulant"],
            side + " linear reconstruct marginal third",
        )
        check(
            str(err3.upper) == marginal["third_cumulant_error_upper"],
            side + " linear reconstruct parity error",
        )
        q_intensity = omega**2 * q
        g = I(F(63) / trace) * 63 * omega**2
        rate2 = F(4, 3) * q_intensity.upper * g.upper
        rate3 = 8 * q_intensity.upper**2 * g.upper
        loss2, loss3 = exposure * rate2, exposure * rate3
        leading_lower = max(F(0), v0.lower - loss2)
        lower = max(F(0), I(leading_lower).root(2).lower - even2.upper) ** 2
        variance = I.bounds(lower, marginal_variance.upper)
        third = I.bounds(marginal_third.lower - loss3, marginal_third.upper + loss3)
        check(variance.lower > 0, side + " linear positive exposure variance")
        skew = third / (variance * variance.root(2))
        classes[side] = {
            "normalized_variance": variance.record(),
            "normalized_third_cumulant": third.record(),
            "skewness": skew.record(),
            "normalized_raw_moment_upper_bounds": deepcopy(
                marginal["normalized_raw_moment_upper_bounds"]
            ),
            "trace_upper_exact": str(63 * (1 + eps)),
            "increment_trace_slope_upper_exact": str(F(2 * 63 * 62) / trace),
            "leading_variance_loss_upper_exact": str(loss2),
            "leading_third_error_upper_exact": str(loss3),
        }
        constants[side] = {
            "q_intensity": q_intensity.record(),
            "kernel_trace_rate": g.record(),
            "leading_variance": v0.record(),
            "leading_third_cumulant": k30.record(),
            "even_L2_upper_exact": str(even2.upper),
            "centered_even_L3_upper_exact": str(even3.upper),
            "odd_L3_squared_upper_exact": str(odd3.upper),
            "centered_leading_L3_upper_exact": str(x3.upper),
            "finite_motion_third_error_upper_exact": str(err3.upper),
            "leading_variance_loss_rate_upper_exact": str(rate2),
            "leading_third_error_rate_upper_exact": str(rate3),
        }
        if not exposure:
            for name in ("normalized_variance", "normalized_third_cumulant", "skewness"):
                check(classes[side][name] == marginal[name], side + " linear zero recovery " + name)
    gap = F(classes["B"]["skewness"]["lower"]) - F(classes["A"]["skewness"]["upper"])
    check(gap > 0, "linear exposure skewness separation")
    return {
        "beta_cap_exact": nominal["beta_cap_exact"],
        "epsilon_exact": str(eps),
        "edge_weight_radius_exact": str(eps / (1 + eps)),
        "exposure_cap_exact": str(exposure),
        "classes": classes,
        "constants": constants,
        "separated": True,
        "gap_lower_exact": str(gap),
        "scope": (
            "Uniform finite-motion averaged moments for exact nominal phases, "
            "fixed positive springs and compatible stationary weighted OU."
        ),
    }


def _derive_extension(core):
    """Derive extension arithmetic conditional on a supplied core record."""
    labels = []

    def check(ok, label):
        if not ok:
            raise CertificateError(label)
        labels.append(label)

    scenario = core["scenario"]
    check(scenario in SCENARIOS and core["status"] == "PASS", "supported exposure reference")
    check("certificate_kind" not in core, "ordinary exposure reference core")
    params = deepcopy(core["parameters"])
    expected_frequency = F(1, 10 ** (14 if scenario == "exact_geometry" else 16))
    expected_position = F(0) if scenario == "exact_geometry" else F(1, 10**14)
    for key, value in {
        "exposure_cap_exact": F(1, 10**20),
        "epsilon_exact": F(1, 100000),
        "frequency_error_cap_exact": expected_frequency,
        "position_error_cap_exact": expected_position,
        "lag_lower_exact": F(1000),
        "eta_exact": F(1, 100000),
        "target_individual_class_error": F(1, 20),
    }.items():
        check(F(params[key]) == value, "fixed exposure reference " + key)
    check(list(map(F, params["h_interval_exact"])) == [F(9, 10), F(11, 10)], "fixed exposure gain")
    check(list(map(F, params["b_interval_exact"])) == [F(0), F(1)], "fixed exposure background")
    params["exposure_cap_exact"] = str(EXPOSURE_CAP)
    nominal, covariance = core["stages"]["nominal"], core["stages"]["covariance"]
    averaged = linear_exposure_certificate(nominal, covariance, EXPOSURE_CAP, check)
    frequency = frequency_certificate(averaged, nominal, covariance, expected_frequency, check)
    stages = {
        "nominal": nominal,
        "covariance": covariance,
        "linear_exposure": averaged,
        "frequency": frequency,
    }
    observation = frequency
    if scenario == "position_uncertainty":
        position_certificate(averaged, nominal, frequency, F(0), check)
        observation = position_certificate(averaged, nominal, frequency, expected_position, check)
        stages["position"] = observation
    stages["counts"] = count_certificate(
        observation,
        nominal,
        {**params, "scenario": scenario, "selection_disclosure": DISCLOSURE},
        check,
    )
    extension = {
        "schema_version": 1,
        "status": "PASS",
        "scenario": scenario,
        "parameters": params,
        "stages": stages,
        "checks": {"count": len(labels), "passed": list(labels)},
        "qualification": QUALIFICATION,
    }
    coordinate = _derive_counts(extension, check)
    coordinate["comparison_baseline"] = "extension.stages.counts"
    coordinate["parameters_shared_with_common_count"] = coordinate.pop("parameters_unchanged")
    coordinate["classifier"].pop("unchanged")
    coordinate["classifier"]["unchanged_relative_to"] = "extension.stages.counts"
    return extension, coordinate, {"count": len(labels), "passed": labels}


def build_exposure_certificate(scenario="exact_geometry"):
    """Freshly recompute the reference core and the separate exposure chain."""
    core = build_certificate(scenario=scenario)
    before = core_digest(core)
    extension, coordinate, checks = _derive_extension(core)
    if core_digest(core) != before:
        raise CertificateError("exposure derivation mutated the reference core")
    return {
        "schema_version": 1,
        "certificate_kind": KIND,
        "revision_kind": "release_adaptation",
        "status": "PASS",
        "scenario": scenario,
        "core_certificate": core,
        "core_certificate_sha256": before,
        "core_digest_encoding": "UTF-8 canonical JSON: sorted keys, compact separators, no NaN",
        "extension": extension,
        "coordinate_counts": coordinate,
        "checks": checks,
        "selection_disclosure": DISCLOSURE,
        "qualification": QUALIFICATION,
    }


def validate_saved_exposure(envelope):
    """Check recorded scope and witness; do not authenticate or rebuild motion."""
    if (
        envelope.get("schema_version") != 1
        or envelope.get("certificate_kind") != KIND
        or envelope.get("revision_kind") != "release_adaptation"
        or envelope.get("status") != "PASS"
    ):
        raise ValueError("unsupported linear exposure extension")
    core = envelope["core_certificate"]
    if not isinstance(core, dict) or "certificate_kind" in core:
        raise ValueError("exposure extension requires an ordinary core certificate")
    if envelope["scenario"] != core["scenario"]:
        raise ValueError("exposure/reference scenario mismatch")
    if envelope["core_certificate_sha256"] != core_digest(core):
        raise ValueError("recorded exposure reference content digest mismatch")
    extension, coordinate, checks = _derive_extension(core)
    if envelope["extension"] != extension:
        raise ValueError("recorded exposure chain differs from its exact construction")
    if envelope["coordinate_counts"] != coordinate or envelope["checks"] != checks:
        raise ValueError("recorded exposure coordinate witness differs from its exact construction")
    return coordinate
