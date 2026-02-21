# Results

This chapter presents the main quantitative findings on the welfare costs of tax rate misperception, drawing on the analytical framework developed earlier and calibrated to U.S. data. All results derive from the closed-form approximation for deadweight loss (DWL) under quasilinear isoelastic preferences:

$$\frac{\text{E}[\text{DWL}]}{\text{earnings}} \approx \frac{1}{2} \frac{\varepsilon \sigma^2}{1 - \bar{\tau}}$$

where $\varepsilon$ is the Frisch elasticity of labor supply, $\sigma$ is the standard deviation of tax rate misperception, and $\bar{\tau}$ is the mean marginal tax rate. The formula captures the welfare cost of workers choosing suboptimal hours because they do not know their true marginal rate.

## Baseline welfare cost

Under the central calibration ($\varepsilon = 0.33$, $\sigma = 0.12$, $\bar{\tau} = 0.30$), the expected deadweight loss is \$187 per worker per year, or \$29.9 billion nationally across 160 million workers. This amounts to 0.11% of GDP.

It is worth emphasizing what this quantity represents and what it does not. The \$187 figure is the expected utility loss, expressed in dollar terms, from a worker who optimizes labor supply against a perceived marginal rate that differs from the true rate by a random draw with standard deviation 0.12. When the perceived rate is too high, the worker supplies too little labor; when it is too low, too much. In both cases the worker ends up on a lower indifference curve than under perfect information. This is a pure behavioral distortion cost -- distinct from compliance costs, which represent resources spent on filing and record-keeping rather than misallocated time.

For context, {cite:t}`kopczuk2013taxation` reviews estimates suggesting the deadweight loss of the federal estate tax is on the order of \$20--30 billion per year. The welfare cost of marginal-rate misperception is comparable in magnitude. Unlike the estate tax, which affects fewer than 0.1% of decedents, misperception-induced DWL falls on the entire working population.

## Sensitivity analysis

The baseline estimate rests on point values for $\varepsilon$ and $\sigma$ that are themselves uncertain. The full sensitivity grid (Table {ref}`tab-sensitivity`) spans per-worker DWL from \$63 to \$442, or 0.04% to 0.25% of GDP. DWL is far more sensitive to $\sigma$ than to $\varepsilon$: moving across a row (doubling $\sigma$ from 0.08 to 0.15) roughly quadruples the cost, whereas moving down a column (doubling $\varepsilon$ from 0.25 to 0.50) only doubles it. This follows directly from the formula, in which $\sigma$ enters quadratically and $\varepsilon$ enters linearly. Even the most conservative cell---low elasticity and low misperception---implies a \$10 billion annual cost.

## Distributional pattern

The per-worker DWL formula can be written as a fraction of that worker's earnings:

$$\frac{\text{DWL}_i}{\text{earnings}_i} = \frac{1}{2} \frac{\varepsilon \, \sigma_i^2}{1 - \tau_i}$$

Two forces shape the distributional pattern. The denominator $(1 - \tau_i)$ means that workers facing higher marginal rates lose a larger share of their earnings to misperception, all else equal. High-income workers face the steepest statutory rates, but they also tend to have lower $\sigma_i$ because they hire tax professionals and face fewer interacting provisions once above the main phase-out ranges.

Middle-income workers are likely the hardest hit. They navigate the densest region of the tax code: earned income tax credit (EITC) and Child Tax Credit (CTC) phase-outs, the transition from the 12% to the 22% federal bracket, alternative minimum tax (AMT) exposure, and overlapping state income taxes. These interacting provisions make it difficult to infer one's true marginal rate, implying a larger $\sigma_i$ than for workers at either tail of the income distribution. Combined with moderate-to-high marginal rates (often 30--40% when payroll and state taxes are included), the DWL-to-earnings ratio peaks in the middle of the distribution. This pattern inverts the common assumption that tax complexity primarily burdens the wealthy.

## Optimal tax rate under misperception

A utilitarian planner choosing a linear tax rate to maximize social welfare faces a modified tradeoff when workers misperceive their marginal rate. Higher tax rates finance larger transfers and reduce inequality, but they also amplify the welfare cost of misperception because the DWL formula has $(1 - \tau)$ in the denominator: as $\tau$ rises, each unit of misperception becomes more costly.

Under the baseline calibration, the optimal tax rate in the absence of misperception is 44.5%. When the planner accounts for $\sigma = 0.12$ misperception, the optimum falls to 42.9%, a decline of 1.6 percentage points. The planner accepts somewhat less redistribution because the marginal cost of public funds is higher when workers cannot perceive their tax rate accurately.

