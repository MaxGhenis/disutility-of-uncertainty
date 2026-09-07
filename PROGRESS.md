# Study 1 feasibility audit progress

## State
Active independent artifact-only audit, begun 2026-09-07. Deadline 21:00 America/New_York.
Branch: audit/study1-feasibility-20260907. Isolated worktree; no PR3 edits.
Base: locally fetched origin/main 5d134c14630613ff32819abe99ad5109b65b07a5.
Live fetch attempted and blocked: could not resolve github.com in sandbox.

## Done
- Read global AGENTS/CLAUDE and project guidance, completed REPORT and NATIVE_MAPPING.
- Inspected original branch, clean status, remotes and fetched base without changes.
- Identified article as Alex Rees-Jones and Dmitry Taubinsky, Measuring “Schmeduling” (2020).
- Confirmed pinned archive includes Study 1 forecasts and individualestimates.dta.
- Verified auto_reset.enabled=false and persistent no-reset block; no resets or paid jobs.

## Next
1. Pin/hash source bytes; inspect every Study 1 native script and exact adapter.
2. Reproduce retained outputs and audit processing, draws, true-tax affine fit and slope leverage.
3. Test repeated-measure estimators and deterministic noise sensitivities with explicit assumptions.
4. Write quantitative methods report, tests and durable handoff; commit each milestone.

Only study1-audit/ and this progress file will change from the base. Raw source archives stay immutable. Final report will also be saved to lane result.md.

## Checkpoint: native replication and local diagnostics
- Pinned archive/member hashes, actual variable labels, dtype/missingness and consulted-source hashes saved.
- Independently reproduced Table 1 pooled coefficients/SEs and all 484 cells of Appendix A5–A8.
- Recovered positive-tax retained individual parameters to <4e-6; OLS also solves source convergence failures. These are heuristic coefficients, not individual MTRs.
- Audited 31 numeric columns shared between native datasets; exact match on 58,758 retained forecast rows.
- Computed selection, nonlinearity, leverage, processing, split-forecast and finite-sample sensitivity tables.
- First 16 analytical/adversarial estimator tests pass. Full native tests and final reproducibility check next.
- New observations: q2 is integer-truncated own income (19 fractional-income cases); 13 own-bracket respondents have stored-tax nonlinearity associated with exemption phaseout.

Next: correlated measurement-error demonstrations, primary-source-linked interpretation, bounded independent review if an authorized subscription lane is accessible, final validated report and handoff.
