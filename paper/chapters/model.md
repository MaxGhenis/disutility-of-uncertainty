# Theoretical framework

This section develops a model of labor supply under tax misperception. A worker who misperceives her marginal tax rate chooses a suboptimal quantity of labor, generating a welfare loss that depends on the elasticity of labor supply, the variance of the misperception, and the level of the tax rate itself. The central result is a closed-form expression for the expected deadweight loss as a fraction of earnings.

## Setup

Consider a population of workers indexed by $i$. Worker $i$ earns hourly wage $w_i$ and faces a linear marginal tax rate $\tau_i$. Due to the complexity of the tax code---overlapping brackets, phase-ins, phase-outs, credits, and the interaction of federal, state, and payroll taxes---the worker does not observe $\tau_i$ directly. Instead, she perceives a noisy signal

$$
\hat{\tau}_i = \tau_i + \delta_i, \qquad \delta_i \sim N(0, \sigma^2),
$$

where $\sigma$ measures the severity of misperception---the misperception error has a standard deviation of $\sigma$ (e.g., 12 percentage points when $\sigma = 0.12$). The noise $\delta_i$ captures the gap between the worker's mental model of her tax rate and the actual statutory-plus-effective rate she faces. This formulation nests perfect information as the special case $\sigma = 0$.

The normality assumption is a modeling convenience that delivers tractable closed-form results. The DWL formula depends only on $E[\delta^2] = \sigma^2$, so it holds for any symmetric distribution with variance $\sigma^2$, not just the Gaussian. Departures from normality (e.g., heavier tails or discreteness in actual misperception) would affect higher-order corrections to the Taylor approximation but not the leading term. The Monte Carlo validation in the approximation accuracy subsection confirms that the second-order formula is robust to the clipping of extreme draws at the [0, 1] boundary.

The mean-zero assumption ($E[\delta_i] = 0$) is a simplification. {cite:t}`rees2020schmeduling` document that misperception is partly systematic: "ironing" taxpayers tend to perceive their marginal rate as closer to their average rate, which in a progressive system means $E[\delta_i] < 0$ (underestimation). Decomposing misperception into bias $\mu_\delta = E[\delta_i]$ and noise $\sigma^2 = \text{Var}(\delta_i)$, the DWL formula generalizes to include a bias term: $E[\text{DWL}] \approx \frac{1}{2}\varepsilon w h^* (\mu_\delta^2 + \sigma^2)/(1-\tau)$. The mean-zero case studied here therefore provides a lower bound on the welfare cost, since any systematic bias adds to the total. The calibrated $\sigma = 0.12$ already incorporates both systematic and idiosyncratic components of the cross-sectional dispersion in perceived rates, so it partially captures the bias channel. Specifically, the calibrated $\sigma = 0.12$ is best interpreted as the root-mean-square error (RMSE) of the misperception distribution, since it is derived from the cross-sectional dispersion of (perceived - actual) rates which includes any systematic component. Under this interpretation, $\sigma^2 = \mu_\delta^2 + \text{Var}(\delta_i)$, and the mean-zero DWL formula $\frac{1}{2}\varepsilon w h^* \sigma^2 / (1-\tau)$ remains correct with $\sigma$ interpreted as the RMSE rather than the standard deviation of mean-zero noise.

Preferences are quasilinear in consumption with isoelastic labor disutility:

$$
U(C, h) = C - \psi \frac{h^{1 + 1/\varepsilon}}{1 + 1/\varepsilon},
$$

where $C$ is consumption, $h$ is hours of labor, $\varepsilon > 0$ is the Frisch elasticity of labor supply, and $\psi > 0$ is a scale parameter governing the disutility of work. Quasilinear preferences eliminate income effects on labor supply, so the Frisch elasticity coincides with the uncompensated and compensated elasticities. This tractability is not merely convenient; it isolates the substitution-effect channel through which tax misperception distorts behavior, as discussed below.

The worker's budget constraint is

$$
C = w(1 - \tau) h + v,
$$

where $v$ is a lump-sum transfer (or non-labor income). Because utility is linear in $C$, the transfer $v$ does not affect the labor supply decision---it shifts consumption one-for-one but leaves the first-order condition for hours unchanged. This separation is essential: it means that misperception of $\tau$ affects only the hours margin, not the marginal utility of income.

## Optimal labor supply

A worker who correctly perceives her tax rate $\tau$ maximizes $U$ by setting the marginal benefit of an hour of work equal to its marginal cost:

$$
w(1 - \tau) = \psi \, h^{1/\varepsilon}.
$$

Solving for optimal hours:

