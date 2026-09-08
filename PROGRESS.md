# Capacity sprint progress

## State

Repairing confirmed importer provenance finding DOU-STUDY1-001 in a fresh
isolated continuation `sprint/study1-provenance-repair-20260907`, based on live
verified PR #3 head `98bc1b77d179d024daba8e2fba66a0f5ae571ea0`. Fresh fetch and
PR checks confirm main remains `5d134c14630613ff32819abe99ad5109b65b07a5`.
The prior continuations and dirty originals are untouched. The frozen scientific
artifacts are correct and will remain byte-identical; only provenance enforcement
and its regressions change. Safe repair target: 20:40 ET; no new work after 21:00.

## Done

- Committed a reproducible, qualified Study 1 appendix and frozen aggregate/code
  package. Exact integration review target: 09a5685; review-ready file committed.
- 267 tests passed; ten native aggregates reproduce exactly; lint/type/generated
  checks pass; 26 installed-wheel files match; affected PDF pages inspected.
- Draft PR #3 updated normally. Remote test and paper-build jobs pass at 81bb5e5;
  preview/Pages deployment skipped. No publication or merge.
- Preserved both dirty originals (50 and 72 file states/status/head/branch) and
  the clean prior continuation at 8e05267. Reset configuration hashes unchanged.
- Durable exact diff, logs, paper, wheel and final report saved in the lane.

## Next

1. Focused host review of exact 09a5685, using STUDY1-REVIEW-READY.md. No new
   integration approval is claimed; later commits contain handoff metadata only.
2. Any later latent calibration requires independent measurement, noise/covariance
   assumptions and population/tax-component coverage. Keep 0.12 illustrative.

## Initial preservation (historical)

- Read global/project instructions, REBUILD_VALIDATION.md and REVIEW.md.
- Inspected status, branches and remotes of both dirty checkouts.
- Saved binary diffs, untracked archives and SHA256 manifests under
  `/Users/maxghenis/capacity-sprint-20260907/disutility/preservation/`.
- Reconstructed the exact rebuild in this worktree and verified every preserved
  file hash before adding this progress file.
- Base: locally recorded `origin/main` at
  `5d134c14630613ff32819abe99ad5109b65b07a5`. A fresh fetch failed because the
  terminal cannot resolve github.com; no claim of a freshly verified base.
- Prior validation: 188 passing tests and one opt-in integration skip; this sprint
  will rerun the meaningful checks in the isolated worktree.

- Locked Python 3.13.9 environment installed offline; pinned Makefile setup to
  that tested interpreter (the machine default is 3.14).
- Corrected the legacy LLM note's unsupported .12 attribution/lower-bound claim.
- Disabled automated Netlify preview publication for draft PRs.

## Initial next steps (historical)

1. Preserved rebuild committed as `4f2d46a`; isolated default suite: 188 passed,
   one opt-in PolicyEngine integration skip.
2. Inspect public Rees-Jones/Taubinsky replication data and the independent source
   memo; implement reproducible signed moments with explicit sample/tax scope.
3. Separate observed error from latent beliefs; test identification assumptions
   and sensitivity bounds when the latter cannot be point identified.
4. Regenerate and inspect the paper; prepare a qualified draft PR and final
   handoff at `/Users/maxghenis/capacity-sprint-20260907/disutility/result.md`.

## Constraints

No resets, paid overflow, paid API/compute jobs, publication, merge or messages to
people. Preserve `auto_reset.enabled=false` and the sprint no-reset marker. Stop
launching new work at 21:00 America/New_York on September 7, 2026.

## Signed-moment checkpoint

- Added `analysis/signed_errors.py`: checksum-validated canonical CSV adapter,
  signed descriptive moments, equal respondent mass, cluster bootstrap, interval
  identification bounds and explicit classical/nonclassical noise sensitivity.
