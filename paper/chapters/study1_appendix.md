# Appendix: Study 1 calibration evidence {#sec-study1-audit}

Study 1 of @rees2020schmeduling supports reproducible **finite-design forecast
projections**, with substantial selection and measurement limitations. It does
not separately identify stable individual marginal-tax beliefs or their latent
variance. This appendix integrates a separately audited calculation; the
original authors did not report the projection-error and sensitivity tables
below. The pooled Table 1 benchmarks and all Study 2 findings above are unchanged.

## Retained sample, processing and true-tax support

The native archive contains {{< var s1_archive_rows >}} forecasts from
{{< var s1_archive_people >}} people. Applying `attention==0` retains
{{< var s1_rows >}} forecasts from {{< var s1_people >}} people. The article's
earlier 195 exclusions and original rolling winsorization cannot be rerun from
these retained files. The {{< var s1_reused_rows >}} rows in
`individualestimates.dta` reuse the same random-income answers: all {{< var s1_reused_columns >}} audited
numeric fields match, so this file supplies no independent remeasurement.
The main outcome `taxguessmain` equals `tgw1`. Relative to retained
pre-winsorization `taxguessds`, {{< var s1_float_changes >}} differences arise
only from float32 storage conversion; {{< var s1_other_changes >}} exceed that
conversion, affecting {{< var s1_other_people >}} people. These differences
do not isolate response noise. For the full random-income design, observed error
SD is {{< var s1_full_main_sd >}} pp with the main outcome,
{{< var s1_full_unwinsorized_sd >}} pp before winsorization, and
{{< var s1_full_tgw5_sd >}} pp with the retained `tgw5` alternative.

The native local flag is `(qnum<=2) or (bracket==ownbracket)` and includes
{{< var s1_outside >}} forecasts outside the respondent's own nominal bracket.
Even bracket matching does not establish a locally affine true tax function.
Of {{< var s1_affine_candidate_n >}} respondents with at least three distinct
own-bracket incomes, {{< var s1_nonaffine >}} fail an **observed affine screen**:
maximum absolute residual from an OLS line through stored true liabilities must
be at most \$0.05. Their {{< var s1_phaseout_rows >}} affected forecasts carry
positive stored exemption phaseout. The maximum departure from the nominal
own-rate line is \${{< var s1_nominal_departure >}}. A separate stored-field
calculation reconciles that departure to the exemption-phaseout tax amount
within \${{< var s1_phaseout_discrepancy >}}. This checks archived arithmetic;
the missing liability-generation code prevents certification of the complete
legal schedule. Passing at observed points does not establish affinity between
them, and a perfect two-point fit supplies no such test.

For each respondent, regress the forecast on income with an intercept and
subtract the slope of stored true tax on the **same incomes**. This signed
projection error has units of tax dollars per income dollar; multiply by 100
for percentage points. It is not automatically a point-MTR error. Unlike the
pooled tax-on-tax coefficient, which weights people by within-person true-tax
variation, the descriptive moments below give each person equal mass and use
variance denominator $N$.

{{< include generated/study1-selection.md >}}

The extreme short-span SDs are untrimmed calculations, not unit mistakes.
Liability winsorization does not cap slopes divided by small income differences.
Requiring four distinct own-bracket incomes, at least \$5,000 support and the
observed affine screen leaves {{< var s1_selected_n >}} people. Their mean signed
error is +{{< var s1_selected_bias >}} pp, but this precision screen raises median
own income from \${{< var s1_original_income >}} to
\${{< var s1_selected_income >}}. The sample and estimand therefore change with
the screen. The smaller full-range SD also does not validate local beliefs:
every respondent's full-range stored true-tax values fail the affine screen.

## Compatibility with an assumed answer-error cap

For an assumed dollar cap $a$, ask whether **some** intercept $\alpha$ and
unrestricted slope $\beta$ satisfy

$$|y_{ij}-\alpha-\beta x_{ij}|\leq a\quad\text{for every retained answer }j.$$

For every pair with $x_j>x_k$, intersect the intervals
$[(y_j-y_k-2a)/(x_j-x_k),(y_j-y_k+2a)/(x_j-x_k)]$; equal-income pairs additionally
require $|y_j-y_k|\leq2a$. This is necessary and sufficient because the implied
intercept intervals have a common intersection exactly when they overlap
pairwise. Writing the intersection bounds as $L,U$, the implementation closes
a reversed endpoint gap only when
$L-U\leq10^{-12}\max(1,|L|,|U|)$, in slope-fraction units; this is numerical
tolerance, not a larger dollar-error cap. The minimum feasible cap is
$\tfrac12\min_\beta[\max_j(y_j-\beta x_j)-\min_j(y_j-\beta x_j)]$.

