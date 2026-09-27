"""Conditional national aggregation of misperception effects.

This module applies the note's per-worker model to every working-age earner
in the managed PolicyEngine-US population microsimulation. It replaces the
retired clipped-MTR calculation (``analysis.empirical``) with these rules:

- Each person's marginal tax rate, as computed by PolicyEngine, is the slope
  of a locally linear budget; observed employment income is their informed
  earnings. PolicyEngine's ``marginal_tax_rate`` is one minus the change in
  household net income (health benefits excluded) when the person's earnings
  rise by the ``marginal_tax_rate_delta`` parameter ($1,000). By default it
  is computed only for the ``marginal_tax_rate_adults`` (two) highest-earning
  adults in each household and is zero by construction for everyone else, so
  the extraction raises that limit to cover every eligible earner and
  reports any record still without a computed rate separately. The model
  does not see benefit cliffs or other nonlinearities beyond the local
  slope.
- Expected private regret, revenue change and social loss come from exact
  quadrature (``models.accounting.evaluate_worker``), never the Taylor
  formula. The Taylor value is reported only as a diagnostic.
- Marginal rates are never clipped. Rates outside the belief model's domain
  are counted and reported separately: a rate of at least one implies zero
  informed hours on a linear budget, which contradicts positive observed
  earnings; a negative rate lies below the default perceived-rate bounds.
  A sensitivity variant evaluates negative rates with no lower belief bound.
- Every group total is a sum of per-person amounts, so quintile and band
  totals add up to the national total.
- Only aggregates are stored. The microdata are not redistributed.

Results are conditional on the assumed elasticity and error distribution.
They are not an identified estimate of the welfare cost of misperception.

Run ``python -m taxuncertainty.analysis.national`` with the ``policyengine``
extra installed to rebuild ``data/national_estimate.json``.
"""

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from taxuncertainty.analysis.calibration import Illustration
from taxuncertainty.models.accounting import evaluate_worker
from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.preferences import QuasilinearIsoelastic

SCHEMA_VERSION = 1
ARTIFACT_PATH = Path(__file__).parents[1] / "data/national_estimate.json"
YEAR = 2024
MIN_AGE, MAX_AGE = 18, 64
QUINTILES = 5
PERCENTILES = (10, 25, 50, 75, 90)
# Band edges for marginal rates; the outer bands hold out-of-domain records.
MTR_BAND_EDGES = (
    -np.inf,
    0.0,
    0.1,
    0.2,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.8,
    0.9,
    1.0,
    np.inf,
)
SENSITIVITY_ELASTICITIES = (0.25, 0.33, 0.50)
SENSITIVITY_STD_ERRORS = (0.08, 0.12, 0.15)
OUTCOMES = ("private_regret", "revenue_change", "social_loss")


@dataclass(frozen=True)
class PersonRecords:
    """Person-level employment income, marginal tax rate and survey weight."""

    earnings: np.ndarray
    marginal_tax_rate: np.ndarray
    weight: np.ndarray

    def __post_init__(self):
        arrays = [
            np.asarray(a, dtype=float)
            for a in (self.earnings, self.marginal_tax_rate, self.weight)
        ]
        if len({a.shape for a in arrays}) != 1 or arrays[0].ndim != 1:
            raise ValueError("records must be matching one-dimensional arrays")
        if not all(np.all(np.isfinite(a)) for a in arrays):
            raise ValueError("records must be finite")
        if np.any(arrays[0] <= 0):
            raise ValueError("earnings must be positive")
        if np.any(arrays[2] < 0):
            raise ValueError("weights must be nonnegative")
        for name, array in zip(("earnings", "marginal_tax_rate", "weight"), arrays):
            object.__setattr__(self, name, array)

    def subset(self, mask):
        return PersonRecords(
            self.earnings[mask], self.marginal_tax_rate[mask], self.weight[mask]
        )

    def digest(self):
        """SHA-256 of the float64 arrays, identifying the aggregated input."""
        h = hashlib.sha256()
        for array in (self.earnings, self.marginal_tax_rate, self.weight):
            h.update(np.ascontiguousarray(array, dtype="<f8").tobytes())
        return h.hexdigest()