- Added a labelled synthetic example; it is a software demonstration only.
- 37 targeted tests pass, covering moment identities, unequal task counts,
  respondent clustering, interval bounds, impossible noise assumptions, component
  cancellation, unit/schema checks and byte-level integrity. Mypy passes.
- Primary paper inspected through the web tool. Author-linked replication ZIP
  located, but terminal download failed with `curl: (6) Could not resolve host:
  www.dropbox.com`. Archive contents and licensing are still unverified.
- Consulted the independent Claude memo in `research-disutility/retry-result.md`.
  It also did not inspect the archive. Its structural-mixture suggestions require
  additional assumptions and corrections (absolute wedge for SD; interior share
  maximizes SD; Table 1 coefficient is design-weighted). Do not substitute them
  for observed signed-error calibration.
- Next: source-instrument adapters, mapping/selection audit, paper identification
  section and one bounded independent semantic review.

## Instrument adapter checkpoint

- Added `analysis/tax_forecasts.py` and canonical JSON examples for local liability
  forecasts and MPL choices. No native archive field names are guessed.
- Local slopes report income leverage, exclusion counts, conditional response-noise
  diagnostics and the separate design-weighted pooled FE coefficient.
- MPL inequalities retain intervals and explicitly record optional support; tests
  reproduce the article's interior example and footnote-28 endpoint convention.
- Added source/access manifest and `calibration/IDENTIFICATION.md`, separating
  primary evidence, proposed estimands, assumptions and the incomplete native-data
  mapping. No empirical microdata moments or national welfare totals are claimed.
- Validation: 238 passed, 1 opt-in skip; fatal lint, Black, isort, mypy (19 source
  files) and generated-results checks pass. Both canonical example CLIs executed.
- One bounded semantic review requested. Claude could not start (enrolled
  credential unavailable); the same review is being attempted on the authorized
  pinned Axiom Codex lane. No reset or overflow.
- Next: integrate the identification protocol into the rendered paper and close
  actionable review findings, then package a draft-PR handoff.

## Paper checkpoint

- Integrated the signed-error identification protocol into the paper, abstract,
  conclusion and reproduction guide. No illustrative belief values were replaced.
- `make replicate check-results check-citations` passes. Quarto generated a 15-page
  PDF and HTML; the new identification pages (7-8) were visually inspected and
  show no clipping or equation/layout defects.
- Built a wheel offline and installed it in a separate runtime-only environment.
- Independent review is blocked, not approved: Claude had no accessible enrolled
  credential; the pinned Codex attempt cannot resolve chatgpt.com. Attempted
  cancellation failed with Operation not permitted for PID 12571. Exact host-side
  termination handoff: lane artifact `REVIEW_STOP_BLOCKED.md`.
- GitHub CLI also cannot connect to api.github.com. Prepare local draft-PR body,
  Git bundle and patch; do not claim a remote PR exists.
- Next: finish runtime-only smoke checks, harden numerical/provenance edge cases
  if concrete failures are found, and record final validation/preservation.

## Numerical and output-integrity fixes

Two concrete local checks found and reproduced defects in the new adapter:

- Errors at `1e8 +/- 1` had true SD 1, but subtracting large raw squared moments
  returned SD 0 in the interval and bootstrap paths. Centering before variance
  calculations restores translation invariance; a regression test covers it.
- Invalid manifest metadata raised after writing rates/manifest files, leaving a
  misleading partial output. Instrument outputs now validate and serialize in
  temporary staging before touching the requested directory. A regression test
  verifies both preservation of existing results and absence of fresh output.

Also retained upstream transformation descriptions and added the calibration
calculation-source hash to reports. All 51 targeted adapter tests and mypy pass.
These are local self-checks; no independent semantic reviewer completed.

## Final checkpoint

- Final suite: 239 passed, 1 optional integration skip, 93% coverage; all lint,
  format, type, citation and generated-result checks pass.
- Fresh runtime-only wheel smoke: 22 packaged source/data files match; full model
  results, the calibration example and stored household fixture reproduce.
