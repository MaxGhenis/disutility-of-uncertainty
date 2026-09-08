"""Exact linear-budget private regret and government revenue accounting."""

from dataclasses import dataclass

import numpy as np

from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.labor import optimal_hours
from taxuncertainty.models.preferences import QuasilinearIsoelastic


@dataclass(frozen=True)
class WorkerOutcome:
    """Expected effects versus an informed worker at the same true tax.

    ``private_regret`` holds transfers fixed. ``transfer_change`` is this
    worker's contribution to the *aggregate* rebate, equal to their revenue
    change; it is not their personal transfer in a heterogeneous population.
    ``social_loss`` values every dollar of private utility and rebated revenue
    equally. A negative social loss is a gain.
    """

    baseline_hours: float
    expected_hours: float
    baseline_earnings: float
    expected_earnings: float
    earnings_change: float
    baseline_revenue: float
    expected_revenue: float
    revenue_change: float
    transfer_change: float
    private_regret: float
    social_loss: float
    latent_rmse: float
    realized_mean_error: float
    realized_std_error: float
    realized_rmse: float


def evaluate_worker(
    wage: float,
    tax_rate: float,
    prefs: QuasilinearIsoelastic,
    beliefs: NormalBeliefs,
    quadrature_order: int = 256,
) -> WorkerOutcome:
    """Evaluate the exact utility function under the true linear budget.

    The worker optimizes against each perceived rate. Labor is zero for
    perceived rates at least one; the true-rate benchmark likewise allows
    this corner. No division by ``1 - tax_rate`` or Taylor approximation is
    used, including at a true rate of one.
    """
    baseline_hours = optimal_hours(wage, tax_rate, prefs)
    perceived, weights = beliefs.quadrature(tax_rate, quadrature_order)
    eps = prefs.frisch_elasticity
    hours = (wage * np.maximum(0.0, 1.0 - perceived) / prefs.psi) ** eps
    expected_hours = float(weights @ hours)
    exponent = 1.0 + 1.0 / eps
    utility = wage * (1.0 - tax_rate) * hours - prefs.psi * hours**exponent / exponent
    baseline_utility = prefs.utility(
        wage * (1.0 - tax_rate) * baseline_hours, baseline_hours
    )
    # Each node's regret is nonnegative; clamp only floating-point roundoff.
    private_regret = float(weights @ np.maximum(0.0, baseline_utility - utility))
    baseline_earnings = wage * baseline_hours
    expected_earnings = wage * expected_hours
    earnings_change = expected_earnings - baseline_earnings
    revenue_change = tax_rate * earnings_change
    moments = beliefs.realized_moments(tax_rate, quadrature_order)
    return WorkerOutcome(
        baseline_hours=baseline_hours,
        expected_hours=expected_hours,
        baseline_earnings=baseline_earnings,
        expected_earnings=expected_earnings,
        earnings_change=earnings_change,
        baseline_revenue=tax_rate * baseline_earnings,
        expected_revenue=tax_rate * expected_earnings,
        revenue_change=revenue_change,
        transfer_change=revenue_change,
        private_regret=private_regret,
        social_loss=private_regret - revenue_change,
        latent_rmse=beliefs.latent_rmse,
        realized_mean_error=moments.mean_error,
        realized_std_error=moments.std_error,
        realized_rmse=moments.rmse,
    )
