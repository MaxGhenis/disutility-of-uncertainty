"""Retirement notice for unsupported population estimates.

The former path clipped comprehensive marginal tax rates to [0, .99], applied a
local linear-budget approximation at cliffs, and loaded caches keyed only by
year. Those caches cannot establish model or data provenance. They must not be
used to generate national welfare estimates.

Use ``policyengine_budgets.sample_us_household_budget`` for provenance-recorded
household *grid* calculations. Population aggregation requires a separately
validated behavioral model and the managed PolicyEngine MicroSeries interface.
"""


class UnsupportedEmpiricalEstimateError(RuntimeError):
    """The requested legacy estimate does not have a defensible methodology."""


class EmpiricalMTR:
    """Fail explicitly instead of silently reusing unsupported legacy caches."""

    def __init__(self, *args, **kwargs):
        raise UnsupportedEmpiricalEstimateError(
            "EmpiricalMTR and its year-only caches are retired: clipped marginal "
            "tax rates and missing model/data provenance do not support national "
            "welfare estimates. Use sample_us_household_budget for explicitly "
            "configured household grids; it does not produce population estimates."
        )
