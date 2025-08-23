"""Tests for uncertainty analysis."""

import pytest
import numpy as np
from taxuncertainty.models.utility import CobbDouglasUtility
from taxuncertainty.analysis.uncertainty import UncertaintyAnalysis


def test_uncertainty_analysis_initialization():
    """Test UncertaintyAnalysis initialization."""
    utility = CobbDouglasUtility(0.5, 0.5)
    analysis = UncertaintyAnalysis(utility)
    
    assert analysis.utility_function == utility
    assert analysis.choice_solver is not None


def test_welfare_loss_calculation():
    """Test welfare loss calculation."""
    utility = CobbDouglasUtility(0.5, 0.5)
    analysis = UncertaintyAnalysis(utility)
    
    # Test with simple parameters
    wage = 20.0
    true_tax = 0.3
    perceived_tax = 0.35  # 5pp misperception
    transfers = 100.0
    
    loss = analysis.calculate_welfare_loss(
        wage, true_tax, perceived_tax, transfers
    )
    
    # Loss should be positive when there's misperception
    assert loss > 0
    
    # Loss should be zero when perception is correct
    loss_zero = analysis.calculate_welfare_loss(
        wage, true_tax, true_tax, transfers
    )
    assert abs(loss_zero) < 1e-10


def test_expected_utility():
    """Test expected utility with uncertainty."""
    utility = CobbDouglasUtility(0.5, 0.5)
    analysis = UncertaintyAnalysis(utility)
    
    wage = 20.0
    tax_scenarios = [0.25, 0.30, 0.35]
    probabilities = [0.3, 0.4, 0.3]
    transfers = 100.0
    
    expected_u = analysis.expected_utility_with_uncertainty(
        wage, tax_scenarios, probabilities, transfers
    )
    
    # Expected utility should be positive
    assert expected_u > 0
    
    # Test with equal probabilities
    equal_probs = [1/3, 1/3, 1/3]
    expected_u2 = analysis.expected_utility_with_uncertainty(
        wage, tax_scenarios, equal_probs, transfers
    )
    assert expected_u2 > 0


def test_deadweight_loss():
    """Test deadweight loss from misperception."""
    utility = CobbDouglasUtility(0.5, 0.5)
    analysis = UncertaintyAnalysis(utility)
    
    # Test with typical parameters
    wage = 20.0
    tax_rate = 0.3
    misperception_sd = 0.1  # 10pp standard deviation
    
    dwl = analysis.deadweight_loss_from_misperception(
        wage, tax_rate, misperception_sd
    )
    
    # DWL should be positive with misperception
    assert dwl > 0
    
    # DWL should be zero with no misperception
    dwl_zero = analysis.deadweight_loss_from_misperception(
        wage, tax_rate, 0.0
    )
    assert abs(dwl_zero) < 1e-10
    
    # DWL should increase with misperception
    dwl_high = analysis.deadweight_loss_from_misperception(
        wage, tax_rate, 0.2
    )
    assert dwl_high > dwl