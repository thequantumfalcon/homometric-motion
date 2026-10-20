"""One cross-platform command catalog for local development and CI."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

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
    "verify": "build and replay both scenarios twice, then check the demo data",
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
    directory, executable, _ = installed(wheel)
    scenarios = []
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
    receipt = {
        "status": "PASS",
        "wheel": wheel.name,
        "wheel_sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
        "scenarios": scenarios,
        "demo_data_matches_exact_geometry": True,
    }
    (directory / "verification.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    print(json.dumps(receipt, indent=2))


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
            "requirements-dev.lock",
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


if __name__ == "__main__":
    main()
