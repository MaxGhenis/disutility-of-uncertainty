"""Deterministic Study 1 audit. No Stata execution, tax model or welfare changes."""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sources import DEFAULT_ARCHIVE, ROOT, frame, inventory, write_json, digest
from estimators import slope_fit, heuristic_fit, moment_outer_bounds, paired_moments

OUTCOMES = ["taxguessmain", "taxguessds", "tgw5", "tg0to100"]
NUMERIC = [
    "mid",
    "qnum",
    "ran",
    "income",
    "attention",
    "tax",
    "taxguessmain",
    "taxguessds",
    "tgw1",
    "tgw5",
    "tg0to100",
    "bracket",
    "ownbracket",
    "ownmarginalrate",
    "amtowntax",
    "fredexempphaseout",
    "ownexempphaseout",
    "fredtaxinc",
    "owntaxinc",
    "exemptions",
    "sdamount",
    "exempphaseoutthreshold",
    "localdraw",
    "highincomedraw",
    "iron",
    "spotlight",
    "filingstatus",
    "similar",
    "age",
    "Confidence_income",
    "mlmeasure",
]


def finite_json(obj):
    if isinstance(obj, dict):
        return {str(k): finite_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, np.ndarray)):
        return [finite_json(x) for x in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (float, np.floating)):
        return float(obj) if np.isfinite(obj) else None
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj


def quantiles(x):
    a = np.asarray(x, float)
    a = a[np.isfinite(a)]
    if not len(a):
        return {"n": 0}
    return {
        "n": len(a),
        "mean": float(a.mean()),
        "sd": float(a.std()),
        **{
            key: float(value)
            for key, value in zip(
                ["min", "p05", "p25", "median", "p75", "p95", "p99", "max"],
                np.quantile(a, [0, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99, 1]),
            )
        },
    }


def save(name, obj):
    write_json(ROOT / "results" / (name + ".json"), finite_json(obj))


def csv(name, rows):
    data = pd.DataFrame(rows)
    data.to_csv(ROOT / "results" / (name + ".csv"), index=False, float_format="%.12g")
    return data


def pooled(d, outcome="taxguessmain"):
    group = d.groupby("mid")
    x = d.tax - group.tax.transform("mean")
    y = d[outcome] - group[outcome].transform("mean")
    sxx = float(x @ x)
    beta = float(x @ y / sxx)
    score = (x * (y - beta * x)).groupby(d.mid).sum().to_numpy()
    g = d.mid.nunique()
    return {
        "n": len(d),
        "respondents": g,
        "coefficient": beta,
        "cluster_se": float(np.sqrt(g / (g - 1) * (score @ score) / sxx**2)),
    }


