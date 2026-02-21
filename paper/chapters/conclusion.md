# Conclusion

This paper has shown that the inability of workers to accurately perceive their marginal tax rates imposes a quantitatively significant welfare cost. Under quasilinear-isoelastic preferences, the expected deadweight loss per worker takes the closed form $\frac{1}{2}\varepsilon\sigma^{2}/(1-\tau)$ times earnings. Calibrated to a Frisch elasticity of 0.33, a misperception standard deviation of 0.12, and a mean marginal rate of 0.30, the central estimate is \$187 per worker and \$30 billion in aggregate---0.11% of GDP annually. The full sensitivity range spans 0.04% to 0.25% of GDP (\$10 to \$71 billion), reflecting plausible variation in labor supply elasticities and misperception magnitudes. These losses arise not from future policy uncertainty but from the current opacity of the tax code.

## Policy implications

The structure of the deadweight loss formula---proportional to $\sigma^{2}$---carries a direct policy message: reducing the variance of misperception is more valuable than reducing the level of the tax rate. A 5 percentage point reduction in the misperception standard deviation (from $\sigma = 0.12$ to $\sigma = 0.07$) lowers $\sigma^{2}$ by 66%, cutting per-worker deadweight loss by roughly two-thirds. By contrast, a 3 percentage point reduction in the statutory rate (from $\tau = 0.30$ to $\tau = 0.27$) reduces the $1/(1-\tau)$ term by only about 4%. Tax simplification that makes marginal rates transparent---replacing overlapping phase-outs, credits, and deductions with a legible rate schedule---therefore dominates rate cuts as a welfare-improving reform, and does so without sacrificing revenue.

The optimal tax analysis reinforces this conclusion from a different angle. A utilitarian planner who accounts for misperception chooses a lower optimal linear tax rate of 42.9%, compared with 44.5% under perfect information. The gap of 1.6 percentage points reflects the additional efficiency cost that misperception imposes at the margin: each dollar of revenue raised creates more deadweight loss when workers cannot accurately perceive the rate they face. Simplification closes this gap by restoring the planner's ability to raise revenue at lower efficiency cost, effectively expanding the set of feasible welfare-improving tax-transfer policies.

These findings also suggest that the traditional distinction between statutory simplification (reducing compliance burden) and substantive simplification (reducing the number of rates and provisions) understates the value of the latter. Compliance costs are real but finite; the welfare cost of misperception operates continuously through distorted labor supply decisions and scales with the size of the workforce. A reform that reduces $\sigma$ even modestly for 160 million workers generates aggregate gains that dwarf plausible estimates of compliance savings.

## Limitations

Several caveats apply. The model is static: workers choose labor supply once, facing a single marginal rate. In reality, labor supply decisions unfold over time, and workers may learn about their true rate as the year progresses. This suggests the static model may overstate the cost for workers with stable employment but understate it for those making discrete labor market transitions (entering or leaving the workforce, choosing between jobs with different hours).

The analysis assumes a linear tax schedule with a single marginal rate. The actual U.S. tax code is piecewise linear with multiple brackets, phase-outs, and cliffs. Misperception of a non-linear schedule may differ qualitatively from misperception of a single rate, as workers may be uncertain not only about the level of their marginal rate but also about where bracket thresholds fall.

I have assumed that the misperception error $\delta$ is normally distributed with mean zero and constant variance across the population. In practice, misperception may be correlated with income (lower-income workers may face more complex effective schedules due to benefit phase-outs), with financial sophistication, and with access to tax preparation services. The model treats $\sigma$ as a population-level parameter and does not capture this heterogeneity.

Finally, the analysis focuses exclusively on labor supply and ignores other margins of response---savings, portfolio allocation, tax avoidance, and organizational form---that may also be distorted by rate misperception. To the extent that these margins respond to perceived rates, the total welfare cost of misperception is larger than the estimates here.

## Future work

Two extensions would strengthen and generalize these results. First, the deadweight loss formula can be applied to non-linear tax schedules by computing $\sigma_{i}$ and $\tau_{i}$ at each point in the income distribution, using microsimulation models such as PolicyEngine to generate household-level marginal rates and calibrating misperception variance as a function of schedule complexity. This would allow estimation of distributional incidence---which income groups bear the largest misperception costs---and evaluation of specific reform proposals.

Second, the assumption of homogeneous $\sigma$ can be relaxed by linking misperception variance to observable household characteristics (income, filing status, use of tax preparers) using the survey data from {cite:t}`gideon2017perception` and {cite:t}`rees2020schmeduling`. Heterogeneous $\sigma$ would sharpen both the aggregate estimates and the targeting of simplification efforts toward the provisions and populations where misperception is most costly.

```{bibliography}
```
