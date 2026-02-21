"""Tests for labor supply and DWL — TDD: written before implementation."""

import pytest
import numpy as np
from taxuncertainty.models.preferences import QuasilinearIsoelastic
from taxuncertainty.models import labor


@pytest.fixture
def prefs():
    return QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)


@pytest.fixture
def prefs_low_e():
    return QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.3)


@pytest.fixture
def prefs_high_e():
    return QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.6)


class TestOptimalHours:
    def test_closed_form(self, prefs):
        """h* = (w(1-τ)/ψ)^ε"""
        w, tau = 20.0, 0.3
        expected = (w * (1 - tau) / prefs.psi) ** prefs.frisch_elasticity
        assert labor.optimal_hours(w, tau, prefs) == pytest.approx(expected)

    def test_zero_at_full_tax(self, prefs):
        assert labor.optimal_hours(20.0, 1.0, prefs) == 0.0

    def test_positive_for_interior_tax(self, prefs):
        assert labor.optimal_hours(20.0, 0.3, prefs) > 0

    def test_decreasing_in_tax_rate(self, prefs):
        h1 = labor.optimal_hours(20.0, 0.2, prefs)
        h2 = labor.optimal_hours(20.0, 0.4, prefs)
        assert h1 > h2

    def test_increasing_in_wage(self, prefs):
        h1 = labor.optimal_hours(15.0, 0.3, prefs)
        h2 = labor.optimal_hours(25.0, 0.3, prefs)
        assert h2 > h1


class TestMisperceivedHours:
    def test_equals_optimal_when_no_misperception(self, prefs):
        w, tau = 20.0, 0.3
        h_opt = labor.optimal_hours(w, tau, prefs)
        h_mis = labor.misperceived_hours(w, tau, tau, prefs)
        assert h_mis == pytest.approx(h_opt)

    def test_overwork_when_underestimate_tax(self, prefs):
        """If perceived tax < true tax, worker overestimates net wage → works more."""
        w, tau = 20.0, 0.3
        h_opt = labor.optimal_hours(w, tau, prefs)
        h_mis = labor.misperceived_hours(w, tau, 0.2, prefs)
        assert h_mis > h_opt

    def test_underwork_when_overestimate_tax(self, prefs):
        w, tau = 20.0, 0.3
        h_opt = labor.optimal_hours(w, tau, prefs)
        h_mis = labor.misperceived_hours(w, tau, 0.4, prefs)
        assert h_mis < h_opt


class TestIndividualDWL:
    def test_zero_when_no_misperception(self, prefs):
        assert labor.individual_dwl(20.0, 0.3, 0.3, prefs) == pytest.approx(0.0)

    def test_nonnegative(self, prefs):
        """Misperception can only reduce welfare."""
        for delta in [-0.2, -0.1, -0.05, 0.05, 0.1, 0.2]:
            dwl = labor.individual_dwl(20.0, 0.3, 0.3 + delta, prefs)
            assert (
                dwl >= -1e-12
            ), f"DWL should be non-negative, got {dwl} for delta={delta}"

    def test_approximately_symmetric(self, prefs):
        """DWL(+δ) ≈ DWL(-δ) for small δ (second-order effect)."""
        dwl_pos = labor.individual_dwl(20.0, 0.3, 0.35, prefs)
        dwl_neg = labor.individual_dwl(20.0, 0.3, 0.25, prefs)
        assert dwl_pos == pytest.approx(dwl_neg, rel=0.15)

    def test_quadratic_in_misperception(self, prefs):
        """DWL(2δ)/DWL(δ) ≈ 4 for small δ."""
        delta = 0.01
        dwl1 = labor.individual_dwl(20.0, 0.3, 0.3 + delta, prefs)
        dwl2 = labor.individual_dwl(20.0, 0.3, 0.3 + 2 * delta, prefs)
        assert dwl2 / dwl1 == pytest.approx(4.0, rel=0.15)

    def test_increases_with_wage(self, prefs):
        """Higher-wage workers lose more from same misperception."""
        dwl_low = labor.individual_dwl(15.0, 0.3, 0.4, prefs)
        dwl_high = labor.individual_dwl(30.0, 0.3, 0.4, prefs)
        assert dwl_high > dwl_low

    def test_higher_elasticity_higher_dwl(self, prefs_low_e, prefs_high_e):
        """More elastic labor supply → larger DWL from misperception."""
        dwl_low = labor.individual_dwl(20.0, 0.3, 0.4, prefs_low_e)
        dwl_high = labor.individual_dwl(20.0, 0.3, 0.4, prefs_high_e)
        assert dwl_high > dwl_low