def validate(d, retained):
    if d.duplicated(["mid", "qnum"]).any():
        raise ValueError("Duplicate person/question keys")
    if d[NUMERIC].isna().any().any():
        raise ValueError("Missing audited numeric field")
    if not (
        d.groupby("mid").qnum.apply(lambda x: sorted(x) == list(range(1, 17)))
    ).all():
        raise ValueError("Incomplete 16-question panel")
    constant = [
        "attention",
        "income",
        "ownbracket",
        "ownmarginalrate",
        "amtowntax",
        "sdamount",
        "exemptions",
        "filingstatus",
    ]
    if not (d.groupby("mid")[constant].nunique() == 1).all().all():
        raise ValueError("Respondent covariate changes across forecasts")
    if not np.array_equal(
        d.highincomedraw.to_numpy(), (d.qnum > 12).astype(float).to_numpy()
    ):
        raise ValueError("High-income flag mismatch")
    expected_local = (d.qnum <= 2) | (d.bracket == d.ownbracket)
    if not np.array_equal(d.localdraw == 1, expected_local):
        raise ValueError("Local flag differs from own-pair plus bracket rule")
    parsed = pd.to_numeric(d.taxguess, errors="raise").to_numpy()
    if not np.array_equal(parsed, d.taxguessds.to_numpy()):
        raise ValueError("Native textual forecast does not reproduce taxguessds")
    primary = d[d.attention == 0].sort_values(["mid", "qnum"])
    matching = primary[primary.qnum > 2].reset_index(drop=True)
    retained = retained.sort_values(["mid", "qnum"]).reset_index(drop=True)
    if len(matching) != len(retained):
        raise ValueError("Retained estimates panel size mismatch")
    for c in NUMERIC:
        if not np.array_equal(matching[c], retained[c], equal_nan=True):
            raise ValueError("Retained forecasts do not match source: " + c)
    checks = {
        "native_text_forecasts_exactly_parsed": len(d),
        "archive_respondents": d.mid.nunique(),
        "archive_forecasts": len(d),
        "primary_respondents": primary.mid.nunique(),
        "primary_forecasts": len(primary),
        "retained_estimates_rows": len(retained),
        "retained_numeric_columns_exactly_matched": len(NUMERIC),
        "local_flag_reconstructed_exactly": True,
        "high_income_flag_reconstructed_exactly": True,
        "own_income_match_by_qnum": {
            int(q): int((x.ran == x.income).sum()) for q, x in primary.groupby("qnum")
        },
        "own_tax_match_q2_max_abs": float(
            (primary[primary.qnum == 2].tax - primary[primary.qnum == 2].amtowntax)
            .abs()
            .max()
        ),
        "own_pair_increment": quantiles(
            primary[primary.qnum == 1].ran - primary[primary.qnum == 1].income
        ),
        "processed_equals_tgw1": bool(
            np.array_equal(primary.taxguessmain, primary.tgw1)
        ),
        "processing_changed_forecasts": int(
            (primary.taxguessmain != primary.taxguessds).sum()
        ),
        "processing_changed_respondents": primary.loc[
            primary.taxguessmain != primary.taxguessds, "mid"
        ].nunique(),
        "local_outside_own_bracket": int(
            ((primary.localdraw == 1) & (primary.bracket != primary.ownbracket)).sum()
        ),
    }
    q2 = primary[primary.qnum == 2]
    checks["q2_equals_floor_own_income"] = bool(
        np.array_equal(q2.ran, np.floor(q2.income))
    )
    checks["fractional_own_income_respondents"] = int((q2.ran != q2.income).sum())
    if not checks["q2_equals_floor_own_income"]:
        raise ValueError("Native q2 differs from integer-truncated own income")
    # Explicitly confirm the diagnostic amount arithmetic using stored fields.
    candidate_taxinc = np.maximum(
        0,
        primary.ran
        - primary.sdamount
        - 3950 * primary.exemptions * (1 - primary.fredexempphaseout),
    )
    beyond_float32 = (
        primary.taxguessmain.to_numpy()
        != primary.taxguessds.to_numpy().astype(np.float32).astype(float)
    )
    checks["processed_differences_beyond_float32"] = int(beyond_float32.sum())
    checks["respondents_changed_beyond_float32"] = primary.loc[
        beyond_float32, "mid"
    ].nunique()
    checks["processed_differences_only_float32"] = int(
        ((primary.taxguessmain != primary.taxguessds) & ~beyond_float32).sum()
    )
    checks["stored_taxable_income_arithmetic_max_abs"] = float(
        np.max(np.abs(candidate_taxinc - primary.fredtaxinc))
    )
    checks["within_bracket_phaseout_forecasts"] = int(
        (
            (primary.bracket == primary.ownbracket) & (primary.fredexempphaseout > 0)
        ).sum()
    )
    save("native_checks", checks)
    return primary, retained


