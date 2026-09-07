"""Verified Rees-Jones/Taubinsky archive to scoped observed-error calibration.

Reads the public, checksum-pinned Stata archive without executing its code or
redistributing microdata. Study 2 choices identify intervals conditional on
monotone monetary choice, not latent beliefs or a national welfare parameter.
"""

import argparse
import csv
import io
import json
import platform
from dataclasses import asdict
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
import pandas as pd

from taxuncertainty.analysis import signed_errors, tax_forecasts
from taxuncertainty.analysis.signed_errors import (
    RATE_COLUMNS,
    RateObservation,
    RateSample,
    calibration_report,
    load_rate_sample,
)

ARCHIVE_URL = "https://www.dropbox.com/s/2q47bj8arbcgr3i/Schmeduling%20Replication%20Code.zip?dl=1"
ARCHIVE_SHA256 = "c578518776c9cd97cc0bcf340558a9574ed2088cfeb5d1b610274e5d7ab48b15"
MEMBERS = {
    "Replication Code/README.txt": "b7ca568355ec9a2ac958f46fe8afc206be397fe901ffa780854ff1f3ff57b507",
    "Replication Code/Study 1/Table 1.do": "c744801b986785c8dda03b84c28a85f0f55583f31cb34cc3c9ad305b13fd7b9f",
    "Replication Code/Study 1/RJT_study_1_data.dta": "bcce8a42c02febba3e5906d9bfba1357d2bad904f2bd2e1bbea2b73611304e83",
    "Replication Code/Study 2/Table 4.do": "0c6622410f47209b2cbdf7bd1c32adcc6e9d6f05729dec1722cee40ba9de2754",
    "Replication Code/Study 2/RJT_study_2_data.dta": "d326b9a3e64480d06ebbe98f8d1eddcf238abc2b5e74af3699a9865bf598434b",
}
OFFERS = (0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21)
STUDY1_COLUMNS = (
    "mid",
    "qnum",
    "attention",
    "tax",
    "taxguessmain",
    "taxguessds",
    "tgw1",
    "ran",
    "income",
    "bracket",
    "ownbracket",
    "localdraw",
    "highincomedraw",
)


def source_hashes():
    """Hash every calculation dependency used for these empirical outputs."""
    return {
        Path(p).name: sha256(Path(p).read_bytes()).hexdigest()
        for p in (__file__, signed_errors.__file__, tax_forecasts.__file__)
    }


def read_archive(path):
    """Reject changed bytes before interpreting any native variable names."""
    raw = Path(path).read_bytes()
    if sha256(raw).hexdigest() != ARCHIVE_SHA256:
        raise ValueError("replication archive checksum mismatch")
    with ZipFile(io.BytesIO(raw)) as archive:
        contents = {}
        for name, digest in MEMBERS.items():
            contents[name] = archive.read(name)
            if sha256(contents[name]).hexdigest() != digest:
                raise ValueError(f"archive member checksum mismatch: {name}")
    frames = []
    for study in (1, 2):
        data = contents[f"Replication Code/Study {study}/RJT_study_{study}_data.dta"]
        # Numeric codes must survive Stata value labels. Study 1 has a malformed
        # unused string label; pandas' documented Latin-1 fallback is harmless
        # for the numeric columns selected here and is left visible to callers.
        frames.append(
            pd.read_stata(
                io.BytesIO(data),
                convert_categoricals=False,
                columns=list(STUDY1_COLUMNS) if study == 1 else None,
            )
        )
    return tuple(frames)


