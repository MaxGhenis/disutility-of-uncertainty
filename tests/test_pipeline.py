"""Tests for the results pipeline — TDD: written before implementation."""

import json
import pytest
from pathlib import Path
from taxuncertainty.pipeline import generate_results
from taxuncertainty.results import Results


@pytest.fixture
def results_path(tmp_path):
    out = tmp_path / "results.json"
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
        for key in ["baseline", "sensitivity", "optimal_tax", "parameters"]:
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
        out1 = tmp_path / "r1.json"
        out2 = tmp_path / "r2.json"
        generate_results(output_path=out1)
        generate_results(output_path=out2)
        assert out1.read_text() == out2.read_text()


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
