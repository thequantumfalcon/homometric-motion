"""Recompute the public scenario and map selected rational claims to Lean."""

import argparse
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path

from homometric_motion import build_certificate
from homometric_motion.arithmetic import rational_from_text, rational_text
from homometric_motion.cli import verify_source_manifest


def statements(certificate):
    """Return closed statements with their exact public certificate field mapping."""
    if certificate["scenario"] != "position_uncertainty":
        raise ValueError("position_uncertainty certificate required")
    position = certificate["stages"]["position"]
    counts = certificate["stages"]["counts"]
    rows = []

    def add(name, expression, fields, meaning):
        rows.append(
            {"theorem": name, "expression": expression, "input_fields": fields, "meaning": meaning}
        )

    def strict(name, left, right, fields, meaning):
        x, y = rational_from_text(left), rational_from_text(right)
        if not 0 <= x < y:
            raise ValueError("nonnegative strict comparison failed")
        expression = (
            f"({rational_text(x.numerator)} : Nat) * {rational_text(y.denominator)} < "
            f"({rational_text(y.numerator)} : Nat) * {rational_text(x.denominator)}"
        )
        add(name, expression, fields, meaning)

    strict(
        "selected_position_shape_gap",
        position["classes"]["A"]["skewness"]["upper"],
        position["classes"]["B"]["skewness"]["lower"],
        ["stages.position.classes.A.skewness.upper", "stages.position.classes.B.skewness.lower"],
        "The class A upper skewness bound is below the class B lower bound.",
    )
    strict(
        "expanded_count_rule_gap",
        counts["expanded_shape_intervals_exact"]["A"][1],
        counts["expanded_shape_intervals_exact"]["B"][0],
        [
            "stages.counts.expanded_shape_intervals_exact.A[1]",
            "stages.counts.expanded_shape_intervals_exact.B[0]",
        ],
        "The intervals enlarged for estimator error are disjoint.",
    )
    budget = rational_from_text(counts["unrounded_window_budget_exact"])
    windows = counts["sufficient_observation_windows"]
    if type(windows) is not int or not windows - 1 < budget <= windows:
        raise ValueError("exact sufficient-count ceiling failed")
    numerator, denominator = rational_text(budget.numerator), rational_text(budget.denominator)
    fields = [
        "stages.counts.sufficient_observation_windows",
        "stages.counts.unrounded_window_budget_exact",
    ]
    add(
        "ceiling_lower",
        f"({windows - 1} : Nat) * {denominator} < {numerator}",
        fields,
        "The integer immediately below the recorded count is below the rational budget.",
    )
    add(
        "ceiling_upper",
        f"({numerator} : Nat) <= ({windows} : Nat) * {denominator}",
        fields,
        "The rational budget does not exceed the recorded sufficient integer count.",
    )
    risk = rational_from_text(counts["individual_class_error_upper_exact"])
    if not 0 <= risk <= F(1, 20):
        raise ValueError("risk checkpoint failed")
    add(
        "recorded_individual_error_at_most_one_twentieth",
        f"(20 : Nat) * {rational_text(risk.numerator)} <= {rational_text(risk.denominator)}",
        ["stages.counts.individual_class_error_upper_exact"],
        "The recorded exact individual-class risk upper bound is at most one twentieth.",
    )
    rho = F(position["position_error_cap_exact"])
    margin = position["nominal_mean_contact_margin_strict_lower_exact"]
    strict(
        "positive_position_contact_margin",
        str(2 * rho),
        margin,
        [
            "stages.position.position_error_cap_exact (multiplied by two)",
            "stages.position.nominal_mean_contact_margin_strict_lower_exact",
        ],
        "Twice the fixed position-error cap is smaller than the nominal contact margin.",
    )
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True, help="new directory only")
    args = parser.parse_args()
    if args.output_dir.exists():
        raise FileExistsError("output directory exists; choose a new one")
    supplied = json.loads(args.certificate.read_text(encoding="utf-8"))
    provenance = verify_source_manifest()
    fresh = build_certificate(scenario="position_uncertainty")
    fresh["source_revision"] = provenance
    if supplied != fresh:
        raise ValueError("supplied certificate differs from fresh installed-package recomputation")
    rows = statements(fresh)
    source = (
        "/- Finite exact arithmetic only; analytic and probabilistic proofs are not formalized. -/\n"
        "import Init\n\n"
        "set_option maxRecDepth 100000\n"
        "set_option maxHeartbeats 5000000\n\n"
        "namespace CertificateCheckpoint\n\n"
        + "\n".join(
            f"theorem {r['theorem']} : {r['expression']} := by\n  decide +kernel\n" for r in rows
        )
        + "\n"
        + "\n".join("#print axioms " + row["theorem"] for row in rows)
        + "\n\nend CertificateCheckpoint\n"
    )
    mapping = {
        "schema_version": 1,
        "scenario": "position_uncertainty",
        "revision_kind": "release_adaptation",
        "source_manifest_sha256": provenance["manifest_sha256"],
        "certificate_sha256": hashlib.sha256(args.certificate.read_bytes()).hexdigest(),
        "lean_source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "lean_version": "4.35.0",
        "proof_method": "Init, closed natural-number inequalities, decide +kernel",
        "theorems": rows,
        "scope": (
            "Input mapping is checked by a fresh public-package recomputation. "
            "Lean checks only the six resulting arithmetic statements; no Gaussian, "
            "OU, moment-bound, probability or physical-model theorem is formalized."
        ),
    }
    args.output_dir.mkdir(parents=True)
    for name, text in (
        ("CertificateCheckpoint.lean", source),
        ("statement_mapping.json", json.dumps(mapping, indent=2, sort_keys=True) + "\n"),
    ):
        with (args.output_dir / name).open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
    print("Wrote six mapped arithmetic statements; execute Lean separately.")


if __name__ == "__main__":
    main()
