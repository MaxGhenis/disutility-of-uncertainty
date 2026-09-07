"""Reproduction, accounting, and stale-publication protections."""

import builtins
import json
from dataclasses import asdict
from pathlib import Path

import pytest

from taxuncertainty.pipeline import (
    check_artifacts,
    compute_results,
    generate_figures,
    generate_results,
    main,
    paper_artifacts,
)
from taxuncertainty.results import Results


@pytest.fixture(scope="module")
def results():
    return compute_results()


def test_headline_reports_conditional_accounting_not_national_dwl(results):
    assert results["schema_version"] == 2
    assert "not a national" in results["status"]
    assert results["assumptions"]["error_source"]["status"] == "assumed"
    for old_field in (
        "empirical",
        "baseline",
        "total_dwl_billions",
        "gdp_fraction_pct",
    ):
        assert old_field not in results
    for scenario in results["scenarios"]:
        worker = scenario["worker"]
        assert worker["social_loss"] == pytest.approx(
            worker["private_regret"] - worker["revenue_change"], abs=1e-8
        )


def test_equal_rmse_does_not_force_same_optimal_tax_direction(results):
    inverse = {
        row["id"]: row["optimum"]["tax_rate"]
        for row in results["planner"]["inverse_wage"]
    }
    assert inverse["unbiased"] < inverse["informed"] < inverse["bias_minus_3"]
    assert results["planner"]["equal"][0]["optimum"]["tax_rate"] == 0
    assert results["planner"]["equal"][0]["optimum"]["at_boundary"]


def test_approximation_error_and_quadrature_are_reported(results):
    cap = next(
        row for row in results["approximation_accuracy"] if row["tax_rate"] == 0.99
    )
    assert cap["latent_ratio"] > 8
    assert results["validation"]["baseline_social_quadrature_difference"] < 0.00001


def test_pipeline_does_not_import_policyengine(monkeypatch):
    original = builtins.__import__

    def reject(name, *args, **kwargs):
        if name == "policyengine" or name.startswith("policyengine_"):
            raise AssertionError("Default pipeline must not run PolicyEngine")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", reject)
    assert compute_results()["household_fixture"]["status"].startswith(
        "executed household"
    )


def test_generate_reproducible_json_and_results_access(tmp_path, results):
    first, second = tmp_path / "one.json", tmp_path / "two.json"
    generate_results(first)
    generate_results(second)
    assert first.read_bytes() == second.read_bytes()
    loaded = Results(first)
    assert loaded.schema_version == 2
    assert loaded.scenarios[1].worker.private_regret_fmt == "190.11"
    assert json.loads(first.read_text()) == results


def test_seed_changes_synthetic_planner_but_not_worker():
    a, b = compute_results(42), compute_results(43)
    assert a["scenarios"] == b["scenarios"]
    assert a["planner"] != b["planner"]


def test_paper_values_follow_results_and_no_longer_embed_old_percentiles(results):
    changed = json.loads(json.dumps(results))
    changed["scenarios"][1]["worker"]["private_regret"] = 1234.56
    original = paper_artifacts(results)
    altered = paper_artifacts(changed)
    assert original["generated/scenarios.md"] != altered["generated/scenarios.md"]
    assert json.loads(altered["_variables.yml"])["unbiased_private"] == "1234.56"
    assert "1,234.56" in altered["generated/scenarios.md"]


def test_cli_check_detects_results_prose_and_figure_drift(tmp_path):
    output = tmp_path / "data/results.json"
    paper = tmp_path / "paper"
    args = ["--output", str(output), "--paper-dir", str(paper)]
    assert main(args) == 0
    assert main(args + ["--check"]) == 0
    generated = paper / "generated/scenarios.md"
    generated.write_text(generated.read_text().replace("190.11", "999.99"))
    assert main(args + ["--check"]) == 1
    assert main(args) == 0
    figure = paper / "generated/welfare.png"
    figure.write_bytes(figure.read_bytes() + b"corrupted")
    assert main(args + ["--check"]) == 1
    assert main(args) == 0
    data = json.loads(output.read_text())
    data["scenarios"][1]["worker"]["social_loss"] += 100
    output.write_text(json.dumps(data))
    assert main(args + ["--check"]) == 1


def test_household_fixture_is_provenance_known_and_finite_grid(results):
    fixture = results["household_fixture"]
    assert len(fixture["artifact_sha256"]) == 64
    assert fixture["package_versions"]["policyengine"] == "5.3.0"
    assert fixture["discretization"]["continuous_utility_error_bound"] is None
    assert fixture["discretization"]["maximum_grid_gap"] == 250
    assert fixture["selected_outcomes"][2]["net_income"] == 42159


def test_nonlinear_examples_keep_private_and_fiscal_effects_separate(results):
    for row in results["nonlinear_examples"]:
        outcome = row["outcome"]
        assert outcome["private_regret"] >= 0
        assert outcome["social_loss"] == pytest.approx(
            outcome["private_regret"] - outcome["revenue_change"]
        )
        assert row["status"].startswith("synthetic")


def test_observed_calibration_drives_paper_but_never_replaces_belief_inputs(results):
    empirical = results["observed_calibration"]
    assert not empirical["welfare_input_replaced"]
    assert not empirical["study2"]["latent_beliefs_identified"]
    assert results["scenarios"][1]["beliefs"]["std_error"] == 0.12
    changed = json.loads(json.dumps(results))
    changed["observed_calibration"]["study2"]["interval_bounds"]["author"]["bias"][
        0
    ] = 0.1234
    assert "12.34 to" in paper_artifacts(changed)["generated/empirical-intervals.md"]
    assert (
        paper_artifacts(changed)["generated/scenarios.md"]
        == paper_artifacts(results)["generated/scenarios.md"]
    )
