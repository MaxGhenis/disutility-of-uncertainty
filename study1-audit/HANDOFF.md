# Study 1 feasibility audit handoff

**Completed:** an independent, artifact-only empirical audit of Alex Rees-Jones and Dmitry Taubinsky's *Measuring “Schmeduling”* (2020). The archive permits observed forecast-slope estimation and conditional sensitivity analysis. Stable individual MTR beliefs and their latent variance are not separately identified.

The [methods report](REPORT.md) contains primary-source links and quantitative tables. [METHODS.md](METHODS.md) derives the estimands and bounds; [MEASUREMENT_PROTOCOL.md](MEASUREMENT_PROTOCOL.md) specifies the next feasible experiment. [README.md](README.md) documents reproduction.

Key findings:

- All three pooled Table 1 regressions and all 484 Appendix A5–A8 cells reproduce. Available identified individual gammas match within 0.000004; these are heuristic coefficients, not repeated MTR measurements.
- 700 people have only two native local forecasts. Own-income pairs span a median $502. Their variance is dominated by a few respondents; direct difference arithmetic independently agrees with the general OLS code.
- Nominal bracket matching leaves 13 respondents with nonaffine stored tax liabilities. Phaseout arithmetic explains the departures, but a complete tax-function certification remains unavailable.
- Only 555/2,470 people with at least four own-bracket points, a $5,000 span and observed affine tax values can fit any affine belief schedule within $100 per answer. Median minimum cap: $693.29.
- Local split covariance can be explained by error correlation of 0.1003 with zero common latent variance. There are no independent repeated waves; the retained individual-estimates file attaches parameters to existing forecasts.
- 958 of 1,501 main/pre-winsor forecast differences are solely float32 conversion; 543 exceed that conversion. Dispersion remains sensitive to source processing and income-span selection.

Branch: `audit/study1-feasibility-20260907`, isolated from locally fetched `origin/main` at `5d134c14630613ff32819abe99ad5109b65b07a5`. Only `PROGRESS.md` and `study1-audit/` differ from that base. The completed PR3 checkout remains clean at `8e052674594673d1090bfb9aedf1086566500c90`. No PR, publication or merge was made. A live base fetch failed because `github.com` could not resolve in the sandbox.

Validation: 28 analytical/adversarial/native-data tests pass, direct source-field arithmetic checks pass, and generated aggregate/report files reproduce byte-for-byte. The final machine-readable count and hashes are in [reproduction evidence](evidence/reproduction-verification.json); source/config preservation is in [preservation evidence](evidence/preservation-verification.json). Formatting, compilation and local links were checked.

Independent review is **not complete**. One bounded Subfleet review of `d1ea8d0e49a44fcd717b3be361e2dfc53339e3ad` on the pinned Axiom subscription lane failed before inference because its Codex state database was read-only and app-server initialization was denied. No findings or review approval were produced. [Exact limitation and retained request](evidence/REVIEW_STATUS.md). Later source-arithmetic verification and delivery documentation were not reviewed either.

Next scientific step: a two-session, independently ordered and cross-format pilot with verified local tax intervals and separate monetary-choice validation. Recovery of missing author cleaning/liability-generation code would close provenance gaps but cannot supply absent repeated measurements. Before external scientific reliance, complete the saved bounded review in a working authorized subscription runtime. No fieldwork, outreach or spending is authorized by this handoff.

No raw source changes, welfare-input changes, reset consumption, automatic resets, overflow, credits purchases, paid API/remote compute, or messages to people occurred. `auto_reset.enabled=false` and the persistent no-reset sentinel remain intact. Raw microdata are not vendored. Lane exports include a git bundle, base-relative patch and a portable artifact archive; see the output report for their absolute locations and final branch head.
