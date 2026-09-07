"""Model falsification and explicitly synthetic correlated-error demonstrations."""

from __future__ import annotations
import itertools
import numpy as np
import pandas as pd
from sources import ROOT, frame, read_archive
from estimators import (
    affine_slope_interval,
    minimum_affine_dollar_error,
    slope_fit,
    paired_moments,
)
from audit import NUMERIC, csv, save, quantiles


def affine_model_checks():
    d = frame(read_archive(), "RJT_study_1_data", NUMERIC)
    d = d[d.attention == 0].copy()
    for c in d:
        if d[c].dtype.kind == "f":
            d[c] = d[c].astype(float)
    rows = []
    samples = {
        "own_pair": d.qnum <= 2,
        "own_bracket": (d.localdraw == 1) & (d.bracket == d.ownbracket),
    }
    radii = []
    for panel, mask in samples.items():
        for mid, g in d[mask].groupby("mid", sort=True):
            if g.ran.nunique() < 2:
                continue
            true = slope_fit(g.ran, g.tax)
            for outcome in ["taxguessmain", "taxguessds"]:
                mincap = minimum_affine_dollar_error(g.ran, g[outcome])
                radii.append(
                    {
                        "panel": panel,
                        "outcome": outcome,
                        "n": len(g),
                        "span": np.ptp(g.ran),
                        "true_affine_observed": g.ran.nunique() >= 3
                        and true["max_abs_residual"] <= 0.05,
                        "mincap": mincap,
                    }
                )
                for cap in [50, 100, 500, 1000, 5000]:
                    interval = affine_slope_interval(g.ran, g[outcome], cap)
                    # Internal mathematical agreement between two separately
                    # derived implementations (minimax and pair constraints).
                    assert (interval is not None) == (mincap <= cap + 1e-7), (
                        mincap,
                        cap,
                    )
                    rows.append(
                        {
                            "panel": panel,
                            "outcome": outcome,
                            "mincap": mincap,
                            "cap": cap,
                            "n": len(g),
                            "span": np.ptp(g.ran),
                            "true_affine_observed": g.ran.nunique() >= 3
                            and true["max_abs_residual"] <= 0.05,
                            "compatible": interval is not None,
                            "width": interval[1] - interval[0] if interval else np.nan,
                        }
                    )
    r = pd.DataFrame(rows)
    m = pd.DataFrame(radii)
    summaries = []
    for panel in samples:
        for outcome in ["taxguessmain", "taxguessds"]:
            for min_n, min_span, affine in [
                (2, 0, False),
                (3, 0, True),
                (4, 5000, True),
            ]:
                selected = r[
                    (r.panel == panel)
                    & (r.outcome == outcome)
                    & (r.n >= min_n)
                    & (r.span >= min_span)
                ]
                minima = m[
                    (m.panel == panel)
                    & (m.outcome == outcome)
                    & (m.n >= min_n)
                    & (m.span >= min_span)
                ]
                if affine:
                    selected = selected[selected.true_affine_observed]
                    minima = minima[minima.true_affine_observed]
                if not len(selected):
                    continue
                for cap, g in selected.groupby("cap"):
                    summaries.append(
                        {
                            "panel": panel,
                            "outcome": outcome,
                            "min_n": min_n,
                            "min_span": min_span,
                            "observed_affine_screen": affine,
                            "dollar_cap": cap,
                            "respondents": len(g),
                            "compatible": int(g.compatible.sum()),
                            "incompatible": int((~g.compatible).sum()),
                            "compatible_share": g.compatible.mean(),
                            "median_width_among_compatible": g.width.median(),
                            "median_minimum_dollar_error": minima.mincap.median(),
                            "p95_minimum_dollar_error": minima.mincap.quantile(0.95),
                        }
                    )
    csv("affine_belief_falsification", summaries)


def covariance_sensitivity():
    r = pd.read_csv(ROOT / "results/repeated_measures.csv")
    choose = r[
        (r.outcome == "taxguessmain")
        & (r.split == "income_interleaved")
        & (
            (
                (r.panel == "own_bracket")
                & r.observed_affine_screen
                & r.min_half_span.isin([5000, 10000])
            )
            | (
                (r.panel == "random_full")
                & ~r.observed_affine_screen
                & (r.min_half_span == 0)
            )
        )
    ]
    result = []
    for _, row in choose.iterrows():
        va, vb, c = row.var_a, row.var_b, row.covariance
        # Assuming both measurement errors are orthogonal to the SAME latent
        # target, solve covariance = V + rho*sqrt((Va-V)*(Vb-V)).
        # rho from 0 to the observed correlation admits a root on [0,C].
        for fraction in [0, 0.25, 0.5, 0.75, 1]:
            rho = fraction * row.correlation
            lo, hi = 0.0, c
            for _ in range(80):
                v = (lo + hi) / 2
                modeled = v + rho * np.sqrt((va - v) * (vb - v))
                if modeled < c:
                    lo = v
                else:
                    hi = v
            v = 0.0 if fraction == 1 else (lo + hi) / 2
            result.append(
                {
                    "panel": row.panel,
                    "min_half_span": row.min_half_span,
                    "n": row.n,
                    "observed_correlation": row.correlation,
                    "assumed_error_correlation": rho,
                    "implied_common_target_variance": v,
                    "implied_common_target_sd": np.sqrt(v),
                    "implied_error_sd_a": np.sqrt(va - v),
                    "implied_error_sd_b": np.sqrt(vb - v),
                    "moment_equation_residual": v
                    + rho * np.sqrt((va - v) * (vb - v))
                    - c,
                }
            )
    csv("correlated_error_sensitivity", result)


