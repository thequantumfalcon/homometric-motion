"""Replay bounded Lean checkpoints from an inspected source distribution.

Lean/Lake are optional development tools. This standard-library verifier never
loads saved scientific results as calculation inputs. Network access is used
only while Lake prepares the pinned mathematical dependencies and their cache.
"""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tarfile
import venv
import zipfile
from pathlib import Path, PurePosixPath

TOOLCHAIN = "leanprover/lean4:v4.35.0"
MATHLIB_REVISION = "56a005855ea17e0b0958f73ec801ae140b0a1679"
FORMAL = "docs/proofs/formal"
FOUNDATIONS = frozenset({"propext", "Classical.choice", "Quot.sound"})
MODULES = (
    "StandardDeviationContinuity",
    "CumulantSensitivity",
    "NinePointBezout",
    "GaussianIntensity",
    "GaussianMoments",
    "GaussianChargeApplication",
    "ChargeHistogram",
    "GraphCommon",
    "GraphCovariance",
)
ANALYTIC_FILES = frozenset(
    {name + ".lean" for name in MODULES}
    | {
        ".gitignore",
        "build_nine_point_checkpoint.py",
        "lake-manifest.json",
        "lakefile.toml",
        "lean-toolchain",
        "mapping.json",
        "README.md",
        "SCOPE.md",
    }
)
FORMAL_FILES = frozenset(
    {
        "README.md",
        "generate_checkpoint.py",
        "lean-toolchain",
        "FactorialIdentities.lean",
        "position_uncertainty/CertificateCheckpoint.lean",
        "position_uncertainty/statement_mapping.json",
        "analytic/source_manifest.json",
    }
    | {"analytic/" + name for name in ANALYTIC_FILES}
)

