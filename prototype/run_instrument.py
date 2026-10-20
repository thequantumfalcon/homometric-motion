"""Synthetic finite-beta instrument; numerical diagnostics are not model validation."""

import argparse
import csv
import hashlib
import json
import platform
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import eigh

HERE = Path(__file__).resolve().parent
CHECKS = []


def require(ok, name):
    if not ok:
        raise AssertionError(name)
    CHECKS.append(name)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scalar(text):
    return float(Fraction(text))


def center_value(row):
    return (scalar(row["lower"]) + scalar(row["upper"])) / 2


def phase(side):
    root3 = np.sqrt(3.0)
    ct, st = np.sqrt(74) / (5 * root3), 1 / (5 * root3)
    cp, sp = np.sqrt(191) / (8 * root3), -1 / (8 * root3)
    zeta = 0.5 + 1j * root3 / 2
    unit = []
    for j in range(10):
        unit += [
            complex((-1) ** j) if j < 2 else (-1) ** j * cp + 1j * sp,
            zeta * ((-1) ** j * ct + 1j * st),
        ]
    unit = np.array(unit + [1.0], dtype=np.complex128)
    multiplier = zeta if side == "A" else zeta * zeta
    z = np.concatenate((unit, multiplier * unit, -unit))
    require(
        abs(np.sum(z)) < 1e-12 and np.max(abs(abs(z) - 1)) < 1e-12,
        side + " float phase/null residual control",
    )
    return z


def graph(side, weights, nominal_trace):
    n = 63
    start = 20 if side == "A" else 41
    edges = [(i, i + 1) for i in range(n - 1)] + [(start, start + 2)]
    L = np.zeros((n, n))
    w = (
        np.ones(len(edges))
        if weights == "unit"
        else np.array([0.5 if i % 2 == 0 else 1.5 for i in range(len(edges))])
    )
    for (i, j), weight in zip(edges, w):
        L[i, i] += weight
        L[j, j] += weight
        L[i, j] -= weight
        L[j, i] -= weight
    lam, Q = eigh(L)
    require(
        abs(lam[0]) < 1e-12 and lam[1] > 0,
        side + weights + " projected positive spectrum",
    )
    lam, Q = lam[1:], Q[:, 1:]
    c = n / nominal_trace
    variances = c / lam
    D = (Q * variances) @ Q.T
    residual = np.max(abs(L @ D - c * (np.eye(n) - np.ones((n, n)) / n)))
    require(residual < 1e-10, side + weights + " covariance inverse residual")
    require(
        np.max(abs(Q.T @ Q - np.eye(n - 1))) < 1e-11,
        side + weights + " mode orthogonality",
    )
    return {
        "L": L,
        "lambda": lam,
        "Q": Q,
        "variances": variances,
        "D": D,
        "c": c,
        "covariance_inverse_residual_max": float(residual),
    }


def correlation(x):
    x = np.asarray(x)
    return float(np.corrcoef(x[:-1], x[1:])[0, 1])


def simulate_latent(rng, model, latent, lag, frames):
    variances = model["variances"]
    if latent == "rademacher_iid":
        modes = (2 * rng.integers(0, 2, size=(frames, 62)) - 1) * np.sqrt(variances)
    elif latent == "gaussian_iid":
        modes = rng.standard_normal((frames, 62)) * np.sqrt(variances)
    else:
        r = np.exp(-model["lambda"] * lag)
        noise_sd = np.sqrt(variances * (-np.expm1(-2 * model["lambda"] * lag)))
        eps = rng.standard_normal((frames, 62))
        modes = np.empty_like(eps)
        modes[0] = eps[0] * np.sqrt(variances)
        for t in range(1, frames):
            modes[t] = r * modes[t - 1] + noise_sd * eps[t]
        require(
            np.max(abs(r * r * variances + noise_sd * noise_sd - variances)) < 1e-11,
            "exact OU stationary variance transition",
        )
    return modes @ model["Q"].T


