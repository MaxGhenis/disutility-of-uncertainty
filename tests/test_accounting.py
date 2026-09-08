"""Independent utility, fiscal, and numerical checks of exact worker accounts."""

from math import sqrt

import numpy as np
import pytest

from taxuncertainty.models import NormalBeliefs, QuasilinearIsoelastic, evaluate_worker
from taxuncertainty.models.labor import expected_private_regret_approx


@pytest.fixture
def prefs():
    return QuasilinearIsoelastic(27.5 * 0.7 / 2000 ** (1 / 0.33), 0.33)


def test_no_error_changes_nothing(prefs):
    outcome = evaluate_worker(27.5, 0.3, prefs, NormalBeliefs())
    for field in (
        "earnings_change",
        "revenue_change",
        "transfer_change",
        "private_regret",
        "social_loss",
    ):
        assert getattr(outcome, field) == pytest.approx(0, abs=1e-9)


def test_fiscal_accounting_identity(prefs):
    outcome = evaluate_worker(27.5, 0.3, prefs, NormalBeliefs(std_error=0.12))
    assert outcome.revenue_change == pytest.approx(0.3 * outcome.earnings_change)
    assert outcome.transfer_change == outcome.revenue_change
    assert outcome.social_loss == outcome.private_regret - outcome.revenue_change
    assert outcome.expected_revenue - outcome.baseline_revenue == pytest.approx(
        outcome.revenue_change
    )


def test_small_noise_private_and_social_expansions(prefs):
    # Independent envelope expansion: fiscal term multiplies private regret
    # by 1 + tau*(1-eps)/(1-tau) for locally unbiased, uncensored errors.
    outcome = evaluate_worker(27.5, 0.3, prefs, NormalBeliefs(std_error=0.002))
    approximate = expected_private_regret_approx(27.5, 0.3, 0.002, prefs)
    assert outcome.private_regret == pytest.approx(approximate, rel=2e-5)
    multiplier = 1 + 0.3 * (1 - 0.33) / 0.7
    assert outcome.social_loss / outcome.private_regret == pytest.approx(
        multiplier, rel=2e-5
    )


def test_deterministic_underestimate_can_increase_social_welfare(prefs):
    outcome = evaluate_worker(27.5, 0.3, prefs, NormalBeliefs(mean_error=-0.01))
    assert outcome.private_regret > 0
    assert outcome.revenue_change > outcome.private_regret
    assert outcome.social_loss < 0


def test_quadratic_labor_cost_has_closed_form_regret():
    # eps=1: U(h*)-U(h) = psi*(h-h*)^2/2. With no binding hours
    # corner or censoring, expected regret = w^2 E[error^2]/(2psi).
    prefs = QuasilinearIsoelastic(2, 1)
    beliefs = NormalBeliefs(-0.03, 0.04, None, None)
    outcome = evaluate_worker(20, 0.3, prefs, beliefs)
    assert outcome.private_regret == pytest.approx(
        20**2 * (0.03**2 + 0.04**2) / 4, rel=1e-12
    )
    assert outcome.earnings_change == pytest.approx(-(20**2) * -0.03 / 2, rel=1e-12)


@pytest.mark.parametrize("tax", [0, 0.3, 0.99, 1, 1.1])
def test_exact_corner_expectations_against_independent_monte_carlo(prefs, tax):
    # Independent direct utility calculation, including actual consumption,
    # not a draw from the quadrature implementation or its regret helper.
    rng = np.random.default_rng(123)
    perceived = np.clip(tax + rng.normal(-0.02, 0.12, 400_000), 0, 1)
    hours = (27.5 * (1 - perceived) / prefs.psi) ** 0.33
    best_hours = (27.5 * max(0, 1 - tax) / prefs.psi) ** 0.33
    exponent = 1 + 1 / 0.33
    utility = 27.5 * (1 - tax) * hours - prefs.psi * hours**exponent / exponent
    best_utility = (
        27.5 * (1 - tax) * best_hours - prefs.psi * best_hours**exponent / exponent
    )
    regret = best_utility - utility
    outcome = evaluate_worker(27.5, tax, prefs, NormalBeliefs(-0.02, 0.12))
    assert np.isfinite(outcome.private_regret)
    assert abs(outcome.private_regret - regret.mean()) < 5 * regret.std() / sqrt(
        len(hours)
    )
    assert abs(outcome.expected_hours - hours.mean()) < 5 * hours.std() / sqrt(
        len(hours)
    )


@pytest.mark.parametrize("tax", [0, 0.3, 0.99, 1.0])
def test_quadrature_converges_at_corners(prefs, tax):
    beliefs = NormalBeliefs(std_error=0.12)
    low = evaluate_worker(27.5, tax, prefs, beliefs, quadrature_order=64)
    high = evaluate_worker(27.5, tax, prefs, beliefs, quadrature_order=512)
    assert low.private_regret == pytest.approx(high.private_regret, rel=1e-7, abs=1e-8)
    assert low.expected_hours == pytest.approx(high.expected_hours, rel=1e-7)


def test_99_percent_rate_does_not_use_taylor_approximation():
    tax, wage, eps = 0.99, 27.5, 0.33
    prefs = QuasilinearIsoelastic(wage * (1 - tax) / 2000 ** (1 / eps), eps)
    exact = evaluate_worker(wage, tax, prefs, NormalBeliefs(std_error=0.12))
    approx = expected_private_regret_approx(wage, tax, 0.12, prefs)
    # Independently integrated in the earlier theory audit, normalized to $55k.
    assert 8.3 < approx / exact.private_regret < 8.5


def test_subsidy_with_unrestricted_beliefs_has_no_spurious_error(prefs):
    outcome = evaluate_worker(27.5, -0.2, prefs, NormalBeliefs(lower_bound=None))
    assert outcome.private_regret == pytest.approx(0, abs=1e-9)
    assert outcome.social_loss == pytest.approx(0, abs=1e-9)
