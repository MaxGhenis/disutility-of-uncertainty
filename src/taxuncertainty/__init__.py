"""
Tax Uncertainty: Analyzing welfare effects of uncertain tax policies.

This package provides tools for modeling and analyzing the welfare implications
of tax rate uncertainty using economic models with heterogeneous agents.
"""

from taxuncertainty.models.utility import CobbDouglasUtility, OptimalChoice
from taxuncertainty.analysis.uncertainty import UncertaintyAnalysis

__version__ = "0.1.0"

__all__ = [
    "CobbDouglasUtility",
    "OptimalChoice",
    "UncertaintyAnalysis",
]
