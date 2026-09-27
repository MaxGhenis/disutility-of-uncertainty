"""Economic and boundary validation for known and sampled nonlinear budgets."""

import math

import numpy as np
import pytest

from taxuncertainty.models.labor import individual_dwl, optimal_hours
from taxuncertainty.models.preferences import QuasilinearIsoelastic
from taxuncertainty.models.schedules import (
    BudgetSegment,
    GridBudget,
    PiecewiseLinearBudget,
    UnattainedOptimumError,
    compare_budgets,
    optimize_budget,
)


def linear(slope, intercept=0, maximum=10):
    return PiecewiseLinearBudget(
        [BudgetSegment(0, maximum, slope, intercept, upper_closed=True)]
    )


def cliff(left_owns=True):
    return PiecewiseLinearBudget(
        [
            BudgetSegment(0, 1, 1, 2, upper_closed=left_owns),
            BudgetSegment(1, 10, 1, 0, lower_closed=not left_owns, upper_closed=True),
        ]
    )


@pytest.fixture
def prefs():
    return QuasilinearIsoelastic(psi=1, frisch_elasticity=1)


def test_progressive_schedule_optimum_at_kink(prefs):
    budget = PiecewiseLinearBudget(
        [BudgetSegment(0, 1, 2), BudgetSegment(1, 10, 0.5, 1.5, upper_closed=True)]
    )
    choice = optimize_budget(budget, 1, prefs)
    assert choice.earnings == 1
    assert choice.net_income == 2
    assert choice.utility == 1.5


def test_subsidies_and_mtrs_above_one_are_not_clipped(prefs):
    subsidy = optimize_budget(linear(1.5), 1, prefs)
    ordinary = optimize_budget(linear(1), 1, prefs)
    confiscation = optimize_budget(linear(-0.5, intercept=2), 1, prefs)
    assert subsidy.earnings == 1.5 > ordinary.earnings
    assert subsidy.net_revenue == -0.75
    assert confiscation.earnings == 0
    assert confiscation.net_income == 2


def test_global_choice_checks_later_segment_after_upward_jump(prefs):
    budget = PiecewiseLinearBudget(
        [BudgetSegment(0, 1, 2), BudgetSegment(1, 10, 2, 100, upper_closed=True)]
    )
    choice = optimize_budget(budget, 1, prefs)
    assert choice.earnings == 2
    assert choice.utility == 102


def test_cliff_includes_correct_side_and_changes_fiscal_accounting(prefs):
    actual = cliff()
    result = compare_budgets(actual, linear(1.5), 1, prefs)
    assert actual.net_income(1) == 3
    assert actual.net_income(math.nextafter(1, math.inf)) < 1.01
    assert result.informed_choice.earnings == 1
    assert result.perceived_choice.earnings == result.realized_choice.earnings == 1.5
    assert result.realized_choice.net_income == 1.5
    assert result.private_regret == 2.125
    assert result.revenue_change == 2
    assert result.social_loss == 0.125


def test_excluded_cliff_endpoint_is_not_misreported_as_feasible(prefs):
    budget = cliff(left_owns=False)
    assert budget.net_income(1) == 1
    with pytest.raises(UnattainedOptimumError, match="no global maximizer"):
        optimize_budget(budget, 1, prefs)


@pytest.mark.parametrize("fixed_transfer", [0, 1e9])
def test_unattained_optimum_detection_is_invariant_to_fixed_transfers(
    prefs, fixed_transfer
):
    budget = PiecewiseLinearBudget(
        [
            BudgetSegment(0, 0.0001, 1, fixed_transfer + 2),
            BudgetSegment(0.0001, 10, 1, fixed_transfer, upper_closed=True),
        ]
    )
    with pytest.raises(UnattainedOptimumError):
        optimize_budget(budget, 1, prefs)


def test_finite_grid_handles_cliff_that_has_no_continuous_maximum(prefs):
    budget = GridBudget([0, 0.99, 1, 2], [2, 2.99, 1, 2])
    choice = optimize_budget(budget, 1, prefs)
    assert choice.earnings == 0.99
    with pytest.raises(ValueError, match="no interpolation"):
        budget.net_income(0.995)
    assert budget.discretization()["continuous_utility_error_bound"] is None
    assert budget.max_grid_gap == 1