def validate_study2(frame):
    """Independently reconstruct all monotonicity and endpoint selection flags."""
    choices = frame[[f"q21_{i}" for i in range(12)]].to_numpy()
    if not np.isin(choices, ["A", "B"]).all():
        raise ValueError("native MPL choices must all be A or B")
    for key in ("irrational", "inattentive_1", "inattentive_2", "table"):
        if not frame[key].isin([0, 1]).all():
            raise ValueError(f"invalid native flag: {key}")
    rates = frame[["ATR", "MTR"]].to_numpy(float)
    if not np.isfinite(rates).all() or not ((rates >= 0) & (rates <= 1)).all():
        raise ValueError("native ATR/MTR must be finite fractional rates")
    if not frame.condition.isin(["1_kink", "4_kink"]).all():
        raise ValueError("unknown schedule condition")
    b = choices == "B"
    inconsistent = (np.diff(b.astype(int), axis=1) < 0).any(axis=1)
    first_b = np.where(b.any(axis=1), b.argmax(axis=1) + 1, 13)
    endpoints = b[:, 0] | ~b[:, -1]
    if not np.array_equal(inconsistent, frame.irrational == 1):
        raise ValueError("irrational flag disagrees with raw choices")
    if not np.array_equal(endpoints, frame.inattentive_1 == 1):
        raise ValueError("endpoint flag disagrees with raw choices")
    if not np.array_equal(first_b[~inconsistent], frame.switchingpoint[~inconsistent]):
        raise ValueError("switchingpoint disagrees with raw choices")
    if not frame.switchingpoint[inconsistent].isna().all():
        raise ValueError("nonmonotone rows must have missing switchingpoint")
    return {
        "raw_choice_rows_checked": len(frame),
        "irrational_mismatches": 0,
        "endpoint_flag_mismatches": 0,
        "switchingpoint_mismatches": 0,
        "final_attention_flag": "native flag only; underlying answer not in archive",
    }


def study2_masks(frame):
    monotone = frame.irrational == 0
    endpoints = frame.inattentive_1 == 0
    attention = frame.inattentive_2 == 0
    return {
        "primary": monotone & endpoints & attention,
        "include_final_attention_failures": monotone & endpoints,
        "include_endpoint_failures": monotone & attention,
        "include_both_attention_failures": monotone,
    }


def study2_sample(frame, convention="author", include_final_attention=False):
    """Map native A/B decisions through the already-tested payoff inequalities.

    Stable row ordinals identify respondents: the native file has no person ID.
    Author support [0,1] follows footnote 28; payoff-only support is [-.05,1]
    among retained endpoint-screen passers. No open bin gets a guessed midpoint.
    """
    validate_study2(frame)
    if convention not in ("author", "payoff"):
        raise ValueError("convention must be author or payoff")
    key = "include_final_attention_failures" if include_final_attention else "primary"
    mask = study2_masks(frame)[key].to_numpy()
    rows = []
    for ordinal in np.flatnonzero(mask):
        native = frame.iloc[ordinal]
        lo, hi = tax_forecasts.mpl_interval(
            OFFERS,
            [native[f"q21_{i}"] == "A" for i in range(12)],
            taxable_increment=20,
            rate_support=(0, 1) if convention == "author" else None,
        )
        rows.append(
            RateObservation(
                f"study2-row-{ordinal + 1:06d}",
                "mpl",
                float(native.MTR),
                lo,
                hi,
            )
        )
    return RateSample(rows)


def midpoint_outcome(frame):
    """Source Table 4 DO lines 14-42, including its 0/1 open-bin imputations.

    Only used to reproduce published regressions. These imputations do NOT
    bound the perceived rate of respondents failing the endpoint screen.
    """
    k = frame.switchingpoint.to_numpy(float)
    return np.select(
        [k == 1, k == 2, k == 12, k == 13],
        [1, 0.975, 0.025, 0],
        default=1.2 - 0.1 * k,
    )


def midpoint_ols(frame):
    """Classical OLS and homoskedastic SEs matching Stata's unweighted reg."""
    y = midpoint_outcome(frame)
    x = np.column_stack([np.ones(len(frame)), frame[["ATR", "MTR"]].to_numpy(float)])
    if len(y) <= 3 or not np.isfinite(y).all() or np.linalg.matrix_rank(x) != 3:
        raise ValueError("midpoint OLS requires finite outcomes and full rank")
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    covariance = (residual @ residual / (len(y) - 3)) * np.linalg.inv(x.T @ x)
    total = beta[1] + beta[2]
    gradient = np.array([0, beta[2], -beta[1]]) / total**2
    return {
        "n": len(y),
        "coefficients": dict(zip(("constant", "ATR", "MTR"), beta.tolist())),
        "standard_errors": dict(
            zip(("constant", "ATR", "MTR"), np.sqrt(np.diag(covariance)).tolist())
        ),
        "r_squared": float(1 - residual @ residual / ((y - y.mean()) @ (y - y.mean()))),
        "ATR_fraction_of_total_coefficient": float(beta[1] / total),
        "ATR_fraction_delta_se": float(np.sqrt(gradient @ covariance @ gradient)),
        "interpretation": "midpoint conditional-mean regression; ratio is not an identified latent population type share",
    }


