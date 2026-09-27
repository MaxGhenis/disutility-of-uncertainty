"""Property tests for exact private, fiscal and social accounting."""

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from taxuncertainty.analysis.welfare import evaluate_population
from taxuncertainty.models.accounting import evaluate_worker
from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.preferences import QuasilinearIsoelastic

finite = dict(allow_nan=False, allow_infinity=False)
wages = st.floats(1.0, 80.0, **finite)
psis = st.floats(0.05, 5.0, **finite)
elasticities = st.floats(0.1, 2.0, **finite)
interior_rates = st.floats(0.0, 0.95, **finite)
means = st.floats(-0.1, 0.1, **finite)
sds = st.floats(0.0, 0.25, **finite)


@given(wages, psis, elasticities, st.floats(-0.5, 1.2, **finite), means, sds)
@settings(max_examples=150, deadline=None)
def test_social_loss_identity_and_signs(wage, psi, eps, tax, mean, sd):
    prefs = QuasilinearIsoelastic(psi, eps)
    out = evaluate_worker(wage, tax, prefs, NormalBeliefs(mean, sd, lower_bound=None))
    assert out.social_loss == pytest.approx(
        out.private_regret - out.revenue_change, abs=1e-9 * (1 + out.private_regret)
    )
    assert out.private_regret >= 0
    assert out.revenue_change == pytest.approx(tax * out.earnings_change)
    assert out.transfer_change == out.revenue_change


@given(wages, psis, elasticities, interior_rates, means, sds)
@settings(max_examples=100, deadline=None)
def test_social_loss_is_expected_surplus_loss(wage, psi, eps, tax, mean, sd):
    """Differential check: surplus w h - v(h) evaluated directly at each node."""
    prefs = QuasilinearIsoelastic(psi, eps)
    beliefs = NormalBeliefs(mean, sd)
    out = evaluate_worker(wage, tax, prefs, beliefs)
    perceived, weights = beliefs.quadrature(tax)
    exponent = 1 + 1 / eps
    hours = (wage * np.maximum(0.0, 1 - perceived) / psi) ** eps
    informed = (wage * (1 - tax) / psi) ** eps

    def surplus(h):
        return wage * h - psi * h**exponent / exponent

    direct = float(weights @ (surplus(informed) - surplus(hours)))
    assert out.social_loss == pytest.approx(
        direct, rel=1e-8, abs=1e-9 * out.baseline_earnings
    )


@given(wages, psis, elasticities, interior_rates, st.floats(0.001, 0.2, **finite))
@settings(max_examples=60, deadline=None)
def test_deterministic_errors_move_revenue_against_the_error(wage, psi, eps, tax, d):
    """Underestimating the rate raises hours and revenue; overestimating lowers."""
    prefs = QuasilinearIsoelastic(psi, eps)
    low = evaluate_worker(wage, tax, prefs, NormalBeliefs(-d, 0, lower_bound=None))
    high = evaluate_worker(wage, tax, prefs, NormalBeliefs(d, 0))
    assert low.revenue_change >= 0 >= high.revenue_change
    assume(tax > 1e-6)  # below this the revenue change underflows
    assert low.social_loss < low.private_regret


@given(
    st.floats(0.5, 2.0, **finite),
    st.floats(0.05, 0.9, **finite),
    st.floats(0.25, 4.0, **finite),
)
@settings(max_examples=60, deadline=None)
def test_small_noise_limit(eps, tax, scale):
    """sigma -> 0: private ~ eps e s^2 / 2(1-t), social ~ that x (1 + t(1-e)/(1-t))."""
    prefs = QuasilinearIsoelastic(1.0, eps)
    sd = 1e-3 * min(tax, 1 - tax)
    out = evaluate_worker(scale, tax, prefs, NormalBeliefs(0, sd))
    private = 0.5 * eps * out.baseline_earnings * sd**2 / (1 - tax)
    assert out.private_regret == pytest.approx(private, rel=1e-2)
    multiplier = 1 + tax * (1 - eps) / (1 - tax)
    assert out.social_loss == pytest.approx(private * multiplier, rel=1e-2)


@given(elasticities, interior_rates)
def test_informed_worker_has_no_effects(eps, tax):
    out = evaluate_worker(10.0, tax, QuasilinearIsoelastic(1.0, eps), NormalBeliefs())
    assert out.private_regret == pytest.approx(0, abs=1e-12)
    assert out.revenue_change == pytest.approx(0, abs=1e-12)


@given(
    st.lists(
        st.tuples(wages, st.sampled_from([0.0, 0.2, 0.35, 0.6])),
        min_size=2,
        max_size=12,
    ),
    st.data(),
)
@settings(max_examples=30, deadline=None)
def test_population_totals_add_across_any_partition(workers, data):
    """With equal social weights, group totals sum to the population total."""
    prefs = QuasilinearIsoelastic(1.0, 0.33)
    beliefs = NormalBeliefs(0, 0.12)
    wage, tax = map(np.array, zip(*workers))
    labels = np.array(
        data.draw(st.lists(st.integers(0, 2), min_size=len(wage), max_size=len(wage)))
    )
    whole = evaluate_population(wage, tax, prefs, beliefs)
    for field in ("private_regret", "revenue_change", "social_loss"):
        parts = sum(
            getattr(evaluate_population(wage[m], tax[m], prefs, beliefs), field)
            for m in (labels == g for g in np.unique(labels))
        )
        assert parts == pytest.approx(
            getattr(whole, field), rel=1e-9, abs=1e-9 * (1 + whole.private_regret)
        )