def weighted_percentile(values, weights, percentile):
    """Weighted percentile by linear interpolation between weight midpoints.

    Zero-weight observations are dropped first: they carry no population
    mass, so they must not anchor an interpolation point.
    """
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    if values.shape != weights.shape or values.ndim != 1:
        raise ValueError("values and weights must be matching vectors")
    if np.any(weights < 0) or not np.all(np.isfinite(weights)):
        raise ValueError("weights must be finite and nonnegative")
    if not 0 <= percentile <= 100:
        raise ValueError("percentile must lie in [0, 100]")
    keep = weights > 0
    if not keep.any():
        raise ValueError("at least one weight must be positive")
    values, weights = values[keep], weights[keep]
    order = np.argsort(values, kind="stable")
    values, weights = values[order], weights[order]
    cumulative = np.cumsum(weights)
    midpoints = 100 * (cumulative - 0.5 * weights) / cumulative[-1]
    return float(np.interp(percentile, midpoints, values))


def quantile_labels(records, n_groups=QUINTILES):
    """Earnings-quantile label (1 to ``n_groups``) for every record.

    Records are ranked by earnings, then marginal rate, then weight, so tied
    records are ordered by their own values rather than by input position.
    A record belongs to group ``q`` when cumulative weight through it lies in
    ``((q - 1) / n, q / n]`` of the total. Every record gets exactly one label.
    """
    order = np.lexsort((records.weight, records.marginal_tax_rate, records.earnings))
    cumulative = np.cumsum(records.weight[order])
    if cumulative[-1] <= 0:
        raise ValueError("total weight must be positive")
    groups = np.ceil(cumulative / cumulative[-1] * n_groups).astype(int)
    labels = np.empty(len(order), dtype=int)
    labels[order] = np.clip(groups, 1, n_groups)
    return labels


def per_dollar_outcomes(tax_rates, elasticity, beliefs_for):
    """Expected outcomes per dollar of informed earnings, by marginal rate.

    ``beliefs_for(tax_rate)`` returns the ``NormalBeliefs`` for that rate.
    A worker with wage one and ``psi = 1 - tax_rate`` has informed earnings
    of exactly one, and every outcome scales with informed earnings, so each
    distinct rate needs one exact evaluation.
    """
    rates = np.asarray(tax_rates, dtype=float)
    if np.any(rates >= 1):
        raise ValueError("per-dollar outcomes require marginal rates below one")
    unique, inverse = np.unique(rates, return_inverse=True)
    table = {name: np.empty(len(unique)) for name in (*OUTCOMES, "second_order")}
    for i, rate in enumerate(unique):
        rate = float(rate)
        beliefs = beliefs_for(rate)
        prefs = QuasilinearIsoelastic(1.0 - rate, elasticity)
        outcome = evaluate_worker(1.0, rate, prefs, beliefs)
        for name in OUTCOMES:
            table[name][i] = getattr(outcome, name)
        # Historical interior approximation with the latent second moment.
        table["second_order"][i] = (
            0.5 * elasticity * beliefs.latent_rmse**2 / (1.0 - rate)
        )
    return {name: values[inverse] for name, values in table.items()}


def _sums(records, per_dollar, mask=None):
    mask = np.ones(len(records.weight), bool) if mask is None else mask
    dollars = records.weight[mask] * records.earnings[mask]
    out = {
        "weighted_workers": float(records.weight[mask].sum()),
        "total_earnings": float(dollars.sum()),
    }
    for name in (*OUTCOMES, "second_order"):
        out[name] = float(dollars @ per_dollar[name][mask])
    return out


def _representative(records, per_dollar, at_mean, name):
    """Population total versus the per-dollar value at weighted means.

    With ``g`` the per-dollar outcome, ``N`` total weight and weighted means
    ``e_bar`` and ``tau_bar``, the identity
    ``population - at_means = rate_dispersion + covariance`` holds exactly,
    where ``rate_dispersion = N e_bar (E[g] - g(tau_bar))`` and
    ``covariance = N Cov(earnings, g)``.
    """
    w, e, g = records.weight, records.earnings, per_dollar[name]
    n = float(w.sum())
    e_bar = float(w @ e) / n
    mean_g = float(w @ g) / n
    mean_eg = float(w @ (e * g)) / n
    return {
        "population": n * mean_eg,
        "at_means": n * e_bar * at_mean,
        "rate_dispersion": n * e_bar * (mean_g - at_mean),
        "covariance": n * (mean_eg - e_bar * mean_g),
    }


def default_beliefs(std_error):
    """The note's belief model: mean-zero errors censored to [0, 1]."""
    return lambda rate: NormalBeliefs(0.0, std_error)


