"""A separate exact feasible coordinate-tolerance count extension.

Only build_coordinate_certificate is a fresh full-model calculation. Internal
arithmetic on a supplied core record is conditional on that record's claims.
"""

import hashlib
import json
from fractions import Fraction as F
from math import comb, factorial

from .arithmetic import ceiling_fraction as ceil
from .arithmetic import integer_root
from .arithmetic import rational_from_text as Q
from .arithmetic import rational_text as text
from .certificate import SCENARIOS, CertificateError, build_certificate
from .counts import classify

KIND = "coordinate_count_extension"
DISCLOSURE = (
    "This release adaptation uses known core bounds. A linear-relaxation-guided "
    "direction and exact feasibility bisection construct a rational witness. "
    "No blind selection, global optimality, required count, or practical "
    "acquisition claim is made."
)


def record(value):
    return {"exact": text(value), "display_only": float(value)}


def root_lower(value, degree, places, check):
    scale = 10**places
    k = integer_root(value.numerator * scale**degree // value.denominator, degree)
    lower = F(k, scale)
    check(lower**degree <= value < (lower + F(1, scale)) ** degree, "exact root enclosure")
    return lower


def core_digest(core):
    """Hash canonical JSON content, not a file or proof of authenticity."""
    encoded = json.dumps(core, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _counts_and_checks(core):
    passed = []

    def check(condition, label):
        if not condition:
            raise CertificateError(label)
        passed.append(label)

    counts = _derive_counts(core, check)
    return counts, {"count": len(passed), "passed": passed}


def build_coordinate_certificate(scenario="exact_geometry"):
    """Freshly recompute the full core and a separate coordinate count proof.

    This API accepts only a named scenario, never a saved certificate. Source
    manifest verification is performed separately by the installed CLI.
    """
    core = build_certificate(scenario=scenario)
    counts, checks = _counts_and_checks(core)
    return {
        "schema_version": 1,
        "certificate_kind": KIND,
        "revision_kind": "release_adaptation",
        "status": "PASS",
        "scenario": scenario,
        "core_certificate": core,
        "core_certificate_sha256": core_digest(core),
        "core_digest_encoding": "UTF-8 canonical JSON: sorted keys, compact separators, no NaN",
        "coordinate_counts": counts,
        "checks": checks,
        "selection_disclosure": DISCLOSURE,
        "qualification": (
            "Conditional finite-window sufficient count with the same model, "
            "classifier and risk target as the embedded core. No physical "
            "validation, human peer review, full-theorem formal verification, "
            "optimality or practical feasibility is claimed."
        ),
    }


def validate_saved_extension(envelope):
    """Check recorded arithmetic; does not authenticate or rebuild core motion.

    The CLI also applies its fixed core-contract checks before displaying this
    object. A saved file remains an unverified claim after these checks.
    """
    if (
        envelope.get("schema_version") != 1
        or envelope.get("certificate_kind") != KIND
        or envelope.get("revision_kind") != "release_adaptation"
        or envelope.get("status") != "PASS"
    ):
        raise ValueError("unsupported coordinate extension")
    core = envelope["core_certificate"]
    if not isinstance(core, dict) or "certificate_kind" in core:
        raise ValueError("coordinate extension requires an ordinary core certificate")
    if envelope["scenario"] != core["scenario"]:
        raise ValueError("coordinate/core scenario mismatch")
    if envelope["core_certificate_sha256"] != core_digest(core):
        raise ValueError("recorded core content digest mismatch")
    expected, checks = _counts_and_checks(core)
    if envelope["coordinate_counts"] != expected or envelope["checks"] != checks:
        raise ValueError("recorded coordinate witness differs from its exact construction")
    return expected


def _derive_counts(certificate, check):
    scenario = certificate["scenario"]
    check(scenario in SCENARIOS, "supported coordinate scenario")
    check(certificate["status"] == "PASS", scenario + " core status")
    old = certificate["stages"]["counts"]
    observation = certificate["stages"][
        "position" if scenario == "position_uncertainty" else "frequency"
    ]
    params = certificate["parameters"]
    eta, target = Q(old["eta_exact"]), Q(params["target_individual_class_error"])
    check(eta == F(1, 100000), scenario + " retained eta")
    check(target == F(1, 20), scenario + " retained risk")
    hlow, hhigh = map(Q, old["h_interval_exact"])
    blow, bhigh = map(Q, old["b_interval_exact"])
    check(
        (hlow, hhigh, blow, bhigh) == (F(9, 10), F(11, 10), F(0), F(1)), scenario + " channel box"
    )
    raw = {0: F(1)} | {
        j: max(
            Q(observation["classes"][side]["normalized_raw_moment_upper_bounds"][str(j)])
            for side in ("A", "B")
        )
        for j in range(1, 7)
    }
    fm = {
        j: sum(comb(j, k) * hhigh**k * bhigh ** (j - k) * raw[k] for k in range(j + 1))
        for j in range(1, 7)
    }
    seconds = {
        j: sum(comb(j, r) ** 2 * factorial(r) * fm[2 * j - r] for r in range(j + 1))
        for j in range(1, 4)
    }
    for j in range(1, 7):
        check(
            fm[j] == Q(old["factorial_moment_upper_exact"][str(j)]),
            scenario + f" reconstructed F{j}",
        )
    for j in range(1, 4):
        check(
            seconds[j] == Q(old["raw_factorial_second_moment_upper_exact"][str(j)]) > 0,
            scenario + f" reconstructed S{j}{j}",
        )
    amin = hlow**2 * min(
        Q(observation["classes"][side]["normalized_variance"]["lower"]) for side in ("A", "B")
    )
    check(
        amin == Q(old["factorial_variance_lower_exact"]) > 0,
        scenario + " positive variance lower bound",
    )
    root = root_lower(amin, 2, 80 if scenario == "position_uncertainty" else 60, check)
    budget2, budget3 = eta * amin, eta * amin * root
    linear = {1: 3 * fm[2] + 6 * fm[1] ** 2, 2: 3 * fm[1], 3: F(1)}
    direction = {j: root_lower(seconds[j] / linear[j], 3, 24, check) for j in range(1, 4)}
    check(all(x > 0 for x in direction.values()), scenario + " positive coordinate direction")

    def errors(scale):
        t1, t2, t3 = (scale * direction[j] for j in range(1, 4))
        return (
            t2 + 2 * fm[1] * t1 + t1**2,
            t3
            + 3 * fm[1] * t2
            + (3 * fm[2] + 6 * fm[1] ** 2) * t1
            + 3 * t1 * t2
            + 6 * fm[1] * t1**2
            + 2 * t1**3,
        )

    def feasible(scale):
        error2, error3 = errors(scale)
        return error2 <= budget2 and error3 <= budget3

    initial_high = min(
        budget2 / (direction[2] + 2 * fm[1] * direction[1]),
        budget3 / sum(linear[j] * direction[j] for j in range(1, 4)),
    )
    lower, upper = F(0), initial_high
    check(
        initial_high > 0 and feasible(lower) and not feasible(upper),
        scenario + " initial feasibility bracket",
    )
    for _ in range(128):
        middle = (lower + upper) / 2
        if feasible(middle):
            lower = middle
        else:
            upper = middle
    check(
        0 < lower < upper and feasible(lower) and not feasible(upper),
        scenario + " final feasibility bracket",
    )
    check(upper - lower == initial_high / 2**128, scenario + " exact bisection width")
    tolerances = {j: lower * direction[j] for j in range(1, 4)}
    error2, error3 = errors(lower)
    check(
        0 < error2 <= budget2 and 0 < error3 <= budget3,
        scenario + " complete polynomial constraints",
    )
    check(error3**2 <= eta**2 * amin**3, scenario + " third relative error")
    H = Q(old["window_variance_inflation_upper_exact"])
    eps = Q(old["epsilon_exact"])
    trace = max(
        Q(certificate["stages"]["nominal"]["classes"][side]["trace_Lplus_exact"])
        for side in ("A", "B")
    )
    gamma = (1 - eps / (1 + eps)) / trace
    check(
        H == 1 + 2 / (gamma * (Q(old["lag_lower_exact"]) - Q(old["exposure_cap_exact"]))),
        scenario + " original dependence bound",
    )
    contributions = {j: H * seconds[j] / tolerances[j] ** 2 for j in range(1, 4)}
    numerator = sum(contributions.values())
    unrounded = numerator / target
    N = ceil(unrounded)
    check(N - 1 < unrounded <= N, scenario + " exact count ceiling")
    risks = {j: contributions[j] / N for j in range(1, 4)}
    total_risk = sum(risks.values())
    check(total_risk == numerator / N <= target, scenario + " union risk budget")
    check(
        N < old["sufficient_observation_windows"], scenario + " strictly improved sufficient bound"
    )
    tau = Q(old["raw_moment_tolerance_exact"])
    old_raw = H * sum(seconds.values()) / (target * tau**2)
    check(
        ceil(old_raw) == old["sufficient_observation_windows"],
        scenario + " old count independently reconstructed",
    )
    threshold = Q(old["threshold_exact"])
    expanded = {
        side: list(map(Q, old["expanded_shape_intervals_exact"][side])) for side in ("A", "B")
    }
    check(
        0 < expanded["A"][0] <= expanded["A"][1] < threshold < expanded["B"][0] <= expanded["B"][1],
        scenario + " retained class threshold",
    )
    endpoint_checks = {}
    for side in ("A", "B"):
        rlo, rhi = (Q(observation["classes"][side]["skewness"][end]) for end in ("lower", "upper"))
        elo, ehi = expanded[side]
        check(eta < rlo <= rhi, scenario + side + " positive numerator on good event")
        check(
            elo > 0 and elo**2 * (1 + eta) ** 3 <= (rlo - eta) ** 2,
            scenario + side + " lower expanded endpoint",
        )
        check(
            ehi**2 * (1 - eta) ** 3 >= (rhi + eta) ** 2,
            scenario + side + " upper expanded endpoint",
        )
        shape = (elo + ehi) / 2
        check(
            classify(F(1), F(2), shape + 4, threshold) == side,
            scenario + side + " exact classifier control",
        )
        endpoint_checks[side] = {
            "original": [text(rlo), text(rhi)],
            "expanded": [text(elo), text(ehi)],
        }
    check(classify(F(1), F(1), F(1), threshold) == "A", scenario + " nonpositive variance fallback")
    check(classify(F(1), F(2), F(0), threshold) == "A", scenario + " negative third fallback")
    return {
        "scenario": scenario,
        "status": "PASS",
        "parameters_unchanged": params,
        "sufficient_observation_windows": N,
        "previous_sufficient_observation_windows": old["sufficient_observation_windows"],
        "previous_over_new_count_ratio": record(F(old["sufficient_observation_windows"], N)),
        "new_unrounded_count": record(unrounded),
        "new_total_individual_class_error_upper": record(total_risk),
        "coordinate_individual_error_upper": {str(j): record(risks[j]) for j in range(1, 4)},
        "raw_mean_tolerances": {str(j): record(tolerances[j]) for j in range(1, 4)},
        "new_over_old_common_tolerance": {str(j): record(tolerances[j] / tau) for j in range(1, 4)},
        "direction": {str(j): record(direction[j]) for j in range(1, 4)},
        "direction_radicands": {str(j): record(seconds[j] / linear[j]) for j in range(1, 4)},
        "direction_root_places": 24,
        "scale_bracket": {
            "initial_upper": record(initial_high),
            "feasible_lower": record(lower),
            "infeasible_upper": record(upper),
            "iterations": 128,
        },
        "polynomial_error_bounds": {"variance": record(error2), "third_cumulant": record(error3)},
        "polynomial_error_budgets": {
            "variance": record(budget2),
            "third_cumulant": record(budget3),
        },
        "fraction_of_error_budget_used": {
            "variance": record(error2 / budget2),
            "third_cumulant": record(error3 / budget3),
        },
        "inputs": {
            "factorial_moments": {str(j): record(fm[j]) for j in range(1, 7)},
            "coordinate_second_moments": {str(j): record(seconds[j]) for j in range(1, 4)},
            "linear_third_sensitivity": {str(j): record(linear[j]) for j in range(1, 4)},
            "variance_lower": record(amin),
            "sqrt_variance_lower": record(root),
            "eta": text(eta),
            "H": record(H),
            "target": text(target),
        },
        "classifier": {
            "threshold": text(threshold),
            "shape_endpoints": endpoint_checks,
            "unchanged": True,
        },
        "scope": "Uniform finite-window sufficient count under the retained scenario's conditional assumptions; not a necessary or practical acquisition cost.",
    }