def benchmarks(d, retained):
    panels = {
        "full": d.qnum > 2,
        "mid_range": (d.qnum > 2) & (d.highincomedraw == 0),
        "local": d.localdraw == 1,
    }
    result = {name: pooled(d[mask]) for name, mask in panels.items()}
    expected = {
        "full": (58758, 0.62, 0.010),
        "mid_range": (41970, 0.82, 0.013),
        "local": (17937, 0.81, 0.043),
    }
    for name, (n, b, se) in expected.items():
        r = result[name]
        # Published printed precision, independently transcribed Table 1.
        assert (
            r["n"] == n
            and round(r["coefficient"], 2) == b
            and round(r["cluster_se"], 3) == se
        ), (name, r)
    cache = json.loads(
        (ROOT / "evidence/completed-adapter-benchmark.json").read_text()
    )["table1_pooled_panels"]
    for name in result:
        result[name]["difference_from_completed_adapter"] = (
            result[name]["coefficient"] - cache[name]["coefficient"]
        )
        result[name]["se_difference_from_completed_adapter"] = (
            result[name]["cluster_se"] - cache[name]["clustered_standard_error"]
        )
        assert abs(result[name]["difference_from_completed_adapter"]) < 1e-12
        assert abs(result[name]["se_difference_from_completed_adapter"]) < 1e-12
    save("pooled_benchmarks", result)
    csv("pooled_benchmarks", [{"panel": k, **v} for k, v in result.items()])
    positive = retained[retained.amtowntax > 0]
    records = []
    matrices = {k: np.zeros((11, 11), dtype=int) for k in range(1, 5)}
    for mid, g in positive.groupby("mid", sort=True):
        for k in range(1, 5):
            p = g[g.highincomedraw == 0] if k <= 2 else g
            r = (
                p[f"residmisperception{1 if k==2 else 2}"].to_numpy()
                if k in (2, 4)
                else None
            )
            fit = heuristic_fit(p.tax, p.iron, p.spotlight, p.taxguessmain, r)
            native = p[[f"gamma_i{k}", f"gamma_s{k}"]].iloc[0].to_numpy(float)
            assert p[[f"gamma_i{k}", f"gamma_s{k}"]].nunique(dropna=False).eq(1).all()
            row = {
                "variant": k,
                "rank": fit["rank"],
                "native_finite": bool(np.isfinite(native).all()),
                "condition": fit["condition"],
            }
            if fit["gamma"] is not None:
                b = fit["gamma"]
                row.update(
                    gamma_i=b[0],
                    gamma_s=b[1],
                    iid_se_i=np.sqrt(fit["iid_covariance"][0, 0]),
                    iid_se_s=np.sqrt(fit["iid_covariance"][1, 1]),
                    grid_gap=fit["grid_gap"],
                )
                if row["native_finite"]:
                    row["max_abs_native_difference"] = np.max(np.abs(native - b))
                    base = p.tax.to_numpy() + (r if r is not None else 0)
                    x = np.column_stack([p.iron - base, p.spotlight - base])
                    nsse = np.sum((p.taxguessmain - base - x @ native) ** 2)
                    row["native_relative_sse_excess"] = (nsse - fit["sse"]) / max(
                        1, fit["sse"]
                    )
                ii, jj = np.rint(fit["grid"] * 10).astype(int)
                matrices[k][ii, jj] += 1
            records.append(row)
    rec = pd.DataFrame(records)
    rows = []
    for k, g in rec.groupby("variant"):
        rows.append(
            {
                "variant": int(k),
                "respondents": len(g),
                "rank2": int((g["rank"] == 2).sum()),
                "native_missing": int((~g.native_finite).sum()),
                "max_abs_difference": quantiles(g.max_abs_native_difference),
                "native_relative_sse_excess": quantiles(g.native_relative_sse_excess),
                "condition": quantiles(g.condition),
                "iid_se_i": quantiles(g.iid_se_i),
                "gamma_i": quantiles(g.gamma_i),
                "gamma_s": quantiles(g.gamma_s),
                "grid_counts": matrices[int(k)].tolist(),
                "corner_counts": {
                    "truth": int(matrices[k][0, 0]),
                    "ironing": int(matrices[k][10, 0]),
                    "spotlighting": int(matrices[k][0, 10]),
                },
            }
        )
        csv(f"appendix_A{k+4}_grid", matrices[k])
    published = json.loads((ROOT / "evidence/published-grids.json").read_text())[
        "matrices"
    ]
    for k in range(1, 5):
        if matrices[k].tolist() != published[f"A{k+4}"]:
            raise ValueError(f"Published appendix A{k+4} grid mismatch")
    all_persons = retained.drop_duplicates("mid")
    save(
        "individual_archive_selection",
        {
            "retained_respondents": len(all_persons),
            "zero_own_tax_respondents": int((all_persons.amtowntax == 0).sum()),
            "positive_own_tax_respondents": positive.mid.nunique(),
            "native_missing_all": {
                k: int(all_persons[f"gamma_i{k}"].isna().sum()) for k in range(1, 5)
            },
            "positive_tax_rank2_recovery": "OLS solves all 3552; source-missing positive-tax fits are retained as newly recovered calculations, not source output",
            "generation_limit": "Archive contains retained gamma fields and Figure 6 usage, but no script creating individualestimates.dta.",
        },
    )
    save("individual_benchmarks", rows)