@pytest.mark.parametrize(
    "budget", [linear(0.7), cliff(), GridBudget([0, 1, 2], [2, 3, 2])]
)
def test_no_error_has_zero_losses_and_fiscal_change(budget, prefs):
    result = compare_budgets(budget, budget, 1, prefs)
    assert result.private_regret == 0
    assert result.revenue_change == 0
    assert result.social_loss == 0


@pytest.mark.parametrize(
    "true_tax,perceived_tax", [(0.3, 0.1), (0.3, 0.5), (-0.2, 0.1)]
)
def test_known_linear_limit_matches_labor_core(true_tax, perceived_tax):
    prefs = QuasilinearIsoelastic(psi=0.3, frisch_elasticity=0.5)
    wage = 2
    result = compare_budgets(
        linear(1 - true_tax), linear(1 - perceived_tax), wage, prefs
    )
    assert result.informed_choice.hours == pytest.approx(
        optimal_hours(wage, true_tax, prefs)
    )
    assert result.private_regret == pytest.approx(
        individual_dwl(wage, true_tax, perceived_tax, prefs)
    )
    assert result.revenue_change == pytest.approx(
        true_tax * (result.realized_choice.earnings - result.informed_choice.earnings)
    )


def test_private_regret_can_coexist_with_social_gain(prefs):
    result = compare_budgets(linear(0.7), linear(1), 1, prefs)
    assert result.private_regret == pytest.approx(0.045)
    assert result.revenue_change == pytest.approx(0.09)
    assert result.social_loss == pytest.approx(-0.045)
    resource_loss = (
        result.informed_choice.earnings
        - result.informed_choice.hours**2 / 2
        - (result.realized_choice.earnings - result.realized_choice.hours**2 / 2)
    )
    assert result.social_loss == pytest.approx(resource_loss)


def test_finite_domain_bound_is_reported(prefs):
    choice = optimize_budget(linear(20, maximum=3), 1, prefs)
    assert choice.earnings == 3
    assert choice.hours == 3
    assert choice.at_domain_boundary


def test_exact_global_optimum_dominates_dense_search():
    budget = PiecewiseLinearBudget(
        [
            BudgetSegment(0, 1, 1.4, 1),
            BudgetSegment(1, 3, -0.2, 2.6),
            BudgetSegment(3, 8, 0.7, -0.1, upper_closed=True),
        ]
    )
    prefs = QuasilinearIsoelastic(psi=0.15, frisch_elasticity=0.5)
    choice = optimize_budget(budget, 2, prefs)
    dense_utilities = [
        prefs.utility(budget.net_income(y), y / 2) for y in np.linspace(0, 8, 10001)
    ]
    assert choice.utility >= max(dense_utilities) - 1e-10


def test_true_and_perceived_domains_must_match(prefs):
    with pytest.raises(ValueError, match="same feasible choice set"):
        compare_budgets(linear(1), linear(1, maximum=5), 1, prefs)
    with pytest.raises(ValueError, match="same feasible choice set"):
        compare_budgets(
            GridBudget([0, 1], [0, 1]), GridBudget([0, 2], [0, 2]), 1, prefs
        )
    with pytest.raises(ValueError, match="same feasible choice set"):
        compare_budgets(linear(1), GridBudget([0, 10], [0, 10]), 1, prefs)


@pytest.mark.parametrize("wage", [0, -1, math.nan, math.inf])
def test_invalid_wages_are_rejected(wage, prefs):
    with pytest.raises(ValueError, match="wage"):
        optimize_budget(linear(1), wage, prefs)


def test_gaps_double_owned_boundaries_and_nonfinite_segments_rejected():
    with pytest.raises(ValueError, match="finite"):
        BudgetSegment(0, math.inf, 1)
    with pytest.raises(ValueError, match="Exactly one"):
        PiecewiseLinearBudget(
            [
                BudgetSegment(0, 1, 1, upper_closed=True),
                BudgetSegment(1, 2, 1, upper_closed=True),
            ]
        )
    with pytest.raises(ValueError, match="gaps or overlaps"):
        PiecewiseLinearBudget(
            [BudgetSegment(0, 1, 1), BudgetSegment(2, 3, 1, upper_closed=True)]
        )


@pytest.mark.parametrize(
    "earnings,incomes",
    [([1, 2], [1, 2]), ([0, 1, 1], [1, 2, 3]), ([0, 1], [0, math.nan]), ([0], [1])],
)
def test_invalid_grid_rejected(earnings, incomes):
    with pytest.raises(ValueError):
        GridBudget(earnings, incomes)