# This is a reviewed statement inventory, not a count inferred from replay output.
STATEMENTS = {
    "CertificateCheckpoint": (
        "CertificateCheckpoint",
        "selected_position_shape_gap expanded_count_rule_gap ceiling_lower ceiling_upper "
        "recorded_individual_error_at_most_one_twentieth positive_position_contact_margin",
    ),
    "FactorialIdentities": (
        "FactorialCheckpoint",
        "product11 product12 product13 product22 product23 product33",
    ),
    "StandardDeviationContinuity": (
        "AnalyticRobustness",
        "norm_toLp_sq_eq_integral_sq sqrt_integral_sq_eq_norm_toLp "
        "sqrt_variance_eq_centered_norm centered_norm_le_norm abs_sqrt_variance_sub_le_l2 "
        "variance_enclosure_of_l2_bound sqrt_integral_sq_le_l3 "
        "abs_sqrt_variance_sub_le_l3 variance_enclosure_of_l3_bound",
    ),
    "CumulantSensitivity": (
        "HomometricMotion",
        "third_cumulant_perturbation_identity third_cumulant_linear_coefficient "
        "third_cumulant_coefficient_interval_bound dropping_variance_upper_term_is_false",
    ),
    "NinePointBezout": (
        "HomometricMotion.NinePoint",
        "bezout_identity no_common_zero mean_factorization cofactor_positive "
        "joint_moment_noncoincidence",
    ),
    "GaussianIntensity": (
        "HomometricMotion",
        "centered_gaussian_characteristic quadratic_form_smul centered_gaussian_linear_phase "
        "continuous_phase_integrable phase_mul_conj finite_intensity_expansion "
        "pair_intensity_integrable finite_intensity_complex_integrable finite_intensity_integrable "
        "coordinate_difference_quadratic gaussian_coordinate_difference_phase "
        "finite_gaussian_intensity_complex_mean finite_gaussian_intensity_mean",
    ),
    "GaussianMoments": (
        "HomometricMotion",
        "inner_moment_charge tuple_phase_product finite_intensity_power_expansion "
        "tuple_intensity_integrable finite_intensity_power_complex_integrable "
        "finite_intensity_power_integrable gaussian_tuple_phase "
        "finite_gaussian_intensity_complex_moment finite_gaussian_intensity_moment",
    ),
    "GaussianChargeApplication": (
        "HomometricMotion",
        "moment_charge_total_zero nominal_moment_weight nominal_moment_weight_real "
        "physical_amplitude_factorization physical_strength_exponent "
        "physical_intensity_power_integrable finite_physical_gaussian_intensity_moment",
    ),
    "ChargeHistogram": (
        "HomometricMotion",
        "charge_vector_of_tuple integer_charge_total_zero charge_histogram_sum "
        "charge_histogram_mass finite_physical_gaussian_intensity_histogram",
    ),
    "GraphCommon": ("HomometricMotion.GraphCovariance", ""),
    "GraphCovariance": (
        "HomometricMotion.GraphCovariance",
        "liftMatrix_mul liftMatrix_transpose lift_projector "
        "rationalA_threshold rationalA_gram rationalA_symmetric rationalA_inverse "
        "rationalA_centered rationalA_projector rationalA_zero_com rationalA_trace "
        "laplacianA_gram inverseA_selfadjoint inverseA_laplacian_right inverseA_projector "
        "projector_laplacianA inverseA_zero_com inverseA_psd covarianceA_psd inverseA_trace "
        "covarianceA_normalization covarianceA_trace covarianceA_zero_com gaussianA_zero_com "
        "rationalB_threshold rationalB_gram rationalB_symmetric rationalB_inverse "
        "rationalB_centered rationalB_projector rationalB_zero_com rationalB_trace "
        "laplacianB_gram inverseB_selfadjoint inverseB_laplacian_right inverseB_projector "
        "projector_laplacianB inverseB_zero_com inverseB_psd covarianceB_psd inverseB_trace "
        "covarianceB_normalization covarianceB_trace covarianceB_zero_com gaussianB_zero_com "
        "negative_covarianceA_not_psd inverse_gram_certificate_psd "
        "centered_gaussian_kernel_direction_ae_zero inner_comOnes_eq_sum",
    ),
}
CACHE_MODULES = (
    "Mathlib.Probability.Moments.Variance",
    "Mathlib.MeasureTheory.Function.L2Space",
    "Mathlib.Basic.Real.Basic",
    "Mathlib.Probability.Distributions.Gaussian.Multivariate",
    "Mathlib.Tactic.Linarith",
    "Mathlib.Tactic.Ring",
    "Mathlib.Tactic.NormNum",
    "Mathlib.Tactic.Positivity",
    "Mathlib.Tactic.FinCases",
)


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def lean_code(source: str) -> str:
    """Remove nested comments and strings before checking forbidden proof escapes."""
    output = []
    index = 0
    depth = 0
    quoted = False
    while index < len(source):
        pair = source[index : index + 2]
        character = source[index]
        if depth:
            if pair == "/-":
                depth += 1
                index += 2
            elif pair == "-/":
                depth -= 1
                index += 2
            else:
                output.append("\n" if character == "\n" else " ")
                index += 1
        elif quoted:
            if character == "\\":
                index += 2
            else:
                quoted = character != '"'
                output.append("\n" if character == "\n" else " ")
                index += 1
        elif pair == "/-":
            depth = 1
            output.append(" ")
            index += 2
        elif pair == "--":
            end = source.find("\n", index)
            index = len(source) if end == -1 else end
        elif character == '"':
            quoted = True
            output.append(" ")
            index += 1
        else:
            output.append(character)
            index += 1
    if depth or quoted:
        raise RuntimeError("unterminated Lean comment or string")
    return "".join(output)


def expected_names(module: str) -> tuple[str, ...]:
    namespace, names = STATEMENTS[module]
    return tuple(namespace + "." + name for name in names.split())


def check_lean_source(module: str, raw: bytes) -> None:
    code = lean_code(raw.decode("utf-8"))
    if re.search(r"\b(?:sorry|admit|native_decide|axiom|unsafe|skipKernelTC)\b", code):
        raise RuntimeError(f"forbidden proof escape in {module}")
    directives = re.findall(r"(?m)^\s*#([A-Za-z_]+)([^\n]*)", code)
    if any(
        command != "print" or not re.fullmatch(r"\s+axioms\s+[A-Za-z0-9_.]+\s*", arguments)
        for command, arguments in directives
    ):
        raise RuntimeError(f"unexpected Lean diagnostic directive in {module}")
    namespace = STATEMENTS[module][0]
    printed = re.findall(r"(?m)^#print axioms ([A-Za-z0-9_.]+)\s*$", code)
    names = tuple(name if "." in name else namespace + "." + name for name in printed)
    if names != expected_names(module):
        raise RuntimeError(f"unexpected statement inventory in {module}")


