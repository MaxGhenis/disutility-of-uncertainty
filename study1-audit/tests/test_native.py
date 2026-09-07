"""Checks against actual pinned native microdata and published retained outputs."""

import json
from pathlib import Path
import sys
import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sources import DEFAULT_ARCHIVE, ROOT, frame, read_archive
from audit import NUMERIC, pooled
from estimators import heuristic_fit


@pytest.fixture(scope="module")
def native():
    if not DEFAULT_ARCHIVE.exists():
        pytest.skip("Pinned author archive unavailable locally")
    members = read_archive()
    d = frame(members, "RJT_study_1_data", NUMERIC)
    d = d[d.attention == 0].copy()
    for c in d:
        if d[c].dtype.kind == "f":
            d[c] = d[c].astype(float)
    return members, d


def test_archive_corruption_rejected(tmp_path):
    p = tmp_path / "archive.zip"
    p.write_bytes(b"corrupt source")
    with pytest.raises(ValueError, match="checksum"):
        read_archive(p)


def test_actual_panel_flags_and_own_anchor(native):
    _, d = native
    assert len(d) == 67152 and d.mid.nunique() == 4197
    assert not d.duplicated(["mid", "qnum"]).any()
    assert np.array_equal(d.localdraw == 1, (d.qnum <= 2) | (d.bracket == d.ownbracket))
    assert np.array_equal(d[d.qnum == 2].ran, np.floor(d[d.qnum == 2].income))
    assert ((d.localdraw == 1) & (d.bracket != d.ownbracket)).sum() == 89


@pytest.mark.parametrize(
    "panel,n,b,se",
    [
        ("local", 17937, 0.81, 0.043),
        ("mid", 41970, 0.82, 0.013),
        ("full", 58758, 0.62, 0.010),
    ],
)
def test_actual_table1_printed_precision(native, panel, n, b, se):
    _, d = native
    mask = {
        "local": d.localdraw == 1,
        "mid": (d.qnum > 2) & (d.highincomedraw == 0),
        "full": d.qnum > 2,
    }[panel]
    fit = pooled(d[mask])
    assert fit["n"] == n
    assert round(fit["coefficient"], 2) == b
    assert round(fit["cluster_se"], 3) == se


def test_actual_retained_individual_gammas_are_model_coefficients(native):
    members, d = native
    est = frame(members, "individualestimates", ["mid", "qnum", "gamma_i3", "gamma_s3"])
    est = est.drop_duplicates("mid").set_index("mid")
    max_difference = 0
    recovered_missing = 0
    rank2 = 0
    for mid, g in d[(d.qnum > 2) & (d.amtowntax > 0)].groupby("mid"):
        fit = heuristic_fit(g.tax, g.iron, g.spotlight, g.taxguessmain)
        assert fit["rank"] == 2
        rank2 += 1
        retained = est.loc[mid, ["gamma_i3", "gamma_s3"]].to_numpy(float)
        if np.isfinite(retained).all():
            max_difference = max(
                max_difference, np.max(np.abs(fit["gamma"] - retained))
            )
        else:
            recovered_missing += 1
    assert rank2 == 3552 and recovered_missing == 6
    assert max_difference < 2e-6


def test_full_published_grid_cache_and_native_parameter_parity():
    actual = json.loads((ROOT / "results/individual_benchmarks.json").read_text())
    expected = json.loads((ROOT / "evidence/published-grids.json").read_text())[
        "matrices"
    ]
    for k, row in enumerate(actual, 5):
        assert row["grid_counts"] == expected[f"A{k}"]
        assert row["max_abs_difference"]["max"] < 4e-6
        assert row["rank2"] == 3552