def individual_slopes(d):
    masks = {
        "own_pair": d.qnum <= 2,
        "native_local": d.localdraw == 1,
        "own_bracket": (d.localdraw == 1) & (d.bracket == d.ownbracket),
        "random_mid": (d.qnum > 2) & (d.highincomedraw == 0),
        "random_full": d.qnum > 2,
    }
    rows = []
    for name, mask in masks.items():
        for mid, g in d[mask].groupby("mid", sort=True):
            x = g.ran.to_numpy(float)
            t = g.tax.to_numpy(float)
            row = {
                "panel": name,
                "mid": mid,
                "n": len(g),
                "distinct_x": g.ran.nunique(),
                "income": g.income.iloc[0],
                "span": float(np.ptp(x)),
                "filingstatus": g.filingstatus.iloc[0],
                "nominal_rate": g.ownmarginalrate.iloc[0],
                "phaseout_any": bool((g.fredexempphaseout > 0).any()),
                "cross_bracket": bool((g.bracket != g.ownbracket).any()),
                "similar": g.similar.iloc[0],
                "age": g.age.iloc[0],
                "changed_processing": bool((g.taxguessmain != g.taxguessds).any()),
                "nominal_max_deviation": float(
                    np.max(
                        np.abs(
                            t
                            - g.amtowntax.to_numpy()
                            - g.ownmarginalrate.to_numpy() * (x - g.income.to_numpy())
                        )
                    )
                ),
            }
            if len(np.unique(x)) >= 2:
                truth = slope_fit(x, t)
                row.update(
                    true_slope=truth["slope"],
                    true_max_residual=truth["max_abs_residual"],
                    positive_tax_variation=bool(np.ptp(t) > 0),
                )
                for outcome in OUTCOMES:
                    fit = slope_fit(x, g[outcome])
                    if outcome == "taxguessmain":
                        row.update(
                            {
                                k: v
                                for k, v in fit.items()
                                if k not in ("n", "distinct_x", "span")
                            }
                        )
                    row[outcome + "_slope"] = fit["slope"]
                    row[outcome + "_error"] = fit["slope"] - truth["slope"]
            rows.append(row)
    slopes = pd.DataFrame(rows)
    summaries = []
    for name, g in slopes.groupby("panel", sort=False):
        valid = g[g.true_slope.notna()]
        summaries.append(
            {
                "panel": name,
                "respondents": len(g),
                "forecasts": int(g.n.sum()),
                "n_distribution": g.n.value_counts().sort_index().to_dict(),
                "slope_identified": len(valid),
                "n_ge3_distinct": int((g.distinct_x >= 3).sum()),
                "zero_tax_variation": int(
                    (valid.positive_tax_variation == False).sum()
                ),
                "observed_nonlinear_gt_005": int(
                    ((g.distinct_x >= 3) & (g.true_max_residual > 0.05)).sum()
                ),
                "nominal_line_fails_gt_005": int(
                    (g.nominal_max_deviation > 0.05).sum()
                ),
                "two_points_are_not_affine_evidence": int((g.distinct_x == 2).sum()),
                **{
                    k: quantiles(g[k])
                    for k in [
                        "span",
                        "true_max_residual",
                        "nominal_max_deviation",
                        "slope",
                        "taxguessmain_error",
                        "true_slope",
                        "iid_se",
                        "hc3_se",
                        "max_leverage",
                        "max_loo_change",
                    ]
                },
                "slope_outside_0_1": int(((valid.slope < 0) | (valid.slope > 1)).sum()),
                "processing_changed_respondents": int(g.changed_processing.sum()),
                "processing_slope_change": quantiles(
                    (g.taxguessmain_slope - g.taxguessds_slope).abs()
                ),
            }
        )
    save("slope_diagnostics", summaries)
    selection = []
    for panel in [
        "own_pair",
        "native_local",
        "own_bracket",
        "random_mid",
        "random_full",
    ]:
        base = slopes[(slopes.panel == panel) & slopes.true_slope.notna()]
        for n in [2, 3, 4, 6]:
            for span in [0, 1000, 5000, 10000, 20000]:
                for affine in [False, True]:
                    g = base[(base.distinct_x >= n) & (base.span >= span)]
                    if affine:
                        g = g[(g.distinct_x >= 3) & (g.true_max_residual <= 0.05)]
                    if not len(g):
                        continue
                    selection.append(
                        {
                            "panel": panel,
                            "min_distinct": n,
                            "min_span": span,
                            "observed_affine_screen": affine,
                            "n": len(g),
                            "median_income": g.income.median(),
                            "median_span": g.span.median(),
                            "mean_true_slope": g.true_slope.mean(),
                            "zero_tax_share": (
                                g.positive_tax_variation == False
                            ).mean(),
                            "share_single": (g.filingstatus == 1).mean(),
                            "share_similar": g.similar.mean(),
                            "mean_error": g.taxguessmain_error.mean(),
                            "sd_error": g.taxguessmain_error.std(ddof=0),
                            "rmse_error": np.sqrt(np.mean(g.taxguessmain_error**2)),
                            "median_iid_se": g.iid_se.median(),
                            "median_hc3_se": g.hc3_se.median(),
                            "median_max_leverage": g.max_leverage.median(),
                            "share_leverage_gt_09": (g.max_leverage > 0.9).mean(),
                            "median_max_loo_change": g.max_loo_change.median(),
                            "median_box_radius_100": 100 * g.l1_weights.median(),
                            "median_rms_radius_100": (
                                100 * np.sqrt(g.n) * g.l2_weights
                            ).median(),
                        }
                    )
    csv("selection", selection)
    process = []
    for name, g in slopes.groupby("panel", sort=False):
        g = g[g.true_slope.notna()]
        for outcome in OUTCOMES:
            e = g[outcome + "_error"]
            process.append(
                {
                    "panel": name,
                    "outcome": outcome,
                    "n": len(g),
                    "mean_error": e.mean(),
                    "sd_error": e.std(ddof=0),
                    "rmse_error": np.sqrt(np.mean(e**2)),
                    "median_error": e.median(),
                    "p95_abs_error": e.abs().quantile(0.95),
                    "slope_change_gt_001": int(
                        (
                            np.abs(g[outcome + "_slope"] - g.taxguessmain_slope) > 0.01
                        ).sum()
                    ),
                }
            )
    csv("processing_sensitivity", process)
    # Every bounded moment row has an explicit finite selected-sample estimand.
    bounds = []
    for panel, n, span, affine in [
        ("own_pair", 2, 0, False),
        ("native_local", 2, 0, False),
        ("own_bracket", 3, 0, True),
        ("own_bracket", 4, 5000, True),
        ("own_bracket", 4, 10000, True),
    ]:
        g = slopes[
            (slopes.panel == panel)
            & (slopes.distinct_x >= n)
            & (slopes.span >= span)
            & slopes.true_slope.notna()
        ]
        if affine:
            g = g[g.true_max_residual <= 0.05]
        for cap in [0, 50, 100, 500, 1000]:
            for kind in ["box", "rms"]:
                r = (
                    cap * g.l1_weights
                    if kind == "box"
                    else cap * np.sqrt(g.n) * g.l2_weights
                )
                b = moment_outer_bounds(g.taxguessmain_error, r)
                bounds.append(
                    {
                        "panel": panel,
                        "min_distinct": n,
                        "min_span": span,
                        "observed_affine_screen": affine,
                        "error_assumption": kind,
                        "dollar_cap": cap,
                        "n": len(g),
                        "median_slope_radius": r.median(),
                        "p95_slope_radius": r.quantile(0.95),
                        **{
                            key + "_" + side: v
                            for key in ["bias", "sd", "rmse"]
                            for side, v in zip(["lower", "upper"], b[key])
                        },
                    }
                )
    csv("finite_sample_bounds", bounds)
    return slopes


