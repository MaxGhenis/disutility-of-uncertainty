# Calibration

The expected DWL formula derived in the previous section---$E[\text{DWL}]/\text{earnings} \approx \frac{1}{2}\varepsilon\sigma^2/(1-\tau)$---requires three inputs: the Frisch elasticity of labor supply $\varepsilon$, the standard deviation of tax misperception $\sigma$, and the average marginal tax rate $\tau$. This section draws on the empirical public finance literature to calibrate each parameter, then computes the implied welfare costs under a range of assumptions.

## Frisch elasticity ($\varepsilon$)

The Frisch (marginal-utility-constant) elasticity governs how strongly workers adjust their hours in response to changes in the perceived net-of-tax wage. {cite:t}`chetty2012bounds` provides the most comprehensive meta-analysis of this parameter, reconciling the long-standing gap between micro and macro estimates. Micro studies using individual-level panel data (tax reforms, lottery winners) typically find Frisch elasticities of 0.25--0.50 on the intensive margin. Macro estimates, which incorporate extensive-margin responses and general equilibrium adjustments, center around 0.50. Chetty argues that optimization frictions---precisely the kind of frictions this paper studies---attenuate micro estimates, so the true structural elasticity lies between the micro and macro figures.

I adopt a central estimate of $\varepsilon = 0.33$, which represents a conservative macro-consistent value that accounts for both intensive and extensive margin responses while remaining below the highest macro estimates. The sensitivity analysis varies $\varepsilon$ over the range $[0.25, 0.50]$, spanning the micro consensus to the macro midpoint. Values below 0.25 would imply that labor supply barely responds to tax incentives (inconsistent with the macro evidence), while values above 0.50 would exceed most structural estimates.

## Misperception standard deviation ($\sigma$)

The standard deviation of tax misperception $\sigma$ is the parameter most distinctive to this paper, and multiple lines of evidence inform its calibration.

{cite:t}`rees2020schmeduling` provide the most detailed evidence on how taxpayers mentally approximate their tax schedules. They find that 43% of taxpayers use an "ironing" heuristic, mentally replacing the piecewise-linear statutory schedule with a linearized version centered on their average tax rate. Because the average rate is below the marginal rate for all taxpayers in a progressive system, this heuristic systematically underestimates the marginal rate. The typical ironer perceives a marginal rate roughly equal to her average rate, generating errors on the order of 5--15 percentage points depending on income.

{cite:t}`gideon2017perception` provides direct survey evidence on tax rate knowledge. Only 33.7% of respondents correctly identify that their marginal tax rate exceeds their average tax rate---the basic qualitative feature of a progressive tax system. The remaining two-thirds either believe the rates are equal (consistent with the ironing heuristic) or believe the marginal rate is lower than the average rate (an error of both sign and magnitude). Gideon estimates mean absolute errors of approximately 15 percentage points relative to the true marginal rate.

The cross-sectional root-mean-square error of perceived minus actual marginal rates in {cite:t}`rees2020schmeduling` is approximately 0.12, which I adopt directly as the calibrated $\sigma$. I use $\sigma = 0.12$ as the central estimate and explore the range $[0.08, 0.15]$. The lower bound ($\sigma = 0.08$) corresponds to a population with moderate confusion about bracket boundaries but correct understanding of the progressive structure. The upper bound ($\sigma = 0.15$) reflects the raw survey evidence without adjustment for any respondent sophistication.

## Mean marginal tax rate ($\bar{\tau}$)

The Congressional Budget Office (CBO) has published detailed estimates of effective marginal tax rates (MTRs) faced by U.S. workers. {cite:t}`cbo2012marginal` and {cite:t}`cbo2016marginal` compute effective rates that incorporate federal income taxes, payroll taxes (employer and employee shares), state income taxes, and the phase-out of major transfer programs. These reports find effective marginal rates of 25--32% for households in the middle three income quintiles, rising to 43% for high-income households (who face the top federal bracket plus the Medicare surtax).

