# Signed-error calibration

The default model still assumes a latent RMSE of 0.12. The adapter here computes
**observed study-sample errors**, not a national distribution of decision-relevant
beliefs. `examples/` contains invented software fixtures, labelled synthetic.

## Reproduce the real archive

The native Rees-Jones/Taubinsky adapter now reproduces selected source benchmarks
and exports observed Study 2 error intervals. See [NATIVE_MAPPING.md](NATIVE_MAPPING.md)
for the exact mapping, source-label discrepancy, limits and commands. The
committed aggregate cache contains real study-sample results, and the `examples/`
fixtures remain synthetic. The default pipeline verifies cache/source integrity
and generates scoped empirical paper tables without downloading microdata.

## Reproduce the offline example

```sh
uv run --no-sync python -m taxuncertainty.analysis.signed_errors \
  --csv calibration/examples/synthetic-rates.csv \
  --manifest calibration/examples/synthetic-rates.manifest.json \
  --output /tmp/synthetic-signed-errors.json
```

The canonical CSV has exactly five columns:

| Column | Meaning |
|---|---|
| `respondent_id` | Nonempty string; leading zeroes preserved; resampling unit |
| `observation_id` | Unique within respondent; identifies task or derived slope |
| `true_rate` | Matched true incentive in fractional units |
| `perceived_rate_lower` | Lower endpoint in fractional units |
| `perceived_rate_upper` | Upper endpoint; equal to lower for point observations |

Rates outside [0,1] are retained. Missing, nonfinite, reversed-interval and duplicate
records fail explicitly. Source adapters must report any exclusions before this
stage. Interval endpoints must be finite; bounding an open end category requires
an explicit support assumption, not silent clipping.

The JSON manifest requires `schema_version: 1`, `rate_unit: "fraction"`,
`weighting: "equal_respondent"`, `data_status: "synthetic"` or `"observed"`,
the canonical CSV's `input_sha256`, and nonempty descriptions of `study`,
`tax_scope`, `population`, `sample_selection`, `transformation`, and
`measurement_error`. Observed data additionally require `source_url`,
`source_sha256`, and `source_location` identifying the upstream input and mapping.
Hashes detect changed bytes; they do not prove source authenticity or validate
the substantive mapping. Archive licensing must be checked before redistribution.

## Estimands

Define signed error as perceived minus true rate. Each respondent has equal mass;
that mass is divided among their tasks. Bias, variance, second moment, RMSE and
MAE use this same measure. Variance is descriptive, with no N-1 correction, so
`RMSE² = bias² + SD²` and `RMSE >= MAE >= abs(bias)` hold. Unequal task counts
do not give some respondents more weight. The decomposition into variation
between respondent means and within respondents is descriptive; the within part
is not an estimate of measurement-error variance.

The seeded bootstrap resamples entire respondents and reports percentile
intervals for the observed moments, conditional on input processing. It is not
design-based national inference and does not account for uncertainty introduced
by estimated cleaning rules. An interval observation does not produce a midpoint
estimate automatically: bias, MSE, RMSE and MAE get sharp marginal bounds instead.
SD gets conservative outer bounds, which need not be jointly sharp with the
other moments. Identification bounds are not confidence intervals.

## Measurement error and coverage

Under `observed error = latent error + noise` and zero latent-noise covariance,
supplied noise mean/SD ranges bound latent bias and dispersion. Assuming zero
mean noise and allowing noise variance anywhere between zero and observed
variance leaves latent SD in `[0, observed SD]` and latent RMSE in
`[abs(observed bias), observed RMSE]`. This result is conditional on the classical
restriction; the data have not established it. A minimum noise SD exceeding
observed SD is rejected as infeasible, rather than set to zero latent variance.

Without the covariance restriction, a bound `a` on noise RMSE only gives latent
RMSE in `[max(0, observed RMSE-a), observed RMSE+a]` by the L2 triangle inequality.
Without a credible bound on noise, this does not identify a finite latent range.

The same triangle argument applies to errors summed across tax components on a
common population. Component errors can cancel. A federal-only RMSE is therefore
not automatically a lower bound for comprehensive-tax RMSE; national transport,
component coverage and dependence require their own evidence.

## Instrument adapters

`taxuncertainty.analysis.tax_forecasts` converts **canonical instrument records**
to the CSV schema above. It does not guess the replication archive's native
variable names. Its outputs explicitly carry
`native_archive_mapping_verified: false` until that separate mapping is audited.

```sh
uv run --no-sync python -m taxuncertainty.analysis.tax_forecasts \
  --input calibration/examples/synthetic-forecasts.json \
  --output-dir /tmp/synthetic-local-calibration
uv run --no-sync python -m taxuncertainty.analysis.tax_forecasts \
  --input calibration/examples/synthetic-mpl.json \
  --output-dir /tmp/synthetic-mpl-calibration
```

Both JSON inputs contain `schema_version: 1`, an `instrument`, a `manifest` with
the substantive scope fields above, and a `records` array. Examples show every
field. The output directory receives rates, manifest, selection diagnostics and a
calibration report. The manifest hashes both the canonical instrument input and
the adapter code, and records adapter settings.

For `instrument: "local_forecasts"`, each record supplies `respondent_id`,
`observation_id`, `income`, `true_tax`, `perceived_tax`, `in_own_bracket`, and an
optional `selected` flag (default true). Dollar amounts require
`manifest.currency_unit: "dollars"`. The caller must first apply and document the
source's respondent exclusions and forecast transformations. Own-bracket flags
must come from verified source logic; with just two points, linearity alone
cannot detect a crossing of a true tax kink or cliff.

The adapter fits separate perceived/true tax slopes on income with an intercept
for each respondent's retained local draws. It audits all exclusions, income
spans and leverage. `--minimum-income-span D` makes selection on span explicit;
changing D changes the sample, not just precision. Where there are more than two
draws, the residual-based slope-noise variance is reported only as a diagnostic
requiring linear perceived taxes and iid homoskedastic dollar-response noise.
With two draws, this variance is unidentified and recorded as null.

The separate pooled fixed-effects coefficient regresses perceived on true tax
within respondents. It weights individual slope ratios by within-respondent
true-tax sum of squares; it is not a mean signed rate error. Zero-tax respondents
can have identifiable rate errors while contributing no identification to this
scaling coefficient.

For `instrument: "mpl"`, retained records supply IDs, `selected: true`,
`true_rate`, `taxable_increment`, `untaxed_amounts` in strictly increasing order,
and `choose_taxable` booleans in that same order. The increment and offers must
use a common monetary unit. True rates require `manifest.rate_unit: "fraction"`.
Excluded records require IDs, `selected: false`, and `exclusion_reason`.
Inconsistent choices are rejected if not explicitly source-excluded. The
inequalities preserve finite intervals and retain negative endpoints. Optional
`rate_support: [0,1]` at the payload level reproduces the article's footnote-28
support convention; it requires a `manifest.rate_support_reason`. Every such
restriction is recorded, and no midpoint estimate is silently substituted.

The [Study 1 appendix evidence](study1/README.md) adds a frozen, independently
audited aggregate package and reproducible local-archive command. Its observed
projection and measurement-sensitivity results remain separate from Study 2's
interval calibration and the model's illustrative 0.12 latent RMSE.
