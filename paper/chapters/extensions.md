# Extensions and robustness

The baseline results rely on quasilinear isoelastic preferences and a static, representative-agent calibration. This chapter examines how the findings change under alternative preference specifications, dynamic considerations, richer heterogeneity, and endogenous information acquisition. Together, these extensions bracket the plausible range of welfare costs and clarify where the baseline estimates sit within that range.

## Cobb-Douglas benchmark

A natural starting point is the Cobb-Douglas utility function $U = L^{\alpha} C^{\beta}$, which the earliest version of this project employed. Under Cobb-Douglas preferences with no government transfers, the optimal labor supply is

$$h^* = \frac{\beta T}{\alpha + \beta}$$

where $T$ is the time endowment. This expression contains no tax rate: the income effect of a higher tax (which makes leisure cheaper in opportunity-cost terms) exactly offsets the substitution effect (which makes leisure more attractive). Because the worker supplies the same hours regardless of the perceived tax rate, misperception has no effect on behavior, and the DWL from uncertainty is exactly zero.

This is a knife-edge result. It holds only when (i) preferences are exactly Cobb-Douglas and (ii) the government rebates no revenue. Once the government finances a lump-sum transfer $G$ from tax revenue, the budget constraint becomes $C = w(1-\tau)(T - L) + G$, and the tax rate re-enters the labor supply decision through the transfer channel. Even under Cobb-Douglas preferences, the worker now adjusts hours in response to perceived $\tau$ because the transfer makes the income and substitution effects no longer cancel. The resulting DWL is positive but smaller than under quasilinear preferences, because the substitution-effect channel -- the dominant channel empirically -- is shut down by assumption.

The quasilinear model captures the substitution-effect channel directly: workers unambiguously reduce labor supply when they perceive a higher marginal rate. Empirical evidence from {cite:t}`chetty2009salience` and {cite:t}`feldstein1999tax` overwhelmingly shows that labor supply responds to perceived net-of-tax rates on the substitution margin, confirming that the quasilinear specification is the more empirically relevant of the two.

## CES generalization

Both Cobb-Douglas and quasilinear preferences are special cases of the CES family

$$U(L, C) = \left[\alpha L^{\rho} + (1 - \alpha) C^{\rho}\right]^{1/\rho}$$

with elasticity of substitution $\sigma_u = 1/(1 - \rho)$ (where $\sigma_u$ denotes the elasticity of substitution between leisure and consumption, distinct from the misperception standard deviation $\sigma$). Cobb-Douglas corresponds to $\sigma_u = 1$ (where income and substitution effects cancel), and the quasilinear specification captures the limit in which the substitution effect dominates the income effect on the relevant margin. As $\sigma_u$ rises above one, the substitution effect increasingly outweighs the income effect, and the DWL from misperception grows.

The quasilinear calibration therefore provides an estimate toward the upper end of the CES family for a given Frisch elasticity. Conversely, preferences with $\sigma_u < 1$ would produce smaller welfare costs. The empirical labor supply literature, which consistently finds that compensated elasticities exceed uncompensated elasticities, implies $\sigma_u > 1$ for most workers, suggesting that the quasilinear estimates are, if anything, conservative relative to the data.

## Dynamic considerations

The static framework ignores at least four channels through which tax misperception could affect welfare beyond the intensive-margin adjustment modeled above.

First, savings and investment decisions depend on perceived after-tax returns. A worker who overestimates her marginal rate may also overestimate the tax on capital income, leading to under-saving. This adds a DWL term on the capital margin that is absent from the baseline model.

Second, human capital investment -- decisions about education, training, and occupational choice -- responds to perceived lifetime tax rates. If a prospective medical student overestimates the marginal rate on physician earnings, she may choose a lower-return career, generating a misallocation cost that compounds over decades.

Third, life-cycle labor supply involves timing decisions (when to enter the labor force, when to retire) that depend on perceived tax rates at different ages. Misperception of the Social Security earnings test or Medicare surtax, for example, could distort retirement timing.

