"""Global labor choice on known piecewise-linear or sampled net-income budgets.

Consumption is the schedule's net income, labor hours are earnings / wage, and
preferences are quasilinear and isoelastic. No marginal tax rates are clipped.
All budgets have an explicit finite feasible earnings range. For continuous
budgets that bound corresponds to maximum hours = maximum earnings / wage.

At a discontinuity, exactly one segment owns the threshold. An open endpoint
can yield an unattained supremum: for example a benefit disappears at the exact
threshold and utility rises toward it from below. We report that mathematical
failure instead of substituting an infeasible endpoint or an arbitrary epsilon.
A finite earnings grid gives a well-defined discrete alternative.
"""

import math
from dataclasses import dataclass

from taxuncertainty.models.preferences import QuasilinearIsoelastic


class UnattainedOptimumError(ValueError):
    """Utility has a superior limit at an excluded cliff endpoint."""


@dataclass(frozen=True)
class BudgetSegment:
    """Net income = intercept + slope * earnings on one explicit interval."""

    lower: float
    upper: float
    slope: float
    intercept: float = 0.0
    lower_closed: bool = True
    upper_closed: bool = False

    def __post_init__(self):
        if not all(
            math.isfinite(x)
            for x in (self.lower, self.upper, self.slope, self.intercept)
        ):
            raise ValueError("Segment bounds and coefficients must be finite")
        if self.lower < 0 or self.upper <= self.lower:
            raise ValueError("Segments require 0 <= lower < upper")
        if not isinstance(self.lower_closed, bool) or not isinstance(
            self.upper_closed, bool
        ):
            raise ValueError("Endpoint closure must be explicit booleans")

    def contains(self, earnings):
        return (
            self.lower < earnings < self.upper
            or (earnings == self.lower and self.lower_closed)
            or (earnings == self.upper and self.upper_closed)
        )

    def value(self, earnings):
        """Evaluate the affine formula, including one-sided limits."""
        return self.intercept + self.slope * earnings


@dataclass(frozen=True)
class PiecewiseLinearBudget:
    """A fully specified schedule on [0, max earnings], including cliff sides.

    Adjacent segments must meet, and exactly one must own the shared endpoint.
    The first and last endpoints must be included. Negative slopes (MTR > 1)
    and slopes above one (earnings subsidies) are valid.
    """

    segments: tuple[BudgetSegment, ...]

    def __post_init__(self):
        object.__setattr__(self, "segments", tuple(self.segments))
        if not self.segments:
            raise ValueError("At least one segment is required")
        if self.segments[0].lower != 0 or not self.segments[0].lower_closed:
            raise ValueError("The schedule must include zero earnings")
        if not self.segments[-1].upper_closed:
            raise ValueError("The finite maximum earnings must be included")
        for left, right in zip(self.segments, self.segments[1:]):
            if left.upper != right.lower:
                raise ValueError("Segments must meet without gaps or overlaps")
            if left.upper_closed == right.lower_closed:
                raise ValueError("Exactly one segment must own each threshold")

    @property
    def max_earnings(self):
        return self.segments[-1].upper

    def net_income(self, earnings):
        if math.isfinite(earnings):
            for segment in self.segments:
                if segment.contains(earnings):
                    return segment.value(earnings)
        raise ValueError("Earnings are outside the feasible budget domain")


@dataclass(frozen=True)
class GridBudget:
    """Net income observed at a finite set of feasible earnings choices.

    There is deliberately no interpolation. Sampled outcomes cannot establish
    the location or size of every statutory cliff between grid points.
    """

    earnings: tuple[float, ...]
    net_incomes: tuple[float, ...]

    def __post_init__(self):
        object.__setattr__(self, "earnings", tuple(float(y) for y in self.earnings))
        object.__setattr__(
            self, "net_incomes", tuple(float(c) for c in self.net_incomes)
        )
        if len(self.earnings) < 2 or len(self.earnings) != len(self.net_incomes):
            raise ValueError("A grid needs at least two matched earnings/income points")
        if not all(math.isfinite(x) for x in self.earnings + self.net_incomes):
            raise ValueError("All grid points must be finite")
        if self.earnings[0] != 0 or any(
            right <= left for left, right in zip(self.earnings, self.earnings[1:])
        ):
            raise ValueError("Grid earnings must start at zero and strictly increase")

    @property
    def max_earnings(self):
        return self.earnings[-1]

    @property
    def max_grid_gap(self):
        return max(b - a for a, b in zip(self.earnings, self.earnings[1:]))

    def net_income(self, earnings):
        try:
            return self.net_incomes[self.earnings.index(earnings)]
        except ValueError as exc:
            raise ValueError(
                "Earnings must be an observed grid point; no interpolation"
            ) from exc

    def discretization(self):
        """State the domain and resolution without inventing a welfare bound."""
        return {
            "choice_set": "supplied earnings grid only",
            "minimum_earnings": 0.0,
            "maximum_earnings": self.max_earnings,
            "number_of_points": len(self.earnings),
            "maximum_grid_gap": self.max_grid_gap,
            "continuous_utility_error_bound": None,
            "limitation": (
                "No finite continuous-choice error bound is certified: unobserved "
                "cliffs and outcomes between grid points are unknown."
            ),
        }


