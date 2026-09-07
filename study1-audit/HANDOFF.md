# Study 1 feasibility audit handoff

**Completed:** an independent, artifact-only empirical audit of Alex Rees-Jones and Dmitry Taubinsky's *Measuring “Schmeduling”* (2020). The archive permits observed forecast-slope estimation and conditional sensitivity analysis. Stable individual MTR beliefs and their latent variance are not separately identified.

The [methods report](REPORT.md) contains primary-source links and quantitative tables. [METHODS.md](METHODS.md) derives the estimands and bounds; [MEASUREMENT_PROTOCOL.md](MEASUREMENT_PROTOCOL.md) specifies the next feasible experiment. [README.md](README.md) documents reproduction.

Key findings:

- All three pooled Table 1 regressions and all 484 Appendix A5–A8 cells reproduce. Available identified individual gammas match within 0.000004; these are heuristic coefficients, not repeated MTR measurements.
- 700 people have only two native local forecasts. Own-income pairs span a median $502. Their variance is dominated by a few respondents; direct difference arithmetic independently agrees with the general OLS code.
- Nominal bracket matching leaves 13 respondents with nonaffine stored tax liabilities. Phaseout arithmetic explains the departures, but a complete tax-function certification remains unavailable.
- Only 555/2,470 people with at least four own-bracket points, a $5,000 span and observed affine tax values can fit any affine belief schedule within $100 per answer. Median minimum cap: $693.29.
- Local split covariance can be explained by error correlation equal to the observed correlation (approximately 0.1002613) with zero common latent variance. There are no independent repeated waves; the retained individual-estimates file attaches parameters to existing forecasts.
- 958 of 1,501 main/pre-winsor forecast differences are solely float32 conversion; 543 exceed that conversion. Dispersion remains sensitive to source processing and income-span selection.

Branch: `audit/study1-feasibility-20260907`, isolated from `origin/main` at `5d134c14630613ff32819abe99ad5109b65b07a5`. Only `PROGRESS.md` and `study1-audit/` differ from that base. A live fetch during this precision follow-up verified the same base; the original sandbox fetch failure remains documented as historical execution context. The completed PR3 checkout is outside this correction's scope and was not edited. No PR, publication or merge was made.

Validation at the independently reviewed head: 28 analytical/adversarial/native-data tests passed, direct source-field arithmetic checks passed, and generated aggregate/report files reproduced byte-for-byte. The original [reproduction evidence](evidence/reproduction-verification.json) and [preservation evidence](evidence/preservation-verification.json) remain unchanged historical records, including the original report hash.

The existing independent host review is **clean within the finite-design feasibility scope** at exact head `a5191ea9f81fd414d9fbf547995dcb31341aa875`. It independently reran all 28 tests and reproduced 36 tracked result/evidence/report files byte-for-byte, with separate source and mathematical checks. Its sole nonblocking finding was rounded precision in the exact-threshold sentence. [Review scope and original evidence](evidence/REVIEW_STATUS.md).

This follow-up resolves only that display finding: the renderer now derives approximately 0.05013 and 0.1002613 from the existing sensitivity CSV and explicitly identifies the exact threshold as the observed correlation. Only that sentence changed in the generated report. All 22 scientific result files, estimation scripts, tests, methods and measurement protocol remain byte-identical to the reviewed head. Black, Python compilation and repeat-render checks passed; consulted source/configuration hashes and the archive hash still match. [Focused verification and current report hash](evidence/precision-verification.json). No statistical analysis or model call was run. The later precision correction is supported by these focused checks, not a claim that the host reviewer reviewed a new head.

Integration handoff: the original DOU owner separately owns paper integration. Use the final head, verified bundle and precision-only continuation patch recorded in the parent lane's `INTEGRATION_HANDOFF.md`; preserve this audit's selection, processing, tax-function, same-session and hypothetical-tax limitations. No welfare-input transfer is supported. The prioritized scientific next step remains the existing two-session, independently ordered and cross-format pilot with verified local tax intervals and separate monetary-choice validation. No additional statistical work, fieldwork, outreach or spending is authorized by this correction.

No raw source changes, welfare-input changes, reset consumption, automatic resets, overflow, credits purchases, paid API/remote compute, or messages to people occurred. `auto_reset.enabled=false` and the persistent no-reset sentinel remain intact. Raw microdata are not vendored. Lane exports include a git bundle, base-relative patch and a portable artifact archive; see the output report for their absolute locations and final branch head.
