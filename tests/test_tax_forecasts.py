"""Instrument adapters tested against analytic slopes and payoff inequalities."""

import json

import numpy as np
import pytest

from taxuncertainty.analysis.tax_forecasts import (
    TaxForecast,
    local_slope_sample,
    main,
    mpl_interval,
    mpl_sample,
)


def forecast(person, i, x, true_slope=0.3, perceived_slope=0.2, **kwargs):
    return TaxForecast(
        person,
        str(i),
        x,
        100 + true_slope * x,
        250 + perceived_slope * x,
        **{"in_own_bracket": True, **kwargs},
    )


def test_individual_slopes_remove_level_errors_and_recover_signed_bias():
    rows = [forecast("a", i, x) for i, x in enumerate((1000, 1500, 2000))]
    sample, audit = local_slope_sample(rows)
    assert sample.moments().bias == pytest.approx(-0.1)
    assert sample.moments().sd == 0
    assert audit["pooled_fe_scale"] == pytest.approx(2 / 3)
    assert audit["respondents"][0]["iid_linear_slope_noise_variance"] == 0
    assert not audit["native_archive_mapping_verified"]


def test_pooled_fe_scaling_is_not_unweighted_mean_rate_ratio():
    # Both people have the same income design but different true slopes.
    rows = [
        forecast(p, i, x, t, b)
        for p, t, b in (("a", 0.1, 0.1), ("b", 0.4, 0.2))
        for i, x in enumerate((0, 100))
    ]
    sample, audit = local_slope_sample(rows)
    assert sample.moments().bias == pytest.approx(-0.1)
    assert audit["pooled_fe_scale"] == pytest.approx((0.01 * 1 + 0.16 * 0.5) / 0.17)
    assert audit["pooled_fe_scale"] != pytest.approx((1 + 0.5) / 2)


def test_flat_zero_tax_can_identify_rate_error_but_not_scale_ratio():
    sample, audit = local_slope_sample(
        [forecast("a", i, x, 0, 0.1) for i, x in enumerate((0, 100))]
    )
    assert sample.moments().bias == pytest.approx(0.1)
    assert audit["pooled_fe_scale"] is None


def test_selection_and_minimum_span_are_audited():
    rows = [
        forecast("a", 1, 0),
        forecast("a", 2, 10),
        forecast("b", 1, 0),
        forecast("b", 2, 100),
        forecast("b", 3, 200, in_own_bracket=False),
        forecast("b", 4, 300, selected=False),
        forecast("c", 1, 0),
    ]
    sample, audit = local_slope_sample(rows, minimum_income_span=20)
    assert list(sample.groups) == ["b"]
    assert audit["excluded_respondents"] == 2
    assert audit["respondents"][1]["source_excluded_forecasts"] == 1
    assert audit["respondents"][1]["selected_nonlocal_forecasts"] == 1
    assert audit["respondents"][1]["iid_linear_slope_noise_variance"] is None
    assert "span" in audit["respondents"][0]["excluded_reason"]


def test_dollar_noise_is_amplified_by_short_income_distance():
    slopes = []
    for delta in (10, 100):
        # Fixed +1 dollar noise at endpoint. Slope error must scale as 1/delta.
        rows = [
            TaxForecast("a", "1", 0, 0, 0, True),
            TaxForecast("a", "2", delta, 0.3 * delta, 0.3 * delta + 1, True),
        ]
        sample, audit = local_slope_sample(rows)
        slopes.append(sample.moments().bias)
        assert audit["respondents"][0]["inverse_income_sum_squares"] == pytest.approx(
            2 / delta**2
        )
    assert slopes[0] / slopes[1] == pytest.approx(10)


def test_slope_noise_variance_formula_with_orthogonal_residuals():
    x = np.array([0, 100, 200.0])
    noise = np.array([1, -2, 1.0])  # orthogonal to intercept and x
    rows = [
        TaxForecast("a", str(i), float(z), 0.3 * z, 0.2 * z + noise[i], True)
        for i, z in enumerate(x)
    ]
    sample, audit = local_slope_sample(rows)
    assert sample.moments().bias == pytest.approx(-0.1)
    assert audit["respondents"][0]["iid_linear_slope_noise_variance"] == pytest.approx(
        6 / 20000
    )


def test_nonlinear_truth_inside_a_claimed_local_bracket_fails():
    rows = [
        TaxForecast("a", str(i), x, y, y, True)
        for i, (x, y) in enumerate(((0, 0), (100, 10), (200, 50)))
    ]
    with pytest.raises(ValueError, match="nonlinear"):
        local_slope_sample(rows)


