"""Uniform finite-motion moments at the exact phase null."""

from fractions import Fraction as F
from math import comb, factorial

from .arithmetic import Interval, interval_controls
from .geometry import (
    direct_phases,
    energy_moments,
    exact_covariance,
    full_contractions,
    moment_recursion,
)


def certificate_for_class(side, z, omega, cap, check):
    covariance, trace_lp = exact_covariance(side, check)
    traces, energy = energy_moments(covariance, check)
    q, p2, real_p, imag_p = full_contractions(z, covariance, check)
    cumulants = {
        k: factorial(k - 1)
        * sum(comb(k, 2 * j) * q ** (k - 2 * j) * p2**j for j in range(k // 2 + 1))
        for k in range(1, 7)
    }
    moments = moment_recursion(cumulants, 6)
    center4 = 9 * q**4 + 42 * q**2 * p2 + 9 * p2**2
    v0, k30 = omega**4 * (q**2 + p2), omega**6 * (2 * q**3 + 6 * q * p2)
    diag_sum = sum(
        Interval(covariance[i][i]) ** 1 * Interval(covariance[i][i]).root(2) for i in range(63)
    )
    s4 = omega * (2 * q**2 + p2).root(4)
    c4 = omega**2 * Interval(energy[4]).root(4) / 2
    e4 = omega**3 * Interval(10395).root(4) * diag_sum / 6
    s6 = omega * (6 * q**3 + 9 * q * p2).root(6)
    c6 = omega**2 * Interval(energy[6]).root(6) / 2
    e6 = omega**3 * Interval(34459425).root(6) * diag_sum / 6
    x3 = (v0 * omega**8 * center4).root(6)
    B = Interval(cap)
    even2 = B * (2 * s4 * e4 + c4**2) + B**2 * e4**2
    odd2 = 4 * B * c4**2 * (s4 + B * e4) ** 2
    sd0 = v0.root(2)
    check(sd0.lower > even2.upper, side + " positive variance lower margin")
    variance = Interval.bounds((sd0.lower - even2.upper) ** 2, ((sd0 + even2) ** 2 + odd2).upper)
    even3 = 2 * B * (2 * s6 * e6 + c6**2) + 2 * B**2 * e6**2
    odd3 = 4 * B * c6**2 * (s6 + B * e6) ** 2
    error3 = 3 * x3**2 * even3 + 3 * x3 * even3**2 + even3**3 + 3 * (x3 + even3) * odd3
    third = Interval.bounds(k30.lower - error3.upper, k30.upper + error3.upper)
    check(variance.lower > 0 and third.lower > 0, side + " positive cumulants")
    skew = third / (variance * variance.root(2))
    raw_bounds = {}
    for r in range(1, 7):
        norm_bound = omega * moments[r].root(2 * r) + (
            omega**2 * B.root(2) * Interval(energy[2 * r]).root(2 * r) / 2
        )
        raw_bounds[str(r)] = str((norm_bound ** (2 * r)).upper)
    return {
        "trace_Lplus_exact": str(trace_lp),
        "covariance_traces_exact": {str(k): str(v) for k, v in traces.items()},
        "energy_raw_moments_exact": {str(k): str(v) for k, v in energy.items()},
        "q": q.record(),
        "real_p": real_p.record(),
        "imag_p": imag_p.record(),
        "abs_p_squared": p2.record(),
        "leading_variance": v0.record(),
        "leading_third_cumulant": k30.record(),
        "normalized_variance": variance.record(),
        "normalized_third_cumulant": third.record(),
        "skewness": skew.record(),
        "normalized_raw_moment_upper_bounds": raw_bounds,
        "error_upper_bounds": {
            "even_L2": str(even2.upper),
            "odd_L2_squared": str(odd2.upper),
            "centered_even_L3": str(even3.upper),
            "odd_L3_squared": str(odd3.upper),
            "third_cumulant": str(error3.upper),
        },
    }


def nominal_certificate(cap, check):
    """Recompute the exact-null certificate from geometry, without saved results."""
    cap = F(cap)
    check(F(1, 10**11) < cap < F(2, 10**11), "fixed strength cap sanity")
    omega = interval_controls(check)
    check(omega.lower > 1, "frequency lower bound for geometric shifts")
    phases = direct_phases(check)
    classes = {
        side: certificate_for_class(side, phases[side], omega, cap, check) for side in ("A", "B")
    }
    gap = F(classes["B"]["skewness"]["lower"]) - F(classes["A"]["skewness"]["upper"])
    check(gap > F(2342, 10**6), "strict nominal uniform skewness separation")
    common_alpha = F(63) * cap / max(F(row["trace_Lplus_exact"]) for row in classes.values())
    return {
        "beta_cap_exact": str(cap),
        "domain": "independent 0 < beta_A,beta_B <= B",
        "normalization": "J=I/beta; variance and third cumulant refer to J",
        "omega": omega.record(),
        "classes": classes,
        "ordering": "A < B",
        "skewness_gap_lower_exact": str(gap),
        "common_alpha_cap_exact": str(common_alpha),
        "arithmetic": "Outward integer intervals on a 10^-72 grid and exact rational graph algebra.",
    }


def covariance_certificate(nominal, epsilon, check):
    """Enclose every covariance in the declared relative Loewner family."""
    B = Interval(F(nominal["beta_cap_exact"]))

    def interval(row):
        return Interval.bounds(F(row["lower"]), F(row["upper"]))

    omega = interval(nominal["omega"])
    diagonal = {}
    for side in ("A", "B"):
        D, trace = exact_covariance(side, check)
        check(
            str(trace) == nominal["classes"][side]["trace_Lplus_exact"],
            side + " exact reconstructed trace",
        )
        diagonal[side] = sum(Interval(D[i][i]) * Interval(D[i][i]).root(2) for i in range(63))
    cells = []
    for text in (str(epsilon),):
        eps = F(text)
        check(0 <= eps < 1, text + " admissible perturbation")
        classes = {}
        for side in ("A", "B"):
            base = nominal["classes"][side]
            baseq = interval(base["q"])
            basep = interval(base["abs_p_squared"]).root(2)
            q = Interval.bounds((1 - eps) * baseq.lower, (1 + eps) * baseq.upper)
            p = Interval.bounds(
                max(F(0), basep.lower - eps * baseq.upper),
                basep.upper + eps * baseq.upper,
            )
            p2 = p**2
            energy = {
                k: Interval(F(base["energy_raw_moments_exact"][str(k)])) * (1 + eps) ** k
                for k in range(1, 13)
            }
            diagonal_bound = diagonal[side] * (Interval(1 + eps) ** 3).root(2)
            cumulants = {
                k: factorial(k - 1)
                * sum(comb(k, 2 * j) * q ** (k - 2 * j) * p2**j for j in range(k // 2 + 1))
                for k in range(1, 7)
            }
            moments = moment_recursion(cumulants, 6)
            v0 = omega**4 * (q**2 + p2)
            k30 = omega**6 * (2 * q**3 + 6 * q * p2)
            m4c = omega**8 * (9 * q**4 + 42 * q**2 * p2 + 9 * p2**2)
            s4 = omega * (2 * q**2 + p2).root(4)
            s6 = omega * (6 * q**3 + 9 * q * p2).root(6)
            c4 = omega**2 * energy[4].root(4) / 2
            c6 = omega**2 * energy[6].root(6) / 2
            e4 = omega**3 * Interval(10395).root(4) * diagonal_bound / 6
            e6 = omega**3 * Interval(34459425).root(6) * diagonal_bound / 6
            even2 = B * (2 * s4 * e4 + c4**2) + B**2 * e4**2
            odd2 = 4 * B * c4**2 * (s4 + B * e4) ** 2
            sd0 = v0.root(2)
            check(sd0.lower > even2.upper, text + side + " positive SD margin")
            variance = Interval.bounds(
                (sd0.lower - even2.upper) ** 2, ((sd0 + even2) ** 2 + odd2).upper
            )
            even3 = 2 * B * (2 * s6 * e6 + c6**2) + 2 * B**2 * e6**2
            odd3 = 4 * B * c6**2 * (s6 + B * e6) ** 2
            x3 = (v0 * m4c).root(6)
            err3 = 3 * x3**2 * even3 + 3 * x3 * even3**2 + even3**3 + 3 * (x3 + even3) * odd3
            third = Interval.bounds(k30.lower - err3.upper, k30.upper + err3.upper)
            check(
                variance.lower > 0 and third.lower > 0,
                text + side + " positive cumulants",
            )
            skew = third / (variance * variance.root(2))
            raw = {}
            for r in range(1, 7):
                bound = omega * moments[r].root(2 * r) + (
                    omega**2 * B.root(2) * energy[2 * r].root(2 * r) / 2
                )
                raw[str(r)] = str((bound ** (2 * r)).upper)
            if not eps:
                for name, result in (
                    ("normalized_variance", variance),
                    ("normalized_third_cumulant", third),
                    ("skewness", skew),
                ):
                    original = interval(base[name])
                    check(
                        result.lower <= original.lower <= original.upper <= result.upper,
                        side + " zero-perturbation contains " + name,
                    )
            # Scalar-rescaling controls are mathematical special cases of the domain.
            for scale in (1 - eps, 1 + eps):
                for name, current, degree in (
                    ("leading_variance", v0, 2),
                    ("leading_third_cumulant", k30, 3),
                ):
                    original = interval(base[name])
                    scaled_low = original.lower * scale**degree
                    scaled_high = original.upper * scale**degree
                    check(
                        current.lower <= scaled_low and scaled_high <= current.upper,
                        text + side + str(scale) + " scale control " + name,
                    )
            classes[side] = {
                "q_enclosure": q.record(),
                "abs_p_squared_enclosure": p2.record(),
                "normalized_variance": variance.record(),
                "normalized_third_cumulant": third.record(),
                "skewness": skew.record(),
                "normalized_raw_moment_upper_bounds": raw,
                "third_cumulant_error_upper": str(err3.upper),
            }
        gap = F(classes["B"]["skewness"]["lower"]) - F(classes["A"]["skewness"]["upper"])
        cells.append(
            {
                "epsilon_exact": text,
                "classes": classes,
                "separated": gap > 0,
                "gap_lower_exact": str(gap),
                "gap_display_only": float(gap),
            }
        )
    return cells[0]