For the representative-worker calculation, I use $\bar{\tau} = 0.30$, which reflects the earnings-weighted average across the working population. This figure includes the combined federal income tax rate (averaging roughly 18% across brackets), the employee share of payroll taxes (7.65%), and an average state income tax contribution of approximately 4%. The sensitivity to $\bar{\tau}$ enters through the $(1-\tau)$ denominator: at $\tau = 0.25$ the amplification factor is $1/0.75 = 1.33$, while at $\tau = 0.43$ it rises to $1/0.57 = 1.75$.

## Labor market parameters

I calibrate the representative worker using standard Bureau of Labor Statistics (BLS) Occupational Employment and Wage Statistics (OEWS) data {cite:p}`bls2023oews`. Mean hourly wages across all occupations are approximately \$27.50 (2023 dollars). At 2,000 annual hours (50 weeks at 40 hours), this implies mean annual earnings of \$55,000. The total number of employed workers in the U.S. civilian labor force is approximately 160 million {cite:p}`bls2024cps`. U.S. GDP is approximately \$28 trillion (Bureau of Economic Analysis), used as the denominator for expressing aggregate costs as a share of national output.

For the optimal tax computation, wages are drawn from a lognormal distribution with log-standard-deviation 0.5, calibrated to match the mean hourly wage of \$27.50. This produces a wage distribution with a Gini coefficient of approximately 0.28, which is conservative relative to the full U.S. hourly wage distribution (Gini ~ 0.40).

## Baseline and sensitivity results

Applying the formula $\text{DWL per worker} = \frac{1}{2}\varepsilon \cdot \text{earnings} \cdot \sigma^2 / (1-\tau)$ with earnings $= \$55{,}000$ and $\tau = 0.30$, and aggregating over 160 million workers:

:::{table} Sensitivity of deadweight loss estimates to Frisch elasticity and misperception standard deviation
:label: tab-sensitivity
:align: center

| $\varepsilon$ | $\sigma$ | Per-worker DWL | Total DWL (\$B) | % of GDP |
|:---:|:---:|---:|---:|---:|
| 0.25 | 0.08 | \$63 | \$10.1 | 0.04 |
| 0.25 | 0.12 | \$141 | \$22.6 | 0.08 |
| 0.25 | 0.15 | \$221 | \$35.4 | 0.13 |
| 0.33 | 0.08 | \$83 | \$13.3 | 0.05 |
| 0.33 | 0.12 | \$187 | \$29.9 | 0.11 |
| 0.33 | 0.15 | \$292 | \$46.7 | 0.17 |
| 0.50 | 0.08 | \$126 | \$20.1 | 0.07 |
| 0.50 | 0.12 | \$283 | \$45.3 | 0.16 |
| 0.50 | 0.15 | \$442 | \$70.7 | 0.25 |

:::

The central estimate (row with $\varepsilon = 0.33$, $\sigma = 0.12$): the expected deadweight loss from tax misperception is approximately \$187 per worker, or \$29.9 billion in aggregate---0.11% of GDP. This is a cost that arises purely from the complexity of the tax code, independent of any distortionary effect of the tax rate itself.

Several features of the table merit emphasis. First, the quadratic dependence on $\sigma$ is visible: moving from $\sigma = 0.08$ to $\sigma = 0.15$ (roughly doubling the misperception) nearly quadruples the per-worker DWL within each elasticity row. Second, the range across the full grid is wide---from \$10.1 billion to \$70.7 billion---reflecting genuine uncertainty about the structural parameters. However, even the most conservative cell (\$10.1 billion at $\varepsilon = 0.25$, $\sigma = 0.08$) represents an annual welfare cost that exceeds the budget of most federal information-provision programs.

The central estimate of 0.11% of GDP is smaller than {cite:t}`skinner1988welfare`'s estimate of 0.4% from future tax policy uncertainty, which is appropriate since Skinner's model includes both risk aversion and intertemporal channels that are absent here. The current paper's contribution is to show that even the static misperception channel---holding tax policy constant and considering only current-period confusion about marginal rates---generates welfare losses of 0.04--0.25% of GDP.