def repeated(d, slopes):
    rows = []
    for panel in ["own_bracket", "random_mid", "random_full"]:
        mask = (
            ((d.localdraw == 1) & (d.bracket == d.ownbracket))
            if panel == "own_bracket"
            else (
                (d.qnum > 2)
                & ((d.highincomedraw == 0) if panel == "random_mid" else True)
            )
        )
        for split in ["income_interleaved", "question_parity"]:
            pairs = []
            for mid, g in d[mask].groupby("mid", sort=True):
                if split == "income_interleaved":
                    g = g.sort_values(["ran", "qnum"])
                    a, b = g.iloc[::2], g.iloc[1::2]
                else:
                    a, b = g[g.qnum % 2 == 0], g[g.qnum % 2 == 1]
                if (
                    len(a) < 2
                    or len(b) < 2
                    or a.ran.nunique() < 2
                    or b.ran.nunique() < 2
                ):
                    continue
                fits = {}
                for outcome in ["taxguessmain", "taxguessds"]:
                    fits[outcome + "_a"] = slope_fit(a.ran, a[outcome] - a.tax)["slope"]
                    fits[outcome + "_b"] = slope_fit(b.ran, b[outcome] - b.tax)["slope"]
                fits.update(
                    mid=mid,
                    span_a=np.ptp(a.ran),
                    span_b=np.ptp(b.ran),
                    min_n=min(len(a), len(b)),
                )
                pairs.append(fits)
            pair = pd.DataFrame(pairs).merge(
                slopes[slopes.panel == panel][
                    ["mid", "true_max_residual", "distinct_x", "span"]
                ],
                on="mid",
                validate="one_to_one",
            )
            for affine in [False, True]:
                for min_span in [0, 1000, 5000, 10000]:
                    p = pair[(pair.span_a >= min_span) & (pair.span_b >= min_span)]
                    if affine:
                        p = p[(p.distinct_x >= 3) & (p.true_max_residual <= 0.05)]
                    if len(p) < 2:
                        continue
                    for outcome in ["taxguessmain", "taxguessds"]:
                        moments = paired_moments(p[outcome + "_a"], p[outcome + "_b"])
                        rows.append(
                            {
                                "panel": panel,
                                "split": split,
                                "observed_affine_screen": affine,
                                "min_half_span": min_span,
                                "outcome": outcome,
                                "median_half_span_a": p.span_a.median(),
                                "median_half_span_b": p.span_b.median(),
                                **moments,
                            }
                        )
    csv("repeated_measures", rows)