- Final paper: 15-page PDF and HTML, new pages and abstract visually checked.
- Preservation recheck: all 50 original and 72 rebuild file states/statuses match
  their initial manifests; both original branches unchanged.
- `auto_reset.enabled=false`, reset block enabled, automatic expiry false; no
  reset, paid compute, publication, merge or messages to people.
- Draft-PR text in `DRAFT_PR.md`; network prevents actual push/PR. `HANDOFF.md`
  records the archive/base/review blockers and exact continuation sequence.
- Final lane export: Git bundle, patch, wheel, rendered paper, validation logs,
  artifact hashes, `REPORT.md` and requested output `result.md`.

## Host-enabled empirical continuation

- Resumed from clean `b9786339f636f5c1f9c510b18610fe6c4dcb7036`; saved exact
  reviewed commit/source fingerprints in lane `review-evidence/`.
- Fresh `git fetch origin main` succeeds and confirms base remains
  `5d134c14630613ff32819abe99ad5109b65b07a5`; no base integration is needed.
- Read coordinator corrections and source-lane progress. Real Study 1/2 archive
  data are now available. Source-lane numerical claims remain preliminary until
  independently reproduced here. Source-lane files will be read only.
- Root terminated failed reviewer PID 12571; do not relaunch it. The host review
  of b978633 is pending separately; empirical changes will need a bounded review
  of their own exact commit.
- Next: inspect native source code/data, reproduce filters and regressions,
  implement provenance-checked archive mapping, and integrate only identified
  observed interval/error quantities into the paper.

## Native empirical checkpoint

- Initial host review of exact b978633 completed with no actionable findings;
  its report and reviewed fingerprints are preserved in lane `review-evidence`.
- Independently verified the author-linked 48 MB ZIP and native README/DO files.
  Added a strict native adapter, canonical interval exports, aggregate cache,
  benchmark gates and `calibration/NATIVE_MAPPING.md`. Raw microdata stay local.
- All 4,582 Study 2 raw choice rows reproduce monotonicity, first-switch and
  endpoint flags. Published selection waterfall and primary/subgroup counts,
  Table 4/A9 primary coefficients/SEs and three pooled Study 1 panels reproduce.
- Documented the apparent A9 reintroduced-group label reversal and the 89
  Study 1 local-flagged draws outside own bracket. No latent heterogeneity
  parameter is inferred from pooled coefficients.
- Retained Study 2 author-convention observed bias bounds: +4.65 to +14.37 pp;
  RMSE: 22.57 to 29.63 pp. Payoff-only endpoint sensitivity remains separate;
  SD bounds are explicitly conservative, not claimed sharp. .12 stays illustrative.
- Native adapter tests: 16 passed with actual pinned archive, including complete
  regenerated-cache equality and both canonical CSV round-trips. Lint/types pass.
- Next: wire scoped aggregate tables into the paper, finish empirical sensitivity
  and independent review of the new exact commit, then create an authorized draft PR.

## Empirical paper checkpoint

- Wired the checked native aggregate cache into the normal pipeline and generated
  empirical benchmark, interval and noise-sensitivity tables. Observed calibration
  is explicitly separate from all welfare-model belief inputs.
- Added arbitrary-bias/covariance noise sensitivity conditional on supplied RMSE
  caps. Random feasible-vector tests verify coverage; caps are assumptions.
- Full suite with actual archive: 257 passed, one optional live PolicyEngine skip,
  93% coverage. All lint, formatting and type checks pass.
- Updated source manifest, identification protocol, abstract, conclusion and
  reproduction instructions. Raw/canonical microdata remain outside the repo.
- Quarto rendered HTML and a 16-page PDF; empirical pages 7-9 visually inspected
  without clipping or broken equations. Generated-results/citations checks pass.
- Next: obtain the empirical milestone's bounded independent review, preserve
  exact reviewed commit evidence, and prepare the live-base draft PR.

## Review and draft preparation

