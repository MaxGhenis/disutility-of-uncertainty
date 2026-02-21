"""Tests for population welfare calculations — TDD: written before implementation."""

import pytest
import numpy as np
from taxuncertainty.models.preferences import QuasilinearIsoelastic
from taxuncertainty.analysis.welfare import PopulationWelfare
from taxuncertainty.analysis.calibration import Calibration


@pytest.fixture
def prefs():
    return QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.33)


@pytest.fixture
def calc():
    return PopulationWelfare()


class TestPopulationDWL:
    def test_zero_when_no_misperception(self, calc, prefs):
        wages = np.array([15.0, 20.0, 30.0])
        tax_rates = np.array([0.25, 0.30, 0.35])
        total = calc.total_dwl(wages, tax_rates, 0.0, prefs)
        assert total == pytest.approx(0.0)

    def test_positive_with_misperception(self, calc, prefs):
        wages = np.array([15.0, 20.0, 30.0])
        tax_rates = np.array([0.25, 0.30, 0.35])
        total = calc.total_dwl(wages, tax_rates, 0.12, prefs)
        assert total > 0

    def test_sum_of_individuals(self, calc, prefs):
        """Total DWL = sum of individual DWLs (using analytical approx)."""
        wages = np.array([15.0, 20.0, 30.0])
        tax_rates = np.array([0.25, 0.30, 0.35])
        sigma = 0.10
        total = calc.total_dwl(wages, tax_rates, sigma, prefs)
        individual_sum = calc.total_dwl_individual_sum(wages, tax_rates, sigma, prefs)
        assert total == pytest.approx(individual_sum)

    def test_analytical_aggregate_close_to_sum(self, calc, prefs):
        """Analytical shortcut ≈ sum for homogeneous tax rates."""
        n = 100
        wages = np.random.default_rng(42).lognormal(3.0, 0.5, n)
        tax_rates = np.full(n, 0.30)
        sigma = 0.10
        total_exact = calc.total_dwl(wages, tax_rates, sigma, prefs)
        total_analytical = calc.total_dwl_analytical(
            np.mean(wages), 0.30, sigma, prefs, n_workers=n
        )
        assert total_analytical == pytest.approx(total_exact, rel=0.10)


class TestGDPFraction:
    def test_in_range(self, calc, prefs):
        """DWL should be a small fraction of GDP."""
        wages = np.full(100, 27.5)  # ~$55k annual at 2000 hrs
        tax_rates = np.full(100, 0.30)
        sigma = 0.12
        dwl = calc.total_dwl(wages, tax_rates, sigma, prefs)
        gdp_for_100 = 100 * 55_000  # rough
        pct = dwl / gdp_for_100 * 100
        assert 0.01 < pct < 1.0


class TestCalibration:
    @pytest.fixture
    def cal(self):
        return Calibration()

    @pytest.fixture
    def baseline(self, cal):
        return cal.baseline_results()

    @pytest.fixture
    def table(self, cal):
        return cal.sensitivity_table()

    def test_baseline_dwl_positive(self, baseline):
        assert baseline["total_dwl_billions"] > 0

    def test_baseline_gdp_fraction_in_range(self, baseline):
        """Central estimate should be 0.05-0.5% of GDP."""
        assert 0.05 < baseline["gdp_fraction_pct"] < 0.5

    def test_per_worker_dwl_reasonable(self, baseline):
        """Per-worker DWL should be $50-$1000."""
        assert 50 < baseline["per_worker_dwl"] < 1000

    def test_sensitivity_table_covers_range(self, table):
        assert len(table) > 1
        for col in ["frisch_elasticity", "misperception_std", "gdp_fraction_pct"]:
            assert col in table.columns

    def test_sensitivity_monotonic_in_sigma(self, table):
        """DWL increases monotonically with misperception."""
        for eps in table["frisch_elasticity"].unique():
            subset = table[table["frisch_elasticity"] == eps].sort_values(
                "misperception_std"
            )
            dwls = subset["gdp_fraction_pct"].values
            assert all(dwls[i] <= dwls[i + 1] for i in range(len(dwls) - 1))

    def test_sensitivity_monotonic_in_elasticity(self, table):
        """DWL increases monotonically with Frisch elasticity."""
        for sigma in table["misperception_std"].unique():
            subset = table[table["misperception_std"] == sigma].sort_values(
                "frisch_elasticity"
            )
            dwls = subset["gdp_fraction_pct"].values
            assert all(dwls[i] <= dwls[i + 1] for i in range(len(dwls) - 1))
