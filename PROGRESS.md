# Capacity sprint progress

## State

The validated September 5 rebuild is preserved byte-for-byte on isolated branch
`sprint/signed-error-calibration-20260907`. Both preexisting dirty checkouts remain
intact. This is a conditional modeling note, not a national welfare estimate.
The 0.12 latent error RMSE remains illustrative.

## Done

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

## Next

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
