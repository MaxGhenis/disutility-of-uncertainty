"""Observed signed tax-rate errors and conditional identification bounds.

All rates are fractions, with error = perceived minus true. Equal respondent
mass is divided among that respondent's observations; these are study-sample
moments, never population-weighted welfare estimates. No clipping, winsorizing,
normality assumption, or measurement-error subtraction happens implicitly.
"""

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from math import isfinite, sqrt
from pathlib import Path

import numpy as np

RATE_COLUMNS = (
    "respondent_id",
    "observation_id",
    "true_rate",
    "perceived_rate_lower",
    "perceived_rate_upper",
)


def _interval(value, name, nonnegative=False):
    if len(value) != 2 or not all(isfinite(x) for x in value):
        raise ValueError(f"{name} must contain two finite endpoints")
    lo, hi = value
    if lo > hi or (nonnegative and lo < 0):
        raise ValueError(f"invalid {name} interval")
    return float(lo), float(hi)


def _square_bounds(lo, hi):
    return (0.0 if lo <= 0 <= hi else min(lo * lo, hi * hi)), max(lo * lo, hi * hi)


@dataclass(frozen=True)
class RateObservation:
    respondent_id: str
    observation_id: str
    true_rate: float
    perceived_rate_lower: float
    perceived_rate_upper: float

    def __post_init__(self):
        if not all(
            isinstance(x, str) and x.strip()
            for x in (self.respondent_id, self.observation_id)
        ):
            raise ValueError("respondent and observation IDs must be nonempty strings")
        if not isfinite(self.true_rate):
            raise ValueError("true_rate must be finite")
        _interval(
            (self.perceived_rate_lower, self.perceived_rate_upper), "perceived rate"
        )

    @property
    def error_interval(self):
        return (
            self.perceived_rate_lower - self.true_rate,
            self.perceived_rate_upper - self.true_rate,
        )


@dataclass(frozen=True)
class SignedMoments:
    bias: float
    variance: float
    sd: float
    second_moment: float
    rmse: float
    mae: float


