# Disutility of uncertainty

Quantifying the welfare cost of tax rate misperception. Workers who misperceive their marginal tax rate choose suboptimal labor supply, generating deadweight loss.

Core result: E[DWL]/earnings ~ 1/2 * epsilon * sigma^2 / (1 - tau).

What's here
------------

- Preference models (quasilinear-isoelastic and Cobb-Douglas): `src/taxuncertainty/models/preferences.py`
- Labor supply and deadweight loss functions: `src/taxuncertainty/models/labor.py`
- Social planner with optimal tax: `src/taxuncertainty/models/planner.py`
- Empirical calibration: `src/taxuncertainty/analysis/calibration.py`
- Population-level welfare analysis: `src/taxuncertainty/analysis/welfare.py`
- Results generation pipeline: `src/taxuncertainty/pipeline.py`
- Results accessor: `src/taxuncertainty/results.py`
- Calibration parameters: `src/taxuncertainty/data/parameters.yaml`
- Generated results: `src/taxuncertainty/data/results.json`
- Tests: `tests/`
- Paper (Quarto): `paper/`

Quick start
-----------

1. Create a virtual environment:
   - `python3 -m venv .venv && source .venv/bin/activate`
2. Install the package for code and fast tests:
   - `pip install -e ".[dev]"`
3. Add empirical microsimulation support when you want to regenerate results:
   - `pip install -e ".[policyengine]"`
4. Run fast tests:
   - `python -m pytest tests/ -m "not slow"`
5. Regenerate results:
   - `python -c "from taxuncertainty.pipeline import generate_results; generate_results()"`
6. Build the paper (optional):
   - Install the Quarto CLI
   - `cd paper && quarto render index.qmd --to html`

Replication details are in `REPRODUCING.md`.