{{< include generated/study1-affine.md >}}

The median minimum cap is \${{< var s1_minimum_cap >}}. Failure rejects the
**joint affine-forecast model and assumed cap**; it does not identify curved
beliefs, response mistakes, stable belief types or irrationality. Passing does
not establish temporal stability. In particular, the {{< var s1_compatible_100 >}}/{{< var s1_selected_n >}} result at a
\$100 cap is not a type share. The experiment's \$100 accuracy window for earning
a \$1 bonus does not bound answer errors. Retaining only compatible respondents
would add outcome-based selection.

Without requiring affine beliefs, a cap $|u_{ij}|\leq a$ bounds the difference
between observed and latent **projected** slopes by
$a\sum_j|x_{ij}-\bar x_i|/S_{xx,i}$. At an assumed \$100 cap, its median radius
is {{< var s1_pair_radius >}} pp for the own-income pair versus
{{< var s1_selected_radius >}} pp in the screened sample. These deterministic
sensitivities permit biased, correlated noise; the cap is not estimated.
Without a noise restriction, no finite latent upper bound follows.

## Within-survey covariance and unidentified latent variance

The archive contains only one incidental exact-income repeat, with a \${{< var s1_incidental_repeat_gap >}}
forecast discrepancy, and no independent waves. Instead, sorting each person's
draws by `(ran,qnum)` and alternating them creates two disjoint income designs.
Each half must contain at least two distinct incomes; `qnum` denotes sampling
slots, not a verified presentation order. Among own-bracket respondents passing
the observed affine screen, requiring each half to span at least \$5,000 leaves
{{< var s1_repeat_n >}} people. The covariance of their signed error projections
is {{< var s1_repeat_covariance >}} pp$^2$, with delete-one-person jackknife SE
{{< var s1_repeat_se >}} pp$^2$ and correlation approximately
{{< var s1_repeat_correlation >}}. Covariance uses denominator $N-1$; both it and
its SE multiply by 10,000 when converting squared fractions to pp$^2$.
The jackknife describes sampling variation under independent respondents, not
a measurement-error correction.

Under $s_A=\theta+u_A$, $s_B=\theta+u_B$, covariance equals
$\operatorname{Var}(\theta)$ only if both errors are orthogonal to the **same**
target and to each other. Curved beliefs and different income supports may
violate the common-target assumption. Homoskedastic iid residual SEs assume a
correct line and independent answer errors; HC3 allows heteroskedasticity but
does not remove shared response errors. Splitting one survey is not test-retest
measurement.

Even granting a common target and orthogonality to it, error correlation $\rho$
changes the variance decomposition:

$$C=V+\rho\sqrt{(V_A-V)(V_B-V)},\qquad 0\leq V\leq\min(V_A,V_B).$$

Here the sample moments in squared fractions are
$V_A$ = {{< var s1_repeat_var_a >}}, $V_B$ = {{< var s1_repeat_var_b >}} and
$C$ = {{< var s1_repeat_covariance_fraction >}}.

{{< include generated/study1-covariance.md >}}

At $\rho=0$, $V=C$; at $\rho=C/\sqrt{V_AV_B}$, $V=0$ reproduces the same second
moments. This admissible decomposition neither estimates actual noise
correlation nor proves zero stable heterogeneity. The archive supplies no
restriction that selects one decomposition.

The hypothetical 2014 federal salary-tax filer, standard deduction and absence
of additional credits/deductions also limit coverage. Recruitment approximating
some census demographics does not establish representative latent beliefs;
state taxes, payroll taxes, benefits and behavioral transport remain unmeasured.
None of these projection SDs, compatibility shares or conditional decompositions
replaces the model's **illustrative latent RMSE of 0.12** or identifies a national
welfare calibration.

The repository's `calibration/study1/README.md` documents reproduction from the
checksum-pinned archive. Its manifest preserves the minimal aggregate inputs
and audit code at reviewed commit `a5191ea`, with the later report precision
clarification recorded separately. The normal pipeline generates the appendix
tables and inline values from that evidence cache. Raw microdata, original
source code and source PDFs are not redistributed; their licensing restrictions
remain unchanged.
