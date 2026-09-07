# Estimands, assumptions and finite-sample calculations

The empirical source is [Rees-Jones and Taubinsky, “Measuring ‘Schmeduling’”](https://alexreesjones.github.io/papers/Measuring%20Schmeduling.pdf), with [native archive](https://www.dropbox.com/s/2q47bj8arbcgr3i/Schmeduling%20Replication%20Code.zip?dl=1). `scripts/sources.py` rejects any archive whose SHA256 differs from the retained source. `scripts/audit.py` works in float64 **after** loading native codes and float32 values; this preserves the stored values while avoiding new single-precision arithmetic errors. No new tax calculation is used as ground truth.

**Observed individual projection.** For a respondent's selected incomes x_j, forecasts y_j and native true liabilities T_j, define

\[
S_{xx}=\sum_j(x_j-\bar x)^2,\qquad
w_j=(x_j-\bar x)/S_{xx},\qquad
\hat b=\sum_jw_jy_j,\quad b_T=\sum_jw_jT_j,\quad
\hat e=\hat b-b_T.
\]

An intercept is always included. Duplicate respondent/question keys and missing audited numeric data fail validation. A slope requires at least two distinct incomes; singular cases are not imputed. Weights w are algebraic OLS contrast coefficients, **not person/tax-unit/population weights**. Person-level moment tables give each retained respondent equal mass.

These objects are finite-design projections. If a latent belief function B_i(x) is nonlinear, its projected derivative depends on the realized income design. Even an affine fit to observed true liabilities cannot establish affinity between observations. A point-MTR interpretation requires a known complete true schedule, an appropriate local derivative/interval, a locally affine latent belief function (or a stated approximation error), and an account of response noise. None is inferred merely from `bracket==ownbracket`.

**Published pooled scale.** Table 1 estimates forecast on true tax with respondent fixed effects. With demeaned x now denoting **true tax**, the coefficient is

\[
\hat\beta=\frac{\sum_i\sum_j(T_{ij}-\bar T_i)(y_{ij}-\bar y_i)}
{\sum_i S_{TT,i}}
=\sum_{i:S_{TT,i}>0}\frac{S_{TT,i}}{\sum_kS_{TT,k}}\hat\beta_i.
\]

A person's zero true-tax variation contributes no identifying variation. The native clustered variance is `G/(G−1) × sum_i(score_i²)/(sum_i S_TT,i)²`, with `score_i=sum_j((T_ij−mean_i T)(y_ij−mean_i y−beta(T_ij−mean_i T)))`. This replicates the native one-slope `xtreg ..., fe vce(cluster mid)` convention. It does not supply the variance of individual beliefs. The pooled coefficient, mean individual income slope and a structural mixture share are distinct estimands. [Table 1, p. 2415](https://alexreesjones.github.io/papers/Measuring%20Schmeduling.pdf); native `Table 1.do:47–75`.

**Retained heuristic estimates.** For equations 3.2 and 3.3, set baseline q=T for variants 1/3 or q=T+r_hat(T) for 2/4. The model is `y−q = gamma_I(iron−q)+gamma_S(spotlight−q)+error`, with no additional intercept. Thus a two-column linear least-squares solution reproduces the source's NLLS estimates without iterative convergence failures. The residual-misperception functions for 2/4 are taken from the retained individualestimates file; their estimation uncertainty is not included in the reported conditional iid SEs. They are common functions estimated using the source sample, which is another reason these SEs cannot be read as complete latent-heterogeneity uncertainty. The simplex grid is all `(i/10,j/10)` with nonnegative integers and `i+j≤10`; squared forecast error determines assignments. All 484 cells of [Tables A5–A8](https://alexreesjones.github.io/papers/Measuring%20Schmeduling%20Online%20Appendix.pdf) match exactly. No density peaks or classification shares are converted into a latent mixture claim.

**Leverage and SE diagnostics.** For a forecast-on-income regression, `h_jj=1/n+(x_j−mean x)²/Sxx`. The iid variance estimate is `SSE/((n−2)Sxx)`. HC3 is `sum_j[w_j residual_j/(1−h_jj)]²`. The absolute change in slope when deleting point j is `|w_j residual_j/(1−h_jj)|` whenever the reduced design still identifies the slope. Two observations give no residual degrees of freedom and unit leverage; their SEs and leave-one-out slopes are undefined, never zero. Heteroskedasticity correction does not correct response errors shared across observations, misspecified latent curves or selection on income support.

**Sharp individual bounds under explicit dollar-error limits.** Let `y_j=B(x_j)+u_j`. Without assuming B is affine, the difference between observed and latent projected slopes is `sum_j w_j u_j`.

- If every `|u_j|≤a`, the sharp radius is `r_i=a sum_j|w_j|`. It is attained by `u_j=a sign(w_j)` or its negative.
- If `sqrt(mean_j u_j²)≤a` separately for this respondent, Cauchy–Schwarz gives sharp radius `r_i=a sqrt(n_i/Sxx_i)`. It is attained by an error vector proportional to w.

The bounds allow arbitrary bias and within-person correlation, including errors proportional to income. The radius is invariant to a common intercept error because `sum w_j=0`. Caps are sensitivity parameters, not estimates from residuals, heaping, the $100 bonus or the source's winsorization. Here u includes all departures between the processed measured forecast and the postulated latent function; interpreting it as mere dollar rounding is much stronger.

Given per-person radii r_i, let `R=sqrt(mean_i r_i²)`. For equal-person finite-sample moments (denominator N):

\[
\begin{aligned}
\operatorname{bias}(e^*)&\in[\bar{\hat e}-\bar r,\bar{\hat e}+\bar r],\\
\operatorname{RMSE}(e^*)&\in[\max(0,\operatorname{RMSE}(\hat e)-R),\operatorname{RMSE}(\hat e)+R],\\
\operatorname{SD}(e^*)&\in[\max(0,\operatorname{SD}(\hat e)-R),\operatorname{SD}(\hat e)+R].
\end{aligned}
\]

The last two are conservative outer bounds from the triangle inequality; demeaning is an orthogonal contraction. They are not necessarily sharp or jointly attainable. The bias interval is sharp for the independent personwise boxes implied by the caps. These are conditional finite-sample sensitivity ranges, not confidence intervals or population moments. Synthetic exhaustive-corner and norm-attainment tests verify the formulas.

**Exact affine-belief falsification and slope sets.** To test the stronger assumption `B(x)=a_0+b x`, impose `|y_j−a_0−b x_j|≤a` for every observation. Sort incomes. For every pair `x_j>x_k`, feasibility requires

\[
\frac{y_j-y_k-2a}{x_j-x_k}\le b\le
\frac{y_j-y_k+2a}{x_j-x_k}.
\]

Equal-income pairs require `|y_j−y_k|≤2a`. Intersecting all slope intervals is necessary and sufficient: at any admissible b the intervals `[y_j−b x_j−a,y_j−b x_j+a]` have pairwise overlap, which for intervals on the real line implies a common intercept. An empty intersection rejects the conjunction of affine beliefs and the specified cap. It does not diagnose which part fails. Selecting respondents based on a nonempty set changes the sample by their outcomes.

An independent calculation finds the smallest feasible cap:

\[
a_i^{\min}=\tfrac12\min_b\left\{\max_j(y_j-bx_j)-\min_j(y_j-bx_j)\right\}.
\]

The objective is convex and piecewise linear. A minimum occurs at a pairwise secant breakpoint or a flat interval with such an endpoint; evaluating the finite set of secants solves it exactly. Equal-income-only designs reduce to half the response range. The algorithm verifies its feasibility answer against every cap in the empirical sensitivity grid. A 1e-12 relative slope tolerance handles numerical endpoint equality only. Two distinct points always fit a line exactly, even for an extreme slope, so these cannot falsify affinity without an external slope restriction.

**Disjoint forecast measurements.** Within each sample, sort by `(ran,qnum)` and take alternating observations for A/B; the second implementation instead separates even/odd qnum. Every half must have two distinct incomes. An optional half-span threshold applies to both halves. The source qnum is a draw slot, not a known temporal order. Fit `(forecast−tax)` on income separately in the halves. This contrasts error projections on different designs; their target need not coincide under nonlinear beliefs.

Under the substantive repeated-measure model `s_A=theta+u_A`, `s_B=theta+u_B`, with both errors mean zero conditional on theta and design and cross-error covariance zero, cross-person covariance identifies Var(theta) in the selected population. Conditional mean zero also implies orthogonality. All stochastic covariance tables use denominator N−1. The identity `Var((A+B)/2)−Var(A−B)/4=Cov(A,B)` holds as sample arithmetic; it does not prove the assumptions. Negative covariance is preserved. An exact leave-one-person covariance formula yields the jackknife SE, conditional on independent respondents; heavy tails, dependence and measurement-model misspecification can undermine normal approximations.

For the correlated-error sensitivity, assume both errors remain orthogonal to the same target but allow correlation rho. Let observed variances be V_A,V_B and covariance C. A candidate target variance V must satisfy

\[
C=V+\rho\sqrt{(V_A-V)(V_B-V)},\qquad 0\le V\le\min(V_A,V_B).
\]

For the reported positive-C rows, a deterministic bisection solves the model for rho from zero to the observed correlation. At rho=0, V=C; at rho=Corr(A,B), V=0. This is a moment-model sensitivity conditional on estimates, with no claim that actual error correlation has been measured. The archive supplies no exclusion restriction to set rho to zero.

The exact 256-person factorial counterexamples are **synthetic**: independent balanced signs generate latent slopes, a common session response slope and six point errors. Each point has its own orthogonal sign. A shared session slope enters both halves indistinguishably from stable heterogeneity. The same measured forecasts can be represented either as heterogeneous stable slopes with no method slope, or homogeneous stable slopes plus heterogeneous session errors. More observations in the same session cannot distinguish those representations. A common dollar-intercept shock cancels from the income slope and is explicitly tested as a negative control.
