# What the available evidence identifies

The author-linked replication archive is now downloaded, checksum-pinned and
mapped to native variables. We independently reproduced the three pooled Study 1
Table 1 panels and Study 2 primary/subgroup counts and midpoint regressions.
`NATIVE_MAPPING.md` records the precise filters, code locations, endpoint
conventions and a discrepancy in Appendix A9's group labels. The project stores
aggregate results; raw microdata remain local because no explicit redistribution
licence was found in the package.

Observed Study 2 intervals now give a scoped empirical result. In the primary
sample of 3,130, author-support bias bounds are +4.65 to +14.37 percentage points,
and RMSE bounds are 22.57 to 29.63 points. These are marginal identification
bounds for choice-rationalizing errors, not confidence intervals or latent
belief parameters. The paper tables are generated from the hashed aggregate
cache; use those artifacts for full precision and payoff-only sensitivity.

## Primary evidence and replication targets

Rees-Jones and Taubinsky's Study 1 elicited 2014 federal tax-liability forecasts
for a simplified salary-only hypothetical filer. The analysis sample has 4,197
respondents. Own-income forecasts, nearby perturbations and other draws in the
same bracket form the local sample. Table 1 reports a respondent-fixed-effects
scaling coefficient of 0.81 (SE 0.043), not an individual error RMSE. Source
processing includes exclusions and income-bin winsorization. The paper warns
that response noise can confound individual-level analysis.
([Article](https://doi.org/10.1093/restud/rdz045), sections 2.2 and 3.1-3.3.)

Study 2 uses randomized experimental schedules and a multiple price list. Its
3,130 retained respondents pass attention, monotonicity and endpoint screens.
Choices identify perception intervals; the paper uses midpoints and imposes
endpoint support as described in footnote 28. These are experimental incentives,
not comprehensive household taxes.
([Article](https://doi.org/10.1093/restud/rdz045), sections 4.1-4.2 and footnote 28.)

Neither source supplies a verified 0.12 latent RMSE for this model. Matching broad
demographic margins does not establish transport to all U.S. workers or to
payroll, state and benefit incentives. The code's equal respondent mass describes
the retained study sample only.

## Local slopes and the different pooled estimand

Our proposed signed-error statistic fits a perceived tax slope and a matched
true tax slope against income within each respondent's local draws. Their
difference is an observed rate error. This is a derived estimand proposed here,
not a claim that it reproduces the authors' published statistic.

Write the within-person income sum of squares as `Sxx_i`, true slope as `t_i`,
and fitted perceived slope as `b_i`. For linear true tax in those draws, pooled
fixed-effects regression of perceived on true tax gives

`beta_FE = sum(t_i * b_i * Sxx_i) / sum(t_i² * Sxx_i)`.

It equals a weighted mean of `b_i/t_i` for respondents with nonzero true tax
variation. It does not equal an unweighted mean of those ratios, and a value of
0.81 does not identify a mean error of -19 percentage points. The signed adapter
reports the pooled coefficient separately from equal-respondent error moments.
The source pooled benchmark is independently reproduced. Individual local slopes
remain a separate estimand; the native local flag includes 89 forecasts outside
the respondent's own bracket, and earlier cleaning is not fully reconstructible.

If each dollar forecast contains independent mean-zero noise with variance
`s_eta²`, a correctly specified local slope has noise variance `s_eta²/Sxx_i`.
With two draws separated by `D`, this is `2*s_eta²/D²`. Short distances amplify
noise, and two points give no residual degrees of freedom to estimate its
variance. Rounding, learning across tasks, nonlinear perceived schedules and
winsorization can violate the classical restrictions. Repeated questions at
different incomes are not automatically repeated measurements of one latent
rate. Dropping short spans needs a sample-composition audit.

## Bounds instead of an assumed reliability estimate

Let `e_obs = e_latent + u`. Under zero covariance, observed variance equals latent
variance plus noise variance. Unknown noise variance in `[0, Var(e_obs)]` and
zero mean noise leave latent SD anywhere in `[0, SD(e_obs)]`; latent RMSE lies
between `abs(E[e_obs])` and observed RMSE. These are moment-conditional ranges,
not confidence intervals. Allowing noise bias widens the bias range too.

If covariance is unrestricted but noise RMSE is bounded by `a`, the L2 triangle
inequality instead yields latent RMSE in
`[max(0, RMSE(e_obs)-a), RMSE(e_obs)+a]`. Without a credible bound on noise, no
useful finite latent range follows from observed RMSE alone. Sampling uncertainty
is a separate problem, addressed descriptively by respondent-cluster bootstrap
for point observations. MPL interval bounds are also separate from confidence
intervals; midpoint regressions do not identify within-bin dispersion.

For component errors, total second moment includes both products of component
biases and their covariances. A federal error can be cancelled by an omitted
component. The code tests this counterexample and supplies dependence-robust
RMSE ranges only when all component bounds refer to the same population and
counterfactual. It makes no automatic welfare or national extrapolation.

## Independent research memo: retained and corrected

The separate Claude research lane's `retry-result.md` was consulted on September
7. Its source locations informed this protocol. We did not adopt its proposed
comprehensive-household mixture calibration:

- A two-type mixture with ironing share `p` and wedge `d=MTR-ATR` implies bias
  `-p*d`, SD `sqrt(p*(1-p))*abs(d)`, and RMSE `sqrt(p)*abs(d)` only under that
  structural assumption. Aggregate forecasting fit does not establish the
  individual latent distribution or exclude within-type noise.
- Over a share interval containing 0.5, the SD upper bound occurs at 0.5,
  not necessarily at an endpoint. Negative wedges require the absolute value.
- The pooled scaling relation is weighted by tax variation, as derived above;
  it is not an unweighted `E[ATR/MTR]` identity.
- The stored household fixture has 401 points. Its earnings-minus-net-income
  quantity is neither federal income tax nor a complete government fiscal
  measure. Applying the federal study's share to it would add an unsupported
  tax-scope and behavioral extrapolation.

The contribution advanced here is a reproducible boundary between observed
signed errors, interval identification, response-noise assumptions and welfare
inputs. It complements the original paper's welfare analysis; it does not claim
to be the first welfare calibration of tax misperception.

## Remaining identification work

The native archive mapping and selected benchmark replication are complete.
What remains is a defensible behavioral and population link. Neither repeated
forecast tasks at different incomes nor one MPL per respondent separates stable
latent heterogeneity from response noise without additional restrictions.
Any individual Study 1 slope analysis must audit source-winsorized versus
pre-winsorization forecasts, own-bracket selection, true-tax nonlinearity and
minimum income spans. A change in span threshold changes the included population.

The source's Table 2 mean ironing coefficient does not distinguish a homogeneous
partially ironing population from an all-or-nothing mixture. Even a good fit to
mean responses therefore cannot determine the heterogeneous belief variance
needed for welfare calculations. Claims based on preliminary individual-type
classifications or interval-regression residual variance are not adopted here.
The illustrative .12 parameter is unchanged.

## Validated Study 1 appendix evidence

The independently reviewed audit at `a5191ea9f81fd414d9fbf547995dcb31341aa875`
now supplies the paper's separate finite-design evidence appendix. See
[reproduction and licensing](study1/README.md) and its exact-file manifest.
The precision-only report correction at `935ed77` leaves every included
scientific aggregate and estimator unchanged. Selection and observed-point
true-tax nonaffinity, joint affine-model/error-cap compatibility, and same-session
covariance sensitivities are documented explicitly. The 555/2470 count is not an
identified type share; the covariance decomposition requires a common target
and assumptions about error covariance. No latent belief input or Study 2
result is replaced. Earlier prospective descriptions are superseded only within
this scoped, reproducible audit.
