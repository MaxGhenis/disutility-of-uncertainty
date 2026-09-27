# From observed forecasts to belief parameters

An error distribution suitable for welfare analysis is not identified merely by
an observed discrepancy between a reported and a true tax rate. The discrepancy
can combine decision-relevant misunderstanding, elicitation noise, uncertainty
about the respondent's circumstances, and a mismatch between the tax components
asked about and those considered by the respondent. The calibration software
therefore keeps observed error moments separate from latent belief inputs.

## Two instruments, different information

Study 1 in @rees2020schmeduling elicits federal tax-liability forecasts for a
simplified hypothetical filer. We independently reproduce the pooled panels of
Table 1 from the author-linked replication archive. The local coefficient in
@tbl-empirical-benchmarks regresses perceived on true tax within respondents.
Its weighting depends on within-person true-tax variation; it is not an
individual rate-error RMSE. The archive already excludes some original survey
completers and provides processed forecasts. Reproducing the remaining
attention filter and regression does not reconstruct earlier cleaning.

Our Study 1 audit implements a distinct descriptive statistic: fit perceived
and true tax against income within each respondent's local draws, then subtract
the slopes. Both regressions include an intercept, so a constant liability
level error does not mechanically become a slope error. Native inspection shows
that 89 forecasts flagged as local lie outside the respondent's own nominal
bracket. A strictly within-bracket slope analysis must therefore distinguish
its sample from the published local regression. @sec-study1-audit reports the
validated selection, stored-tax nonaffinity, affine-fit and within-survey
covariance diagnostics. Neither that audit nor the pooled regression identifies
a stable latent dispersion parameter.

Study 2 in @rees2020schmeduling uses choices between taxable and untaxed money
under experimental schedules. Our adapter checks every native A/B choice
against the source monotonicity, first-switch and endpoint flags, then retains
the inequalities. The final attention flag is available, but its underlying
answer is absent. The source exclusion sequence gives 4,582, 3,868, 3,689 and
{{< var rjt_respondents >}} observations. The last group supplies the observed
interval calibration below. The archive checksum begins
{{< var rjt_archive_hash >}}; full member and calculation hashes accompany the
aggregate results.

{{< include generated/empirical-benchmarks.md >}}

## Observed experimental error bounds

For each retained Study 2 respondent, the twelve choices bound the perceived
rate that rationalizes their monetary choices. Subtracting the assigned MTR
gives a signed error interval. Minimizing or maximizing each error or squared
error separately gives sharp marginal bias and RMSE bounds for this sample.
SD has a conservative outer bound because its mean and second moment vary
jointly. These are new descriptive calculations from the replication data,
not latent error estimates reported by the original authors.

{{< include generated/empirical-intervals.md >}}

The first row follows the article's footnote 28 convention, restricting retained
rates to [0,1]. The second uses only the monetary inequalities: for 72 retained
respondents the lowest interval expands from [0,0.05] to [-0.05,0.05]. The
endpoint screen by itself does not justify a nonnegative lower endpoint.
The third row reintroduces final-attention failures while preserving monotone
choices and the endpoint screen. Respondents failing the endpoint screen have
open intervals, so source 0/1 imputations in sensitivity regressions do not
identify finite error-moment bounds for them.

The positive mean-error range is specific to this experimental sample and its
assigned schedules. It is not a contradiction of the Study 1 pooled local
scaling coefficient: the instruments, tax objects, populations and estimands
differ. It also provides no estimate of heterogeneous latent ironing shares.
Our replication reproduces Appendix A9's sensitivity coefficients and counts,
but its printed labels for the two reintroduced groups appear reversed relative
to native flags. The outputs name the actual filters and record this
discrepancy; the primary regression is unaffected.

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

For the real Study 2 intervals, @tbl-empirical-noise unions the observed bounds
with these triangle inequalities under several assumed noise-RMSE caps.
The mean-noise magnitude is bounded by the same cap through Cauchy-Schwarz.
No cap is estimated by the experiment; this calculation makes the unresolved
measurement assumption visible rather than selecting a reliability value.

{{< include generated/empirical-noise.md >}}

For interval observations, we report marginal bounds on bias, second moment,
RMSE and MAE, and conservative outer bounds on SD. These endpoints need not be
jointly attainable. Interval identification, response-noise sensitivity and
sampling uncertainty are distinct sources of uncertainty.

Neither instrument directly measures the comprehensive incentive faced by a
representative U.S. worker. Federal, state, payroll and benefit errors can have
offsetting biases and nonzero covariance. A federal-only RMSE is thus not
automatically a lower bound for their sum. Transport across populations, tax
components and choice contexts requires additional evidence. The native mapping
and selected benchmarks are now validated, but the behavioral and transport
links remain unresolved. The model's 12-point latent RMSE therefore remains an
illustrative assumption, separate from the observed experimental bounds.
