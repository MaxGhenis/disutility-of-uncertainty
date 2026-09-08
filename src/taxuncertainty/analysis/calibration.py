"""Explicit illustrative inputs and their evidentiary status.

These inputs do not identify national welfare costs. In particular, .12 is
an assumed latent rate-error RMSE, not an estimate attributed to a survey.
"""

from dataclasses import asdict, dataclass
from math import isfinite, sqrt

from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.preferences import QuasilinearIsoelastic


@dataclass(frozen=True)
class Illustration:
    """Dollar normalization and assumptions for the research note."""

    elasticity: float = 0.33
    hourly_wage: float = 27.5
    baseline_hours: float = 2000.0
    tax_rate: float = 0.30
    error_rmse: float = 0.12
    wage_log_std: float = 0.5
    synthetic_workers: int = 500
    seed: int = 42

    def __post_init__(self):
        for name in ("elasticity", "hourly_wage", "baseline_hours"):
            value = getattr(self, name)
            if not isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be positive and finite")
        if not isfinite(self.tax_rate) or self.tax_rate >= 1:
            raise ValueError("the earnings normalization requires tax_rate < 1")
        for name in ("error_rmse", "wage_log_std"):
            value = getattr(self, name)
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be nonnegative and finite")
        if not isinstance(self.synthetic_workers, int) or self.synthetic_workers < 1:
            raise ValueError("synthetic_workers must be a positive integer")

    @property
    def earnings(self):
        return self.hourly_wage * self.baseline_hours

    @property
    def preferences(self):
        psi = (
            self.hourly_wage
            * (1 - self.tax_rate)
            / self.baseline_hours ** (1 / self.elasticity)
        )
        return QuasilinearIsoelastic(psi, self.elasticity)

    def assumptions(self):
        return {
            **asdict(self),
            "baseline_earnings": self.earnings,
            "psi": self.preferences.psi,
            "status": "illustrative; no population calibration",
            "elasticity_source": {
                "url": "https://doi.org/10.3982/ECTA9043",
                "location": "Chetty (2012), abstract and p. 972",
                "concept": "Hicksian intensive-margin estimate, mapped to the common elasticity under quasilinearity",
            },
            "error_source": {
                "status": "assumed",
                "note": "No verified .12 RMSE estimate or behavioral error distribution is attributed to Rees-Jones and Taubinsky (2020).",
            },
            "dollar_normalization": f"{self.hourly_wage:.2f} dollars/hour and {self.baseline_hours:,.0f} hours are illustrative, not estimated population means",
            "perception_bounds": [0.0, 1.0],
            "fiscal_closure": "all incremental net tax revenue rebated equally; wages fixed",
        }


def beliefs_with_rmse(mean_error, rmse=0.12):
    """Normal latent errors with a specified signed mean and second moment."""
    if not isfinite(mean_error) or not isfinite(rmse) or rmse < abs(mean_error):
        raise ValueError("finite RMSE must be at least the absolute mean error")
    return NormalBeliefs(mean_error, sqrt(max(0, rmse**2 - mean_error**2)))


def private_regret_approx(earnings, elasticity, tax_rate, error_second_moment):
    """Local private regret, not social DWL; use realized moments if censored.

    This expression is a diagnostic only near tax/choice boundaries. At a
    nonpositive net wage the interior expansion does not exist.
    """
    values = (earnings, elasticity, tax_rate, error_second_moment)
    if not all(isfinite(value) for value in values):
        raise ValueError("all inputs must be finite")
    if earnings < 0 or elasticity <= 0 or error_second_moment < 0 or tax_rate >= 1:
        raise ValueError(
            "requires earnings >= 0, elasticity > 0, second moment >= 0, tax_rate < 1"
        )
    return 0.5 * elasticity * earnings * error_second_moment / (1 - tax_rate)
