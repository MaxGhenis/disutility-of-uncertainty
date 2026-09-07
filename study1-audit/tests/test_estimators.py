"""Analytical and adversarial estimator tests; all examples are synthetic."""

import sys
from pathlib import Path
import itertools
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from estimators import (
    slope_fit,
    slope_weights,
    box_slope_radius,
    rms_slope_radius,
    moment_outer_bounds,
    paired_moments,
    heuristic_fit,
)


def test_affine_and_shift_invariance():
    x = np.array([100.0, 300.0, 800.0, 1200.0])
    y = 33 + 0.27 * x
    f = slope_fit(x, y)
    assert f["slope"] == pytest.approx(0.27)
    assert f["max_abs_residual"] < 1e-12
    assert slope_fit(x + 1e6, y + 777)["slope"] == pytest.approx(0.27)
    assert slope_weights(x).sum() == pytest.approx(0)
    assert slope_weights(x) @ x == pytest.approx(1)


def test_two_points_have_no_variance_estimate_or_affine_test():
    f = slope_fit([0, 1], [2, 1002])
    assert f["slope"] == 1000
    assert f["max_leverage"] == 1
    assert np.isnan(f["iid_se"]) and np.isnan(f["hc3_se"])
    assert f["distinct_x"] == 2 and f["max_abs_residual"] == 0


@pytest.mark.parametrize(
    "x,y", [([1, 1], [2, 3]), ([1], [2]), ([1, 2], [3, np.nan]), ([1, np.inf], [2, 3])]
)
def test_unidentified_or_invalid_raises(x, y):
    with pytest.raises(ValueError):
        slope_fit(x, y)


def test_loo_matches_refit_and_hc3_formula():
    x = np.array([1.0, 2.0, 8.0, 20.0])
    y = np.array([0.0, 2.0, 3.0, 19.0])
    f = slope_fit(x, y)
    actual = max(
        abs(slope_fit(np.delete(x, j), np.delete(y, j))["slope"] - f["slope"])
        for j in range(4)
    )
    assert f["max_loo_change"] == pytest.approx(actual)
    w = slope_weights(x)
    h = 0.25 + (x - x.mean()) * w
    e = y - y.mean() - f["slope"] * (x - x.mean())
    assert f["hc3_se"] ** 2 == pytest.approx(np.sum((w * e / (1 - h)) ** 2))


def test_box_bound_sharp_exhaustive_correlated_errors():
    x = np.array([0.0, 200.0, 700.0, 1000.0])
    cap = 100.0
    w = slope_weights(x)
    radius = box_slope_radius(x, cap)
    attained = max(
        abs(w @ (cap * np.array(signs)))
        for signs in itertools.product([-1, 1], repeat=4)
    )
    assert attained == pytest.approx(radius)
    assert w @ (cap * np.sign(w)) == pytest.approx(radius)


def test_rms_bound_sharp():
    x = np.array([0.0, 10.0, 900.0, 1000.0])
    cap = 500.0
    w = slope_weights(x)
    u = cap * np.sqrt(len(w)) * w / np.linalg.norm(w)
    assert np.sqrt(np.mean(u * u)) == pytest.approx(cap)
    assert w @ u == pytest.approx(rms_slope_radius(x, cap))


def test_moment_outer_bounds_cover_every_box_corner():
    observed = np.array([-0.3, 0.02, 0.25, 0.4])
    r = np.array([0.1, 0.2, 0.01, 0.05])
    bounds = moment_outer_bounds(observed, r)
    for signs in itertools.product([-1, 1], repeat=4):
        latent = observed + r * np.array(signs)
        for name, value in [
            ("bias", latent.mean()),
            ("rmse", np.sqrt(np.mean(latent**2))),
            ("sd", latent.std()),
        ]:
            assert bounds[name][0] - 1e-12 <= value <= bounds[name][1] + 1e-12


def test_bounds_do_not_clip_rates_or_center_bias_away():
    b = moment_outer_bounds([2.0, 3.0], [0.0, 0.0])
    assert b["bias"] == [2.5, 2.5]
    assert b["rmse"] == [np.sqrt(6.5)] * 2
    assert b["sd"] == [0.5, 0.5]
    with pytest.raises(ValueError):
        moment_outer_bounds([1], [-1])
    with pytest.raises(ValueError):
        box_slope_radius([0, 1], -1)


def test_covariance_identity_and_negative_value_retained():
    a = np.array([-2.0, 0.0, 3.0, 5.0])
    b = -a
    m = paired_moments(a, b)
    assert m["covariance"] < 0
    assert m["average_variance"] - m["difference_variance_over_four"] == pytest.approx(
        m["covariance"]
    )


