"""Test suite for uncertainty analysis."""

import numpy as np
import pytest
from src.taxuncertainty.models.utility import CobbDouglasUtility, OptimalChoice
from src.taxuncertainty.analysis.uncertainty import (
    UncertaintyAnalysis,
    UncertaintyResults,
)


class TestUncertaintyAnalysis:
    """Test uncertainty analysis functionality."""

    @pytest.fixture
    def setup_analysis(self):
        """Set up basic analysis components."""
        utility = CobbDouglasUtility(leisure_exponent=0.5, consumption_exponent=0.5)
        analysis = UncertaintyAnalysis(utility)
        return utility, analysis

    def test_uncertainty_reduces_welfare(self, setup_analysis):
        """Test that uncertainty reduces welfare compared to certainty."""
        utility, analysis = setup_analysis

        wage = 20
        tax_rates = [0.2, 0.3, 0.4]
        probabilities = [0.25, 0.5, 0.25]

        u_certain = analysis.expected_utility_with_certainty(
            wage, tax_rates, probabilities
        )
        u_uncertain = analysis.expected_utility_with_uncertainty(
            wage, tax_rates, probabilities
        )

        # Uncertainty should reduce welfare
        assert u_certain >= u_uncertain

        # With non-trivial uncertainty, should be strictly greater
        if len(set(tax_rates)) > 1:
            assert u_certain > u_uncertain

    def test_no_uncertainty_no_loss(self, setup_analysis):
        """Test that no uncertainty means no welfare loss."""
        utility, analysis = setup_analysis

        wage = 20
        tax_rates = [0.3]  # Single tax rate = no uncertainty
        probabilities = [1.0]

        u_certain = analysis.expected_utility_with_certainty(
            wage, tax_rates, probabilities
        )
        u_uncertain = analysis.expected_utility_with_uncertainty(
            wage, tax_rates, probabilities
        )

        # Should be equal when no uncertainty
        assert np.isclose(u_certain, u_uncertain)

    def test_deadweight_loss_calculation(self, setup_analysis):
        """Test deadweight loss calculation."""
        utility, analysis = setup_analysis

        wage = 20
        tax_mean = 0.3
        tax_std = 0.1

        dwl, dwl_percent = analysis.deadweight_loss_from_uncertainty(
            wage, tax_mean, tax_std
        )

        # DWL should be non-negative
        assert dwl >= 0
        assert dwl_percent >= 0

        # No uncertainty should give zero DWL
        dwl_zero, dwl_percent_zero = analysis.deadweight_loss_from_uncertainty(
            wage, tax_mean, tax_std=0
        )
        assert dwl_zero == 0
        assert dwl_percent_zero == 0

    def test_increasing_uncertainty_increases_dwl(self, setup_analysis):
        """Test that more uncertainty leads to more deadweight loss."""
        utility, analysis = setup_analysis

        wage = 20
        tax_mean = 0.3

        # Calculate DWL for increasing uncertainty
        dwl_low, _ = analysis.deadweight_loss_from_uncertainty(
            wage, tax_mean, tax_std=0.05
        )
        dwl_medium, _ = analysis.deadweight_loss_from_uncertainty(
            wage, tax_mean, tax_std=0.10
        )
        dwl_high, _ = analysis.deadweight_loss_from_uncertainty(
            wage, tax_mean, tax_std=0.15
        )

        # More uncertainty should increase DWL
        assert dwl_low <= dwl_medium <= dwl_high
        assert dwl_low < dwl_high  # Strictly increasing for non-trivial range

    def test_social_welfare_calculation(self, setup_analysis):
        """Test social welfare calculation."""
        utility, analysis = setup_analysis

        # Create wage distribution
        np.random.seed(42)
        wages = np.random.lognormal(mean=3.0, sigma=0.5, size=100)

        # Calculate welfare with no tax
        welfare_no_tax = analysis.social_welfare(0, wages, redistribute=False)

        # Calculate welfare with tax and redistribution
        welfare_with_tax = analysis.social_welfare(0.3, wages, redistribute=True)

        # Both should be positive
        assert welfare_no_tax > 0
        assert welfare_with_tax > 0

        # With redistribution, moderate tax can increase welfare
        # (depends on wage inequality)
        # This is not guaranteed to hold for all distributions

    def test_optimal_tax_search(self, setup_analysis):
        """Test optimal tax rate search."""
        utility, analysis = setup_analysis

        # Create wage distribution with inequality
        np.random.seed(42)
        wages = np.random.lognormal(mean=3.0, sigma=0.7, size=200)

        # Find optimal tax without uncertainty
        results = analysis.optimal_tax_rate(
            wages, tax_rate_uncertainty=0, search_range=(0.1, 0.5)
        )

        # Check results structure
        assert isinstance(results, UncertaintyResults)
        assert 0.1 <= results.optimal_tax_certain <= 0.5
        assert results.deadweight_loss == 0  # No uncertainty
        assert results.expected_utility_certain > 0

    def test_optimal_tax_with_uncertainty(self, setup_analysis):
        """Test that uncertainty affects optimal tax rate."""
        utility, analysis = setup_analysis

        np.random.seed(42)
        wages = np.random.lognormal(mean=3.0, sigma=0.7, size=200)

        # Find optimal tax with uncertainty
        results = analysis.optimal_tax_rate(
            wages, tax_rate_uncertainty=0.1, search_range=(0.1, 0.5)
        )

        # Check that uncertainty causes welfare loss
        assert results.deadweight_loss > 0
        assert results.deadweight_loss_percent > 0
        assert results.expected_utility_certain > results.expected_utility_uncertain

        # Information provision should have positive value
        assert results.welfare_gain_from_information > 0

    def test_heterogeneous_agents(self, setup_analysis):
        """Test analysis with heterogeneous agent wages."""
        utility, analysis = setup_analysis

        # Create diverse wage distribution
        np.random.seed(42)
        low_wage = np.random.normal(10, 2, 50)
        high_wage = np.random.normal(50, 10, 50)
        wages = np.concatenate([low_wage, high_wage])
        wages = np.maximum(wages, 1)  # Ensure positive wages

        # Calculate welfare effects
        results = analysis.optimal_tax_rate(
            wages, tax_rate_uncertainty=0.08, search_range=(0.15, 0.4)
        )

        # Verify reasonable results
        assert 0.15 <= results.optimal_tax_certain <= 0.4
        assert results.deadweight_loss >= 0
        assert results.welfare_gain_from_information >= 0
