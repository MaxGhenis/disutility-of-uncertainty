Review status: COMPLETE
Review severity: COMMENT
Still-open critical count: 0
Confirmed critical count: 0
Confirmed noncritical findings: 1 (P2, DOU-STUDY1-001)

# Independent Study 1 integration review

Exact integration target: `09a5685bef8e614ed77f8878426efd347727de12`.
Prior delivered head: `8e052674594673d1090bfb9aedf1086566500c90`.
Completed 2026-09-07, approximately 20:06 America/New_York.

The current frozen data, generated appendix values/math and rendered qualifications reconcile. **One actionable provenance-validation defect remains in the new importer.** This is a focused integration review; it inherits the audited science at `a5191ea9f81fd414d9fbf547995dcb31341aa875` and does not repeat or expand that scientific approval. Later delivery/handoff commits, including the owner's `81bb5e5...` checkout, are outside the exact target reviewed here.

## DOU-STUDY1-001 — P2: anchor the manifest and cache to the reviewed evidence

File: `src/taxuncertainty/analysis/study1_evidence.py:26-42` and `:212-225`.

`verify_bundle` checks only the file entries that a supplied manifest chooses to list. `build_evidence` then consumes a fixed set of aggregate files independently of that inventory. Neither the manifest's full reviewed identity nor its original source-path mappings are pinned by the verifier. The installed cache reader likewise accepts a self-recomputed checksum with unchanged audit/archive labels.

Three independent aggregate-only reproductions demonstrate the gap:

1. Delete `results/selection.csv` from the manifest inventory, then change the exact screened cohort's `sd_error` from `0.450752035248` to `0.123`. Both `verify_bundle` and `build_evidence` succeed, retaining audit attribution `a5191ea...`. The real `paper_artifacts` function then renders **12.30 pp instead of 45.08 pp** under that attribution.
2. Change the manifest's original `source_path` for selection to `never-reviewed/selection.csv`, keeping every frozen file unchanged. The importer accepts and republishes that source attribution.
3. Change the cache's selected scientific value to `0.123`, recompute its own `artifact_sha256`, and keep the original provenance/scope flags. `load_evidence` accepts it. A self-checksum establishes internal consistency, not correspondence to the named reviewed audit.

These are validation failures, not allegations that the delivered numbers are wrong or that the welfare parameter was replaced. The recommended fix is to pin the exact reviewed manifest identity/required inventory and source mappings, and anchor the installed aggregate-cache identity or provide equivalent validation against trusted frozen inputs. A rewritten checksum should require a deliberate reviewed source/version change rather than retaining the old attribution. Add regressions for an omitted consumed file, changed original source mapping and a self-rehashed changed cache.

Runnable reproducer: `study1-integration/independent-importer-repro-host.py`.
Results: `study1-integration/independent-importer-repro-host.json`.
All mutations were confined to disposable aggregate-only copies. Owner source and raw archives were untouched.

## Independent checks that passed

- **21 focused importer/pipeline tests passed** in 5.03 seconds. The runner blocked socket operations and actual PolicyEngine/model-package execution. Live policy tests were not enabled.
- The normal **aggregate importer `--check` passed**, and the **pipeline `--check` passed**, comparing numerical results, generated paper text and figure provenance.
- All **18 frozen files** match their manifest lengths/hashes and their actual original Git blobs in both `a5191ea...` and precision-only `935ed77...`. The copied independent-review report matches its specified SHA-256. These checks validate the delivered package's correspondence to the inherited review despite the malformed-input gate above.
- Independently reconciled the **six selected cohorts** to exact source CSV criteria and source values. Verified all **18 numeric selection-table cells**, **20 affine-table cells**, and **six covariance-table cells** with their source values, selection and formatting.
- Confirmed slope/SD conversion by **100** and covariance/SE conversion by **10,000**. Descriptive moments retain denominator **N**; the split covariance retains **N−1**.
- Independently checked all **five retained covariance moment equations** and square-root conversions. Maximum residual was `8.9064e-14` in squared-fraction units. The exact zero-target-variance correlation comes from the observed moments, approximately `0.1002613`; literal `0.100000` does not satisfy that zero-variance identity. The displayed midpoint approximately `0.0501306` and implied SD `12.76` pp follow the cache.
- Reviewed the new appendix mathematics against the inherited audited definitions: equal-income constraints and pairwise interval intersection; the minimum feasible affine cap; the explicit relative endpoint tolerance; finite-design projection-error bound; and the same-target/orthogonality/covariance assumptions. No new mathematical error was found.
- Every preexisting results field equals the prior delivered head after removing only the model-source fingerprint; `study1_evidence` is the sole new field. Study 2 cache/analysis, household fixture, welfare parameters, five existing tables and both welfare plots are byte-identical. **Illustrative latent RMSE remains 0.12.**
- Independently compared **26 installed wheel files**—including the evidence cache and importer—to the exact target's source bytes. The repository's new tracked additions include **no raw DTA, original DO, ZIP or PDF files**. The new wrapper stages the frozen audit/code in a temporary directory, takes a separately supplied local archive and compares ten included aggregate outputs. Its audited source reader checks the archive hash and reads source text/data without executing original archive code.
- Reviewed supplied PDF pages **7 and 16–20** visually, and extracted pages 16–20 from the delivered PDF. The cross-reference resolves; all three appendix tables, formulas, numeric moment substitutions and bibliography are legible without clipping or unresolved shortcode content. PDF SHA-256: `9a70517d42b0ced041019ad412204a31ae4c6024f764bf306416792ad277725d`.
- The rendered appendix preserves the material qualifications: selection/processing, the $0.05 observed-point screen, missing original cleaning/liability-generation code, 555/2470 as a joint affine-model/error-cap compatibility check, no stable-type or irrationality inference, hypothetical federal coverage, no independent waves, same-target/error restrictions, and no latent or national welfare calibration.
- Verified **all 123 tracked reviewer files** against exact target Git blobs. The reviewer checkout stayed clean and was removed normally. `git diff --check` passed; no owner edits occurred.

## Limits and inherited evidence

The original raw-data mapping, pooled coefficients/clustered SEs, native phaseout identities, explicit covariance jackknife, 2,470 affine minima/LP checks and 484 published grid cells are inherited from the supplied independent audit at a5191ea. I verified the copied files against that exact commit, but did not rerun its full raw-data scientific campaign. I read the owner's successful ten-aggregate native-wrapper reproduction evidence; I did not repeat native extraction/reproduction here. The broad 267-test suite and a fresh Quarto render were also not repeated.

The PDF was reviewed as the supplied exact-integration render artifact; later source/render changes need a scoped delta check. No subsequent PR/CI/delivery claim is approved by this report. No new model or human collection, PolicyEngine calculation, raw redistribution, publication, push, merge, reset redemption or paid-capacity action was performed.

## Evidence artifacts

Under `study1-integration/`:

- `independent-tests-host.log` / `independent-offline-tests-host.py`
- `independent-importer-repro-host.py` / `independent-importer-repro-host.json`
- `independent-integration-checks-host.py` / `independent-integration-checks-host.json` / `independent-integration-checks-host.log`
- `independent-appendix-text-host.txt`
- `paper-inspection/page-07.png`, `page-16.png` through `page-20.png`
