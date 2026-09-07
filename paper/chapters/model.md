# Model and welfare accounting

## Preferences and informed choice

Worker $i$ earns wage $w_i>0$ and has preferences

$$U_i(c_i,h_i)=c_i-\psi\frac{h_i^{1+1/\varepsilon}}{1+1/\varepsilon},\qquad \psi>0,\;\varepsilon>0.$$

Consumption under a linear tax is $c_i=w_i(1-\tau)h_i+v$, where $v$ is an equal transfer. Labor is nonnegative. For $\tau<1$, the informed choice is

$$h_i^0=\left[\frac{w_i(1-\tau)}{\psi}\right]^{\varepsilon}.$$

At $\tau\geq1$, the informed choice is zero. Negative tax rates are valid earnings subsidies; they require a belief specification that permits negative perceived rates. Quasilinearity eliminates income effects, so the transfer shifts utility without changing optimal hours. This is a tractability assumption, not a claim that income effects are absent empirically.

## Bias, dispersion, and perception bounds

The latent error has distribution $\delta_i\sim N(\mu,s^2)$. Its signed mean is $\mu$, standard deviation is $s$, and root-mean-square error is $r=\sqrt{\mu^2+s^2}$. Negative $\mu$ means underestimation. For the central illustrations the perceived rate is

$$\widehat\tau_i=\min\{1,\max\{0,\tau+\delta_i\}\}.$$

The implementation makes both bounds explicit and allows them to be changed or removed. These bounds censor the distribution; they do not truncate and redraw it. They create probability masses at the bounds and change the realized error moments. Define $e_i=\widehat\tau_i-\tau$. In general, $E[e_i]\ne\mu$ and $E[e_i^2]\ne r^2$. All three realized moments are recorded alongside the latent parameters.

A worker chooses $\widehat h_i=h_i^0(\widehat\tau_i)$ and receives consumption under the true rate. The analysis assumes belief errors are independent of wages and that workers optimize against their perceived rate. The numerical expectations need only the marginal distribution of each error: quasilinearity makes social welfare additive even when the transfer depends on everyone's choices.

## Private regret

Write $u_i(h;\tau)=w_i(1-\tau)h-\psi h^{1+1/\varepsilon}/(1+1/\varepsilon)$ for utility before the common transfer. Private optimization regret is

$$P_i=u_i(h_i^0;\tau)-E[u_i(\widehat h_i;\tau)]\geq0.$$

The inequality follows because informed hours maximize true private utility. It applies with the transfer held fixed. The exact calculation integrates realized utility at each perceived rate; it does not substitute expected hours into the nonlinear disutility term.

For small errors around an interior informed choice, with $y_i^0=w_i h_i^0$,

$$P_i\approx\frac{1}{2}\frac{\varepsilon y_i^0 E[e_i^2]}{1-\tau}.$$

Without consequential censoring, $E[e_i^2]=\mu^2+s^2$. This second-order expression concerns private regret. It does not by itself measure the change in social welfare.

## Revenue, transfers, and social loss

The expected change in revenue is

$$\Delta R=\tau\sum_iw_i(E[\widehat h_i]-h_i^0),\qquad\Delta v=\frac{\Delta R}{N}.$$

With normative social dollar weights $\omega_i$, the loss in average social welfare is exactly

$$L=\frac{1}{N}\sum_i\omega_iP_i-\overline\omega\frac{\Delta R}{N},\qquad\overline\omega=\frac{1}{N}\sum_i\omega_i.$$

A positive $L$ is a loss; a negative $L$ is a gain. Under equal weights, total social loss is $\sum_iP_i-\Delta R$. Misperception need not reduce revenue: an underestimate can induce additional taxable labor. This revenue is a transfer between workers and the government, but its *change between behavioral counterfactuals* matters when combining private utility with the government account. The identity neither creates resources by collecting a tax nor counts a rebate twice.

For a small interior error, the fiscal channel has a first-order bias term:

$$\Delta R_i\approx\tau y_i^0\left[-\frac{\varepsilon E[e_i]}{1-\tau}+\frac{\varepsilon(\varepsilon-1)E[e_i^2]}{2(1-\tau)^2}\right].$$

Consequently, a second moment is insufficient to identify the fiscal or social effect. For mean-zero uncensored errors, the ratio of approximate social loss to private regret under equal weights is $1+\tau(1-\varepsilon)/(1-\tau)$. With nonzero mean, the first-order term can dominate private regret for small errors.

## The planner

A planner chooses a common linear rate within the stated search range and returns the resulting revenue equally. Its objective is expected average utility, using either equal weights or $\omega_i=\overline w/w_i$. The inverse-wage weights introduce a redistribution motive. They are normative choices, not survey weights.

The planner evaluates exactly the same hours, utility, and government account as the worker analysis. Its optimum is computed on a coarse grid and then a finer local grid. The result records the search range, resolution, and whether the solution touches a boundary. The reported rate is a numerical maximizer on that search grid; no claim of a general optimal-tax theorem follows from comparing two scenarios.
