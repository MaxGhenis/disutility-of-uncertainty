# Conditional results

## Private and social effects can diverge

For the unbiased latent-error scenario, exact expected private regret is \${{< var unbiased_private >}}. Expected revenue falls by \${{< var unbiased_revenue_loss >}}, so social loss with an equal-valued rebate is \${{< var unbiased_social >}}. The fiscal effect increases the loss relative to the private calculation.

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

![Left: the inverse-wage-weighted optimum as bias changes while latent RMSE remains 12 points; the dashed line is the informed optimum. Right: approximation error across true rates, comparing latent and realized second moments. Informed earnings in the right panel are separately normalized at each rate.](generated/robustness.png){#fig-robustness width=100%}

{{< include generated/sensitivity.md >}}

The sensitivity table varies assumed elasticities and mean-zero error dispersions. It describes the model across those inputs. It is not an uncertainty interval around an empirically identified national estimate.
