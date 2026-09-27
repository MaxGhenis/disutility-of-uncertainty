"""Independent direct-pair check and stored-tax decomposition (aggregate only)."""

import numpy as np
import pandas as pd
from sources import frame, read_archive
from audit import save


def main():
    d = frame(
        read_archive(),
        "RJT_study_1_data",
        [
            "mid",
            "qnum",
            "attention",
            "ran",
            "income",
            "tax",
            "taxguessmain",
            "amtowntax",
            "ownmarginalrate",
            "bracket",
            "ownbracket",
            "fredexempphaseout",
            "exemptions",
        ],
    )
    d = d[d.attention == 0].copy()
    for c in d:
        if d[c].dtype.kind == "f":
            d[c] = d[c].astype(float)
    pair = d[d.qnum <= 2].pivot(
        index="mid", columns="qnum", values=["ran", "tax", "taxguessmain"]
    )
    increment = pair.ran[1] - pair.ran[2]
    forecast_delta = pair.taxguessmain[1] - pair.taxguessmain[2]
    true_delta = pair.tax[1] - pair.tax[2]
    direct_error = (forecast_delta - true_delta) / increment
    centered_square = (direct_error - direct_error.mean()) ** 2
    # Compare against the report's independent general OLS implementation.
    import json
    from sources import ROOT

    stats = {
        r["panel"]: r
        for r in json.loads((ROOT / "results/slope_diagnostics.json").read_text())
    }
    assert (
        abs(direct_error.std(ddof=0) - stats["own_pair"]["taxguessmain_error"]["sd"])
        < 1e-9
    )
    assert (
        abs(direct_error.mean() - stats["own_pair"]["taxguessmain_error"]["mean"])
        < 1e-9
    )
    own = d[d.bracket == d.ownbracket]
    nominal_dev = own.tax - own.amtowntax - own.ownmarginalrate * (own.ran - own.income)
    phaseout_amount = (
        own.ownmarginalrate * 3950 * own.exemptions * own.fredexempphaseout
    )
    difference = nominal_dev - phaseout_amount
    # Source-field monetary identity, not a claim about the missing full legal
    # tax processor. All native own exemption phaseouts are zero in this sample.
    assert np.max(np.abs(difference)) < 0.01
    assert int((np.abs(nominal_dev) > 0.05).sum()) == 30
    save(
        "independent_arithmetic",
        {
            "own_pair_direct_difference_mean_error": direct_error.mean(),
            "own_pair_direct_difference_sd_error": direct_error.std(ddof=0),
            "own_pair_direct_formula_matches_general_OLS": True,
            "own_pair_variance_share_largest_respondent": centered_square.nlargest(
                1
            ).sum()
            / centered_square.sum(),
            "own_pair_variance_share_largest_10_respondents": centered_square.nlargest(
                10
            ).sum()
            / centered_square.sum(),
            "own_bracket_nominal_departure_forecasts": int(
                (np.abs(nominal_dev) > 0.05).sum()
            ),
            "own_bracket_nominal_departure_respondents": own.loc[
                np.abs(nominal_dev) > 0.05, "mid"
            ].nunique(),
            "nominal_departure_minus_stored_phaseout_tax_max_abs_dollars": np.max(
                np.abs(difference)
            ),
            "scope": "Exact source-field arithmetic on stored observations only. No extrapolated tax schedule or raw respondent output.",
        },
    )
    print("Direct two-point arithmetic and stored-tax phaseout decomposition verified.")


if __name__ == "__main__":
    main()
