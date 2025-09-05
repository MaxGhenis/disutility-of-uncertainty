Reproducing results
===================

This guide explains how to reproduce the figures and tables used in the paper’s stylized blocks (1)–(4) using Python 3.13.

Environment
-----------

- Python: 3.13 (as declared in `pyproject.toml`)
- Install dependencies:
  - Development + research extras: `pip install -e ".[dev,research]"`
  - Optional: `mystmd`/`jupyter-book` for building the paper (or use `make install`).

Quick start
-----------

1. Create a virtual environment and install deps:
   - `python3.13 -m venv .venv && source .venv/bin/activate`
   - `pip install -e ".[dev,research]"`
   - `pip install mystmd jupyter-book` (for the book)
2. Generate figures and CSVs for blocks (1)–(4):
   - `make figures` (writes to `results/latest/`)
3. Build the MyST site (optional):
   - `make myst` (outputs to `paper/_build/site/`)

What is generated
-----------------

- Figures:
  - `block1_bias_loss.png` — Utility loss vs. perceived tax bias
  - `block2_uncertainty_loss.png` — Utility loss vs. symmetric tax uncertainty
  - `block3_two_worker_welfare.png` — Welfare vs. tax (two workers; uncertain vs. certain)
  - `block4_opt_tax_vs_sd.png` — Optimal tax vs. tax-rate uncertainty
  - `block4_welfare_vs_sd.png` — Welfare vs. tax-rate uncertainty
- CSVs mirroring each figure’s underlying series
- `summary.json` with the run configuration

Determinism and seeds
---------------------

- Scripts set a fixed NumPy seed (`--seed`) to ensure repeatable wage sampling.
- No external data are used for blocks (1)–(4); PolicyEngine integration is kept separate and can be added in a later step.

Notes on interpretation
-----------------------

- Stylized preferences (Cobb–Douglas) and simple tax uncertainty are used for transparency. Results are qualitative; magnitudes are sensitive to parameters and grids. See `scripts/run_analysis.py` for configurable options.
- For uncertainty, the analysis includes both the “optimize under expected tax” rule and the more appropriate “expected-utility maximizing labor” rule.

Next steps
----------

- Integrate PolicyEngine-US microdata for empirical exercises and richer, non-linear tax-benefit schedules.
- Pin a full environment lockfile (pip-tools or conda) and archive inputs for long-term replication.

