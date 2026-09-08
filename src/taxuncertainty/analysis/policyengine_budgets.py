"""Provenance-recorded household grids from the canonical PolicyEngine wrapper.

This adapter performs no population aggregation and does not extract statutory
breakpoints. ``household_net_income`` includes valued noncash benefits such as
SNAP. Health benefits and health costs are explicitly excluded here. Therefore
earnings minus net income is an accounting residual for this outcome measure,
not a complete government budget score (in particular, health costs are omitted).
"""

import hashlib
import importlib.metadata as metadata
import json
import math
import platform
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from taxuncertainty.models.schedules import GridBudget

SCHEMA_VERSION = 1
HEALTH_PARAMETER = "gov.simulation.include_health_benefits_in_net_income"
MEASURE = "household_net_income"


def _canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _sha256(value):
    return hashlib.sha256(_canonical_json(value).encode()).hexdigest()


def _validate_axis(configuration, budget):
    """Require the complete observed grid to match the recorded single sweep."""
    try:
        axes = configuration["axes"]
        if not isinstance(axes, list) or len(axes) != 1:
            raise ValueError("Exactly one earnings axis is required")
        if not isinstance(axes[0], list) or len(axes[0]) != 1:
            raise ValueError("Exactly one earnings axis is required")
        axis = axes[0][0]
        if (
            axis["count"] != len(budget.earnings)
            or axis["min"] != 0
            or not math.isclose(
                axis["max"], budget.max_earnings, rel_tol=1e-7, abs_tol=1e-6
            )
            or axis["name"] != "employment_income"
            or axis["index"] != 0
            or axis["period"] != configuration["year"]
        ):
            raise ValueError("Grid does not match the configured earnings axis")
        # Country-model outputs use single precision; allow its rounding, not
        # arbitrary changes to the interior choice points.
        step = axis["max"] / (len(budget.earnings) - 1)
        if any(
            not math.isclose(y, index * step, rel_tol=1e-7, abs_tol=1e-6)
            for index, y in enumerate(budget.earnings)
        ):
            raise ValueError("Grid earnings do not match the equally spaced axis")
    except (KeyError, TypeError, IndexError) as exc:
        raise ValueError("Missing or invalid earnings axis provenance") from exc


def _installed_provenance():
    try:
        versions = {
            name: metadata.version(name)
            for name in (
                "policyengine",
                "policyengine-us",
                "policyengine-core",
                "numpy",
            )
        }
        manifest_path = Path(
            str(
                metadata.distribution("policyengine").locate_file(
                    "policyengine/data/bundle/manifest.json"
                )
            )
        )
    except metadata.PackageNotFoundError as exc:
        raise ModuleNotFoundError(
            "Household sampling requires the pinned `.[policyengine]` extra."
        ) from exc
    manifest = json.loads(manifest_path.read_text())
    if (
        versions["policyengine"] != manifest["policyengine_version"]
        or versions["policyengine-us"]
        != manifest["data_releases"]["us"]["model_package"]["version"]
    ):
        raise ValueError(
            "Installed PolicyEngine versions do not match the bundle manifest"
        )
    if (
        versions["policyengine-core"]
        != manifest["packages"]["policyengine-core"]["version"]
    ):
        raise ValueError(
            "Installed PolicyEngine core does not match the bundle manifest"
        )
    return {
        "package_versions": versions,
        "bundle_manifest": manifest,
        "bundle_manifest_sha256": _sha256(manifest),
        "python_version": platform.python_version(),
        "population_dataset_used": False,
        "source": "policyengine.us.calculate_household(axes=...)",
    }


@dataclass(frozen=True)
class HouseholdBudgetSample:
    """A finite observed choice set with verifiable generation metadata."""

    budget: GridBudget
    provenance: dict

    def to_dict(self):
        _validate_axis(self.provenance.get("configuration", {}), self.budget)
        payload = {
            "schema_version": SCHEMA_VERSION,
            "kind": "policyengine_household_grid",
            "earnings": list(self.budget.earnings),
            "net_incomes": list(self.budget.net_incomes),
            "discretization": self.budget.discretization(),
            "provenance": self.provenance,
        }
        return {**payload, "artifact_sha256": _sha256(payload)}

    def write(self, path):
        Path(path).write_text(
            json.dumps(self.to_dict(), indent=2, allow_nan=False) + "\n"
        )


