# Technical appendix

## Derivation of optimal labor supply

Consider a worker with quasilinear isoelastic preferences:

$$U(C, h) = C - \frac{\psi \, h^{1+1/\varepsilon}}{1+1/\varepsilon}$$

subject to the budget constraint $C = w(1-\tau)h + v$, where $w$ is the wage, $\tau$ is the marginal tax rate, $h$ is hours worked, and $v$ is a lump-sum transfer.

Substituting the budget constraint:

$$U = w(1-\tau)h + v - \frac{\psi \, h^{1+1/\varepsilon}}{1+1/\varepsilon}$$

The first-order condition with respect to $h$:

$$U_h = w(1-\tau) - \psi \, h^{1/\varepsilon} = 0$$

Solving for $h$:

$$h^*(\tau) = \left(\frac{w(1-\tau)}{\psi}\right)^\varepsilon$$

This confirms that labor supply is increasing in the net-of-tax wage $w(1-\tau)$ with constant elasticity $\varepsilon$.

## Proof of the DWL formula

### Setup

A worker perceives $\hat{\tau} = \tau + \delta$ where $\delta$ is the misperception error. The worker chooses labor to maximize utility under the perceived rate:

$$h(\hat{\tau}) = \left(\frac{w(1-\hat{\tau})}{\psi}\right)^\varepsilon$$

But utility is realized at the true rate $\tau$:

$$U(\tau, h(\hat{\tau})) = w(1-\tau)h(\hat{\tau}) + v - \frac{\psi \, h(\hat{\tau})^{1+1/\varepsilon}}{1+1/\varepsilon}$$

### Second-order Taylor expansion

Define $\text{DWL}(\delta) = U(\tau, h^*(\tau)) - U(\tau, h(\hat{\tau}))$. Since $h^*$ maximizes $U(\tau, \cdot)$, the first-order term vanishes by the envelope theorem, and:

$$\text{DWL}(\delta) \approx -\frac{1}{2} U_{hh}\big|_{h=h^*} \cdot (\Delta h)^2$$

*Computing $U_{hh}$:*

$$U_{hh} = -\frac{\psi}{\varepsilon} h^{1/\varepsilon - 1}$$

At the optimum, $\psi (h^*)^{1/\varepsilon} = w(1-\tau)$, so $\psi = w(1-\tau) \cdot (h^*)^{-1/\varepsilon}$. Substituting:

$$U_{hh}\big|_{h^*} = -\frac{w(1-\tau)}{\varepsilon \, h^*}$$

*Computing $\Delta h$:*

$$\Delta h = h(\hat{\tau}) - h^*(\tau) = \left(\frac{w(1-\tau-\delta)}{\psi}\right)^\varepsilon - \left(\frac{w(1-\tau)}{\psi}\right)^\varepsilon$$

For small $\delta$, linearizing:

$$\Delta h \approx -\frac{\varepsilon \, h^*}{1-\tau} \cdot \delta$$

*Combining:*

$$\text{DWL}(\delta) \approx \frac{1}{2} \cdot \frac{w(1-\tau)}{\varepsilon \, h^*} \cdot \left(\frac{\varepsilon \, h^*}{1-\tau}\right)^2 \delta^2 = \frac{1}{2} \varepsilon \, w \, h^* \cdot \frac{\delta^2}{1-\tau}$$

### Expected DWL

If $\delta \sim N(0, \sigma^2)$, then $E[\delta^2] = \sigma^2$ and:

$$\boxed{E[\text{DWL}] \approx \frac{1}{2} \varepsilon \, w \, h^* \cdot \frac{\sigma^2}{1-\tau}}$$

Dividing by earnings $w h^*$:

$$\frac{E[\text{DWL}]}{\text{earnings}} \approx \frac{1}{2} \varepsilon \cdot \frac{\sigma^2}{1-\tau}$$

## Comparative statics

The formula $E[\text{DWL}]/\text{earnings} = \frac{1}{2}\varepsilon\sigma^2/(1-\tau)$ yields immediate comparative statics:

| Parameter | Effect on DWL | Intuition |
|-----------|-------------|-----------|
| $\varepsilon$ (Frisch elasticity) | Linear, positive | More elastic workers make larger errors |
| $\sigma$ (misperception std dev) | Quadratic, positive | Larger errors cause disproportionately larger losses |
| $\tau$ (marginal rate) | Positive via $1/(1-\tau)$ | Higher rates amplify errors in the net-of-tax wage |
| $w h^*$ (earnings) | Linear, positive | Higher earners lose more in absolute terms |

## Optimal tax under misperception

Consider a utilitarian planner choosing $\tau$ to maximize average welfare with a balanced-budget demogrant $v = \tau \bar{w} \bar{h} / N$. The planner's problem under perfect information yields the standard equity-efficiency tradeoff. Under misperception, the effective elasticity of the DWL with respect to $\tau$ increases, since:

$$\frac{\partial \, E[\text{DWL}]}{\partial \tau} > 0$$

The planner internalizes that a marginal increase in $\tau$ raises the DWL from misperception (through the $1/(1-\tau)$ term), leading to:

$$\frac{\partial \tau^*}{\partial \sigma} < 0$$

The optimal tax rate decreases with misperception noise. This is confirmed numerically: the calibration shows $\tau^*$ falls from 44.5% to 42.9% when $\sigma$ increases from 0 to 0.12.

## Cobb-Douglas knife-edge result

For Cobb-Douglas utility $U(L, C) = L^\alpha C^\beta$ with leisure $L = T - h$ and no transfers ($v = 0$), the optimal leisure is:

$$L^* = \frac{\alpha T}{\alpha + \beta}$$

This is independent of the tax rate. The income and substitution effects of a tax change exactly cancel, so misperceiving $\tau$ has no effect on labor supply and hence zero DWL. This knife-edge property motivates the use of quasilinear preferences, which isolate the substitution effect — the empirically relevant channel for tax rate misperception.

```{bibliography}
```
