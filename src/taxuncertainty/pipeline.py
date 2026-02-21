"""Results pipeline: generate all paper results and write to JSON.

This module orchestrates the calibration, optimal tax computation,
and sensitivity analysis, then serializes everything to a single
JSON file that the paper can reference.
"""

import json
from pathlib import Path

import numpy as np

from taxuncertainty.analysis.calibration import Calibration
from taxuncertainty.models.planner import SocialPlanner
from taxuncertainty.models.preferences import QuasilinearIsoelastic


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

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)

    return results
