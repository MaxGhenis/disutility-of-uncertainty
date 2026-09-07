# Empirical calibration handoff

## State

Active continuation on `sprint/signed-error-calibration-20260907` in
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
- 257 tests passed including actual archive integration; one optional live PE
  skip; lint/types and generated-result/citation checks pass. Paper renders to
  16 pages, with empirical pages inspected.

## Pending

- Bounded empirical review of exact 10e9321; integrate actionable file/line
  findings and preserve the original reviewed evidence. Claude review attempts
  hit subscription limits; pinned Axiom Codex is reviewing the same scope.
  Do not relaunch the old disconnected reviewer PID 12571 (root killed it).
- Draft PR creation and remote check status, followed by updated artifact bundle,
  wheel, paper, final report and preservation verification.
- Final source-lane identification memo, when available, may refine caveats;
  `identification-unreviewed.md` is not validated evidence. Research files remain
  read-only to this implementation lane.

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
