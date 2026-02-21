"""Population-level welfare calculations.

Aggregates individual DWL from tax misperception across a population
of heterogeneous workers. Wages are interpreted as annual earnings
(consistent with the calibration approach), so the DWL formula uses
earnings directly:

    DWL_i = 0.5 * epsilon * earnings_i * sigma^2 / (1 - tau_i)
"""

import numpy as np

from taxuncertainty.models.preferences import QuasilinearIsoelastic


STANDARD_ANNUAL_HOURS = 2000


def _individual_dwl_from_wages(wage, tax_rate, misperception_std, prefs):
    """Per-worker DWL using hourly wages and standard annual hours.

    DWL = 0.5 * epsilon * (wage * STANDARD_ANNUAL_HOURS) * sigma^2 / (1 - tau)

    This uses the calibration-consistent approach where annual earnings
    are computed as wage * 2000 hours, matching macro statistics.

    Parameters
    ----------
    wage : float
        Hourly wage for this worker.
    tax_rate : float
        Marginal tax rate.
    misperception_std : float
        Standard deviation of misperception.
    prefs : QuasilinearIsoelastic
        Preference parameters (only frisch_elasticity is used).

    Returns
    -------
    float
        Expected annual DWL for this worker.
    """
    if misperception_std == 0:
        return 0.0
    eps = prefs.frisch_elasticity
    annual_earnings = wage * STANDARD_ANNUAL_HOURS
    return 0.5 * eps * annual_earnings * misperception_std ** 2 / (1 - tax_rate)


class PopulationWelfare:
    """Aggregate deadweight loss calculations for a population.

    All methods interpret the wages parameter as annual earnings,
    consistent with the calibration approach. The DWL formula is:
        DWL_i = 0.5 * epsilon * earnings_i * sigma^2 / (1 - tau_i)
    """

    def total_dwl(self, wages, tax_rates, misperception_std, prefs):
        """Sum of expected DWL (analytical approx) across all workers.

        Parameters
        ----------
        wages : array-like
            Annual earnings for each worker.
        tax_rates : array-like
            Marginal tax rate for each worker.
        misperception_std : float
            Standard deviation of misperception (same for all workers).
        prefs : QuasilinearIsoelastic
            Preference parameters.

        Returns
        -------
        float
            Total expected DWL across all workers.
        """
        if misperception_std == 0:
            return 0.0
        wages = np.asarray(wages, dtype=float)
        tax_rates = np.asarray(tax_rates, dtype=float)
        eps = prefs.frisch_elasticity
        annual_earnings = wages * STANDARD_ANNUAL_HOURS
        return float(np.sum(
            0.5 * eps * annual_earnings * misperception_std ** 2 / (1 - tax_rates)
        ))

    def total_dwl_individual_sum(self, wages, tax_rates, misperception_std, prefs):
        """Same as total_dwl -- explicit summation for testing.

        Parameters
        ----------
        wages : array-like
            Annual earnings for each worker.
        tax_rates : array-like
            Marginal tax rate for each worker.
        misperception_std : float
            Standard deviation of misperception.
        prefs : QuasilinearIsoelastic
            Preference parameters.

        Returns
        -------
        float
            Total expected DWL (same as total_dwl).
        """
        return self.total_dwl(wages, tax_rates, misperception_std, prefs)

    def total_dwl_analytical(self, mean_wage, mean_tax_rate, misperception_std,
                              prefs, n_workers=1):
        """Shortcut using representative-agent approximation.

        total DWL ~ n * 0.5 * epsilon * earnings_bar * sigma^2 / (1 - tau_bar)

        Parameters
        ----------
        mean_wage : float
            Mean annual earnings.
        mean_tax_rate : float
            Mean marginal tax rate.
        misperception_std : float
            Standard deviation of misperception.
        prefs : QuasilinearIsoelastic
            Preference parameters.
        n_workers : int
            Number of workers.

        Returns
        -------
        float
            Approximate total DWL.
        """
        per_worker = _individual_dwl_from_wages(
            mean_wage, mean_tax_rate, misperception_std, prefs
        )
        return n_workers * per_worker