def subsidy_beliefs(std_error):
    """Sensitivity: no lower perceived-rate bound, so subsidies are coherent."""
    return lambda rate: NormalBeliefs(0.0, std_error, lower_bound=None)


def aggregate(records, elasticity, std_error):
    """Aggregate per-person exact outcomes for one set of assumptions.

    Records with ``0 <= rate < 1`` form the main estimate under the note's
    default belief model. The ``subsidy_inclusive`` variant adds records
    with negative rates, evaluating all rates below one with no lower bound.
    """
    rates = records.marginal_tax_rate
    in_domain = (rates >= 0) & (rates < 1)
    main = records.subset(in_domain)
    per_dollar = per_dollar_outcomes(
        main.marginal_tax_rate, elasticity, default_beliefs(std_error)
    )
    below_one = rates < 1
    inclusive = records.subset(below_one)
    inclusive_per_dollar = per_dollar_outcomes(
        inclusive.marginal_tax_rate, elasticity, subsidy_beliefs(std_error)
    )
    return (
        main,
        per_dollar,
        _sums(main, per_dollar),
        _sums(inclusive, inclusive_per_dollar),
    )


def national_estimate(records, elasticity=None, std_error=None):
    """Build every aggregate for the committed artifact from person records."""
    illustration = Illustration()
    elasticity = illustration.elasticity if elasticity is None else elasticity
    std_error = illustration.error_rmse if std_error is None else std_error
    rates = records.marginal_tax_rate
    main, per_dollar, totals, inclusive = aggregate(records, elasticity, std_error)

    domain = {}
    for key, mask in (
        ("negative_rate", rates < 0),
        ("in_domain", (rates >= 0) & (rates < 1)),
        ("rate_at_least_one", rates >= 1),
    ):
        domain[key] = {
            "records": int(mask.sum()),
            "weighted_workers": float(records.weight[mask].sum()),
            "total_earnings": float(records.weight[mask] @ records.earnings[mask]),
        }

    labels = quantile_labels(main)
    quintiles = []
    for q in range(1, QUINTILES + 1):
        mask = labels == q
        row = _sums(main, per_dollar, mask)
        # A group is empty only when there are fewer records than groups.
        row.update(
            {
                "quintile": q,
                "records": int(mask.sum()),
                "min_earnings": (
                    float(main.earnings[mask].min()) if mask.any() else None
                ),
                "max_earnings": (
                    float(main.earnings[mask].max()) if mask.any() else None
                ),
                "mean_marginal_rate": (
                    float(main.weight[mask] @ main.marginal_tax_rate[mask])
                    / row["weighted_workers"]
                    if mask.any()
                    else None
                ),
            }
        )
        quintiles.append(row)

    bands = []
    for lo, hi in zip(MTR_BAND_EDGES[:-1], MTR_BAND_EDGES[1:]):
        mask = (rates >= lo) & (rates < hi)
        row = {
            "rate_min": None if lo == -np.inf else lo,
            "rate_max_exclusive": None if hi == np.inf else hi,
            "records": int(mask.sum()),
            "weighted_workers": float(records.weight[mask].sum()),
            "total_earnings": float(records.weight[mask] @ records.earnings[mask]),
        }
        if lo >= 0 and hi <= 1:
            sub = (main.marginal_tax_rate >= lo) & (main.marginal_tax_rate < hi)
            row.update(
                {
                    k: v
                    for k, v in _sums(main, per_dollar, sub).items()
                    if k in (*OUTCOMES, "second_order")
                }
            )
        bands.append(row)

    n = float(main.weight.sum())
    mean_rate = float(main.weight @ main.marginal_tax_rate) / n
    at_mean = per_dollar_outcomes([mean_rate], elasticity, default_beliefs(std_error))
    representative = {
        "mean_earnings": float(main.weight @ main.earnings) / n,
        "mean_marginal_rate": mean_rate,
        "weighted_workers": n,
        "second_order": _representative(
            main, per_dollar, float(at_mean["second_order"][0]), "second_order"
        ),
        "social_loss": _representative(
            main, per_dollar, float(at_mean["social_loss"][0]), "social_loss"
        ),
    }

    sensitivity = []
    for eps in SENSITIVITY_ELASTICITIES:
        for sd in SENSITIVITY_STD_ERRORS:
            if (eps, sd) == (elasticity, std_error):
                row = totals
            else:
                row = _sums(
                    main,
                    per_dollar_outcomes(
                        main.marginal_tax_rate, eps, default_beliefs(sd)
                    ),
                )
            sensitivity.append(
                {
                    "elasticity": eps,
                    "std_error": sd,
                    **{k: row[k] for k in (*OUTCOMES, "second_order")},
                }
            )

    return {
        "assumptions": {
            "elasticity": elasticity,
            "latent_error_mean": 0.0,
            "latent_error_std": std_error,
            "perception_bounds": [0.0, 1.0],
            "fiscal_closure": (
                "revenue changes rebated lump sum; private utility and revenue "
                "valued equally"
            ),
            "budget": (
                "locally linear at each person's PolicyEngine marginal tax rate; "
                "observed employment income is informed earnings"
            ),
            "population": (
                f"people aged {MIN_AGE}-{MAX_AGE} with positive employment income"
            ),
            "status": (
                "conditional on assumed elasticity and error distribution; not an "
                "identified welfare estimate"
            ),
        },
        "domain": domain,
        "totals": totals,
        "subsidy_inclusive": inclusive,
        "quintiles": quintiles,
        "mtr_bands": bands,
        "mtr_percentiles": {
            "in_domain": {
                f"p{p}": weighted_percentile(main.marginal_tax_rate, main.weight, p)
                for p in PERCENTILES
            },
            "all_records": {
                f"p{p}": weighted_percentile(rates, records.weight, p)
                for p in PERCENTILES
            },
        },
        "representative_worker": representative,
        "sensitivity": sensitivity,
    }


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def content_sha256(artifact):
    """Hash of everything except the hash field itself."""
    body = {k: v for k, v in artifact.items() if k != "artifact_sha256"}
    return hashlib.sha256(_canonical(body).encode()).hexdigest()


