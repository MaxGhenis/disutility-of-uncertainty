"""Tests for utility models."""

import pytest
import numpy as np
from taxuncertainty.models.utility import CobbDouglasUtility, OptimalChoice


def test_cobb_douglas_initialization():
    """Test Cobb-Douglas utility initialization."""
    # Valid initialization
    u = CobbDouglasUtility(0.5, 0.5)
    assert u.leisure_exponent == 0.5
    assert u.consumption_exponent == 0.5

    # Invalid initialization
    with pytest.raises(ValueError):
        CobbDouglasUtility(0, 0.5)

    with pytest.raises(ValueError):
        CobbDouglasUtility(0.5, -1)


def test_cobb_douglas_utility_calculation():
    """Test utility calculation."""
    u = CobbDouglasUtility(0.5, 0.5)

    # Test with positive values
    utility = u.calculate(10, 20)
    expected = (10**0.5) * (20**0.5)
    assert abs(utility - expected) < 1e-6

    # Test with zero values
    assert u.calculate(0, 10) == 0
    assert u.calculate(10, 0) == 0


def test_marginal_utilities():
    """Test marginal utility calculations."""
    u = CobbDouglasUtility(0.5, 0.5)

    # Test marginal utility of leisure
    mul = u.marginal_utility_leisure(10, 20)
    expected = 0.5 * (10**-0.5) * (20**0.5)
    assert abs(mul - expected) < 1e-6

    # Test marginal utility of consumption
    muc = u.marginal_utility_consumption(10, 20)
    expected = 0.5 * (10**0.5) * (20**-0.5)
    assert abs(muc - expected) < 1e-6

    # Test infinity for zero values
    assert u.marginal_utility_leisure(0, 10) == np.inf
    assert u.marginal_utility_consumption(10, 0) == np.inf


def test_optimal_choice():
    """Test optimal choice calculations."""
    u = CobbDouglasUtility(0.5, 0.5)
    choice = OptimalChoice(u)

    # Test optimal leisure
    wage = 20
    tax_rate = 0.3
    transfers = 100
    total_hours = 24

    leisure = choice.optimal_leisure(wage, tax_rate, transfers, total_hours)
    assert 0 <= leisure <= total_hours

    # Test labor supply
    labor = choice.labor_supply(wage, tax_rate, transfers, total_hours)
    assert abs(labor + leisure - total_hours) < 1e-6

    # Test optimal consumption
    consumption = choice.optimal_consumption(wage, tax_rate, transfers, total_hours)
    assert consumption > 0
