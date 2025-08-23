# Technical Appendix

## Proof of Optimal Leisure Formula

Consider the optimization problem:
$$\max_{L} U(L, w(1-\tau)(T-L) + v)$$

For Cobb-Douglas utility $U(L,C) = L^\alpha C^\beta$, the first-order condition is:
$$\alpha L^{\alpha-1}C^\beta = \beta L^\alpha C^{\beta-1} w(1-\tau)$$

Simplifying:
$$\frac{\alpha C}{\beta L} = w(1-\tau)$$

Substituting the budget constraint $C = w(1-\tau)(T-L) + v$:
$$\frac{\alpha[w(1-\tau)(T-L) + v]}{\beta L} = w(1-\tau)$$

Solving for L:
$$L^* = \frac{\alpha[w(1-\tau)T + v]}{w(1-\tau)(\alpha + \beta)}$$

## Welfare Loss Under Uncertainty

Let $\tau \sim F(\tau)$ be the distribution of tax rates. Under certainty, expected utility is:
$$EU_c = \int U(L^*(\tau), C^*(\tau)) dF(\tau)$$

Under uncertainty, agents choose based on $E[\tau]$:
$$EU_u = \int U(L^*(E[\tau]), C(\tau, L^*(E[\tau]))) dF(\tau)$$

The deadweight loss equals:
$$DWL = EU_c - EU_u$$

By Taylor expansion around $E[\tau]$:
$$DWL \approx \frac{1}{2}\text{Var}(\tau) \cdot U''(\tau)|_{\tau=E[\tau]}$$

## Comparative Statics

The effect of uncertainty on optimal tax rates:
$$\frac{\partial \tau^*}{\partial \sigma_\tau} = -\frac{\partial^2 W/\partial \tau \partial \sigma}{\partial^2 W/\partial \tau^2} < 0$$

This confirms that optimal tax rates decrease with uncertainty.
