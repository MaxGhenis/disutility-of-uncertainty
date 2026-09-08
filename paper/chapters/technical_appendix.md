# Derivation and numerical checks

## Private-regret expansion

Let $q=1-\tau>0$. At the informed interior optimum, $u_h=0$ and $u_{hh}=-wq/(\varepsilon h^0)$. The response to a small realized error is

$$\Delta h=-\frac{\varepsilon h^0}{q}e+\frac{\varepsilon(\varepsilon-1)h^0}{2q^2}e^2+O(e^3).$$

Substitution into the second-order utility expansion gives

$$P\approx\frac{1}{2}|u_{hh}|E[(\Delta h)^2]=\frac{\varepsilon y^0}{2q}E[e^2].$$

The same hours expansion gives $\Delta R=\tau wE[\Delta h]$. The social-loss identity follows by adding the expected change in the balanced-budget transfer to private utility, with the specified social dollar weights. It does not require a Taylor approximation.

## Expectation and optimization

The primary linear calculation integrates the normal density deterministically, including probability masses at censoring bounds. Integration intervals are split at the zero-hours corner. A change of variables resolves the fractional-power labor-supply behavior there. Uncensored tails beyond 12 standard deviations are omitted and probabilities normalized; this probability approximation is negligible for the reported parameter range. Numerical convergence is checked by increasing quadrature order, and independent Monte Carlo checks evaluate utility and balanced transfers directly.

For the planner, common preferences and a belief distribution independent of wages allow wage moments and belief moments to be evaluated separately. Expected labor disutility uses the expected power of hours, not the power of expected hours. The default tax search spans 0 to 0.8 with 81 grid points, followed by another 81-point grid around the coarse maximum. The final grid spacing and boundary status are stored.

Tests cover no-error identities, the small-error limit, signed-bias fiscal effects, equal and inverse-wage objectives, negative true rates with compatible belief bounds, corners at and above a 100% tax, censored moments, explicit nonlinear thresholds, subsidies, and discrete grid optimization. A deterministic one-point underestimate is checked against direct realized utility. Zero private regret and zero fiscal change are required in an informed comparison whenever the chosen belief bounds contain the true rate.

## Replication and scope controls

The default pipeline generates only synthetic scenarios. Source fingerprints and explicit assumptions accompany the versioned results. Quarto reads generated tables and variables; a check command compares recomputed numbers and paper artifacts to their stored versions. A separately enabled PolicyEngine check runs an actual household model and verifies the finite-grid interpretation. Stored household artifacts carry their complete request and model provenance. Unknown legacy cache provenance is rejected.

The model has no calibrated national sample, no estimated intervention effect on beliefs, and no general-equilibrium wage response. Social welfare calculations use a stated rebate rule and social dollar weights. These limits are part of the estimand rather than adjustments that can be inferred after computing a population total.
