Scripts
=======

- `run_analysis.py`: Generates figures and CSV summaries for blocks (1)–(4).

Usage examples:

- Default run (figures to timestamped results dir):
  - `PYTHONPATH=src python3 scripts/run_analysis.py`
- Reproduce paper figures to `paper/figures/`:
  - `make figures`

Key flags:

- `--a`, `--b`: Cobb–Douglas exponents
- `--T`: Total time endowment
- `--grid`: Labor grid points for EU-max (default 241)
- `--uncertainty-sd-max`: Max sd of tax uncertainty for Block 2
- `--two-worker-sd`: Sd for Block 3 comparisons
- `--pop-n`, `--wage-median`, `--wage-sigma`: Wage sampling controls for Block 4

