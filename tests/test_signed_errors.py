"""Independent algebraic and data-integrity checks for signed calibration."""

import csv
import json
from dataclasses import asdict
from hashlib import sha256
from math import sqrt

import numpy as np
import pytest

from taxuncertainty.analysis.signed_errors import (
    RATE_COLUMNS,
    RateObservation,
    RateSample,
    calibration_report,
    classical_error_bounds,
    component_rmse_bounds,
    load_rate_sample,
    main,
    nonclassical_rmse_bounds,
)


def point(person, observation, error):
    return RateObservation(person, observation, 0, error, error)


def test_bias_variance_rmse_and_mae_have_distinct_meanings():
    # Exact enumeration: E[e] = -.05, E[e²] = .025, Var(e) = .0225.
    sample = RateSample([point("a", "1", -0.2), point("b", "1", 0.1)])
    m = sample.moments()
    assert asdict(m) == pytest.approx(
        dict(
            bias=-0.05,
            variance=0.0225,
            sd=0.15,
            second_moment=0.025,
            rmse=sqrt(0.025),
            mae=0.15,
        )
    )
    assert m.rmse**2 == pytest.approx(m.bias**2 + m.sd**2)
    assert m.rmse >= m.mae >= abs(m.bias)


def test_equal_respondent_mass_and_total_variance_decomposition():
    sample = RateSample(
        [point("a", "1", -0.2), point("a", "2", 0.2), point("b", "1", 0.4)]
    )
    m = sample.moments()
    assert m.bias == pytest.approx(0.2)  # Not the observation-weighted .1333.
    d = sample.variance_decomposition()
    assert d["between_respondent_variance"] == pytest.approx(0.04)
    assert d["within_respondent_variance"] == pytest.approx(0.02)
    assert d["total_variance"] == pytest.approx(0.06)
    assert not d["measurement_error_identified"]


def test_outliers_are_not_silently_censored():
    sample = RateSample([point("a", "1", -5), point("b", "1", 2)])
    assert sample.moments().bias == -1.5


@pytest.mark.parametrize(
    "args",
    [
        ("", "1", 0, 0, 0),
        ("a", " ", 0, 0, 0),
        ("a", "1", float("nan"), 0, 0),
        ("a", "1", 0, 0, float("inf")),
        ("a", "1", 0, 1, -1),
    ],
)
def test_invalid_observations_fail(args):
    with pytest.raises(ValueError):
        RateObservation(*args)


def test_duplicates_and_empty_samples_fail():
    with pytest.raises(ValueError, match="duplicate"):
        RateSample([point("a", "1", 0), point("a", "1", 1)])
    with pytest.raises(ValueError, match="contain"):
        RateSample([])


def test_cluster_bootstrap_is_order_invariant_and_does_not_resample_rows():
    rows = [point("a", "1", -1), point("a", "2", 1), point("b", "1", 0)]
    report = RateSample(rows).bootstrap(100, 4)
    assert report == RateSample(rows[::-1]).bootstrap(100, 4)
    # Every respondent has zero mean; row resampling would invent bias variation.
    assert report["intervals"]["bias"] == [0, 0]
    assert report["intervals"]["sd"] == pytest.approx([0, 1])
    assert not report["population_inference"]


def test_common_large_bias_does_not_erase_small_dispersion():
    # A tiny income perturbation can produce very large local slope errors.
    # SD must still be invariant to shifting all errors by the same amount.
    baseline = RateSample([point("a", "1", -1), point("b", "1", 1)])
    shifted = RateSample([point("a", "1", 1e8 - 1), point("b", "1", 1e8 + 1)])
    assert shifted.moments().sd == 1
    assert shifted.interval_bounds()["sd_outer"] == [1, 1]
    assert (
        shifted.bootstrap(100, 4)["intervals"]["sd"]
        == baseline.bootstrap(100, 4)["intervals"]["sd"]
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        {"replications": 1},
        {"replications": 2.5},
        {"replications": True},
        {"confidence": 0},
        {"confidence": 1},
        {"confidence": float("nan")},
    ],
)
def test_invalid_bootstrap_settings_fail(kwargs):
    with pytest.raises(ValueError):
        RateSample([point("a", "1", 0), point("b", "1", 1)]).bootstrap(**kwargs)


def test_single_cluster_is_not_bootstrapped():
    with pytest.raises(ValueError, match="two respondents"):
        RateSample([point("a", "1", 0)]).bootstrap()


def test_interval_bounds_enumerate_endpoints_and_contain_interior():
    sample = RateSample(
        [
            RateObservation("a", "1", 0.3, 0.1, 0.2),
            RateObservation("b", "1", 0.2, 0.1, 0.3),
        ]
    )
    bounds = sample.interval_bounds()
    assert bounds["bias"] == pytest.approx([-0.15, 0])
    assert bounds["second_moment"] == pytest.approx([0.005, 0.025])
    assert bounds["mae"] == pytest.approx([0.05, 0.15])
    for a in np.linspace(-0.2, -0.1, 11):
        for b in np.linspace(-0.1, 0.1, 11):
            m = RateSample([point("a", "1", a), point("b", "1", b)]).moments()
            for key in ("bias", "rmse", "mae"):
                assert (
                    bounds[key][0] - 1e-12 <= getattr(m, key) <= bounds[key][1] + 1e-12
                )
            assert (
                bounds["sd_outer"][0] - 1e-12 <= m.sd <= bounds["sd_outer"][1] + 1e-12
            )
    with pytest.raises(ValueError, match="interval"):
        sample.moments()
    with pytest.raises(ValueError, match="interval"):
        sample.bootstrap()