def test_bad_flags_duplicate_forecasts_and_no_slope_fail():
    with pytest.raises(ValueError, match="booleans"):
        forecast("a", 1, 0, selected="false")
    with pytest.raises(ValueError, match="duplicate"):
        local_slope_sample([forecast("a", 1, 0)] * 2)
    with pytest.raises(ValueError, match="no respondents"):
        local_slope_sample([forecast("a", 1, 0), forecast("a", 2, 0)])
    with pytest.raises(ValueError, match="finite"):
        local_slope_sample([], minimum_income_span=-1)


def test_published_mpl_example_is_interval_identified():
    offers = [0, *range(1, 22, 2)]
    choices = [b <= 15 for b in offers]
    assert mpl_interval(offers, choices) == pytest.approx([0.15, 0.25])
    # Every interior rate gives precisely these strict payoff rankings.
    for rate in np.linspace(0.151, 0.249, 20):
        assert [20 * (1 - rate) >= b for b in offers] == choices


def test_published_footnote_28_support_is_explicit():
    offers = [0, *range(1, 22, 2)]
    low = [b <= 19 for b in offers]
    assert mpl_interval(offers, low) == pytest.approx([-0.05, 0.05])
    assert mpl_interval(offers, low, rate_support=(0, 1)) == pytest.approx([0, 0.05])
    high = [b == 0 for b in offers]
    assert mpl_interval(offers, high, rate_support=(0, 1)) == pytest.approx([0.95, 1])


def test_mpl_cannot_force_finite_intervals_or_hide_nonmonotonicity():
    with pytest.raises(ValueError, match="nonmonotone"):
        mpl_interval([1, 3, 5], [True, False, True])
    with pytest.raises(ValueError, match="support"):
        mpl_interval([1, 3], [True, True])
    assert mpl_interval([1, 3], [True, True], rate_support=(0, 1)) == pytest.approx(
        [0, 0.85]
    )
    with pytest.raises(ValueError, match="increasing"):
        mpl_interval([1, 1], [True, False])
    with pytest.raises(ValueError, match="booleans"):
        mpl_interval([1, 3], [1, 0])


def test_mpl_exclusions_are_explicit_and_no_midpoint_is_reported():
    records = [
        dict(
            respondent_id="a",
            observation_id="1",
            selected=True,
            untaxed_amounts=[15, 17],
            choose_taxable=[True, False],
            taxable_increment=20,
            true_rate=0.3,
        ),
        dict(
            respondent_id="b",
            observation_id="1",
            selected=False,
            exclusion_reason="Source attention-check failure",
        ),
    ]
    sample, audit = mpl_sample(records)
    assert sample.interval_bounds()["bias"] == pytest.approx([-0.15, -0.05])
    assert audit["excluded_records"][0]["respondent_id"] == "b"
    with pytest.raises(ValueError, match="interval"):
        sample.moments()
    del records[1]["exclusion_reason"]
    with pytest.raises(ValueError, match="reason"):
        mpl_sample(records)


def test_instrument_cli_produces_scoped_hashed_report(tmp_path):
    payload = dict(
        schema_version=1,
        instrument="local_forecasts",
        manifest=dict(
            data_status="synthetic",
            currency_unit="dollars",
            study="Test",
            tax_scope="Artificial linear tax",
            population="Constructed",
            sample_selection="All",
            measurement_error="Not identified",
        ),
        records=[
            dict(
                respondent_id="a",
                observation_id=str(i),
                income=x,
                true_tax=0.3 * x,
                perceived_tax=0.2 * x,
                in_own_bracket=True,
            )
            for i, x in enumerate((0, 100))
        ],
    )
    source = tmp_path / "input.json"
    source.write_text(json.dumps(payload))
    output = tmp_path / "out"
    assert main(["--input", str(source), "--output-dir", str(output)]) == 0
    report = json.loads((output / "report.json").read_text())
    assert report["observed_moments"]["bias"] == pytest.approx(-0.1)
    assert not report["provenance"]["native_archive_mapping_verified"]
    assert len(report["provenance"]["canonical_instrument_sha256"]) == 64
    assert "synthetic" in report["status"]
    assert not report["latent_beliefs_identified"]
    assert len(report["calculation_source_sha256"]) == 64
    # Invalid metadata must preserve a prior valid run and leave a new path absent.
    before = {path.name: path.read_bytes() for path in output.iterdir()}
    payload["manifest"]["population"] = ""
    source.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="population"):
        main(["--input", str(source), "--output-dir", str(output)])
    assert before == {path.name: path.read_bytes() for path in output.iterdir()}
    fresh = tmp_path / "fresh"
    with pytest.raises(ValueError, match="population"):
        main(["--input", str(source), "--output-dir", str(fresh)])
    assert not fresh.exists()