def fixed_effects_scale(frame):
    """Table 1 within-person OLS; clustered SE finite-sample factor G/(G-1)."""
    xy = frame[["tax", "taxguessmain"]].astype(float)
    centered = xy - xy.groupby(frame.mid).transform("mean")
    x, y = centered.to_numpy().T
    n, g = len(frame), frame.mid.nunique()
    sxx = x @ x
    if g < 2 or sxx <= 0:
        raise ValueError("fixed-effects regression needs two groups and tax variation")
    beta = x @ y / sxx
    scores = pd.Series(x * (y - beta * x), index=frame.index).groupby(frame.mid).sum()
    # One slope: xtreg's (N-1)/(N-K) factor equals 1. Absorbed fixed
    # effects are not subtracted in this cluster correction.
    variance = g / (g - 1) * (scores.to_numpy() @ scores.to_numpy()) / sxx**2
    by_tax_variation = centered.tax.pow(2).groupby(frame.mid).sum()
    return {
        "forecasts": n,
        "respondents": int(g),
        "coefficient": float(beta),
        "clustered_standard_error": float(np.sqrt(variance)),
        "respondents_with_positive_tax_variation": int((by_tax_variation > 0).sum()),
        "estimand": "within-person true-tax-variation weighted scale; not mean signed rate error",
    }


def study1_benchmarks(frame):
    if frame.duplicated(["mid", "qnum"]).any():
        raise ValueError("duplicate native Study 1 respondent/forecast")
    if frame[list(STUDY1_COLUMNS)].isna().any().any():
        raise ValueError("missing native Study 1 field")
    data = frame[frame.attention == 0]
    local = data.localdraw == 1
    within = data.bracket == data.ownbracket
    panels = {
        "full": data.qnum > 2,
        "mid_range": (data.qnum > 2) & (data.highincomedraw == 0),
        "local": local,
    }
    return {
        "archive_respondents": int(frame.mid.nunique()),
        "archive_forecasts": len(frame),
        "retained_respondents": int(data.mid.nunique()),
        "retained_forecasts": len(data),
        "source_preprocessing": "archive already excludes 195 survey completers; cleaning from original 4828 is not reproducible from this archive",
        "processed_equals_tgw1": bool(np.array_equal(data.taxguessmain, data.tgw1)),
        "forecasts_changed_from_taxguessds": int(
            (data.taxguessmain != data.taxguessds).sum()
        ),
        "local_flag_outside_own_bracket": int((local & ~within).sum()),
        "table1_pooled_panels": {
            key: fixed_effects_scale(data[mask]) for key, mask in panels.items()
        },
        "latent_dispersion_identified": False,
    }


