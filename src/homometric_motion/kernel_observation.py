"""Per-cell nuisance propagation and losslessly factored observation evidence."""

import json
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256

from .arithmetic import rational_from_text, rational_text
from .kernel import TIME_CELLS
from .position import position_certificate
from .robustness import frequency_certificate

TERMINAL_SHAPE_GATES = {
    "frequency-robust shape separation",
    "combined position and frequency shape separation",
}
VARIABLE_CLASS_FIELDS = {
    "normalized_variance",
    "normalized_third_cumulant",
    "skewness",
    "baseline_centered_L3_upper_exact",
    "baseline_centered_L3_interpolated_exact",
    "third_cumulant_change_upper_exact",
}
VARIABLE_WRAPPER_FIELDS = {
    "classes",
    "root_certificates",
    "status",
    "signed_gap_exact",
    "gap_display_only",
}


def _fraction(value):
    return rational_from_text(value) if isinstance(value, str) else F(value)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return sha256(_canonical(value).encode()).hexdigest()


class _EvidenceTable:
    """Factor only fields proved identical; all varying witnesses stay explicit."""

    def __init__(self, check):
        self.check = check
        self.common = {}
        self.roots = []
        self._root_indices = {}

    def append(self, kind, record):
        header = {key: value for key, value in record.items() if key not in VARIABLE_WRAPPER_FIELDS}
        common_classes, varying_classes = {}, {}
        for side in ("A", "B"):
            common_classes[side] = {
                key: value
                for key, value in record["classes"][side].items()
                if key not in VARIABLE_CLASS_FIELDS
            }
            varying_classes[side] = {
                key: value
                for key, value in record["classes"][side].items()
                if key in VARIABLE_CLASS_FIELDS
            }
        common = {"header": header, "classes": common_classes}
        if kind not in self.common:
            self.common[kind] = common
        self.check(common == self.common[kind], kind + " identical factored invariants")
        ids = []
        for root in record["root_certificates"]:
            encoded = _canonical(root)
            if encoded not in self._root_indices:
                self._root_indices[encoded] = len(self.roots)
                self.roots.append(root)
            ids.append(self._root_indices[encoded])
        return {
            "classes": varying_classes,
            "root_record_indices": ids,
            "status": record["status"],
            "signed_gap_exact": record["signed_gap_exact"],
            "complete_wrapper_result_sha256": _digest(record),
        }

    def record(self):
        return {
            "format": "common-fields-and-interned-exact-roots-v1",
            "common": self.common,
            "root_records": self.roots,
        }


def restore_observation(evidence, kind, compact):
    """Restore a computed wrapper exactly; this does not authenticate a record."""
    if evidence["format"] != "common-fields-and-interned-exact-roots-v1":
        raise ValueError("unsupported observation evidence format")
    common = evidence["common"][kind]
    result = deepcopy(common["header"])
    result["classes"] = {
        side: {**deepcopy(common["classes"][side]), **deepcopy(compact["classes"][side])}
        for side in ("A", "B")
    }
    result["root_certificates"] = [
        deepcopy(evidence["root_records"][index]) for index in compact["root_record_indices"]
    ]
    result["status"] = compact["status"]
    result["signed_gap_exact"] = compact["signed_gap_exact"]
    result["gap_display_only"] = (
        float(_fraction(compact["signed_gap_exact"]))
        if compact["signed_gap_exact"] is not None
        else None
    )
    return result


def _pair_record(lower, upper):
    return {
        "lower": rational_text(lower),
        "upper": rational_text(upper),
        "decimal_display_only": [float(lower), float(upper)],
    }