def load_household_budget(path):
    """Reject legacy, damaged, or provenance-incomplete artifacts.

    Hashes detect accidental changes; they do not authenticate a trusted author.
    Installed PolicyEngine is not required to inspect a saved household grid.
    """
    payload = json.loads(Path(path).read_text())
    if payload.get("schema_version") != SCHEMA_VERSION or payload.get("kind") != (
        "policyengine_household_grid"
    ):
        raise ValueError(
            "Unsupported or legacy household artifact; provenance is required"
        )
    artifact_hash = payload.pop("artifact_sha256", None)
    if artifact_hash != _sha256(payload):
        raise ValueError("Household artifact hash mismatch")

    def require(condition):
        if not condition:
            raise ValueError("Missing or inconsistent household provenance")

    try:
        provenance = payload["provenance"]
        config = provenance["configuration"]
        versions = provenance["package_versions"]
        manifest = provenance["bundle_manifest"]
        require(provenance["source"] == "policyengine.us.calculate_household(axes=...)")
        require(provenance["population_dataset_used"] is False)
        require(provenance["configuration_sha256"] == _sha256(config))
        require(provenance["bundle_manifest_sha256"] == _sha256(manifest))
        require(versions["policyengine"] == manifest["policyengine_version"])
        require(
            versions["policyengine-us"]
            == manifest["data_releases"]["us"]["model_package"]["version"]
        )
        require(
            versions["policyengine-core"]
            == manifest["packages"]["policyengine-core"]["version"]
        )
        require(versions["numpy"])
        require(provenance["generated_at_utc"])
        require(provenance["net_income_measure"] == MEASURE)
        require(config["year"] and config["people"])
        require(config["tax_unit"]["filing_status"])
        require(config["household"]["state_code"])
        require(config["reform"][HEALTH_PARAMETER] is False)
    except (KeyError, TypeError) as exc:
        raise ValueError("Missing or inconsistent household provenance") from exc
    budget = GridBudget(payload["earnings"], payload["net_incomes"])
    if payload["discretization"] != budget.discretization():
        raise ValueError("Grid bounds do not match the saved discretization metadata")
    _validate_axis(config, budget)
    return HouseholdBudgetSample(budget, provenance)


def sample_us_household_budget(
    *, year, people, tax_unit, household, earnings_max, count, spm_unit=None
):
    """Execute one explicitly configured household earnings sweep.

    The first person's annual employment income varies from zero to
    ``earnings_max`` at ``count`` equally spaced points. Remaining inputs are
    held fixed; unspecified inputs use defaults of the recorded model version.
    The year, people, state, filing status, and finite grid are mandatory.
    A returned grid can only optimize over its supplied points. Refining a grid
    is a sensitivity check, not proof that all benefit cliffs were discovered.
    """
    if (
        isinstance(year, bool)
        or not isinstance(year, int)
        or not (1900 <= year <= 2200)
    ):
        raise ValueError("An explicit integer calendar year is required")
    if not people or not isinstance(people, (list, tuple)):
        raise ValueError("Explicit household people are required")
    if not tax_unit.get("filing_status") or not household.get("state_code"):
        raise ValueError("Explicit filing_status and state_code are required")
    if not math.isfinite(earnings_max) or earnings_max <= 0:
        raise ValueError("Maximum earnings must be finite and positive")
    if isinstance(count, bool) or not isinstance(count, int) or count < 2:
        raise ValueError("An integer grid count of at least two is required")
    configuration = json.loads(
        _canonical_json(
            {
                "year": year,
                "people": people,
                "tax_unit": tax_unit,
                "household": household,
                "spm_unit": spm_unit or {},
                "reform": {HEALTH_PARAMETER: False},
                "extra_variables": [
                    "household_health_benefits",
                    "household_health_costs",
                ],
                "axes": [
                    [
                        {
                            "name": "employment_income",
                            "min": 0,
                            "max": float(earnings_max),
                            "count": count,
                            "index": 0,
                            "period": year,
                        }
                    ]
                ],
            }
        )
    )
    provenance = _installed_provenance()
    import policyengine as pe

    result = pe.us.calculate_household(**configuration)
    budget = GridBudget(
        result.person[0].employment_income, result.household.household_net_income
    )
    _validate_axis(configuration, budget)
    if any(result.household.household_health_benefits) or any(
        result.household.household_health_costs
    ):
        raise ValueError(
            "Health exclusion was requested but not reflected in the output"
        )
    provenance.update(
        {
            "configuration": configuration,
            "configuration_sha256": _sha256(configuration),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "net_income_measure": MEASURE,
            "income_measure_scope": (
                "Includes model-valued noncash benefits such as SNAP and housing; "
                "excludes health benefits and health costs explicitly."
            ),
            "fiscal_scope": (
                "Earnings minus this net-income measure is an accounting residual, "
                "not a complete government budget score. Health spending and other "
                "omitted costs/externalities are not valued."
            ),
            "defaults": (
                "Unspecified household inputs use the recorded model's defaults."
            ),
            "interpolation": "none; statutory cliff positions are not inferred",
        }
    )
    return HouseholdBudgetSample(budget, provenance)