def check_axioms(module: str, stdout: str, stderr: str = "") -> dict[str, list[str]]:
    """Require every named report exactly once, with no unrecognized diagnostics."""
    if stderr.strip():
        raise RuntimeError(f"unexpected Lean stderr for {module}")
    pattern = re.compile(
        r"'([^'\n]+)' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)"
    )
    found = {}
    position = 0
    for match in pattern.finditer(stdout):
        if stdout[position : match.start()].strip():
            raise RuntimeError(f"unexpected Lean diagnostic for {module}")
        name = match[1]
        if name in found:
            raise RuntimeError(f"duplicate axiom report for {name}")
        axioms = [item.strip() for item in (match[2] or "").split(",") if item.strip()]
        expected = frozenset() if module == "CertificateCheckpoint" else FOUNDATIONS
        if len(axioms) != len(set(axioms)) or frozenset(axioms) != expected:
            raise RuntimeError(f"unexpected axioms for {name}: {axioms}")
        found[name] = axioms
        position = match.end()
    if stdout[position:].strip() or tuple(found) != expected_names(module):
        raise RuntimeError(f"missing, reordered or unexpected axiom reports for {module}")
    return found


def verified_files(reviewed_root: Path) -> dict[str, bytes]:
    directory = reviewed_root / FORMAL
    files = {}
    for name in sorted(FORMAL_FILES):
        path = directory / name
        if (
            path.is_symlink()
            or not path.resolve().is_relative_to(directory.resolve())
            or not path.is_file()
            or path.stat().st_size > 1_000_000
        ):
            raise RuntimeError(f"invalid reviewed formal source: {name}")
        files[name] = path.read_bytes()
    manifest = json.loads(files["analytic/source_manifest.json"])
    entries = manifest.get("files", [])
    if (
        manifest.get("schema_version") != 1
        or len(entries) != len(ANALYTIC_FILES)
        or {row.get("path") for row in entries} != ANALYTIC_FILES
    ):
        raise RuntimeError("invalid analytic source manifest inventory")
    for row in entries:
        raw = files["analytic/" + row["path"]]
        if row.get("bytes") != len(raw) or row.get("sha256") != digest(raw):
            raise RuntimeError("analytic source manifest mismatch: " + row["path"])
    for name in ("lean-toolchain", "analytic/lean-toolchain"):
        if files[name].decode().strip() != TOOLCHAIN:
            raise RuntimeError("unexpected Lean toolchain pin")
    for module in MODULES:
        check_lean_source(module, files[f"analytic/{module}.lean"])
    check_lean_source("FactorialIdentities", files["FactorialIdentities.lean"])
    check_lean_source(
        "CertificateCheckpoint", files["position_uncertainty/CertificateCheckpoint.lean"]
    )
    dependency_pins(files["analytic/lake-manifest.json"])
    return files


def dependency_pins(raw: bytes) -> dict[str, str]:
    lock = json.loads(raw)
    packages = lock.get("packages", [])
    names = [item.get("name") for item in packages]
    if (
        lock.get("version") != "1.3.0"
        or lock.get("packagesDir") != ".lake/packages"
        or lock.get("fixedToolchain") is not True
        or len(packages) != 9
        or len(set(names)) != 9
    ):
        raise RuntimeError("invalid Lake dependency inventory")
    pins = {}
    for item in packages:
        name, revision = item["name"], item.get("rev", "")
        if (
            not isinstance(name, str)
            or not re.fullmatch(r"[A-Za-z0-9_]+", name)
            or item.get("type") != "git"
            or not re.fullmatch(r"[0-9a-f]{40}", revision)
        ):
            raise RuntimeError("invalid pinned Lake dependency")
        pins[name] = revision
    if pins.get("mathlib") != MATHLIB_REVISION:
        raise RuntimeError("unexpected mathlib revision")
    return pins


def extract_reviewed(archive: Path, files: dict[str, bytes], destination: Path) -> None:
    """Extract matching regular files explicitly, never following archive links."""
    destination.mkdir(parents=True, exist_ok=False)
    seen = set()
    roots = set()
    with tarfile.open(archive, "r:gz") as source:
        for member in source:
            path = PurePosixPath(member.name)
            parts = path.parts
            if path.is_absolute() or ".." in parts or "\\" in member.name or not parts:
                raise RuntimeError("unsafe source archive path")
            roots.add(parts[0])
            if len(roots) != 1:
                raise RuntimeError("source archive has multiple roots")
            if parts[1:4] != ("docs", "proofs", "formal") or member.isdir():
                continue
            name = PurePosixPath(*parts[4:]).as_posix()
            if name not in files or name in seen or not member.isfile():
                raise RuntimeError("unexpected or duplicate formal archive member")
            if member.size != len(files[name]):
                raise RuntimeError("formal archive size differs from reviewed source")
            stream = source.extractfile(member)
            if stream is None or stream.read() != files[name]:
                raise RuntimeError("formal archive differs from reviewed source")
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(files[name])
            seen.add(name)
    if seen != set(files):
        raise RuntimeError("formal source archive is incomplete")


