"""Signed normal errors, with explicit censoring of perceived tax rates.

The latent error is ``perceived_tax - true_tax`` before censoring. Its
standard deviation and RMSE are different parameters whenever its mean
is nonzero. Censoring also changes all three realized moments.
"""

from dataclasses import dataclass
from functools import lru_cache
from math import erfc, isfinite, sqrt

import numpy as np


@lru_cache(maxsize=16)
def _legendre(order: int) -> tuple[np.ndarray, np.ndarray]:
    return np.polynomial.legendre.leggauss(order)


def _cdf(value: float) -> float:
    return 0.5 * erfc(-value / sqrt(2.0))


@dataclass(frozen=True)
class BeliefMoments:
    """Moments of the *realized* error after perceived-rate censoring."""

    mean_error: float
    std_error: float
    rmse: float
    lower_atom_probability: float
    upper_atom_probability: float


@dataclass(frozen=True)
class NormalBeliefs:
    """Normal latent errors censored to user-specified perceived-rate bounds.

    A negative mean means tax underestimation. ``None`` removes a bound;
    for a subsidy, use a lower bound below the true rate or no lower bound.
    The default [0, 1] bounds are an assumption, not an empirical finding.
    """

    mean_error: float = 0.0
    std_error: float = 0.0
    lower_bound: float | None = 0.0
    upper_bound: float | None = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.mean_error):
            raise ValueError("mean_error must be finite")
        if not isfinite(self.std_error) or self.std_error < 0:
            raise ValueError("std_error must be finite and nonnegative")
        for name in ("lower_bound", "upper_bound"):
            value = getattr(self, name)
            if value is not None and not isfinite(value):
                raise ValueError(f"{name} must be finite or None")
        if (
            self.lower_bound is not None
            and self.upper_bound is not None
            and self.lower_bound >= self.upper_bound
        ):
            raise ValueError("lower_bound must be below upper_bound")

    @property
    def latent_rmse(self) -> float:
        return float(np.hypot(self.mean_error, self.std_error))

    def clip(self, perceived_tax):
        """Apply the configured perceived-rate bounds to scalars or arrays."""
        return np.clip(
            perceived_tax,
            -np.inf if self.lower_bound is None else self.lower_bound,
            np.inf if self.upper_bound is None else self.upper_bound,
        )

    def quadrature(
        self, tax_rate: float, order: int = 256
    ) -> tuple[np.ndarray, np.ndarray]:
        """Return deterministic perceived rates and probability weights.

        Censoring atoms are integrated explicitly. The continuous normal
        component is integrated in standardized-error space, split at the
        zero-hours corner (perceived rate 1). A fourth-power coordinate
        transform resolves fractional-power labor supply at that corner.
        Only uncensored normal tails beyond 12 standard deviations are
        omitted (less than 4e-33 probability); weights are normalized.
        ``order`` is the Gauss-Legendre order per continuous interval.
        """
        if not isfinite(tax_rate):
            raise ValueError("tax_rate must be finite")
        if not isinstance(order, (int, np.integer)) or order < 8:
            raise ValueError("quadrature order must be an integer of at least 8")
        center = tax_rate + self.mean_error
        if not isfinite(center):
            raise ValueError("tax_rate + mean_error must be finite")
        if self.std_error == 0:
            return np.array([float(self.clip(center))]), np.array([1.0])

        lower = (
            -np.inf
            if self.lower_bound is None
            else (self.lower_bound - center) / self.std_error
        )
        upper = (
            np.inf
            if self.upper_bound is None
            else (self.upper_bound - center) / self.std_error
        )
        rates, masses = [], []
        if self.lower_bound is not None:
            rates.append(np.array([self.lower_bound]))
            masses.append(np.array([_cdf(lower)]))
        if self.upper_bound is not None:
            rates.append(np.array([self.upper_bound]))
            masses.append(np.array([_cdf(-upper)]))

        lo, hi = max(lower, -12.0), min(upper, 12.0)
        if lo < hi:
            corner = (1.0 - center) / self.std_error
            boundaries = [lo]
            if lo < corner < hi:
                boundaries.append(corner)
            boundaries.append(hi)
            nodes, weights = _legendre(order)
            unit = (nodes + 1.0) / 2.0
            for left, right in zip(boundaries[:-1], boundaries[1:]):
                span = right - left
                if right == corner:
                    # Small positive net rates remain well resolved for eps < 1.
                    z = right - span * unit**4
                    jacobian = 2.0 * span * unit**3
                else:
                    z = left + span * unit
                    jacobian = np.full_like(unit, span / 2.0)
                rates.append(np.asarray(self.clip(center + self.std_error * z)))
                density = np.exp(-0.5 * z**2) / np.sqrt(2.0 * np.pi)
                masses.append(weights * jacobian * density)

        perceived = np.concatenate(rates)
        probability = np.concatenate(masses)
        keep = probability > 0
        return perceived[keep], probability[keep] / probability.sum()

    def realized_moments(self, tax_rate: float, order: int = 256) -> BeliefMoments:
        perceived, weights = self.quadrature(tax_rate, order)
        errors = perceived - tax_rate
        mean = float(weights @ errors)
        second = float(weights @ errors**2)
        if self.std_error == 0:
            lower_atom = float(
                self.lower_bound is not None and perceived[0] == self.lower_bound
            )
            upper_atom = float(
                self.upper_bound is not None and perceived[0] == self.upper_bound
            )
        else:
            center = tax_rate + self.mean_error
            lower_atom = (
                0.0
                if self.lower_bound is None
                else _cdf((self.lower_bound - center) / self.std_error)
            )
            upper_atom = (
                0.0
                if self.upper_bound is None
                else _cdf((center - self.upper_bound) / self.std_error)
            )
        return BeliefMoments(
            mean_error=mean,
            std_error=sqrt(max(0.0, second - mean**2)),
            rmse=sqrt(second),
            lower_atom_probability=lower_atom,
            upper_atom_probability=upper_atom,
        )