class TestDWLApprox:
    def test_formula(self, prefs):
        """Approximate DWL ≈ ½ε·w·h*·σ²/(1-τ)"""
        w, tau, sigma = 20.0, 0.3, 0.10
        h_star = labor.optimal_hours(w, tau, prefs)
        expected = 0.5 * prefs.frisch_elasticity * w * h_star * sigma**2 / (1 - tau)
        assert labor.expected_dwl_approx(w, tau, sigma, prefs) == pytest.approx(
            expected
        )

    def test_zero_when_sigma_zero(self, prefs):
        assert labor.expected_dwl_approx(20.0, 0.3, 0.0, prefs) == 0.0

    def test_quadratic_in_sigma(self, prefs):
        dwl1 = labor.expected_dwl_approx(20.0, 0.3, 0.05, prefs)
        dwl2 = labor.expected_dwl_approx(20.0, 0.3, 0.10, prefs)
        assert dwl2 / dwl1 == pytest.approx(4.0)


class TestTaylorValidation:
    def test_approx_close_to_mc_at_calibrated_sigma(self, prefs):
        """Taylor approximation should be within 5% of MC at sigma=0.12 (calibrated value)."""
        w, tau, sigma = 20.0, 0.3, 0.12
        approx = labor.expected_dwl_approx(w, tau, sigma, prefs)
        mc = labor.expected_dwl_monte_carlo(
            w, tau, sigma, prefs, n_draws=100_000, seed=42
        )
        assert mc == pytest.approx(approx, rel=0.05)

    def test_approx_diverges_at_large_sigma(self, prefs):
        """Taylor approximation should diverge more from MC at large sigma."""
        w, tau = 20.0, 0.3
        # At sigma=0.12, should be close
        err_small = abs(
            labor.expected_dwl_approx(w, tau, 0.12, prefs)
            - labor.expected_dwl_monte_carlo(
                w, tau, 0.12, prefs, n_draws=100_000, seed=42
            )
        )
        # At sigma=0.30, should diverge more
        err_large = abs(
            labor.expected_dwl_approx(w, tau, 0.30, prefs)
            - labor.expected_dwl_monte_carlo(
                w, tau, 0.30, prefs, n_draws=100_000, seed=42
            )
        )
        assert err_large > err_small


class TestDWLMonteCarlo:
    def test_close_to_approx_for_small_sigma(self, prefs):
        """Analytical and Monte Carlo should agree for small σ."""
        w, tau, sigma = 20.0, 0.3, 0.03
        approx = labor.expected_dwl_approx(w, tau, sigma, prefs)
        mc = labor.expected_dwl_monte_carlo(
            w, tau, sigma, prefs, n_draws=50_000, seed=42
        )
        assert mc == pytest.approx(approx, rel=0.10)

    def test_mc_nonnegative(self, prefs):
        mc = labor.expected_dwl_monte_carlo(
            20.0, 0.3, 0.10, prefs, n_draws=10_000, seed=42
        )
        assert mc >= 0

    def test_mc_increases_with_sigma(self, prefs):
        mc1 = labor.expected_dwl_monte_carlo(
            20.0, 0.3, 0.05, prefs, n_draws=10_000, seed=42
        )
        mc2 = labor.expected_dwl_monte_carlo(
            20.0, 0.3, 0.15, prefs, n_draws=10_000, seed=42
        )
        assert mc2 > mc1