def reproduce(study1, study2):
    checks = validate_study2(study2)
    masks = study2_masks(study2)
    primary = study2[masks["primary"]]
    samples = {key: study2_sample(study2, key) for key in ("author", "payoff")}
    midpoint = RateSample(
        RateObservation(
            r.respondent_id,
            r.observation_id,
            r.true_rate,
            (r.perceived_rate_lower + r.perceived_rate_upper) / 2,
            (r.perceived_rate_lower + r.perceived_rate_upper) / 2,
        )
        for r in samples["author"].observations
    )
    waterfall = [
        len(study2),
        int((study2.inattentive_2 == 0).sum()),
        int(((study2.inattentive_2 == 0) & (study2.irrational == 0)).sum()),
        len(primary),
    ]
    subgroups = {
        "simple": primary.condition == "1_kink",
        "complex": primary.condition == "4_kink",
        "table_reopened": primary.table == 1,
        "table_not_reopened": primary.table == 0,
    }
    return {
        "schema_version": 1,
        "status": "observed retained study-sample calibration; no national welfare estimate",
        "provenance": {
            "archive_url": ARCHIVE_URL,
            "archive_sha256": ARCHIVE_SHA256,
            "archive_members": MEMBERS,
            "calculation_sources": source_hashes(),
            "versions": {
                "python": platform.python_version(),
                "numpy": np.__version__,
                "pandas": pd.__version__,
            },
            "native_archive_mapping_verified": True,
            "licence": "no explicit redistribution licence in archive; microdata not vendored",
        },
        "study1": study1_benchmarks(study1),
        "study2": {
            "native_checks": checks,
            "selection_order": [
                "archive",
                "pass final attention",
                "also monotone",
                "also pass MPL endpoints",
            ],
            "selection_counts": waterfall,
            "retained_switch_counts": {
                str(int(k)): int(n)
                for k, n in primary.switchingpoint.value_counts().sort_index().items()
            },
            "table4_primary": midpoint_ols(primary),
            "table4_subgroups": {
                key: midpoint_ols(primary[mask]) for key, mask in subgroups.items()
            },
            "attention_sensitivity_regressions": {
                key: midpoint_ols(study2[mask])
                for key, mask in masks.items()
                if key != "primary"
            },
            "appendix_A9_label_discrepancy": "native include_final_attention_failures matches printed col3 (N=3603); include_endpoint_failures matches col4 (N=3689); printed group labels appear reversed",
            "interval_bounds": {
                key: sample.interval_bounds() for key, sample in samples.items()
            },
            "midpoint_imputation_moments": asdict(midpoint.moments()),
            "include_final_attention_interval_bounds": study2_sample(
                study2, include_final_attention=True
            ).interval_bounds(),
            "scope": "retained MTurk respondents, 2018-2019 experimental assigned schedules and 20-cent increment; equal respondent mass",
            "measurement_limit": "one MPL per person; intervals rationalize choices under stable monetary preferences; response noise, rounding and stable latent beliefs are not separated",
            "endpoint_failure_limit": "reintroduced endpoint failures have open intervals; source 0/1 imputations reproduce OLS only, not finite moment bounds",
            "latent_beliefs_identified": False,
        },
        "welfare_input_replaced": False,
        "illustrative_welfare_rmse": 0.12,
    }


def canonical_manifest(csv_bytes, convention):
    return {
        "schema_version": 1,
        "rate_unit": "fraction",
        "data_status": "observed",
        "study": "Rees-Jones and Taubinsky (2020), Study 2",
        "tax_scope": "experimental tax on 20-cent increment; assigned MTR, not US federal or comprehensive taxes",
        "population": "3130 retained MTurk study respondents, December 2018-January 2019; no population weights",
        "sample_selection": "irrational==0 & inattentive_1==0 & inattentive_2==0; all MPL flags checked against raw A/B decisions",
        "transformation": f"q21_0..q21_11 A/B payoff inequalities; {convention} interval convention; native float32 MTR retained as stored; stable archive row ordinal IDs",
        "measurement_error": "one MPL per respondent; intervals describe monetary-choice rationalization, not noise-free latent beliefs",
        "weighting": "equal_respondent",
        "source_url": ARCHIVE_URL,
        "source_sha256": ARCHIVE_SHA256,
        "source_location": "Replication Code/Study 2/RJT_study_2_data.dta; Table 4.do lines 14-48; article footnote 28",
        "input_sha256": sha256(csv_bytes).hexdigest(),
        "native_archive_mapping_verified": True,
        "calculation_sources": source_hashes(),
        "support": (
            "author footnote 28: [0,1]"
            if convention == "author"
            else "payoff inequalities only; lowest retained bin [-.05,.05]"
        ),
    }


