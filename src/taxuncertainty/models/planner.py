"""Expected social welfare with a budget-balanced, endogenous demogrant.

Workers have a common belief-error distribution independent of wages. Errors
may be independent across workers: quasilinearity and additive welfare mean
that expectations require only marginal moments, not simulation of a joint
error vector. Inverse-wage welfare weights are an explicit normative choice.
"""

from dataclasses import dataclass
from math import isfinite

import numpy as np

from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.preferences import QuasilinearIsoelastic


@dataclass(frozen=True)
class PlannerOutcome:
    """Aggregate fiscal quantities and per-capita (weighted) social welfare."""

    tax_rate: float
    social_weights: str
    baseline_social_welfare: float
    expected_social_welfare: float
    social_welfare_loss: float
    mean_private_regret: float
    weighted_mean_private_regret: float
    baseline_revenue: float
    expected_revenue: float
    revenue_change: float
    baseline_demogrant: float
    expected_demogrant: float
    demogrant_change: float
    baseline_earnings: float
    expected_earnings: float
    earnings_change: float
    baseline_hours: list[float]
    expected_hours: list[float]


@dataclass(frozen=True)
class OptimalTaxResult:
    """Best tax on the two-pass search grid, including restricted boundaries."""

    tax_rate: float
    welfare: float
    at_boundary: bool
    search_range: tuple[float, float]
    social_weights: str
    grid_resolution: float


