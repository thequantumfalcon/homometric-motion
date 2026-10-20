"""Run and inspect the installed mathematical certificate."""

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from importlib.resources import files
from pathlib import Path

from . import __version__
from .arithmetic import rational_from_text
from .certificate import SCENARIOS, build_certificate
from .coordinate import KIND, build_coordinate_certificate, validate_saved_extension
from .exposure import KIND as EXPOSURE_KIND
from .exposure import build_exposure_certificate, validate_saved_exposure
from .profiles import KIND as PROFILE_KIND
from .profiles import PROFILES, build_count_certificate, validate_saved_count

MANIFEST_FILES = {
    "__init__.py",
    "__main__.py",
    "arithmetic.py",
    "allocation.py",
    "certificate.py",
    "cli.py",
    "counts.py",
    "coordinate.py",
    "exposure.py",
    "geometry.py",
    "kernel.py",
    "kernel_arithmetic.py",
    "kernel_observation.py",
    "motion.py",
    "position.py",
    "profiles.py",
    "robustness.py",
    "inputs.json",
    "protocol.json",
}


def verify_source_manifest() -> dict:
    """Verify the exact relative allowlist embedded in the installed package."""
    package = files("homometric_motion")
    raw = package.joinpath("source_manifest.json").read_bytes()
    manifest = json.loads(raw)
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported source manifest schema")
    if manifest.get("revision_kind") != "release_adaptation":
        raise ValueError("source manifest must identify a new release adaptation")
    records = manifest.get("files", [])
    paths = [record.get("path") for record in records]
    if len(paths) != len(MANIFEST_FILES) or set(paths) != MANIFEST_FILES:
        raise ValueError("source manifest does not match the package allowlist")
    bindings = {}
    for record in records:
        name = record["path"]
        digest = hashlib.sha256(package.joinpath(name).read_bytes()).hexdigest()
        if digest != record.get("sha256"):
            raise ValueError(f"source digest mismatch: {name}")
        bindings[name] = digest
    return {
        "schema_version": 1,
        "revision_kind": "release_adaptation",
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "bindings": bindings,
    }


