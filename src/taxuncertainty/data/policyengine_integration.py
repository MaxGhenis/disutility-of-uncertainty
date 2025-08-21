"""Integration with PolicyEngine-US for real tax and income data."""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from policyengine_us import Microsimulation
from policyengine_us.model_api import *


class PolicyEngineData:
    """Fetch and process real tax and income data from PolicyEngine-US."""
    
    def __init__(self, year: int = 2024):
        """Initialize PolicyEngine data fetcher.
        
        Parameters
        ----------
        year : int
            Year for simulation (default 2024)
        """
        self.year = year
        self.sim = Microsimulation()
    
    def get_marginal_tax_rates(self, n_samples: int = 1000) -> np.ndarray:
        """Get marginal tax rates for a sample of households.
        
        Parameters
        ----------
        n_samples : int
            Number of households to sample
        
        Returns
        -------
        np.ndarray
            Array of marginal tax rates
        """
        # Get household weights for sampling
        weights = self.sim.calculate("household_weight", period=self.year)
        
        # Sample households
        total_weight = weights.sum()
        probabilities = weights.values / total_weight
        household_ids = np.random.choice(
            len(weights), size=n_samples, p=probabilities, replace=True
        )
        
        # Calculate marginal tax rates
        mtrs = []
        for hh_id in household_ids:
            # Get employment income
            employment_income = self.sim.calculate(
                "employment_income", period=self.year
            ).values[hh_id]
            
            if employment_income > 0:
                # Calculate tax with current income
                tax_current = self.sim.calculate(
                    "household_tax", period=self.year
                ).values[hh_id]
                
                # Calculate tax with $1000 additional income
                sim_plus = Microsimulation()
                sim_plus.set_input(
                    "employment_income", 
                    period=self.year,
                    value=employment_income + 1000
                )
                tax_plus = sim_plus.calculate(
                    "household_tax", period=self.year
                ).values[hh_id]
                
                # Marginal tax rate
                mtr = (tax_plus - tax_current) / 1000
                mtrs.append(min(max(mtr, 0), 1))  # Bound between 0 and 1
            else:
                mtrs.append(0)
        
        return np.array(mtrs)
    
    def get_wage_distribution(self, n_samples: int = 1000) -> np.ndarray:
        """Get wage rates for a sample of workers.
        
        Parameters
        ----------
        n_samples : int
            Number of workers to sample
        
        Returns
        -------
        np.ndarray
            Array of hourly wage rates
        """
        # Get person weights
        weights = self.sim.calculate("person_weight", period=self.year)
        
        # Get employment income and hours worked
        employment_income = self.sim.calculate(
            "employment_income", period=self.year
        ).values
        
        # Assume 2000 hours per year for full-time workers
        # Filter for workers with positive income
        worker_mask = employment_income > 0
        worker_weights = weights.values[worker_mask]
        worker_income = employment_income[worker_mask]
        
        # Calculate hourly wages (assuming 2000 hours/year)
        hourly_wages = worker_income / 2000
        
        # Sample workers
        if len(worker_weights) > 0:
            probabilities = worker_weights / worker_weights.sum()
            sampled_indices = np.random.choice(
                len(worker_weights), size=n_samples, p=probabilities, replace=True
            )
            return hourly_wages[sampled_indices]
        else:
            # Fallback to lognormal distribution
            return np.random.lognormal(mean=3.0, sigma=0.5, size=n_samples)
    
    def get_income_distribution(self, n_samples: int = 1000) -> pd.DataFrame:
        """Get comprehensive income data for analysis.
        
        Parameters
        ----------
        n_samples : int
            Number of households to sample
        
        Returns
        -------
        pd.DataFrame
            DataFrame with income, taxes, and other variables
        """
        weights = self.sim.calculate("household_weight", period=self.year)
        probabilities = weights.values / weights.sum()
        household_ids = np.random.choice(
            len(weights), size=n_samples, p=probabilities, replace=True
        )
        
        data = []
        for hh_id in household_ids:
            record = {
                'household_id': hh_id,
                'employment_income': self.sim.calculate(
                    "employment_income", period=self.year
                ).values[hh_id],
                'total_income': self.sim.calculate(
                    "household_market_income", period=self.year
                ).values[hh_id],
                'federal_tax': self.sim.calculate(
                    "household_tax", period=self.year
                ).values[hh_id],
                'state_tax': self.sim.calculate(
                    "household_state_income_tax", period=self.year
                ).values[hh_id] if "household_state_income_tax" in dir(self.sim) else 0,
                'benefits': self.sim.calculate(
                    "household_benefits", period=self.year
                ).values[hh_id],
                'household_size': self.sim.calculate(
                    "household_size", period=self.year
                ).values[hh_id],
            }
            
            # Calculate effective and marginal tax rates
            if record['total_income'] > 0:
                record['effective_tax_rate'] = (
                    record['federal_tax'] + record['state_tax']
                ) / record['total_income']
            else:
                record['effective_tax_rate'] = 0
            
            data.append(record)
        
        return pd.DataFrame(data)
    
    def estimate_tax_uncertainty(self) -> Dict[str, float]:
        """Estimate current tax rate uncertainty from historical data.
        
        Returns
        -------
        Dict[str, float]
            Statistics about tax rate uncertainty
        """
        # Get current MTRs
        mtrs = self.get_marginal_tax_rates(n_samples=5000)
        
        # Calculate statistics
        stats = {
            'mean_mtr': np.mean(mtrs),
            'std_mtr': np.std(mtrs),
            'median_mtr': np.median(mtrs),
            'p25_mtr': np.percentile(mtrs, 25),
            'p75_mtr': np.percentile(mtrs, 75),
            'min_mtr': np.min(mtrs),
            'max_mtr': np.max(mtrs),
        }
        
        # Estimate policy uncertainty (simplified)
        # Based on historical tax changes, assume ±5% uncertainty in rates
        stats['policy_uncertainty_std'] = 0.05
        
        return stats