- Preserved exact empirical review target 10e93217d4e49e80c743f27bc6542e02b7ef4411.
- Requested one bounded semantic review. Claude subscription lanes returned hard
  limits/auth failure; submitted the same scope on authorized pinned Axiom Codex
  capacity. This is distinct from the old killed network-stuck review.
- Refetched live origin/main, unchanged at 5d134c1; GitHub authentication works.
  Draft PR text and handoff now describe the actual empirical implementation.
- Next: complete wheel verification, open the authorized draft, integrate review
  findings and preserve exact final artifacts and remote-check status.

## Draft PR and CI fixes

- Opened draft PR https://github.com/MaxGhenis/disutility-of-uncertainty/pull/3
  from freshly verified origin/main 5d134c1. Remote branch and PR head were checked.
- Installed-wheel smoke passes: all 24 source/data files match; complete model
  and calibration results reproduce without PolicyEngine or Matplotlib.
- First CI runs exposed a generated scenarios-table mismatch and an intermittent
  TinyTeX release-lookup HTTP 403. Added a regression-tested display normalization
  for negative zero cents (raw accounting unchanged) and Quarto's documented
  GH_TOKEN setup for authenticated release lookup.
- Both publication/deployment jobs are skipped on the draft. Next: confirm the
  corrected CI run and integrate pending exact-scope empirical review findings.

## Reviewed delivery checkpoint

- Exact empirical review 10e9321: no actionable findings; independent fresh
  archive reproduction, raw flags, benchmark coefficients/SEs and bounds agree.
  Reviewer executed 23 focused tests, deselecting five temporary-file tests in
  its read-only sandbox. Both scoped reports are committed in calibration/reviews.
- Final implementation validation: 258 passed, one optional live PE skip, 93%
  coverage. Lint/types/citations/generated outputs pass. Fresh installed wheel
  reproduces all results and matches 24 packaged source/data files.
- Remote test/paper jobs pass at 9611794; draft preview and Pages deployment skip.
  PR remains draft and no merge or publication occurred.
- Direct public ZIP download matches the pinned hash. Separate independent audit
  reconciles all 45,820 experimental tax-table entries and assigned ATR/MTR
  amounts, with only native float32 quantization differences in rates.
- Final PDF is 16 pages; empirical pages 7-9, abstract and coverage/results
  transition visually checked. Both dirty originals and reset controls preserved.
- Source lane final identification.md remains pending; consulted source manifest,
  native code, primary texts and coordinator corrections without adopting
  identification-unreviewed.md.
- Next scientific step: independently validated behavioral measurements and
  population/component transport; audit Study 1 slope processing and spans before
  treating any descriptive dispersion as a welfare input.

## Study 1 integration started

- Read the completed audit and independent host review of exact commit
  `a5191ea9f81fd414d9fbf547995dcb31341aa875`. That review verified native source
  mappings, pooled benchmarks, the affine-fit calculation and covariance
  sensitivity; it does not cover this integration.
- Owner's report precision correction is pending; the exact aggregate correlation
  is 0.10026128922382825. Neither 555/2470 affine-compatible forecasts nor the
  covariance sensitivity identify stable belief types or latent welfare variance.
- Next: package minimal frozen aggregates and reproducible audit code, generate a
  qualified appendix, test provenance/units/unchanged welfare inputs, render and
  inspect affected pages, and write STUDY1-REVIEW-READY.md for host review.
- No nested reviewers, raw-data redistribution, new model/API computation,
  publication or merge. The draft branch will receive a normal fast-forward update.

## Study 1 scientific integration checkpoint

- Packaged 18 byte-identical audit files from independently reviewed a5191ea:
  five audit-authored scripts, ten aggregate outputs and three dependency files.
  No raw microdata, original DO files or source PDFs are included. All included
  files also match the owner's precision-only correction commit 935ed77.
