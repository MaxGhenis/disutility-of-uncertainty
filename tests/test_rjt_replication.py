"""Native mapping invariants and optional checksum-pinned archive replication."""

import json
import os
from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from taxuncertainty.analysis.rjt_replication import (
    ARCHIVE_SHA256,
    artifact_hash,
    fixed_effects_scale,
    interval_noise_sensitivity,
    load_replication,
    main,
    midpoint_ols,
    midpoint_outcome,
    read_archive,
    reproduce,
    study2_masks,
    study2_sample,
    validate_benchmarks,
    validate_study2,
)
from taxuncertainty.analysis.signed_errors import RateSample, load_rate_sample


def native(switches=range(1, 14)):
    rows = []
    for i, switch in enumerate(switches):
        choices = ["A" if j + 1 < switch else "B" for j in range(12)]
        rows.append(
            dict(
                switchingpoint=float(switch),
                irrational=0,
                inattentive_1=int(switch in (1, 13)),
                inattentive_2=0,
                condition="1_kink",
                table=0,
                ATR=0.2 + 0.1 * (i % 3),
                MTR=0.2 + 0.1 * (i % 4),
                **{f"q21_{j}": choice for j, choice in enumerate(choices)},
            )
        )
    return pd.DataFrame(rows)


def test_all_native_bins_map_to_payoff_inequalities_and_author_convention():
    frame = native()
    author, payoff = study2_sample(frame), study2_sample(frame, "payoff")
    assert len(author.groups) == 11
    assert author.observations[0].respondent_id == "study2-row-000002"
    for i, row in enumerate(payoff.observations):
        # Every interior point in the resulting interval satisfies all 12
        # original choices, independently of switchingpoint's derived code.
        rate = (row.perceived_rate_lower + row.perceived_rate_upper) / 2
        offers = [0, *range(1, 22, 2)]
        assert ["A" if 20 * (1 - rate) > x else "B" for x in offers] == frame.loc[
            i + 1, [f"q21_{j}" for j in range(12)]
        ].tolist()
    assert payoff.observations[-1].perceived_rate_lower == pytest.approx(-0.05)
    assert author.observations[-1].perceived_rate_lower == 0
    assert author.observations[-1].perceived_rate_upper == pytest.approx(0.05)
    assert author.observations[0].perceived_rate_lower == pytest.approx(0.95)
    assert author.observations[0].perceived_rate_upper == 1
    with pytest.raises(ValueError, match="interval"):
        author.moments()


@pytest.mark.parametrize(
    "column,value,message",
    [
        ("q21_4", "C", "A or B"),
        ("irrational", 1, "irrational flag"),
        ("inattentive_1", 1, "endpoint flag"),
        ("inattentive_2", np.nan, "native flag"),
        ("switchingpoint", 8, "switchingpoint"),
        ("MTR", 50, "fractional"),
        ("ATR", np.nan, "fractional"),
        ("condition", "unknown", "schedule"),
    ],
)
def test_native_inconsistencies_fail_closed(column, value, message):
    frame = native([5])
    frame.loc[0, column] = value
    with pytest.raises(ValueError, match=message):
        validate_study2(frame)


def test_nonmonotone_and_endpoint_failures_are_distinct_and_auditable():
    frame = native([1, 5, 13, 7, 6])
    frame.loc[3, "q21_2"] = "B"
    frame.loc[3, "irrational"] = 1
    frame.loc[3, "switchingpoint"] = np.nan
    frame.loc[4, "inattentive_2"] = 1
    validate_study2(frame)
    masks = study2_masks(frame)
    assert masks["primary"].tolist() == [False, True, False, False, False]
    assert masks["include_endpoint_failures"].sum() == 3
    assert masks["include_final_attention_failures"].sum() == 2
    assert len(study2_sample(frame, include_final_attention=True).groups) == 2
    frame.loc[3, "switchingpoint"] = 3
    with pytest.raises(ValueError, match="missing switchingpoint"):
        validate_study2(frame)


def test_ols_imputation_matches_source_end_bins_but_is_not_a_finite_bound():
    frame = native()
    y = midpoint_outcome(frame)
    assert y == pytest.approx(
        [1, 0.975, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.025, 0]
    )
    fit = midpoint_ols(frame)
    x = np.column_stack([np.ones(len(frame)), frame.ATR, frame.MTR])
    coefficients = np.array(list(fit["coefficients"].values()))
    assert x.T @ (y - x @ coefficients) == pytest.approx(np.zeros(3), abs=1e-14)
    with pytest.raises(ValueError, match="full rank"):
        midpoint_ols(native([5, 5]))


def test_fe_matches_explicit_dummy_regression_with_unequal_group_sizes():
    frame = pd.DataFrame(
        {
            "mid": [1, 1, 2, 2, 2, 3, 3],
            "tax": [1, 2, 1, 3, 5, 10, 10],
            "taxguessmain": [3, 4, 2, 4, 10, 15, 17],
        }
    )
    result = fixed_effects_scale(frame)
    design = np.column_stack([frame.tax, pd.get_dummies(frame.mid).to_numpy()])
    expected = np.linalg.lstsq(design, frame.taxguessmain, rcond=None)[0][0]
    assert result["coefficient"] == pytest.approx(expected)
    assert result["respondents_with_positive_tax_variation"] == 2
    # Adding arbitrary person-specific level errors preserves the slope and SE.
    shifted = frame.copy()
    shifted.taxguessmain += shifted.mid.map({1: 500, 2: -25, 3: 9})
    assert fixed_effects_scale(shifted) == pytest.approx(result)