def _assemble_union(records, first, check):
    check(len(records) == TIME_CELLS, "kernel complete observation domain")
    shared = {
        key: deepcopy(value) for key, value in first.items() if key not in VARIABLE_WRAPPER_FIELDS
    }
    classes = {}
    for side in ("A", "B"):
        current, witnesses = {}, {}
        for field in ("normalized_variance", "normalized_third_cumulant", "skewness"):
            lows = [_fraction(row["classes"][side][field]["lower"]) for row in records]
            highs = [_fraction(row["classes"][side][field]["upper"]) for row in records]
            lower, upper = min(lows), max(highs)
            current[field] = _pair_record(lower, upper)
            witnesses[field] = {
                "lower_cell": lows.index(lower),
                "upper_cell": highs.index(upper),
            }
        current["normalized_raw_moment_upper_bounds"] = deepcopy(
            first["classes"][side]["normalized_raw_moment_upper_bounds"]
        )
        current["extremal_time_cells"] = witnesses
        current["shape_proof"] = (
            "Union of per-time-cell perturbed skewness intervals; not recomputed "
            "from the separate global variance and third-cumulant enclosures."
        )
        check(
            _fraction(current["normalized_variance"]["lower"]) > 0,
            side + " kernel global positive observation variance",
        )
        classes[side] = current
    gap = _fraction(classes["B"]["skewness"]["lower"]) - _fraction(
        classes["A"]["skewness"]["upper"]
    )
    return {
        **shared,
        "classes": classes,
        "status": "CERTIFIED_SEPARATED" if gap > 0 else "UNRESOLVED_BY_THIS_BOUND",
        "signed_gap_exact": rational_text(gap),
        "gap_display_only": float(gap),
        "domain": "All positive exposures up to the cap, independently chosen by class",
        "time_cell_count_per_class": TIME_CELLS,
        "skewness_proof": "Class-wise union after nuisance propagation on each actual time cell",
        "global_moment_intervals_use": (
            "Separate conservative concentration inputs, not a joint rectangle used to derive skewness"
        ),
    }