SOURCE_FILES = {
    "run_instrument.py",
    "inspect_run.py",
    "protocol.json",
    "reference.json",
    "requirements.txt",
    "README.md",
    "MODEL_AND_LIMITS.md",
    ".gitignore",
}
SCENARIO_SETTINGS = (
    ("iid_nominal", "B", "gaussian_iid", 1000, "unit", "fixed"),
    ("ou_short_lag", "B", "gaussian_ou", 1, "unit", "fixed"),
    ("ou_long_lag", "B", "gaussian_ou", 1000, "unit", "fixed"),
    ("finite_beta_stress", "0.01", "gaussian_ou", 1000, "unit", "fixed"),
    ("spring_misspecification", "B", "gaussian_iid", 1000, "alternating_0.5_1.5", "fixed"),
    ("nongaussian_same_covariance", "B", "rademacher_iid", 1000, "unit", "fixed"),
    ("gain_background_drift", "B", "gaussian_iid", 1000, "unit", "linear_drift"),
    ("correlated_channel_noise", "B", "gaussian_iid", 1000, "unit", "lognormal_AR1"),
)


def verify_manifest():
    manifest = json.loads((HERE / "source_manifest.json").read_text(encoding="utf-8"))
    require(
        manifest.get("schema_version") == 1
        and manifest.get("revision_kind") == "portable_synthetic_prototype_v2",
        "portable manifest schema and revision",
    )
    paths = [row.get("path") for row in manifest.get("files", [])]
    require(
        len(paths) == len(SOURCE_FILES) and set(paths) == SOURCE_FILES,
        "exact source allowlist",
    )
    for row in manifest["files"]:
        require(sha(HERE / row["path"]) == row["sha256"], "source hash " + row["path"])
    return manifest


def validate_reference(source):
    require(
        source.get("schema_version") == 1 and source.get("status") == "BOUND_PUBLIC_CORE_REFERENCE",
        "public reference schema",
    )
    origin = source["source"]
    require(
        origin["package"] == "homometric-motion" and origin["scenario"] == "exact_geometry",
        "public reference origin",
    )
    for key in ["certificate_sha256", "source_manifest_sha256"]:
        require(
            isinstance(origin[key], str)
            and len(origin[key]) == 64
            and all(c in "0123456789abcdef" for c in origin[key]),
            "public " + key,
        )
    fields = source["certificate"]
    require(Fraction(fields["beta_cap_exact"]) > 0, "positive exact beta cap")
    require(set(fields["classes"]) == {"A", "B"}, "reference classes")
    for side, trace in [("A", Fraction(121486, 189)), ("B", Fraction(121570, 189))]:
        cls = fields["classes"][side]
        require(Fraction(cls["trace_Lplus_exact"]) == trace, side + " exact trace invariant")
        ql, qu = [Fraction(cls["q"][key]) for key in ["lower", "upper"]]
        pl, pu = [Fraction(cls["abs_p_squared"][key]) for key in ["lower", "upper"]]
        require(
            0 < ql <= qu and 0 <= pl <= pu < ql * ql,
            side + " positive projected covariance reference",
        )


