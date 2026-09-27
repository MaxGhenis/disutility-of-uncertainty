"""Saved provenance checks and opt-in validation of real household extraction."""

import copy
import hashlib
import json
from pathlib import Path

import pytest

from taxuncertainty.analysis.policyengine_budgets import (
    HouseholdBudgetSample,
    load_household_budget,
    sample_us_household_budget,
)
from taxuncertainty.models.preferences import QuasilinearIsoelastic
from taxuncertainty.models.schedules import GridBudget, compare_budgets, optimize_budget

FIXTURE = Path(__file__).parents[1] / "src/taxuncertainty/data/household_budget.json"


def artifact_hash(payload):
    return hashlib.sha256(
        json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
    ).hexdigest()


def test_saved_household_grid_has_complete_provenance_and_no_population_weights():
    sample = load_household_budget(FIXTURE)
    assert sample.provenance["population_dataset_used"] is False
    assert sample.provenance["configuration"]["year"] == 2024
    assert sample.provenance["configuration"]["household"]["state_code"] == "TX"
    assert sample.provenance["package_versions"]["policyengine"] == "5.3.0"
    assert sample.budget.max_grid_gap == 250
    assert sample.budget.net_income(0) == 3495
    assert sample.budget.net_income(50000) == 42159
    assert "excludes health" in sample.provenance["income_measure_scope"]
    assert sample.budget.discretization()["continuous_utility_error_bound"] is None


def test_saved_fixture_roundtrip(tmp_path):
    original = load_household_budget(FIXTURE)
    target = tmp_path / "household.json"
    original.write(target)
    assert load_household_budget(target).to_dict() == original.to_dict()


@pytest.mark.parametrize(
    "mutation", ["output", "config", "missing_provenance", "version"]
)
def test_altered_or_missing_provenance_is_rejected(tmp_path, mutation):
    payload = copy.deepcopy(json.loads(FIXTURE.read_text()))
    if mutation == "output":
        payload["net_incomes"][0] += 1
    elif mutation == "config":
        payload["provenance"]["configuration"]["year"] = 2025
    elif mutation == "missing_provenance":
        del payload["provenance"]["bundle_manifest"]
    elif mutation == "version":
        payload["provenance"]["package_versions"]["policyengine-us"] = "unknown"
    if mutation != "output":
        payload.pop("artifact_sha256")
        payload["artifact_sha256"] = artifact_hash(payload)
    target = tmp_path / "invalid.json"
    target.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="hash mismatch|provenance"):
        load_household_budget(target)


def test_year_only_legacy_cache_is_rejected(tmp_path):
    target = tmp_path / "legacy.json"
    target.write_text(json.dumps({"year": 2024, "earnings": [100], "mtr": [0.99]}))
    with pytest.raises(ValueError, match="legacy.*provenance"):
        load_household_budget(target)


@pytest.mark.parametrize("mutation", ["interior_point", "extra_axis"])
def test_loader_rejects_inconsistent_full_grid_even_with_refreshed_hashes(
    tmp_path, mutation
):
    payload = json.loads(FIXTURE.read_text())
    if mutation == "interior_point":
        payload["earnings"][1] = 123
        changed = GridBudget(payload["earnings"], payload["net_incomes"])
        payload["discretization"] = changed.discretization()
    else:
        config = payload["provenance"]["configuration"]
        config["axes"].append(copy.deepcopy(config["axes"][0]))
        payload["provenance"]["configuration_sha256"] = artifact_hash(config)
    payload.pop("artifact_sha256")
    payload["artifact_sha256"] = artifact_hash(payload)
    target = tmp_path / "inconsistent.json"
    target.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="axis"):
        load_household_budget(target)


def test_writer_cannot_reuse_provenance_for_a_different_earnings_grid(tmp_path):
    sample = load_household_budget(FIXTURE)
    earnings = list(sample.budget.earnings)
    earnings[1] = 123
    inconsistent = HouseholdBudgetSample(
        GridBudget(earnings, sample.budget.net_incomes), sample.provenance
    )
    with pytest.raises(ValueError, match="equally spaced axis"):
        inconsistent.write(tmp_path / "invalid.json")


def test_grid_refinement_is_a_finite_choice_sensitivity_check():
    fine = load_household_budget(FIXTURE).budget
    coarse = GridBudget(fine.earnings[::2], fine.net_incomes[::2])
    wage = 27.5
    elasticity = 0.5
    prefs = QuasilinearIsoelastic(
        psi=wage * 0.7 / (2000 ** (1 / elasticity)), frisch_elasticity=elasticity
    )
    fine_choice = optimize_budget(fine, wage, prefs)
    coarse_choice = optimize_budget(coarse, wage, prefs)
    assert fine_choice.utility >= coarse_choice.utility
    assert abs(fine_choice.earnings - coarse_choice.earnings) <= coarse.max_grid_gap
    # This is an observed sensitivity result for this fixture, not a certified
    # continuous-choice error bound or evidence of every cliff's position.
    assert fine_choice.utility - coarse_choice.utility < 5
    assert compare_budgets(fine, fine, wage, prefs).social_loss == 0


@pytest.mark.parametrize(
    "overrides",
    [
        {"year": None},
        {"people": []},
        {"tax_unit": {}},
        {"household": {}},
        {"count": 1},
        {"earnings_max": float("inf")},
    ],
)
def test_sampler_requires_explicit_valid_configuration(overrides):
    config = {
        "year": 2024,
        "people": [{"age": 40}],
        "tax_unit": {"filing_status": "SINGLE"},
        "household": {"state_code": "TX"},
        "count": 5,
        "earnings_max": 100000,
    }
    config.update(overrides)
    with pytest.raises(ValueError):
        sample_us_household_budget(**config)


@pytest.mark.policyengine
def test_live_household_grid_reproduces_saved_values_and_coarse_grid():
    """Execute actual wrapper calls without downloading any population data."""
    saved = load_household_budget(FIXTURE)
    config = saved.provenance["configuration"]
    kwargs = {
        key: config[key]
        for key in ("year", "people", "tax_unit", "household", "spm_unit")
    }
    fine = sample_us_household_budget(**kwargs, earnings_max=100000, count=401)
    coarse = sample_us_household_budget(**kwargs, earnings_max=100000, count=201)
    assert fine.provenance["package_versions"] == saved.provenance["package_versions"]
    assert fine.budget.earnings == saved.budget.earnings
    assert fine.budget.net_incomes == pytest.approx(saved.budget.net_incomes, abs=0.01)
    assert coarse.budget.earnings == fine.budget.earnings[::2]
    assert coarse.budget.net_incomes == pytest.approx(
        fine.budget.net_incomes[::2], abs=0.01
    )
