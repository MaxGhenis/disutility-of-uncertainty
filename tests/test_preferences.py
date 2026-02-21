"""Tests for preference models — TDD: written before implementation."""

import pytest
import numpy as np
from taxuncertainty.models.preferences import QuasilinearIsoelastic, CobbDouglas


class TestQuasilinearIsoelastic:
    """U(C, h) = C - ψ·h^(1+1/ε) / (1+1/ε)"""

    def test_init_valid(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        assert p.psi == 1.0
        assert p.frisch_elasticity == 0.5

    def test_init_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            QuasilinearIsoelastic(psi=0, frisch_elasticity=0.5)
        with pytest.raises(ValueError):
            QuasilinearIsoelastic(psi=1.0, frisch_elasticity=-0.1)

    def test_utility_formula(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        C, h = 100.0, 8.0
        expected = C - 1.0 * h ** (1 + 1 / 0.5) / (1 + 1 / 0.5)
        assert p.utility(C, h) == pytest.approx(expected)

    def test_utility_increases_in_consumption(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        assert p.utility(200, 8) > p.utility(100, 8)

    def test_utility_decreases_in_hours(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        assert p.utility(100, 8) > p.utility(100, 10)

    def test_marginal_utility_consumption_is_one(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        assert p.marginal_utility_consumption() == 1.0

    def test_marginal_disutility_labor_positive(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        assert p.marginal_disutility_labor(8.0) > 0

    def test_marginal_disutility_labor_increasing(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        assert p.marginal_disutility_labor(10.0) > p.marginal_disutility_labor(8.0)

    def test_marginal_disutility_formula(self):
        """MDL = ψ·h^(1/ε)"""
        p = QuasilinearIsoelastic(psi=2.0, frisch_elasticity=0.5)
        h = 8.0
        expected = 2.0 * h ** (1 / 0.5)
        assert p.marginal_disutility_labor(h) == pytest.approx(expected)

    def test_zero_hours_zero_disutility(self):
        p = QuasilinearIsoelastic(psi=1.0, frisch_elasticity=0.5)
        assert p.utility(100, 0.0) == pytest.approx(100.0)


class TestCobbDouglas:
    """U(L, C) = L^α · C^β"""

    def test_init_valid(self):
        cd = CobbDouglas(alpha=0.5, beta=0.5)
        assert cd.alpha == 0.5
        assert cd.beta == 0.5

    def test_init_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            CobbDouglas(alpha=0, beta=0.5)
        with pytest.raises(ValueError):
            CobbDouglas(alpha=0.5, beta=-1)

    def test_utility_formula(self):
        cd = CobbDouglas(alpha=0.5, beta=0.5)
        assert cd.utility(10, 20) == pytest.approx(10**0.5 * 20**0.5)

    def test_zero_boundary(self):
        cd = CobbDouglas(alpha=0.5, beta=0.5)
        assert cd.utility(0, 10) == 0.0
        assert cd.utility(10, 0) == 0.0