def test_interval_marginal_extrema_are_attained_by_feasible_native_vectors():
    sample = study2_sample(native())
    bounds = sample.interval_bounds()
    for side, index in (("perceived_rate_lower", 0), ("perceived_rate_upper", 1)):
        point = RateSample(
            replace(
                r,
                perceived_rate_lower=getattr(r, side),
                perceived_rate_upper=getattr(r, side),
            )
            for r in sample.observations
        )
        assert point.moments().bias == pytest.approx(bounds["bias"][index])
    for closest, index in ((True, 0), (False, 1)):
        points = []
        for r in sample.observations:
            endpoints = [r.perceived_rate_lower, r.perceived_rate_upper]
            rate = (
                np.clip(r.true_rate, *endpoints)
                if closest
                else max(endpoints, key=lambda x: abs(x - r.true_rate))
            )
            points.append(
                replace(r, perceived_rate_lower=rate, perceived_rate_upper=rate)
            )
        assert RateSample(points).moments().rmse == pytest.approx(bounds["rmse"][index])


def test_archive_integrity_fails_before_parsing_and_preserves_output(tmp_path):
    archive = tmp_path / "changed.zip"
    archive.write_bytes(b"not the source archive")
    out = tmp_path / "out"
    out.mkdir()
    previous = out / "replication.json"
    previous.write_text("previous validated result")
    with pytest.raises(ValueError, match="archive checksum"):
        main(["--archive", str(archive), "--output-dir", str(out)])
    assert previous.read_text() == "previous validated result"
    assert len(list(out.iterdir())) == 1


def test_interval_noise_bounds_cover_arbitrarily_correlated_biased_noise():
    sample = study2_sample(native())
    rng = np.random.default_rng(421)
    ranges = interval_noise_sensitivity(sample)
    for _ in range(30):
        errors = np.array([rng.uniform(*r.error_interval) for r in sample.observations])
        for row in ranges["rows"]:
            noise = rng.normal(0.4, 1, len(errors))
            noise *= row["noise_rmse_max"] / np.sqrt(np.mean(noise**2))
            latent = errors - noise
            for key, value in (
                ("latent_bias_outer", latent.mean()),
                ("latent_rmse_outer", np.sqrt(np.mean(latent**2))),
            ):
                lo, hi = row[key]
                assert lo - 1e-12 <= value <= hi + 1e-12
    with pytest.raises(ValueError, match="finite and nonnegative"):
        interval_noise_sensitivity(sample, [-0.1])


def test_committed_empirical_cache_has_current_provenance_and_published_benchmarks(
    tmp_path,
):
    result = load_replication()
    assert result["provenance"]["archive_sha256"] == ARCHIVE_SHA256
    assert not result["welfare_input_replaced"]
    assert not result["study2"]["latent_beliefs_identified"]
    assert result["study1"]["local_flag_outside_own_bracket"] == 89
    assert result["study2"]["interval_bounds"]["author"]["bias"] == pytest.approx(
        [0.04648561694275452, 0.14369008978620498]
    )
    # Hash failures and wrong but rehashed benchmark claims are separate gates.
    path = tmp_path / "cache.json"
    result["study2"]["selection_counts"][-1] = 3200
    path.write_text(json.dumps(result))
    with pytest.raises(ValueError, match="artifact checksum"):
        load_replication(path)
    result["artifact_sha256"] = artifact_hash(result)
    path.write_text(json.dumps(result))
    with pytest.raises(ValueError, match="sample benchmark"):
        load_replication(path)


@pytest.mark.skipif(
    not os.environ.get("RJT_ARCHIVE"),
    reason="set RJT_ARCHIVE to checksum-pinned local ZIP for real-data replication",
)
def test_real_archive_reproduces_committed_cache_and_canonical_outputs(tmp_path):
    archive = os.environ["RJT_ARCHIVE"]
    first, second = read_archive(archive)
    actual = reproduce(first, second)
    validate_benchmarks(actual)
    cached = load_replication()
    # Floating results are deterministic within the locked stack; runtime
    # metadata is not used to obscure numerical or mapping differences.
    actual["artifact_sha256"] = artifact_hash(actual)
    assert actual == cached
    main(["--archive", archive, "--output-dir", str(tmp_path)])
    for convention in ("author", "payoff"):
        sample, manifest = load_rate_sample(
            tmp_path / f"{convention}-rates.csv",
            tmp_path / f"{convention}-manifest.json",
        )
        assert len(sample.groups) == 3130
        assert manifest["native_archive_mapping_verified"]
        assert (
            sample.interval_bounds() == cached["study2"]["interval_bounds"][convention]
        )
