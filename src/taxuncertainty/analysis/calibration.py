"""Calibration of model parameters and baseline results.

Uses empirical estimates from the public finance literature to calibrate
the model and compute deadweight loss estimates.
"""

import pandas as pd


class Calibration:
    """Calibrated parameter sets and baseline results.

    Literature sources
    ------------------
    - Frisch elasticity: Chetty (2012) meta-analysis
    - Misperception std: Rees-Jones & Taubinsky (2020), Gideon & Keen (2017)
    - US macro parameters: CBO, BLS
    """

    # From Chetty (2012) meta-analysis of Frisch elasticity
    FRISCH_ELASTICITY_LOW = 0.25
    FRISCH_ELASTICITY_CENTRAL = 0.33
    FRISCH_ELASTICITY_HIGH = 0.50

    # From Rees-Jones & Taubinsky (2020) and Gideon & Keen (2017)
    MISPERCEPTION_STD_LOW = 0.08
    MISPERCEPTION_STD_CENTRAL = 0.12
    MISPERCEPTION_STD_HIGH = 0.15

    # US macro parameters
    MEAN_MARGINAL_RATE = 0.30  # From CBO
    MEAN_HOURLY_WAGE = 27.5   # ~$55k annual at 2000 hrs
    MEAN_ANNUAL_EARNINGS = 55_000
    TOTAL_WORKERS = 160_000_000
    GDP = 28_000_000_000_000  # ~$28T

    # Disutility scale psi calibrated so median worker works ~2000 hrs/year
    PSI = 1.0  # normalized

    def per_worker_dwl(self, eps, sigma, tau=None, earnings=None):
        """Analytical per-worker DWL: 0.5 * eps * earnings * sigma^2 / (1 - tau)."""
        tau = tau if tau is not None else self.MEAN_MARGINAL_RATE
        earnings = earnings if earnings is not None else self.MEAN_ANNUAL_EARNINGS
        return 0.5 * eps * earnings * sigma ** 2 / (1 - tau)

    def _dwl_row(self, eps, sigma):
        """Build a result dict for one (elasticity, sigma) combination."""
        per_worker = self.per_worker_dwl(eps, sigma)
        total = per_worker * self.TOTAL_WORKERS
        return {
            "frisch_elasticity": eps,
            "misperception_std": sigma,
            "per_worker_dwl": per_worker,
            "total_dwl_billions": total / 1e9,
            "gdp_fraction_pct": total / self.GDP * 100,
        }

    def baseline_results(self):
        """Compute baseline DWL using central parameters.

        Uses the analytical formula:
            per_worker = 0.5 * epsilon * annual_earnings * sigma^2 / (1 - tau)

        Returns
        -------
        dict
            Keys: total_dwl_billions, per_worker_dwl, gdp_fraction_pct,
            frisch_elasticity, misperception_std.
        """
        return self._dwl_row(
            self.FRISCH_ELASTICITY_CENTRAL,
            self.MISPERCEPTION_STD_CENTRAL,
        )

    def sensitivity_table(self):
        """Grid of DWL across (frisch_elasticity, misperception_std) pairs.

        Computes 3 x 3 = 9 rows using low, central, high values for each.

        Returns
        -------
        pd.DataFrame
            Columns: frisch_elasticity, misperception_std, per_worker_dwl,
            total_dwl_billions, gdp_fraction_pct.
        """
        elasticities = [
            self.FRISCH_ELASTICITY_LOW,
            self.FRISCH_ELASTICITY_CENTRAL,
            self.FRISCH_ELASTICITY_HIGH,
        ]
        sigmas = [
            self.MISPERCEPTION_STD_LOW,
            self.MISPERCEPTION_STD_CENTRAL,
            self.MISPERCEPTION_STD_HIGH,
        ]

        rows = [
            self._dwl_row(eps, sigma)
            for eps in elasticities
            for sigma in sigmas
        ]
        return pd.DataFrame(rows)