def heaping(d):
    rows = []
    for name, mask in [
        ("all", d.qnum > 0),
        ("pair", d.qnum <= 2),
        ("random", d.qnum > 2),
    ]:
        for outcome in OUTCOMES:
            y = d.loc[mask, outcome].to_numpy()
            rows.append(
                {
                    "panel": name,
                    "outcome": outcome,
                    "n": len(y),
                    "zero_share": np.mean(y == 0),
                    "multiple_100_share": np.mean(
                        np.isclose(y / 100, np.round(y / 100), atol=1e-7, rtol=0)
                    ),
                    "multiple_1000_share": np.mean(
                        np.isclose(y / 1000, np.round(y / 1000), atol=1e-7, rtol=0)
                    ),
                }
            )
    csv("heaping", rows)
    pair = d[d.qnum <= 2].pivot(
        index="mid", columns="qnum", values=["ran", "tax", "taxguessmain", "taxguessds"]
    )
    extra = {
        "identical_processed_pair_forecasts": int(
            (pair.taxguessmain[1] == pair.taxguessmain[2]).sum()
        ),
        "identical_prewinsor_pair_forecasts": int(
            (pair.taxguessds[1] == pair.taxguessds[2]).sum()
        ),
        "identical_income_pair": int((pair.ran[1] == pair.ran[2]).sum()),
        "pair_slope_abs_above_one": int(
            (
                np.abs(
                    (pair.taxguessmain[1] - pair.taxguessmain[2])
                    / (pair.ran[1] - pair.ran[2])
                )
                > 1
            ).sum()
        ),
    }
    # Incidental repeats at exactly the same income provide occasional paired
    # outcome discrepancies, but cannot establish independent errors or waves.
    duplicate = d[d.duplicated(["mid", "ran"], keep=False)]
    diffs = []
    for _, g in duplicate.groupby(["mid", "ran"]):
        diffs.append(float(np.ptp(g.taxguessmain)))
    extra.update(
        incidental_duplicate_income_groups=len(diffs),
        incidental_duplicate_income_respondents=duplicate.mid.nunique(),
        duplicate_income_outcome_ranges=quantiles(diffs),
    )
    save("pair_repeats", extra)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    args = p.parse_args()
    members = inventory(args.archive)
    d = frame(members, "RJT_study_1_data", NUMERIC + ["taxguess"])
    est = frame(
        members,
        "individualestimates",
        NUMERIC
        + ["gamma_" + t + str(k) for k in range(1, 5) for t in ["i", "s"]]
        + ["residmisperception1", "residmisperception2"],
    )
    # Promote native float32 before subtraction or multiplication. Retain exact
    # stored values; never silently round rates to nominal legal parameters.
    for f in [d, est]:
        for c in f:
            if f[c].dtype.kind == "f":
                f[c] = f[c].astype(float)
    d, est = validate(d, est)
    benchmarks(d, est)
    slopes = individual_slopes(d)
    repeated(d, slopes)
    heaping(d)
    print(
        "Audit complete: pinned native checks, benchmarks, slope and repeated-measure diagnostics."
    )


if __name__ == "__main__":
    main()
