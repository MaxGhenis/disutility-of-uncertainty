Reproducing results
===================

This guide explains how to reproduce the analysis results and build the paper.

Environment
-----------

- Python: 3.13+ (as declared in `pyproject.toml`)
- Install dependencies: `pip install -e ".[dev]"`
- Optional: `mystmd` for building the paper (or use `make install`).

Quick start
-----------

1. Create a virtual environment and install deps:
   - `python3 -m venv .venv && source .venv/bin/activate`
   - `pip install -e ".[dev]"`
2. Run the test suite:
   - `python -m pytest tests/ -v --cov`
3. Regenerate results:
   - `python -c "from taxuncertainty.pipeline import generate_results; generate_results()"`
4. Build the paper:
   - `cd paper && myst build`

What is generated
-----------------

- `src/taxuncertainty/data/results.json` — All computed results from the pipeline, including:
  - Calibrated DWL per worker and aggregate DWL
  - DWL as share of earnings and GDP
  - Optimal tax rates under uncertainty
  - Sensitivity analysis across elasticity and misperception parameters

Determinism and seeds
---------------------

- All results are deterministic (seed=42).
- No external data are fetched; all parameters are in `src/taxuncertainty/data/parameters.yaml`.

Key model
---------

- Quasilinear-isoelastic preferences: U(C,h) = C - psi * h^(1+1/epsilon) / (1+1/epsilon)
- Optimal hours: h* = (w(1-tau)/psi)^epsilon
- DWL from misperception: E[DWL] ~ 1/2 * epsilon * w * h* * sigma^2 / (1-tau)
- Calibrated to US labor market data (BLS wages, CBO tax rates, Chetty elasticities, Rees-Jones & Taubinsky misperception estimates).