$$
h^*(\tau) = \left( \frac{w(1 - \tau)}{\psi} \right)^\varepsilon.
$$

Hours are decreasing in the tax rate and increasing in the wage, with the Frisch elasticity $\varepsilon$ governing the responsiveness of labor supply to the net-of-tax wage.

## Misperceived labor supply

A worker who perceives the tax rate to be $\hat{\tau} = \tau + \delta$ solves the same first-order condition but evaluated at $\hat{\tau}$:

$$
h(\hat{\tau}) = \left( \frac{w(1 - \hat{\tau})}{\psi} \right)^\varepsilon = \left( \frac{w(1 - \tau - \delta)}{\psi} \right)^\varepsilon.
$$

When $\delta > 0$ the worker overestimates her tax rate and undersupplies labor; when $\delta < 0$ she underestimates the rate and oversupplies labor. In both cases, utility evaluated at the true tax rate $\tau$ is lower than it would be at the optimum $h^*(\tau)$.

## Individual deadweight loss

Define the individual deadweight loss from a misperception of magnitude $\delta$ as the utility gap between optimal and misperceived behavior, with consumption evaluated at the true tax rate in both cases:

$$
\text{DWL}(\delta) = U\bigl(h^*(\tau)\bigr) - U\bigl(h(\tau + \delta)\bigr).
$$

Here $U(h)$ is shorthand for indirect utility at hours $h$ given the true budget constraint: $U(h) = w(1-\tau)h + v - \psi h^{1+1/\varepsilon}/(1+1/\varepsilon)$. Since $h^*(\tau)$ maximizes this expression, $\text{DWL}(\delta) \geq 0$ for all $\delta$, with equality only at $\delta = 0$.

## Second-order approximation

To obtain a closed-form expression for expected DWL, expand $U(h)$ around the optimum $h^*$. Write $\Delta h = h(\hat{\tau}) - h^*(\tau)$ for the hours distortion.

The first derivative of indirect utility with respect to hours is

$$
U_h = w(1 - \tau) - \psi \, h^{1/\varepsilon},
$$

which equals zero at $h = h^*$ by the first-order condition. The second derivative is

$$
U_{hh} = -\frac{\psi}{\varepsilon} h^{* \, (1/\varepsilon - 1)} = -\frac{w(1-\tau)}{\varepsilon \, h^*},
$$

where the second equality substitutes $\psi = w(1-\tau) / h^{*\,1/\varepsilon}$ from the first-order condition. Since $U_h = 0$ at the optimum, the Taylor expansion gives

$$
\text{DWL}(\delta) \approx \frac{1}{2} |U_{hh}| (\Delta h)^2.
$$

Next, compute $\Delta h$. Since $h(\hat{\tau}) = (w(1 - \tau - \delta)/\psi)^\varepsilon$, a first-order expansion around $\delta = 0$ yields

$$
\Delta h \approx -\varepsilon \, h^* \frac{\delta}{1 - \tau}.
$$

Substituting both expressions:

$$
\text{DWL}(\delta) \approx \frac{1}{2} \cdot \frac{w(1-\tau)}{\varepsilon \, h^*} \cdot \varepsilon^2 h^{*2} \frac{\delta^2}{(1-\tau)^2} = \frac{1}{2} \varepsilon \, w \, h^* \frac{\delta^2}{1-\tau}.
$$

The deadweight loss is quadratic in the misperception $\delta$: small errors are relatively harmless, but large errors are disproportionately costly. This convexity is central to the welfare analysis.

## Expected deadweight loss

Taking expectations over $\delta \sim N(0, \sigma^2)$ and using $E[\delta^2] = \sigma^2$:

$$
E[\text{DWL}] = \frac{1}{2} \varepsilon \cdot w \cdot h^* \cdot \frac{\sigma^2}{1-\tau}.
$$

Since $w \cdot h^*$ equals earnings, this can be expressed as a fraction of earnings:

$$
\boxed{\frac{E[\text{DWL}]}{\text{earnings}} \approx \frac{1}{2} \varepsilon \cdot \frac{\sigma^2}{1-\tau}.}
$$

This is the paper's core formula. It gives the welfare cost of tax misperception as a share of labor income, depending on three key parameters: the Frisch elasticity, the variance of misperception, and the tax rate.

### Approximation accuracy

