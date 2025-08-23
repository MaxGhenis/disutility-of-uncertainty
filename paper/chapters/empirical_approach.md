# Empirical Approach

This chapter describes the empirical methodology used to quantify the welfare costs of tax rate uncertainty using real-world data from the United States tax system.

## Data Sources

The empirical analysis relies on two primary data sources. First, PolicyEngine-US provides comprehensive tax calculations for U.S. households, incorporating federal and state tax codes, various credits and deductions, and the interaction between taxes and transfer programs. This microsimulation model allows us to compute actual marginal tax rates for a representative sample of households, capturing the full complexity of the tax system that contributes to uncertainty.

Second, when PolicyEngine data is unavailable or for robustness checks, we use distributional parameters from the Current Population Survey (CPS) and Internal Revenue Service Statistics of Income (SOI) to calibrate wage and income distributions. These sources provide nationally representative data on labor market outcomes and tax filing patterns.

## Measuring Tax Rate Uncertainty

Tax rate uncertainty in our framework arises from two distinct sources that affect households differently. Policy uncertainty stems from potential changes in tax legislation, which create doubt about future tax rates even when current rates are known. Complexity-induced uncertainty arises when households cannot accurately determine their current marginal tax rate due to the intricate interaction of various tax provisions.

To quantify policy uncertainty, we examine historical variation in effective tax rates over the past two decades. Using Congressional Budget Office data on average federal tax rates by income quintile from 2000-2020, we calculate the standard deviation of tax rates within each income group. This historical variation provides a lower bound on policy uncertainty, as it excludes proposed but unenacted changes that nonetheless affect expectations.

Complexity-induced uncertainty is measured by comparing households' self-reported expected tax rates from survey data with their actual computed marginal rates. The discrepancy between perceived and actual rates reveals the extent to which tax complexity prevents optimal decision-making. Studies suggest that most households misestimate their marginal tax rate by 5-10 percentage points, with larger errors for those facing more complex tax situations.

## Calibration Strategy

The model calibration proceeds in several steps to ensure realistic parameter values. For utility function parameters, we set the Cobb-Douglas exponents for leisure and consumption equal (α = β = 0.5), consistent with balanced growth preferences and empirical estimates of labor supply elasticities. This parameterization implies a Frisch elasticity of labor supply of unity, within the range of empirical estimates.

The wage distribution is calibrated to match moments from the CPS. We use a lognormal distribution with parameters chosen to reproduce the observed mean hourly wage of $28, median of $20, and 90/10 ratio of 5.2. The resulting distribution captures the right-skewed nature of wages while maintaining computational tractability.

For the tax rate distribution, we compute marginal tax rates for each household in our sample using PolicyEngine-US. This calculation accounts for federal income taxes, payroll taxes, state income taxes where applicable, and the phase-in and phase-out of various credits and deductions. The resulting distribution shows substantial heterogeneity, with marginal rates ranging from negative values (due to refundable credits) to over 50% for high-income households in high-tax states.

## Welfare Calculation Methodology

The welfare analysis compares outcomes under certainty versus uncertainty to isolate the deadweight loss from imperfect information. Under certainty, each agent chooses optimal labor supply given their known tax rate, achieving utility U*(w,τ). Under uncertainty, agents must choose labor supply based on the expected tax rate E[τ], but utility is realized based on the actual tax rate, yielding expected utility E[U(w,τ̃)].

The deadweight loss from uncertainty equals the difference between these utility levels, aggregated across the population. We express this loss both in utility units and as a percentage of certain utility to facilitate interpretation. To convert utility losses to dollar equivalents, we use the marginal utility of consumption at the optimal allocation, providing a money-metric measure of welfare loss.

For the aggregate analysis, we weight household-level welfare losses by population weights from the CPS to obtain nationally representative estimates. This weighting ensures that our results reflect the actual distribution of households across income levels and tax situations.

## Addressing Endogeneity Concerns

A potential concern is that tax uncertainty may be endogenous to economic conditions or household characteristics. Households with more volatile incomes may face greater tax uncertainty mechanically, and economic downturns might increase both income volatility and policy uncertainty simultaneously.

We address these concerns through several strategies. First, we focus on uncertainty about tax rates conditional on income, rather than uncertainty about tax liability that stems from income volatility. Second, we use predetermined household characteristics (education, age, occupation) as instruments for exposure to tax complexity. Third, we exploit quasi-experimental variation from tax reforms that affected some households more than others due to arbitrary thresholds or phase-in schedules.

## Robustness Checks

The empirical results are subjected to extensive robustness checks to ensure reliability. We vary the assumed level of tax rate uncertainty from ±5% to ±15% of the mean rate, finding that welfare losses scale approximately quadratically with uncertainty. Alternative utility specifications, including CES preferences with different elasticities of substitution, yield qualitatively similar results, though the magnitude of welfare losses varies.

We also examine sensitivity to the labor supply elasticity, recognizing that this parameter is contentious in the literature. Using elasticities ranging from 0.5 to 1.5, we find that welfare losses remain economically significant across the plausible range, though higher elasticities imply larger losses as agents' inability to optimize becomes more costly.

The distribution of tax uncertainty across income levels proves robust to alternative data sources and measurement approaches. Whether using self-reported tax rates, variation in effective rates over time, or complexity measures based on tax form length and number of schedules, we consistently find that middle-income households face the greatest uncertainty.

## Limitations and Caveats

Several limitations of the empirical approach warrant discussion. First, the static model abstracts from dynamic considerations such as savings and human capital investment, which may also be affected by tax uncertainty. These omissions likely lead us to underestimate total welfare costs.

Second, we assume that agents have rational expectations about tax rate distributions, when behavioral evidence suggests systematic biases in tax perception. If agents overestimate their marginal tax rates on average, as some studies suggest, the welfare losses from uncertainty may be partially offset by reduced labor supply distortions.

Third, the analysis focuses on intensive margin labor supply responses, abstracting from extensive margin decisions about labor force participation. For some groups, particularly secondary earners and those near retirement, extensive margin responses may be more important.

Despite these limitations, the empirical approach provides conservative estimates of the welfare costs of tax uncertainty. The finding that these costs are economically significant even under conservative assumptions strengthens the case for policy interventions to reduce uncertainty through simplification and improved information provision.