def summary(certificate: dict, *, verified: bool = False) -> str:
    """Display the fixed contract; saved records are explicitly unverified.

    ``verified=True`` is reserved for the freshly recomputed CLI result. These
    consistency checks do not authenticate an arbitrary supplied JSON record.
    """
    if not isinstance(certificate, dict):
        raise ValueError("certificate must be a JSON object")
    if "certificate_kind" in certificate:
        if certificate["certificate_kind"] == PROFILE_KIND:
            return profile_summary(certificate, verified=verified)
        if certificate["certificate_kind"] == EXPOSURE_KIND:
            return exposure_summary(certificate, verified=verified)
        if certificate["certificate_kind"] != KIND:
            raise ValueError("unsupported saved certificate kind")
        return extension_summary(certificate, verified=verified)
    if certificate.get("schema_version") != 1 or certificate.get("status") != "PASS":
        raise ValueError("unsupported or unsuccessful certificate")
    scenario = certificate["scenario"]
    if scenario not in SCENARIOS:
        raise ValueError("unsupported saved certificate scenario")
    frequency = certificate["stages"]["frequency"]
    position = scenario == "position_uncertainty"
    selected = certificate["stages"]["position"] if position else frequency
    counts = certificate["stages"]["counts"]
    parameters = certificate["parameters"]
    windows = counts["sufficient_observation_windows"]
    gap = rational_from_text(selected["signed_gap_exact"])
    if type(windows) is not int or windows <= 0 or gap <= 0:
        raise ValueError("invalid certificate summary fields")
    budget = rational_from_text(counts["unrounded_window_budget_exact"])
    risk = rational_from_text(counts["individual_class_error_upper_exact"])
    if not windows - 1 < budget <= windows:
        raise ValueError("saved observation count is not its recorded exact ceiling")
    if risk != budget / (20 * windows) or not 0 < risk <= Fraction(1, 20):
        raise ValueError("saved count risk is inconsistent with its recorded budget")
    frequency_cap = Fraction(1, 10 ** (16 if position else 14))
    position_cap = Fraction(1, 10**14) if position else Fraction(0)
    fixed = {
        "epsilon_exact": "1/100000",
        "edge_weight_radius_exact": "1/100001",
        "exposure_cap_exact": "1/100000000000000000000",
        "frequency_error_cap_exact": str(frequency_cap),
        "lag_lower_exact": "1000",
        "eta_exact": "1/100000",
        "target_individual_class_error": "1/20",
    }
    for name, expected in fixed.items():
        if Fraction(parameters[name]) != Fraction(expected):
            raise ValueError(f"saved parameters differ from the fixed contract: {name}")
        if name != "target_individual_class_error":
            if Fraction(counts[name]) != Fraction(expected):
                raise ValueError(f"saved count parameters are inconsistent: {name}")
    if Fraction(parameters["position_error_cap_exact"]) != position_cap:
        raise ValueError("saved position cap differs from the scenario contract")
    if Fraction(frequency["frequency_error_cap_exact"]) != frequency_cap:
        raise ValueError("saved frequency stage differs from the scenario contract")
    if position:
        for record in (selected, counts):
            if Fraction(record["position_error_cap_exact"]) != position_cap:
                raise ValueError("saved position stages differ from the scenario contract")
        if Fraction(selected["mean_contact_remaining_margin_strict_lower_exact"]) != (
            Fraction(1, 4) - 2 * position_cap
        ):
            raise ValueError("saved position contact margin is inconsistent")
    elif "position" in certificate["stages"]:
        raise ValueError("exact-geometry scenario has an unexpected position stage")
    for name, expected in (
        ("h_interval_exact", [Fraction(9, 10), Fraction(11, 10)]),
        ("b_interval_exact", [Fraction(0), Fraction(1)]),
    ):
        if list(map(Fraction, parameters[name])) != expected:
            raise ValueError(f"saved parameters differ from the fixed contract: {name}")
        if list(map(Fraction, counts[name])) != expected:
            raise ValueError(f"saved count parameters are inconsistent: {name}")
    inputs = json.loads(files("homometric_motion").joinpath("inputs.json").read_text("utf-8"))
    cap = Fraction(inputs["beta_cap_exact"])
    if Fraction(parameters["beta_cap_exact"]) != cap:
        raise ValueError("saved strength cap differs from the fixed contract")
    for record in (parameters, frequency, selected, counts):
        band = record["beta_band_exact"]
        if Fraction(band["lower"]) != cap / 2 or Fraction(band["upper"]) != cap:
            raise ValueError("saved strength band differs from the fixed contract")
    heading = (
        f"PASS: homometric-motion {__version__}"
        if verified
        else "UNVERIFIED DISPLAY: saved certificate claims (not recomputed)"
    )
    qualifier = "" if verified else "Recorded claim - "
    return "\n".join(
        [
            heading,
            f"{qualifier}scenario: {scenario}",
            f"{qualifier}mathematical checks: {certificate['checks']['count']}",
            f"{qualifier}selected shape gap lower bound: {float(gap):.16g} (display only)",
            f"{qualifier}sufficient observation windows: {windows:,}",
            f"{qualifier}risk bound: at most 5% in either class under the declared model.",
            f"{qualifier}domain: beta in [B/2,B], fixed frequency error <= {float(frequency_cap):.0e},",
            "spring weights within 1 +/- 1/100001, exposure <= 1e-20, start lag >= 1000,",
            "fixed integrated normalized gain in [0.9,1.1], Poisson background in [0,1].",
            (
                "Fixed position errors <= 1e-14; homometry applies to nominal templates only."
                if position
                else "Exact mean geometry is assumed."
            ),
            "Stationary weighted Gaussian OU motion is assumed.",
            "No physical validation, optimality or practical feasibility is claimed.",
        ]
    )


