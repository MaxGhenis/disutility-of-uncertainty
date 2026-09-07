# From observed forecasts to belief parameters

An error distribution suitable for welfare analysis is not identified merely by
an observed discrepancy between a reported and a true tax rate. The discrepancy
can combine decision-relevant misunderstanding, elicitation noise, uncertainty
about the respondent's circumstances, and a mismatch between the tax components
asked about and those considered by the respondent. The calibration software
therefore keeps observed error moments separate from latent belief inputs.

## Two instruments, different information

Study 1 in @rees2020schmeduling elicits federal tax-liability forecasts for a simplified
hypothetical filer. Local forecasts permit an analysis of perceived slopes.
The reported respondent-fixed-effects scaling coefficient in Table 1 is 0.81,
with a standard error of 0.043. It is a coefficient from regressing perceived on
true tax within respondents, not an individual rate-error RMSE. The source's
selection and winsorization choices also matter for any new dispersion analysis.

Our adapter proposes a distinct descriptive statistic: fit perceived and true
tax against income within each respondent's local draws, then subtract the two
slopes. Both regressions include an intercept, so a constant error in the level
of reported liability does not mechanically become a slope error. The adapter
records exclusions, income spans and leverage, and reports the pooled source
estimand separately. Its canonical input schema has been tested; mapping the
replication archive's native fields and reproducing its cleaning remain
unverified. Consequently, no empirical microdata moments are reported here.

Study 2 in @rees2020schmeduling infers perceived rates from choices between taxable and
untaxed money under experimental tax schedules. These choices identify
intervals. The article's midpoint coding and endpoint convention are described
in section 4.1.3 and footnote 28. Our adapter preserves the inequalities and
records an optional support restriction explicitly. It does not infer individual
within-interval dispersion from a midpoint.

## Observed moments and response noise

Let $e^{\mathrm{obs}}_{ij}$ be perceived minus true rate for respondent $i$ and
observation $j$, with $m_i$ observations for that respondent. For $N$ respondents,
the descriptive mean of a function $g$ is

$$\overline{g(e)}=\frac{1}{N}\sum_{i=1}^{N}\frac{1}{m_i}
\sum_{j=1}^{m_i}g(e^{\mathrm{obs}}_{ij}).$$

This gives each respondent equal mass. The observed bias, SD, RMSE and MAE use
the same measure, so

$$\mathrm{RMSE}_{\mathrm{obs}}^2=b_{\mathrm{obs}}^2+s_{\mathrm{obs}}^2,
\qquad \mathrm{RMSE}_{\mathrm{obs}}\geq\mathrm{MAE}_{\mathrm{obs}}
\geq |b_{\mathrm{obs}}|.$$

The variance is descriptive and uses no degrees-of-freedom correction.
Respondent-cluster bootstrap intervals describe sampling variation conditional
on the supplied records and transformations. They do not establish national
representativeness or correct elicitation noise.

For a local slope, independent homoskedastic dollar-response noise with variance
$s_\eta^2$ contributes slope variance $s_\eta^2/S_{xx,i}$, where
$S_{xx,i}=\sum_j(z_{ij}-\bar z_i)^2$. With two income draws separated by $D$,
this becomes $2s_\eta^2/D^2$. Short spans can therefore amplify even small dollar
errors. Two draws leave no residual degrees of freedom to estimate this noise.
Repeated tasks at different incomes can also reflect a nonlinear perceived
schedule, rounding or learning. Within-respondent variation is not automatically
measurement error.

## Conditional bounds and coverage

Suppose $e^{\mathrm{obs}}=e^{\mathrm{latent}}+u$. If $E[u]=0$ and
$\operatorname{Cov}(e^{\mathrm{latent}},u)=0$, allowing noise variance anywhere
between zero and observed variance implies

$$s_{\mathrm{latent}}\in[0,s_{\mathrm{obs}}],\qquad
\mathrm{RMSE}_{\mathrm{latent}}\in[|b_{\mathrm{obs}}|,
\mathrm{RMSE}_{\mathrm{obs}}].$$

These are sensitivity ranges conditional on classical-noise restrictions and
observed moments, not confidence intervals or estimates of reliability. The
implementation also allows assumed noise-bias and noise-SD ranges, and rejects
incompatible variance assumptions. If covariance is unrestricted but the RMSE of
$u$ is bounded by $a$, the triangle inequality gives only

$$\mathrm{RMSE}_{\mathrm{latent}}\in
[\max(0,\mathrm{RMSE}_{\mathrm{obs}}-a),\mathrm{RMSE}_{\mathrm{obs}}+a].$$

For interval observations, we report marginal bounds on bias, second moment,
RMSE and MAE, and conservative outer bounds on SD. These endpoints need not be
jointly attainable. Interval identification, response-noise sensitivity and
sampling uncertainty are distinct sources of uncertainty.

Neither instrument directly measures the comprehensive incentive faced by a
representative U.S. worker. Federal, state, payroll and benefit errors can have
offsetting biases and nonzero covariance. A federal-only RMSE is thus not
automatically a lower bound for their sum. Transport across populations, tax
components and choice contexts requires additional evidence. Until those links
and the native-data mapping are validated, the model's 12-point latent RMSE
remains an illustrative assumption.
