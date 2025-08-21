"""Test suite for utility functions."""

import numpy as np
import pytest
from src.taxuncertainty.models.utility import (
    CobbDouglasUtility,
    OptimalChoice,
    UtilityFunction,
)


class TestCobbDouglasUtility:
    """Test Cobb-Douglas utility function implementation."""

    def test_initialization(self):
        """Test proper initialization of Cobb-Douglas utility."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        assert util.leisure_exponent == 0.5
        assert util.consumption_exponent == 0.5
        assert util.elasticity_of_substitution == 1.0

    def test_invalid_exponents(self):
        """Test that invalid exponents raise appropriate errors."""
        with pytest.raises(ValueError, match="Exponents must be positive"):
            CobbDouglasUtility(leisure_exponent=-0.5, consumption_exponent=0.5)
        
        with pytest.raises(ValueError, match="Exponents must be positive"):
            CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0)

    def test_utility_calculation(self):
        """Test utility calculation for various inputs."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        
        # Test basic calculation
        u = util.calculate(leisure=10, consumption=100)
        expected = (10 ** 0.5) * (100 ** 0.5)
        assert np.isclose(u, expected)
        
        # Test with different exponents
        util2 = CobbDouglasUtility(leisure_exponent=0.3, consumption_exponent=0.7)
        u2 = util2.calculate(leisure=10, consumption=100)
        expected2 = (10 ** 0.3) * (100 ** 0.7)
        assert np.isclose(u2, expected2)
        
        # Test edge cases
        assert util.calculate(leisure=0, consumption=100) == 0
        assert util.calculate(leisure=10, consumption=0) == 0

    def test_marginal_utilities(self):
        """Test calculation of marginal utilities."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        
        # Test marginal utility of leisure
        mu_leisure = util.marginal_utility_leisure(leisure=10, consumption=100)
        expected_mul = 0.5 * (10 ** -0.5) * (100 ** 0.5)
        assert np.isclose(mu_leisure, expected_mul)
        
        # Test marginal utility of consumption
        mu_consumption = util.marginal_utility_consumption(leisure=10, consumption=100)
        expected_muc = 0.5 * (10 ** 0.5) * (100 ** -0.5)
        assert np.isclose(mu_consumption, expected_muc)

    def test_mrs(self):
        """Test marginal rate of substitution calculation."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        
        mrs = util.marginal_rate_substitution(leisure=10, consumption=100)
        expected_mrs = (0.5 / 0.5) * (100 / 10)
        assert np.isclose(mrs, expected_mrs)


class TestOptimalChoice:
    """Test optimal choice calculations."""

    def test_optimal_leisure_basic(self):
        """Test basic optimal leisure calculation."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        choice = OptimalChoice(utility_function=util)
        
        optimal_l = choice.optimal_leisure(
            wage=10,
            tax_rate=0.2,
            transfers=0,
            total_hours=24
        )
        
        # With Cobb-Douglas and equal exponents, optimal leisure formula is:
        # L = a(wT(1-t)+v)/[w(1-t)(a+b)]
        net_wage = 10 * (1 - 0.2)
        expected = 0.5 * (net_wage * 24 + 0) / (net_wage * 1.0)
        assert np.isclose(optimal_l, expected)

    def test_optimal_leisure_with_transfers(self):
        """Test optimal leisure with positive transfers."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        choice = OptimalChoice(utility_function=util)
        
        optimal_l = choice.optimal_leisure(
            wage=10,
            tax_rate=0.2,
            transfers=50,
            total_hours=24
        )
        
        net_wage = 10 * (1 - 0.2)
        expected = 0.5 * (net_wage * 24 + 50) / (net_wage * 1.0)
        assert np.isclose(optimal_l, expected)

    def test_optimal_leisure_corner_solution(self):
        """Test that leisure is capped at total available hours."""
        util = CobbDouglasUtility(leisure_exponent=0.9, consumption_exponent=0.1)
        choice = OptimalChoice(utility_function=util)
        
        # With very high leisure preference, should hit corner
        optimal_l = choice.optimal_leisure(
            wage=10,
            tax_rate=0.2,
            transfers=1000,
            total_hours=24
        )
        
        assert optimal_l == 24

    def test_labor_supply(self):
        """Test labor supply calculation."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        choice = OptimalChoice(utility_function=util)
        
        labor = choice.labor_supply(
            wage=10,
            tax_rate=0.2,
            transfers=0,
            total_hours=24
        )
        
        optimal_leisure = choice.optimal_leisure(
            wage=10, tax_rate=0.2, transfers=0, total_hours=24
        )
        expected_labor = 24 - optimal_leisure
        assert np.isclose(labor, expected_labor)

    def test_consumption(self):
        """Test consumption calculation."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        choice = OptimalChoice(utility_function=util)
        
        consumption = choice.consumption(
            wage=10,
            tax_rate=0.2,
            transfers=50,
            total_hours=24
        )
        
        labor = choice.labor_supply(wage=10, tax_rate=0.2, transfers=50, total_hours=24)
        expected_consumption = 10 * (1 - 0.2) * labor + 50
        assert np.isclose(consumption, expected_consumption)

    def test_indirect_utility(self):
        """Test indirect utility calculation."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        choice = OptimalChoice(utility_function=util)
        
        indirect_u = choice.indirect_utility(
            wage=10,
            tax_rate=0.2,
            transfers=50,
            total_hours=24
        )
        
        optimal_l = choice.optimal_leisure(wage=10, tax_rate=0.2, transfers=50, total_hours=24)
        optimal_c = choice.consumption(wage=10, tax_rate=0.2, transfers=50, total_hours=24)
        expected_u = util.calculate(leisure=optimal_l, consumption=optimal_c)
        assert np.isclose(indirect_u, expected_u)


class TestUncertaintyInvariance:
    """Test the special property of Cobb-Douglas with uncertainty."""

    def test_wage_uncertainty_invariance(self):
        """Test that Cobb-Douglas labor supply is invariant to wage uncertainty."""
        util = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        choice = OptimalChoice(utility_function=util)
        
        # Deterministic case
        wage_certain = 10
        labor_certain = choice.labor_supply(
            wage=wage_certain, tax_rate=0.2, transfers=0, total_hours=24
        )
        
        # Uncertain case - mean-preserving spread
        wage_low = 5
        wage_high = 15
        prob_low = 0.5
        prob_high = 0.5
        
        # Expected wage should equal certain wage
        expected_wage = prob_low * wage_low + prob_high * wage_high
        assert np.isclose(expected_wage, wage_certain)
        
        # For Cobb-Douglas, labor supply at expected wage equals expected labor supply
        labor_at_expected = choice.labor_supply(
            wage=expected_wage, tax_rate=0.2, transfers=0, total_hours=24
        )
        
        labor_low = choice.labor_supply(
            wage=wage_low, tax_rate=0.2, transfers=0, total_hours=24
        )
        labor_high = choice.labor_supply(
            wage=wage_high, tax_rate=0.2, transfers=0, total_hours=24
        )
        
        # For Cobb-Douglas with σ=1, these should be equal
        expected_labor = prob_low * labor_low + prob_high * labor_high
        
        # Due to the special property of Cobb-Douglas
        assert np.isclose(labor_at_expected, labor_certain)
        assert np.isclose(expected_labor, labor_certain, rtol=0.01)