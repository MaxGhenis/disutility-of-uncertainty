"""Social planner model for optimal taxation under misperception.

Implements a social planner who chooses a linear tax rate and lump-sum
demogrant to maximize utilitarian social welfare, accounting for the
possibility that workers misperceive the tax rate.
"""

import numpy as np

from taxuncertainty.models.preferences import QuasilinearIsoelastic


class SocialPlanner:
    """Utilitarian social planner with linear tax and lump-sum transfer."""

    def _compute_hours_and_revenue(self, tax_rate, wages, prefs,
                                    misperception_std=0, seed=42):
        """Shared helper: compute hours for each worker and total revenue.

        Returns
        -------
        hours : np.ndarray
            Hours worked by each worker.
        revenue : float
            Total tax revenue = sum(tau * w_i * h_i).
        """
        wages = np.asarray(wages, dtype=float)
        n = len(wages)

        if misperception_std > 0:
            rng = np.random.default_rng(seed)
            errors = rng.normal(0, misperception_std, n)
            perceived_taxes = np.clip(tax_rate + errors, 0.0, 1.0)
            net_wages = wages * (1.0 - perceived_taxes)
            hours = np.where(
                perceived_taxes >= 1.0, 0.0,
                (net_wages / prefs.psi) ** prefs.frisch_elasticity,
            )
        else:
            net_wages = wages * (1.0 - tax_rate)
            hours = np.where(
                tax_rate >= 1.0, 0.0,
                (net_wages / prefs.psi) ** prefs.frisch_elasticity,
            )

        revenue = tax_rate * np.sum(wages * hours)
        return hours, revenue

    def revenue(self, tax_rate, wages, prefs, misperception_std=0, seed=42):
        """Total tax revenue = sum(tau * w_i * h_i).

        Parameters
        ----------
        tax_rate : float
            Linear marginal tax rate tau.
        wages : array-like
            Hourly wage for each worker.
        prefs : QuasilinearIsoelastic
            Preference parameters.
        misperception_std : float
            Standard deviation of tax misperception (0 = perfect info).
        seed : int
            Random seed for misperception draws.

        Returns
        -------
        float
            Total tax revenue.
        """
        _, rev = self._compute_hours_and_revenue(
            tax_rate, wages, prefs, misperception_std, seed
        )
        return rev

    def demogrant(self, tax_rate, wages, prefs, misperception_std=0, seed=42):
        """Per-capita lump-sum transfer = revenue / N.

        Parameters
        ----------
        tax_rate : float
            Linear marginal tax rate tau.
        wages : array-like
            Hourly wage for each worker.
        prefs : QuasilinearIsoelastic
            Preference parameters.
        misperception_std : float
            Standard deviation of tax misperception.
        seed : int
            Random seed.

        Returns
        -------
        float
            Per-capita demogrant.
        """
        rev = self.revenue(tax_rate, wages, prefs, misperception_std, seed)
        return rev / len(np.asarray(wages))

    def _welfare_one_draw(self, tax_rate, wages, prefs, hours, rev):
        """Compute weighted-utilitarian welfare for one draw of hours.

        Parameters
        ----------
        tax_rate : float
            True marginal tax rate.
        wages : np.ndarray
            Hourly wages.
        prefs : QuasilinearIsoelastic
            Preferences.
        hours : np.ndarray
            Hours worked by each agent.
        rev : float
            Total tax revenue.

        Returns
        -------
        float
            Weighted average utility.
        """
        n = len(wages)
        v = rev / n  # demogrant
        w_mean = np.mean(wages)

        eps = prefs.frisch_elasticity
        exponent = 1.0 + 1.0 / eps

        consumption = wages * (1 - tax_rate) * hours + v
        disutility = prefs.psi * hours ** exponent / exponent
        utilities = consumption - disutility
        weights = w_mean / wages

        return float(np.sum(weights * utilities) / n)

    def social_welfare(self, tax_rate, wages, prefs, misperception_std=0, seed=42,
                       n_mc=1000):
        """Expected weighted-utilitarian social welfare (inequality-averse).

        Each worker's indirect utility is:
            U_i = w_i(1-tau)*h_i + v - psi*h_i^(1+1/eps)/(1+1/eps)

        where v = demogrant, and h_i is determined by the worker's
        (possibly misperceived) tax rate. Consumption is evaluated at the
        true tax rate.

        The social welfare function uses inverse-wage weights to create
        a redistribution motive:
            W = (1/N) * sum((w_mean / w_i) * U_i)

        When misperception_std > 0, welfare is computed as the expected
        value over multiple Monte Carlo draws of misperception errors.

        Parameters
        ----------
        tax_rate : float
            Linear marginal tax rate.
        wages : array-like
            Hourly wage for each worker.
        prefs : QuasilinearIsoelastic
            Preference parameters.
        misperception_std : float
            Standard deviation of tax misperception.
        seed : int
            Random seed.
        n_mc : int
            Number of Monte Carlo draws for expected welfare under
            misperception (default 1000).

        Returns
        -------
        float
            Weighted average utility (social welfare).
        """
        wages = np.asarray(wages, dtype=float)

        if misperception_std <= 0:
            hours, rev = self._compute_hours_and_revenue(
                tax_rate, wages, prefs, 0, seed
            )
            return self._welfare_one_draw(tax_rate, wages, prefs, hours, rev)

        # Average welfare over many draws to get expected welfare
        rng = np.random.default_rng(seed)
        n = len(wages)
        total_welfare = 0.0
        for _ in range(n_mc):
            errors = rng.normal(0, misperception_std, n)
            perceived_taxes = np.clip(tax_rate + errors, 0.0, 1.0)
            net_wages = wages * (1.0 - perceived_taxes)
            hours = np.where(
                perceived_taxes >= 1.0, 0.0,
                (net_wages / prefs.psi) ** prefs.frisch_elasticity,
            )
            rev = tax_rate * np.sum(wages * hours)
            total_welfare += self._welfare_one_draw(
                tax_rate, wages, prefs, hours, rev
            )
        return total_welfare / n_mc

    def optimal_tax(self, wages, prefs, misperception_std=0, seed=42,
                    search_range=(0.0, 0.80), n_grid=81):
        """Find tax rate maximizing social welfare via grid search.

        Uses a two-pass approach: first a coarse grid, then a fine grid
        around the coarse optimum, for better precision.

        Parameters
        ----------
        wages : array-like
            Hourly wage for each worker.
        prefs : QuasilinearIsoelastic
            Preference parameters.
        misperception_std : float
            Standard deviation of tax misperception.
        seed : int
            Random seed.
        search_range : tuple
            (min_tax, max_tax) range for grid search.
        n_grid : int
            Number of grid points per pass.

        Returns
        -------
        float
            Tax rate that maximizes social welfare.
        """
        def best_on_grid(lo, hi):
            grid = np.linspace(lo, hi, n_grid)
            welfares = [
                self.social_welfare(tau, wages, prefs, misperception_std, seed)
                for tau in grid
            ]
            idx = int(np.argmax(welfares))
            return grid[idx], welfares[idx]

        # Coarse pass
        best_tau, best_welfare = best_on_grid(*search_range)

        # Fine pass around the coarse optimum
        step = (search_range[1] - search_range[0]) / max(n_grid - 1, 1)
        lo = max(search_range[0], best_tau - step)
        hi = min(search_range[1], best_tau + step)
        fine_tau, fine_welfare = best_on_grid(lo, hi)

        if fine_welfare > best_welfare:
            best_tau = fine_tau

        return float(best_tau)
