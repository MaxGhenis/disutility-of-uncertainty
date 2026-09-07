# Signed-error calibration handoff

## State

Validated offline milestone completed September 7, 2026. Branch:
`sprint/signed-error-calibration-20260907`, in
`/Users/maxghenis/disutility-of-uncertainty-calibration-20260907`.
The preserved rebuild and the new calibration work are committed. Both prior
dirty checkouts remain intact. The model's 0.12 latent RMSE is illustrative;
no empirical microdata calibration or national welfare estimate is claimed.

## Delivered

- Exact preservation of the validated welfare-accounting rebuild, including
  source, tests, generated results, nonlinear budgets and real household fixture.
- Canonical signed-rate and instrument schemas, observed bias/SD/RMSE/MAE,
  respondent-cluster bootstrap, selection/leverage diagnostics and the separate
  pooled fixed-effects estimand.
- MPL interval bounds, explicit support conventions, classical/nonclassical
  measurement-error sensitivity and dependence-robust component RMSE bounds.
- Source/access manifest and identification protocol, incorporating and checking
  the independent research memo without adopting unsupported mixture inferences.
- Updated 15-page paper in PDF/HTML, draft-PR body and offline branch artifacts.

Primary files: `calibration/README.md`, `calibration/IDENTIFICATION.md`,
`calibration/sources.json`, `src/taxuncertainty/analysis/signed_errors.py`,
`src/taxuncertainty/analysis/tax_forecasts.py`,
`paper/chapters/identification.md`, `DRAFT_PR.md` and `PROGRESS.md`.

## Validation

239 tests pass, one optional live PolicyEngine test skipped, 93% overall coverage.
Fatal flake8, Black, isort, mypy (19 source files), citation checks,
generated-artifact checks and `git diff --check` pass. Quarto renders HTML and a
15-page PDF; new pages and the abstract were visually inspected. A runtime-only
wheel installation matches all 22 source/data files and reproduces the complete
model results, the canonical calibration example and the household fixture
without PolicyEngine or Matplotlib installed.

Tests include independent arithmetic/inequality checks, respondent weighting,
noise amplification, interval endpoints, impossible-noise rejection, tax-component
cancellation, numerical stability under large common bias, and preserving output
when validation fails. No new live household or population computation was run.

Preservation verification finds unchanged bytes/status for 50 original-checkout
files and 72 rebuild files. The original branches remain `main` and
`rebuild-welfare-accounting-20260905`. Reset blocking remains enabled and
`auto_reset.enabled` remains false; this lane changed neither control file.

## Blockers and exact next steps

1. The terminal cannot resolve Dropbox or GitHub. The author-linked archive is
   located, but its contents, native fields, cleaning and licence are unverified.
   Download and hash it using an available public route; inspect the source
   mapping and reproduce benchmarks before reporting observed microdata moments.
   Continue on this same implementation branch.
2. A fresh base fetch, branch push and GitHub API access failed. No remote draft
   PR exists and remote CI has not run. After access returns, fetch current
   `origin/main`, integrate changes safely, validate, and open a **draft** using
   `DRAFT_PR.md`. Do not merge or publish. Draft previews are disabled.
3. Independent semantic review did not complete. Claude could not access its
   enrolled credential; the pinned Axiom Codex attempt could not resolve
   `chatgpt.com`. No approval is claimed. Its network-stalled run is
   `20260907-170836-disutility-signed-error-review`, PID 12571. Attempted
   `subfleet kill` failed with Operation not permitted. A host-authorized
   coordinator must terminate that specific run; do not reset or launch overflow.

Local base: recorded `origin/main` at
`5d134c14630613ff32819abe99ad5109b65b07a5`. This is not represented as a freshly
fetched base. Historical rebuild reviews are retained in the architecture-review
directory; they do not approve the new empirical adapters.

## Durable lane artifacts

`/Users/maxghenis/capacity-sprint-20260907/disutility/` contains preservation
diffs/archives/manifests, test/lint/build/smoke logs, canonical adapter outputs,
rendered paper and inspected pages, wheel and smoke environment, draft-PR body,
review failure logs, and the explicit review-process termination handoff. The
final checkpoint also exports `signed-error-calibration.bundle`, a full branch
patch, a SHA256 artifact manifest and the final report.
