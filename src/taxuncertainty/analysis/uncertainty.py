"""Analysis of welfare effects from tax rate uncertainty."""

from dataclasses import dataclass
from typing import List, Tuple, Optional, Any
import numpy as np

# SciPy is optional; provide graceful fallback where possible
try:  # pragma: no cover - environment-dependent
    from scipy import stats as _scipy_stats  # type: ignore
except Exception:  # pragma: no cover - environment-dependent
    _scipy_stats = None  # type: ignore

from taxuncertainty.models.utility import CobbDouglasUtility, OptimalChoice


@dataclass
class UncertaintyResults:
    """Results from uncertainty analysis."""

    expected_utility_certain: float
    expected_utility_uncertain: float
    deadweight_loss: float
    deadweight_loss_percent: float
    optimal_tax_certain: float
    optimal_tax_uncertain: float
    welfare_gain_from_information: float


class UncertaintyAnalysis:
    """Analyzes welfare effects of tax rate uncertainty."""

    def __init__(
        self,
        utility_function: CobbDouglasUtility,
        wage_distribution: Optional[Any] = None,
    ):
        """Initialize uncertainty analysis.

        Parameters
        ----------
        utility_function : CobbDouglasUtility
            Utility function for agents
        wage_distribution : stats.rv_continuous, optional
            Distribution of wages in population
        """
        self.utility_function = utility_function
        self.choice_solver = OptimalChoice(utility_function)
        # Keep reference to wage distribution if provided; avoid requiring SciPy by default
        self.wage_distribution = wage_distribution

    # -----------------
    # Block 1: Bias loss
    # -----------------
    def utility_loss_from_bias(
        self,
        wage: float,
        true_tax_rate: float,
        bias: float,
        transfers: float = 0.0,
        total_hours: float = 24.0,
    ) -> Tuple[float, float]:
        """Utility loss when worker misperceives the tax rate by a bias.

        The worker chooses labor based on perceived tax rate t_hat = clamp(0,1,t+bias)
        but utility is realized at the true tax rate.

        Returns (absolute loss, percent loss vs. correct perception).
        """
        t_hat = float(np.clip(true_tax_rate + bias, 0.0, 1.0))

        # Baseline: correct perception
        u_correct = self.choice_solver.indirect_utility(
            wage, true_tax_rate, transfers, total_hours
        )

        # With bias: choose based on t_hat, realize at true t
        labor_biased = self.choice_solver.labor_supply(
            wage, t_hat, transfers, total_hours
        )
        leisure_biased = total_hours - labor_biased
        consumption_biased = wage * (1 - true_tax_rate) * labor_biased + transfers
        u_biased = self.utility_function.calculate(leisure_biased, consumption_biased)

        loss = u_correct - u_biased
        loss_pct = (loss / u_correct * 100.0) if u_correct > 0 else 0.0
        return float(loss), float(loss_pct)

    # ---------------------------------------------
    # Block 2: EU-maximizing choice under uncertainty
    # ---------------------------------------------
    def _eu_given_labor(
        self,
        wage: float,
        tax_rates: List[float],
        probabilities: List[float],
        transfers: float,
        labor: float,
        total_hours: float = 24.0,
    ) -> float:
        leisure = total_hours - labor
        eu = 0.0
        for t, p in zip(tax_rates, probabilities):
            consumption = wage * (1 - t) * labor + transfers
            eu += p * self.utility_function.calculate(leisure, consumption)
        return float(eu)

    def labor_supply_eu_max(
        self,
        wage: float,
        tax_rates: List[float],
        probabilities: List[float],
        transfers: float = 0.0,
        total_hours: float = 24.0,
        n_grid: int = 241,
    ) -> float:
        """Choose labor that maximizes expected utility under tax uncertainty.

        Grid search over labor in [0, total_hours]. Returns optimal labor.
        """
        grid = np.linspace(0.0, total_hours, n_grid)
        eus = [
            self._eu_given_labor(wage, tax_rates, probabilities, transfers, h, total_hours)
            for h in grid
        ]
        best_idx = int(np.argmax(eus))
        return float(grid[best_idx])

    def expected_utility_with_uncertainty_eu_max(
        self,
        wage: float,
        tax_rates: List[float],
        probabilities: List[float],
        transfers: float = 0.0,
        total_hours: float = 24.0,
        n_grid: int = 241,
    ) -> Tuple[float, float]:
        """Expected utility when choosing labor to maximize expected utility.

        Returns (expected utility, optimal labor).
        """
        labor = self.labor_supply_eu_max(
            wage, tax_rates, probabilities, transfers, total_hours, n_grid
        )
        eu = self._eu_given_labor(
            wage, tax_rates, probabilities, transfers, labor, total_hours
        )
        return float(eu), float(labor)

    # -------------------------------------------------------
    # Block 3: Two-worker planner, ex-post demogrant balancing
    # -------------------------------------------------------
    def _closed_form_demogrant_certain(
        self,
        wages: np.ndarray,
        tax_rate: float,
        total_hours: float = 24.0,
    ) -> float:
        """Closed-form demogrant that balances the budget under certainty.

        Uses the Cobb-Douglas closed-form leisure in OptimalChoice.
        Assumes atomistic agents and linear tax with equal per-capita transfers.
        """
        if not isinstance(self.choice_solver.utility_function, CobbDouglasUtility):
            raise NotImplementedError("Closed-form only for Cobb-Douglas")
        a = self.choice_solver.utility_function.leisure_exponent
        b = self.choice_solver.utility_function.consumption_exponent
        n = len(wages)
        sum_w = float(np.sum(wages))
        # v = [(b/(a+b)) * T * t * sum(w)] / [n * (1 + (a/(a+b))* t/(1-t))]
        numerator = (b / (a + b)) * total_hours * tax_rate * sum_w
        denominator = n * (1.0 + (a / (a + b)) * tax_rate / max(1e-9, (1.0 - tax_rate)))
        return float(numerator / denominator)

    def two_worker_planner_misperception(
        self,
        wages: Tuple[float, float],
        tax_rate: float,
        tax_rates_uncertain: Optional[List[float]] = None,
        probabilities: Optional[List[float]] = None,
        total_hours: float = 24.0,
        n_grid: int = 241,
    ) -> Tuple[float, float, float]:
        """Compare welfare under perfect info vs. worker uncertainty for two agents.

        Planner picks `tax_rate` and sets demogrant using perfect-information budget
        balance. Workers actually face tax uncertainty and choose labor by maximizing
        EU given the fixed demogrant expectation; planner adjusts demogrant ex-post
        per scenario to balance the budget.

        Returns (welfare_certain, expected_welfare_uncertain, welfare_loss).
        """
        w = np.array(wages, dtype=float)
        n = len(w)

        # Perfect information demogrant and welfare
        v_certain = self._closed_form_demogrant_certain(w, tax_rate, total_hours)
        welfare_certain = 0.0
        for wi in w:
            welfare_certain += self.choice_solver.indirect_utility(
                wi, tax_rate, v_certain, total_hours
            )
        welfare_certain /= n

        # Set default symmetric uncertainty if not provided
        if tax_rates_uncertain is None or probabilities is None:
            # 5-point symmetric distribution around tax_rate
            zs = np.array([-1.5, -0.5, 0.0, 0.5, 1.5])
            probs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
            # Approx 10pp std if we treat 1.5 as ~1.5 sd units => choose sd accordingly
            sd = 0.1
            tax_rates_uncertain = [
                float(np.clip(tax_rate + sd * z, 0.0, 1.0)) for z in zs
            ]
            probabilities = probs.tolist()

        # Workers choose labor to maximize EU with expected transfers fixed to v_certain
        chosen_labor = []
        for wi in w:
            _, h = self.expected_utility_with_uncertainty_eu_max(
                wi, tax_rates_uncertain, probabilities, v_certain, total_hours, n_grid
            )
            chosen_labor.append(h)
        chosen_labor = np.array(chosen_labor)

        # Ex-post demogrant adjusts per scenario; compute expected welfare
        expected_welfare_uncertain = 0.0
        for t, p in zip(tax_rates_uncertain, probabilities):
            revenue = float(np.sum(w * t * chosen_labor))
            v_s = revenue / n
            welfare_s = 0.0
            for wi, hi in zip(w, chosen_labor):
                leisure = total_hours - hi
                consumption = wi * (1.0 - t) * hi + v_s
                welfare_s += self.utility_function.calculate(leisure, consumption)
            expected_welfare_uncertain += p * (welfare_s / n)

        welfare_loss = welfare_certain - expected_welfare_uncertain
        return float(welfare_certain), float(expected_welfare_uncertain), float(welfare_loss)

    def expected_utility_with_uncertainty(
        self,
        wage: float,
        tax_rates: List[float],
        probabilities: List[float],
        transfers: float = 0,
        total_hours: float = 24,
    ) -> float:
        """Calculate expected utility when tax rate is uncertain.

        When agents must choose labor supply before knowing the tax rate,
        they optimize based on expected after-tax wage.

        Parameters
        ----------
        wage : float
            Agent's wage rate
        tax_rates : List[float]
            Possible tax rates
        probabilities : List[float]
            Probability of each tax rate
        transfers : float
            Lump-sum transfers
        total_hours : float
            Total hours available

        Returns
        -------
        float
            Expected utility under uncertainty
        """
        # Agent chooses labor based on expected tax rate
        expected_tax = np.sum([t * p for t, p in zip(tax_rates, probabilities)])

        # Labor choice made under expected tax
        labor_choice = self.choice_solver.labor_supply(
            wage, expected_tax, transfers, total_hours
        )
        leisure_choice = total_hours - labor_choice

        # But utility realized depends on actual tax
        expected_utility = 0
        for tax_rate, prob in zip(tax_rates, probabilities):
            # Consumption depends on realized tax rate
            consumption = wage * (1 - tax_rate) * labor_choice + transfers
            utility = self.utility_function.calculate(leisure_choice, consumption)
            expected_utility += prob * utility

        return expected_utility

    def expected_utility_with_certainty(
        self,
        wage: float,
        tax_rates: List[float],
        probabilities: List[float],
        transfers: float = 0,
        total_hours: float = 24,
    ) -> float:
        """Calculate expected utility when tax rate is known before choice.

        Parameters
        ----------
        wage : float
            Agent's wage rate
        tax_rates : List[float]
            Possible tax rates
        probabilities : List[float]
            Probability of each tax rate
        transfers : float
            Lump-sum transfers
        total_hours : float
            Total hours available

        Returns
        -------
        float
            Expected utility with perfect information
        """
        expected_utility = 0
        for tax_rate, prob in zip(tax_rates, probabilities):
            # Agent can optimize for each possible tax rate
            utility = self.choice_solver.indirect_utility(
                wage, tax_rate, transfers, total_hours
            )
            expected_utility += prob * utility

        return expected_utility

    def deadweight_loss_from_uncertainty(
        self,
        wage: float,
        tax_rate_mean: float,
        tax_rate_std: float,
        n_scenarios: int = 5,
        transfers: float = 0,
        total_hours: float = 24,
    ) -> Tuple[float, float]:
        """Calculate deadweight loss from tax rate uncertainty.

        Parameters
        ----------
        wage : float
            Agent's wage rate
        tax_rate_mean : float
            Mean tax rate
        tax_rate_std : float
            Standard deviation of tax rate
        n_scenarios : int
            Number of tax rate scenarios to consider
        transfers : float
            Lump-sum transfers
        total_hours : float
            Total hours available

        Returns
        -------
        Tuple[float, float]
            (absolute DWL, DWL as percent of certain utility)
        """
        if tax_rate_std == 0:
            return 0.0, 0.0

        # Create discrete approximation of tax rate distribution
        quantiles = np.linspace(0.1, 0.9, n_scenarios)

        if _scipy_stats is not None:
            tax_dist = _scipy_stats.norm(loc=tax_rate_mean, scale=tax_rate_std)
            tax_rates = [max(0, min(1, float(tax_dist.ppf(q)))) for q in quantiles]
        else:
            # Fallback using z-scores for common quantiles; supports default n_scenarios=5
            z_lookup = {
                0.1: -1.281551565545,
                0.3: -0.524400512708,
                0.5: 0.0,
                0.7: 0.524400512708,
                0.9: 1.281551565545,
            }
            tax_rates = []
            for q in quantiles:
                z = z_lookup.get(float(np.round(q, 1)))
                if z is None:
                    raise RuntimeError(
                        "SciPy not available and quantile approximation unsupported for n_scenarios != 5"
                    )
                rate = tax_rate_mean + tax_rate_std * z
                tax_rates.append(max(0.0, min(1.0, float(rate))))
        probabilities = [1 / n_scenarios] * n_scenarios

        # Calculate utilities
        u_certain = self.expected_utility_with_certainty(
            wage, tax_rates, probabilities, transfers, total_hours
        )
        u_uncertain = self.expected_utility_with_uncertainty(
            wage, tax_rates, probabilities, transfers, total_hours
        )

        dwl = u_certain - u_uncertain
        dwl_percent = (dwl / u_certain) * 100 if u_certain > 0 else 0

        return dwl, dwl_percent

    def social_welfare(
        self, tax_rate: float, wage_samples: np.ndarray, redistribute: bool = True
    ) -> float:
        """Calculate social welfare for a given tax rate.

        Parameters
        ----------
        tax_rate : float
            Tax rate to evaluate
        wage_samples : np.ndarray
            Sample of wages from population
        redistribute : bool
            Whether tax revenue is redistributed as transfers

        Returns
        -------
        float
            Social welfare (utilitarian)
        """
        n_agents = len(wage_samples)

        # Calculate tax revenue if redistributing
        if redistribute:
            total_revenue = 0
            for wage in wage_samples:
                labor = self.choice_solver.labor_supply(wage, tax_rate, 0)
                total_revenue += wage * tax_rate * labor
            transfers = total_revenue / n_agents
        else:
            transfers = 0

        # Calculate total welfare
        total_welfare = 0.0
        for wage in wage_samples:
            utility = self.choice_solver.indirect_utility(wage, tax_rate, transfers)
            total_welfare += utility

        return total_welfare / n_agents

    def optimal_tax_rate(
        self,
        wage_samples: np.ndarray,
        tax_rate_uncertainty: float = 0,
        search_range: Tuple[float, float] = (0.1, 0.5),
        n_grid: int = 50,
    ) -> UncertaintyResults:
        """Find optimal tax rate with and without uncertainty.

        Parameters
        ----------
        wage_samples : np.ndarray
            Sample of wages from population
        tax_rate_uncertainty : float
            Standard deviation of tax rate uncertainty
        search_range : Tuple[float, float]
            Range of tax rates to search
        n_grid : int
            Number of points in grid search

        Returns
        -------
        UncertaintyResults
            Results comparing certain and uncertain cases
        """
        tax_grid = np.linspace(search_range[0], search_range[1], n_grid)

        # Find optimal tax under certainty
        welfare_certain = []
        for tax in tax_grid:
            w = self.social_welfare(tax, wage_samples, redistribute=True)
            welfare_certain.append(w)

        optimal_idx_certain = np.argmax(welfare_certain)
        optimal_tax_certain = tax_grid[optimal_idx_certain]
        max_welfare_certain = welfare_certain[optimal_idx_certain]

        # Find optimal tax under uncertainty: EU-maximizing labor + ex-post transfers
        if tax_rate_uncertainty > 0:
            welfare_uncertain = []
            for tax_mean in tax_grid:
                # Symmetric 5-point distribution around tax_mean
                zs = np.array([-1.5, -0.5, 0.0, 0.5, 1.5])
                probs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
                tax_scenarios = [
                    float(np.clip(tax_mean + tax_rate_uncertainty * z, 0.0, 1.0))
                    for z in zs
                ]

                # Expected transfers under certainty for reference (atomistic agents)
                v_certain = self._closed_form_demogrant_certain(
                    wage_samples, tax_mean
                )

                # Workers choose labor ex-ante to maximize EU with fixed expected transfer
                h_choices = np.array(
                    [
                        self.labor_supply_eu_max(
                            w, tax_scenarios, probs.tolist(), v_certain
                        )
                        for w in wage_samples
                    ]
                )

                # Compute expected welfare with ex-post demogrant adjustment per scenario
                n = len(wage_samples)
                expected_w = 0.0
                for t, p in zip(tax_scenarios, probs):
                    revenue = float(np.sum(wage_samples * t * h_choices))
                    v_s = revenue / n
                    total_w = 0.0
                    for wi, hi in zip(wage_samples, h_choices):
                        leisure = 24.0 - hi
                        consumption = wi * (1.0 - t) * hi + v_s
                        total_w += self.utility_function.calculate(leisure, consumption)
                    expected_w += p * (total_w / n)

                welfare_uncertain.append(expected_w)

            optimal_idx_uncertain = int(np.argmax(welfare_uncertain))
            optimal_tax_uncertain = float(tax_grid[optimal_idx_uncertain])
            max_welfare_uncertain = float(welfare_uncertain[optimal_idx_uncertain])
        else:
            optimal_tax_uncertain = float(optimal_tax_certain)
            max_welfare_uncertain = float(max_welfare_certain)

        # Calculate deadweight loss
        dwl = max_welfare_certain - max_welfare_uncertain
        dwl_percent = (
            (dwl / max_welfare_certain) * 100 if max_welfare_certain > 0 else 0
        )

        # Welfare gain from providing information
        welfare_gain = dwl  # Direct gain from removing uncertainty

        return UncertaintyResults(
            expected_utility_certain=max_welfare_certain,
            expected_utility_uncertain=max_welfare_uncertain,
            deadweight_loss=dwl,
            deadweight_loss_percent=dwl_percent,
            optimal_tax_certain=optimal_tax_certain,
            optimal_tax_uncertain=optimal_tax_uncertain,
            welfare_gain_from_information=welfare_gain,
        )
