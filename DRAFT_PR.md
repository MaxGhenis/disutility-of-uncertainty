# Rebuild welfare accounting and calibrate observed tax-perception error bounds

The previous pipeline interpreted private optimization losses as national social
welfare costs and attributed an unsupported 0.12 RMSE to survey evidence. This
rebuild separates exact private regret, revenue changes and social welfare under
explicit fiscal closure and social weights. It preserves feasible nonlinear
budget choices and a provenance-checked real PolicyEngine household fixture.
The 0.12 latent RMSE remains illustrative; national welfare claims are withdrawn.

The empirical adapter reads the checksum-pinned Rees-Jones/Taubinsky archive,
reproduces the three pooled Study 1 Table 1 panels and Study 2 primary/subgroup
benchmarks, and checks all 4,582 raw choice rows against native selection flags.
For the 3,130 retained Study 2 respondents, author-convention observed bias bounds
are +4.65 to +14.37 percentage points and RMSE bounds are 22.57 to 29.63 points.
Payoff-only endpoints, attention selection and assumed noise ranges remain
separate. These quantities do not replace welfare inputs.

A new Study 1 appendix integrates independently audited finite-design forecast
projections. It documents processing and income-support selection, stored-tax
nonaffinity, compatibility with an assumed dollar-error cap, and same-survey
covariance assumptions. The 555/2,470 compatibility count at a $100 cap tests an
affine forecast model jointly with that cap; it does not identify belief types
or irrationality. Conditional covariance decompositions range from a 17.58-point
common-target SD at zero error correlation to zero at the observed correlation
(approximately 0.1002613). The archive does not identify which decomposition
holds, stable latent variance, or a national welfare calibration.

The appendix package contains 18 byte-identical audit-authored code/aggregate
files from reviewed commit a5191ea, with a manifest and local-archive reproduction
command. Raw/canonical microdata, original DO files and source PDFs are excluded;
no redistribution licence was established. All Study 2 results, existing welfare
parameters/tables and figures are byte-identical to the previously delivered PR
head 8e05267. The only new results field is separate `study1_evidence`.

Validation:

- 267 tests pass with the pinned archive; one optional live PolicyEngine test is
  skipped. Nine new integration tests cover provenance, exact cohort selection,
  units, the covariance equation/threshold and unchanged welfare/Study 2 outputs.
- The packaged native reproduction reproduces all ten included aggregate files
  byte for byte. Lint, formatting, mypy, citations and generated-result checks pass.
- HTML and a 20-page PDF render; affected pages 7 and 16-20 are visually checked.
  Tables and inline numbers come from the checked aggregate cache.
- A fresh runtime-only wheel matches all 26 packaged source/data files and
  reproduces complete results without PolicyEngine or Matplotlib.

Review scope:

- Earlier clean reviews cover b978633 (offline adapters) and 10e9321 (native
  empirical integration). Later CI setup/display fixes have local and remote tests.
- The separate Study 1 audit is independently clean at a5191ea: 28 tests, 36 files
  reproduced exactly, independent native/LP/covariance checks. Its precision-only
  report correction 935ed77 changes none of the included code or aggregates.
- The **new paper/importer integration awaits focused independent review** at
  09a5685. `STUDY1-REVIEW-READY.md` records the exact head/diff, inherited evidence,
  new review scope and validation artifacts. No nested reviewer was launched.

Both dirty original checkouts remain preserved. The new isolated continuation
starts at verified PR head 8e05267; a fresh fetch confirms main remains 5d134c1.
This remains a draft; publication/deployment jobs are disabled for drafts and no
merge is authorized. No paid compute, reset, source redistribution or live
PolicyEngine computation was used for this integration.

The scientific next step is independent measurement that supports a stable,
decision-relevant belief target and population/tax-component transport. Neither
average ironing nor within-survey covariance alone identifies that calibration.
