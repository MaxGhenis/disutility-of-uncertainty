"""Preference models for tax uncertainty analysis.

Provides utility function specifications used in labor supply and DWL calculations.
"""

import numpy as np


class QuasilinearIsoelastic:
    """Quasilinear utility with isoelastic labor disutility.

    U(C, h) = C - psi * h^(1 + 1/epsilon) / (1 + 1/epsilon)

    Parameters
    ----------
    psi : float
        Disutility-of-labor scale parameter (must be > 0).
    frisch_elasticity : float
        Frisch elasticity of labor supply, epsilon (must be > 0).
    """

    def __init__(self, psi: float, frisch_elasticity: float) -> None:
        if psi <= 0:
            raise ValueError(f"psi must be positive, got {psi}")
        if frisch_elasticity <= 0:
            raise ValueError(
                f"frisch_elasticity must be positive, got {frisch_elasticity}"
            )
        self.psi = psi
        self.frisch_elasticity = frisch_elasticity

    def utility(self, consumption: float, hours: float) -> float:
        """Compute utility U(C, h).

        Parameters
        ----------
        consumption : float
            Consumption level C.
        hours : float
            Hours of labor h.

        Returns
        -------
        float
            Utility value.
        """
        eps = self.frisch_elasticity
        exponent = 1.0 + 1.0 / eps
        return consumption - self.psi * hours**exponent / exponent

    def marginal_utility_consumption(self) -> float:
        """Marginal utility of consumption (always 1 for quasilinear)."""
        return 1.0

    def marginal_disutility_labor(self, hours: float) -> float:
        """Marginal disutility of labor: psi * h^(1/epsilon).

        Parameters
        ----------
        hours : float
            Hours of labor h.

        Returns
        -------
        float
            Marginal disutility value.
        """
        return self.psi * hours ** (1.0 / self.frisch_elasticity)


class CobbDouglas:
    """Cobb-Douglas utility over leisure and consumption.

    U(L, C) = L^alpha * C^beta

    Parameters
    ----------
    alpha : float
        Exponent on leisure (must be > 0).
    beta : float
        Exponent on consumption (must be > 0).
    """

    def __init__(self, alpha: float, beta: float) -> None:
        if alpha <= 0:
            raise ValueError(f"alpha must be positive, got {alpha}")
        if beta <= 0:
            raise ValueError(f"beta must be positive, got {beta}")
        self.alpha = alpha
        self.beta = beta

    def utility(self, leisure: float, consumption: float) -> float:
        """Compute utility U(L, C).

        Parameters
        ----------
        leisure : float
            Leisure level L.
        consumption : float
            Consumption level C.

        Returns
        -------
        float
            Utility value. Returns 0 at boundaries (leisure=0 or consumption=0).
        """
        if leisure <= 0 or consumption <= 0:
            return 0.0
        return leisure**self.alpha * consumption**self.beta
