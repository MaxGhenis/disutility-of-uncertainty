# Tax misperception: private losses, fiscal effects, and social welfare

This research project studies when acting on a mistaken tax rate reduces private and social welfare. It retains the original project's labor-supply model and rebuilds its welfare accounting.

The model evaluates three distinct quantities:

- **Private regret:** the worker's utility loss at the true budget, holding the common transfer fixed.
- **Revenue change:** the change in net tax receipts caused by different work choices.
- **Social loss:** private regret minus the value of the revenue change under an explicit rebate rule and social dollar weights. A negative loss is a gain.

For the illustrative worker, unbiased latent errors generate about $190 of private regret and $247 of social loss. Bias can reverse the social effect. These are assumed scenarios, not estimates of national losses. The former $30–37 billion headline and clipped-MTR population calculation are retired.

## Reproduce

Install [uv](https://docs.astral.sh/uv/) and Quarto 1.9.36, then:

```sh
make install
make test
make replicate
make check-results
```

The locked default environment excludes PolicyEngine. The pipeline reads a stored, provenance-recorded household grid; it does not run or download a population simulation. Outputs are `src/taxuncertainty/data/results.json`, `paper/generated/`, `paper/_variables.yml`, and rendered `paper/_build/index.html` and `index.pdf`.

## Use the accounting model

```python
from taxuncertainty.analysis.calibration import Illustration
from taxuncertainty.models.accounting import evaluate_worker
from taxuncertainty.models.beliefs import NormalBeliefs

inputs = Illustration()
outcome = evaluate_worker(
    wage=inputs.hourly_wage,
    tax_rate=inputs.tax_rate,
    prefs=inputs.preferences,
    beliefs=NormalBeliefs(mean_error=-0.03, std_error=0.1161895003862225),
)
print(outcome.private_regret, outcome.revenue_change, outcome.social_loss)
```

The belief distribution separates signed bias, dispersion, and censoring bounds. Latent and realized error moments are both reported. The planner uses the same exact expectations with an endogenous demogrant and an explicit choice of equal or inverse-wage social weights.

`models/schedules.py` optimizes globally over known piecewise-linear budgets with explicit threshold ownership, or over supplied finite grid points without interpolation. It supports earnings subsidies and benefit cliffs. `analysis/policyengine_budgets.py` samples actual household outcomes using pinned `policyengine[us]==5.3.0` and records inputs, model/bundle versions, measure scope, and hashes. To run the separately enabled live household checks:

```sh
make test-policyengine
```

This integration is household-level and does not establish a national welfare estimate or certify every cliff between sampled points. See [REPRODUCING.md](REPRODUCING.md) for numerical conventions, artifact validation, and migration details.

## Signed-error calibration

The [calibration protocol](calibration/IDENTIFICATION.md) distinguishes observed
bias, dispersion, measurement error and tax/population coverage. The
[adapter guide](calibration/README.md) provides executable canonical examples for
local tax-liability slopes and interval-valued choices, checksum-validated CSVs,
respondent-cluster bootstrap and conditional identification bounds.

All bundled calibration examples are synthetic software fixtures. The
Rees-Jones/Taubinsky replication archive's native data mapping is still
unverified; the 0.12 latent RMSE remains illustrative. Source URLs and the exact
access blocker are recorded in [the source manifest](calibration/sources.json).
