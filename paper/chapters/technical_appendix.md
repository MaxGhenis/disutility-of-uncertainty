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

The default pipeline generates synthetic scenarios and reads the committed national aggregate; it never runs PolicyEngine. Source fingerprints and explicit assumptions accompany the versioned results. Quarto reads generated tables and variables; a check command compares recomputed numbers and paper artifacts to their stored versions. A separately enabled PolicyEngine check runs an actual household model and verifies the finite-grid interpretation. Stored household artifacts carry their complete request and model provenance. Unknown legacy cache provenance is rejected.

The model has no estimated population distribution of beliefs, no estimated intervention effect on beliefs, and no general-equilibrium wage response. The national aggregation weights the illustrative model by PolicyEngine microdata; it does not calibrate beliefs to them. Social welfare calculations use a stated rebate rule and social dollar weights. These limits are part of the estimand rather than adjustments that can be inferred after computing a population total.

## National aggregation

Every expected outcome is proportional to informed earnings $y^0$. A worker with wage one and $\psi=1-\tau$ has $y^0=1$, so one exact evaluation per distinct marginal rate gives private regret, revenue change and social loss per dollar of informed earnings. Each person's amounts are those per-dollar values times observed earnings (employment plus positive self-employment income), and all totals are survey-weighted sums of per-person amounts. Group totals therefore add to the national total by construction. On generated populations, tests check this identity, that quintile totals do not depend on record order, and that national totals do not change when one record's weight is split between two copies.

Earnings quintiles rank records by earnings, then marginal rate, then weight, and assign a record to quintile $q$ when the cumulative weight through it lies in $((q-1)/5,q/5]$ of the total. Weighted percentiles interpolate between cumulative-weight midpoints after dropping zero-weight records, which carry no population mass, and merging tied values, so they depend only on the weighted distribution.

The representative-worker comparison uses the identity
$$\sum_i n_iy_i^0g(\tau_i)-Ny^0_\text{mean}g(\tau_\text{mean})=Ny^0_\text{mean}\big(E[g(\tau)]-g(\tau_\text{mean})\big)+N\,\text{Cov}\big(y^0,g(\tau)\big),$$
where $g$ is a per-dollar outcome, $n_i$ are survey weights, $N=\sum_in_i$, and means and covariance are weighted. The first term is nonnegative for the convex interior formula $g(\tau)=\varepsilon r^2/[2(1-\tau)]$; the second can take either sign.

The aggregate is built by `python -m taxuncertainty.analysis.national` with the PolicyEngine extra. It records package versions, the certified bundle manifest, the dataset's URI and hash, the person filter, a hash of the extracted arrays, and a hash of the aggregate itself; the pipeline rejects an aggregate whose content hash does not match. The microdata are not stored.
