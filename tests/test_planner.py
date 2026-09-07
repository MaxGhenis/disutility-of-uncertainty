"""Tests for social planner — TDD: written before implementation."""

import numpy as np
import pytest

from taxuncertainty.models.planner import SocialPlanner
from taxuncertainty.models.preferences import QuasilinearIsoelastic


@pytest.fixture
def prefs():
    return QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)


@pytest.fixture
def wages():
    return np.array([15.0, 20.0, 25.0, 30.0, 40.0])


@pytest.fixture
def planner():
    return SocialPlanner()


class TestBudgetBalance:
    def test_revenue_equals_transfers(self, planner, wages, prefs):
        """Government budget must balance: revenue = N * demogrant."""
        tau = 0.3
        rev = planner.revenue(tau, wages, prefs)
        dem = planner.demogrant(tau, wages, prefs)
        assert rev == pytest.approx(dem * len(wages))

    def test_budget_balance_various_rates(self, planner, wages, prefs):
        for tau in [0.1, 0.2, 0.3, 0.4, 0.5]:
            rev = planner.revenue(tau, wages, prefs)
            dem = planner.demogrant(tau, wages, prefs)
            assert rev == pytest.approx(dem * len(wages), rel=1e-10)

    def test_zero_tax_zero_transfers(self, planner, wages, prefs):
        assert planner.demogrant(0.0, wages, prefs) == pytest.approx(0.0)

    def test_revenue_positive_for_positive_tax(self, planner, wages, prefs):
        assert planner.revenue(0.3, wages, prefs) > 0

    def test_budget_balance_under_misperception(self, planner, wages, prefs):
        """Budget should still balance with misperception (ex-post)."""
        tau = 0.3
        sigma = 0.1
        rev = planner.revenue(tau, wages, prefs, misperception_std=sigma, seed=42)
        dem = planner.demogrant(tau, wages, prefs, misperception_std=sigma, seed=42)
        assert rev == pytest.approx(dem * len(wages))


class TestSocialWelfare:
    def test_welfare_positive(self, planner, wages, prefs):
        w = planner.social_welfare(0.3, wages, prefs)
        assert w > 0

    def test_welfare_higher_without_misperception(self, planner, wages, prefs):
        """Perfect information yields higher welfare."""
        w_certain = planner.social_welfare(0.3, wages, prefs, misperception_std=0)
        w_uncertain = planner.social_welfare(
            0.3, wages, prefs, misperception_std=0.1, seed=42
        )
        assert w_certain > w_uncertain

    def test_welfare_decreases_with_more_misperception(self, planner, wages, prefs):
        w1 = planner.social_welfare(0.3, wages, prefs, misperception_std=0.05, seed=42)
        w2 = planner.social_welfare(0.3, wages, prefs, misperception_std=0.15, seed=42)
        assert w1 > w2


class TestOptimalTax:
    def test_optimal_tax_in_range(self, planner, wages, prefs):
        tau_star = planner.optimal_tax(wages, prefs)
        assert 0.0 < tau_star < 1.0

    def test_optimal_tax_decreases_with_misperception(self, planner, wages, prefs):
        """Key result: optimal tax lower under misperception."""
        tau_certain = planner.optimal_tax(wages, prefs, misperception_std=0)
        tau_uncertain = planner.optimal_tax(
            wages, prefs, misperception_std=0.1, seed=42
        )
        assert tau_uncertain < tau_certain

    def test_optimal_tax_with_equal_wages_is_zero(self, planner, prefs):
        """With identical wages, no redistribution motive → τ*=0."""
        equal_wages = np.array([20.0, 20.0, 20.0])
        tau_star = planner.optimal_tax(equal_wages, prefs)
        assert tau_star == pytest.approx(0.0, abs=0.02)

    def test_optimal_tax_increases_with_wage_inequality(self, planner, prefs):
        """More inequality → higher optimal tax."""
        low_ineq = np.array([18.0, 20.0, 22.0])
        high_ineq = np.array([10.0, 20.0, 50.0])
        tau_low = planner.optimal_tax(low_ineq, prefs)
        tau_high = planner.optimal_tax(high_ineq, prefs)
        assert tau_high > tau_low