- The new temporary-directory reproduction wrapper reran the frozen native
  calculations with the pinned archive: all ten aggregate files reproduce byte
  for byte. The source lane and prior continuation remain untouched.
- Added a checksum-checked aggregate importer and separate `study1_evidence`
  results field. Nine integration tests cover source/provenance drift, exact
  cohort selection, percentage-point units, covariance decomposition, the exact
  correlation threshold and isolation from welfare inputs/Study 2 outputs.
- Full local suite: 267 passed, one optional live PE skip, 92% coverage. Lint,
  Black/isort, mypy, generated results and citations pass. No live PE computation.
- Every preexisting result equals PR head 8e05267 except the model source hash.
  Study 2 cache, household fixture, welfare inputs/tables and figures are byte
  identical. The latent RMSE stays 0.12 and no national calibration is claimed.
- Added a generated three-table appendix with selection, processing/nonaffinity,
  dollar-cap compatibility and same-survey covariance caveats. Corrected a Quarto
  inline-math shortcode rendering defect found during PDF inspection; numerical
  variables now render as numbers. HTML/PDF and affected-page inspection are
  recorded in the lane artifacts. New integration review remains pending.
- Next: freeze the exact integration head and diff in STUDY1-REVIEW-READY.md,
  update the existing draft PR normally from the live verified base, and save
  rendered artifacts, test evidence and handoff. No nested reviewer was launched.

- Artifact cleanup: excluded Quarto's transient `paper/index.tex`, which was
  staged during rendering. The final review diff contains generated Markdown/JSON
  inputs; the complete rendered PDF/HTML are preserved in the lane export.

## Review-ready delivery checkpoint

- Exact integration target and binary diff are saved with inherited/new review
  scopes; no new integration approval is claimed. A fresh installed wheel
  reproduces all results and matches 26 packaged source/data files without PE
  or Matplotlib. Final appendix and bibliography pages render correctly.
- Updated draft description and handoff to the actual final scientific scope.
  Next: normal fast-forward draft update, verify remote checks, preserve final
  artifacts/configuration and report the outstanding host-review step.

## Verified remote delivery

- PR #3 is draft at 81bb5e5 after the authorized fast-forward update; its body was
  read back and verified exactly. Both push and PR CI runs succeed, including
  test and paper-build jobs. This checkpoint changes delivery documentation only;
  implementation review target remains 09a5685.
- Final preservation checks match all 50 original and 72 rebuild file states,
  Git statuses, heads and branches. The prior continuation remains clean at
  8e05267. Both no-reset protection files match their original hashes.

## Study 1 provenance repair started

- Read the host's confirmed P2 and preserved its aggregate-only reproducer/report
  in lane `study1-repair/`. A manifest can currently omit consumed files or change
  source mappings; a self-rehashed changed cache retains the reviewed identity.
- Next: anchor the exact reviewed manifest and cache identity, add bypass
  regressions, verify unchanged science and relevant tests, and write exact
  STUDY1-REPAIR-READY.md for the same host reviewer's focused rereview.
- Final integration review is still in progress; read its final report before
  delivery. No nested review, raw-data change, reset, paid compute or publication.

## Anchored provenance repair validated

- Final host integration report is COMPLETE with one P2 (DOU-STUDY1-001), no
  other actionable finding. Its independent source/units/math/render checks pass;
  copied the exact final report into calibration/reviews/integration-09a5685.md.
- Eight new negative regressions fail on the previous implementation: omitted
  consumed files, altered source mapping, rehashed changed file, empty/expanded
  inventory, and three self-rehashed scientific/provenance cache changes.
- Anchored manifest bytes now pin all inventory/source mappings; the canonical
  aggregate digest is anchored in both builder and installed loader. One positive
  regression allows harmless cache JSON formatting changes.
- All 30 focused importer/pipeline tests and lint/type checks pass. Next: regenerate
  the source fingerprint, compare every scientific value and paper artifact,
  commit the exact repair and prepare STUDY1-REPAIR-READY.md for host rereview.