These calibrated values align with the code implementation in the `Calibration` class, which uses identical parameter values and the same analytical formula to produce the sensitivity grid. All results are reproducible from the accompanying code repository.

## Empirical marginal tax rate distribution

The representative-agent calculations above assume a single mean marginal rate $\bar{\tau} = 0.30$ applied uniformly across workers. To assess the distributional implications of MTR heterogeneity, I compute household-level comprehensive marginal tax rates using PolicyEngine-US {cite:p}`policyengine2024`, a microsimulation model built on the Enhanced Current Population Survey. The simulation covers approximately 149 million working-age adults (18--64) with positive employment income in 2024.

Marginal tax rates are clipped to the interval [0, 0.99] before analysis: benefit phase-outs can produce MTRs above 100% (benefit cliffs), and refundable credits can produce negative MTRs. I clip rather than exclude these observations to avoid selection bias, though the choice has minimal impact on weighted means because extreme MTRs affect a small share of the weighted population.

The weighted mean comprehensive MTR is 0.25, somewhat below the CBO estimate of 0.30 used in the stylized calibration. This difference reflects the large mass of low-income workers who face zero or low federal income tax rates, partially offset by payroll taxes. The weighted standard deviation is 0.16, and the distribution spans from 0.00 at the 10th percentile to 0.45 at the 90th percentile. The median MTR is 0.26, with an interquartile range of [0.20, 0.36].

These empirical rates are *comprehensive*: they include federal income taxes, employee payroll taxes (Social Security and Medicare), state income taxes, and the phase-out of transfer programs (EITC, CTC, SNAP, Medicaid). This comprehensiveness is precisely the source of a critical scope mismatch with the misperception parameter $\sigma$.

### The $\sigma$ scope mismatch

The calibrated $\sigma = 0.12$ is drawn from {cite:t}`rees2020schmeduling`, who measured misperception of *federal income tax rates only*. Their survey instrument asked respondents to estimate federal marginal tax rates; it did not cover payroll taxes, state taxes, or benefit phase-outs. However, the marginal tax rates in both the stylized calibration ($\bar{\tau} = 0.30$) and the microsimulation include all of these components.

This creates an asymmetry: $\tau$ is comprehensive but $\sigma$ captures only one component of the tax system. Workers who face EITC phase-outs, state income surtaxes, or benefit cliffs confront additional sources of complexity beyond the federal income tax schedule. If the misperception of each additional tax component is even partially independent of federal income tax misperception, then the true comprehensive $\sigma$ exceeds 0.12. This means the calibrated $\sigma = 0.12$ is best interpreted as a **lower bound** on the standard deviation of comprehensive MTR misperception.

The magnitude of this understatement depends on how correlated the various misperception components are. If workers who misperceive their federal rate also misperceive payroll and state taxes in the same direction (correlated errors), the comprehensive $\sigma$ may be only modestly larger than 0.12. If the errors are largely independent---which is plausible given the distinct administrative origins of each tax---the comprehensive $\sigma$ could be substantially larger. A rough calculation: if federal income tax misperception contributes $\sigma_{\text{fed}} = 0.12$ and the combined payroll-plus-state-plus-benefit component contributes an independent $\sigma_{\text{other}} = 0.06$, the comprehensive $\sigma = \sqrt{0.12^2 + 0.06^2} \approx 0.13$. With a larger non-federal component ($\sigma_{\text{other}} = 0.10$), the comprehensive $\sigma$ would be approximately 0.16.

Because DWL is quadratic in $\sigma$, even a modest understatement matters: $0.16^2 / 0.12^2 = 1.78$, implying the welfare costs could be 78% larger than the baseline estimate. The empirical microsimulation results in the next chapter provide a complementary perspective by using actual MTR heterogeneity rather than a single representative rate.

```{bibliography}
```
