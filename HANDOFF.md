# Empirical calibration handoff

## State

Validated draft PR https://github.com/MaxGhenis/disutility-of-uncertainty/pull/3
on `sprint/signed-error-calibration-20260907` in
`/Users/maxghenis/disutility-of-uncertainty-calibration-20260907`. Exact empirical
review target is `10e93217d4e49e80c743f27bc6542e02b7ef4411`; initial clean host
review covers only `b9786339f636f5c1f9c510b18610fe6c4dcb7036`.
The 0.12 latent RMSE remains illustrative. Observed experimental interval
calibration is implemented and validated; no national welfare claim is made.

## Done

- Entire validated September 5 rebuild preserved on a reviewable isolated branch.
  Both original dirty checkouts remain intact; lane `preservation/` has original
  binary diffs, untracked archives and per-file hashes.
- Canonical signed-error and instrument schemas; observed moments, respondent
  bootstrap, interval bounds and explicit noise/component sensitivity.
- Native checksum-pinned RJT ZIP reader, raw-choice/selection checks, Study 1
  pooled and Study 2 OLS benchmark reproduction, endpoint and attention variants.
- Real aggregate cache and generated paper tables. Primary observed bias bounds
  +4.65 to +14.37 pp; RMSE bounds 22.57 to 29.63 pp under author support.
- `calibration/NATIVE_MAPPING.md` records field meanings, exact filters, omitted
  original cleaning, source-label discrepancy and data/licence limitations.
- 258 tests passed including actual archive integration; one optional live PE
  skip; lint/types and generated-result/citation checks pass. Paper renders to
  16 pages, with empirical pages inspected.

## Review and delivery status

- Initial b978633 review and empirical 10e9321 review both found no actionable
  findings in their exact scopes. Reports are committed in `calibration/reviews/`.
  The empirical reviewer independently reproduced the archive and ran 23 focused
  tests; five temporary-file-dependent tests were deselected in its read-only
  sandbox. The implementation lane ran all tests, including those five.
- Later commit 9611794 fixes signed-zero display and authenticates the TinyTeX
  release lookup. It changes no empirical estimator or welfare formula; local
  regression tests and remote test/paper jobs pass. It is outside 10e9321 review.
- PR #3 remains draft. Both deployment jobs are skipped. Live base was verified
  at 5d134c14630613ff32819abe99ad5109b65b07a5; no incoming changes required merging.
- Fresh direct archive download matches the source-lane copy exactly. Local
  `source-evidence/verify-experimental-taxes.py` independently reconciles all
  45,820 native tax-table entries and assigned ATR/MTR amounts.
- Both original dirty checkouts still match their snapshots (50/72 files and
  statuses), with both reset controls intact. No new live PE or paid computation.

## Remaining scientific work

The source lane's final `identification.md` had not arrived at this checkpoint;
its source manifest and coordinator corrections were inspected. Consult the
final memo when present, corroborating any new claims against its evidence.
`identification-unreviewed.md` remains unvalidated. Do not edit that lane.

A strictly local Study 1 slope calibration needs its own defined estimand and
processing/span audit. A preliminary read-only probe found that nominal bracket
matching does not guarantee an affine true-tax schedule and that short spans
can dominate dispersion. Those exploratory values are not adopted as parameters
or published results. Use the canonical adapter's linearity safeguards and
explicit sample auditing; do not simply apply the source local flag.

## Reproduction

See `REPRODUCING.md` and `calibration/NATIVE_MAPPING.md`. Local pinned archive:
`/Users/maxghenis/capacity-sprint-20260907/disutility/source-evidence/Schmeduling_Replication_Code.zip`.
Canonical author/payoff CSVs, manifests and reports are in lane `empirical/`.
They are local review artifacts, not redistributed in the Git repository.

Set `RJT_ARCHIVE` to that ZIP when running `tests/test_rjt_replication.py` to
execute real-data checks. Without it, default tests validate mapping invariants
and cache integrity; they do not claim a fresh microdata replication.
`make replicate check-results check-citations` regenerates the paper from the
verified aggregate cache. It never substitutes empirical moments for beliefs.

## Scientific next step

A latent-error calibration still requires a credible behavioral measurement
model and population/tax-component coverage. A single experimental MPL or pooled
ironing coefficient cannot identify individual stable belief variance. Study 1
individual slopes also need cleaning, within-bracket and income-span sensitivity;
small dollar-response errors can be amplified by short distances. Keep observed
bounds and assumed noise limits separate from these unresolved parameters.

No reset, paid overflow/API/remote compute, publication or merge. Stop launching
new work at 21:00 America/New_York and checkpoint safe in-flight milestones.