A 1.6 percentage-point adjustment corresponds to approximately \$141 billion in annual revenue foregone -- revenue the planner judges is not worth collecting given the amplified behavioral distortions it would cause.

## Value of information

Because DWL is quadratic in $\sigma$, even partial reductions in misperception yield large welfare gains. Reducing $\sigma$ from 0.12 to 0.08 -- plausibly achievable through tax simplification, better withholding tables, or enhanced taxpayer communication -- lowers total DWL from \$29.9 billion to \$13.3 billion, a saving of approximately \$17 billion per year.

To appreciate this magnitude, a \$17 billion welfare gain exceeds the annual budget of most federal information-provision programs and is achieved without any reduction in tax revenue: simplification merely helps workers perceive the rate they already face. The U.S. tax preparation industry generates roughly \$35 billion in annual revenue {cite:p}`irs2023databook`, suggesting that households already spend considerable resources trying to reduce their own $\sigma$. Public investments in simplification that lower $\sigma$ for all workers simultaneously would capture economies of scale unavailable to individual tax filers.

## Microsimulation results

The stylized calculations above use a single representative marginal tax rate ($\bar{\tau} = 0.30$) and a lognormal wage distribution. To assess the distributional incidence of misperception-induced DWL across the actual income distribution, I apply the per-worker DWL formula to household-level data from PolicyEngine-US {cite:p}`policyengine2024`, a microsimulation model that computes comprehensive marginal tax rates for approximately 149 million working-age adults with positive employment income.

### MTR distribution

The weighted mean comprehensive MTR is 0.25, with a standard deviation of 0.16. The distribution is right-skewed: the median (0.26) is close to the mean, but the 90th percentile (0.45) is far above it, reflecting the steep statutory rates faced by high earners. At the bottom, 10% of workers face an MTR at or near zero, typically because they earn below the payroll tax threshold or receive offsetting credits.

### DWL by income quintile

Applying the per-worker DWL formula $\frac{1}{2}\varepsilon \cdot \text{earnings}_i \cdot \sigma^2 / (1 - \tau_i)$ with $\varepsilon = 0.33$ and $\sigma = 0.12$ to each worker in the microsimulation yields the distributional breakdown in {numref}`tab-quintile-dwl`.

:::{table} Deadweight loss from tax misperception by income quintile
:label: tab-quintile-dwl
:align: center

| Quintile | Mean earnings | Mean MTR | Per-worker DWL | Share of total |
|:---:|---:|:---:|---:|---:|
| 1 (lowest) | \$7,355 | 0.11 | \$20 | 1.8% |
| 2 | \$23,550 | 0.23 | \$73 | 6.8% |
| 3 | \$40,742 | 0.27 | \$132 | 12.3% |
| 4 | \$64,301 | 0.31 | \$220 | 20.1% |
| 5 (highest) | \$171,542 | 0.34 | \$614 | 58.9% |

:::

Three findings stand out. First, the top quintile bears 59% of total DWL despite constituting only 20% of workers. This reflects the multiplicative interaction of higher earnings and higher marginal rates in the DWL formula: workers earning \$172k at a 34% MTR lose \$614/year to misperception, compared to \$20/year for workers earning \$7k at an 11% MTR.

Second, as a *fraction of earnings*, the distributional pattern is more uniform. The DWL-to-earnings ratio is $\frac{1}{2}\varepsilon\sigma^2/(1-\tau_i)$, which depends only on $\varepsilon$, $\sigma$, and the individual's MTR. Workers in the top quintile lose 0.36% of earnings, versus 0.27% for bottom-quintile workers---a narrower gap than the absolute dollar figures suggest. The $(1-\tau)$ denominator drives this mild progressivity: higher-MTR workers face a larger amplification of the same misperception variance.

Third, the aggregate DWL from the microsimulation (\$36.6 billion) exceeds the stylized estimate (\$27.8 billion) by 32%. This divergence arises because the DWL formula is convex in both earnings and $1/(1-\tau)$: the actual distribution of incomes and tax rates has heavier tails than the representative-agent approximation, and Jensen's inequality ensures that the population-level DWL exceeds the DWL evaluated at population means. The stylized calculation understates aggregate costs by compressing the joint distribution of earnings and MTRs into a single representative point.

In sum, the welfare costs of tax rate misperception range from 0.04% to 0.25% of GDP under every calibration considered, and the microsimulation analysis suggests aggregate costs of \$37 billion---32% above the stylized baseline. The costs are concentrated in absolute terms among higher earners but are moderately progressive as a share of earnings. These results imply large welfare gains from policies that make marginal rates more transparent, and they reduce the optimal tax rate by 1.6 percentage points.

```{bibliography}
```
