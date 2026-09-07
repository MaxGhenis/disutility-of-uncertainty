# Study 1 feasibility audit progress

## State
Completed independent artifact-only scientific audit on 2026-09-07, before the 21:00 America/New_York deadline. Scientific conclusion: observed finite-design projections are estimable, but stable individual MTR beliefs and latent heterogeneity are not separately identified from this archive.

Branch: `audit/study1-feasibility-20260907`. Isolated worktree based on locally fetched `origin/main` `5d134c14630613ff32819abe99ad5109b65b07a5`. Live fetch was blocked by sandbox DNS (`github.com`). Only this progress file and `study1-audit/` changed. Completed Disutility PR3 is untouched.

## Done
- Read global/project guidance, completed Disutility report/adapter/mapping, retained primary article/appendix/source manifest, every Study 1 native script and both native datasets.
- Identified the actual paper: Alex Rees-Jones and Dmitry Taubinsky, “Measuring ‘Schmeduling’” (2020).
- Pinned archive/member and consulted-source hashes; recorded native variable labels/types/missingness; verified 31 numeric columns match across 58,758 retained forecast rows and all 74,128 native forecast strings parse exactly.
- Independently reproduced all three Table 1 panels and all 484 Appendix A5–A8 cells; matched retained identified individual parameters within 0.000004.
- Audited local counts, income spans, bracket versus observed tax affinity, leverage, residual SEs, leave-one-out sensitivity, processing/heaping and extreme variance concentration.
- Derived/tested sharp individual box/RMS slope bounds, conservative finite-sample moment bounds and exact affine-belief feasibility/minimax calculations.
- Computed disjoint-forecast covariances with jackknife diagnostics and correlated-error sensitivity; exact synthetic counterexamples distinguish shared intercept and shared slope errors.
- Produced generated REPORT.md, METHODS.md, concrete measurement protocol, scripts, tests, source inventory, aggregate tables, README and HANDOFF.md.
- All 28 tests pass. Direct monetary/source arithmetic checks pass. Full regenerated artifacts match byte-for-byte; final count/hashes in evidence/reproduction-verification.json. Formatting, compilation and local links pass.
- Verified raw/consulted source and configuration hashes unchanged; original PR3 remains clean at 8e05267. No resets, paid overflow/API/remote compute, messages, publication or merge.
- One bounded semantic review of d1ea8d0 on pinned Axiom subscription capacity failed before inference: read-only Codex state DB and denied app-server initialization. No findings/approval and no replacement reviewer. Exact evidence and request retained.

## Next
1. Finish the retained bounded semantic review in a working authorized subscription runtime before external scientific reliance.
2. Recover author cleaning/liability-generation code if available through separately authorized follow-up.
3. Run the proposed two-session/cross-format pilot with complete verified local schedules and separate choice validation; current data cannot identify stable latent variance without additional restrictions.

No further scientific implementation is required for this bounded audit. Final output report and durable git/artifact exports are saved in the parent lane directory. Commit history preserves the start, native replication, sensitivity analysis and final validation/handoff milestones.
