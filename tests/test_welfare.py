"""Fiscal closure and calibration regressions, independent of national totals."""

from types import SimpleNamespace

import numpy as np
import pytest

from taxuncertainty.analysis.calibration import (
    Illustration,
    beliefs_with_rmse,
    private_regret_approx,
)
from taxuncertainty.analysis.welfare import evaluate_population
from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.labor import individual_dwl, optimal_hours


def test_illustrative_normalization_and_evidence():
    inputs = Illustration()
    hours = optimal_hours(inputs.hourly_wage, inputs.tax_rate, inputs.preferences)
    assert hours == pytest.approx(2000)
    assert inputs.assumptions()["error_source"]["status"] == "assumed"
    assert "total_workers" not in inputs.assumptions()


@pytest.mark.parametrize("mean", [-0.12, -0.06, 0, 0.06, 0.12])
def test_rmse_decomposition(mean):
    belief = beliefs_with_rmse(mean)
    assert belief.mean_error**2 + belief.std_error**2 == pytest.approx(0.12**2)


def test_impossible_rmse_rejected():
    with pytest.raises(ValueError):
        beliefs_with_rmse(-0.13, 0.12)


def test_small_error_approximation_matches_exact_private_regret():
    inputs = Illustration()
    error = 0.0001
    exact = individual_dwl(27.5, 0.3, 0.3 + error, inputs.preferences)
    approx = private_regret_approx(55000, 0.33, 0.3, error**2)
    assert approx == pytest.approx(exact, rel=0.001)


def test_approximation_rejects_invalid_interior():
    with pytest.raises(ValueError):
        private_regret_approx(55000, 0.33, 1, 0.12**2)


def test_population_matches_direct_realized_utility_and_budget():
    inputs = Illustration()
    wages = np.array([15.0, 27.5, 50.0])
    taxes = np.array([0.1, 0.3, 0.4])
    omega = np.array([2.0, 1.0, 0.5])
    bias = -0.01
    prefs = inputs.preferences
    baseline_hours = np.array(
        [optimal_hours(w, t, prefs) for w, t in zip(wages, taxes)]
    )
    mistaken_hours = np.array(
        [optimal_hours(w, t + bias, prefs) for w, t in zip(wages, taxes)]
    )
    baseline_revenue = np.sum(taxes * wages * baseline_hours)
    mistaken_revenue = np.sum(taxes * wages * mistaken_hours)
    baseline_c = wages * (1 - taxes) * baseline_hours + baseline_revenue / 3
    mistaken_c = wages * (1 - taxes) * mistaken_hours + mistaken_revenue / 3
    direct_loss = sum(
        o * (prefs.utility(c0, h0) - prefs.utility(c1, h1))
        for o, c0, h0, c1, h1 in zip(
            omega, baseline_c, baseline_hours, mistaken_c, mistaken_hours
        )
    )
    outcome = evaluate_population(wages, taxes, prefs, NormalBeliefs(bias, 0), omega)
    assert outcome.social_loss == pytest.approx(direct_loss, abs=1e-8)
    assert outcome.workers * outcome.per_capita_transfer_change == pytest.approx(
        mistaken_revenue - baseline_revenue
    )


def test_population_no_error():
    outcome = evaluate_population(
        [20, 30], [0.2, 0.3], Illustration().preferences, NormalBeliefs()
    )
    assert outcome.private_regret == pytest.approx(0, abs=1e-8)
    assert outcome.revenue_change == pytest.approx(0, abs=1e-8)
    assert outcome.social_loss == pytest.approx(0, abs=1e-8)


@pytest.mark.parametrize(
    "wages,rates,weights",
    [
        ([], [], None),
        ([20], [0.2, 0.3], None),
        ([20], [0.2], [-1]),
        ([20], [0.2], [float("nan")]),
    ],
)
def test_bad_population_rejected(wages, rates, weights):
    with pytest.raises(ValueError):
        evaluate_population(
            wages, rates, Illustration().preferences, NormalBeliefs(), weights
        )


def test_overflowing_aggregate_social_weights_rejected():
    with pytest.raises(ValueError):
        evaluate_population(
            [20, 30],
            [0.3, 0.3],
            Illustration().preferences,
            NormalBeliefs(-0.01, 0),
            [1e308, 1e308],
        )


def test_assumption_description_tracks_custom_normalization():
    assumptions = Illustration(hourly_wage=40, baseline_hours=1000).assumptions()
    assert assumptions["baseline_earnings"] == 40000
    assert assumptions["dollar_normalization"].startswith(
        "40.00 dollars/hour and 1,000 hours"
    )


@pytest.mark.parametrize(
    "field", ["private_regret", "earnings_change", "revenue_change"]
)
def test_overflowing_unweighted_totals_rejected(monkeypatch, field):
    worker = dict(private_regret=0.0, earnings_change=0.0, revenue_change=0.0)
    worker[field] = 1e308
    monkeypatch.setattr(
        "taxuncertainty.analysis.welfare.evaluate_worker",
        lambda *args: SimpleNamespace(**worker),
    )
    with pytest.raises(ValueError, match="overflowed"):
        evaluate_population(
            [20, 30],
            [0.3, 0.3],
            Illustration().preferences,
            NormalBeliefs(),
            [1e-300, 1e-300],
        )
