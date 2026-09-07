# Signed-error calibration

The default model still assumes a latent RMSE of 0.12. The adapter here computes
**observed study-sample errors**, not a national distribution of decision-relevant
beliefs. `examples/` contains invented software fixtures, labelled synthetic.

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
