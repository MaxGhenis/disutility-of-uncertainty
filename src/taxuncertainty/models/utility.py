"""Utility functions and optimal choice models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Union, Tuple
import numpy as np


class UtilityFunction(ABC):
    """Abstract base class for utility functions."""

    @abstractmethod
    def calculate(self, leisure: float, consumption: float) -> float:
        """Calculate utility given leisure and consumption."""
        pass

    @abstractmethod
    def marginal_utility_leisure(self, leisure: float, consumption: float) -> float:
        """Calculate marginal utility of leisure."""
        pass

    @abstractmethod
    def marginal_utility_consumption(self, leisure: float, consumption: float) -> float:
        """Calculate marginal utility of consumption."""
        pass


class CobbDouglasUtility(UtilityFunction):
    """Cobb-Douglas utility function: U = L^a * C^b."""

    def __init__(self, leisure_exponent: float, consumption_exponent: float):
        """Initialize Cobb-Douglas utility function.

        Parameters
        ----------
        leisure_exponent : float
            Exponent on leisure (a > 0)
        consumption_exponent : float
            Exponent on consumption (b > 0)
        """
        if leisure_exponent <= 0 or consumption_exponent <= 0:
            raise ValueError("Exponents must be positive")

        self.leisure_exponent = leisure_exponent
        self.consumption_exponent = consumption_exponent
        self.elasticity_of_substitution = 1.0  # Always 1 for Cobb-Douglas

    def calculate(self, leisure: float, consumption: float) -> float:
        """Calculate utility given leisure and consumption."""
        if leisure == 0 or consumption == 0:
            return 0.0
        return (leisure**self.leisure_exponent) * (
            consumption**self.consumption_exponent
        )

    def marginal_utility_leisure(self, leisure: float, consumption: float) -> float:
        """Calculate marginal utility of leisure."""
        if leisure == 0:
            return np.inf
        return (
            self.leisure_exponent
            * (leisure ** (self.leisure_exponent - 1))
            * (consumption**self.consumption_exponent)
        )

    def marginal_utility_consumption(self, leisure: float, consumption: float) -> float:
        """Calculate marginal utility of consumption."""
        if consumption == 0:
            return np.inf
        return (
            self.consumption_exponent
            * (leisure**self.leisure_exponent)
            * (consumption ** (self.consumption_exponent - 1))
        )

    def marginal_rate_substitution(self, leisure: float, consumption: float) -> float:
        """Calculate marginal rate of substitution (MUL/MUC)."""
        return (self.leisure_exponent / self.consumption_exponent) * (
            consumption / leisure
        )


class OptimalChoice:
    """Solves for optimal choices given utility function and constraints."""

    def __init__(self, utility_function: UtilityFunction):
        """Initialize optimal choice solver.

        Parameters
        ----------
        utility_function : UtilityFunction
            The utility function to optimize
        """
        self.utility_function = utility_function

    def optimal_leisure(
        self, wage: float, tax_rate: float, transfers: float, total_hours: float = 24
    ) -> float:
        """Calculate optimal leisure given parameters.

        For Cobb-Douglas utility, the optimal leisure is:
        L = a(w(1-t)T + v) / [w(1-t)(a+b)]

        Parameters
        ----------
        wage : float
            Wage rate per hour
        tax_rate : float
            Tax rate on labor income (between 0 and 1)
        transfers : float
            Lump-sum transfer income
        total_hours : float
            Total hours available (default 24)

        Returns
        -------
        float
            Optimal leisure hours
        """
        if not isinstance(self.utility_function, CobbDouglasUtility):
            raise NotImplementedError(
                "Only Cobb-Douglas utility is currently supported"
            )

        a = self.utility_function.leisure_exponent
        b = self.utility_function.consumption_exponent
        net_wage = wage * (1 - tax_rate)

        if net_wage <= 0:
            return total_hours  # No incentive to work

        uncapped = a * (net_wage * total_hours + transfers) / (net_wage * (a + b))
        return min(uncapped, total_hours)

    def labor_supply(
        self, wage: float, tax_rate: float, transfers: float, total_hours: float = 24
    ) -> float:
        """Calculate labor supply (work hours).

        Parameters
        ----------
        wage : float
            Wage rate per hour
        tax_rate : float
            Tax rate on labor income
        transfers : float
            Lump-sum transfer income
        total_hours : float
            Total hours available

        Returns
        -------
        float
            Hours of labor supplied
        """
        leisure = self.optimal_leisure(wage, tax_rate, transfers, total_hours)
        return total_hours - leisure

    def consumption(
        self, wage: float, tax_rate: float, transfers: float, total_hours: float = 24
    ) -> float:
        """Calculate consumption given optimal labor supply.

        Parameters
        ----------
        wage : float
            Wage rate per hour
        tax_rate : float
            Tax rate on labor income
        transfers : float
            Lump-sum transfer income
        total_hours : float
            Total hours available

        Returns
        -------
        float
            Consumption level
        """
        labor = self.labor_supply(wage, tax_rate, transfers, total_hours)
        return wage * (1 - tax_rate) * labor + transfers

    def indirect_utility(
        self, wage: float, tax_rate: float, transfers: float, total_hours: float = 24
    ) -> float:
        """Calculate indirect utility at optimal choices.

        Parameters
        ----------
        wage : float
            Wage rate per hour
        tax_rate : float
            Tax rate on labor income
        transfers : float
            Lump-sum transfer income
        total_hours : float
            Total hours available

        Returns
        -------
        float
            Utility at optimal leisure and consumption
        """
        leisure = self.optimal_leisure(wage, tax_rate, transfers, total_hours)
        consumption_level = self.consumption(wage, tax_rate, transfers, total_hours)
        return self.utility_function.calculate(leisure, consumption_level)
