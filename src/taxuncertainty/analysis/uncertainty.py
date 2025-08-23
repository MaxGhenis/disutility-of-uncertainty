"""Analysis of welfare effects from tax rate uncertainty."""

from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
from scipy import stats
from src.taxuncertainty.models.utility import CobbDouglasUtility, OptimalChoice


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
        wage_distribution: Optional[stats.rv_continuous] = None,
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
        self.wage_distribution = wage_distribution or stats.lognorm(s=0.5, scale=20)

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
        tax_dist = stats.norm(loc=tax_rate_mean, scale=tax_rate_std)
        quantiles = np.linspace(0.1, 0.9, n_scenarios)
        tax_rates = [max(0, min(1, tax_dist.ppf(q))) for q in quantiles]
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
        total_welfare = 0
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

        # Find optimal tax under uncertainty
        if tax_rate_uncertainty > 0:
            welfare_uncertain = []
            for tax_mean in tax_grid:
                # Calculate expected welfare under uncertainty
                total_welfare = 0
                for wage in wage_samples:
                    # Create tax distribution
                    tax_scenarios = [
                        max(0, min(1, tax_mean + tax_rate_uncertainty * z))
                        for z in [-1.5, -0.5, 0, 0.5, 1.5]
                    ]
                    probs = [0.1, 0.2, 0.4, 0.2, 0.1]

                    # Calculate transfers based on expected tax
                    labor = self.choice_solver.labor_supply(wage, tax_mean, 0)
                    revenue = wage * tax_mean * labor
                    transfers = revenue  # Will be averaged across population

                    # Get expected utility
                    u = self.expected_utility_with_uncertainty(
                        wage, tax_scenarios, probs, transfers / len(wage_samples)
                    )
                    total_welfare += u

                welfare_uncertain.append(total_welfare / len(wage_samples))

            optimal_idx_uncertain = np.argmax(welfare_uncertain)
            optimal_tax_uncertain = tax_grid[optimal_idx_uncertain]
            max_welfare_uncertain = welfare_uncertain[optimal_idx_uncertain]
        else:
            optimal_tax_uncertain = optimal_tax_certain
            max_welfare_uncertain = max_welfare_certain

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