class RateSample:
    """One explicitly scoped study sample, with equal mass per respondent."""

    def __init__(self, observations):
        self.observations = tuple(observations)
        if not self.observations:
            raise ValueError("sample must contain observations")
        seen = set()
        groups: dict[str, list[RateObservation]] = {}
        for row in self.observations:
            key = (row.respondent_id, row.observation_id)
            if key in seen:
                raise ValueError(f"duplicate respondent/observation key: {key}")
            seen.add(key)
            groups.setdefault(row.respondent_id, []).append(row)
        # Canonical ordering also makes seeded bootstrap invariant to CSV row order.
        self.groups = {
            key: tuple(sorted(groups[key], key=lambda row: row.observation_id))
            for key in sorted(groups)
        }

    @property
    def is_point_identified(self):
        return all(
            row.perceived_rate_lower == row.perceived_rate_upper
            for row in self.observations
        )

    def _arrays(self):
        intervals, weights = [], []
        for rows in self.groups.values():
            for row in rows:
                intervals.append(row.error_interval)
                weights.append(1 / (len(self.groups) * len(rows)))
        return np.array(intervals), np.array(weights)

    def moments(self):
        """Descriptive finite-sample moments (no N-1 correction)."""
        if not self.is_point_identified:
            raise ValueError("interval observations do not identify point moments")
        intervals, weights = self._arrays()
        errors = intervals[:, 0]
        bias = float(weights @ errors)
        variance = float(weights @ ((errors - bias) ** 2))
        second = float(weights @ (errors**2))
        return SignedMoments(
            bias,
            variance,
            sqrt(variance),
            second,
            sqrt(second),
            float(weights @ np.abs(errors)),
        )

    def interval_bounds(self):
        """Sharp marginal bounds on bias/MSE/MAE; conservative SD outer bounds.

        The endpoints for different moments need not be jointly attainable.
        Finite closed intervals are supplied by an adapter; any endpoint support
        assumption (especially for an MPL end bin) belongs in its manifest.
        """
        intervals, weights = self._arrays()
        lo, hi = intervals.T
        sq = np.array([_square_bounds(a, b) for a, b in intervals])
        bias = [float(weights @ lo), float(weights @ hi)]
        second = [float(weights @ sq[:, 0]), float(weights @ sq[:, 1])]
        # Variance is invariant to a common shift. Center first so that two
        # nearly equal large squared moments do not erase small dispersion.
        center = bias[0] + (bias[1] - bias[0]) / 2
        centered = intervals - center
        centered_sq = np.array([_square_bounds(a, b) for a, b in centered])
        centered_bias_sq = _square_bounds(
            float(weights @ centered[:, 0]), float(weights @ centered[:, 1])
        )
        variance = [
            max(0.0, float(weights @ centered_sq[:, 0]) - centered_bias_sq[1]),
            max(0.0, float(weights @ centered_sq[:, 1]) - centered_bias_sq[0]),
        ]
        return {
            "bias": bias,
            "second_moment": second,
            "rmse": [sqrt(x) for x in second],
            "mae": [float(weights @ np.sqrt(sq[:, k])) for k in (0, 1)],
            "sd_outer": [sqrt(x) for x in variance],
            "interpretation": "marginal identification bounds, not confidence intervals; SD bounds are outer bounds",
        }

    def variance_decomposition(self):
        """Between respondent means + within respondent observed variation.

        Within-person variation is not automatically measurement error: true
        belief heterogeneity across tasks can also generate it.
        """
        moments = self.moments()
        means, within = [], []
        for rows in self.groups.values():
            errors = np.array([row.error_interval[0] for row in rows])
            means.append(errors.mean())
            within.append(errors.var())
        return {
            "between_respondent_variance": float(np.var(means)),
            "within_respondent_variance": float(np.mean(within)),
            "total_variance": moments.variance,
            "measurement_error_identified": False,
        }

    def bootstrap(self, replications=1000, seed=20260907, confidence=0.95):
        """Respondent-cluster percentile intervals for observed point moments.

        Conditions on the supplied selection/transformations. This does not
        resample source cleaning or validate a survey's population transport.
        """
        center = self.moments().bias  # Refuse interval midpoint substitution.
        if len(self.groups) < 2:
            raise ValueError("bootstrap needs at least two respondents")
        if (
            isinstance(replications, bool)
            or not isinstance(replications, int)
            or replications < 2
        ):
            raise ValueError("replications must be an integer >= 2")
        if not isfinite(confidence) or not 0 < confidence < 1:
            raise ValueError("confidence must lie strictly between zero and one")
        sufficient = []
        for rows in self.groups.values():
            errors = np.array([row.error_interval[0] for row in rows])
            centered = errors - center
            sufficient.append(
                [centered.mean(), (centered**2).mean(), np.abs(errors).mean()]
            )
        cluster_moments = np.array(sufficient)
        rng = np.random.default_rng(seed)
        draws = []
        for _ in range(replications):
            first, second, absolute = cluster_moments[
                rng.integers(len(cluster_moments), size=len(cluster_moments))
            ].mean(axis=0)
            variance = max(0.0, second - first**2)
            bias = first + center
            draws.append([bias, sqrt(variance), sqrt(variance + bias**2), absolute])
        alpha = (1 - confidence) / 2
        endpoints = np.quantile(draws, [alpha, 1 - alpha], axis=0)
        return {
            "method": "equal-respondent cluster percentile bootstrap, conditional on supplied data processing",
            "replications": replications,
            "seed": seed,
            "confidence": confidence,
            "intervals": {
                name: endpoints[:, k].tolist()
                for k, name in enumerate(("bias", "sd", "rmse", "mae"))
            },
            "population_inference": False,
        }


def classical_error_bounds(
    observed_bias, observed_variance, noise_mean=(0, 0), noise_sd=(0, 0)
):
    """Moment-conditional bounds under error = latent + noise, Cov(latent,noise)=0.

    Mean and SD ranges are analyst assumptions. They do not estimate reliability
    or justify a classical error model. Incompatible minimum noise SD raises;
    an upper endpoint above observed SD is intersected with feasibility.
    """
    if (
        not isfinite(observed_bias)
        or not isfinite(observed_variance)
        or observed_variance < 0
    ):
        raise ValueError("observed bias/variance must be finite, variance nonnegative")
    nmean = _interval(noise_mean, "noise mean")
    nsd = _interval(noise_sd, "noise SD", nonnegative=True)
    observed_sd = sqrt(observed_variance)
    if nsd[0] > observed_sd:
        raise ValueError("minimum noise SD exceeds observed SD under zero covariance")
    feasible_sd = [nsd[0], min(nsd[1], observed_sd)]
    bias = [observed_bias - nmean[1], observed_bias - nmean[0]]
    variance = [
        max(0.0, observed_variance - feasible_sd[1] ** 2),
        max(0.0, observed_variance - feasible_sd[0] ** 2),
    ]
    bsq = _square_bounds(*bias)
    return {
        "assumptions": "observed error = latent error + noise; zero latent-noise covariance; supplied noise mean/SD ranges",
        "noise_mean": list(nmean),
        "requested_noise_sd": list(nsd),
        "feasible_noise_sd": feasible_sd,
        "latent_bias": bias,
        "latent_sd": [sqrt(x) for x in variance],
        "latent_rmse": [sqrt(variance[k] + bsq[k]) for k in (0, 1)],
        "interpretation": "sensitivity bounds conditional on observed moments and assumptions, not confidence intervals",
    }


