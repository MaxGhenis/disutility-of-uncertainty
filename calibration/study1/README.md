# Study 1 appendix evidence

This directory preserves **18 byte-identical files** from the independently
reviewed audit at `a5191ea9f81fd414d9fbf547995dcb31341aa875`. `manifest.json`
records every original path, size and SHA256. Only audit-authored Python,
aggregate outputs and benchmark inputs are included. The two benchmark JSONs
are dependencies of the frozen audit, including its pooled/grid verification;
no additional grid/type interpretation is introduced into the paper.

The source report's later precision-only correction is commit
`935ed77d4a7afe4ed721f1ff6dd147254a9ff4bf`: all 22 scientific aggregate files
remain unchanged. The paper uses approximately **0.05013** and the **observed
correlation, approximately 0.1002613**, rather than interpreting 0.100000 as an
exact threshold. The inherited [independent review](../reviews/study1-a5191ea.md)
covers a5191ea only. Its original snapshot links refer to the external review
archive; this directory is a minimal reproducibility subset, not that snapshot.
The integration and its new importer require their own scoped review.

## Reproduce

From the repository root, install the locked environment (`make install`) and
supply a separately obtained local copy of the [author-linked archive](https://www.dropbox.com/s/2q47bj8arbcgr3i/Schmeduling%20Replication%20Code.zip?dl=1):

```sh
RJT_ARCHIVE=/path/to/Schmeduling_Replication_Code.zip \
  uv run --no-sync python calibration/study1/reproduce.py
uv run --no-sync python -m taxuncertainty.analysis.study1_evidence --check
make check-results
```

The first command runs the frozen audit in a temporary directory and compares
all **10 included aggregate files byte for byte**. The pinned source hash is
`c578518776c9cd97cc0bcf340558a9574ed2088cfeb5d1b610274e5d7ab48b15`.
No network access, Stata execution, new tax computation or model call is needed.
The frozen source reader temporarily numbers the archive's native text/code;
these files stay in the temporary directory and are not redistributed. Synthetic
counterexamples and prospective pilot calculations are not run by this wrapper.
`requirements.txt` records the audited NumPy/pandas/pytest versions; the project
lock supplies those same versions and Python 3.13.9.

The second command verifies the frozen-file hashes and exact cohort selections
against the packaged aggregate cache, without needing microdata. Regenerate the
cache by omitting `--check`, then run `make generate` for paper inputs. The model
pipeline reads that cache as `study1_evidence`, separately from Study 2's
`observed_calibration` and all welfare assumptions. Slopes remain fractions in
JSON; paper slopes/SDs multiply by 100, and covariance and its SE by 10,000.

## Interpretation and source restrictions

The appendix describes **observed finite-design forecast projections**, not
noise-free marginal-tax beliefs. It states attention/processing selection,
observed-point true-tax nonaffinity, missing cleaning/liability-generation code,
short income support, and the extra common-target/orthogonality assumptions for
the same-session split covariance. The 555/2470 compatibility count jointly tests
an affine forecast model and an assumed $100 answer-error cap. It does not
identify stable belief types or prove irrationality. The incentive window does
not bound response errors. The hypothetical federal filer and selected survey
sample do not identify comprehensive population incentives or national welfare.
The model's latent RMSE **0.12 remains illustrative**.

No explicit redistribution licence was found in the original archive. Raw and
canonical microdata, original DO files and source PDFs are excluded from this
package. Obtain and retain source bytes separately under their applicable terms.
The repository's MIT licence does not grant rights to those external sources.

## Reviewed provenance identities

The importer pins the exact manifest SHA256 in code, covering the entire
18-file inventory, source mappings, file hashes, sizes and audit/archive identity.
It also pins the canonical aggregate-content digest for both fresh imports and
installed cache loads. Rewriting a file hash, dropping a consumed file, changing
source attribution or self-rehashing changed scientific values cannot retain the
old reviewed identity. Cache JSON whitespace/key order may vary without changing
its canonical content. The frozen manifest itself remains byte-identical.

These anchors refer to the correct frozen evidence delivered at integration
09a5685; [its completed integration review](../reviews/integration-09a5685.md)
identified the missing trust anchors (DOU-STUDY1-001). Changing evidence requires
an explicit source/version review and corresponding code-anchor update, not just
regenerating local checksums. This repair changes no aggregate or welfare input;
the same host reviewer will assess the exact repair delta separately.
