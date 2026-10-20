"""Exposure and fixed-frequency error bounds for weighted stationary OU motion."""

from fractions import Fraction as F

from .arithmetic import Interval as I


def interval(row):
    return I.bounds(F(row["lower"]), F(row["upper"]))


def overlap(a, b):
    return max(a.lower, b.lower) <= min(a.upper, b.upper)


def exposure_class_bounds(side, marginal, trace_nominal, epsilon, exposure, omega, check):
    n = 63
    v = interval(marginal["normalized_variance"])
    k3 = interval(marginal["normalized_third_cumulant"])
    raw = {r: F(marginal["normalized_raw_moment_upper_bounds"][str(r)]) for r in range(1, 7)}
    trace_upper = n * (1 + epsilon)
    increment_slope = F(2 * n * (n - 1)) / trace_nominal
    delta_interval = (
        F(4, 3) * omega**2 * n * I(15).root(3) * I(trace_upper * increment_slope * exposure).root(2)
    )
    alternative = (
        F(4, 3)
        * omega**2
        * n
        * n
        * I(15).root(3)
        * I(F(2 * (n - 1)) * (1 + epsilon) * exposure / trace_nominal).root(2)
    )
    check(
        overlap(delta_interval, alternative),
        side + " equivalent exposure error formulas",
    )
    delta = delta_interval.upper
    m_basic = 2 * I(raw[3]).root(3)
    fourth_center_upper = raw[4] + 6 * raw[1] ** 2 * raw[2]
    m_interpolated = I(v.upper * fourth_center_upper).root(6)
    m = min(m_basic.upper, m_interpolated.upper)
    check(m > 0 and delta >= 0, side + " nonnegative perturbation constants")
    sd = v.root(2)
    lower_base = max(F(0), sd.lower - delta)
    variance = I.bounds(lower_base**2, v.upper)
    # E(barJ-J0)=0 by stationarity. No generic L3 centering factor is needed.
    error3 = (3 * I(m) ** 2 * delta + 3 * I(m) * delta**2 + I(delta) ** 3).upper
    third = I.bounds(k3.lower - error3, k3.upper + error3)
    check(variance.lower > 0, side + " positive finite-exposure variance")
    check(third.lower > 0, side + " positive finite-exposure third cumulant")
    skew = third / (variance * variance.root(2))
    check(variance.upper <= v.upper, side + " stationary Jensen variance cap")
    return {
        "normalized_variance": variance.record(),
        "normalized_third_cumulant": third.record(),
        "skewness": skew.record(),
        "normalized_raw_moment_upper_bounds": {str(r): str(raw[r]) for r in raw},
        "trace_upper_exact": str(trace_upper),
        "increment_trace_slope_upper_exact": str(increment_slope),
        "exposure_L3_error_upper_exact": str(delta),
        "centered_L3_norm_upper_exact": str(m),
        "centered_L3_basic_upper_exact": str(m_basic.upper),
        "centered_L3_interpolated_upper_exact": str(m_interpolated.upper),
        "centered_fourth_moment_upper_exact": str(fourth_center_upper),
        "third_cumulant_error_upper_exact": str(error3),
    }


def exposure_certificate(nominal, covariance, exposure, check):
    """Combine relative covariance uncertainty with a positive exposure cap."""
    exposure = F(exposure)
    epsilon = F(covariance["epsilon_exact"])
    check(exposure > 0, "positive exposure cap")
    omega = interval(nominal["omega"])
    classes = {
        side: exposure_class_bounds(
            side,
            covariance["classes"][side],
            F(nominal["classes"][side]["trace_Lplus_exact"]),
            epsilon,
            exposure,
            omega,
            check,
        )
        for side in ("A", "B")
    }
    gap = F(classes["B"]["skewness"]["lower"]) - F(classes["A"]["skewness"]["upper"])
    check(gap > 0, "joint covariance and exposure skewness separation")
    return {
        "beta_cap_exact": nominal["beta_cap_exact"],
        "epsilon_exact": str(epsilon),
        "edge_weight_radius_exact": str(epsilon / (1 + epsilon)),
        "exposure_cap_exact": str(exposure),
        "classes": classes,
        "separated": True,
        "gap_lower_exact": str(gap),
        "scope": "Fixed positive spring weights and compatible stationary OU dynamics; positive exposure.",
    }