def synthetic_demonstrations():
    # Exact 2^8 factorial: each respondent receives one combination of +/-1
    # latent slope, common method slope, and six mutually orthogonal point errors.
    # SYNTHETIC ONLY: these are mathematical counterexamples, not study results.
    signs = np.array(list(itertools.product([-1.0, 1.0], repeat=8)))
    x = np.array([-15000.0, -9000.0, -3000.0, 3000.0, 9000.0, 15000.0])
    out = []
    for name, latent_sd, common_sd, point_sd, intercept_sd in [
        ("iid_noise_only_homogeneous_belief", 0, 0, 500, 0),
        ("iid_noise_with_latent_heterogeneity", 0.08, 0, 500, 0),
        ("common_intercept_error_cancels", 0, 0, 500, 1000),
        ("common_slope_error_homogeneous_belief", 0, 0.10, 500, 0),
        ("common_slope_plus_latent_heterogeneity", 0.08, 0.10, 500, 0),
    ]:
        latent = 0.2 + latent_sd * signs[:, 0]
        common = common_sd * signs[:, 1]
        y = (
            5000
            + (latent + common)[:, None] * x
            + point_sd * signs[:, 2:]
            + intercept_sd * signs[:, 1, None]
        )
        a = np.array([slope_fit(x[::2], z[::2])["slope"] for z in y])
        b = np.array([slope_fit(x[1::2], z[1::2])["slope"] for z in y])
        moments = paired_moments(a, b)
        out.append(
            {
                "SYNTHETIC_ONLY": True,
                "scenario": name,
                "latent_sd_parameter": latent_sd,
                "common_response_slope_sd_parameter": common_sd,
                "point_error_dollar_sd_parameter": point_sd,
                "true_finite_sample_latent_variance": np.var(latent, ddof=1),
                "expected_finite_sample_covariance": (latent_sd**2 + common_sd**2)
                * len(signs)
                / (len(signs) - 1),
                "mean_noise_dollar_rms": np.sqrt(
                    np.mean((y - (5000 + latent[:, None] * x)) ** 2)
                ),
                **moments,
            }
        )
        assert (
            abs(moments["covariance"] - out[-1]["expected_finite_sample_covariance"])
            < 1e-12
        )
    csv("SYNTHETIC_correlated_error", out)
    # A known common latent component cannot be separated from an unknown
    # method component by adding within-session observations: algebraic equality.
    observed = 5000 + (0.2 + 0.1 * signs[:, 1, None]) * x
    alternative = 5000 + 0.2 * x + (0.1 * signs[:, 1, None] * x)
    save(
        "SYNTHETIC_observational_equivalence",
        {
            "SYNTHETIC_ONLY": True,
            "maximum_outcome_difference": np.max(np.abs(observed - alternative)),
            "interpretation": "Identical same-session data: stable heterogeneous beliefs versus homogeneous stable beliefs plus a respondent-specific session response slope. A new independent session or external validation is required to distinguish them.",
        },
    )


def measurement_design():
    # Prospective arithmetic only; error scales are assumptions, not estimates.
    designs = {
        "pair_500_span": np.array([0.0, 500.0]),
        "six_points_10000_span": np.linspace(-5000, 5000, 6),
        "six_points_30000_span": np.linspace(-15000, 15000, 6),
        "eight_points_30000_span": np.linspace(-15000, 15000, 8),
    }
    from estimators import slope_weights, box_slope_radius

    rows = []
    for name, x in designs.items():
        for sigma in [100, 500, 1000]:
            rows.append(
                {
                    "PROSPECTIVE_ASSUMPTIONS_ONLY": True,
                    "design": name,
                    "n_per_session": len(x),
                    "income_span": np.ptp(x),
                    "assumed_iid_dollar_sd": sigma,
                    "one_session_slope_se": sigma * np.linalg.norm(slope_weights(x)),
                    "two_independent_sessions_mean_slope_se": sigma
                    * np.linalg.norm(slope_weights(x))
                    / np.sqrt(2),
                    "box_radius_if_dollar_cap_100": box_slope_radius(x, 100),
                }
            )
    csv("prospective_design", rows)


if __name__ == "__main__":
    affine_model_checks()
    covariance_sensitivity()
    synthetic_demonstrations()
    measurement_design()
    print(
        "Affine-belief falsification, correlated-error sensitivities and synthetic estimator demonstrations complete."
    )