RAW_VARIABLES = (
    "employment_income",
    "marginal_tax_rate",
    "person_weight",
    "age",
    "adult_earnings_index",
)


def _simulate(year):
    import policyengine as pe

    sim = pe.us.managed_microsimulation()

    def values(name):
        return np.asarray(sim.calculate(name, year).values, dtype=float)

    default_adults = int(
        sim.tax_benefit_system.parameters(year).simulation.marginal_tax_rate_adults
    )
    age, earnings = values("age"), values("employment_income")
    eligible = (age >= MIN_AGE) & (age <= MAX_AGE) & (earnings > 0)
    needed = int(values("adult_earnings_index")[eligible].max())
    if needed > default_adults:
        # Compute marginal rates for every eligible earner, not only the two
        # highest-earning adults per household.
        sim.apply_reform(
            {
                "simulation.marginal_tax_rate_adults": {
                    f"{year}-01-01.{year}-12-31": needed
                }
            }
        )
    settings = sim.tax_benefit_system.parameters(year).simulation
    raw = {name: values(name) for name in RAW_VARIABLES}
    bundle = json.loads(json.dumps(sim.policyengine_bundle, default=str))
    bundle["marginal_tax_rate_settings"] = {
        "adults": int(settings.marginal_tax_rate_adults),
        "default_adults": default_adults,
        "delta": float(settings.marginal_tax_rate_delta),
    }
    return raw, bundle


