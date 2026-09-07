# Native replication mapping

`taxuncertainty.analysis.rjt_replication` reads the author-linked ZIP with SHA256
`c578518776c9cd97cc0bcf340558a9574ed2088cfeb5d1b610274e5d7ab48b15`.
It verifies the archive and five required members before parsing Stata data;
it executes no Stata code. The archive README contains no explicit redistribution
licence. Raw and canonical person-level data remain local; the repository stores
aggregate replication results and calculation/source hashes only.

Sources: [author's publication index](https://www.dmitrytaubinsky.com/),
[archive](https://www.dropbox.com/s/2q47bj8arbcgr3i/Schmeduling%20Replication%20Code.zip?dl=1),
[article](https://alexreesjones.github.io/papers/Measuring%20Schmeduling.pdf),
[appendix](https://alexreesjones.github.io/papers/Measuring%20Schmeduling%20Online%20Appendix.pdf).
The live index was checked on September 7, 2026. See `sources.json` for hashes.

## Study 2

| Native field | Canonical meaning and verification |
|---|---|
| Original row ordinal | `respondent_id=study2-row-000001`, etc.; native file has no unique respondent-ID field. IDs are meaningful only within this pinned archive. |
| `q21_0` through `q21_11` | Twelve raw A/B choices. A adds 20 taxable cents; B adds respectively 0, 1, 3, ..., 21 untaxed cents. Observation ID is `mpl`. |
| `MTR` | `true_rate`: native fractional tax rate on the extra 20 cents. Stored float32 values are preserved, with no rounding to nominal treatment rates. |
| `ATR` | Native fraction on the initial 40 cents; a separate regression covariate, never substituted for the true incremental tax. |
| `switchingpoint` | First B choice, 1 through 13 (13 means all A). Recomputed from all raw choices for monotone rows. |
| `irrational` | Any B followed later by A; independently checked against all twelve decisions. |
| `inattentive_1` | B on first item or A on last item; independently reconstructed endpoint screen. |
| `inattentive_2` | Source final-attention failure flag; its underlying attention answer is absent and cannot be independently rescored. |
| `condition`, `table` | Schedule complexity and reopening the table; source Table 4 subgroup filters. |

The primary filter is exactly `irrational==0 & inattentive_1==0 & inattentive_2==0`
(Table 4.do lines 44-48). Every retained respondent receives equal mass. In the
article's order, the sample waterfall is 4,582 -> 3,868 -> 3,689 -> 3,130.
All 4,582 raw choice rows reproduce the derived flags without disagreement.
The 868 endpoint failures include some nonmonotone people; they are not just
the 603 all-B and 108 all-A respondents.

Each choice contributes a weak payoff inequality. Intersecting them gives
closed perception intervals, allowing indifference at the endpoints. The
`author` variant also imposes [0,1], matching Table 4.do lines 14-42 and article
footnote 28. The `payoff` variant uses the inequalities alone. They differ for
the 72 retained people switching at item 12: [-.05,.05] becomes [0,.05]. The
endpoint screen alone does not justify the latter lower bound. No default
clipping occurs in the canonical signed-error engine.

The main OLS and subgroup regressions use source interval midpoints. The
reintroduced-endpoint regressions reproduce the source's 0/1 imputations for
open bins; those imputations do not identify finite error-moment bounds. The
adapter therefore supplies finite reinclusion bounds only for reintroducing
final-attention failures while keeping both monotonicity and endpoint screens.

**Appendix A9 label discrepancy:** the native filter that reintroduces final
attention failures gives N=3,603 and coefficients matching printed column 3.
Reintroducing endpoint failures gives N=3,689 and coefficients matching column
4. The appendix's printed reintroduced-group labels indicate the reverse. Both
native variable labels and reconstructed choices confirm our meanings. Results
are named by actual filters and retain this discrepancy; they do not silently
adopt the printed labels. The primary regression is unaffected.

## Study 1

| Native field | Use |
|---|---|
| `mid`, `qnum` | Respondent and forecast identifiers; duplicate pairs are rejected. |
| `attention` | Retain numeric code 0, exactly Table 1.do line 19. |
| `tax` | Source-calculated true federal liability. No tax model is rerun here. |
| `taxguessmain`, `tgw1` | Source processed forecast; byte values agree throughout retained data. |
| `taxguessds` | Source pre-winsorization forecast; differs on 1,501 retained forecasts. This is still an archive variable, not the original survey export. |
| `ran` | Hypothetical forecast income; `income` is the respondent's own income. |
| `qnum>2` | Table 1 full sampling panel. |
| `qnum>2 & highincomedraw==0` | Table 1 middle sampling panel. |
| `localdraw==1` | Table 1 local panel, exactly as published. |
| `bracket`, `ownbracket` | Nominal bracket comparison; 89 local-flagged rows are outside the own bracket. |

The supplied archive starts after 195 survey completers were excluded; it has
4,633 respondents and 74,128 forecasts. The remaining attention exclusion is
reproducible: 4,197 respondents, 67,152 forecasts. Reconstructing the original
4,828-person cleaning or rolling winsorization is not claimed: the original
export and full cleaning script are absent.

The three pooled Table 1 panels are reproduced by within-person OLS with
respondent-clustered standard errors. They measure a scale weighted by true-tax
variation. In the local panel, 601 of 4,197 respondents have no within-person
true-tax variation, and contribute no identifying variation for the scale.
The reported coefficient is neither an average signed slope error nor a latent
type share. A stricter within-bracket individual slope analysis must distinguish
its exclusions and its income-leverage sensitivity from this benchmark.

## Reproduction and integrity

With the public archive downloaded to a local path:

```sh
uv run --no-sync python -m taxuncertainty.analysis.rjt_replication \
  --archive /path/to/Schmeduling_Replication_Code.zip --output-dir /tmp/rjt
RJT_ARCHIVE=/path/to/Schmeduling_Replication_Code.zip \
  uv run --no-sync pytest tests/test_rjt_replication.py -q --no-cov
```

The first command validates published counts and printed coefficient/SE
precision before producing `replication.json`, and author/payoff variants of
`rates.csv`, `manifest.json`, and `report.json`. Preserve all files locally for
review. To update the committed aggregate cache, copy `replication.json` to
`src/taxuncertainty/data/rjt_replication.json` and regenerate paper artifacts.
No download, API job, or paid compute is triggered by the pipeline or tests.

The native integration test compares the whole fresh result against the cache
in the locked environment and round-trips both canonical datasets. Default
tests validate synthetic native-format invariants plus cache integrity and
published benchmark gates. A cache check detects drift; it is not a substitute
for the separately reported actual archive execution.
