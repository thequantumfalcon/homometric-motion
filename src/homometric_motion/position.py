"""Fixed position offsets combined with the original exposure baseline."""

from fractions import Fraction as F

from .arithmetic import Interval as I


def position_certificate(joint, nominal, frequency, rho, check):
    """Bound fixed offsets uniformly, including their frequency interaction.

    The zero-offset case is supported as an exact regression control. This
    calculation starts from the original joint exposure law, not the already
    perturbed frequency intensity law.
    """
    rho = F(rho)
    check(0 <= 2 * rho < F(1, 4), "position errors preserve mean contact topology")
    check(frequency["status"] == "CERTIFIED_SEPARATED", "position baseline separates")
    check(
        F(joint["beta_cap_exact"]) == F(nominal["beta_cap_exact"]),
        "position baseline strength agrees",
    )
    for key in ("epsilon_exact", "exposure_cap_exact", "edge_weight_radius_exact"):
        check(F(joint[key]) == F(frequency[key]), "position family agrees " + key)
    roots = []

    def root(x, degree, label):
        x = F(x)
        value = I(x).root(degree)
        lo, hi = value.lower, value.upper
        check(0 <= lo and lo**degree <= x <= hi**degree, "position root " + label)
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
        check(lo <= hi, "ordered position input interval")
        return lo, hi

    def record(lo, hi):
        check(lo <= hi, "ordered position output interval")
        return {
            "lower": str(lo),
            "upper": str(hi),
            "decimal_display_only": [float(lo), float(hi)],
        }

    beta_min = F(frequency["beta_band_exact"]["lower"])
    beta_max = F(frequency["beta_band_exact"]["upper"])
    check(0 < beta_min == beta_max / 2, "positive position strength floor")
    check(beta_max == F(nominal["beta_cap_exact"]), "position strength cap agrees")
    detuning = F(frequency["frequency_error_cap_exact"])
    omega_l, omega_u = pair(nominal["omega"])
    check(0 < detuning < omega_l, "positive position frequency range")
    sqrt_beta_lower = root(beta_min, 2, "strength floor")[0]
    check(sqrt_beta_lower > 0, "positive position amplitude denominator")
    coefficient = (omega_u + detuning) * 63 / sqrt_beta_lower
    qpos = coefficient * rho
    classes = {}
    for side in ("A", "B"):
        base = joint["classes"][side]
        previous = frequency["classes"][side]
        raw = {r: F(base["normalized_raw_moment_upper_bounds"][str(r)]) for r in range(1, 7)}
        vl0, vu0 = pair(base["normalized_variance"])
        kl0, ku0 = pair(base["normalized_third_cumulant"])
        check(vl0 > 0, side + " positive position baseline variance")
        sd_l = root(vl0, 2, side + " baseline SD lower")[0]
        sd_u = root(vu0, 2, side + " baseline SD upper")[1]
        amplitude = {
            r: root(raw[r], 2 * r, side + " baseline amplitude " + str(r))[1] for r in range(1, 7)
        }
        p = F(previous["nominal_amplitude_L6_upper_exact"])
        m = F(previous["baseline_centered_L3_upper_exact"])
        qfreq = F(previous["frequency_amplitude_difference_L6_upper_exact"])
        qr = {r: F(previous["amplitude_difference_norm_upper_by_r"][str(r)]) for r in range(1, 7)}
        check(
            p == min(F(previous["global_amplitude_L6_upper_exact"]), amplitude[3]),
            side + " position baseline amplitude agrees",
        )
        check(qfreq == qr[3], side + " frequency L6 errors agree")
        check(
            m
            == min(
                F(previous["baseline_centered_L3_basic_exact"]),
                F(previous["baseline_centered_L3_interpolated_exact"]),
            ),
            side + " position baseline centered norm agrees",
        )
        qtotal = qfreq + qpos
        delta = 2 * p * qtotal + qtotal * qtotal
        centered_error = 2 * delta
        error3 = 3 * m * m * centered_error + 3 * m * centered_error**2 + centered_error**3
        vl, vu = max(F(0), sd_l - delta) ** 2, (sd_u + delta) ** 2
        kl, ku = kl0 - error3, ku0 + error3
        check(vl > 0, side + " positive position-robust variance")
        dl = vl * root(vl, 2, side + " actual SD lower")[0]
        du = vu * root(vu, 2, side + " actual SD upper")[1]
        check(0 < dl <= du, side + " positive position skewness denominator")
        ratios = [kl / dl, kl / du, ku / dl, ku / du]
        raw_actual = {str(r): str((amplitude[r] + qr[r] + qpos) ** (2 * r)) for r in range(1, 7)}
        classes[side] = {
            "nominal_amplitude_L6_upper_exact": str(p),
            "frequency_amplitude_L6_error_upper_exact": str(qfreq),
            "position_amplitude_error_upper_exact": str(qpos),
            "total_amplitude_L6_error_upper_exact": str(qtotal),
            "total_intensity_L3_error_upper_exact": str(delta),
            "centered_L3_error_upper_exact": str(centered_error),
            "baseline_centered_L3_upper_exact": str(m),
            "third_cumulant_change_upper_exact": str(error3),
            "normalized_variance": record(vl, vu),
            "normalized_third_cumulant": record(kl, ku),
            "skewness": record(min(ratios), max(ratios)),
            "normalized_raw_moment_upper_bounds": raw_actual,
        }
        if rho == 0:
            for key in ("normalized_variance", "normalized_third_cumulant", "skewness"):
                check(
                    classes[side][key] == previous[key],
                    side + " zero-position equality " + key,
                )
            check(
                raw_actual == previous["normalized_raw_moment_upper_bounds"],
                side + " zero-position raw moment equality",
            )
    gap = F(classes["B"]["skewness"]["lower"]) - F(classes["A"]["skewness"]["upper"])
    check(gap > 0, "combined position and frequency shape separation")
    return {
        "status": "CERTIFIED_SEPARATED",
        "position_error_cap_exact": str(rho),
        "frequency_error_cap_exact": str(detuning),
        "beta_band_exact": frequency["beta_band_exact"],
        "common_alpha_band_exact": frequency["common_alpha_band_exact"],
        "epsilon_exact": joint["epsilon_exact"],
        "edge_weight_radius_exact": joint["edge_weight_radius_exact"],
        "exposure_cap_exact": joint["exposure_cap_exact"],
        "position_amplitude_error_coefficient_upper_exact": str(coefficient),
        "mean_contact_threshold_exact": "5/2",
        "nominal_mean_contact_margin_strict_lower_exact": "1/4",
        "mean_contact_remaining_margin_strict_lower_exact": str(F(1, 4) - 2 * rho),
        "classes": classes,
        "signed_gap_exact": str(gap),
        "gap_display_only": float(gap),
        "root_certificates": roots,
        "scope": (
            "Fixed mean offsets about the nominal templates with unchanged permanent "
            "contact graphs; actual configurations need not remain clean-homometric."
        ),
    }
