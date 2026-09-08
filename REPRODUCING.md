# Reproducing the revised model

The version-2 pipeline produces conditional model results. Its default inputs are illustrative and are not sufficient to identify a national welfare cost.

## Environment and commands

The project is tested with Python 3.13.9, uv 0.11.7, and Quarto 1.9.36. `uv.lock` records Python dependencies, including an optional managed PolicyEngine bundle. Python 3.10+ is declared; older supported interpreter versions are not part of the current CI runtime.

```sh
make install          # locked dev and paper extras, no PolicyEngine
make lint
make test
make generate         # exact numerical results, tables, variables, PNG figures
make check-results    # fails on changed model/results/text or figure provenance
make paper
make pdf
```

`make replicate` regenerates inputs and builds HTML and PDF. Quarto needs an installed LaTeX distribution for PDF output. The GitHub workflow installs TinyTeX. `make clean` removes project build outputs without traversing the virtual environment.

The numerical library can be installed without plotting or PolicyEngine dependencies. The full paper CLI requires the `paper` or `dev` extra for Matplotlib. The default CLI assumes it is run at the repository root; `--paper-dir` and `--output` support explicit destinations.

## Numerical definitions

For the illustrative worker, $27.50/hour, 2,000 informed hours, and a 30% true tax rate determine the labor-disutility scale. The elasticity of .33 is informed by Chetty's Hicksian intensive-margin result and mapped to the common elasticity in the quasilinear model. Error RMSE .12 is assumed, not attributed to a verified survey statistic. No workforce or GDP multiplier is applied.

`NormalBeliefs` accepts a signed `mean_error`, a nonnegative `std_error`, and lower/upper perceived-rate bounds. The defaults censor perceived rates to [0,1]; they do not redraw a truncated normal. A true subsidy with correct perceptions requires bounds containing the negative rate, for example `lower_bound=None`. Realized mean, SD and RMSE are recorded after censoring.

`evaluate_worker` reports expected private regret, earnings and revenue changes, and the equal-dollar social loss under rebating incremental revenue. `SocialPlanner` evaluates the same utility and tax account with equal or inverse-wage social weights and a uniform demogrant. Its social-welfare values are per-capita weighted utility; revenue and earnings are population totals. `evaluate_population` instead returns sums for an explicitly enumerated synthetic population and accepts normative social weights, never survey weights.

Expectations use deterministic quadrature with explicit censoring atoms and a transformation at the zero-hours corner. The default order is 256; tests compare alternative orders, analytic identities, and independent Monte Carlo calculations. Planner optimization uses 81 coarse and 81 fine points over [0,.8], recording grid resolution and whether the maximum is at a search boundary. The wage sample alone uses seed 42; changing the seed changes the synthetic planner illustration but not worker calculations.

The second-order expression is a private-regret diagnostic. It is not used as the primary welfare estimator near zero net wages or cliffs. The nonlinear solver uses the complete supplied budget and feasible earnings choices. A discontinuous continuous problem without an attained maximum raises an error; it does not invent a feasible endpoint. A sampled grid is optimized exactly over its points and carries no certified continuous-choice welfare bound.

## Generated artifacts

- `data/results.json` within the package contains schema version 2, illustrative assumptions, signed-error scenarios, exact fiscal accounting, planner results, approximation diagnostics, nonlinear examples, and the identity of the stored real household grid.
- `data/parameters.yaml` is a generated documentation snapshot (JSON, a YAML subset) of the runtime assumptions in `analysis/calibration.py`.
- `paper/generated/*.md` and `paper/_variables.yml` contain every main numerical table and inline result; editing them manually is detected by the check command.
- `paper/generated/*.png` are scientific plots generated with Matplotlib. Their manifest records model source hash, seed, and image hashes. Numerical comparisons tolerate roundoff across platforms; generated text must match.
- The package wheel includes the JSON and YAML data resources. CI installs the wheel outside the checkout to test those resources.

## Real PolicyEngine household validation

The optional extra pins `policyengine[us]==5.3.0`, verified from the live PyPI registry on September 5, 2026. That wrapper's bundle pins `policyengine-us==1.764.6` and `policyengine-core==3.30.1`; the newest standalone country release is not substituted for the certified bundle. Sources: [wrapper registry](https://pypi.org/pypi/policyengine/json) and the installed `policyengine/data/bundle/manifest.json`.

```sh
make test-policyengine
```

This explicitly enables tests marked `policyengine` with `--run-policyengine`. The normal test suite skips live integration and never installs a fake module. The live test executes actual household calculations and compares a finer nested earnings grid with a coarser one. It does not download a population dataset.

The checked-in `src/taxuncertainty/data/household_budget.json` was generated with that real wrapper for a single adult age 40, single filing status, Texas, tax year 2024, at 401 earnings points from $0 to $100,000. Its `household_net_income` measure excludes health benefits and includes some other noncash benefits. Earnings minus this measure is not a complete government fiscal score. The fixture carries its complete request, wrapper/model/bundle metadata, timestamp, grid resolution, and hashes. The loader checks provenance and rejects damaged or inconsistent artifacts.

A fresh extraction can be created explicitly:

```python
from taxuncertainty.analysis.policyengine_budgets import sample_us_household_budget

sample = sample_us_household_budget(
    year=2024,
    people=[{"age": 40}],
    tax_unit={"filing_status": "SINGLE"},
    household={"state_code": "TX"},
    earnings_max=100_000,
    count=401,
)
sample.write("household_budget.json")
```

A fresh artifact has a new generation timestamp; compare model outcomes and configuration rather than expecting its full file hash to equal an earlier run. Do not overwrite the checked-in fixture after changing model inputs without also regenerating the paper and reviewing its scope.

## Migration from version 1

`Calibration`, `PopulationWelfare`, and the national `baseline/empirical` results schema are replaced by `Illustration`, explicit accounting, and scenario results. The year-only `EmpiricalMTR` cache path fails with a retirement explanation; it cannot silently generate a national estimate. Existing labor helper names containing `dwl` remain private-regret compatibility helpers, documented accordingly. Legacy planner `seed` and `n_mc` arguments remain accepted but do not affect deterministic expectations.

The original working tree and review artifacts were preserved when the rebuild branch was created. Prior results remain accessible in Git history; they are not retained as current findings in the revised publication.

## Observed signed-error adapters

The independent calibration CLI is documented in [calibration/README.md](calibration/README.md).
It does not overwrite the model's illustrative beliefs or compute national
welfare. Run the synthetic canonical instrument examples to reproduce the
adapter outputs, then inspect the manifest, selection diagnostics and report.
`calibration/IDENTIFICATION.md` gives the proposed estimands, source locations,
noise assumptions and unresolved behavioral/population links.
`calibration/NATIVE_MAPPING.md` documents the verified native archive mapping,
actual-data command and optional `RJT_ARCHIVE` integration test. The committed
`data/rjt_replication.json` is an aggregate cache; the default pipeline checks
its hashes and published benchmark gates before generating empirical tables.
These observed quantities never replace the illustrative belief parameters. The default test suite
checks these adapters without downloading source data or calling any API.
