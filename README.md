# Disutility of uncertainty

How uncertainty around marginal tax rates affects social welfare.

What’s here
------------

- Core models implementing Cobb–Douglas utility and optimal labor choice: `src/taxuncertainty/models/utility.py`
- Uncertainty analysis (bias loss, EU-maximizing labor under uncertainty, two-worker planner, optimal taxes with uncertainty): `src/taxuncertainty/analysis/uncertainty.py`
- PolicyEngine-US integration scaffold: `src/taxuncertainty/data/policyengine_integration.py`
- Tests: `tests/`
- Reproducible runner for figures and tables (blocks 1–4): `scripts/run_analysis.py`

Quick start
-----------

1. Python 3.13 environment:
   - `python3.13 -m venv .venv && source .venv/bin/activate`
   - `pip install -e ".[dev,research]"`
2. Generate figures (blocks 1–4):
   - `make figures` (outputs to `results/latest`)
3. Build the MyST site (optional):
   - `make myst` (outputs to `paper/_build/site`)

Replication details are in `REPRODUCING.md`.

Roadmap
-------

1. Stylized theory and figures (done)
2. Robustness and sensitivity (grids, parameters)
3. Microdata integration with PolicyEngine-US (non-linear schedules)
4. Calibration or sufficient-statistics extensions
5. Paper polishing and submission