def extension_summary(certificate: dict, *, verified: bool = False) -> str:
    """Display a named extension, keeping recorded-input limits explicit."""
    core = certificate["core_certificate"]
    if not isinstance(core, dict) or "certificate_kind" in core:
        raise ValueError("coordinate extension requires an ordinary core certificate")
    core_text = summary(core, verified=verified)
    counts = validate_saved_extension(certificate)
    qualifier = "" if verified else "Recorded claim - "
    heading = (
        f"PASS: homometric-motion {__version__} coordinate-count extension"
        if verified
        else "UNVERIFIED DISPLAY: saved certificate claims (not recomputed)"
    )
    domain = core_text.splitlines()
    domain_index = next(
        index for index, line in enumerate(domain) if line.startswith(f"{qualifier}domain:")
    )
    return "\n".join(
        [
            heading,
            f"{qualifier}scenario: {certificate['scenario']}",
            f"{qualifier}core mathematical checks: {core['checks']['count']}",
            f"{qualifier}coordinate mathematical checks: {certificate['checks']['count']}",
            (
                f"{qualifier}common-tolerance sufficient windows: "
                f"{counts['previous_sufficient_observation_windows']:,}"
            ),
            (
                f"{qualifier}coordinate-tolerance sufficient windows: "
                f"{counts['sufficient_observation_windows']:,}"
            ),
            f"{qualifier}risk bound: at most 5% in either class under the same declared model.",
            (
                "The full core and coordinate proof were freshly recomputed."
                if verified
                else "Saved-input consistency checks do not authenticate or recompute the core model."
            ),
            "The coordinate allocation is an exact feasible witness, not a global optimum.",
            *domain[domain_index:],
        ]
    )


def exposure_summary(certificate: dict, *, verified: bool = False) -> str:
    """Display the new chain's domain and counts, not its reference core's."""
    if (
        "source_revision" in certificate
        and certificate["source_revision"] != verify_source_manifest()
    ):
        raise ValueError("saved exposure provenance differs from the installed source manifest")
    core = certificate["core_certificate"]
    if not isinstance(core, dict) or "certificate_kind" in core:
        raise ValueError("exposure extension requires an ordinary core certificate")
    summary(core, verified=verified)
    coordinate = validate_saved_exposure(certificate)
    extension = certificate["extension"]
    common = extension["stages"]["counts"]
    params = extension["parameters"]
    position = certificate["scenario"] == "position_uncertainty"
    heading = (
        f"PASS: homometric-motion {__version__} linear-exposure count extension"
        if verified
        else "UNVERIFIED DISPLAY: saved certificate claims (not recomputed)"
    )
    qualifier = "" if verified else "Recorded claim - "
    return "\n".join(
        [
            heading,
            f"{qualifier}scenario: {certificate['scenario']}",
            f"{qualifier}extension mathematical checks: {certificate['checks']['count']}",
            f"{qualifier}new common-tolerance sufficient windows: {common['sufficient_observation_windows']:,}",
            f"{qualifier}new coordinate-tolerance sufficient windows: {coordinate['sufficient_observation_windows']:,}",
            f"{qualifier}risk bound: at most 5% in either class under the extension's declared model.",
            f"{qualifier}domain: beta in [B/2,B], fixed frequency error <= {float(Fraction(params['frequency_error_cap_exact'])):.0e},",
            "spring weights within 1 +/- 1/100001, exposure <= 1e-5, start lag >= 1000,",
            "fixed integrated normalized gain in [0.9,1.1], Poisson background in [0,1].",
            (
                "Fixed position errors <= 1e-14; homometry applies to nominal templates only."
                if position
                else "Exact mean geometry is assumed."
            ),
            "Stationary compatible weighted Gaussian OU motion is assumed.",
            "Exposure, strength, frequency, springs, positions and channel parameters stay fixed during acquisition.",
            "The embedded 1e-20 core is a reference; these are newly computed bounds and a new classifier threshold.",
            (
                "The reference core and full exposure/count chain were freshly recomputed."
                if verified
                else "Saved-input consistency checks do not authenticate or recompute the reference motion model."
            ),
            "The coordinate allocation is an exact feasible witness, not a global optimum.",
            "No physical validation, necessary count or practical feasibility is claimed.",
        ]
    )