def extract_person_records(year=YEAR, cache=None):
    """Run the managed PolicyEngine-US microsimulation for one year.

    Returns ``(records, provenance)``. Requires the ``policyengine`` extra.
    ``cache`` names a local ``.npz`` of the raw person variables (with a
    ``.bundle.json`` sidecar) that is reused when present and written when
    absent, so rebuilding aggregates need not rerun the simulation. Keep it
    outside the repository: it is microdata.
    """
    from taxuncertainty.analysis.policyengine_budgets import _installed_provenance

    provenance = _installed_provenance()
    cache = None if cache is None else Path(cache)
    if cache is not None and cache.exists():
        with np.load(cache) as data:
            raw = {name: np.asarray(data[name], dtype=float) for name in RAW_VARIABLES}
        bundle = json.loads(Path(f"{cache}.bundle.json").read_text())
        extracted_at = datetime.fromtimestamp(cache.stat().st_mtime, timezone.utc)
    else:
        raw, bundle = _simulate(year)
        extracted_at = datetime.now(timezone.utc)
        if cache is not None:
            np.savez_compressed(cache, **raw)
            Path(f"{cache}.bundle.json").write_text(json.dumps(bundle, indent=1))
    eligible = (
        (raw["age"] >= MIN_AGE)
        & (raw["age"] <= MAX_AGE)
        & (raw["employment_income"] > 0)
    )
    rate_adults = bundle["marginal_tax_rate_settings"]["adults"]
    computed = raw["adult_earnings_index"] <= rate_adults
    keep = eligible & computed
    skipped = eligible & ~computed
    records = PersonRecords(
        raw["employment_income"][keep],
        raw["marginal_tax_rate"][keep],
        raw["person_weight"][keep],
    )
    provenance.update(
        {
            "source": "policyengine.us.managed_microsimulation()",
            "population_dataset_used": True,
            "dataset_bundle": bundle,
            "year": year,
            "variables": {
                "earnings": "employment_income",
                "marginal_tax_rate": "marginal_tax_rate (unclipped)",
                "weight": "person_weight",
                "filter": f"age {MIN_AGE}-{MAX_AGE} and employment_income > 0",
                "rate_computed": (
                    f"adult_earnings_index <= {rate_adults}; PolicyEngine sets "
                    "marginal_tax_rate to zero for other people"
                ),
            },
            "person_records_total": int(len(keep)),
            "person_records_eligible": int(eligible.sum()),
            "person_records_used": int(keep.sum()),
            "rate_not_computed": {
                "records": int(skipped.sum()),
                "weighted_workers": float(raw["person_weight"][skipped].sum()),
                "total_earnings": float(
                    raw["person_weight"][skipped] @ raw["employment_income"][skipped]
                ),
            },
            "records_sha256": records.digest(),
            "microdata_extracted_at_utc": extracted_at.isoformat(),
        }
    )
    return records, provenance


def build_artifact(records, provenance):
    artifact = {
        "schema_version": SCHEMA_VERSION,
        "status": (
            "conditional national aggregation of the illustrative model; "
            "not an identified welfare estimate"
        ),
        "provenance": provenance,
        **national_estimate(records),
    }
    artifact = json.loads(_canonical(artifact))
    artifact["artifact_sha256"] = content_sha256(artifact)
    return artifact


def national_dataset(provenance):
    """The dataset identity and rate settings recorded with the simulation."""
    bundle = provenance["dataset_bundle"]
    return {
        "name": bundle["runtime_dataset"],
        "uri": bundle["runtime_dataset_uri"],
        "sha256": bundle["runtime_dataset_sha256"],
        "marginal_tax_rate_settings": bundle["marginal_tax_rate_settings"],
    }


def load_national_estimate(path=ARTIFACT_PATH):
    """Load the committed aggregate artifact, failing closed on tampering."""
    artifact = json.loads(Path(path).read_text())

    def require(condition, message):
        if not condition:
            raise ValueError(f"Invalid national estimate: {message}")

    require(artifact.get("schema_version") == SCHEMA_VERSION, "schema version")
    require(artifact.get("artifact_sha256") == content_sha256(artifact), "hash")
    provenance = artifact["provenance"]
    require(provenance.get("population_dataset_used") is True, "dataset flag")
    require(len(provenance.get("records_sha256", "")) == 64, "records hash")
    require(
        provenance["person_records_eligible"]
        == provenance["person_records_used"]
        + provenance["rate_not_computed"]["records"],
        "record counts",
    )
    manifest = provenance["bundle_manifest"]
    versions = provenance["package_versions"]
    require(
        versions["policyengine"] == manifest["policyengine_version"],
        "policyengine version",
    )
    require(
        versions["policyengine-us"]
        == manifest["data_releases"]["us"]["model_package"]["version"],
        "country model version",
    )
    certified = manifest["data_releases"]["us"]["certified_data_artifact"]
    dataset = national_dataset(provenance)
    require(dataset["sha256"] == certified["sha256"], "dataset not certified")
    return artifact


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=ARTIFACT_PATH)
    parser.add_argument("--year", type=int, default=YEAR)
    parser.add_argument(
        "--records-cache",
        type=Path,
        help="local .npz of raw person variables to reuse or create",
    )
    args = parser.parse_args(argv)
    records, provenance = extract_person_records(args.year, args.records_cache)
    artifact = build_artifact(records, provenance)
    args.output.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
    print(f"Wrote {args.output} ({provenance['person_records_used']:,} records)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
