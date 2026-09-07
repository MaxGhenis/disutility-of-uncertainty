# Study 1 empirical feasibility audit

Read [REPORT.md](REPORT.md) for the substantive conclusion, [METHODS.md](METHODS.md) for definitions and proofs, and [MEASUREMENT_PROTOCOL.md](MEASUREMENT_PROTOCOL.md) for the next experiment. This independent artifact lane changes no Disutility implementation or welfare inputs.

**Reproduce locally** from this directory:

```sh
export RJT_ARCHIVE=/path/to/Schmeduling_Replication_Code.zip
export AUDIT_PYTHON=/path/to/existing/python
./reproduce.sh
```

The pinned archive is rejected unless its SHA256 is `c578518776c9cd97cc0bcf340558a9574ed2088cfeb5d1b610274e5d7ab48b15`. On this machine the script defaults to the existing PR3 virtual environment and retained archive; it installs nothing and launches no network jobs. Elsewhere provide Python 3.13 with the versions in [requirements.txt](requirements.txt). The captured environment was Python 3.13.9, NumPy 2.5.2, pandas 3.0.5 and pytest 8.4.2. Bitwise regenerated-output equality is validated in that environment; other numerical libraries can differ at machine precision.

`reproduce.sh` regenerates aggregate evidence and results, renders the report and runs the native and mathematical tests. It does not invoke the original model package. The completed adapter's Table 1 aggregate is vendored as a small provenance-tagged benchmark; its source SHA is checked against the original local file during delivery. Reproduction requires only the author archive and this artifact directory, not the PR3 checkout. The local default environment path is a convenience, not a runtime dependency on PR3's code.

- `scripts/sources.py`: in-memory ZIP verification; labels/dtypes/missingness; private numbered native-script extraction into ignored `local/native/`.
- `scripts/audit.py`: processing checks, Table 1 and retained individual parameter/grid replication, local projections, leverage, selection, repeated-measure and finite-sample bounds.
- `scripts/estimators.py`: independent numerical/statistical primitives with explicit singular-case handling.
- `scripts/sensitivity.py`: exact affine-belief falsification, correlated-error moment sensitivities, explicitly synthetic counterexamples and prospective design arithmetic.
- `scripts/verify_native_arithmetic.py`: direct two-point slope/variance validation and monetary decomposition of within-bracket phaseouts.
- `scripts/verify_reproduction.py`: one complete pipeline rerun with generated-output hash comparison.
- `scripts/report.py` and `report.template.md`: report generation from checked aggregates.
- `tests/`: actual pinned-data benchmark checks, analytical cases, adversarial errors, sharp-bound attainment, affine feasibility, rank failure, leverage and observational equivalence.
- `evidence/`: immutable-source hashes, native metadata, primary appendix grids, completed-adapter benchmark and environment.
- `results/`: aggregate JSON/CSV only. Rates/slopes are fractions; multiply by 100 for percentage points, variances by 10,000 for squared percentage points. `SYNTHETIC_*` and prospective tables are labeled mathematical examples or proposals.

No raw microdata are committed or published; the author archive gives no explicit redistribution licence. `local/` is ignored. Income and respondent selection tables describe only the retained sample. No inferred sampling weights, latent type share, national latent variance or welfare recalibration is supplied.

For Table 1, `tax` is the x-variable. For individual slopes, `ran` (income) is the x-variable. Confusing those is an estimand error. `taxguessmain` equals the source's `tgw1`; differences from `taxguessds` include 958 float32-only changes as well as 543 beyond storage conversion. The `individualestimates` rows repeat the same forecasts with model coefficients attached; they are not repeated waves.

The only edited paths relative to base are the repository's `PROGRESS.md` and `study1-audit/`. Raw source, original checkouts and the completed PR3 remain unchanged. Branch and final handoff are recorded in the lane's output report and committed progress file.

Validation and delivery evidence: [test output](evidence/validation.txt), [byte-exact reproduction](evidence/reproduction-verification.json), [source preservation](evidence/preservation-verification.json), and [independent review runtime limitation](evidence/REVIEW_STATUS.md).
