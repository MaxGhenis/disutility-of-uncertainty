# Project guidance

This project studies tax misperception with quasilinear labor supply. Version 2 separates private optimization regret, changes in government revenue, and social welfare under explicit rebate rules and social dollar weights.

- Treat .12 latent error RMSE as an illustrative assumption, not a sourced empirical estimate.
- Do not present scenarios as national welfare estimates or reinstate clipped-MTR population aggregation. The national aggregation (`analysis/national.py`, Max's d340 ruling, 2026-09-25) is conditional on the assumed beliefs and elasticity: quote it only as such, only from the committed `data/national_estimate.json`, and lead with social loss, with private regret as a component.
- Use exact expected utility and fiscal accounting. The Taylor formula is a local private-regret check.
- Keep signed bias separate from dispersion and distinguish latent from censored error moments.
- For nonlinear budgets, preserve feasible choices and threshold ownership; never interpolate over unknown cliffs or invent an attained endpoint.
- Real PolicyEngine runs use the pinned managed wrapper and retain full provenance. Household net income is not automatically a complete government fiscal measure.
- `make install`, `make lint`, `make test`, `make check-results`, and `make replicate` provide the reproducible workflow. Live household tests require explicit `make test-policyengine`.
- The pipeline generates results, parameter documentation, paper tables/variables, and figures. Change the source and regenerate; do not hand-edit output numbers.
- Runtime APIs: `models/beliefs.py`, `models/accounting.py`, `models/planner.py`, `models/schedules.py`; orchestration: `pipeline.py`; assumptions: `analysis/calibration.py`; national aggregate: `analysis/national.py` (rebuild with `make national`).
- Group totals must sum per-person amounts; never evaluate a nonlinear formula at group means. Weighted statistics must ignore zero-weight records.
