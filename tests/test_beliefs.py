"""Belief moments checked against normal identities and independent draws."""

from math import pi, sqrt

import numpy as np
import pytest

from taxuncertainty.models.beliefs import NormalBeliefs


def test_latent_rmse_includes_signed_bias():
    beliefs = NormalBeliefs(mean_error=-0.03, std_error=0.04)
    assert beliefs.latent_rmse == pytest.approx(0.05)


def test_uncensored_normal_moments():
    beliefs = NormalBeliefs(-0.03, 0.12, None, None)
    moments = beliefs.realized_moments(0.3)
    assert moments.mean_error == pytest.approx(-0.03, abs=1e-13)
    assert moments.std_error == pytest.approx(0.12, abs=1e-13)
    assert moments.rmse == pytest.approx(beliefs.latent_rmse)
    assert moments.lower_atom_probability == moments.upper_atom_probability == 0


def test_lower_censored_normal_has_known_half_normal_moments():
    # max(0, N(0,sigma^2)) has a half-probability atom and known moments.
    sigma = 0.2
    beliefs = NormalBeliefs(std_error=sigma, upper_bound=None)
    moments = beliefs.realized_moments(0)
    assert moments.lower_atom_probability == 0.5
    assert moments.mean_error == pytest.approx(sigma / sqrt(2 * pi), abs=1e-12)
    assert moments.rmse == pytest.approx(sigma / sqrt(2), abs=1e-12)
    assert moments.std_error == pytest.approx(sigma * sqrt(0.5 - 1 / (2 * pi)))


def test_censoring_changes_realized_bias_and_rmse():
    moments = NormalBeliefs(std_error=0.12).realized_moments(0.99)
    assert moments.mean_error < -0.04
    assert moments.rmse < 0.12
    assert moments.upper_atom_probability > 0.45


@pytest.mark.parametrize("tax", [-0.1, 0, 0.3, 0.99, 1.1])
def test_atoms_and_continuous_mass_sum_to_one(tax):
    rates, probability = NormalBeliefs(std_error=0.12).quadrature(tax)
    assert probability.sum() == pytest.approx(1, abs=1e-14)
    assert np.all(probability > 0)
    assert np.all((rates >= 0) & (rates <= 1))


def test_deterministic_beliefs_clip_explicitly():
    assert NormalBeliefs().quadrature(-0.1)[0][0] == 0
    assert NormalBeliefs(lower_bound=None).quadrature(-0.1)[0][0] == -0.1
    assert NormalBeliefs(-0.03, 0).realized_moments(0.3).std_error == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"mean_error": np.nan},
        {"std_error": np.inf},
        {"std_error": -0.1},
        {"lower_bound": np.inf},
        {"lower_bound": 1, "upper_bound": 0},
    ],
)
def test_invalid_beliefs_rejected(kwargs):
    with pytest.raises(ValueError):
        NormalBeliefs(**kwargs)


def test_invalid_quadrature_inputs_rejected():
    with pytest.raises(ValueError):
        NormalBeliefs().quadrature(np.nan)
    with pytest.raises(ValueError):
        NormalBeliefs().quadrature(0.3, order=0)