def nonclassical_rmse_bounds(observed_rmse, noise_rmse_max):
    """L2 triangle bounds, allowing arbitrary latent-noise covariance and bias."""
    if not all(isfinite(x) and x >= 0 for x in (observed_rmse, noise_rmse_max)):
        raise ValueError("RMSE inputs must be finite and nonnegative")
    return [max(0.0, observed_rmse - noise_rmse_max), observed_rmse + noise_rmse_max]


def component_rmse_bounds(first, second):
    """Marginal L2 bounds for summed errors, with unknown component dependence.

    Both inputs must describe the same population/units/counterfactual. This
    algebra supplies no transport from a federal survey to comprehensive taxes.
    """
    a, b = _interval(first, "first RMSE", True), _interval(second, "second RMSE", True)
    return [max(0.0, a[0] - b[1], b[0] - a[1]), a[1] + b[1]]


def load_rate_sample(csv_path, manifest_path):
    """Read a canonical CSV only after verifying its units/scope and byte hash.

    Provenance declarations do not authenticate upstream data. A native source
    adapter must document and verify its raw-input mapping separately.
    """
    csv_path, manifest_path = Path(csv_path), Path(manifest_path)
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("schema_version") != 1 or manifest.get("rate_unit") != "fraction":
        raise ValueError("requires schema_version 1 and explicit fractional rate units")
    if manifest.get("data_status") not in ("synthetic", "observed"):
        raise ValueError("data_status must be synthetic or observed")
    for key in (
        "study",
        "tax_scope",
        "population",
        "sample_selection",
        "transformation",
        "measurement_error",
    ):
        if not isinstance(manifest.get(key), str) or not manifest[key].strip():
            raise ValueError(f"manifest requires an explicit {key}")
    if manifest.get("weighting") != "equal_respondent":
        raise ValueError(
            "only explicit equal_respondent study-sample weighting is supported"
        )
    if sha256(csv_path.read_bytes()).hexdigest() != manifest.get("input_sha256"):
        raise ValueError("canonical CSV checksum mismatch")
    if manifest["data_status"] == "observed":
        for key in ("source_url", "source_sha256", "source_location"):
            if not isinstance(manifest.get(key), str) or not manifest[key].strip():
                raise ValueError(f"observed data requires {key}")
        if len(manifest["source_sha256"]) != 64 or any(
            c not in "0123456789abcdef" for c in manifest["source_sha256"]
        ):
            raise ValueError("source_sha256 must be a SHA256 hex digest")
    with csv_path.open(newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != list(RATE_COLUMNS):
            raise ValueError(f"CSV columns must be exactly {RATE_COLUMNS}")
        rows = []
        for line, row in enumerate(reader, 2):
            try:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError("malformed CSV row")
                rows.append(
                    RateObservation(
                        row["respondent_id"],
                        row["observation_id"],
                        *(float(row[key]) for key in RATE_COLUMNS[2:]),
                    )
                )
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"invalid canonical CSV line {line}: {error}"
                ) from error
    return RateSample(rows), manifest


def calibration_report(sample, manifest, replications=1000, seed=20260907):
    report = {
        "schema_version": 1,
        "calculation_source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "status": f"{manifest['data_status']} study-sample errors; no national welfare estimate",
        "provenance": manifest,
        "sign_convention": "perceived minus true",
        "respondents": len(sample.groups),
        "observations": len(sample.observations),
        "interval_bounds": sample.interval_bounds(),
        "latent_beliefs_identified": False,
    }
    if sample.is_point_identified:
        moments = sample.moments()
        report["observed_moments"] = asdict(moments)
        report["variance_decomposition"] = sample.variance_decomposition()
        if len(sample.groups) >= 2:
            report["bootstrap"] = sample.bootstrap(replications, seed)
        report["classical_zero_mean_unknown_noise"] = classical_error_bounds(
            moments.bias, moments.variance, noise_sd=(0, moments.sd)
        )
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--replications", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=20260907)
    args = parser.parse_args(argv)
    if args.output.resolve() in (args.csv.resolve(), args.manifest.resolve()):
        parser.error("output must not overwrite an input")
    sample, manifest = load_rate_sample(args.csv, args.manifest)
    report = calibration_report(sample, manifest, args.replications, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
