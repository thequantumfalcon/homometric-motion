"""Run and inspect the installed mathematical certificate."""

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from importlib.resources import files
from pathlib import Path

from . import __version__
from .certificate import build_certificate

MANIFEST_FILES = {
    "__init__.py",
    "__main__.py",
    "arithmetic.py",
    "certificate.py",
    "cli.py",
    "counts.py",
    "geometry.py",
    "motion.py",
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
    if certificate.get("schema_version") != 1 or certificate.get("status") != "PASS":
        raise ValueError("unsupported or unsuccessful certificate")
    frequency = certificate["stages"]["frequency"]
    counts = certificate["stages"]["counts"]
    parameters = certificate["parameters"]
    windows = counts["sufficient_observation_windows"]
    gap = Fraction(frequency["signed_gap_exact"])
    if type(windows) is not int or windows != 975281623024726766278 or gap <= 0:
        raise ValueError("invalid certificate summary fields")
    fixed = {
        "epsilon_exact": "1/100000",
        "edge_weight_radius_exact": "1/100001",
        "exposure_cap_exact": "1/100000000000000000000",
        "frequency_error_cap_exact": "1/100000000000000",
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
    for record in (parameters, frequency, counts):
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
            f"{qualifier}mathematical checks: {certificate['checks']['count']}",
            f"{qualifier}frequency-robust gap lower bound: {float(gap):.16g} (display only)",
            f"{qualifier}sufficient observation windows: {windows:,}",
            f"{qualifier}risk bound: at most 5% in either class under the declared model.",
            f"{qualifier}domain: beta in [B/2,B], fixed frequency error <= 1e-14,",
            "spring weights within 1 +/- 1/100001, exposure <= 1e-20, start lag >= 1000,",
            "fixed integrated normalized gain in [0.9,1.1], Poisson background in [0,1].",
            "Exact geometry and stationary weighted Gaussian OU motion are assumed.",
            "No physical validation, optimality or practical feasibility is claimed.",
        ]
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="homometric-motion")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="recompute the full fixed certificate")
    verify.add_argument(
        "--output",
        required=True,
        type=Path,
        help="new JSON file; existing files are never overwritten",
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
        certificate = build_certificate()
        certificate["source_revision"] = provenance
        encoded = json.dumps(certificate, indent=2, sort_keys=True, allow_nan=False) + "\n"
        with args.output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(encoded)
        print(summary(certificate, verified=True))
        return 0
    except (OSError, ValueError, ArithmeticError, KeyError, TypeError) as exc:
        print(f"Verification failed: {exc}", file=sys.stderr)
        return 1