def test_shared_slope_error_looks_stable_even_with_homogeneous_latent_beliefs():
    x = np.array([-15000.0, -9000.0, -3000.0, 3000.0, 9000.0, 15000.0])
    error_slope = np.array([-0.1, 0.1, -0.1, 0.1])
    latent_slope = 0.2
    y = 5000 + (latent_slope + error_slope[:, None]) * x
    a = np.array([slope_fit(x[::2], v[::2])["slope"] for v in y])
    b = np.array([slope_fit(x[1::2], v[1::2])["slope"] for v in y])
    assert paired_moments(a, b)["correlation"] == pytest.approx(1)
    assert paired_moments(a, b)["covariance"] == pytest.approx(
        np.var(error_slope, ddof=1)
    )
    assert np.var(np.full(4, latent_slope)) == 0


def test_common_intercept_error_cancels_in_income_slope():
    x = np.array([0.0, 1.0, 2.0, 5.0])
    y = 5 + 0.2 * x
    assert slope_fit(x, y + 1000)["slope"] == pytest.approx(0.2)


def test_nonlinear_truth_can_share_nominal_bracket():
    x = np.array([0.0, 10.0, 20.0])
    nominal_bracket = np.array([3, 3, 3])
    tax = 0.25 * x + np.array([0.0, 0.0, 2.0])
    assert np.unique(nominal_bracket).size == 1
    assert slope_fit(x, tax)["max_abs_residual"] > 0.05


def test_heuristic_linear_recovery_and_rank_failure():
    x = np.array([10.0, 40.0, 80.0, 100.0])
    tax = np.array([0.0, 3.0, 15.0, 24.0])
    iron = 0.1 * x
    spotlight = 0.25 * x - 5
    y = (1 - 0.4 - 0.1) * tax + 0.4 * iron + 0.1 * spotlight
    f = heuristic_fit(tax, iron, spotlight, y)
    assert f["gamma"] == pytest.approx([0.4, 0.1])
    assert f["grid"] == pytest.approx([0.4, 0.1])
    assert heuristic_fit(tax, np.zeros(4), np.zeros(4), y)["rank"] == 1


def test_affine_box_interval_and_minimax_are_sharp():
    from estimators import affine_slope_interval, minimum_affine_dollar_error

    x = np.array([0.0, 1.0, 2.0])
    y = np.array([0.0, 0.0, 2.0])
    assert minimum_affine_dollar_error(x, y) == pytest.approx(0.5)
    assert affine_slope_interval(x, y, 0.49) is None
    assert affine_slope_interval(x, y, 0.5) == pytest.approx((1.0, 1.0))
    # The admissible slope must permit one common intercept, not separate
    # pair-specific intercepts. Check both endpoints directly.
    interval = affine_slope_interval(x, y, 1.0)
    for slope in interval:
        lower = np.max(y - slope * x - 1)
        upper = np.min(y - slope * x + 1)
        assert lower <= upper + 1e-12
    assert interval == pytest.approx((0.0, 2.0))


def test_repeated_income_can_reject_bounded_error_without_slope_variation():
    from estimators import affine_slope_interval, minimum_affine_dollar_error

    assert affine_slope_interval([1, 1], [0, 401], 100) is None
    assert minimum_affine_dollar_error([1, 1], [0, 401]) == 200.5
    assert affine_slope_interval([1, 1], [0, 401], 201) == (-np.inf, np.inf)


def test_exact_pair_is_always_affine_even_with_extreme_slope():
    from estimators import affine_slope_interval, minimum_affine_dollar_error

    assert minimum_affine_dollar_error([100, 101], [0, 10000]) == 0
    assert affine_slope_interval([100, 101], [0, 10000], 100) == pytest.approx(
        (9800, 10200)
    )


def test_minimax_invariant_to_large_income_origin_and_common_intercept():
    from estimators import minimum_affine_dollar_error

    x = np.array([1, 2, 5, 6.0])
    y = np.array([0, 3, 4, 8.0])
    assert minimum_affine_dollar_error(x, y) == pytest.approx(
        minimum_affine_dollar_error(x + 1e9, y + 1000)
    )


def test_covariance_delete_one_and_jackknife_match_explicit_deletions():
    a = np.array([0.1, 0.3, -1.0, 0.2, 3.0])
    b = np.array([0.6, 0.2, 0.2, -0.1, 2.0])
    m = paired_moments(a, b)
    actual = np.array(
        [np.cov(np.delete(a, i), np.delete(b, i), ddof=1)[0, 1] for i in range(len(a))]
    )
    assert m["covariance_delete_one_min"] == pytest.approx(actual.min())
    assert m["covariance_delete_one_max"] == pytest.approx(actual.max())
    assert m["covariance_jackknife_se"] == pytest.approx(
        np.sqrt((len(a) - 1) / len(a) * np.sum((actual - actual.mean()) ** 2))
    )
