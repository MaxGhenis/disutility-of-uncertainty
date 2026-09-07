"""Exact fiscal accounting for explicitly enumerated synthetic workers.

This module has no survey-data weighting path. PolicyEngine population analysis
must use managed simulation and MicroSeries entity-mapping operations.
"""

from dataclasses import dataclass

import numpy as np

from taxuncertainty.models.accounting import evaluate_worker


@dataclass(frozen=True)
class PopulationOutcome:
    workers: int
    private_regret: float
    weighted_private_regret: float
    earnings_change: float
    revenue_change: float
    per_capita_transfer_change: float
    social_loss: float


def evaluate_population(wages, tax_rates, prefs, beliefs, social_weights=None):
    """Sum worker outcomes with a common equal-per-person rebate.

    Social weights are normative utility weights, not sampling weights.
    Social loss is the weighted sum of utility losses; negative means a gain.
    """
    wages = np.asarray(wages, dtype=float)
    rates = np.asarray(tax_rates, dtype=float)
    if wages.ndim != 1 or wages.size == 0 or rates.shape != wages.shape:
        raise ValueError("wages and tax_rates must be nonempty matching vectors")
    omega = (
        np.ones_like(wages)
        if social_weights is None
        else np.asarray(social_weights, dtype=float)
    )
    if omega.shape != wages.shape or not np.all(np.isfinite(omega)):
        raise ValueError("social weights must be finite and match wages")
    with np.errstate(over="ignore", invalid="ignore"):
        total_social_weight = float(omega.sum())
    if (
        np.any(omega < 0)
        or not np.isfinite(total_social_weight)
        or total_social_weight <= 0
    ):
        raise ValueError("social weights must be nonnegative with positive total")
    outcomes = [evaluate_worker(w, t, prefs, beliefs) for w, t in zip(wages, rates)]
    regrets = np.array([outcome.private_regret for outcome in outcomes])
    with np.errstate(over="ignore", invalid="ignore"):
        private_regret = float(regrets.sum())
        earnings_change = sum(outcome.earnings_change for outcome in outcomes)
        revenue_change = sum(outcome.revenue_change for outcome in outcomes)
        transfer_change = revenue_change / len(wages)
        weighted_regret = float(np.dot(omega, regrets))
        social_loss = weighted_regret - total_social_weight * transfer_change
    if not all(
        np.isfinite(value)
        for value in (
            private_regret,
            weighted_regret,
            earnings_change,
            revenue_change,
            transfer_change,
            social_loss,
        )
    ):
        raise ValueError(
            "Aggregate welfare overflowed; rescale social weights or preferences"
        )
    return PopulationOutcome(
        workers=len(wages),
        private_regret=private_regret,
        weighted_private_regret=weighted_regret,
        earnings_change=earnings_change,
        revenue_change=revenue_change,
        per_capita_transfer_change=transfer_change,
        social_loss=social_loss,
    )
