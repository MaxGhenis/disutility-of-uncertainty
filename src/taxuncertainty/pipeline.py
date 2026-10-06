"""Results pipeline: generate all paper results and write to JSON.

This module orchestrates the calibration, optimal tax computation,
sensitivity analysis, and empirical microsimulation results, then
serializes everything to a single JSON file that the paper can reference.
"""

import json
from pathlib import Path

import numpy as np

from taxuncertainty.analysis.calibration import Calibration
from taxuncertainty.models.planner import SocialPlanner
from taxuncertainty.models.preferences import QuasilinearIsoelastic


def _generate_empirical_section(cal, prefs):
    """Generate empirical results from PolicyEngine-US microsimulation.

    Parameters
    ----------
    cal : Calibration
        Calibration instance for baseline comparison.
    prefs : QuasilinearIsoelastic
        Preference parameters.

    Returns
    -------
    dict
        Empirical results section for results.json.
    """
    from taxuncertainty.analysis.empirical import EmpiricalMTR

    emp = EmpiricalMTR(year=2024, cache=True)
    stats = emp.summary_stats()
    sigma = cal.MISPERCEPTION_STD_CENTRAL
    eps = prefs.frisch_elasticity
    per_worker_dwl = 0.5 * eps * emp.earnings * sigma**2 / (1.0 - emp.mtr)
    aggregate_dwl = float(np.sum(emp.weights * per_worker_dwl))
    quintile_labels = emp.quantile_labels(5)

    quintiles_with_dwl = []
    for quantile in range(1, 6):
        mask = quintile_labels == quantile
        if not np.any(mask):
            continue
        weights = emp.weights[mask]
        quintile_total_dwl = float(np.sum(weights * per_worker_dwl[mask]))
        quintiles_with_dwl.append({
            "quantile": quantile,
            "mean_earnings": float(np.average(emp.earnings[mask], weights=weights)),
            "mean_mtr": float(np.average(emp.mtr[mask], weights=weights)),
            "n_observations": int(mask.sum()),
            "weighted_workers": float(np.sum(weights)),
            "per_worker_dwl": float(np.average(per_worker_dwl[mask], weights=weights)),
            "quintile_total_dwl": quintile_total_dwl,
            "share_of_total_dwl": (
                quintile_total_dwl / aggregate_dwl if aggregate_dwl > 0 else 0.0
            ),
        })

    # Stylized baseline comparison
    stylized_dwl = cal.per_worker_dwl(
        eps,
        sigma,
        tau=stats["weighted_mean"],
        earnings=stats["mean_earnings"],
    ) * stats["total_weighted_workers"]

    return {
        "mtr_distribution": stats,
        "aggregate_dwl": aggregate_dwl,
        "aggregate_dwl_billions": aggregate_dwl / 1e9,
        "quintiles": quintiles_with_dwl,
        "comparison": {
            "empirical_dwl_billions": aggregate_dwl / 1e9,
            "stylized_dwl_billions": stylized_dwl / 1e9,
            "ratio": aggregate_dwl / stylized_dwl if stylized_dwl > 0 else None,
        },
    }


def generate_results(output_path=None, seed=42):
    """Generate all results for the paper and write to JSON.

    Parameters
    ----------
    output_path : str or Path or None
        Where to write results.json. If None, writes to
        src/taxuncertainty/data/results.json.
    seed : int
        Random seed for reproducibility.

    Output structure
    ----------------
    {
        "baseline": { ...from Calibration.baseline_results() },
        "sensitivity": [ ...rows from sensitivity_table() as dicts ],
        "optimal_tax": {
            "certain": float,
            "uncertain": float,
        },
        "parameters": {
            "frisch_elasticity_central": 0.33,
            "misperception_std_central": 0.12,
            ...
        },
        "empirical": {
            "mtr_distribution": { ...weighted stats },
            "aggregate_dwl": float,
            "aggregate_dwl_billions": float,
            "quintiles": [ ...per-quintile breakdown ],
            "comparison": { ...empirical vs stylized }
        }
    }
    """
    output_path = (
        Path(output_path)
        if output_path
        else Path(__file__).parent / "data" / "results.json"
    )

    # Calibration
    cal = Calibration()
    baseline = cal.baseline_results()
    sensitivity = cal.sensitivity_table()

    # Optimal tax computation using a representative wage distribution
    prefs = QuasilinearIsoelastic(
        psi=cal.PSI,
        frisch_elasticity=cal.FRISCH_ELASTICITY_CENTRAL,
    )

    # Create a small representative wage distribution
    rng = np.random.default_rng(seed)
    wages = rng.lognormal(
        mean=np.log(cal.MEAN_HOURLY_WAGE) - 0.5 * 0.5**2,
        sigma=0.5,
        size=500,
    )

    planner = SocialPlanner()
    tau_certain = planner.optimal_tax(wages, prefs, misperception_std=0, seed=seed)
    tau_uncertain = planner.optimal_tax(
        wages,
        prefs,
        misperception_std=cal.MISPERCEPTION_STD_CENTRAL,
        seed=seed,
    )

    results = {
        "baseline": baseline,
        "sensitivity": sensitivity.to_dict(orient="records"),
        "optimal_tax": {
            "certain": tau_certain,
            "uncertain": tau_uncertain,
        },
        "parameters": {
            "frisch_elasticity_central": cal.FRISCH_ELASTICITY_CENTRAL,
            "frisch_elasticity_low": cal.FRISCH_ELASTICITY_LOW,
            "frisch_elasticity_high": cal.FRISCH_ELASTICITY_HIGH,
            "misperception_std_central": cal.MISPERCEPTION_STD_CENTRAL,
            "misperception_std_low": cal.MISPERCEPTION_STD_LOW,
            "misperception_std_high": cal.MISPERCEPTION_STD_HIGH,
            "mean_marginal_rate": cal.MEAN_MARGINAL_RATE,
            "mean_hourly_wage": cal.MEAN_HOURLY_WAGE,
            "mean_annual_earnings": cal.MEAN_ANNUAL_EARNINGS,
            "total_workers": cal.TOTAL_WORKERS,
            "gdp": cal.GDP,
            "psi": cal.PSI,
            "seed": seed,
        },
    }

    # Empirical microsimulation results
    results["empirical"] = _generate_empirical_section(cal, prefs)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    return results