Fourth, the model focuses on continuous hours adjustment, whereas most workers face fixed-hours contracts. The extensive margin --- the decision of whether to work at all --- may be more responsive to perceived tax rates than the intensive margin for many workers. A worker who overestimates her marginal rate by 10 percentage points may not reduce her weekly hours (which are contractually fixed) but may delay entry into the labor force, choose part-time over full-time work, or retire earlier. These discrete decisions are governed by participation elasticities, which {cite:t}`chetty2012bounds` estimates at approximately 0.25 on the extensive margin. The calibrated Frisch elasticity of 0.33, which blends intensive and extensive margin responses, implicitly captures some of this channel.

Each of these channels would add to the baseline welfare cost. Their omission means the static estimate of 0.11% of GDP is best interpreted as a lower bound on the total cost of marginal-rate misperception.

## Heterogeneous misperception

The baseline model assumes a uniform $\sigma = 0.12$ for all workers. In practice, misperception almost certainly varies across the income distribution.

Low-income workers face relatively simple statutory schedules, but limited financial literacy and less experience with tax filing may raise their subjective uncertainty. The EITC phase-in and phase-out create steep effective marginal rates that many recipients do not understand, as documented by {cite:t}`chetty2013teaching`.

Middle-income workers confront the densest thicket of interacting provisions: CTC phase-outs, the EITC cliff, the transition between federal brackets, the standard-versus-itemized deduction choice, AMT exposure, and state income taxes that piggyback on federal definitions. For these households, $\sigma$ is plausibly well above 0.12.

High-income workers face complex capital-gains rules, the net investment income tax, and state-specific provisions, but they also disproportionately hire CPAs and financial advisors. Professional tax planning likely compresses $\sigma$ below the population mean for this group.

Incorporating a $\sigma$ that rises and then falls with income would shift the aggregate welfare cost toward middle-income workers and could raise or lower the population total depending on the covariance between $\sigma_i$ and $\tau_i$. Given that middle-income workers face both elevated $\sigma$ and moderate-to-high $\tau$, the net effect would likely increase total DWL relative to the homogeneous-$\sigma$ baseline.

## Endogenous information acquisition

Workers are not passive recipients of tax confusion; they can invest in learning their marginal rate by hiring accountants, purchasing tax software, or spending time reading IRS publications. The observed $\sigma$ is therefore an equilibrium outcome in which each worker balances the cost of information against the utility gain from more accurate optimization.

The DWL formula implies that the private benefit of reducing one's own $\sigma$ by a small amount $d\sigma$ is approximately $\varepsilon \cdot \sigma \cdot \text{earnings} \cdot d\sigma / (1 - \tau)$. Workers with higher earnings, higher $\tau$, or higher $\varepsilon$ gain more from information and should invest more in acquiring it. This is consistent with the observation that high-income households are far more likely to hire professional tax preparers.

The U.S. tax preparation industry generates roughly \$35 billion in annual revenue, representing the private sector's partial response to the misperception problem. This expenditure is itself a deadweight cost: in a world with transparent marginal rates, most of it would be unnecessary. The existence and scale of the industry is thus independent evidence that marginal-rate misperception is economically costly. Public simplification efforts that reduce $\sigma$ for all workers simultaneously capture scale economies that private information acquisition cannot, and they reduce both the behavioral DWL and the preparation expenditure.

## Comparison to prior estimates

{cite:t}`skinner1988welfare` estimated the welfare cost of tax *policy* uncertainty -- uncertainty about future legislative changes -- at 0.4% of national income per year. That concept is distinct from the misperception studied here: Skinner's agents know the current tax schedule perfectly but face uncertainty about what it will be next year. The two sources of uncertainty are additive in welfare terms. The estimate of 0.04--0.25% of GDP from misperception alone implies a combined cost of tax-related uncertainty on the order of 0.4--0.7% of GDP.

{cite:t}`chetty2009salience` find that salience manipulations shift consumer behavior by amounts equivalent to 1--4% of the tax revenue at stake. Translating their experimental magnitudes into a population-wide DWL is not straightforward, but the orders of magnitude are compatible: if misperception shifts effective labor supply responses by a few percent of the tax wedge, the resulting DWL as a share of GDP falls squarely in the estimated range.

Taken together, the extensions and comparisons reinforce the central finding. The baseline estimate of 0.11% of GDP is robust to reasonable perturbations and, if anything, understates the full welfare cost once dynamic channels and heterogeneous misperception are accounted for.

```{bibliography}
```