def profile_summary(certificate: dict, *, verified: bool = False) -> str:
    """Display the selected profile; saved-input arithmetic is not authentication."""
    if (
        "source_revision" in certificate
        and certificate["source_revision"] != verify_source_manifest()
    ):
        raise ValueError("saved profile provenance differs from the installed source manifest")
    summary(certificate["core_certificate"], verified=verified)
    allocation = validate_saved_count(certificate)
    params = certificate["parameters"]
    heading = (
        f"PASS: homometric-motion {__version__} profiled count certificate"
        if verified
        else "UNVERIFIED DISPLAY: saved certificate claims (reference model not recomputed)"
    )
    qualifier = "" if verified else "Recorded claim - "
    return "\n".join(
        [
            heading,
            f"{qualifier}profile: {certificate['profile']}",
            f"{qualifier}scenario: {certificate['scenario']}",
            f"{qualifier}profile mathematical checks: {certificate['checks']['count']}",
            f"{qualifier}sufficient observation windows: {allocation['sufficient_observation_windows']:,}",
            f"{qualifier}risk bound: at most 5% in either class under the selected model.",
            f"{qualifier}domain: beta in [B/2,B], fixed frequency error <= {float(Fraction(params['frequency_error_cap_exact'])):.0e},",
            f"spring weights within 1 +/- 1/100001, exposure <= {float(Fraction(params['exposure_cap_exact'])):g}, start lag >= 1000,",
            "fixed integrated normalized gain in [0.9,1.1], Poisson background in [0,1].",
            (
                "Fixed position errors <= 1e-14; homometry applies to nominal templates only."
                if certificate["scenario"] == "position_uncertainty"
                else "Exact mean geometry is assumed."
            ),
            "Stationary compatible weighted Gaussian OU motion is assumed.",
            "Exposure, strength, frequency, springs, positions and channel parameters stay fixed during acquisition.",
            "Use this profile's newly computed threshold in allocation.classifier.",
            "The embedded 1e-20 core is a reference; its eta, count and threshold are not selected here.",
            (
                "The reference core and full selected count chain were freshly recomputed."
                if verified
                else "Saved-input checks reconstruct conditional arithmetic; they do not authenticate the reference motion model."
            ),
            "The allocation is a feasible witness, not a global optimum or a necessary count.",
            "The exact-geometry exposure cap 0.01 remains unresolved by these bounds.",
            "No physical validation or practical feasibility is claimed.",
        ]
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="homometric-motion")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="recompute the full fixed certificate")
    verify.add_argument("--scenario", choices=SCENARIOS, default="exact_geometry")
    verify.add_argument(
        "--output",
        required=True,
        type=Path,
        help="new JSON file; existing files are never overwritten",
    )
    coordinate = commands.add_parser(
        "coordinate-count", help="freshly recompute core and coordinate-tolerance count proof"
    )
    coordinate.add_argument("--scenario", choices=SCENARIOS, default="exact_geometry")
    coordinate.add_argument(
        "--output",
        required=True,
        type=Path,
        help="new extension JSON file; existing files are never overwritten",
    )
    exposure = commands.add_parser(
        "exposure-count", help="freshly recompute the separate linear-exposure count proof"
    )
    exposure.add_argument("--scenario", choices=SCENARIOS, default="exact_geometry")
    exposure.add_argument(
        "--output",
        required=True,
        type=Path,
        help="new exposure extension JSON file; existing files are never overwritten",
    )
    count = commands.add_parser(
        "count", help="freshly recompute a required, explicitly versioned count profile"
    )
    count.add_argument("--profile", choices=PROFILES, required=True)
    count.add_argument("--scenario", choices=SCENARIOS, default="exact_geometry")
    count.add_argument(
        "--output",
        required=True,
        type=Path,
        help="new profile JSON file; existing files are never overwritten",
    )
    show = commands.add_parser("summary", help="display a saved certificate")
    show.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "summary":
            certificate = json.loads(args.path.read_text(encoding="utf-8"))
            print(summary(certificate))
            return 0
        if args.output.exists():
            raise FileExistsError("output exists; choose a new path")
        provenance = verify_source_manifest()
        builders = {
            "verify": build_certificate,
            "coordinate-count": build_coordinate_certificate,
            "exposure-count": build_exposure_certificate,
        }
        certificate = (
            build_count_certificate(profile=args.profile, scenario=args.scenario)
            if args.command == "count"
            else builders[args.command](scenario=args.scenario)
        )
        certificate["source_revision"] = provenance
        encoded = json.dumps(certificate, indent=2, sort_keys=True, allow_nan=False) + "\n"
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
        print(summary(certificate, verified=True))
        return 0
    except (OSError, ValueError, ArithmeticError, KeyError, TypeError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1