Because the formula is a second-order Taylor expansion of utility around the optimum, it is exact only for infinitesimal $\delta$ and may diverge for large misperceptions. To assess its accuracy over the parameter ranges used in this paper, I compare the analytical approximation to a Monte Carlo estimate (500,000 draws of $\delta \sim N(0, \sigma^2)$, evaluating exact utility at each draw). At the baseline calibration ($\varepsilon = 0.33$, $\sigma = 0.12$, $\tau = 0.30$), the analytical formula understates the Monte Carlo estimate by 1.1%. At the most extreme corner of the sensitivity grid ($\varepsilon = 0.50$, $\sigma = 0.15$, $\tau = 0.43$), where $\sigma/(1-\tau) = 0.26$, the approximation understates the true expected DWL by 4.7%. The closed-form expression is therefore reliable across the entire parameter space considered here.

## Discussion of the formula

The formula reveals several comparative statics.

*Quadratic in $\sigma$.* Doubling the standard deviation of misperception quadruples the expected welfare cost. This convexity implies large returns to reducing the worst misperceptions---moving from $\sigma = 0.15$ to $\sigma = 0.10$ reduces costs by more than moving from $\sigma = 0.10$ to $\sigma = 0.05$. For policy, this means that interventions targeting the most confused taxpayers (those facing complex phase-out interactions) yield the highest welfare gains per dollar spent.

*Linear in $\varepsilon$.* More elastic labor supply amplifies the cost of misperception because workers with elastic supply distort their hours more in response to a given perceived price change. If labor supply were perfectly inelastic ($\varepsilon = 0$), misperception would have no welfare cost at all---workers would supply the same hours regardless of their beliefs about tax rates. The empirical magnitude of $\varepsilon$ is therefore a key input to the calibration.

A note on elasticity concepts is warranted. The Frisch elasticity $\varepsilon$ in the formula governs the responsiveness of hours to the net-of-tax wage, holding the marginal utility of wealth constant. Under quasilinear preferences, the Frisch, compensated (Hicksian), and uncompensated (Marshallian) elasticities all coincide because there is no income effect. The elasticity of taxable income (ETI) is a broader concept that captures responses on all margins---hours, effort, avoidance, and evasion---and is therefore typically larger than the hours elasticity. The baseline calibration uses $\varepsilon = 0.33$, which corresponds to the hours-only Frisch elasticity from {cite:t}`chetty2012bounds`. If misperception also distorts avoidance and reporting decisions, the relevant elasticity would be closer to the ETI (approximately 0.25--0.50 per {cite:t}`saez2012elasticity`), and the welfare costs could be correspondingly larger or smaller depending on the specific margin. The present analysis isolates the labor supply channel for transparency.

*Denominator $(1 - \tau)$.* Higher tax rates amplify the welfare cost of misperception. This occurs because the same absolute misperception $\delta$ represents a larger proportional change in the net-of-tax wage when $\tau$ is high. A 10-percentage-point misperception shifts the net-of-tax rate from 70% to 60% (a 14% change) when $\tau = 0.30$, but from 40% to 30% (a 25% change) when $\tau = 0.60$.

*Connection to Harberger triangles.* The formula is a direct application of the Harberger approximation to the deadweight loss of taxation, except that the distortionary "wedge" is not the tax itself but the misperception $\delta$. Just as the traditional DWL of a tax $\tau$ is approximately $\frac{1}{2}\varepsilon \tau^2 / (1-\tau)$ times earnings, the DWL of misperception replaces $\tau^2$ with $\sigma^2$. The analogy makes precise the sense in which tax complexity acts like an additional implicit tax on the economy.

## Social planner extension

Consider a utilitarian social planner who chooses a linear tax rate $\tau$ and finances a uniform lump-sum transfer (demogrant) $v$ from the resulting revenue. The government budget constraint requires

$$
v = \frac{\tau}{N} \sum_{i=1}^{N} w_i \, h_i.
$$

The social welfare function uses inverse-wage weights $\omega_i = \bar{w}/w_i$ to create a redistribution motive, so $W = (1/N) \sum_i \omega_i U_i$. Workers with below-average wages receive higher weight, reflecting the standard utilitarian motive for progressive taxation. Under perfect information, these weights generate an interior optimal tax rate that balances redistribution gains against efficiency losses.

The disutility scale $\psi$ is normalized to one. Since rescaling $\psi$ by any constant $\lambda$ multiplies all hours, all revenues, and all utility levels by the same factor $(1/\lambda)^\varepsilon$, the optimal tax rate $\tau^*$ is invariant to the choice of $\psi$. The calibrated optimal tax therefore depends only on the wage distribution and the elasticity, not on the normalization of hours.

Under perfect information ($\sigma = 0$), each worker chooses $h_i = h^*(\tau_i)$ and the planner selects $\tau$ to balance the equity gains from redistribution against the efficiency losses from labor supply distortion.

