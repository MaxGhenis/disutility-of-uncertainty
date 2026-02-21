"""Tests for empirical MTR distribution module."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from taxuncertainty.analysis.empirical import EmpiricalMTR


class MockMicroSeries:
    """Minimal mock for PolicyEngine MicroSeries."""

    def __init__(self, values):
        self.values = np.asarray(values, dtype=np.float32)


def _make_mock_sim():
    """Create a mock Microsimulation with realistic test data."""
    n = 100
    rng = np.random.default_rng(42)

    # Mix of ages: some children, working-age, elderly
    ages = np.concatenate([
        rng.integers(0, 17, size=20),      # children
        rng.integers(18, 64, size=60),      # working-age
        rng.integers(65, 90, size=20),      # elderly
    ]).astype(np.float32)

    # Employment income: zero for children/some elderly, positive for workers
    emp_inc = np.zeros(n, dtype=np.float32)
    emp_inc[20:75] = rng.lognormal(10.5, 0.8, size=55).astype(np.float32)

    # MTRs: mostly 0.15-0.45, with some extreme values
    mtr = np.zeros(n, dtype=np.float32)
    mtr[20:75] = rng.normal(0.30, 0.10, size=55).astype(np.float32)
    mtr[25] = -0.5   # benefit cliff (negative MTR)
    mtr[30] = 1.5    # extreme benefit phase-out
    mtr[35] = 2.0    # another extreme

    weights = rng.uniform(500, 3000, size=n).astype(np.float32)

    sim = MagicMock()

    def mock_calculate(var_name, year):
        data = {
            "employment_income": emp_inc,
            "marginal_tax_rate": mtr,
            "person_weight": weights,
            "age": ages,
        }
        return MockMicroSeries(data[var_name])

    sim.calculate = mock_calculate
    return sim


class TestEmpiricalMTRMocked:
    """Tests using mocked PolicyEngine data."""

    @pytest.fixture
    def empirical(self, tmp_path):
        with patch(
            "policyengine_us.Microsimulation",
            return_value=_make_mock_sim(),
        ):
            with patch(
                "taxuncertainty.analysis.empirical.CACHE_DIR", tmp_path
            ):
                return EmpiricalMTR(year=2024, cache=False)

    def test_filters_to_working_age_earners(self, empirical):
        """Should exclude children, elderly, and zero-earners."""
        assert len(empirical.earnings) > 0
        assert len(empirical.earnings) < 100  # filtered some out
        assert all(empirical.earnings > 0)

    def test_clips_mtr_range(self, empirical):
        """MTRs should be clipped to [0, 0.99]."""
        assert empirical.mtr.min() >= 0.0
        assert empirical.mtr.max() <= 0.99

    def test_arrays_same_length(self, empirical):
        assert len(empirical.earnings) == len(empirical.mtr) == len(empirical.weights)

    def test_summary_stats_keys(self, empirical):
        stats = empirical.summary_stats()
        expected_keys = {
            "weighted_mean", "weighted_std", "p10", "p25", "p50", "p75", "p90",
            "n_observations", "total_weighted_workers", "mean_earnings",
        }
        assert set(stats.keys()) == expected_keys

    def test_summary_stats_values(self, empirical):
        stats = empirical.summary_stats()
        assert 0.0 < stats["weighted_mean"] < 1.0
        assert stats["weighted_std"] > 0
        assert stats["n_observations"] > 0
        assert stats["total_weighted_workers"] > 0
        assert stats["mean_earnings"] > 0

    def test_quintile_results(self, empirical):
        quintiles = empirical.quintile_results()
        assert len(quintiles) == 5
        # Income should be monotonically increasing across quintiles
        incomes = [q["mean_earnings"] for q in quintiles]
        assert all(incomes[i] <= incomes[i + 1] for i in range(4))

    def test_decile_results(self, empirical):
        deciles = empirical.decile_results()
        assert len(deciles) == 10

    def test_cache_roundtrip(self, tmp_path):
        """Cached results should match original."""
        with patch(
            "policyengine_us.Microsimulation",
            return_value=_make_mock_sim(),
        ):
            with patch(
                "taxuncertainty.analysis.empirical.CACHE_DIR", tmp_path
            ):
                e1 = EmpiricalMTR(year=2024, cache=True)
                stats1 = e1.summary_stats()

        # Load from cache (don't mock Microsimulation — it shouldn't be called)
        with patch(
            "taxuncertainty.analysis.empirical.CACHE_DIR", tmp_path
        ):
            e2 = EmpiricalMTR(year=2024, cache=True)
            stats2 = e2.summary_stats()

        assert stats1["weighted_mean"] == pytest.approx(stats2["weighted_mean"])
        assert stats1["n_observations"] == stats2["n_observations"]


@pytest.mark.slow
class TestEmpiricalMTRIntegration:
    """Integration tests that run actual PolicyEngine-US microsimulation."""

    @pytest.fixture(scope="class")
    def empirical(self, tmp_path_factory):
        cache_dir = tmp_path_factory.mktemp("pe_cache")
        with patch(
            "taxuncertainty.analysis.empirical.CACHE_DIR", cache_dir
        ):
            return EmpiricalMTR(year=2024, cache=True)

    def test_weighted_mean_mtr_near_cbo(self, empirical):
        """Weighted mean MTR should be in the neighborhood of CBO's 0.30."""
        stats = empirical.summary_stats()
        assert 0.15 < stats["weighted_mean"] < 0.45

    def test_reasonable_number_of_workers(self, empirical):
        stats = empirical.summary_stats()
        # Should represent roughly 100-200 million weighted workers
        assert 50_000_000 < stats["total_weighted_workers"] < 250_000_000

    def test_quintile_income_ordering(self, empirical):
        quintiles = empirical.quintile_results()
        incomes = [q["mean_earnings"] for q in quintiles]
        assert all(incomes[i] <= incomes[i + 1] for i in range(4))

    def test_mean_earnings_reasonable(self, empirical):
        stats = empirical.summary_stats()
        # Mean earnings should be roughly $40k-$120k
        assert 40_000 < stats["mean_earnings"] < 120_000