class TestExpectedAccounting:
    def test_seed_and_draw_count_do_not_change_expected_results(
        self, planner, wages, prefs
    ):
        a = planner.social_welfare(0.3, wages, prefs, 0.12, seed=42, n_mc=10)
        b = planner.social_welfare(0.3, wages, prefs, 0.12, seed=777, n_mc=1000)
        assert a == b

    @pytest.mark.parametrize("mode", ["equal", "inverse_wage"])
    def test_regret_and_transfer_identity(self, wages, prefs, mode):
        from taxuncertainty.models.beliefs import NormalBeliefs

        result = SocialPlanner(mode).evaluate(
            0.3, wages, prefs, NormalBeliefs(-0.03, 0.12)
        )
        weight_mean = 1 if mode == "equal" else np.mean(np.mean(wages) / wages)
        assert result.social_welfare_loss == pytest.approx(
            result.weighted_mean_private_regret - weight_mean * result.demogrant_change
        )
        assert result.expected_demogrant * len(wages) == pytest.approx(
            result.expected_revenue
        )
        assert result.demogrant_change * len(wages) == pytest.approx(
            result.revenue_change
        )

    def test_equal_weights_aggregate_worker_accounting(self, wages, prefs):
        from taxuncertainty.models import NormalBeliefs, evaluate_worker

        beliefs = NormalBeliefs(-0.03, 0.12)
        workers = [evaluate_worker(wage, 0.3, prefs, beliefs) for wage in wages]
        result = SocialPlanner("equal").evaluate(0.3, wages, prefs, beliefs)
        assert result.mean_private_regret == pytest.approx(
            np.mean([x.private_regret for x in workers])
        )
        assert result.social_welfare_loss == pytest.approx(
            np.mean([x.social_loss for x in workers])
        )
        assert result.revenue_change == pytest.approx(
            sum(x.revenue_change for x in workers)
        )

    @pytest.mark.parametrize("mode", ["equal", "inverse_wage"])
    def test_expected_welfare_against_independent_realized_utility(
        self, wages, prefs, mode
    ):
        from taxuncertainty.models.beliefs import NormalBeliefs

        tax = 0.3
        beliefs = NormalBeliefs(-0.03, 0.12)
        rng = np.random.default_rng(129)
        error = rng.normal(-0.03, 0.12, (200_000, len(wages)))
        perceived = np.clip(tax + error, 0, 1)
        hours = (wages * (1 - perceived) / prefs.psi) ** prefs.frisch_elasticity
        earnings = wages * hours
        # Each draw balances its own government budget, not just mean hours.
        grant = tax * earnings.mean(axis=1, keepdims=True)
        consumption = (1 - tax) * earnings + grant
        exponent = 1 + 1 / prefs.frisch_elasticity
        utility = consumption - prefs.psi * hours**exponent / exponent
        weights = np.ones_like(wages) if mode == "equal" else np.mean(wages) / wages
        realized_welfare = (weights * utility).mean(axis=1)
        expected = SocialPlanner(mode).evaluate(tax, wages, prefs, beliefs)
        se = realized_welfare.std() / np.sqrt(len(realized_welfare))
        assert abs(expected.expected_social_welfare - realized_welfare.mean()) < 5 * se

    def test_no_error_has_zero_loss(self, planner, wages, prefs):
        result = planner.evaluate(0.3, wages, prefs)
        assert result.social_welfare_loss == 0
        assert result.mean_private_regret == 0
        assert result.revenue_change == 0


class TestOptimalTaxScenarios:
    def test_signed_bias_at_same_rmse_reverses_optimal_tax_direction(self):
        from taxuncertainty.models.beliefs import NormalBeliefs

        # Distribution and directional result independently established by
        # the pre-rebuild theory audit (0.445, 0.429, 0.456 respectively).
        wages = np.random.default_rng(42).lognormal(
            np.log(27.5) - 0.5 * 0.5**2, 0.5, 500
        )
        prefs = QuasilinearIsoelastic(1, 0.33)
        planner = SocialPlanner()
        informed = planner.optimal_tax(wages, prefs)
        unbiased = planner.optimal_tax(wages, prefs, misperception_std=0.12)
        underestimation = NormalBeliefs(-0.03, np.sqrt(0.12**2 - 0.03**2))
        biased = planner.optimal_tax(wages, prefs, beliefs=underestimation)
        assert unbiased < informed < biased
        assert informed == pytest.approx(0.4453, abs=0.0003)
        assert unbiased == pytest.approx(0.4293, abs=0.0003)
        assert biased == pytest.approx(0.4563, abs=0.0003)

    def test_equal_dollar_weights_have_zero_tax_optimum(self, wages, prefs):
        result = SocialPlanner("equal").optimal_tax_result(wages, prefs)
        assert result.tax_rate == 0
        assert result.at_boundary
        assert result.search_range == (0, 0.8)

    def test_restricted_upper_boundary_is_reported(self, planner, wages, prefs):
        result = planner.optimal_tax_result(wages, prefs, search_range=(0, 0.01))
        assert result.tax_rate == 0.01
        assert result.at_boundary

    def test_belief_arguments_cannot_silently_override_each_other(
        self, planner, wages, prefs
    ):
        from taxuncertainty.models.beliefs import NormalBeliefs

        with pytest.raises(ValueError):
            planner.evaluate(0.3, wages, prefs, NormalBeliefs(), mean_error=-0.1)

    @pytest.mark.parametrize("wages", [[], [[20]], [20, -1], [np.nan], [np.inf]])
    def test_invalid_wages_rejected(self, planner, wages, prefs):
        with pytest.raises(ValueError):
            planner.evaluate(0.3, wages, prefs)

    def test_invalid_configuration_rejected(self, planner, wages, prefs):
        with pytest.raises(ValueError):
            SocialPlanner("income")
        with pytest.raises(ValueError):
            planner.optimal_tax(wages, prefs, n_grid=1)
        with pytest.raises(ValueError):
            planner.optimal_tax(wages, prefs, search_range=(0.8, 0))