When workers misperceive the tax rate ($\sigma > 0$), the planner faces an additional cost. Workers choose $h(\hat{\tau}_i)$ instead of $h^*(\tau_i)$, reducing both private welfare and government revenue (since misallocated labor reduces the tax base). The expected per-worker welfare loss from misperception, $\frac{1}{2}\varepsilon w h^* \sigma^2 / (1-\tau)$, is increasing in $\tau$ through the $(1-\tau)$ denominator. This means that at the margin, raising the tax rate imposes a larger misperception cost when rates are already high.

The optimal tax rate $\tau^*$ is therefore decreasing in $\sigma$. As misperception worsens, the planner optimally reduces the tax rate, accepting less redistribution in exchange for lower misperception-induced deadweight loss. In the extreme of perfect information ($\sigma = 0$), the planner chooses the standard optimal tax; as $\sigma$ grows large, the optimal rate converges toward zero because the misperception cost eventually dominates the redistribution benefit.

The model predicts that a reduction in $\sigma$ permits higher $\tau$ at constant total DWL, implying that simplification and progressivity are complements rather than substitutes.

## Why quasilinear preferences, not Cobb-Douglas?

A natural alternative specification is Cobb-Douglas utility over leisure $L$ and consumption $C$:

$$
U(L, C) = L^\alpha C^\beta,
$$

with time constraint $L + h = T$. Under this specification, optimal leisure is $L^* = \alpha T / (\alpha + \beta)$ when the worker receives no transfers, and this expression is independent of the net-of-tax wage $w(1-\tau)$. The income and substitution effects of a wage change exactly cancel, producing a knife-edge result: hours are invariant to the perceived tax rate, so misperception has zero welfare cost.

This invariance is a well-known property of Cobb-Douglas preferences {cite:p}`block1980labor`, and while it provides a useful theoretical benchmark, it is empirically implausible as a description of labor supply responses to taxation. A large body of evidence reviewed by {cite:t}`chetty2012bounds` documents positive compensated labor supply elasticities, meaning that the substitution effect dominates the income effect on the relevant margins. The quasilinear specification isolates this substitution effect by eliminating the income effect entirely, making it the natural workhorse for analyzing how tax misperception distorts labor supply.

More precisely, the welfare cost of misperception operates through the substitution effect: a worker who overestimates her tax rate reduces labor supply because she perceives a lower return to work, not because she feels wealthier. By shutting down income effects, the quasilinear model isolates this channel cleanly. Any utility specification with positive compensated elasticity would generate qualitatively similar results; the quasilinear form simply yields the most transparent closed-form expressions.

A further limitation of the model is its focus on the intensive margin of labor supply. Most workers cannot continuously adjust their hours; the majority of employees work fixed schedules set by employers {cite:p}`keane2012reassessment`. However, the intensive-margin framework can be reinterpreted as capturing responses at the extensive margin (employment entry and exit) or along the effort margin, both of which are governed by similar elasticities. Moreover, the minority of workers with flexible hours---the self-employed, gig workers, and those choosing between part-time and full-time positions---may have substantially higher effective elasticities than the population average, partially offsetting the lower responsiveness of fixed-hours workers. The calibrated $\varepsilon = 0.33$ represents a blend of intensive and extensive margin responses, as discussed by {cite:t}`chetty2012bounds`.

## Misperception versus inattention

The model assumes that workers actively optimize against a perceived tax rate $\hat{\tau}$, which may differ from the true rate. An alternative behavioral model posits that workers are *inattentive* to the tax rate---they assign zero or near-zero weight to the marginal rate in their labor supply decisions and instead follow heuristics or social norms (e.g., working 40 hours because the employer expects it). Under the inattention model, the welfare cost depends on the degree of under-reaction to tax incentives (the "attention parameter" $\theta$ in the framework of {cite:t}`chetty2009salience`), not on the variance of perceived rates.

The distinction matters empirically. Survey evidence on perceived rates {cite:p}`rees2020schmeduling`, {cite:p}`gideon2017perception` reveals that taxpayers do form beliefs about their marginal rates---they are not ignoring the rate but rather estimating it with error. The behavioral responses documented by {cite:t}`chetty2013teaching`, in which EITC recipients adjusted their earnings after receiving information about marginal incentives, suggest that workers do optimize against perceived rates rather than ignoring them entirely. The misperception framework adopted here is therefore the more appropriate model for the population segments that form and act on tax rate beliefs, while the inattention framework may apply to workers who delegate all tax decisions to accountants or employers. The two models are complements rather than substitutes, and a complete welfare accounting would include both channels.

```{bibliography}
```