def test_degenerate_intervals_recover_point_moments():
    sample = RateSample([point("a", "1", -0.2), point("b", "1", 0.1)])
    for key in ("bias", "rmse", "mae", "second_moment"):
        assert sample.interval_bounds()[key] == pytest.approx(
            [getattr(sample.moments(), key)] * 2
        )
    assert sample.interval_bounds()["sd_outer"] == pytest.approx([0.15, 0.15])


def test_classical_variance_subtraction_and_nonzero_noise_bias():
    bounds = classical_error_bounds(
        -0.03, 0.04**2, noise_mean=(0.01, 0.02), noise_sd=(0.02, 0.03)
    )
    assert bounds["latent_bias"] == pytest.approx([-0.05, -0.04])
    assert bounds["latent_sd"] == pytest.approx([sqrt(0.0007), sqrt(0.0012)])
    assert bounds["latent_rmse"] == pytest.approx([sqrt(0.0023), sqrt(0.0037)])


def test_unidentified_classical_noise_leaves_bias_floor_only():
    bounds = classical_error_bounds(-0.03, 0.04**2, noise_sd=(0, 0.2))
    assert bounds["feasible_noise_sd"] == [0, 0.04]
    assert bounds["latent_sd"] == [0, 0.04]
    assert bounds["latent_rmse"] == pytest.approx([0.03, 0.05])


@pytest.mark.parametrize(
    "kwargs",
    [
        {"observed_bias": float("nan"), "observed_variance": 0},
        {"observed_bias": 0, "observed_variance": -1},
        {"observed_bias": 0, "observed_variance": 0.01, "noise_sd": (0.11, 0.12)},
        {"observed_bias": 0, "observed_variance": 0.01, "noise_sd": (-1, 0)},
        {"observed_bias": 0, "observed_variance": 0.01, "noise_mean": (1, -1)},
    ],
)
def test_incompatible_noise_assumptions_fail_instead_of_clamping_to_zero(kwargs):
    with pytest.raises(ValueError):
        classical_error_bounds(**kwargs)


def test_nonclassical_bounds_allow_bias_and_dependence():
    assert nonclassical_rmse_bounds(0.12, 0.05) == pytest.approx([0.07, 0.17])
    assert nonclassical_rmse_bounds(0.12, 0.2) == pytest.approx([0, 0.32])
    for value in (-1, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            nonclassical_rmse_bounds(0.12, value)


def test_federal_errors_need_not_bound_comprehensive_errors_from_below():
    assert component_rmse_bounds((0.12, 0.12), (0.12, 0.12)) == [0, 0.24]
    assert component_rmse_bounds((0.1, 0.12), (0.02, 0.04)) == pytest.approx(
        [0.06, 0.16]
    )
    with pytest.raises(ValueError):
        component_rmse_bounds((0.12, 0.1), (0, 0))


@pytest.fixture
def files(tmp_path):
    data = tmp_path / "rates.csv"
    with data.open("w", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(RATE_COLUMNS)
        writer.writerows([["001", "1", 0.3, 0.2, 0.2], ["002", "1", 0.3, 0.4, 0.4]])
    manifest = tmp_path / "manifest.json"
    meta = dict(
        schema_version=1,
        data_status="synthetic",
        rate_unit="fraction",
        study="Unit test",
        tax_scope="Artificial flat tax",
        population="Two constructed records",
        sample_selection="All constructed records",
        transformation="None",
        measurement_error="Not estimated",
        weighting="equal_respondent",
        input_sha256=sha256(data.read_bytes()).hexdigest(),
    )
    manifest.write_text(json.dumps(meta))
    return data, manifest


def test_schema_checksum_scope_and_cli_are_reproducible(files, tmp_path):
    data, manifest = files
    sample, meta = load_rate_sample(data, manifest)
    assert list(sample.groups) == ["001", "002"]
    report = calibration_report(sample, meta, replications=50)
    assert report["status"].startswith("synthetic")
    assert not report["latent_beliefs_identified"]
    args = ["--csv", str(data), "--manifest", str(manifest), "--replications", "50"]
    output = tmp_path / "report.json"
    assert main(args + ["--output", str(output)]) == 0
    assert json.loads(output.read_text()) == report
    before = output.read_bytes()
    assert main(args + ["--output", str(output)]) == 0
    assert output.read_bytes() == before
    with pytest.raises(SystemExit):
        main(args + ["--output", str(data)])


@pytest.mark.parametrize(
    "key,value",
    [
        ("rate_unit", "percent"),
        ("schema_version", 2),
        ("data_status", "unknown"),
        ("population", ""),
        ("weighting", "population"),
        ("input_sha256", "bad"),
        ("data_status", "observed"),
    ],
)
def test_incomplete_or_incompatible_manifests_fail(files, key, value):
    data, manifest = files
    meta = json.loads(manifest.read_text())
    meta[key] = value
    manifest.write_text(json.dumps(meta))
    with pytest.raises(ValueError):
        load_rate_sample(data, manifest)


def test_corrupted_data_fails_before_calibration(files):
    data, manifest = files
    data.write_text(data.read_text().replace("0.3", "0.9"))
    with pytest.raises(ValueError, match="checksum"):
        load_rate_sample(data, manifest)
