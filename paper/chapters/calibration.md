# Inputs and evidentiary status

The illustrative worker earns \$27.50 per hour and works 2,000 hours under correct perceptions at a 30% true tax rate. These choices normalize annual earnings to \$55,000. The labor-disutility scale is chosen to make this an actual model optimum:

$$\psi=\frac{27.50(1-0.30)}{2000^{1/\varepsilon}}.$$

The central elasticity is 0.33, with sensitivity values 0.25 and 0.50. The central value is informed by the intensive-margin Hicksian estimate discussed above; applying it to quasilinear preferences is an assumption. The wage, hours, tax rate, and sensitivity endpoints are illustrative inputs, not estimated population means or statistical confidence limits.

The normal belief distributions in @tbl-beliefs separate signed bias from dispersion. Four scenarios share a latent RMSE of 12 percentage points. This common RMSE allows a controlled comparison of the error distribution's shape. It does not imply that their realized moments after censoring are identical. The deterministic one-point underestimate provides a small-error accounting check.

{{< include generated/beliefs.md >}}

For the planner, 500 synthetic wages are drawn from a lognormal distribution with a target mean of \$27.50 and log standard deviation 0.5, using seed 42. The finite sample need not equal that target mean exactly. The sample is an illustration of wage heterogeneity and does not represent 500 survey records or a calibrated U.S. population. The planner uses the same common preferences across workers. Rescaling $\psi$ rescales hours, revenue, and utility by a common factor and leaves the optimal tax unchanged in this unconstrained linear model.

An empirical calibration would need a specified sample linking perceived and actual incentives, a separation of measurement error from decision-relevant misperception, and explicit coverage of federal, state, payroll, and benefit components. For summed component errors, variance includes covariance terms; positive covariance increases total variance relative to independence, holding component variances fixed. No ordering of comprehensive error magnitude follows merely from calling some components complex.