def kernel_observation_certificate(kernel, nominal, covariance, parameters, check):
    """Apply fixed nuisance errors inside every cell, then union each class.

    Parameters are supplied by the versioned profile dispatcher. An internal
    call at the unresolved exact-geometry cap is supported as a negative
    control; it returns no allocation or count.
    """
    scenario = parameters["scenario"]
    check(
        scenario in ("exact_geometry", "position_uncertainty"),
        "kernel supported observation scenario",
    )
    cap = _fraction(parameters["exposure_cap_exact"])
    epsilon = _fraction(parameters["epsilon_exact"])
    detuning = _fraction(parameters["frequency_error_cap_exact"])
    rho = _fraction(parameters["position_error_cap_exact"])
    expected_frequency = F(1, 10 ** (14 if scenario == "exact_geometry" else 16))
    expected_position = F(0) if scenario == "exact_geometry" else F(1, 10**14)
    check(
        detuning == expected_frequency and rho == expected_position,
        "kernel declared frequency and position scenario",
    )
    check(
        cap == _fraction(kernel["exposure_cap_exact"])
        and epsilon == _fraction(covariance["epsilon_exact"])
        and epsilon == _fraction(kernel["epsilon_exact"]),
        "kernel observation family agrees",
    )
    check(
        kernel["beta_cap_exact"] == nominal["beta_cap_exact"],
        "kernel observation strength cap agrees",
    )
    check(kernel["status"] == "SEPARATED_BY_THIS_BOUND", "kernel baseline separates")
    check(kernel["time_cells_per_class"] == TIME_CELLS, "kernel fixed full time cover")
    for side in ("A", "B"):
        check(
            len(kernel["classes"][side]["cells"]) == TIME_CELLS,
            side + " kernel upstream complete cells",
        )
    table = _EvidenceTable(check)
    cells, frequency_records, observation_records, deferred = [], [], [], []
    first_frequency = first_observation = None
    for j in range(TIME_CELLS):
        local_classes = {}
        expected_time = [cap * j / TIME_CELLS, cap * (j + 1) / TIME_CELLS]
        for side in ("A", "B"):
            original = kernel["classes"][side]["cells"][j]
            check(original["status"] == "ENCLOSED", side + " kernel upstream cell enclosed")
            check(
                list(map(_fraction, original["time_interval"])) == expected_time,
                side + " kernel exact local time interval",
            )
            trace = _fraction(nominal["classes"][side]["trace_Lplus_exact"])
            local_classes[side] = {
                "normalized_variance": original["variance"],
                "normalized_third_cumulant": original["third"],
                "skewness": original["skewness"],
                "normalized_raw_moment_upper_bounds": covariance["classes"][side][
                    "normalized_raw_moment_upper_bounds"
                ],
                "trace_upper_exact": rational_text(63 * (1 + epsilon)),
                "increment_trace_slope_upper_exact": rational_text(F(2 * 63 * 62) / trace),
            }
        joint = {
            "beta_cap_exact": nominal["beta_cap_exact"],
            "epsilon_exact": covariance["epsilon_exact"],
            "edge_weight_radius_exact": rational_text(epsilon / (1 + epsilon)),
            "exposure_cap_exact": rational_text(cap),
            "actual_time_interval_exact": list(map(rational_text, expected_time)),
            "classes": local_classes,
        }
        gates = []

        def local_check(ok, label):
            if not ok and label in TERMINAL_SHAPE_GATES:
                gates.append(label)
                return
            check(ok, label)

        frequency = frequency_certificate(joint, nominal, covariance, detuning, local_check)
        if first_frequency is None:
            first_frequency = frequency
        compact_frequency = table.append("frequency", frequency)
        frequency_records.append(frequency)
        local = {
            "index": j,
            "time_interval_exact": joint["actual_time_interval_exact"],
            "frequency": compact_frequency,
            "deferred_terminal_gates": gates,
        }
        observation = frequency
        if scenario == "position_uncertainty":
            if frequency["status"] != "CERTIFIED_SEPARATED":
                local["status"] = "UNRESOLVED_FREQUENCY_BASELINE"
                cells.append(local)
                deferred.append({"cell": j, "gates": list(gates)})
                continue
            if j in (0, TIME_CELLS // 2, TIME_CELLS - 1):
                position_certificate(joint, nominal, frequency, F(0), check)
            observation = position_certificate(joint, nominal, frequency, rho, local_check)
            if "combined position and frequency shape separation" in gates:
                observation = {**observation, "status": "UNRESOLVED_BY_THIS_BOUND"}
            local["position"] = table.append("position", observation)
        if first_observation is None:
            first_observation = observation
        observation_records.append(observation)
        local["status"] = observation["status"]
        cells.append(local)
        if gates:
            deferred.append({"cell": j, "gates": list(gates)})
    evidence = table.record()
    # A lossless round trip checks every factorization, including repeated roots.
    for cell in cells:
        for kind in ("frequency", "position"):
            if kind in cell:
                restored = restore_observation(evidence, kind, cell[kind])
                check(
                    _digest(restored) == cell[kind]["complete_wrapper_result_sha256"],
                    kind + " lossless observation evidence",
                )
    result = {
        "scenario": scenario,
        "exposure_cap_exact": rational_text(cap),
        "time_cells": cells,
        "evidence": evidence,
        "deferred_terminal_gates": deferred,
        "frequency_union": _assemble_union(frequency_records, first_frequency, check),
    }
    if len(observation_records) != TIME_CELLS:
        return {
            **result,
            "status": "UNRESOLVED_BY_THIS_BOUND",
            "gate": "incomplete positive-position domain",
        }
    union = _assemble_union(observation_records, first_observation, check)
    result["observation_union"] = union
    if union["status"] != "CERTIFIED_SEPARATED":
        return {
            **result,
            "status": "UNRESOLVED_BY_THIS_BOUND",
            "gate": "global independent-exposure skewness union",
        }
    check(not deferred, "kernel no deferred local failure in complete positive domain")
    return {**result, "status": "CERTIFIED_SEPARATED"}
