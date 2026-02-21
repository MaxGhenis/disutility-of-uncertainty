"""Empirical marginal tax rate distribution from PolicyEngine-US microsimulation.

Loads the Enhanced CPS via PolicyEngine-US, extracts person-level
employment income, comprehensive marginal tax rates, and survey weights,
then provides summary statistics and distributional breakdowns.
"""

import hashlib
from pathlib import Path

import numpy as np

CACHE_DIR = Path(__file__).parent.parent / "data" / "cache"


class EmpiricalMTR:
    """Household-level comprehensive MTRs from PolicyEngine-US.

    Parameters
    ----------
    year : int
        Tax year for the simulation (default 2024).
    cache : bool
        Whether to cache/load results from disk (default True).
    """

    def __init__(self, year=2024, cache=True):
        self.year = year
        self._cache = cache
        self._earnings = None
        self._mtr = None
        self._weights = None
        self._load()

    def _cache_path(self):
        tag = hashlib.md5(f"empirical_mtr_{self.year}".encode()).hexdigest()[:8]
        return CACHE_DIR / f"empirical_mtr_{self.year}_{tag}.npz"

    def _load(self):
        cache_path = self._cache_path()
        if self._cache and cache_path.exists():
            data = np.load(cache_path)
            self._earnings = data["earnings"]
            self._mtr = data["mtr"]
            self._weights = data["weights"]
            return

        self._run_simulation()

        if self._cache:
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(
                cache_path,
                earnings=self._earnings,
                mtr=self._mtr,
                weights=self._weights,
            )

    def _run_simulation(self):
        from policyengine_us import Microsimulation

        sim = Microsimulation()

        emp_inc = sim.calculate("employment_income", self.year).values
        mtr_raw = sim.calculate("marginal_tax_rate", self.year).values
        weights = sim.calculate("person_weight", self.year).values
        ages = sim.calculate("age", self.year).values

        # Filter to working-age adults with positive earnings
        mask = (ages >= 18) & (ages <= 64) & (emp_inc > 0)

        self._earnings = emp_inc[mask]
        self._mtr = np.clip(mtr_raw[mask], 0.0, 0.99)
        self._weights = weights[mask]

    @property
    def earnings(self):
        return self._earnings

    @property
    def mtr(self):
        return self._mtr

    @property
    def weights(self):
        return self._weights

    def summary_stats(self):
        """Weighted summary statistics for the MTR distribution.

        Returns
        -------
        dict
            Keys: weighted_mean, weighted_std, p10, p25, p50, p75, p90,
            n_observations, total_weighted_workers, mean_earnings.
        """
        w_mean = float(np.average(self._mtr, weights=self._weights))
        w_var = float(
            np.average((self._mtr - w_mean) ** 2, weights=self._weights)
        )
        return {
            "weighted_mean": w_mean,
            "weighted_std": float(np.sqrt(w_var)),
            "p10": float(np.percentile(self._mtr, 10)),
            "p25": float(np.percentile(self._mtr, 25)),
            "p50": float(np.percentile(self._mtr, 50)),
            "p75": float(np.percentile(self._mtr, 75)),
            "p90": float(np.percentile(self._mtr, 90)),
            "n_observations": len(self._mtr),
            "total_weighted_workers": float(np.sum(self._weights)),
            "mean_earnings": float(np.average(self._earnings, weights=self._weights)),
        }

    def _assign_quantile_labels(self, n_groups):
        """Assign income quantile labels based on weighted income distribution."""
        sorted_idx = np.argsort(self._earnings)
        cum_w = np.cumsum(self._weights[sorted_idx])
        total_w = cum_w[-1]
        labels = np.zeros(len(self._earnings), dtype=int)
        for q in range(n_groups):
            lo = q / n_groups * total_w
            hi = (q + 1) / n_groups * total_w
            in_q = (cum_w > lo) & (cum_w <= hi)
            labels[sorted_idx[in_q]] = q + 1
        return labels

    def _quantile_results(self, n_groups):
        """DWL breakdown by income quantile.

        Parameters
        ----------
        n_groups : int
            Number of quantile groups (5 for quintiles, 10 for deciles).

        Returns
        -------
        list[dict]
            One dict per quantile with keys: quantile, mean_earnings,
            mean_mtr, n_observations, weighted_workers.
        """
        labels = self._assign_quantile_labels(n_groups)
        results = []
        for q in range(1, n_groups + 1):
            mask = labels == q
            if not mask.any():
                continue
            e, m, w = self._earnings[mask], self._mtr[mask], self._weights[mask]
            results.append(
                {
                    "quantile": q,
                    "mean_earnings": float(np.average(e, weights=w)),
                    "mean_mtr": float(np.average(m, weights=w)),
                    "n_observations": int(mask.sum()),
                    "weighted_workers": float(np.sum(w)),
                }
            )
        return results

    def quintile_results(self):
        """DWL breakdown by income quintile."""
        return self._quantile_results(5)

    def decile_results(self):
        """DWL breakdown by income decile."""
        return self._quantile_results(10)
