"""Instrument-level adapters motivated by Rees-Jones and Taubinsky (2020).

Inputs use documented canonical fields, NOT guessed native archive columns.
Source sample restrictions and own-bracket flags must be mapped from inspected
replication code. These routines do not reproduce that unavailable cleaning code.
"""

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import isfinite
from pathlib import Path

import numpy as np

from taxuncertainty.analysis.signed_errors import (
    RATE_COLUMNS,
    RateObservation,
    RateSample,
    calibration_report,
    load_rate_sample,
)


@dataclass(frozen=True)
class TaxForecast:
    respondent_id: str
    observation_id: str
    income: float
    true_tax: float
    perceived_tax: float
    in_own_bracket: bool
    selected: bool = True

    def __post_init__(self):
        if not all(
            isinstance(x, str) and x.strip()
            for x in (self.respondent_id, self.observation_id)
        ):
            raise ValueError("forecast IDs must be nonempty strings")
        if not all(
            isfinite(x) for x in (self.income, self.true_tax, self.perceived_tax)
        ):
            raise ValueError("forecast dollars must be finite")
        if type(self.in_own_bracket) is not bool or type(self.selected) is not bool:
            raise ValueError("selection and own-bracket flags must be booleans")


def local_slope_sample(forecasts, minimum_income_span=0.0):
    """OLS dollar-tax slopes within each respondent's supplied own-bracket draws.

    Reports a separate pooled respondent-FE regression of perceived on true tax
    (the Table 1 estimand), without equating it to a mean individual rate error.
    Its implicit slope-ratio weights are proportional to within-person true-tax
    sum of squares. Excluded respondents and weak leverage are audited.
    """
    if not isfinite(minimum_income_span) or minimum_income_span < 0:
        raise ValueError("minimum income span must be finite and nonnegative")
    groups: dict[str, list[TaxForecast]] = {}
    seen = set()
    for row in forecasts:
        key = (row.respondent_id, row.observation_id)
        if key in seen:
            raise ValueError(f"duplicate forecast key: {key}")
        seen.add(key)
        groups.setdefault(row.respondent_id, []).append(row)
    if not groups:
        raise ValueError("no forecasts supplied")
    rates, diagnostics = [], []
    pooled_numerator = pooled_denominator = 0.0
    for person in sorted(groups):
        all_rows = sorted(groups[person], key=lambda row: row.observation_id)
        rows = [row for row in all_rows if row.selected and row.in_own_bracket]
        record = {
            "respondent_id": person,
            "input_forecasts": len(all_rows),
            "source_excluded_forecasts": sum(not row.selected for row in all_rows),
            "selected_nonlocal_forecasts": sum(
                row.selected and not row.in_own_bracket for row in all_rows
            ),
            "local_forecasts": len(rows),
        }
        if len(rows) < 2:
            record["excluded_reason"] = "fewer than two selected local forecasts"
            diagnostics.append(record)
            continue
        x = np.array([row.income for row in rows])
        truth = np.array([row.true_tax for row in rows])
        forecast = np.array([row.perceived_tax for row in rows])
        dx, dt, df = x - x.mean(), truth - truth.mean(), forecast - forecast.mean()
        span = float(np.ptp(x))
        sxx = float(dx @ dx)
        record.update(income_span=span, income_sum_squares=sxx)
        if sxx == 0 or span < minimum_income_span:
            record["excluded_reason"] = (
                "insufficient income variation at requested span threshold"
            )
            diagnostics.append(record)
            continue
        true_slope, perceived_slope = float(dx @ dt / sxx), float(dx @ df / sxx)
        # A supplied own-bracket flag cannot certify a nonlinear/cliff interval.
        residual_truth = dt - true_slope * dx
        if not np.allclose(residual_truth, 0, rtol=0, atol=1e-6):
            raise ValueError(
                f"nonlinear true tax in supplied own-bracket forecasts for {person}"
            )
        residual_forecast = df - perceived_slope * dx
        iid_variance = (
            float(residual_forecast @ residual_forecast / (len(rows) - 2) / sxx)
            if len(rows) > 2
            else None
        )
        rates.append(
            RateObservation(
                person, "local-ols-slope", true_slope, perceived_slope, perceived_slope
            )
        )
        pooled_numerator += float(dt @ df)
        pooled_denominator += float(dt @ dt)
        record.update(
            true_slope=true_slope,
            perceived_slope=perceived_slope,
            signed_error=perceived_slope - true_slope,
            inverse_income_sum_squares=1 / sxx,
            iid_linear_slope_noise_variance=iid_variance,
            true_tax_sum_squares=float(dt @ dt),
        )
        diagnostics.append(record)
    if not rates:
        raise ValueError("no respondents have identifiable local slopes")
    return RateSample(rates), {
        "method": "respondent-specific OLS perceived and true tax on income, with intercept, selected own-bracket draws only",
        "native_archive_mapping_verified": False,
        "minimum_income_span": minimum_income_span,
        "input_respondents": len(groups),
        "retained_respondents": len(rates),
        "excluded_respondents": len(groups) - len(rates),
        "pooled_fe_scale": (
            pooled_numerator / pooled_denominator if pooled_denominator else None
        ),
        "pooled_fe_denominator": pooled_denominator,
        "pooled_fe_interpretation": "design-weighted scaling of perceived on true tax; not mean signed rate error or RMSE",
        "noise_variance_assumptions": "correctly linear perceived schedule and iid homoskedastic dollar-response noise; undefined with only two observations; diagnostic, not validated measurement-error correction",
        "respondents": diagnostics,
    }


