# The disutility of uncertainty: welfare costs of noisy tax perceptions

**Max Ghenis**

## Abstract

Most taxpayers cannot accurately state their marginal tax rate. This paper quantifies the welfare cost of such misperception using a model in which workers choose labor supply based on a noisy signal of their true marginal rate. I adopt quasilinear-isoelastic preferences, which yield a clean closed-form expression for the expected deadweight loss (DWL) per worker: $\frac{1}{2}\varepsilon\sigma^{2}/(1-\tau)$ times earnings, where $\varepsilon$ is the Frisch elasticity of labor supply, $\sigma$ is the standard deviation of the misperception error (12 percentage points), and $\tau$ is the true marginal rate. Calibrating to a Frisch elasticity of 0.33 {cite:p}`chetty2012bounds`, a misperception standard deviation of 0.12 {cite:p}`rees2020schmeduling`, and a mean marginal rate of 0.30 {cite:p}`cbo2016marginal`, the stylized central estimate is \$187 per worker and \$30 billion in aggregate, or 0.11% of gross domestic product (GDP) annually. Applying the formula to household-level marginal tax rates from PolicyEngine-US microsimulation yields a higher aggregate estimate of \$37 billion, reflecting the convexity of the DWL formula in the joint distribution of earnings and tax rates. The top income quintile bears 59% of total deadweight loss. Sensitivity analysis across plausible parameter ranges places the cost between 0.04% and 0.25% of GDP (\$10--71 billion), and the calibrated $\sigma = 0.12$---measured for federal income taxes only---may understate comprehensive marginal rate misperception. A utilitarian planner who internalizes misperception chooses a lower optimal tax rate (42.9% versus 44.5% under perfect information). Reducing $\sigma$ by 5 percentage points cuts aggregate DWL by approximately two-thirds.

## Keywords

Tax complexity, marginal rate misperception, bounded rationality, labor supply, deadweight loss

## JEL classification

H21, H30, D83, J22

## Replication

Code and data for all results are available at [github.com/maxghenis/disutility-of-uncertainty](https://github.com/maxghenis/disutility-of-uncertainty). All numerical results are generated deterministically from a fixed seed.