def checked_run(
    command: list[str | Path], cwd: Path, logs: Path, label: str, env: dict, timeout: int = 1200
) -> subprocess.CompletedProcess:
    try:
        result = subprocess.run(
            [str(argument) for argument in command],
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        for stream in ("stdout", "stderr"):
            raw = getattr(error, stream) or b""
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8", errors="replace")
            (logs / f"{label}.{stream}.txt").write_text(raw, encoding="utf-8", newline="\n")
        raise RuntimeError(f"Lean verification step {label} timed out; inspect {logs}") from error
    for stream in ("stdout", "stderr"):
        (logs / f"{label}.{stream}.txt").write_text(
            getattr(result, stream), encoding="utf-8", newline="\n"
        )
    if result.returncode:
        raise RuntimeError(f"Lean verification step {label} failed; inspect {logs}")
    print(f"PASS: {label}", flush=True)
    return result


def check_sources(source: Path, files: dict[str, bytes]) -> None:
    for name, raw in files.items():
        path = source / name
        if path.is_symlink() or path.read_bytes() != raw:
            raise RuntimeError("Lean replay modified packaged source: " + name)


def check_wheel(wheel: Path, package: Path) -> None:
    """Reject foreign import hooks or payloads before installing the optional task's wheel."""
    expected = {
        "homometric_motion/" + path.name: path.read_bytes()
        for path in package.iterdir()
        if path.is_file() and path.suffix in {".py", ".json"}
    }
    metadata = {
        "licenses/LICENSE.txt",
        "METADATA",
        "WHEEL",
        "entry_points.txt",
        "top_level.txt",
        "RECORD",
    }
    with zipfile.ZipFile(wheel) as built:
        names = built.namelist()
        roots = {name.split("/", 1)[0] for name in names if ".dist-info/" in name}
        if len(names) != len(set(names)) or len(roots) != 1:
            raise RuntimeError("duplicate or invalid wheel inventory")
        root = roots.pop()
        if not re.fullmatch(r"homometric_motion-[A-Za-z0-9_.+]+\.dist-info", root):
            raise RuntimeError("unexpected wheel metadata directory")
        if set(names) != set(expected) | {root + "/" + name for name in metadata}:
            raise RuntimeError("unexpected wheel payload")
        for name, raw in expected.items():
            if built.read(name) != raw:
                raise RuntimeError("Lean task wheel differs from reviewed package")


def verify_archive(
    archive: Path,
    wheel: Path,
    reviewed_root: Path,
    destination: Path,
    *,
    lean: str = "lean",
    lake: str = "lake",
) -> dict:
    archive, wheel, reviewed_root = archive.resolve(), wheel.resolve(), reviewed_root.resolve()
    files = verified_files(reviewed_root)
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("Lean verification destination must be new")
    destination = destination.resolve()
    destination.mkdir(parents=True)
    logs = destination / "logs"
    logs.mkdir()
    env = dict(os.environ)
    for name in ("LEAN_PATH", "LEAN_SRC_PATH", "LEAN_SYSROOT", "LAKE_HOME", "ELAN_TOOLCHAIN"):
        env.pop(name, None)
    env["ELAN_TOOLCHAIN"] = TOOLCHAIN
    env["MATHLIB_CACHE_DIR"] = str(destination / "mathlib-cache")
    env["MATHLIB_NO_CACHE_ON_UPDATE"] = "1"
    env.pop("MATHLIB_CACHE_GET_URL", None)
    env["GIT_TERMINAL_PROMPT"] = "0"
    config_count = int(env.get("GIT_CONFIG_COUNT", "0"))
    env["GIT_CONFIG_COUNT"] = str(config_count + 1)
    env[f"GIT_CONFIG_KEY_{config_count}"] = "core.longpaths"
    env[f"GIT_CONFIG_VALUE_{config_count}"] = "true"
    lean = shutil.which(str(lean)) or str(lean)
    lake = shutil.which(str(lake)) or str(lake)
    env["PATH"] = str(Path(lean).resolve().parent) + os.pathsep + env.get("PATH", "")

    def run(command, cwd, label, timeout=1200):
        return checked_run(command, cwd, logs, label, env, timeout)

    lean_version = run([lean, "--version"], destination, "lean-version", 30).stdout.strip()
    lake_version = run([lake, "--version"], destination, "lake-version", 30).stdout.strip()
    if not re.match(r"^Lean \(version 4\.35\.0(?:,|\))", lean_version) or not re.search(
        r"\(Lean version 4\.35\.0\)", lake_version
    ):
        raise RuntimeError("Lean and Lake must both use Lean 4.35.0")
    source = destination / "source"
    extract_reviewed(archive, files, source)
    analytic = source / "analytic"
    check_wheel(wheel, reviewed_root / "src/homometric_motion")
    environment = destination / "venv"
    venv.EnvBuilder(with_pip=True).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    run(
        [python, "-I", "-m", "pip", "install", "--no-index", "--no-deps", wheel],
        destination,
        "install-wheel",
        120,
    )
    work = destination / "reconstruction"
    work.mkdir()
    run(
        [
            python,
            "-I",
            "-m",
            "homometric_motion",
            "verify",
            "--scenario",
            "position_uncertainty",
            "--output",
            "position.json",
        ],
        work,
        "position-certificate",
        600,
    )
    run(
        [
            python,
            "-I",
            source / "generate_checkpoint.py",
            "position.json",
            "--output-dir",
            "position",
        ],
        work,
        "position-mapping",
        600,
    )
    for name in ("CertificateCheckpoint.lean", "statement_mapping.json"):
        if (work / "position" / name).read_bytes() != files["position_uncertainty/" + name]:
            raise RuntimeError("finite checkpoint differs from fresh installed reconstruction")
    run(
        [python, "-I", analytic / "build_nine_point_checkpoint.py", "--output-dir", "nine-point"],
        work,
        "nine-point-mapping",
        600,
    )
    for name in ("NinePointBezout.lean", "mapping.json"):
        if (work / "nine-point" / name).read_bytes() != files["analytic/" + name]:
            raise RuntimeError("nine-point checkpoint differs from fresh installed reconstruction")

    # Dependency preparation may use the network. All source replays below are local.
    run([lake, "exe", "cache", "get", *CACHE_MODULES], analytic, "dependency-cache", 3600)
    pins = dependency_pins(files["analytic/lake-manifest.json"])

    def check_dependencies(stage):
        for name, revision in pins.items():
            dependency = analytic / ".lake/packages" / name
            actual = run(
                ["git", "rev-parse", "HEAD"], dependency, f"{stage}-dependency-{name}", 30
            ).stdout.strip()
            if actual != revision:
                raise RuntimeError("Lake dependency revision mismatch: " + name)
            run(
                ["git", "diff", "--quiet", "HEAD", "--"],
                dependency,
                f"{stage}-dependency-clean-{name}",
                30,
            )

    check_dependencies("prepared")
    effective = run(
        [lake, "env", "lean", "--version"], analytic, "lake-lean-version", 30
    ).stdout.strip()
    if effective != lean_version:
        raise RuntimeError("Lake selected a different Lean toolchain")
    run([lake, "build"], analytic, "lake-build", 3600)
    check_sources(source, files)

    reports = {}
    for module, path in (
        ("CertificateCheckpoint", source / "position_uncertainty/CertificateCheckpoint.lean"),
        ("FactorialIdentities", source / "FactorialIdentities.lean"),
    ):
        result = run([lean, "--trust=0", path], source, module)
        reports[module] = check_axioms(module, result.stdout, result.stderr)
    for module in MODULES:
        output = Path(".lake/build/lib/lean") / (module + ".olean")
        result = run(
            [lake, "env", "lean", "--trust=0", "-o", output, module + ".lean"], analytic, module
        )
        reports[module] = check_axioms(module, result.stdout, result.stderr)
    check_sources(source, files)
    check_dependencies("replayed")
    receipt = {
        "status": "PASS",
        "scope": "Bounded Lean checkpoints and source mappings; not full-theorem formalization",
        "source_archive_sha256": digest(archive.read_bytes()),
        "wheel_sha256": digest(wheel.read_bytes()),
        "formal_source_sha256": {name: digest(raw) for name, raw in sorted(files.items())},
        "toolchain": TOOLCHAIN,
        "lean_version": lean_version,
        "lake_version": lake_version,
        "dependency_revisions": pins,
        "fresh_position_mapping_sha256": digest(
            (work / "position/statement_mapping.json").read_bytes()
        ),
        "fresh_nine_point_mapping_sha256": digest((work / "nine-point/mapping.json").read_bytes()),
        "replayed_sources": 11,
        "trust_level": 0,
        "trusted_imports": "Pinned Lean and mathlib compiled dependencies remain trusted",
        "axiom_reports": reports,
        "source_unchanged_after_replay": True,
    }
    (destination / "verification.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("archive", "wheel", "reviewed-root", "destination"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--lean", default="lean")
    parser.add_argument("--lake", default="lake")
    args = parser.parse_args()
    print(
        json.dumps(
            verify_archive(
                args.archive,
                args.wheel,
                args.reviewed_root,
                args.destination,
                lean=args.lean,
                lake=args.lake,
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
