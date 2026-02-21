"""Tests for the results pipeline — TDD: written before implementation."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch
from taxuncertainty.pipeline import generate_results
from taxuncertainty.results import Results


def _mock_empirical_section(cal, prefs):
    """Return a fake empirical section without running PolicyEngine."""
    return {
        "mtr_distribution": {
            "weighted_mean": 0.30,
            "weighted_std": 0.04,
            "p10": 0.15,
            "p25": 0.22,
            "p50": 0.30,
            "p75": 0.36,
            "p90": 0.42,
            "n_observations": 3,
            "total_weighted_workers": 3000.0,
            "mean_earnings": 60000.0,
        },
        "aggregate_dwl": 500000.0,
        "aggregate_dwl_billions": 0.0005,
        "quintiles": [
            {
                "quantile": q,
                "mean_earnings": 20000 + q * 20000,
                "mean_mtr": 0.20 + q * 0.04,
                "n_observations": 1,
                "weighted_workers": 600.0,
                "per_worker_dwl": 100.0 + q * 50,
                "quintile_total_dwl": (100.0 + q * 50) * 600,
                "share_of_total_dwl": 0.2,
            }
            for q in range(1, 6)
        ],
        "comparison": {
            "empirical_dwl_billions": 0.0005,
            "stylized_dwl_billions": 0.0006,
            "ratio": 0.83,
        },
    }


@pytest.fixture
def results_path(tmp_path):
    out = tmp_path / "results.json"
    with patch(
        "taxuncertainty.pipeline._generate_empirical_section",
        _mock_empirical_section,
    ):
        generate_results(output_path=out)
    return out


@pytest.fixture
def results_data(results_path):
    return json.loads(results_path.read_text())


class TestPipeline:
    def test_generates_valid_json(self, results_path):
        assert results_path.exists()
        data = json.loads(results_path.read_text())
        assert isinstance(data, dict)

    def test_results_contain_required_keys(self, results_data):
        for key in ["baseline", "sensitivity", "optimal_tax", "parameters", "empirical"]:
            assert key in results_data, f"Missing key: {key}"

    def test_baseline_has_required_fields(self, results_data):
        baseline = results_data["baseline"]
        for field in [
            "total_dwl_billions",
            "per_worker_dwl",
            "gdp_fraction_pct",
            "frisch_elasticity",
            "misperception_std",
        ]:
            assert field in baseline, f"Missing baseline field: {field}"

    def test_deterministic_with_seed(self, tmp_path):
        with patch(
            "taxuncertainty.pipeline._generate_empirical_section",
            _mock_empirical_section,
        ):
            out1 = tmp_path / "r1.json"
            out2 = tmp_path / "r2.json"
            generate_results(output_path=out1)
            generate_results(output_path=out2)
        assert out1.read_text() == out2.read_text()


class TestEmpiricalSection:
    def test_empirical_has_required_keys(self, results_data):
        emp = results_data["empirical"]
        for key in ["mtr_distribution", "aggregate_dwl", "aggregate_dwl_billions",
                     "quintiles", "comparison"]:
            assert key in emp, f"Missing empirical key: {key}"

    def test_mtr_distribution_stats(self, results_data):
        dist = results_data["empirical"]["mtr_distribution"]
        assert 0.0 < dist["weighted_mean"] < 1.0
        assert dist["weighted_std"] > 0

    def test_quintiles_present(self, results_data):
        quintiles = results_data["empirical"]["quintiles"]
        assert len(quintiles) == 5
        for q in quintiles:
            assert "per_worker_dwl" in q
            assert "share_of_total_dwl" in q

    def test_comparison_has_both_estimates(self, results_data):
        comp = results_data["empirical"]["comparison"]
        assert "empirical_dwl_billions" in comp
        assert "stylized_dwl_billions" in comp
        assert "ratio" in comp


class TestResultsSingleton:
    def test_loads_from_file(self, results_path):
        r = Results(results_path)
        assert r.baseline.total_dwl_billions > 0

    def test_attribute_access(self, results_path):
        r = Results(results_path)
        assert isinstance(r.baseline.gdp_fraction_pct, float)
        assert isinstance(r.baseline.per_worker_dwl, float)

    def test_formatted_values(self, results_path):
        r = Results(results_path)
        assert isinstance(r.baseline.total_dwl_billions_fmt, str)
        assert isinstance(r.baseline.gdp_fraction_pct_fmt, str)
