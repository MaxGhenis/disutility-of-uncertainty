"""Frozen Study 1 audit evidence, separate from every welfare-model input.

The aggregate importer selects explicit cohorts; it estimates no latent model.
Native reproduction uses the separately preserved, independently reviewed code
in calibration/study1. No raw observations are packaged with this module.
"""

import argparse
import csv
import json
from hashlib import sha256
from pathlib import Path

from taxuncertainty.analysis.rjt_replication import ARCHIVE_SHA256

AUDIT_COMMIT = "a5191ea9f81fd414d9fbf547995dcb31341aa875"
CACHE = Path(__file__).parents[1] / "data/study1_evidence.json"


def digest(data):
    return sha256(
        json.dumps(data, sort_keys=True, allow_nan=False).encode()
    ).hexdigest()


def verify_bundle(root):
    """Fail closed on altered frozen code, aggregates, or source attribution."""
    root = Path(root)
    manifest = json.loads((root / "manifest.json").read_text())
    if (
        manifest["audit_commit"] != AUDIT_COMMIT
        or manifest["archive_sha256"] != ARCHIVE_SHA256
    ):
        raise ValueError("Study 1 reviewed source identity mismatch")
    for name, item in manifest["files"].items():
        path = root / name
        if path.resolve().is_relative_to(root.resolve()) is False:
            raise ValueError("Study 1 manifest path escapes bundle")
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != item["sha256"] or len(raw) != item["bytes"]:
            raise ValueError(f"Study 1 frozen file mismatch: {name}")
    return manifest


def _rows(root, name):
    with (Path(root) / "results" / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def _select(rows, **criteria):
    return [r for r in rows if all(r[k] == str(v) for k, v in criteria.items())]


def _one(rows, **criteria):
    selected = _select(rows, **criteria)
    if len(selected) != 1:
        raise ValueError(f"Expected exactly one Study 1 cohort: {criteria}")
    return selected[0]


def build_evidence(root):
    """Import the reviewed aggregate cells with their original fraction units."""
    root = Path(root)
    manifest = verify_bundle(root)
    selection = _rows(root, "selection.csv")
    cohorts = []
    for label, panel, count, span, affine_screen in (
        ("Own-income pair", "own_pair", 2, 0, False),
        ("Native local", "native_local", 2, 0, False),
        ("Own bracket, affine, at least 3 incomes", "own_bracket", 3, 0, True),
        ("Also at least 4 incomes, span at least $5,000", "own_bracket", 4, 5000, True),
        (
            "Also at least 4 incomes, span at least $10,000",
            "own_bracket",
            4,
            10000,
            True,
        ),
        ("All 14 random-income draws", "random_full", 2, 0, False),
    ):
        row = _one(
            selection,
            panel=panel,
            min_distinct=count,
            min_span=span,
            observed_affine_screen=affine_screen,
        )
        cohorts.append(
            {
                "label": label,
                "panel": panel,
                "min_distinct": count,
                "min_span_dollars": span,
                "observed_affine_screen": affine_screen,
                "n": int(row["n"]),
                **{
                    key: float(row[key])
                    for key in (
                        "median_income",
                        "median_span",
                        "mean_error",
                        "sd_error",
                        "median_max_leverage",
                        "median_box_radius_100",
                    )
                },
            }
        )
    affine_rows = _select(
        _rows(root, "affine_belief_falsification.csv"),
        panel="own_bracket",
        outcome="taxguessmain",
        min_n=4,
        min_span=5000,
        observed_affine_screen=True,
    )
    affine = [
        {
            **{k: int(r[k]) for k in ("dollar_cap", "respondents", "compatible")},
            **{
                k: float(r[k])
                for k in (
                    "median_width_among_compatible",
                    "median_minimum_dollar_error",
                    "p95_minimum_dollar_error",
                )
            },
        }
        for r in affine_rows
    ]
    repeated = _one(
        _rows(root, "repeated_measures.csv"),
        panel="own_bracket",
        split="income_interleaved",
        observed_affine_screen=True,
        min_half_span=5000,
        outcome="taxguessmain",
    )
    covariance = _select(
        _rows(root, "correlated_error_sensitivity.csv"),
        panel="own_bracket",
        min_half_span=5000,
    )
    processing = _select(_rows(root, "processing_sensitivity.csv"), panel="random_full")
    result = {
        "schema_version": 1,
        "status": "observed finite-design projections and conditional diagnostics",
        "latent_beliefs_identified": False,
        "welfare_input_replaced": False,
        "provenance": {
            "audit_commit": AUDIT_COMMIT,
            "archive_sha256": ARCHIVE_SHA256,
            "bundle_manifest_sha256": sha256(
                (root / "manifest.json").read_bytes()
            ).hexdigest(),
            "frozen_files": manifest["files"],
        },
        "units": {
            "slope": "tax dollars / income dollars; multiply by 100 for pp",
            "variance_covariance_and_covariance_se": "slope fraction squared; multiply by 10000 for pp squared",
            "descriptive_variance_denominator": "N (equal respondent mass)",
            "repeated_variance_covariance_denominator": "N-1",
        },
        "observed_affine_screen": {
            "minimum_distinct_incomes": 3,
            "maximum_stored_tax_ols_residual_dollars": 0.05,
            "validates_between_observation_tax_schedule": False,
        },
        "affine_fit_slope_relative_tolerance": 1e-12,
        "selection": cohorts,
        "affine_compatibility": affine,
        "repeated": {
            "n": int(repeated["n"]),
            **{
                k: float(repeated[k])
                for k in (
                    "var_a",
                    "var_b",
                    "covariance",
                    "correlation",
                    "covariance_jackknife_se",
                )
            },
        },
        "correlated_error_sensitivity": [
            {
                k: float(r[k])
                for k in (
                    "assumed_error_correlation",
                    "implied_common_target_variance",
                    "implied_common_target_sd",
                )
            }
            for r in covariance
        ],
        "full_range_processing_sd": {
            r["outcome"]: float(r["sd_error"]) for r in processing
        },
    }
    for name in (
        "native_checks",
        "independent_arithmetic",
        "pair_repeats",
        "pooled_benchmarks",
        "slope_diagnostics",
    ):
        result[name] = json.loads((root / f"results/{name}.json").read_text())
    result["artifact_sha256"] = digest(result)
    return result


def load_evidence(path=CACHE):
    data = json.loads(Path(path).read_text())
    claimed = data.pop("artifact_sha256")
    if digest(data) != claimed:
        raise ValueError("Study 1 aggregate artifact checksum mismatch")
    if (
        data["provenance"]["audit_commit"] != AUDIT_COMMIT
        or data["provenance"]["archive_sha256"] != ARCHIVE_SHA256
        or data["latent_beliefs_identified"] is not False
        or data["welfare_input_replaced"] is not False
    ):
        raise ValueError("Study 1 evidence scope or source mismatch")
    data["artifact_sha256"] = claimed
    return data


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, default=Path("calibration/study1"))
    parser.add_argument("--output", type=Path, default=CACHE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    data = build_evidence(args.bundle)
    if args.check:
        if load_evidence(args.output) != data:
            raise ValueError("Study 1 cache differs from reviewed aggregate inputs")
        print("Study 1 aggregate provenance and cache verified")
    else:
        args.output.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
