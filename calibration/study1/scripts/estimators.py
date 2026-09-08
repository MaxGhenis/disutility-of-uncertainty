"""Finite-design linear estimators and sensitivity formulas, independent of PR3."""

from __future__ import annotations
import numpy as np


def slope_weights(x):
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        raise ValueError("Need at least two finite income points")
    centered = x - x.mean()
    sxx = centered @ centered
    if sxx <= 0:
        raise ValueError("Income slope is unidentified with zero income variation")
    return centered / sxx


def slope_fit(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    if x.shape != y.shape or not np.isfinite(y).all():
        raise ValueError("Finite paired outcomes required")
    w = slope_weights(x)
    xc = x - x.mean()
    sxx = xc @ xc
    slope = w @ y
    residual = y - y.mean() - slope * xc
    n = len(x)
    leverage = 1 / n + xc**2 / sxx
    mse = residual @ residual / (n - 2) if n > 2 else np.nan
    # OLS residual variance under a correctly specified line and iid zero-mean
    # errors. Two points give no residual degrees of freedom, never zero SE.
    iid_se = np.sqrt(mse / sxx) if n > 2 else np.nan
    # HC3 is undefined for unit leverage. Keep that fact explicit.
    hc3_se = (
        np.sqrt(np.sum((w * residual / (1 - leverage)) ** 2))
        if n > 2 and np.max(leverage) < 1 - 1e-12
        else np.nan
    )
    # Exact leave-one-out slope change from full fit, only where identified.
    valid_loo = (1 - leverage) > 1e-12
    loo_change = np.abs(w[valid_loo] * residual[valid_loo] / (1 - leverage[valid_loo]))
    return {
        "n": n,
        "distinct_x": len(np.unique(x)),
        "span": float(np.ptp(x)),
        "sxx": float(sxx),
        "slope": float(slope),
        "intercept": float(y.mean() - slope * x.mean()),
        "max_abs_residual": float(np.max(np.abs(residual))),
        "residual_rmse": float(np.sqrt(np.mean(residual**2))),
        "iid_se": float(iid_se),
        "hc3_se": float(hc3_se),
        "max_leverage": float(np.max(leverage)),
        "max_loo_change": (
            float(np.max(loo_change)) if n > 2 and len(loo_change) else np.nan
        ),
        "loo_identified_count": int(valid_loo.sum()),
        "l1_weights": float(np.abs(w).sum()),
        "l2_weights": float(np.sqrt(w @ w)),
    }


def box_slope_radius(x, dollar_cap):
    """Sharp slope radius if every error obeys |u_j| <= cap, any correlation."""
    if not np.isfinite(dollar_cap) or dollar_cap < 0:
        raise ValueError("Dollar cap must be nonnegative and finite")
    return float(dollar_cap * np.abs(slope_weights(x)).sum())


def rms_slope_radius(x, dollar_rms_cap):
    """Sharp radius if sqrt(mean(u_j**2)) <= cap, any correlation."""
    if not np.isfinite(dollar_rms_cap) or dollar_rms_cap < 0:
        raise ValueError("RMS cap must be nonnegative and finite")
    w = slope_weights(x)
    return float(dollar_rms_cap * np.sqrt(len(w) * (w @ w)))


def moment_outer_bounds(observed, radii):
    """Finite equal-person moment outer bounds; no stochastic assumptions.

    If each latent error is within radius_i of its observed slope error, its
    noise RMS is at most RMS(radius_i). Projection onto centered vectors is
    a contraction, giving conservative SD bounds too (ddof=0 throughout).
    """
    z, r = np.asarray(observed, float), np.asarray(radii, float)
    if (
        z.ndim != 1
        or z.shape != r.shape
        or not len(z)
        or not np.isfinite(z).all()
        or not np.isfinite(r).all()
        or (r < 0).any()
    ):
        raise ValueError("Need nonempty finite aligned errors and nonnegative radii")
    cap = float(np.sqrt(np.mean(r**2)))
    rmse = float(np.sqrt(np.mean(z**2)))
    sd = float(np.std(z))
    return {
        "n": len(z),
        "bias": [float(z.mean() - r.mean()), float(z.mean() + r.mean())],
        "rmse": [max(0.0, rmse - cap), rmse + cap],
        "sd": [max(0.0, sd - cap), sd + cap],
        "noise_rms_outer": cap,
    }


def paired_moments(a, b):
    """Two noisy measurements: covariance and difference diagnostics.

    Interpretation as latent variance requires a common latent target,
    conditional zero mean errors, and zero cross-measure error covariance.
    ddof=1 is used for cross-person stochastic covariance estimates.
    """
    a, b = np.asarray(a, float), np.asarray(b, float)
    if (
        a.shape != b.shape
        or a.ndim != 1
        or len(a) < 2
        or not np.isfinite(a).all()
        or not np.isfinite(b).all()
    ):
        raise ValueError("Need two nonempty aligned finite measurement vectors")
    va, vb = np.var(a, ddof=1), np.var(b, ddof=1)
    covariance = np.cov(a, b, ddof=1)[0, 1]
    # Exact leave-one-person covariance and jackknife SE. This is a sampling
    # diagnostic conditional on independent respondents, not a noise correction.
    if len(a) > 2:
        n = len(a)
        product = (a - a.mean()) * (b - b.mean())
        leaveout = ((n - 1) * covariance - n / (n - 1) * product) / (n - 2)
        jackknife_se = float(
            np.sqrt((n - 1) / n * np.sum((leaveout - leaveout.mean()) ** 2))
        )
        loo_min, loo_max = float(leaveout.min()), float(leaveout.max())
    else:
        jackknife_se = loo_min = loo_max = None
    # No truncation of negative covariance: the moment model can fail.
    return {
        "covariance_jackknife_se": jackknife_se,
        "covariance_delete_one_min": loo_min,
        "covariance_delete_one_max": loo_max,
        "n": len(a),
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
        "var_a": float(va),
        "var_b": float(vb),
        "covariance": float(covariance),
        "correlation": float(covariance / np.sqrt(va * vb)) if va * vb > 0 else None,
        "difference_sd": float(np.std(a - b, ddof=1)),
        "difference_rmse": float(np.sqrt(np.mean((a - b) ** 2))),
        "average_variance": float(np.var((a + b) / 2, ddof=1)),
        "difference_variance_over_four": float(np.var(a - b, ddof=1) / 4),
    }


def heuristic_fit(tax, iron, spotlight, forecast, residual=None):
    """Equation 3.2/3.3 is linear in the two gamma parameters given residual."""
    tax, iron, spotlight, forecast = [
        np.asarray(x, float) for x in (tax, iron, spotlight, forecast)
    ]
    baseline = tax if residual is None else tax + np.asarray(residual, float)
    x = np.column_stack((iron - baseline, spotlight - baseline))
    y = forecast - baseline
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("Finite heuristic inputs required")
    beta, _, rank, singular = np.linalg.lstsq(x, y, rcond=None)
    if rank < 2:
        return {"rank": int(rank), "gamma": None, "condition": None}
    e = y - x @ beta
    grid = np.array([(i / 10, j / 10) for i in range(11) for j in range(11 - i)])
    sse = np.sum((y[:, None] - x @ grid.T) ** 2, axis=0)
    k = int(np.argmin(sse))
    mse = e @ e / (len(y) - 2)
    covariance = mse * np.linalg.inv(x.T @ x)
    return {
        "rank": int(rank),
        "gamma": beta,
        "condition": float(singular[0] / singular[1]),
        "grid": grid[k],
        "sse": float(e @ e),
        "iid_covariance": covariance,
        "grid_gap": float(np.partition(sse, 1)[1] - sse[k]),
    }


def affine_slope_interval(x, y, dollar_cap):
    """Sharp slope set under |y_j - a - b*x_j| <= cap for some intercept.

    Every pair's residual-intercept intervals must overlap; intervals on R have
    a common intersection iff all pairs overlap. No clipping of belief slopes.
    An empty set falsifies this affine-belief + bounded-error model on the data.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    if (
        x.ndim != 1
        or x.shape != y.shape
        or not len(x)
        or not np.isfinite(x).all()
        or not np.isfinite(y).all()
        or not np.isfinite(dollar_cap)
        or dollar_cap < 0
    ):
        raise ValueError("Need finite paired observations and nonnegative cap")
    order = np.argsort(x, kind="stable")
    x = x[order]
    y = y[order]
    lower, upper = -np.inf, np.inf
    for j in range(len(x)):
        for k in range(j):
            dx = x[j] - x[k]
            dy = y[j] - y[k]
            if dx == 0:
                if abs(dy) > 2 * dollar_cap:
                    return None
                continue
            lower = max(lower, (dy - 2 * dollar_cap) / dx)
            upper = min(upper, (dy + 2 * dollar_cap) / dx)
    # A numerical tolerance is only used to close a vanishingly small negative
    # width, never to make a substantively inconsistent model feasible.
    if lower > upper + 1e-12 * max(1.0, abs(lower), abs(upper)):
        return None
    if lower > upper:
        lower = upper = (lower + upper) / 2
    return float(lower), float(upper)


def minimum_affine_dollar_error(x, y):
    """Exact minimax line error by the finite breakpoints of its convex width.

    For fixed slope b the best intercept bisects max(y-b*x), min(y-b*x).
    The width is convex piecewise linear; a minimum occurs at a breakpoint
    (a pairwise secant), or a flat interval with a breakpoint endpoint.
    """
    x, y = np.asarray(x, float), np.asarray(y, float)
    if (
        x.ndim != 1
        or x.shape != y.shape
        or not len(x)
        or not np.isfinite(x).all()
        or not np.isfinite(y).all()
    ):
        raise ValueError("Finite paired observations required")
    candidates = [0.0]
    for j in range(len(x)):
        for k in range(j):
            if x[j] != x[k]:
                candidates.append((y[j] - y[k]) / (x[j] - x[k]))
    residual_intercepts = (
        y[:, None] - (x - x.mean())[:, None] * np.asarray(candidates)[None, :]
    )
    widths = np.ptp(residual_intercepts, axis=0)
    return float(widths.min() / 2)
