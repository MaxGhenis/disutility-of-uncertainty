# Conditional results

## Private and social effects can diverge

For the unbiased latent-error scenario, social loss with an equal-valued rebate is \${{< var unbiased_social >}}. It has two components: exact expected private regret of \${{< var unbiased_private >}} and a revenue loss of \${{< var unbiased_revenue_loss >}}. The fiscal effect increases the loss relative to the private calculation.

Downward bias changes that conclusion. With a deterministic one-percentage-point underestimate, the worker loses \${{< var small_bias_private >}} privately but generates \${{< var small_bias_revenue >}} in additional revenue. Under the stipulated fiscal closure and equal social dollar weights, this is a social gain of \${{< var small_bias_social_gain >}}. This example is not a recommendation to mislead workers. It demonstrates that a private loss alone does not identify the sign of the social effect.

{{< include generated/scenarios.md >}}

![Private losses, revenue changes, and social losses at the same latent RMSE. The common true tax rate is 30%; all values are illustrative annual dollars.](generated/welfare.png){#fig-welfare width=100%}

## Optimal taxation is conditional on bias and social weights

Under inverse-wage welfare weights, the informed optimum is {{< var optimal_informed >}}%. The unbiased-error optimum is {{< var optimal_unbiased >}}%, while the scenario with a three-point downward bias and the same latent RMSE has an optimum of {{< var optimal_bias_minus_3 >}}%. A common RMSE therefore does not imply a common direction of the tax response. Equal social dollar weights yield different optima because the redistribution motive changes.

{{< include generated/planner.md >}}

The comparison holds preferences, wage distribution, fiscal closure, and the bounds on perceived rates fixed. It does not identify how a real information intervention changes beliefs. Nor does it prove that the optimum is globally monotone in noise. At very large noise levels, censoring itself changes how beliefs respond to the true rate.

## Approximation accuracy and sensitivity

The exact utility calculation remains finite at boundaries where the interior approximation is unreliable or undefined. @tbl-accuracy compares it with the historical formula using the latent second moment. The discrepancy can reflect both changed realized moments after censoring and failure of the local expansion. Replacing the latent second moment with the realized one addresses the former but does not make large behavioral errors local.

{{< include generated/accuracy.md >}}

Across true rates of 25%, 30% and 43%, assumed elasticities from 0.25 to 0.50 and error dispersions from 8 to 15 points, the interior formula ranges from understating exact private regret by {{< var approx_worst_error >}}% (elasticity {{< var approx_worst_elasticity >}}, rate {{< var approx_worst_tax >}}%, dispersion {{< var approx_worst_sd >}} points) to overstating it by {{< var approx_max_overstatement >}}% (@tbl-approximation-grid). At the illustrative baseline it understates by {{< var approx_baseline_error >}}%. An earlier draft reported 1.1% at the baseline and called 4.7% at an elasticity of 0.50 the extreme case; neither holds under exact integration, which gives {{< var approx_former_extreme_error >}}% for that case.

{{< include generated/approximation-grid.md >}}

![Left: the inverse-wage-weighted optimum as bias changes while latent RMSE remains 12 points; the dashed line is the informed optimum. Right: approximation error across true rates, comparing latent and realized second moments. Informed earnings in the right panel are separately normalized at each rate.](generated/robustness.png){#fig-robustness width=100%}

{{< include generated/sensitivity.md >}}

The sensitivity table varies assumed elasticities and mean-zero error dispersions. It describes the model across those inputs. It is not an uncertainty interval around an empirically identified national estimate.

## A conditional national aggregation {#sec-national}

The same model can be applied to every working-age earner in a population microsimulation. The result shows the national scale the illustrative assumptions imply. It is not an identified estimate of what tax misperception costs the United States: the error distribution is assumed rather than estimated, beliefs are independent of income, each budget is linear at the person's current marginal rate, and hours adjust continuously.

The {{< var national_year >}} calculation uses the managed PolicyEngine-US population microsimulation [@policyengine2026] with its certified dataset. PolicyEngine defines a person's marginal tax rate as one minus the change in household net income, excluding health benefits, when that person's earnings rise by \$1,000. By default it computes the rate only for the {{< var national_default_rate_adults >}} adults with the highest market income in each household and assigns zero to everyone else. This calculation raises that limit to {{< var national_rate_adults >}}, enough to cover every earner in the sample. It keeps people aged 18 to 64 with positive employment income: {{< var national_records >}} records. Each record's observed employment income is its informed earnings, and its marginal rate is the slope of its budget. Expected private regret, revenue change and social loss are computed exactly for each record, under mean-zero latent errors with a 12-point standard deviation censored to [0, 1] and an elasticity of 0.33, then summed with survey weights.

Marginal rates are not clipped. The {{< var national_negative_share >}}% of these workers who face negative rates lie below the default perceived-rate bounds, and the {{< var national_cliff_share >}}% facing rates of 100% or more would choose zero hours on a linear budget despite positive observed earnings. Neither group enters the main total; @tbl-national-bands reports them separately. Evaluating negative-rate workers with no lower perception bound gives a social loss of \${{< var national_inclusive_social_bn >}} billion.

For the remaining {{< var national_workers_m >}} million workers, social loss totals \${{< var national_social_bn >}} billion a year, or \${{< var national_social_per_worker >}} per worker. It has two components: private regret of \${{< var national_private_bn >}} billion and a revenue loss of \${{< var national_revenue_loss_bn >}} billion. Social loss is {{< var national_social_ratio >}} times private regret. Applying the interior formula to each record gives \${{< var national_second_order_bn >}} billion of private regret. Across elasticities from 0.25 to 0.50 and error dispersions from 8 to 15 points, the conditional total ranges from \${{< var national_social_min_bn >}} billion to \${{< var national_social_max_bn >}} billion (@tbl-national-sensitivity).

{{< include generated/national-bands.md >}}

{{< include generated/national-sensitivity.md >}}

Group totals in this section are sums of per-person amounts, so they add up to the national total. The top earnings quintile accounts for {{< var national_top_quintile_share >}}% of social loss (@tbl-national-quintiles). As a share of earnings, social loss ranges from {{< var national_quintile_share_min >}}% to {{< var national_quintile_share_max >}}% across quintiles. Weighted by survey weights, marginal rates among included workers have quartiles of {{< var mtr_p25 >}}, {{< var mtr_p50 >}} and {{< var mtr_p75 >}}, and a 90th percentile of {{< var mtr_p90 >}}.

{{< include generated/national-quintiles.md >}}

A representative worker with the included population's weighted-mean earnings (\${{< var rep_mean_earnings >}}) and weighted-mean marginal rate ({{< var rep_mean_rate >}}%) is a natural comparison. The difference between the population total and that worker's total, scaled to the same headcount, splits exactly into two terms: one from the dispersion of marginal rates, holding earnings at their mean, and one from the covariance between earnings and the per-dollar loss. The dispersion term cannot be negative for the interior private-regret formula, which is convex in the rate. The covariance term can take either sign, so a population total need not exceed the representative value. For that formula, the population total {{< var rep_second_order_direction >}} the representative value by {{< var rep_second_order_gap_pct >}}%: rate dispersion {{< var rep_second_order_dispersion_verb >}} \${{< var rep_second_order_dispersion_bn >}} billion and the covariance {{< var rep_second_order_covariance_verb >}} \${{< var rep_second_order_covariance_bn >}} billion. For exact social loss, the population total {{< var rep_social_direction >}} the representative value by {{< var rep_social_gap_pct >}}%: rate dispersion {{< var rep_social_dispersion_verb >}} \${{< var rep_social_dispersion_bn >}} billion and the covariance {{< var rep_social_covariance_verb >}} \${{< var rep_social_covariance_bn >}} billion.