class SocialPlanner:
    """Linear tax planner with equal or inverse-wage social dollar weights.

    ``inverse_wage`` uses mean(wages)/wage for continuity with the historical
    model. ``equal`` assigns one to every worker. Population weights are one
    per wage observation, distinct from these normative welfare weights.
    """

    def __init__(self, social_weights="inverse_wage", quadrature_order=256):
        if social_weights not in ("equal", "inverse_wage"):
            raise ValueError("social_weights must be 'equal' or 'inverse_wage'")
        if not isinstance(quadrature_order, (int, np.integer)) or quadrature_order < 8:
            raise ValueError("quadrature_order must be an integer of at least 8")
        self.social_weights = social_weights
        self.quadrature_order = int(quadrature_order)

    def _wages_and_weights(self, wages):
        wages = np.asarray(wages, dtype=float)
        if (
            wages.ndim != 1
            or wages.size == 0
            or not np.all(np.isfinite(wages))
            or np.any(wages <= 0)
        ):
            raise ValueError(
                "wages must be a nonempty 1-D array of finite positive wages"
            )
        weights = (
            np.ones_like(wages)
            if self.social_weights == "equal"
            else np.mean(wages) / wages
        )
        return wages, weights

    @staticmethod
    def _beliefs(beliefs, misperception_std, mean_error):
        if beliefs is not None:
            if misperception_std != 0 or mean_error != 0:
                raise ValueError(
                    "pass beliefs or mean_error/misperception_std, not both"
                )
            if not isinstance(beliefs, NormalBeliefs):
                raise TypeError("beliefs must be NormalBeliefs")
            return beliefs
        return NormalBeliefs(mean_error=mean_error, std_error=misperception_std)

    def evaluate(
        self,
        tax_rate: float,
        wages,
        prefs: QuasilinearIsoelastic,
        beliefs: NormalBeliefs | None = None,
        *,
        misperception_std: float = 0.0,
        mean_error: float = 0.0,
    ) -> PlannerOutcome:
        """Expected realized utility with each draw's tax revenue rebated.

        Private regret is evaluated with transfers fixed at their informed
        level; social welfare includes the expected change in the demogrant.
        Expected disutility is integrated separately from expected hours.
        """
        wages, social_weights = self._wages_and_weights(wages)
        beliefs = self._beliefs(beliefs, misperception_std, mean_error)
        perceived, probability = beliefs.quadrature(tax_rate, self.quadrature_order)
        eps = prefs.frisch_elasticity
        net = np.maximum(0.0, 1.0 - perceived)
        hours_moment = float(probability @ net**eps)
        disutility_moment = float(probability @ net ** (eps + 1.0))
        scale = (wages / prefs.psi) ** eps
        expected_hours = scale * hours_moment
        baseline_hours = scale * max(0.0, 1.0 - tax_rate) ** eps
        expected_earnings = float(wages @ expected_hours)
        baseline_earnings = float(wages @ baseline_hours)
        expected_revenue = tax_rate * expected_earnings
        baseline_revenue = tax_rate * baseline_earnings
        demogrant = expected_revenue / len(wages)
        baseline_demogrant = baseline_revenue / len(wages)
        # psi*scale**(1+1/eps) = wage*scale avoids unnecessary large powers.
        disutility_scale = wages * scale * eps / (eps + 1.0)
        expected_private_utility = (
            wages * (1.0 - tax_rate) * expected_hours
            - disutility_scale * disutility_moment
        )
        baseline_private_utility = wages * (
            1.0 - tax_rate
        ) * baseline_hours - disutility_scale * max(0.0, 1.0 - tax_rate) ** (eps + 1.0)
        private_regret = baseline_private_utility - expected_private_utility
        baseline_social = float(
            np.mean(social_weights * (baseline_private_utility + baseline_demogrant))
        )
        expected_social = float(
            np.mean(social_weights * (expected_private_utility + demogrant))
        )
        return PlannerOutcome(
            tax_rate=float(tax_rate),
            social_weights=self.social_weights,
            baseline_social_welfare=baseline_social,
            expected_social_welfare=expected_social,
            social_welfare_loss=baseline_social - expected_social,
            mean_private_regret=float(np.mean(private_regret)),
            weighted_mean_private_regret=float(
                np.mean(social_weights * private_regret)
            ),
            baseline_revenue=baseline_revenue,
            expected_revenue=expected_revenue,
            revenue_change=expected_revenue - baseline_revenue,
            baseline_demogrant=baseline_demogrant,
            expected_demogrant=demogrant,
            demogrant_change=demogrant - baseline_demogrant,
            baseline_earnings=baseline_earnings,
            expected_earnings=expected_earnings,
            earnings_change=expected_earnings - baseline_earnings,
            baseline_hours=baseline_hours.tolist(),
            expected_hours=expected_hours.tolist(),
        )

    def _compute_hours_and_revenue(
        self,
        tax_rate,
        wages,
        prefs,
        misperception_std=0,
        seed=42,
        *,
        mean_error=0,
        beliefs=None,
    ):
        result = self.evaluate(
            tax_rate,
            wages,
            prefs,
            beliefs,
            misperception_std=misperception_std,
            mean_error=mean_error,
        )
        return np.asarray(result.expected_hours), result.expected_revenue

    def revenue(
        self,
        tax_rate,
        wages,
        prefs,
        misperception_std=0,
        seed=42,
        *,
        mean_error=0,
        beliefs=None,
    ):
        """Expected total revenue. Legacy seed is accepted and unused."""
        return self.evaluate(
            tax_rate,
            wages,
            prefs,
            beliefs,
            misperception_std=misperception_std,
            mean_error=mean_error,
        ).expected_revenue

    def demogrant(
        self,
        tax_rate,
        wages,
        prefs,
        misperception_std=0,
        seed=42,
        *,
        mean_error=0,
        beliefs=None,
    ):
        """Expected per-capita rebate, equal to expected revenue / N."""
        return self.evaluate(
            tax_rate,
            wages,
            prefs,
            beliefs,
            misperception_std=misperception_std,
            mean_error=mean_error,
        ).expected_demogrant

    def _welfare_one_draw(self, tax_rate, wages, prefs, hours, rev):
        """Evaluate realized utility; useful for independent simulation checks."""
        wages, weights = self._wages_and_weights(wages)
        hours = np.asarray(hours, dtype=float)
        if (
            hours.shape != wages.shape
            or np.any(hours < 0)
            or not np.all(np.isfinite(hours))
        ):
            raise ValueError("hours must match wages and be finite/nonnegative")
        if not isfinite(tax_rate) or not isfinite(rev):
            raise ValueError("tax_rate and rev must be finite")
        exponent = 1.0 + 1.0 / prefs.frisch_elasticity
        utility = (
            wages * (1.0 - tax_rate) * hours
            + rev / len(wages)
            - prefs.psi * hours**exponent / exponent
        )
        return float(np.mean(weights * utility))

    def social_welfare(
        self,
        tax_rate,
        wages,
        prefs,
        misperception_std=0,
        seed=42,
        n_mc=1000,
        *,
        mean_error=0,
        beliefs=None,
    ):
        """Deterministic expected welfare; legacy seed/n_mc are unused."""
        return self.evaluate(
            tax_rate,
            wages,
            prefs,
            beliefs,
            misperception_std=misperception_std,
            mean_error=mean_error,
        ).expected_social_welfare

    def optimal_tax_result(
        self,
        wages,
        prefs,
        misperception_std=0,
        seed=42,
        search_range=(0.0, 0.80),
        n_grid=81,
        *,
        mean_error=0,
        beliefs=None,
    ) -> OptimalTaxResult:
        """Two-pass deterministic grid search, reporting endpoint solutions.

        A boundary result is an optimum only within the stated search range.
        Grid resolution reports the refined grid spacing, not a statistical
        confidence interval or a proof of a unique global optimum.
        """
        wages, _ = self._wages_and_weights(wages)
        beliefs = self._beliefs(beliefs, misperception_std, mean_error)
        if len(search_range) != 2 or not all(isfinite(x) for x in search_range):
            raise ValueError("search_range must contain two finite rates")
        lower, upper = search_range
        if lower >= upper:
            raise ValueError("search_range must be strictly increasing")
        if not isinstance(n_grid, (int, np.integer)) or n_grid < 3:
            raise ValueError("n_grid must be an integer of at least 3")

        def best_on_grid(lo, hi):
            grid = np.linspace(lo, hi, n_grid)
            welfare = np.array(
                [
                    self.evaluate(tax, wages, prefs, beliefs).expected_social_welfare
                    for tax in grid
                ]
            )
            index = int(np.argmax(welfare))
            return float(grid[index]), float(welfare[index])

        coarse_tax, coarse_welfare = best_on_grid(lower, upper)
        step = (upper - lower) / (n_grid - 1)
        fine_lower, fine_upper = max(lower, coarse_tax - step), min(
            upper, coarse_tax + step
        )
        tax, welfare = best_on_grid(fine_lower, fine_upper)
        if coarse_welfare > welfare:
            tax, welfare = coarse_tax, coarse_welfare
        return OptimalTaxResult(
            tax_rate=tax,
            welfare=welfare,
            at_boundary=tax == lower or tax == upper,
            search_range=(float(lower), float(upper)),
            social_weights=self.social_weights,
            grid_resolution=(fine_upper - fine_lower) / (n_grid - 1),
        )

    def optimal_tax(
        self,
        wages,
        prefs,
        misperception_std=0,
        seed=42,
        search_range=(0.0, 0.80),
        n_grid=81,
        *,
        mean_error=0,
        beliefs=None,
    ):
        """Compatibility wrapper returning the tax; use result API for diagnostics."""
        return self.optimal_tax_result(
            wages,
            prefs,
            misperception_std,
            seed,
            search_range,
            n_grid,
            mean_error=mean_error,
            beliefs=beliefs,
        ).tax_rate
