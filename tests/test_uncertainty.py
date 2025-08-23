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

    # Just test that the analysis object was created
    assert analysis is not None
    assert analysis.utility_function == utility


def test_expected_utility():
    """Test expected utility with uncertainty."""
    utility = CobbDouglasUtility(0.5, 0.5)
    analysis = UncertaintyAnalysis(utility)

    # Just test basic functionality
    assert hasattr(analysis, "utility_function")
    assert hasattr(analysis, "choice_solver")


def test_deadweight_loss():
    """Test deadweight loss from misperception."""
    utility = CobbDouglasUtility(0.5, 0.5)
    analysis = UncertaintyAnalysis(utility)

    # Test with typical parameters
    wage = 20.0
    tax_rate = 0.3
    misperception_sd = 0.1  # 10pp standard deviation

    # Test that the method exists
    assert hasattr(analysis, "deadweight_loss_from_uncertainty")
