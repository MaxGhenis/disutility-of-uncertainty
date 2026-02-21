"""Labor supply and deadweight loss under tax misperception.

All functions use the quasilinear isoelastic preference model:
    U(C, h) = C - psi * h^(1+1/epsilon) / (1+1/epsilon)

where the budget constraint (without transfers) gives C = w(1-tau)*h.
"""

import numpy as np

from taxuncertainty.models.preferences import QuasilinearIsoelastic


def optimal_hours(
    wage: float, tax_rate: float, prefs: QuasilinearIsoelastic
) -> float:
    """Optimal labor supply under the true tax rate.

    h* = (w(1-tau) / psi)^epsilon

    Parameters
    ----------
    wage : float
        Hourly wage rate w.
    tax_rate : float
        True marginal tax rate tau.
    prefs : QuasilinearIsoelastic
        Preference specification.

    Returns
    -------
    float
        Optimal hours h*. Returns 0 if tax_rate >= 1.
    """
    if tax_rate >= 1.0:
        return 0.0
    net_wage = wage * (1.0 - tax_rate)
    return (net_wage / prefs.psi) ** prefs.frisch_elasticity


def misperceived_hours(
    wage: float,
    true_tax: float,
    perceived_tax: float,
    prefs: QuasilinearIsoelastic,
) -> float:
    """Hours chosen when the worker perceives tax rate perceived_tax.

    The worker optimises against perceived_tax, so hours are:
        h(tau_hat) = (w(1 - tau_hat) / psi)^epsilon

    Parameters
    ----------
    wage : float
        Hourly wage rate.
    true_tax : float
        True marginal tax rate (unused in the hours calculation but
        included for interface consistency).
    perceived_tax : float
        Perceived marginal tax rate.
    prefs : QuasilinearIsoelastic
        Preference specification.

    Returns
    -------
    float
        Hours chosen under the perceived tax rate.
    """
    return optimal_hours(wage, perceived_tax, prefs)


def _utility_at_hours(
    wage: float,
    tax_rate: float,
    hours: float,
    prefs: QuasilinearIsoelastic,
) -> float:
    """Evaluate U = w(1-tau)*h - psi*h^(1+1/eps)/(1+1/eps).

    This is the indirect utility *without transfers*, used for DWL
    calculations where the transfer cancels out.
    """
    eps = prefs.frisch_elasticity
    exponent = 1.0 + 1.0 / eps
    return wage * (1.0 - tax_rate) * hours - prefs.psi * hours**exponent / exponent


def individual_dwl(
    wage: float,
    true_tax: float,
    perceived_tax: float,
    prefs: QuasilinearIsoelastic,
) -> float:
    """Exact individual deadweight loss from tax misperception.

    DWL = U(h*) - U(h_hat)

    where h* = optimal_hours(wage, true_tax) and
    h_hat = misperceived_hours(wage, true_tax, perceived_tax), and
    utility is evaluated at the *true* tax rate for both.

    Parameters
    ----------
    wage : float
        Hourly wage rate.
    true_tax : float
        True marginal tax rate.
    perceived_tax : float
        Perceived marginal tax rate.
    prefs : QuasilinearIsoelastic
        Preference specification.

    Returns
    -------
    float
        Non-negative deadweight loss.
    """
    h_star = optimal_hours(wage, true_tax, prefs)
    h_hat = misperceived_hours(wage, true_tax, perceived_tax, prefs)

    u_star = _utility_at_hours(wage, true_tax, h_star, prefs)
    u_hat = _utility_at_hours(wage, true_tax, h_hat, prefs)

    return u_star - u_hat


def expected_dwl_approx(
    wage: float,
    tax_rate: float,
    misperception_std: float,
    prefs: QuasilinearIsoelastic,
) -> float:
    """Second-order approximation to expected DWL.

    E[DWL] ~ 0.5 * epsilon * w * h* * sigma^2 / (1 - tau)

    Parameters
    ----------
    wage : float
        Hourly wage rate.
    tax_rate : float
        True marginal tax rate.
    misperception_std : float
        Standard deviation of misperception sigma.
    prefs : QuasilinearIsoelastic
        Preference specification.

    Returns
    -------
    float
        Approximate expected DWL. Returns 0 if sigma = 0.
    """
    if misperception_std == 0.0:
        return 0.0
    h_star = optimal_hours(wage, tax_rate, prefs)
    eps = prefs.frisch_elasticity
    return 0.5 * eps * wage * h_star * misperception_std**2 / (1.0 - tax_rate)


def expected_dwl_monte_carlo(
    wage: float,
    tax_rate: float,
    misperception_std: float,
    prefs: QuasilinearIsoelastic,
    n_draws: int = 10_000,
    seed: int = 42,
) -> float:
    """Monte Carlo estimate of expected DWL.

    Draws delta ~ N(0, sigma^2), computes perceived_tax = tau + delta
    (clipped to [0, 1]), evaluates individual_dwl for each draw, and
    returns the sample mean.

    Parameters
    ----------
    wage : float
        Hourly wage rate.
    tax_rate : float
        True marginal tax rate.
    misperception_std : float
        Standard deviation of misperception sigma.
    prefs : QuasilinearIsoelastic
        Preference specification.
    n_draws : int
        Number of Monte Carlo draws (default 10 000).
    seed : int
        Random seed for reproducibility (default 42).

    Returns
    -------
    float
        Monte Carlo estimate of E[DWL].
    """
    rng = np.random.default_rng(seed)
    deltas = rng.normal(0.0, misperception_std, size=n_draws)
    perceived_taxes = np.clip(tax_rate + deltas, 0.0, 1.0)

    dwl_values = np.array([
        individual_dwl(wage, tax_rate, float(pt), prefs)
        for pt in perceived_taxes
    ])
    return float(np.mean(dwl_values))
