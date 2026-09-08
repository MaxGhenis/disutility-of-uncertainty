# Study 1 provenance repair handoff

DOU-STUDY1-001 is repaired at exact `cd204c90e2ca94a2f81766cfb1e06320b76d1832`.
[STUDY1-REPAIR-READY.md](STUDY1-REPAIR-READY.md) supplies the precise diff from
98bc1b7, owner verification and scope for the same host reviewer's rereview.
That rereview is pending; no new independent repair approval is claimed.

Current isolated continuation: `sprint/study1-provenance-repair-20260907` in
`/Users/maxghenis/disutility-of-uncertainty-study1-repair-20260907`.
Current base checks: draft PR #3 head 98bc1b7, main 5d134c1. No base changes needed.

The completed integration review at 09a5685 found one P2: a manifest/cache could
rewrite its own identity while retaining reviewed-source attribution. The repair
pins the exact manifest bytes and canonical aggregate digest in code and checks
both rebuilt evidence and installed cache loads. Eight bypass regressions fail
before and pass after; one positive formatting case passes. All 30 focused tests,
lint/types, generated/citation checks and 26-file installed-wheel checks pass.
All scientific values are unchanged; 49 source/artifact paths are byte-identical.
The only rendered-output change is the model-source fingerprint on page 2.

Repair artifacts: `/Users/maxghenis/capacity-sprint-20260907/disutility/study1-repair/`.
The same reviewer should rereview only this repair. Keep original a5191ea and
09a5685 scientific/integration reviews scoped to their exact targets. Draft updates
are authorized; no publication, merge, reset, paid compute or raw-source changes.
Safe checkpoint by 20:40 ET; stop new work 21:00 ET.

## Prior integration handoff (historical)

# Study 1 integration handoff

## State

The narrow Study 1 evidence appendix is implemented and locally validated at
`09a5685bef8e614ed77f8878426efd347727de12`. Focused independent integration
review is pending; see [exact review scope](STUDY1-REVIEW-READY.md).
Existing draft: https://github.com/MaxGhenis/disutility-of-uncertainty/pull/3.
Remote PR branch: `sprint/signed-error-calibration-20260907`.
Local continuation: `sprint/study1-evidence-integration-20260907` at
`/Users/maxghenis/disutility-of-uncertainty-study1-integration-20260907`.
It starts at verified PR head 8e05267; fetched main is 5d134c1.
The previous continuation and both original dirty checkouts remain intact.
The draft was updated normally at 81bb5e5; both push and PR test/paper CI runs
succeeded and deployment stayed skipped. Later delivery-documentation commits
do not change the exact implementation review target.

## Done

- Preserved the exact independently reviewed audit a5191ea through 18 unchanged
  code/aggregate files and SHA256 manifest. All included files also match the
  precision-only report correction 935ed77. No raw microdata, original DO files
  or source PDFs are included.
- Added a separate aggregate importer/cache and three generated appendix tables.
  The paper explains selection, retained processing, observed-point true-tax
  nonaffinity, exact tolerances/units, affine-model/error-cap compatibility,
  repeated-measure assumptions, covariance sensitivity and population/tax scope.
- The 555/2470 result is not a belief-type classification or irrationality claim.
  Error correlation is unmeasured; approximately 0.1002613 is the displayed
  observed correlation, not a literal 0.100000 threshold.
- Study 2 bounds are unchanged: author-support bias +4.65 to +14.37 pp, RMSE
  22.57 to 29.63 pp. Every existing result except the model source fingerprint is
  unchanged. Welfare inputs and figures remain byte-identical; latent RMSE 0.12
  stays illustrative. No national welfare estimate is identified.
- Full suite 267 passed, one optional live PE skip, 92% coverage; final focused
  suite 21 passed. Nine integration tests are new. Lint/types/citations/generated
  checks pass. Native wrapper reproduces ten included aggregate files exactly.
- Fresh wheel: 26 packaged source/data files match, all results reproduce without
  PE or Matplotlib. HTML/PDF generated; pages 7 and 16-20 inspected. The 20-page
  PDF and full HTML tree are saved in the lane's `study1-integration/paper/`.

## Reproduce and review

[Package instructions](calibration/study1/README.md) describe an offline aggregate
check and optional pinned-archive reproduction. The source archive remains at
`/Users/maxghenis/capacity-sprint-20260907/disutility/source-evidence/Schmeduling_Replication_Code.zip`.
The source licence is unspecified; obtain/retain it separately under applicable
terms. `make generate` and `make replicate` generate paper inputs/artifacts from
checked caches, with no live PolicyEngine execution.

The inherited audit review a5191ea does not approve this integration. Its 28-test,
36-file and independent native/LP/covariance verification remains exact-scope
historical evidence. New host review should focus on the importer, units/cohorts,
appendix claims, reproduction packaging and isolation from welfare/Study 2 inputs.
No nested reviewers were launched. Durable patch, frozen head, logs, preservation
comparison and paper artifacts are in
`/Users/maxghenis/capacity-sprint-20260907/disutility/study1-integration/`.

## Next

Complete the focused host integration review against 09a5685 and fix actionable
file/line findings on this isolated continuation, preserving the exact reviewed
head. Keep draft status and reverify current base before subsequent updates.
Further scientific calibration requires independent measurements supporting a
common stable belief target, noise/covariance restrictions and population/tax
coverage. Do not infer latent variance or national welfare from these diagnostics.

No reset, paid overflow/API/remote compute, publication or merge. Stop new work
at 21:00 America/New_York on September 7 and checkpoint safe in-flight work.
