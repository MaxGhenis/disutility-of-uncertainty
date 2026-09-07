# Rebuild welfare accounting and calibrate observed tax-perception error bounds

The previous pipeline interpreted private optimization losses as national social
welfare costs and attributed an unsupported 0.12 RMSE to survey evidence. This
rebuild separates exact private regret, revenue changes and social welfare under
explicit fiscal closure and social weights. It preserves feasible nonlinear
budget choices and a provenance-checked real PolicyEngine household fixture.
The 0.12 latent RMSE remains illustrative; national welfare claims are withdrawn.

The empirical addition reads the real, checksum-pinned Rees-Jones/Taubinsky
replication archive. It reproduces the three pooled Study 1 Table 1 panels and
Study 2 primary/subgroup benchmarks, checks all 4,582 raw choice rows against
native selection flags, and exports canonical observed-error intervals. For the
3,130 retained Study 2 respondents, author-convention bias bounds are +4.65 to
+14.37 percentage points and RMSE bounds are 22.57 to 29.63 points. Payoff-only
endpoint bounds, attention-selection sensitivity and assumed measurement-noise
ranges are reported separately. These quantities do not replace welfare inputs.

The mapping documents incomplete original cleaning, the 89 Study 1 local draws
outside respondents' own brackets, and an apparent reversal of Appendix A9's
reinclusion labels. Pooled ironing coefficients are not interpreted as an
identified distribution of latent types. Study 2 has one MPL per respondent;
response noise and population/tax-component transport remain unresolved. Raw
microdata are not vendored: the archive contains no explicit redistribution
licence. The committed aggregate artifact carries source and calculation hashes.

Validation completed locally:

- 258 tests pass with the actual pinned archive; one optional live PolicyEngine
  integration test skipped; 93% coverage. No new PolicyEngine computation.
- The native integration test regenerates the complete aggregate cache and
  round-trips both canonical CSV variants. Tests also cover source-flag mismatch,
  published benchmarks, payoff inequalities, FE weighting, arbitrary biased and
  correlated noise, checksum drift and preserving output on invalid input.
- Fatal flake8, Black, isort, mypy on 20 source files, citations and generated
  numerical/text/figure checks pass.
- Quarto builds HTML and a 16-page PDF; affected empirical pages 7-9 visually
  inspected. All empirical tables are generated from the checked aggregate cache.

Review scope and status:

- Initial independent host review of `b978633` found no actionable issues in the
  earlier offline adapters. It does not approve empirical ingestion.
- Independent semantic review of exact empirical commit `10e9321` found no
  actionable findings and independently reproduced the archive results, native
  flags and source-label discrepancy. It ran 23 focused tests; five requiring
  temporary-file writes were unavailable in its read-only sandbox. Exact reports
  are preserved in `calibration/reviews/`. Later CI formatting/setup fixes are
  outside that review scope and have regression tests plus passing remote CI.
- A fresh direct archive download matches the pinned checksum. A separate local
  monetary audit reconciles all 45,820 experimental tax-table entries and native
  ATR/MTR amounts (differences only at float32 rate precision).
- Both original dirty checkouts remain preserved; the rebuilt state was copied
  exactly to this isolated continuation and committed before new work.
- Live `origin/main` was fetched and remains `5d134c1`; no incoming base changes.
- Remote test and paper-build jobs pass on `9611794`. Draft preview and Pages
  deployment jobs are skipped. This PR remains draft; no publication or merge.
- A fresh runtime-only wheel matches all 24 packaged source/data files and
  reproduces model and calibration results without PolicyEngine or Matplotlib.

Next scientific step: obtain independent repeated or otherwise validated
measurements linking choice-rationalizing errors to stable, decision-relevant
beliefs; audit any Study 1 individual slope estimator for processing and income
span sensitivity before using it as a welfare input.
