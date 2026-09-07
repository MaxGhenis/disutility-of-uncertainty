# Rebuild welfare accounting and add signed-error identification

The previous pipeline interpreted private optimization losses as national social
welfare costs and attributed an unsupported 0.12 RMSE to survey evidence. This
change separates exact private regret, government revenue changes and social
welfare under explicit fiscal closure and social weights. The 0.12 latent RMSE
remains illustrative, and the unsupported national estimates are withdrawn.

The rebuild also preserves explicit nonlinear budget choices and a
provenance-validated real PolicyEngine household fixture. Results, tables,
figures and inline paper values are generated from the same pipeline.

The new calibration layer provides checksum-validated canonical data schemas,
signed moments, equal respondent mass, cluster bootstrap, local tax-forecast
slopes, MPL perception intervals, and conditional measurement-error and
tax-component bounds. It distinguishes the source's pooled fixed-effects scaling
coefficient from individual signed errors. The paper now explains these
identification limits and the remaining empirical work.

All bundled calibration examples are explicitly synthetic. Native field mapping,
cleaning and licensing for the author-linked Rees-Jones/Taubinsky archive remain
unverified because this execution environment cannot download it. No empirical
microdata calibration, latent behavioral distribution or national welfare
estimate is claimed.

Validation:

- 239 tests pass; one opt-in live PolicyEngine integration test skipped; 93%
  overall coverage. Existing household fixture validated offline.
- Fatal flake8, Black, isort, mypy on 19 source files, citation checks and
  `git diff --check` pass.
- Generated-results checks pass; Quarto builds HTML and a 15-page PDF. New paper
  pages inspected visually.
- Fresh runtime-only wheel installation matches all 22 packaged source/data
  files and reproduces model results and the calibration example without
  PolicyEngine or Matplotlib.
- Regression tests cover response-noise amplification, design weighting,
  interval endpoints, component cancellation, large-bias variance stability and
  preservation of existing output on invalid input.

Review and handoff:

- Both preexisting dirty checkouts were preserved by binary diff, untracked-file
  archive and per-file hashes; the rebuild was committed in an isolated worktree.
- Independent semantic review did not complete: Claude credential access and
  pinned Codex network resolution were blocked. No approval is claimed.
- The local base is recorded `origin/main` at
  `5d134c14630613ff32819abe99ad5109b65b07a5`; fresh fetch, push and GitHub API access
  are blocked. Refresh and safely integrate the base before opening this draft.
- Draft PRs skip automated Netlify publication. No publication or merge is part
  of this handoff. Remote CI has not run.

Next: inspect and hash the replication archive, verify its licence and native
field/selection mapping, reproduce source benchmarks, then report signed moments
with processing, measurement-error and population-coverage sensitivity.
