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

## Next

1. Validate and commit the preserved rebuild.
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
