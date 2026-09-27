# Independent host review: initial signed-error milestone

**Scoped verdict: no actionable findings in the reviewed offline milestone.**

Reviewed commit: `b9786339f636f5c1f9c510b18610fe6c4dcb7036`, branch `sprint/signed-error-calibration-20260907`, in `/Users/maxghenis/disutility-of-uncertainty-calibration-20260907`. This verdict applies only to that revision. The newly resumed empirical-ingestion work and subsequent commits require their own review. The earlier disconnected model reviewer supplies no approval and is not counted here.

## Scope and conclusions

I inspected the actual added `analysis/signed_errors.py` and `analysis/tax_forecasts.py`, their 51 focused tests, canonical schemas and fixtures, source manifest, identification protocol, new paper chapter, and handoff claims. I compared the implementation against the coordinator's earlier scientific warnings and the preserved welfare-accounting base.

- Signed moments consistently use equal respondent mass divided across that respondent's observations. Bias, variance, RMSE and MAE have their stated interpretations. Between/within variance decomposition is descriptive, with no unsupported measurement-error interpretation.
- Interval bias, second-moment and MAE bounds are marginal bounds; SD bounds are correctly qualified as outer bounds. Classical and nonclassical noise bounds state their identifying assumptions, and component-error bounds allow cancellation.
- The local-slope adapter separates individual signed slope errors from pooled fixed-effects scaling. Its tax-variation weighting agrees with an independently fitted explicit-dummy regression. True-tax linearity checks and span/exclusion diagnostics are present; the documentation correctly notes that two-point data cannot certify the absence of a kink or cliff.
- MPL inequalities have the correct direction, permit ties, preserve negative endpoints, require explicit finite support for open-end bins, and reject contradictory choices. Support, native-mapping status and source exclusions are carried in diagnostics/provenance.
- The protocol corrects the earlier mixture SD/RMSE signs, interior maximum, and incorrect unweighted regression identity. A two-type mixture remains a structural assumption; no individual latent distribution is inferred from average fit. Neither it nor the broader household-net-income fixture is used as empirical federal-tax calibration.
- Input CSV hashes, required scope/unit fields, duplicate/nonfinite/interval validation, adapter hashes, synthetic/observed status and staged instrument-output validation provide an auditable canonical boundary. The documents explicitly distinguish hash integrity from source authenticity and verified native mapping.

## Checks executed on the reviewed revision

1. `python -m pytest tests/test_signed_errors.py tests/test_tax_forecasts.py -q -p no:cacheprovider --no-cov`: **51 passed**. These include corrupted inputs, unsupported schemas/units, duplicate observations, invalid settings, explicit exclusions/support, and preserving prior output on invalid instrument metadata.
2. Independently enumerated **8,100 feasible interval vectors** across 100 generated unequal-task-count samples. All point bias/MSE/RMSE/MAE/SD values lay within their corresponding calculated marginal or outer bounds.
3. Independently fit **50 pooled regressions using explicit respondent dummy columns** with unequal respondent draw counts and varied positive/negative true slopes. Their coefficients matched `pooled_fe_scale`.
4. Regenerated the committed synthetic report in memory from its hashed canonical CSV/manifest. It matched `calibration/examples/synthetic-report.json` exactly.
5. `git diff --check` passed. The new milestone does not change the retained welfare-model, live-household adapter or pipeline formulas relative to the preserved rebuilt base.
6. Checked the article's Table 1/local-regression description and footnote 28 against the [primary article](https://alexreesjones.github.io/papers/Measuring%20Schmeduling.pdf). The new paper's 0.81 coefficient, 0.043 standard error, distinction from individual RMSE, and explicit MPL endpoint convention are consistent with those passages. This was a targeted check, not a replication or exhaustive reference audit.

## Limits of this verdict

All committed calibration examples at this revision are explicitly synthetic. Native archive fields, source cleaning, empirical moments, licence, and a decision-relevant latent error distribution remain unverified here. Source authentication, benchmark replication, sensitivity to cleaning and task spans, and population/tax-component transport must be reviewed when actual data are integrated. The current paper retains the illustrative 0.12 RMSE and makes no new national welfare estimate.

I did not rerun the optional live PolicyEngine calculation, whole paper render, whole 239-test suite, or previously reviewed welfare formulas; their prior reported checks are not new independent verification by this review. This is a clean review of the bounded offline adapter/identification change, not publication, merge, or empirical-calibration approval. No implementation files were edited, and no commit, push, publication or reset was performed.
