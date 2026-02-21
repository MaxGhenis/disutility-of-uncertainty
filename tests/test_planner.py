"""Tests for social planner — TDD: written before implementation."""

import pytest
import numpy as np
from taxuncertainty.models.preferences import QuasilinearIsoelastic
from taxuncertainty.models.planner import SocialPlanner


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
        w_uncertain = planner.social_welfare(0.3, wages, prefs, misperception_std=0.1, seed=42)
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
        tau_uncertain = planner.optimal_tax(wages, prefs, misperception_std=0.1, seed=42)
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
