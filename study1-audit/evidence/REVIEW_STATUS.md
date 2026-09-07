# Independent review status

**Clean within the stated finite-design feasibility scope at `a5191ea9f81fd414d9fbf547995dcb31341aa875`.** The existing [independent host review](../../../independent-review-host.md) used a separate [frozen snapshot](../../../independent-review-a5191ea/REVIEWED_HEAD), reran all 28 tests, reproduced 36 tracked result/evidence/report files byte-for-byte and independently checked source mapping, selection, pooled benchmarks, affine feasibility and covariance arithmetic. Its scope does not authorize welfare-input transfer, publication or paper integration and does not cover later commits.

The sole nonblocking finding was displayed precision at frozen `REPORT.md:68`, `report.template.md:47` and `scripts/report.py:106`: rounded 0.050 and 0.100 were used in a sentence about exact observed moments. This follow-up resolves it with approximately 0.05013 and the observed correlation, approximately 0.1002613, derived from the existing CSV. [Focused checks](precision-verification.json) record the original review report's SHA256, the current report hash and unchanged scientific aggregates. No statistical analysis or new review/model call was run for the correction. The host review remains scoped to a5191ea; subsequent display/documentation changes have focused implementation checks only.

The review and frozen evidence are existing lane artifacts outside the git bundle; their relative links above resolve from this worktree. The parent lane's export manifest hashes the host review and its verification evidence for handoff.

Historical failed attempt: one authorized bounded semantic Subfleet review was dispatched against commit `d1ea8d0e49a44fcd717b3be361e2dfc53339e3ad` on the pinned Axiom subscription lane `/Users/maxghenis/.codex-3`, using `--task review --tier hard -s read-only`. No implementation agent or second reviewer was spawned during that attempt.

Run ID: `20260907-184406-independent-review-md`. The provider failed before reviewing any artifact (rc=1, output bytes=0):

```
failed to open state DB at /Users/maxghenis/.codex-3/state_5.sqlite:
attempt to write a readonly database
Error: failed to initialize in-process app-server client:
Operation not permitted (os error 1)
```

That attempt was a sandbox/runtime failure and produced no file/line findings or approval. Its [exact bounded review request](review-request.md) is retained as historical evidence; the separate completed host review above supplies the subsequent independent review.

No reset, automatic reset, overflow, paid API, paid remote computation, publication, merge or message to a person was used in this correction. No claim of journal or external scientific approval is made.
