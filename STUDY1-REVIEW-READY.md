# Study 1 integration ready for focused host review

Exact integration target: `09a5685bef8e614ed77f8878426efd347727de12`.
Prior delivered PR #3 head: `8e052674594673d1090bfb9aedf1086566500c90`.
Review diff: `git diff 8e052674594673d1090bfb9aedf1086566500c90 09a5685bef8e614ed77f8878426efd347727de12`.
Binary diff SHA256: `e5643891668104ff049304a83ecf1547a6f6ff26cf74b887140ce6d3e575190f`.
Branch: `sprint/study1-evidence-integration-20260907`.
Isolated worktree: `/Users/maxghenis/disutility-of-uncertainty-study1-integration-20260907`.
Existing draft: https://github.com/MaxGhenis/disutility-of-uncertainty/pull/3

The integration is locally validated and **awaits its own focused independent
review**. No nested reviewer was launched. Later handoff/PR-description commits
are outside this exact implementation target; they must not be represented as
independently reviewed code.

## Inherited evidence, not a new review of this diff

- Independent host review is clean at audit commit
  `a5191ea9f81fd414d9fbf547995dcb31341aa875`. Verbatim report:
  `calibration/reviews/study1-a5191ea.md`; SHA256
  `58ba502e1c09bc567a1eb19ba2d96d48bf0eccf09ef7d0545b969fa5f7579178`.
- That reviewer ran 28 tests and reproduced 36 files byte for byte, independently
  checked source mappings, selection, three pooled coefficients/cluster SEs,
  stored-tax phaseout identities, explicit delete-one covariance jackknife,
  all 2,470 affine minima with an independent LP dual and 1,000 synthetic cases.
  It verified all 484 printed grid cells, which this appendix does not interpret
  as latent types. Those inherited checks need not be repeated broadly here.
- The audit owner's precision-only report commit is
  `935ed77d4a7afe4ed721f1ff6dd147254a9ff4bf`. All 18 included frozen files also
  match this corrected commit. Exact source results and code remain a5191ea;
  the appendix uses the observed correlation approximately 0.1002613, never
  treating literal 0.100000 as the exact zero-variance threshold.
- Prior DOU reviews b978633 and 10e9321 retain their original scopes. They do not
  approve this importer, appendix or package.

## New verification scope

Review primarily:

1. `src/taxuncertainty/analysis/study1_evidence.py`: strict aggregate-file hashes,
   exact cohort selection, fraction units, cache attribution and no latent-input
   replacement. `calibration/study1/manifest.json` maps all 18 frozen files back
   to exact reviewed paths/hashes. No raw data/DO/PDF is included.
2. `src/taxuncertainty/pipeline.py` and `tests/test_study1_evidence.py`: source-driven
   tables/inline values, 100 versus 10,000 conversions, denominator N versus N-1,
   correct covariance moment equation and unchanged Study 2/welfare results.
3. `paper/chapters/study1_appendix.md` and the short identification cross-reference:
   selection/processing and observed-point nonaffinity caveats; exact $0.05
   screening and slope endpoint tolerance; 555/2470 as a joint affine-model/cap
   compatibility check, never stable types or irrationality; same-target and
   error orthogonality/covariance assumptions; hypothetical federal coverage;
   illustrative latent RMSE 0.12 and no national calibration.
4. `calibration/study1/reproduce.py` and README: minimal pinned aggregate/code
   package, local raw archive only, temporary outputs, no source redistribution.
   Frozen audit scripts are byte-identical inherited code, not new estimators.
5. Generated appendix tables and rendered PDF pages 16-19 (plus page 7 reference
   and page 20 bibliography). Inspect that displayed numbers and mathematics
   follow the cache and preserve scientific qualifications.

## Completed implementation validation

- Native pinned-archive wrapper: all 10 included aggregate results reproduced
  byte for byte, independently rerun in this integration environment.
- Full suite: 267 passed, one optional live PolicyEngine skip, 92% coverage.
  Final focused pipeline/importer suite: 21 passed. Nine tests are new.
- Fatal flake8, Black, isort, mypy (21 modules), generated results and citations
  pass. Aggregate importer `--check` passes. `git diff --check` passes for the
  final target diff; transient Quarto compilation source is excluded.
- All existing results equal prior PR head except model source fingerprint.
  Study 2 cache, household fixture, welfare parameters/tables and plots are byte
  identical. `study1_evidence` is the only new results field.
- Quarto HTML and 20-page PDF generated; pages 7 and 16-20 visually inspected.
  Fixed and rerendered an inline-math shortcode defect; claim/placeholder checks
  confirm actual covariance numbers render. No clipping or equation defects remain.

Evidence: `/Users/maxghenis/capacity-sprint-20260907/disutility/study1-integration/`
contains the exact target, binary patch, diff stat, logs, preserved-results
comparison and complete HTML/PDF artifacts. The PDF is `paper/index.pdf`.
The source archive remains local outside Git, SHA256
`c578518776c9cd97cc0bcf340558a9574ed2088cfeb5d1b610274e5d7ab48b15`.

Please report actionable findings with file/line references against the exact
integration target. The remaining scientific blocker is latent measurement and
population/component transport, not raw-data access. No new model, human-data or
PolicyEngine computation is requested. No publication, merge or nested review.