def validate_benchmarks(result):
    """Gate native replication on primary-source printed counts and precision.

    This is deliberately independent of the research lane's numerical output.
    Appendix A9 is checked by coefficients/counts, with its label discrepancy
    retained separately. No interval-regression replication is claimed here.
    """
    first, second = result["study1"], result["study2"]
    if (first["archive_respondents"], first["retained_respondents"]) != (4633, 4197):
        raise ValueError("Study 1 sample benchmark failed")
    if second["selection_counts"] != [4582, 3868, 3689, 3130]:
        raise ValueError("Study 2 sample benchmark failed")
    for key, count, coefficient, se in (
        ("full", 58758, "0.62", "0.010"),
        ("mid_range", 41970, "0.82", "0.013"),
        ("local", 17937, "0.81", "0.043"),
    ):
        panel = first["table1_pooled_panels"][key]
        if (
            panel["forecasts"],
            f'{panel["coefficient"]:.2f}',
            f'{panel["clustered_standard_error"]:.3f}',
        ) != (count, coefficient, se):
            raise ValueError(f"Study 1 Table 1 {key} benchmark failed")
    primary = second["table4_primary"]
    for key, coefficient, se, digits in (
        ("ATR", "0.350", "0.0236", 3),
        ("MTR", "0.0934", "0.0238", 4),
        ("constant", "0.281", "0.0126", 3),
    ):
        if (
            f'{primary["coefficients"][key]:.{digits}f}',
            f'{primary["standard_errors"][key]:.4f}',
        ) != (coefficient, se):
            raise ValueError(f"Study 2 Table 4 / A9 {key} benchmark failed")
    for key, count in (
        ("simple", 1571),
        ("complex", 1559),
        ("table_reopened", 1431),
        ("table_not_reopened", 1699),
    ):
        if second["table4_subgroups"][key]["n"] != count:
            raise ValueError(f"Study 2 subgroup {key} count failed")
    for key, count, atr, mtr in (
        ("include_final_attention_failures", 3603, "0.336", "0.0855"),
        ("include_endpoint_failures", 3689, "0.333", "0.0850"),
        ("include_both_attention_failures", 4314, "0.308", "0.0879"),
    ):
        fit = second["attention_sensitivity_regressions"][key]
        if (
            fit["n"],
            f'{fit["coefficients"]["ATR"]:.3f}',
            f'{fit["coefficients"]["MTR"]:.4f}',
        ) != (count, atr, mtr):
            raise ValueError(f"Study 2 Appendix A9 {key} benchmark failed")


def artifact_hash(result):
    payload = {key: value for key, value in result.items() if key != "artifact_sha256"}
    return sha256(
        json.dumps(payload, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()


def load_replication(path=None):
    """Read the aggregate cache only if its source, bytes and benchmarks agree.

    This checks integrity and drift; authenticating the reported derivation still
    requires running the archive CLI or optional native-data integration test.
    """
    if path is None:
        path = Path(__file__).parents[1] / "data" / "rjt_replication.json"
    result = json.loads(Path(path).read_text())
    if result.get("artifact_sha256") != artifact_hash(result):
        raise ValueError("replication artifact checksum mismatch")
    provenance = result["provenance"]
    if (
        provenance["archive_sha256"] != ARCHIVE_SHA256
        or provenance["archive_members"] != MEMBERS
    ):
        raise ValueError("replication archive provenance mismatch")
    if provenance["calculation_sources"] != source_hashes():
        raise ValueError("replication calculation source drift; rerun archive CLI")
    validate_benchmarks(result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    study1, study2 = read_archive(args.archive)
    result = reproduce(study1, study2)
    validate_benchmarks(result)
    result["artifact_sha256"] = artifact_hash(result)
    files = {"replication.json": json.dumps(result, indent=2, allow_nan=False) + "\n"}
    for convention in ("author", "payoff"):
        sample = study2_sample(study2, convention)
        buffer = io.StringIO(newline="")
        writer = csv.DictWriter(buffer, fieldnames=RATE_COLUMNS)
        writer.writeheader()
        writer.writerows(asdict(row) for row in sample.observations)
        csv_text = buffer.getvalue()
        manifest = canonical_manifest(csv_text.encode(), convention)
        # Exercise the public canonical boundary before writing requested output.
        with TemporaryDirectory() as staging:
            csv_path, manifest_path = (
                Path(staging) / "rates.csv",
                Path(staging) / "manifest.json",
            )
            csv_path.write_bytes(csv_text.encode())
            manifest_path.write_text(json.dumps(manifest))
            verified, metadata = load_rate_sample(csv_path, manifest_path)
            report = calibration_report(verified, metadata)
        files[f"{convention}-rates.csv"] = csv_text
        files[f"{convention}-manifest.json"] = json.dumps(manifest, indent=2) + "\n"
        files[f"{convention}-report.json"] = (
            json.dumps(report, indent=2, allow_nan=False) + "\n"
        )
    if args.archive.resolve() in {(args.output_dir / name).resolve() for name in files}:
        parser.error("output must not overwrite archive")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (args.output_dir / name).write_bytes(content.encode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
