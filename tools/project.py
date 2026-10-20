"""One cross-platform command catalog for local development and CI."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from fractions import Fraction
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "src" / "homometric_motion"
BUILD = ROOT / ".build"
COMMANDS = {
    "help": "show the command catalog",
    "setup": "install hash-locked development dependencies in the active environment",
    "lint": "check Ruff, formatting and committed text hygiene",
    "manifest": "explicitly record the current package source revision",
    "build": "check the manifest and build an sdist and wheel",
    "test": "build, install and test a wheel with a coverage gate",
    "verify": "replay both scenarios/all method profiles and the fixed nine-point model twice",
    "phase-permutation": "build and replay the complete-graph documentation checker from the sdist",
    "prototype": "build and replay the optional instrument from the source archive",
    "release": "run lint, installed tests and artifact verification; publish nothing",
    "hooks": "run the pinned pre-commit checks on all tracked files",
}


def run(*args: object, cwd: Path = ROOT, env: dict | None = None) -> None:
    subprocess.run([str(arg) for arg in args], cwd=cwd, env=env, check=True)


def package_manifest() -> dict:
    paths = sorted([*PACKAGE.glob("*.py"), PACKAGE / "inputs.json", PACKAGE / "protocol.json"])
    return {
        "schema_version": 1,
        "revision_kind": "release_adaptation",
        "files": [
            {"path": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in paths
        ],
    }


def check_manifest() -> None:
    path = PACKAGE / "source_manifest.json"
    if not path.exists() or json.loads(path.read_text("utf-8")) != package_manifest():
        raise RuntimeError("source manifest is absent or stale; review changes, then run manifest")


def text_hygiene() -> None:
    paths = (
        subprocess.check_output(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
        )
        .decode("utf-8")
        .split("\0")
    )
    for name in sorted(set(filter(None, paths))):
        path = ROOT / name
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if b"\0" in raw:
            raise RuntimeError(f"unexpected binary source: {name}")
        content = raw.decode("utf-8")
        if "\r" in content or (content and not content.endswith("\n")):
            raise RuntimeError(f"expected LF text with a final newline: {name}")
        if any(line != line.rstrip() for line in content.splitlines()):
            raise RuntimeError(f"trailing whitespace: {name}")
        if len(raw) > 1_000_000:
            raise RuntimeError(f"unexpectedly large source file: {name}")


def build() -> Path:
    check_manifest()
    run(sys.executable, "-m", "build", "--no-isolation")
    wheels = list((ROOT / "dist").glob("homometric_motion-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError("dist must contain exactly one project wheel")
    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        if any(name.startswith(("tests/", "tools/", "workspace/")) for name in names):
            raise RuntimeError("development or private files leaked into wheel")
        for record in package_manifest()["files"]:
            name = "homometric_motion/" + record["path"]
            if hashlib.sha256(archive.read(name)).hexdigest() != record["sha256"]:
                raise RuntimeError(f"wheel/source mismatch: {name}")
        if (
            archive.read("homometric_motion/source_manifest.json")
            != (PACKAGE / "source_manifest.json").read_bytes()
        ):
            raise RuntimeError("wheel manifest differs from the source manifest")
    return wheel


def installed(wheel: Path) -> tuple[Path, Path, Path]:
    BUILD.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="artifact-", dir=BUILD))
    environment = directory / "venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    executable = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run(executable, "-I", "-m", "pip", "install", "--no-index", "--no-deps", wheel, cwd=directory)
    site = Path(
        subprocess.check_output(
            [str(executable), "-I", "-c", "import sysconfig; print(sysconfig.get_path('purelib'))"],
            cwd=directory,
            text=True,
        ).strip()
    )
    return directory, executable, site


def test(wheel: Path) -> None:
    directory, executable, site = installed(wheel)
    # The ordinary suite runs with only the wheel and the standard library.
    run(
        executable,
        "-I",
        ROOT / "tools/run_installed_tests.py",
        site,
        ROOT / "tests",
        cwd=directory,
        env=dict(os.environ, HM_TEST_PYTHON=str(executable)),
    )
    # Instrument the same installed package with the development coverage tool.
    env = dict(
        os.environ,
        COVERAGE_FILE=str(directory / ".coverage"),
        HM_TEST_PYTHON=str(executable),
    )
    run(
        sys.executable,
        "-I",
        "-m",
        "coverage",
        "run",
        "--rcfile",
        ROOT / "pyproject.toml",
        ROOT / "tools/run_installed_tests.py",
        site,
        ROOT / "tests",
        env=env,
    )
    run(sys.executable, "-m", "coverage", "report", env=env)


def verify(wheel: Path) -> None:
    documentation_check = phase_permutation()
    directory, executable, _ = installed(wheel)
    scenarios = []
    extensions = []
    exposure_extensions = []
    profile_certificates = []
    for scenario, expected_count in (
        ("exact_geometry", 975281623024726766278),
        ("position_uncertainty", 975028627229038193209),
    ):
        outputs = [directory / f"{scenario}-{name}.json" for name in ("first", "second")]
        for output in outputs:
            run(
                executable,
                "-I",
                "-m",
                "homometric_motion",
                "verify",
                "--scenario",
                scenario,
                "--output",
                output,
                cwd=directory,
            )
        if outputs[0].read_bytes() != outputs[1].read_bytes():
            raise RuntimeError(f"{scenario}: installed CLI certificates differ")
        certificate = json.loads(outputs[0].read_text("utf-8"))
        if certificate["status"] != "PASS" or certificate["scenario"] != scenario:
            raise RuntimeError(f"{scenario}: certificate did not pass with the expected scenario")
        count = certificate["stages"]["counts"]["sufficient_observation_windows"]
        if count != expected_count:
            raise RuntimeError(f"{scenario}: published count changed; review scientific revision")
        run(executable, "-I", "-m", "homometric_motion", "summary", outputs[0], cwd=directory)
        if scenario == "exact_geometry":
            run(
                executable,
                "-I",
                ROOT / "tools/build_demo.py",
                "--certificate",
                outputs[0],
                "--check",
                cwd=directory,
            )
        scenarios.append(
            {
                "scenario": scenario,
                "certificate_sha256": hashlib.sha256(outputs[0].read_bytes()).hexdigest(),
                "deterministic_cli_runs": 2,
                "checks": certificate["checks"]["count"],
                "sufficient_observation_windows": count,
            }
        )
        coordinate_outputs = [
            directory / f"{scenario}-coordinate-{name}.json" for name in ("first", "second")
        ]
        for output in coordinate_outputs:
            run(
                executable,
                "-I",
                "-m",
                "homometric_motion",
                "coordinate-count",
                "--scenario",
                scenario,
                "--output",
                output,
                cwd=directory,
            )
        if coordinate_outputs[0].read_bytes() != coordinate_outputs[1].read_bytes():
            raise RuntimeError(f"{scenario}: coordinate certificates differ")
        extension = json.loads(coordinate_outputs[0].read_text("utf-8"))
        core = dict(certificate)
        provenance = core.pop("source_revision")
        if (
            extension["status"] != "PASS"
            or extension["certificate_kind"] != "coordinate_count_extension"
            or extension["core_certificate"] != core
            or extension["source_revision"] != provenance
        ):
            raise RuntimeError(f"{scenario}: coordinate extension changed the core or provenance")
        coordinate_count = extension["coordinate_counts"]["sufficient_observation_windows"]
        expected_coordinate = {
            "exact_geometry": 26814048499063502,
            "position_uncertainty": 26808243624540316,
        }[scenario]
        if coordinate_count != expected_coordinate:
            raise RuntimeError(f"{scenario}: coordinate count changed; review scientific revision")
        run(
            executable,
            "-I",
            "-m",
            "homometric_motion",
            "summary",
            coordinate_outputs[0],
            cwd=directory,
        )
        extensions.append(
            {
                "scenario": scenario,
                "certificate_sha256": hashlib.sha256(
                    coordinate_outputs[0].read_bytes()
                ).hexdigest(),
                "deterministic_cli_runs": 2,
                "coordinate_checks": extension["checks"]["count"],
                "sufficient_observation_windows": coordinate_count,
                "embedded_core_matches_original_method": True,
            }
        )
        exposure_outputs = [
            directory / f"{scenario}-exposure-{name}.json" for name in ("first", "second")
        ]
        for output in exposure_outputs:
            run(
                executable,
                "-I",
                "-m",
                "homometric_motion",
                "exposure-count",
                "--scenario",
                scenario,
                "--output",
                output,
                cwd=directory,
            )
        if exposure_outputs[0].read_bytes() != exposure_outputs[1].read_bytes():
            raise RuntimeError(f"{scenario}: exposure certificates differ")
        exposure_extension = json.loads(exposure_outputs[0].read_text("utf-8"))
        if (
            exposure_extension["status"] != "PASS"
            or exposure_extension["certificate_kind"] != "linear_exposure_count_extension"
            or exposure_extension["core_certificate"] != core
            or exposure_extension["source_revision"] != provenance
            or exposure_extension["extension"]["parameters"]["exposure_cap_exact"] != "1/100000"
        ):
            raise RuntimeError(f"{scenario}: exposure extension changed its reference or contract")
        exposure_count = exposure_extension["coordinate_counts"]["sufficient_observation_windows"]
        expected_exposure = {
            "exact_geometry": 26815183544609917,
            "position_uncertainty": 26809378397093764,
        }[scenario]
        if exposure_count != expected_exposure:
            raise RuntimeError(f"{scenario}: exposure count changed; review scientific revision")
        run(
            executable,
            "-I",
            "-m",
            "homometric_motion",
            "summary",
            exposure_outputs[0],
            cwd=directory,
        )
        exposure_extensions.append(
            {
                "scenario": scenario,
                "certificate_sha256": hashlib.sha256(exposure_outputs[0].read_bytes()).hexdigest(),
                "deterministic_cli_runs": 2,
                "extension_checks": exposure_extension["checks"]["count"],
                "sufficient_observation_windows": exposure_count,
                "exposure_cap_exact": "1/100000",
                "reference_core_matches_original_method": True,
            }
        )
        expected_profiles = {
            "short-exposure-v1": {
                "exact_geometry": (69803163290068, "1/100000"),
                "position_uncertainty": (5362340030851, "1/100000"),
            },
            "long-exposure-v1": {
                "exact_geometry": (36938105282195, "1/1000"),
                "position_uncertainty": (16852383428868, "1/100"),
            },
        }
        for profile, selected in expected_profiles.items():
            profile_outputs = [
                directory / f"{scenario}-{profile}-{name}.json" for name in ("first", "second")
            ]
            for output in profile_outputs:
                run(
                    executable,
                    "-I",
                    "-m",
                    "homometric_motion",
                    "count",
                    "--profile",
                    profile,
                    "--scenario",
                    scenario,
                    "--output",
                    output,
                    cwd=directory,
                )
            if profile_outputs[0].read_bytes() != profile_outputs[1].read_bytes():
                raise RuntimeError(f"{scenario}/{profile}: profile certificates differ")
            result = json.loads(profile_outputs[0].read_text("utf-8"))
            expected, cap = selected[scenario]
            if (
                result["status"] != "PASS"
                or result["certificate_kind"] != "profiled_count_certificate"
                or result["profile"] != profile
                or result["scenario"] != scenario
                or result["core_certificate"] != core
                or result["source_revision"] != provenance
                or result["parameters"]["exposure_cap_exact"] != cap
                or "eta_exact" in result["parameters"]
                or result["allocation"]["sufficient_observation_windows"] != expected
            ):
                raise RuntimeError(f"{scenario}/{profile}: profile reference or contract changed")
            run(
                executable,
                "-I",
                "-m",
                "homometric_motion",
                "summary",
                profile_outputs[0],
                cwd=directory,
            )
            profile_certificates.append(
                {
                    "profile": profile,
                    "scenario": scenario,
                    "certificate_sha256": hashlib.sha256(
                        profile_outputs[0].read_bytes()
                    ).hexdigest(),
                    "deterministic_cli_runs": 2,
                    "profile_checks": result["checks"]["count"],
                    "sufficient_observation_windows": expected,
                    "exposure_cap_exact": cap,
                    "reference_core_matches_original_method": True,
                }
            )
    small_outputs = [directory / f"nine-point-{name}.json" for name in ("first", "second")]
    for output in small_outputs:
        run(
            executable,
            "-I",
            "-m",
            "homometric_motion",
            "small-pair",
            "--output",
            output,
            cwd=directory,
        )
    if small_outputs[0].read_bytes() != small_outputs[1].read_bytes():
        raise RuntimeError("nine-point installed CLI certificates differ")
    small = json.loads(small_outputs[0].read_text("utf-8"))
    bands = small["independent_strength_bands"]
    if (
        small["status"] != "PASS"
        or small["certificate_kind"] != "nine_point_finite_motion_v1"
        or small["parameters"]["n"] != 9
        or small["source_revision"] != provenance
        or "core_certificate" in small
        or bands["passing_projection_radii"] != ["1/1024", "1/4096"]
        or len(bands["rows"]) != 5
    ):
        raise RuntimeError("nine-point fixed model or scope changed")
    for index, row in enumerate(bands["rows"]):
        tests = row["independent_strength_range_tests"]
        if any(tests[name]["status"] != "UNRESOLVED_RANGE_OVERLAP" for name in ("mu1", "mu2")):
            raise RuntimeError("nine-point single-moment range result changed")
        projection = tests["projection"]
        if index < 3:
            if projection["status"] != "UNRESOLVED_RANGE_OVERLAP":
                raise RuntimeError("nine-point wider unresolved projection band changed")
        elif projection["status"] != "CERTIFIED_B_BELOW_A" or Fraction(
            projection["positive_gap"]
        ) <= Fraction(7, 100000):
            raise RuntimeError("nine-point local projection gap changed")
    run(executable, "-I", "-m", "homometric_motion", "summary", small_outputs[0], cwd=directory)
    receipt = {
        "status": "PASS",
        "wheel": wheel.name,
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "scenarios": scenarios,
        "coordinate_extensions": extensions,
        "exposure_extensions": exposure_extensions,
        "profile_certificates": profile_certificates,
        "nine_point_certificate": {
            "certificate_sha256": hashlib.sha256(small_outputs[0].read_bytes()).hexdigest(),
            "deterministic_cli_runs": 2,
            "checks": small["checks"]["count"],
            "saved_summary_fresh_reconstructions": 1,
            "has_detector_or_count_guarantee": False,
        },
        "fresh_cli_calculations": 22,
        "demo_data_matches_exact_geometry": True,
        "phase_permutation_documentation": documentation_check,
    }
    (directory / "verification.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(receipt, indent=2))


def phase_permutation() -> dict:
    """Replay the two reviewed documentation files from the actual source archive."""
    expected = {
        "docs/proofs/phase-permutation.md",
        "docs/proofs/check_phase_permutation.py",
    }
    distributions = list((ROOT / "dist").glob("homometric_motion-*.tar.gz"))
    if len(distributions) != 1:
        raise RuntimeError("dist must contain exactly one source distribution")
    payload = {}
    archive_root = None
    with tarfile.open(distributions[0], "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = path.parts
            if path.is_absolute() or ".." in parts or "\\" in member.name or not parts:
                raise RuntimeError("unsafe source-archive member path")
            if archive_root is None:
                archive_root = parts[0]
            elif archive_root != parts[0]:
                raise RuntimeError("source archive has multiple top-level directories")
            relative = PurePosixPath(*parts[1:]).as_posix()
            if relative not in expected:
                continue
            if not member.isfile() or member.size > 100_000 or relative in payload:
                raise RuntimeError("unexpected phase-permutation documentation member")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError("phase-permutation source could not be read")
            raw = stream.read()
            if raw != (ROOT / relative).read_bytes():
                raise RuntimeError("phase-permutation archive differs from reviewed source")
            payload[relative] = raw
    if set(payload) != expected:
        raise RuntimeError("phase-permutation source archive is incomplete")
    BUILD.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="phase-permutation-", dir=BUILD))
    outputs = []
    for label in ("first", "second"):
        isolated = directory / label
        isolated.mkdir()
        for relative, raw in payload.items():
            target = isolated / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(raw)
        checker = isolated / "docs/proofs/check_phase_permutation.py"
        output = isolated / "result.json"
        subprocess.run(
            [sys.executable, "-I", "-S", "-B", str(checker), "--output", str(output)],
            cwd=isolated,
            check=True,
            timeout=30,
        )
        outputs.append(output)
    first = outputs[0].read_bytes()
    if first != outputs[1].read_bytes():
        raise RuntimeError("phase-permutation artifact replay outputs differ")
    certificate = json.loads(first)
    if (
        certificate["status"] != "PASS"
        or certificate["kind"] != "phase_permutation_k9_algebra_v1"
        or certificate["schema_version"] != 1
        or certificate["phase_permutation"]["row_to_column_zero_based"]
        != [0, 1, 2, 5, 3, 4, 6, 7, 8]
        or not certificate["phase_permutation"]["all_81_formal_intensity_coefficients_identical"]
        or certificate["common_graph"]["nominal_threshold_exact"] != "28"
        or certificate["common_graph"]["trace_Lplus_exact"] != "8/9"
        or certificate["common_graph"]["relative_pair_variance_exact"] != "9/4"
    ):
        raise RuntimeError("phase-permutation artifact fixed model changed")
    controls = certificate["negative_controls"]
    if any(
        controls[name] is not False
        for name in (
            "cross_residue_permutation_phase_match",
            "perturbed_covariance_permutation_invariant",
            "threshold_15_over_2_full_graph_conjugacy_under_fixed_P",
        )
    ):
        raise RuntimeError("phase-permutation failed-criterion controls changed")
    refused = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-B",
            str(outputs[0].parent / "docs/proofs/check_phase_permutation.py"),
            "--output",
            str(outputs[0]),
        ],
        cwd=outputs[0].parent,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    if (
        refused.returncode == 0
        or "FileExistsError: output exists; choose a new file" not in refused.stderr
        or outputs[0].read_bytes() != first
    ):
        raise RuntimeError("phase-permutation output overwrite was not refused")
    receipt = {
        "status": "PASS",
        "scope": "Finite algebra from source-archive documentation; analytic path proof is separate",
        "sdist_sha256": hashlib.sha256(distributions[0].read_bytes()).hexdigest(),
        "documentation_files": {
            name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(payload.items())
        },
        "checks": certificate["checks"]["count"],
        "deterministic_runs": 2,
        "separate_isolated_directories": True,
        "site_imports_disabled": True,
        "overwrite_refused": True,
        "overwrite_refusal_exit_code": refused.returncode,
        "result_sha256": hashlib.sha256(first).hexdigest(),
    }
    with (directory / "verification.json").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2))
    return receipt


def prototype() -> None:
    """Execute source-archive scripts using the active optional numerical environment."""
    source = ROOT / "prototype"
    manifest = json.loads((source / "source_manifest.json").read_text("utf-8"))
    expected = {row["path"] for row in manifest["files"]} | {"source_manifest.json"}
    if any(PurePosixPath(name).name != name for name in expected):
        raise RuntimeError("prototype manifest paths must be simple filenames")
    distributions = list((ROOT / "dist").glob("homometric_motion-*.tar.gz"))
    if len(distributions) != 1:
        raise RuntimeError("dist must contain exactly one source distribution")
    BUILD.mkdir(exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix="prototype-", dir=BUILD))
    package = directory / "prototype"
    package.mkdir()
    found = set()
    with tarfile.open(distributions[0], "r:gz") as archive:
        for member in archive.getmembers():
            parts = PurePosixPath(member.name).parts
            if len(parts) < 2 or parts[1] != "prototype" or member.isdir():
                continue
            if len(parts) != 3 or not member.isfile() or member.size > 1_000_000:
                raise RuntimeError("unexpected prototype archive member")
            name = parts[2]
            if name not in expected or name in found:
                raise RuntimeError("unexpected or duplicate prototype source")
            stream = archive.extractfile(member)
            if stream is None:
                raise RuntimeError("prototype archive file could not be read")
            raw = stream.read()
            if raw != (source / name).read_bytes():
                raise RuntimeError("prototype archive differs from reviewed source")
            (package / name).write_bytes(raw)
            found.add(name)
    if found != expected:
        raise RuntimeError("prototype source archive is incomplete")
    for label in ("first", "second"):
        output = directory / label
        run(
            sys.executable,
            "-I",
            "-B",
            package / "run_instrument.py",
            "--output",
            output,
            cwd=directory,
        )
        run(sys.executable, "-I", "-B", package / "inspect_run.py", "--run", output, cwd=directory)
    inventories = []
    for label in ("first", "second"):
        output = directory / label
        inventories.append(
            {
                path.relative_to(output).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(output.rglob("*"))
                if path.is_file()
            }
        )
    if inventories[0] != inventories[1]:
        raise RuntimeError("prototype outputs differ between repeated runs")
    receipt = {
        "status": "PASS",
        "scope": "Synthetic source-artifact replay and saved-output consistency, not physical validation",
        "sdist_sha256": hashlib.sha256(distributions[0].read_bytes()).hexdigest(),
        "prototype_manifest_sha256": hashlib.sha256(
            (package / "source_manifest.json").read_bytes()
        ).hexdigest(),
        "replays": 2,
        "files_per_run": len(inventories[0]),
        "output_hashes": inventories[0],
    }
    (directory / "verification.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"PASS: two matching synthetic artifact runs, {len(inventories[0])} files each")


def lint() -> None:
    run(sys.executable, "-m", "ruff", "check", ".")
    run(sys.executable, "-m", "ruff", "format", "--check", ".")
    text_hygiene()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=COMMANDS, nargs="?", default="help")
    command = parser.parse_args().command
    if command == "help":
        for name, description in COMMANDS.items():
            print(f"{name:10} {description}")
    elif command == "setup":
        run(
            sys.executable,
            "-m",
            "pip",
            "install",
            "--require-hashes",
            "-r",
            "requirements-dev.txt",
        )
    elif command == "lint":
        lint()
    elif command == "manifest":
        (PACKAGE / "source_manifest.json").write_text(
            json.dumps(package_manifest(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print("Recorded a new source revision. Run release to validate it.")
    elif command == "hooks":
        run(sys.executable, "-m", "pre_commit", "run", "--all-files")
    else:
        if command == "release":
            lint()
        wheel = build()
        if command in {"test", "release"}:
            test(wheel)
        if command in {"verify", "release"}:
            verify(wheel)
        if command == "prototype":
            prototype()
        if command == "phase-permutation":
            phase_permutation()


if __name__ == "__main__":
    main()