def frequency_certificate(joint, nominal, marginal, detuning, check):
    """Propagate a fixed frequency error with the essential positive beta floor."""
    roots = []

    def root(x, degree, label):
        x = F(x)
        r = I(x).root(degree)
        lo, hi = r.lower, r.upper
        check(0 <= lo and lo**degree <= x <= hi**degree, "root powers " + label)
        roots.append(
            {
                "label": label,
                "degree": degree,
                "radicand": str(x),
                "lower": str(lo),
                "upper": str(hi),
            }
        )
        return lo, hi

    def pair(row):
        lo, hi = F(row["lower"]), F(row["upper"])
        check(lo <= hi, "ordered frequency input interval")
        return lo, hi

    def record(lo, hi):
        check(lo <= hi, "ordered frequency output interval")
        return {
            "lower": str(lo),
            "upper": str(hi),
            "decimal_display_only": [float(lo), float(hi)],
        }

    epsilon = F(joint["epsilon_exact"])
    exposure = F(joint["exposure_cap_exact"])
    check(F(marginal["epsilon_exact"]) == epsilon, "matching covariance families")
    baseline = joint
    marginal_cell = marginal
    cap = F(nominal["beta_cap_exact"])
    check(cap == F(joint["beta_cap_exact"]) and cap > 0, "common positive strength cap")
    beta_min = cap / 2
    n = 63
    trace_upper = F(n) * (1 + epsilon)
    omega_l, omega_u = pair(nominal["omega"])
    grid = [F(detuning)]
    check(0 < grid[0] < omega_l, "positive fixed frequency-error cap")
    sqrt_beta_l = root(beta_min, 2, "positive strength floor")[0]
    check(sqrt_beta_l > 0, "nonzero floor denominator")
    sqrt_n_u = root(F(n), 2, "sqrt dimension")[1]
    sqrt_trace_u = root(trace_upper, 2, "sqrt covariance trace bound")[1]
    geometry_coefficient = F(n * 94) / sqrt_beta_l
    H = {}
    for r in range(1, 7):
        gaussian_moment = 1
        for k in range(1, 2 * r, 2):
            gaussian_moment *= k
        H[r] = root(F(gaussian_moment), 2 * r, "Gaussian radial norm " + str(r))[1] * sqrt_trace_u
    P_global = omega_u * sqrt_n_u * H[3]
    data_by_class = {}
    c_values = {}
    for label in ["A", "B"]:
        inp = baseline["classes"][label]
        marginal_inp = marginal_cell["classes"][label]
        raw = {r: F(inp["normalized_raw_moment_upper_bounds"][str(r)]) for r in range(1, 7)}
        check(
            all(
                raw[r] == F(marginal_inp["normalized_raw_moment_upper_bounds"][str(r)])
                for r in range(1, 7)
            ),
            label + " marginal and exposure raw bounds agree",
        )
        check(F(inp["trace_upper_exact"]) == trace_upper, label + " trace bound agrees")
        v_l, v_u = pair(inp["normalized_variance"])
        k_l, k_u = pair(inp["normalized_third_cumulant"])
        check(v_l > 0 and all(x > 0 for x in raw.values()), label + " positive baseline")
        sd_l = root(v_l, 2, label + " baseline SD lower")[0]
        sd_u = root(v_u, 2, label + " baseline SD upper")[1]
        amplitude = {
            r: root(raw[r], 2 * r, label + " nominal amplitude norm " + str(r))[1]
            for r in range(1, 7)
        }
        P = min(P_global, amplitude[3])
        central4 = raw[4] + 6 * raw[1] ** 2 * raw[2]
        M_basic = 2 * root(raw[3], 3, label + " centered L3 basic")[1]
        M_interpolation = root(v_u * central4, 6, label + " centered L3 interpolation")[1]
        M = min(M_basic, M_interpolation)
        trace = F(nominal["classes"][label]["trace_Lplus_exact"])
        c_values[label] = F(n) / trace
        data_by_class[label] = {
            "raw": raw,
            "v_l": v_l,
            "v_u": v_u,
            "k_l": k_l,
            "k_u": k_u,
            "sd_l": sd_l,
            "sd_u": sd_u,
            "amplitude": amplitude,
            "P": P,
            "M": M,
            "M_basic": M_basic,
            "M_interpolation": M_interpolation,
            "central4": central4,
        }
    alpha_l = beta_min * max(c_values.values())
    alpha_u = cap * min(c_values.values())
    check(0 < alpha_l <= alpha_u, "nonempty positive common-alpha band")
    for label, c in c_values.items():
        check(
            alpha_l / c >= beta_min and alpha_u / c <= cap,
            label + " common-alpha beta inclusion",
        )
    cells = []
    for d in grid:
        classes = {}
        skew = {}
        for label in ["A", "B"]:
            base = data_by_class[label]
            Q = d * (geometry_coefficient + sqrt_n_u * H[3])
            delta = 2 * base["P"] * Q + Q * Q
            e = 2 * delta
            M = base["M"]
            error3 = 3 * M * M * e + 3 * M * e * e + e**3
            vl = max(F(0), base["sd_l"] - delta) ** 2
            vu = (base["sd_u"] + delta) ** 2
            kl, ku = base["k_l"] - error3, base["k_u"] + error3
            skew_record = None
            if vl > 0:
                dl = vl * root(vl, 2, label + " detuned SD lower " + str(d))[0]
                du = vu * root(vu, 2, label + " detuned SD upper " + str(d))[1]
                check(0 < dl <= du, label + " positive detuned skew denominator")
                choices = [kl / dl, kl / du, ku / dl, ku / du]
                sl, su = min(choices), max(choices)
                skew[label] = (sl, su)
                skew_record = record(sl, su)
            raw_detuned = {}
            Qr = {}
            for r in range(1, 7):
                qr = d * (geometry_coefficient + sqrt_n_u * H[r])
                Qr[str(r)] = str(qr)
                new_raw = (base["amplitude"][r] + qr) ** (2 * r)
                check(new_raw >= base["raw"][r], label + " enlarged raw moment " + str(r))
                raw_detuned[str(r)] = str(new_raw)
            classes[label] = {
                "nominal_amplitude_L6_upper_exact": str(base["P"]),
                "global_amplitude_L6_upper_exact": str(P_global),
                "moment_amplitude_L6_upper_exact": str(base["amplitude"][3]),
                "frequency_amplitude_difference_L6_upper_exact": str(Q),
                "frequency_intensity_L3_difference_upper_exact": str(delta),
                "centered_difference_L3_upper_exact": str(e),
                "baseline_centered_L3_upper_exact": str(M),
                "baseline_centered_L3_basic_exact": str(base["M_basic"]),
                "baseline_centered_L3_interpolated_exact": str(base["M_interpolation"]),
                "baseline_centered_fourth_upper_exact": str(base["central4"]),
                "third_cumulant_change_upper_exact": str(error3),
                "normalized_variance": record(vl, vu),
                "normalized_third_cumulant": record(kl, ku),
                "skewness": skew_record,
                "normalized_raw_moment_upper_bounds": raw_detuned,
                "amplitude_difference_norm_upper_by_r": Qr,
            }
        gap = skew["B"][0] - skew["A"][1] if len(skew) == 2 else None
        separated = gap is not None and gap > 0
        cells.append(
            {
                "frequency_error_cap_exact": str(d),
                "frequency_error_cap_display_only": float(d),
                "status": "CERTIFIED_SEPARATED" if separated else "UNRESOLVED_BY_THIS_BOUND",
                "classes": classes,
                "signed_gap_exact": str(gap) if gap is not None else None,
                "gap_display_only": float(gap) if gap is not None else None,
            }
        )
    selected = cells[0]
    check(selected["status"] == "CERTIFIED_SEPARATED", "frequency-robust shape separation")
    return {
        "beta_band_exact": {"lower": str(beta_min), "upper": str(cap)},
        "epsilon_exact": str(epsilon),
        "exposure_cap_exact": str(exposure),
        "edge_weight_radius_exact": str(epsilon / (1 + epsilon)),
        "common_alpha_band_exact": {"lower": str(alpha_l), "upper": str(alpha_u)},
        "trace_upper_exact": str(trace_upper),
        "geometry_abs_sum_upper_exact": str(n * 94),
        "inverse_sqrt_beta_floor_geometry_upper_exact": str(geometry_coefficient),
        "radial_norm_upper_by_r": {str(r): str(v) for r, v in H.items()},
        "root_certificates": roots,
        **selected,
        "scope": "Fixed geometry and frequency; beta in [B/2,B]; compatible weighted OU motion and positive exposure.",
    }