@dataclass(frozen=True)
class BudgetChoice:
    earnings: float
    hours: float
    net_income: float
    utility: float
    net_revenue: float
    at_domain_boundary: bool


@dataclass(frozen=True)
class BudgetComparison:
    """Losses relative to informed choice under the same true schedule.

    ``revenue_change`` is realized minus informed net tax revenue. With one
    dollar of revenue rebated worth one dollar of utility, ``social_loss`` is
    private regret minus revenue change. This equal-dollar accounting is not
    a distributionally weighted planner criterion. Net revenue = earnings -
    net income requires the budget to include relevant taxes and transfers;
    other fixed income cancels in the difference. Omitted health-program costs
    or other externalities remain omitted, and must be stated by data adapters.
    """

    informed_choice: BudgetChoice
    perceived_choice: BudgetChoice
    realized_choice: BudgetChoice
    private_regret: float
    revenue_change: float
    social_loss: float


def _validate_worker(wage, prefs):
    if not math.isfinite(wage) or wage <= 0:
        raise ValueError("Hourly wage must be finite and positive")
    if not isinstance(prefs, QuasilinearIsoelastic):
        raise TypeError(
            "Schedule optimization requires QuasilinearIsoelastic preferences"
        )
    if not all(
        math.isfinite(x) and x > 0 for x in (prefs.psi, prefs.frisch_elasticity)
    ):
        raise ValueError("Preference parameters must be finite and positive")


def _choice(budget, earnings, wage, prefs):
    consumption = budget.net_income(earnings)
    hours = earnings / wage
    utility = prefs.utility(consumption, hours)
    if not math.isfinite(utility):
        raise ValueError("Utility overflowed; rescale the budget or preferences")
    return BudgetChoice(
        earnings=earnings,
        hours=hours,
        net_income=consumption,
        utility=utility,
        net_revenue=earnings - consumption,
        at_domain_boundary=earnings in (0, budget.max_earnings),
    )


def optimize_budget(budget, wage, prefs):
    """Find the global optimum, with lowest-earnings tie breaking.

    On each affine segment utility is strictly concave. Its stationary earnings
    are w * (w * slope / psi)**epsilon when slope > 0. Checking those points and
    all feasible endpoints therefore finds the global optimum. Open-endpoint
    limits are checked separately to detect a superior unattained supremum.
    Grid optimization evaluates every supplied point and makes no claim about
    the unknown schedule between points.
    """
    _validate_worker(wage, prefs)
    open_limits = []
    if isinstance(budget, GridBudget):
        candidates = list(budget.earnings)
    elif isinstance(budget, PiecewiseLinearBudget):
        candidate_set = set()
        for segment in budget.segments:
            for earnings, closed in (
                (segment.lower, segment.lower_closed),
                (segment.upper, segment.upper_closed),
            ):
                if closed:
                    candidate_set.add(earnings)
                else:
                    open_limits.append(
                        prefs.utility(segment.value(earnings), earnings / wage)
                    )
            if segment.slope > 0:
                stationary = (
                    wage * (wage * segment.slope / prefs.psi) ** prefs.frisch_elasticity
                )
                if segment.contains(stationary):
                    candidate_set.add(stationary)
        candidates = sorted(candidate_set)
    else:
        raise TypeError("Expected PiecewiseLinearBudget or GridBudget")
    choices = [_choice(budget, y, wage, prefs) for y in candidates]
    best = max(choices, key=lambda c: (c.utility, -c.earnings))
    if any(
        limit > best.utility
        # A relative tolerance would let a large fixed transfer conceal a real
        # cliff loss, although quasilinear choice is invariant to that transfer.
        and not math.isclose(limit, best.utility, rel_tol=0.0, abs_tol=1e-10)
        for limit in open_limits
    ):
        raise UnattainedOptimumError(
            "An excluded cliff endpoint has a superior utility limit: no global "
            "maximizer exists on this continuous choice set. Specify economically "
            "appropriate threshold ownership or a finite GridBudget."
        )
    return best


def compare_budgets(true_budget, perceived_budget, wage, prefs):
    """Choose on perceived income, then evaluate at the same feasible earnings."""
    if type(true_budget) is not type(perceived_budget):
        raise ValueError(
            "True and perceived budgets must use the same feasible choice set"
        )
    if isinstance(true_budget, GridBudget):
        domains_match = true_budget.earnings == perceived_budget.earnings
    elif isinstance(true_budget, PiecewiseLinearBudget):
        domains_match = true_budget.max_earnings == perceived_budget.max_earnings
    else:
        raise TypeError("Expected PiecewiseLinearBudget or GridBudget")
    if not domains_match:
        raise ValueError(
            "True and perceived budgets must use the same feasible choice set"
        )
    informed = optimize_budget(true_budget, wage, prefs)
    perceived = optimize_budget(perceived_budget, wage, prefs)
    realized = _choice(true_budget, perceived.earnings, wage, prefs)
    private_regret = informed.utility - realized.utility
    revenue_change = realized.net_revenue - informed.net_revenue
    return BudgetComparison(
        informed_choice=informed,
        perceived_choice=perceived,
        realized_choice=realized,
        private_regret=private_regret,
        revenue_change=revenue_change,
        social_loss=private_regret - revenue_change,
    )
