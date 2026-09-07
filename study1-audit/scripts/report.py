"""Render quantitative report from checked aggregate tables, never hand-copy numbers."""

import json
import re
import pandas as pd
from sources import ROOT


def table(headers, rows):
    return "\n".join(
        [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        + ["| " + " | ".join(map(str, row)) + " |" for row in rows]
    )


def main():
    load = lambda n: json.loads((ROOT / "results" / f"{n}.json").read_text())
    data = lambda n: pd.read_csv(ROOT / "results" / f"{n}.csv")
    native = load("native_checks")
    diag = {r["panel"]: r for r in load("slope_diagnostics")}
    selection = data("selection")
    filt = (selection.panel == "own_bracket") & selection.observed_affine_screen
    selected = lambda n, span: selection[
        filt & (selection.min_distinct == n) & (selection.min_span == span)
    ].iloc[0]
    strict3 = selected(3, 0)
    strict4 = selected(4, 5000)
    strict10 = selected(4, 10000)
    process = data("processing_sensitivity")
    p = process[process.panel == "random_full"].set_index("outcome")
    bounds = data("finite_sample_bounds")
    b = bounds[(bounds.error_assumption == "box") & (bounds.dollar_cap == 100)]
    pairb = b[b.panel == "own_pair"].iloc[0]
    selb = b[
        (b.panel == "own_bracket") & (b.min_distinct == 4) & (b.min_span == 5000)
    ].iloc[0]
    aff = data("affine_belief_falsification")
    aff = aff[
        (aff.panel == "own_bracket")
        & (aff.outcome == "taxguessmain")
        & (aff.min_n == 4)
        & (aff.min_span == 5000)
    ]
    rep = data("repeated_measures")
    r = rep[(rep.outcome == "taxguessmain") & (rep.split == "income_interleaved")]
    local5 = r[
        (r.panel == "own_bracket")
        & r.observed_affine_screen
        & (r.min_half_span == 5000)
    ].iloc[0]
    local10 = r[
        (r.panel == "own_bracket")
        & r.observed_affine_screen
        & (r.min_half_span == 10000)
    ].iloc[0]
    broad = r[
        (r.panel == "random_full") & ~r.observed_affine_screen & (r.min_half_span == 0)
    ].iloc[0]
    corr = data("correlated_error_sensitivity")
    c = corr[(corr.panel == "own_bracket") & (corr.min_half_span == 5000)].reset_index(
        drop=True
    )
    design = data("prospective_design")
    design = design[design.assumed_iid_dollar_sd == 500].set_index("design")
    pooled = load("pooled_benchmarks")
    values = {
        "pooled_table": table(
            ["Panel", "Forecasts", "Coefficient", "Cluster SE"],
            [
                [
                    name.replace("_", " "),
                    f"{pooled[name]['n']:,}",
                    f"{pooled[name]['coefficient']:.6f}",
                    f"{pooled[name]['cluster_se']:.6f}",
                ]
                for name in ["local", "mid_range", "full"]
            ],
        ),
        "gamma_se": f"{load('individual_benchmarks')[2]['iid_se_i']['median']:.3f}",
        "parsed_count": f"{native['native_text_forecasts_exactly_parsed']:,}",
        "float_only": str(native["processed_differences_only_float32"]),
        "processing_real": str(native["processed_differences_beyond_float32"]),
        "processing_people": str(native["respondents_changed_beyond_float32"]),
        "full_processed_sd": f"{100*p.loc['taxguessmain','sd_error']:.2f}",
        "full_raw_sd": f"{100*p.loc['taxguessds','sd_error']:.2f}",
        "full_five_sd": f"{100*p.loc['tgw5','sd_error']:.2f}",
        "heaping": f"{100*data('heaping').query('panel == \"all\" and outcome == \"taxguessds\"').iloc[0].multiple_100_share:.1f}",
        "nominal_departure": f"{diag['own_bracket']['nominal_max_deviation']['max']:,.2f}",
        "pair_outside": f"{diag['own_pair']['slope_outside_0_1']:,}",
        "local_iid_se": f"{100*strict3.median_iid_se:.2f}",
        "local_hc3_se": f"{100*strict3.median_hc3_se:.2f}",
        "local_loo": f"{100*strict3.median_max_loo_change:.2f}",
        "selected_income": f"{strict4.median_income:,.0f}",
        "min_cap": f"{aff.iloc[0].median_minimum_dollar_error:,.2f}",
        "min_cap_p95": f"{aff.iloc[0].p95_minimum_dollar_error:,.2f}",
        "pair_radius": f"{100*pairb.median_slope_radius:.2f}",
        "selected_radius": f"{100*selb.median_slope_radius:.2f}",
        "selected_sd_bounds": f"{100*selb.sd_lower:.2f}–{100*selb.sd_upper:.2f}",
        "broad_corr": f"{broad.correlation:.3f}",
        "naive_sd": f"{100*c.iloc[0].implied_common_target_sd:.2f}",
        "half_rho": f"{c.iloc[2].assumed_error_correlation:.3f}",
        "half_sd": f"{100*c.iloc[2].implied_common_target_sd:.2f}",
        "zero_rho": f"{c.iloc[-1].assumed_error_correlation:.3f}",
        "design_se": f"{100*design.loc['six_points_30000_span','one_session_slope_se']:.2f}",
        "pair_design_se": f"{100*design.loc['pair_500_span','one_session_slope_se']:.2f}",
    }
    slope_rows = []
    for key, title in [
        ("own_pair", "Own-income pair"),
        ("native_local", "Native local"),
    ]:
        g = diag[key]
        slope_rows.append(
            [
                title,
                f"{g['respondents']:,}",
                f"${g['span']['median']:,.0f}",
                f"{100*g['taxguessmain_error']['sd']:,.2f}",
                f"{g['max_leverage']['median']:.3f}",
            ]
        )
    for g, title in [
        (strict3, "Own bracket, ≥3 points, observed affine"),
        (strict4, "Also ≥4 points and ≥$5,000 span"),
        (strict10, "Also ≥4 points and ≥$10,000 span"),
    ]:
        slope_rows.append(
            [
                title,
                f"{g.n:,}",
                f"${g.median_span:,.0f}",
                f"{100*g.sd_error:,.2f}",
                f"{g.median_max_leverage:.3f}",
            ]
        )
    g = diag["random_full"]
    slope_rows.append(
        [
            "All 14 random draws",
            f"{g['respondents']:,}",
            f"${g['span']['median']:,.0f}",
            f"{100*g['taxguessmain_error']['sd']:,.2f}",
            f"{g['max_leverage']['median']:.3f}",
        ]
    )
    values["slope_table"] = table(
        [
            "Sample",
            "Respondents",
            "Median span",
            "Observed error SD (pp)",
            "Median largest leverage",
        ],
        slope_rows,
    )
    values["affine_table"] = table(
        [
            "Assumed per-answer error cap",
            "Compatible respondents",
            "Compatible share",
            "Median slope-set width among compatible (pp)",
        ],
        [
            [
                f"${g.dollar_cap:,.0f}",
                f"{g.compatible:,}",
                f"{100*g.compatible_share:.1f}%",
                f"{100*g.median_width_among_compatible:.2f}",
            ]
            for _, g in aff.iterrows()
        ],
    )
    values["repeat_table"] = table(
        [
            "Split sample",
            "Respondents",
            "Correlation",
            "Covariance (pp²)",
            "Jackknife SE (pp²)",
        ],
        [
            [
                title,
                f"{int(g.n):,}",
                f"{g.correlation:.3f}",
                f"{10000*g.covariance:.1f}",
                f"{10000*g.covariance_jackknife_se:.1f}",
            ]
            for title, g in [
                ("Own bracket, observed affine; each half spans ≥$5,000", local5),
                ("Same; each half spans ≥$10,000", local10),
                ("Full random-income range", broad),
            ]
        ],
    )
    text = (ROOT / "report.template.md").read_text()
    for k, v in values.items():
        text = text.replace("{{" + k + "}}", v)
    if re.search(r"\{\{[^}]+\}\}", text):
        raise ValueError("Unfilled report placeholder")
    (ROOT / "REPORT.md").write_text(text)
    print("Generated REPORT.md from checked results.")


if __name__ == "__main__":
    main()