def write_summary(path, rows):
    fields = [
        "synthetic",
        "scenario",
        "class",
        "beta",
        "descriptive_flags",
        "nominal_whitened_covariance_frobenius_relative",
        "mean_modal_excess_kurtosis",
        "first_nominal_mode_lag1_correlation",
        "reference_channel_pearson_mean",
        "truth_channel_pearson_mean",
        "reference_channel_pearson_residual_lag1",
        "reference_channel_residual_second_minus_first_half_z",
        "finite_vs_leading_relative_RMS",
    ]
    with path.open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            values = {key: row["diagnostics"][key] for key in fields[5:]}
            values.update(
                synthetic=True,
                scenario=row["scenario"]["name"],
                **{"class": row["class"]},
                beta=row["beta_numeric"],
                descriptive_flags=";".join(row["descriptive_flags"]),
            )
            writer.writerow(values)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Synthetic virtual instrument; no physical validation."
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new output directory; existing paths are refused",
    )
    args = parser.parse_args(argv)
    if platform.python_implementation() != "CPython" or not (3, 11) <= sys.version_info[:2] < (
        3,
        14,
    ):
        raise ValueError("supported interpreter: conventional CPython >=3.11,<3.14")
    if np.__version__ != "2.2.6" or scipy.__version__ != "1.16.3":
        raise ValueError("install the pinned optional requirements.txt")
    CHECKS.clear()
    manifest = verify_manifest()
    protocol = json.loads((HERE / "protocol.json").read_text(encoding="utf-8"))
    source = json.loads((HERE / "reference.json").read_text(encoding="utf-8"))
    validate_reference(source)
    require(
        protocol["frames_per_class_scenario"] == 8192 and protocol["classes"] == ["A", "B"],
        "fixed frame/class contract",
    )
    require(protocol["root_seed"] == 202610200920, "fixed default seed")
    require(
        tuple(
            tuple(row[key] for key in ("name", "beta", "latent", "lag", "weights", "channel"))
            for row in protocol["scenarios"]
        )
        == SCENARIO_SETTINGS,
        "all eight declared scenarios and settings",
    )
    output = args.output.resolve()
    output.mkdir(parents=False, exist_ok=False)
    for name in ["protocol.json", "reference.json", "source_manifest.json"]:
        with (output / name).open("xb") as stream:
            stream.write((HERE / name).read_bytes())
    beta_B = scalar(source["certificate"]["beta_cap_exact"])
    omega = np.pi / 3
    nominal = {}
    for side in protocol["classes"]:
        src = source["certificate"]["classes"][side]
        model = graph(side, "unit", scalar(src["trace_Lplus_exact"]))
        z = phase(side)
        q = float(np.vdot(z, model["D"] @ z).real)
        p2 = float(abs(z @ (model["D"] @ z)) ** 2)
        require(
            abs(np.sum(1 / model["lambda"]) / scalar(src["trace_Lplus_exact"]) - 1) < 1e-9,
            side + " nominal pseudoinverse trace",
        )
        require(
            abs(q - center_value(src["q"])) < 1e-8
            and abs(p2 - center_value(src["abs_p_squared"])) < 1e-8,
            side + " projected q/p2 against retained enclosure midpoint",
        )
        model.update(z=z, q=q, p2=p2, leading_mean=omega**2 * q)
        nominal[side] = model
    gain = 10 / np.mean([m["leading_mean"] for m in nominal.values()])
    nframes = protocol["frames_per_class_scenario"]
    frame_dir = output / "frames"
    frame_dir.mkdir()
    rows = []
    for scenario_index, scenario in enumerate(protocol["scenarios"]):
        beta = beta_B if scenario["beta"] == "B" else scalar(scenario["beta"])
        for class_index, side in enumerate(protocol["classes"]):
            seed = [protocol["root_seed"], scenario_index, class_index]
            rng = np.random.Generator(np.random.PCG64(np.random.SeedSequence(seed)))
            base = nominal[side]
            actual = (
                base
                if scenario["weights"] == "unit"
                else graph(
                    side,
                    scenario["weights"],
                    scalar(source["certificate"]["classes"][side]["trace_Lplus_exact"]),
                )
            )
            Y = simulate_latent(rng, actual, scenario["latent"], scenario["lag"], nframes)
            com = float(np.max(abs(np.mean(Y, axis=1))))
            require(com < 1e-11, "zero COM numerical control " + scenario["name"] + side)
            angle = omega * np.sqrt(beta) * Y
            amplitude = np.sum(np.expm1(1j * angle) * base["z"], axis=1)
            direct = np.sum(np.exp(1j * angle) * base["z"], axis=1)
            direct_difference = float(np.max(abs(amplitude - direct)))
            require(
                direct_difference < 1e-11,
                "stable/direct amplitude control " + scenario["name"] + side,
            )
            J = abs(amplitude) ** 2 / beta
            Jleading = omega**2 * abs(Y @ base["z"]) ** 2
            require(
                np.all(np.isfinite(J)) and np.min(J) >= 0,
                "finite nonnegative exact-observable evaluation",
            )
            reference_rate = gain * J + 1
            actual_gain_multiplier = np.ones(nframes)
            actual_background = np.ones(nframes)
            if scenario["channel"] == "linear_drift":
                actual_gain_multiplier = np.linspace(0.8, 1.2, nframes)
                actual_background = np.linspace(0.0, 2.0, nframes)
            elif scenario["channel"] == "lognormal_AR1":
                eta = np.empty(nframes)
                eta[0] = 0.2 * rng.standard_normal()
                innovations = 0.2 * np.sqrt(1 - 0.95**2) * rng.standard_normal(nframes - 1)
                for t in range(1, nframes):
                    eta[t] = 0.95 * eta[t - 1] + innovations[t - 1]
                actual_gain_multiplier = np.exp(eta - 0.02)
            actual_rate = gain * actual_gain_multiplier * J + actual_background
            counts = rng.poisson(actual_rate)
            whitened = (Y @ base["Q"]) / np.sqrt(base["variances"])
            sample_cov = np.cov(whitened, rowvar=False, ddof=1)
            centered = whitened - np.mean(whitened, axis=0)
            modal2 = np.mean(centered**2, axis=0)
            excess = np.mean(centered**4, axis=0) / (modal2 * modal2) - 3
            reference_residual = (counts - reference_rate) / np.sqrt(reference_rate)
            actual_residual = (counts - actual_rate) / np.sqrt(actual_rate)
            half = nframes // 2
            drift_z = float(
                (np.mean(reference_residual[half:]) - np.mean(reference_residual[:half]))
                / np.sqrt(2 / half)
            )
            diagnostics = {
                "nominal_whitened_covariance_frobenius_relative": float(
                    np.linalg.norm(sample_cov - np.eye(62), "fro") / np.sqrt(62)
                ),
                "mean_modal_excess_kurtosis": float(np.mean(excess)),
                "first_nominal_mode_lag1_correlation": correlation(whitened[:, 0]),
                "intensity_lag1_correlation": correlation(J),
                "count_lag1_correlation": correlation(counts),
                "reference_channel_pearson_mean": float(np.mean(reference_residual**2)),
                "truth_channel_pearson_mean": float(np.mean(actual_residual**2)),
                "reference_channel_pearson_residual_lag1": correlation(reference_residual),
                "reference_channel_residual_second_minus_first_half_z": drift_z,
                "finite_vs_leading_relative_RMS": float(
                    np.sqrt(np.mean((J - Jleading) ** 2) / np.mean(Jleading**2))
                ),
                "finite_intensity_sample_mean": float(np.mean(J)),
                "leading_intensity_sample_mean": float(np.mean(Jleading)),
                "count_sample_mean": float(np.mean(counts)),
                "actual_rate_sample_mean": float(np.mean(actual_rate)),
            }
            flags = protocol["descriptive_flags_not_hypothesis_tests"]
            flagged = []
            for key, value in diagnostics.items():
                if key + "_above" in flags and value > flags[key + "_above"]:
                    flagged.append(key)
                if key + "_absolute_above" in flags and abs(value) > flags[key + "_absolute_above"]:
                    flagged.append(key)
                if key + "_outside" in flags:
                    lo, hi = flags[key + "_outside"]
                    if not lo <= value <= hi:
                        flagged.append(key)
            distance_variance = (
                np.diag(actual["D"])[:, None] + np.diag(actual["D"])[None, :] - 2 * actual["D"]
            )
            gaussian_mean = float(
                np.sum(
                    (base["z"][:, None] * base["z"].conj()[None, :]).real
                    * np.expm1(-0.5 * omega**2 * beta * distance_variance)
                )
                / beta
            )
            expected_rho = (
                float(np.exp(-actual["lambda"][0] * scenario["lag"]))
                if scenario["latent"] == "gaussian_ou" and scenario["weights"] == "unit"
                else 0.0
                if scenario["latent"] != "gaussian_ou"
                else None
            )
            name = scenario["name"] + "_" + side + ".npz"
            target = frame_dir / name
            with target.open("xb") as stream:
                np.savez_compressed(
                    stream,
                    synthetic=np.array(True),
                    class_label=np.array(side),
                    scenario=np.array(scenario["name"]),
                    seed_tuple=np.array(seed, dtype=np.uint64),
                    dimensionless_time=np.arange(nframes) * scenario["lag"],
                    normalized_finite_intensity=J,
                    normalized_leading_intensity=Jleading,
                    counts=counts,
                    reference_rate=reference_rate,
                    actual_rate=actual_rate,
                    actual_gain_multiplier=actual_gain_multiplier,
                    actual_background=actual_background,
                    nominal_whitened_modes=whitened,
                )
            rows.append(
                {
                    "synthetic": True,
                    "scenario": scenario,
                    "class": side,
                    "seed_tuple": seed,
                    "frames": nframes,
                    "beta_numeric": beta,
                    "common_gain_on_J": float(gain),
                    "diagnostics": diagnostics,
                    "descriptive_flags": flagged,
                    "flags_are_not_calibrated_tests": True,
                    "nominal_whitened_sample_covariance": sample_cov.tolist(),
                    "modal_excess_kurtosis": excess.tolist(),
                    "gaussian_finite_mean_reference": gaussian_mean,
                    "gaussian_reference_is_actual_latent_model": scenario["latent"]
                    != "rademacher_iid",
                    "expected_first_nominal_mode_lag1": expected_rho,
                    "numeric_controls": {
                        "COM_max_abs": com,
                        "stable_vs_direct_amplitude_max_abs": direct_difference,
                        "covariance_inverse_residual_max": actual[
                            "covariance_inverse_residual_max"
                        ],
                    },
                    "frame_artifact": {
                        "path": "frames/" + name,
                        "sha256": sha(target),
                        "bytes": target.stat().st_size,
                    },
                    "truth_disclosure": "The generating latent and channel settings are known because this is synthetic data.",
                }
            )
            print(
                json.dumps({"scenario": scenario["name"], "class": side, "flags": flagged}),
                flush=True,
            )
    for row in manifest["files"]:
        require(sha(HERE / row["path"]) == row["sha256"], "unchanged " + row["path"])
    result = {
        "status": "COMPLETED_SYNTHETIC_PROTOTYPE",
        "synthetic": True,
        "revision_kind": "portable_synthetic_prototype_v2",
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "total_frames": len(rows) * nframes,
        "scenarios_and_classes": rows,
        "checks": {"count": len(CHECKS), "passed": CHECKS},
        "bindings": {r["path"]: r["sha256"] for r in manifest["files"]},
        "source_manifest_sha256": sha(HERE / "source_manifest.json"),
        "reference_certificate_sha256": source["source"]["certificate_sha256"],
        "qualification": "Synthetic mechanism exercise, not empirical validation, finite-error classification, calibrated hypothesis testing or hardware readiness.",
    }
    with (output / "result.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    write_summary(output / "summary.csv", rows)
    print(
        json.dumps(
            {
                "status": result["status"],
                "numerical_controls": len(CHECKS),
                "frames": result["total_frames"],
            }
        )
    )


if __name__ == "__main__":
    try:
        main()
    except (
        OSError,
        ValueError,
        ArithmeticError,
        KeyError,
        TypeError,
        AssertionError,
    ) as exc:
        print(f"Prototype failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
