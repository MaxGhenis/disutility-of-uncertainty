# Study 1 provenance repair ready for focused rereview

Exact repair target: `cd204c90e2ca94a2f81766cfb1e06320b76d1832`.
Prior delivered PR head: `98bc1b77d179d024daba8e2fba66a0f5ae571ea0`.
Diff: `git diff 98bc1b77d179d024daba8e2fba66a0f5ae571ea0 cd204c90e2ca94a2f81766cfb1e06320b76d1832`.
Binary patch SHA256: `4facd03b58a915b8e701a63037975298e8fd81e251ab5caaa0a1cb5c479d8c86`.
Local branch: `sprint/study1-provenance-repair-20260907`.
Isolated worktree: `/Users/maxghenis/disutility-of-uncertainty-study1-repair-20260907`.
Existing draft: https://github.com/MaxGhenis/disutility-of-uncertainty/pull/3

## Finding and repair

The completed host integration review of exact 09a5685 identifies one P2,
DOU-STUDY1-001, at study1_evidence.py:26-42 and :212-225 in that reviewed tree.
Current frozen science and the inherited a5191ea evidence are correct. The final
report was read and is preserved in `calibration/reviews/integration-09a5685.md`.

The new importer change adds two code-level trust anchors:

- Exact manifest SHA256
  `eaa4d3358abb068bccd0d5204fd4c2ef2e5c0eac86c5693f4580d2972055055d`
  covers the full 18-file inventory, original source mappings, hashes, sizes and
  audit/archive labels before any listed-file verification or aggregate import.
- Canonical aggregate-content SHA256
  `d16e23fe64d4d78da75eec90c53c8b7c185270f00fc4bb2209299ea03354b3fc`
  is required for both newly built evidence and installed-cache loads, in
  addition to the existing self-consistency and scope checks. Scientific values
  and provenance cannot be changed by simply recomputing their own checksum.

A future evidence version requires a deliberate reviewed code-anchor update.
Cache JSON whitespace/key order may vary without changing canonical content;
the frozen manifest identity is byte-exact. No scientific file or value changes.

## Owner verification

- Eight negative regression cases **fail before the fix and pass after it**:
  omitted consumed file plus changed science, changed source mapping, changed
  file with rewritten manifest hash/size, empty inventory, extra inventory entry,
  and self-rehashed cache changes to science, source mapping or inventory.
- One positive regression accepts harmless JSON cache formatting changes.
- **30 focused importer/pipeline tests pass**; fatal flake8, Black, isort and mypy
  pass. Aggregate importer and generated-results/citations checks pass.
- Original aggregate-only host reproducer now stops at its first altered-manifest
  attempt with the anchored-identity error. All three original bypass classes
  and the added inventory/rehashed-file variants are exercised by the tests.
- All scientific results, including every Study 1/2 value and welfare input 0.12,
  equal the prior delivered head. **49 paths are byte-identical**, including the
  evidence cache, source manifest and all 18 frozen files, paper sources/tables,
  existing welfare data and figures. Only model-source fingerprints regenerate.
- HTML/PDF were refreshed because that fingerprint appears in the paper. Exact
  extracted PDF text differs only by replacing the 12-character fingerprint on
  page 2; the appendix and all other page text are unchanged. PDF remains
  20 pages. The new fingerprint page is inspected in the lane artifacts.

## Focused rereview scope and artifacts

Please rereview only the provenance-gate repair, its regression cases and the
unchanged-science comparison. No new scientific campaign, model, human-data or
PolicyEngine computation is needed. The existing a5191ea scientific review and
09a5685 integration review retain their exact scopes. This repair is not yet
claimed independently approved. No nested reviewer was launched.

Lane `/Users/maxghenis/capacity-sprint-20260907/disutility/study1-repair/` contains
`repair.patch`, `REPAIR_HEAD`, `regressions-before.log`, `focused-tests.log`,
`lint.log`, `generated-checks.log`, `unchanged-science.json`, `paper-delta.json`
and the original reproducer plus rejection evidence. Later delivery metadata
commits do not change the exact repair target above.

Safe checkpoint deadline is 20:40 ET; stop new work 21:00. Draft update only;
no merge/publication, dirty-original edits, paid compute or reset actions.