def mpl_interval(
    untaxed_amounts, choose_taxable, taxable_increment=20.0, rate_support=None
):
    """Closed feasible rate interval from binary payoff-maximizing choices.

    Choose taxable A implies t <= 1-B/A; choose untaxed B implies t >= 1-B/A.
    Ties are allowed. No support bound or midpoint substitution is imposed.
    Both types of choices are required to obtain a finite interval unless the
    caller supplies finite support. Source footnote 28 uses [0,1] support; this
    restriction is optional and must be documented rather than imposed silently.
    """
    offers = np.asarray(untaxed_amounts, dtype=float)
    choices = tuple(choose_taxable)
    if offers.ndim != 1 or len(offers) < 2 or len(offers) != len(choices):
        raise ValueError("MPL requires matched one-dimensional offers and choices")
    if not np.all(np.isfinite(offers)) or np.any(np.diff(offers) <= 0):
        raise ValueError("MPL offers must be finite and strictly increasing")
    if not isfinite(taxable_increment) or taxable_increment <= 0:
        raise ValueError("taxable increment must be finite and positive")
    if any(type(choice) is not bool for choice in choices):
        raise ValueError("MPL choices must be booleans (true = taxable account)")
    thresholds = 1 - offers / taxable_increment
    upper = [float(t) for t, choice in zip(thresholds, choices) if choice]
    lower = [float(t) for t, choice in zip(thresholds, choices) if not choice]
    if rate_support is not None:
        if (
            len(rate_support) != 2
            or not all(isfinite(x) for x in rate_support)
            or rate_support[0] > rate_support[1]
        ):
            raise ValueError("rate support must have two ordered finite endpoints")
        lower.append(float(rate_support[0]))
        upper.append(float(rate_support[1]))
    if not upper or not lower:
        raise ValueError(
            "open-ended MPL response requires an explicit support assumption"
        )
    lo, hi = max(lower), min(upper)
    if lo > hi:
        raise ValueError("nonmonotone MPL choices have no consistent perceived rate")
    return lo, hi


def mpl_sample(records, rate_support=None):
    """Study-2-like records with explicit source selection and exclusion audit."""
    observations, excluded = [], []
    seen = set()
    for record in records:
        person, task = record["respondent_id"], record["observation_id"]
        if (person, task) in seen:
            raise ValueError("duplicate MPL respondent/observation key")
        seen.add((person, task))
        if type(record["selected"]) is not bool:
            raise ValueError("MPL selection must be boolean")
        if not record["selected"]:
            reason = record.get("exclusion_reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError(
                    "excluded MPL record requires a source exclusion reason"
                )
            excluded.append(
                {"respondent_id": person, "observation_id": task, "reason": reason}
            )
            continue
        lo, hi = mpl_interval(
            record["untaxed_amounts"],
            record["choose_taxable"],
            record["taxable_increment"],
            rate_support,
        )
        observations.append(RateObservation(person, task, record["true_rate"], lo, hi))
    sample = RateSample(observations)
    return sample, {
        "method": "MPL payoff inequalities; no midpoint substitution; support restriction only if explicitly supplied",
        "rate_support": rate_support,
        "native_archive_mapping_verified": False,
        "retained_records": len(observations),
        "excluded_records": excluded,
        "assumptions": "choices maximize perceived monetary payoff; common unit across taxable increment and untaxed offers; supplied source selection",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="canonical instrument JSON; see calibration/README.md",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--minimum-income-span", type=float, default=0)
    args = parser.parse_args(argv)
    outputs = [
        args.output_dir / name
        for name in ("rates.csv", "manifest.json", "diagnostics.json", "report.json")
    ]
    if args.input.resolve() in [path.resolve() for path in outputs]:
        parser.error("output must not overwrite input")
    payload = json.loads(args.input.read_text())
    if payload.get("schema_version") != 1:
        parser.error("requires canonical instrument schema_version 1")
    manifest = dict(payload["manifest"])
    if (
        manifest.get("currency_unit") != "dollars"
        and payload["instrument"] == "local_forecasts"
    ):
        parser.error("local forecasts require explicit dollar units")
    if payload["instrument"] == "local_forecasts":
        sample, audit = local_slope_sample(
            [TaxForecast(**row) for row in payload["records"]], args.minimum_income_span
        )
    elif payload["instrument"] == "mpl":
        if manifest.get("rate_unit") != "fraction":
            parser.error("MPL true rates require explicit fractional units")
        support = payload.get("rate_support")
        if support is not None and not manifest.get("rate_support_reason"):
            parser.error("MPL rate support requires a documented rate_support_reason")
        sample, audit = mpl_sample(payload["records"], support)
    else:
        parser.error("unknown instrument")
    manifest.update(
        schema_version=1,
        rate_unit="fraction",
        weighting="equal_respondent",
        canonical_instrument_sha256=sha256(args.input.read_bytes()).hexdigest(),
        adapter_source_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
        native_archive_mapping_verified=False,
        transformation=audit["method"],
        adapter_settings=(
            {"minimum_income_span": args.minimum_income_span}
            if payload["instrument"] == "local_forecasts"
            else {"rate_support": payload.get("rate_support")}
        ),
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with outputs[0].open("w", newline="") as target:
        writer = csv.DictWriter(target, RATE_COLUMNS)
        writer.writeheader()
        writer.writerows(asdict(row) for row in sample.observations)
    manifest["input_sha256"] = sha256(outputs[0].read_bytes()).hexdigest()
    outputs[1].write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    # Use the same schema validator as downstream consumers.
    sample, manifest = load_rate_sample(outputs[0], outputs[1])
    outputs[2].write_text(json.dumps(audit, indent=2, allow_nan=False) + "\n")
    outputs[3].write_text(
        json.dumps(calibration_report(sample, manifest), indent=2, allow_nan=False)
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
