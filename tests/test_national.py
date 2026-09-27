"""Invariants for the conditional national aggregation (audit 2026-09-25)."""

import json

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from taxuncertainty.analysis import national
from taxuncertainty.analysis.calibration import private_regret_approx
from taxuncertainty.analysis.national import (
    OUTCOMES,
    PersonRecords,
    build_artifact,
    load_national_estimate,
    national_estimate,
    per_dollar_outcomes,
    quantile_labels,
    weighted_percentile,
)
from taxuncertainty.models.accounting import evaluate_worker
from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.preferences import QuasilinearIsoelastic

finite = dict(allow_nan=False, allow_infinity=False)
FIELDS = (*OUTCOMES, "second_order")
# Rates are drawn from a small grid so each example needs few exact evaluations.
RATE_GRID = [-0.3, -0.05, 0.0, 0.1, 0.25, 0.3, 0.45, 0.9, 0.99, 1.0, 1.4]


@st.composite
def populations(draw, min_size=5, max_size=40, rates=RATE_GRID):
    n = draw(st.integers(min_size, max_size))
    earnings = draw(st.lists(st.floats(100, 4e5, **finite), min_size=n, max_size=n))
    tax = draw(st.lists(st.sampled_from(rates), min_size=n, max_size=n))
    weights = draw(
        st.lists(
            st.one_of(st.just(0.0), st.floats(0.5, 5e3, **finite)),
            min_size=n,
            max_size=n,
        )
    )
    return PersonRecords(np.array(earnings), np.array(tax), np.array(weights))


def in_domain_populations():
    return populations(rates=[r for r in RATE_GRID if 0 <= r < 1])


def _close(a, b, scale):
    return a == pytest.approx(b, rel=1e-9, abs=1e-9 * max(scale, 1.0))


class TestPerDollarOutcomes:
    @given(
        st.floats(1.0, 80.0, **finite),
        st.floats(0.1, 5.0, **finite),
        st.floats(0.1, 1.5, **finite),
        st.sampled_from([0.0, 0.2, 0.3, 0.6, 0.95]),
        st.floats(0.02, 0.2, **finite),
    )
    @settings(max_examples=40, deadline=None)
    def test_scale_invariant_in_wage_and_psi(self, wage, psi, eps, rate, sd):
        """Every outcome is proportional to informed earnings."""
        prefs = QuasilinearIsoelastic(psi, eps)
        beliefs = NormalBeliefs(0.0, sd)
        worker = evaluate_worker(wage, rate, prefs, beliefs)
        unit = per_dollar_outcomes([rate], eps, lambda r: beliefs)
        for name in OUTCOMES:
            assert getattr(worker, name) / worker.baseline_earnings == pytest.approx(
                unit[name][0], rel=1e-9, abs=1e-15
            )

    @given(st.sampled_from([0.0, 0.3, 0.9]), st.floats(0.05, 1.5, **finite))
    @settings(max_examples=20, deadline=None)
    def test_second_order_matches_calibration_formula(self, rate, eps):
        """Differential test against analysis.calibration.private_regret_approx."""
        unit = per_dollar_outcomes([rate], eps, national.default_beliefs(0.12))
        assert unit["second_order"][0] == pytest.approx(
            private_regret_approx(1.0, eps, rate, 0.12**2)
        )

    def test_rejects_rates_of_one_or_more(self):
        with pytest.raises(ValueError):
            per_dollar_outcomes([1.0], 0.33, national.default_beliefs(0.12))


class TestAggregation:
    @given(populations())
    @settings(max_examples=25, deadline=None)
    def test_group_totals_add_up_and_identity_holds(self, records):
        in_domain = (records.marginal_tax_rate >= 0) & (records.marginal_tax_rate < 1)
        if not (in_domain & (records.weight > 0)).any():
            return
        est = national_estimate(records)
        totals = est["totals"]
        scale = abs(totals["private_regret"]) + abs(totals["revenue_change"])
        for group in ("quintiles", "mtr_bands"):
            rows = [r for r in est[group] if "private_regret" in r]
            for name in FIELDS:
                assert _close(sum(r[name] for r in rows), totals[name], scale)
        assert sum(q["weighted_workers"] for q in est["quintiles"]) == pytest.approx(
            totals["weighted_workers"]
        )
        rows = [totals, est["subsidy_inclusive"], *est["quintiles"]]
        rows += [r for r in est["mtr_bands"] if "private_regret" in r]
        rows += est["sensitivity"]
        for row in rows:
            assert _close(
                row["social_loss"], row["private_regret"] - row["revenue_change"], scale
            )
            assert row["private_regret"] >= 0

    @given(populations())
    @settings(max_examples=25, deadline=None)
    def test_domains_partition_records_without_clipping(self, records):
        est_zero = int(np.sum(records.weight == 0))
        records = records.subset(records.weight > 0)
        rates = records.marginal_tax_rate
        if not ((rates >= 0) & (rates < 1)).any():
            return
        est = national_estimate(records)
        assert est["zero_weight_records"] == 0 <= est_zero
        domain = est["domain"]
        assert sum(d["records"] for d in domain.values()) == len(rates)
        assert sum(d["weighted_workers"] for d in domain.values()) == pytest.approx(
            records.weight.sum()
        )
        assert domain["rate_at_least_one"]["records"] == int((rates >= 1).sum())
        assert domain["negative_rate"]["records"] == int((rates < 0).sum())
        assert est["totals"]["weighted_workers"] == pytest.approx(
            domain["in_domain"]["weighted_workers"]
        )
        assert est["subsidy_inclusive"]["weighted_workers"] == pytest.approx(
            domain["in_domain"]["weighted_workers"]
            + domain["negative_rate"]["weighted_workers"]
        )
        bands = est["mtr_bands"]
        assert sum(b["records"] for b in bands) == len(rates)

    @given(in_domain_populations(), st.data())
    @settings(max_examples=20, deadline=None)
    def test_permutation_and_split_invariance(self, records, data):
        if not (records.weight > 0).any():
            return
        base = national_estimate(records)
        order = data.draw(st.permutations(range(len(records.weight))))
        permuted = national_estimate(
            PersonRecords(
                records.earnings[list(order)],
                records.marginal_tax_rate[list(order)],
                records.weight[list(order)],
            )
        )
        scale = abs(base["totals"]["private_regret"]) + 1
        for name in FIELDS:
            for a, b in zip(base["quintiles"], permuted["quintiles"]):
                assert _close(a[name], b[name], scale)
        # Splitting one record into two with the same total weight leaves
        # national totals unchanged.
        i = data.draw(st.integers(0, len(records.weight) - 1))
        share = data.draw(st.floats(0.05, 0.95))
        split = PersonRecords(
            np.append(records.earnings, records.earnings[i]),
            np.append(records.marginal_tax_rate, records.marginal_tax_rate[i]),
            np.append(records.weight, records.weight[i] * (1 - share)),
        )
        split.weight[i] *= share
        after = national_estimate(split)
        for name in FIELDS:
            assert _close(after["totals"][name], base["totals"][name], scale)

    def test_zero_weight_records_are_ignored(self):
        """Review counterexample: a zero-weight record crashed the quintile mean."""
        with_zero = national_estimate(
            PersonRecords(
                np.array([1.0, 2.0]), np.array([0.3, 0.3]), np.array([0, 1.0])
            )
        )
        without = national_estimate(
            PersonRecords(np.array([2.0]), np.array([0.3]), np.array([1.0]))
        )
        assert with_zero["zero_weight_records"] == 1
        for name in FIELDS:
            assert with_zero["totals"][name] == without["totals"][name]
        assert with_zero["mtr_percentiles"] == without["mtr_percentiles"]

    def test_quintiles_are_ordered_by_earnings(self):
        rng = np.random.default_rng(0)
        records = PersonRecords(
            rng.lognormal(10.5, 0.8, 300),
            rng.choice([0.1, 0.25, 0.3, 0.45], 300),
            rng.uniform(1, 10, 300),
        )
        est = national_estimate(records)
        quintiles = est["quintiles"]
        for low, high in zip(quintiles[:-1], quintiles[1:]):
            assert low["max_earnings"] <= high["min_earnings"]
        assert est["sensitivity"][4]["social_loss"] == est["totals"]["social_loss"]


class TestRepresentativeWorker:
    @given(in_domain_populations())
    @settings(max_examples=25, deadline=None)
    def test_decomposition_identity(self, records):
        if not (records.weight > 0).any():
            with pytest.raises(ValueError, match="positive-weight"):
                national_estimate(records)
            return
        est = national_estimate(records)
        for name in ("second_order", "social_loss"):
            d = est["representative_worker"][name]
            scale = abs(d["population"]) + abs(d["at_means"])
            assert _close(
                d["population"] - d["at_means"],
                d["rate_dispersion"] + d["covariance"],
                scale,
            )
            assert d["population"] == pytest.approx(est["totals"][name], rel=1e-9)
        # The second-order formula is convex in the rate, so rate dispersion
        # can only raise it; the covariance term can take either sign.
        second = est["representative_worker"]["second_order"]
        assert second["rate_dispersion"] >= -1e-9 * abs(second["population"])

    def test_population_below_means_under_negative_covariance(self):
        """Audit counterexample: earnings [1, 2] at rates [.25, 0]."""
        records = PersonRecords(np.array([1.0, 2.0]), np.array([0.25, 0.0]), np.ones(2))
        second = national_estimate(records)["representative_worker"]["second_order"]
        assert second["population"] < second["at_means"]
        assert second["covariance"] < 0 < second["rate_dispersion"]


class TestQuantilesAndPercentiles:
    @given(populations(), st.sampled_from([5, 10]))
    @settings(max_examples=40)
    def test_every_record_gets_one_label(self, records, n_groups):
        if records.weight.sum() <= 0:
            with pytest.raises(ValueError):
                quantile_labels(records, n_groups)
            return
        labels = quantile_labels(records, n_groups)
        assert labels.shape == records.weight.shape
        assert labels.min() >= 1 and labels.max() <= n_groups

    def test_review_tie_counterexample(self):
        """Same weighted distribution, different record order: same answer."""
        a = weighted_percentile([0, 0, 1], [1, 3, 1], 75)
        b = weighted_percentile([0, 0, 1], [3, 1, 1], 75)
        assert a == b == weighted_percentile([0, 1], [4, 1], 75)

    @given(
        st.lists(
            st.sampled_from([-0.2, 0.0, 0.1, 0.3, 0.3, 0.5]), min_size=1, max_size=20
        ),
        st.data(),
    )
    def test_invariant_to_order_and_splitting(self, values, data):
        n = len(values)
        weights = data.draw(
            st.lists(st.floats(0.01, 100, **finite), min_size=n, max_size=n)
        )
        p = data.draw(st.sampled_from([10, 25, 50, 75, 90]))
        base = weighted_percentile(values, weights, p)
        order = data.draw(st.permutations(range(n)))
        assert weighted_percentile(
            [values[i] for i in order], [weights[i] for i in order], p
        ) == pytest.approx(base)
        i = data.draw(st.integers(0, n - 1))
        share = data.draw(st.floats(0.05, 0.95))
        split_weights = weights[:i] + [weights[i] * share] + weights[i + 1 :]
        assert weighted_percentile(
            values + [values[i]], split_weights + [weights[i] * (1 - share)], p
        ) == pytest.approx(base)

    def test_verified_zero_weight_counterexamples(self):
        assert weighted_percentile([0.0, 0.5], [0.0, 1.0], 10) == 0.5
        assert weighted_percentile([0.0, 0.5], [1.0, 0.0], 90) == 0.0

    @given(
        st.lists(st.floats(-1, 2, **finite), min_size=1, max_size=30),
        st.data(),
    )
    def test_zero_weight_rows_are_ignored(self, values, data):
        n = len(values)
        weights = data.draw(
            st.lists(st.floats(0.01, 100, **finite), min_size=n, max_size=n)
        )
        extra = data.draw(st.lists(st.floats(-1, 2, **finite), min_size=1, max_size=5))
        p = data.draw(st.sampled_from([10, 25, 50, 75, 90]))
        base = weighted_percentile(values, weights, p)
        padded = weighted_percentile(values + extra, weights + [0.0] * len(extra), p)
        assert padded == pytest.approx(base)
        assert min(values) <= base <= max(values)

    @given(
        st.lists(st.floats(-1, 2, **finite), min_size=2, max_size=30),
        st.data(),
    )
    def test_monotone_in_percentile(self, values, data):
        n = len(values)
        weights = data.draw(
            st.lists(st.floats(0.01, 100, **finite), min_size=n, max_size=n)
        )
        results = [weighted_percentile(values, weights, p) for p in (10, 50, 90)]
        assert results == sorted(results)

    def test_rejects_invalid_weights(self):
        with pytest.raises(ValueError):
            weighted_percentile([0.1, 0.2], [1.0, -1.0], 50)
        with pytest.raises(ValueError):
            weighted_percentile([0.1, 0.2], [0.0, 0.0], 50)


def _fake_provenance():
    manifest = {
        "policyengine_version": "5.3.0",
        "data_releases": {
            "us": {
                "model_package": {"version": "1.764.6"},
                "certified_data_artifact": {"sha256": "a" * 64},
            }
        },
    }
    return {
        "dataset_bundle": {
            "runtime_dataset": "populace_us_2024",
            "runtime_dataset_uri": "hf://example",
            "runtime_dataset_sha256": "a" * 64,
            "marginal_tax_rate_settings": {"adults": 2, "delta": 1000.0},
        },
        "bundle_manifest": manifest,
        "package_versions": {"policyengine": "5.3.0", "policyengine-us": "1.764.6"},
        "population_dataset_used": True,
        "records_sha256": "0" * 64,
        "person_records_eligible": 210,
        "person_records_used": 200,
        "rate_not_computed": {"records": 10},
    }


class TestArtifact:
    @pytest.fixture(scope="class")
    def artifact(self):
        rng = np.random.default_rng(1)
        records = PersonRecords(
            rng.lognormal(10.5, 0.8, 200),
            rng.choice([-0.2, 0.0, 0.2, 0.3, 0.5, 1.2], 200),
            rng.uniform(1, 10, 200),
        )
        return build_artifact(records, _fake_provenance())

    def test_round_trip_and_tamper_detection(self, artifact, tmp_path):
        path = tmp_path / "national.json"
        path.write_text(json.dumps(artifact))
        assert load_national_estimate(path) == artifact
        tampered = json.loads(json.dumps(artifact))
        tampered["totals"]["social_loss"] *= 2
        path.write_text(json.dumps(tampered))
        with pytest.raises(ValueError, match="hash"):
            load_national_estimate(path)

    def test_records_validation(self):
        with pytest.raises(ValueError):
            PersonRecords(np.array([0.0]), np.array([0.3]), np.array([1.0]))
        with pytest.raises(ValueError):
            PersonRecords(np.array([1.0]), np.array([np.nan]), np.array([1.0]))
        with pytest.raises(ValueError):
            PersonRecords(np.array([1.0]), np.array([0.3]), np.array([-1.0]))


class TestCommittedArtifact:
    """Identities on the committed aggregate that the paper quotes."""

    @pytest.fixture(scope="class")
    def committed(self):
        return load_national_estimate()

    def test_group_totals_add_up(self, committed):
        totals = committed["totals"]
        scale = abs(totals["private_regret"])
        for group in ("quintiles", "mtr_bands"):
            rows = [r for r in committed[group] if "private_regret" in r]
            for name in FIELDS:
                assert _close(sum(r[name] for r in rows), totals[name], scale)
        rows = [totals, committed["subsidy_inclusive"], *committed["quintiles"]]
        for row in rows:
            assert _close(
                row["social_loss"], row["private_regret"] - row["revenue_change"], scale
            )

    def test_domains_cover_every_record(self, committed):
        provenance = committed["provenance"]
        used = provenance["person_records_used"]
        assert sum(d["records"] for d in committed["domain"].values()) == used
        assert sum(b["records"] for b in committed["mtr_bands"]) == used
        assert (
            used + provenance["rate_not_computed"]["records"]
            == provenance["person_records_eligible"]
        )

    def test_representative_identity(self, committed):
        for name in ("second_order", "social_loss"):
            d = committed["representative_worker"][name]
            assert _close(
                d["population"] - d["at_means"],
                d["rate_dispersion"] + d["covariance"],
                abs(d["population"]),
            )

    def test_every_eligible_earner_has_a_computed_rate(self, committed):
        """The paper says the raised limit covers every earner in the sample."""
        provenance = committed["provenance"]
        settings = provenance["dataset_bundle"]["marginal_tax_rate_settings"]
        assert provenance["rate_not_computed"]["records"] == 0
        assert settings["adults"] > settings["default_adults"]
        assert (
            provenance["person_records_used"] == provenance["person_records_eligible"]
        )


class TestExtraction:
    """The PolicyEngine path, with the simulation replaced by fixed arrays."""

    @pytest.fixture
    def fake_simulation(self, monkeypatch):
        calls = []
        raw = {
            "employment_income": np.array([0.0, 20e3, 50e3, 90e3, 30e3, 40e3, 0.0]),
            "self_employment_income": np.array([0.0, 5e3, -8e3, 0.0, 0, 0, 12e3]),
            "sstb_self_employment_income": np.array([0.0, 0, 0, 1e3, 0, 0, 0]),
            "marginal_tax_rate": np.array([0.0, -0.1, 0.25, 0.35, 1.2, 0.0, 0.4]),
            "person_weight": np.array([5.0, 2.0, 3.0, 1.0, 1.0, 4.0, 2.0]),
            "age": np.array([40.0, 30.0, 45.0, 50.0, 70.0, 22.0, 33.0]),
            "adult_earnings_index": np.array([1.0, 1.0, 2.0, 1.0, 1.0, 3.0, 1.0]),
        }
        manifest = _fake_provenance()["bundle_manifest"]
        bundle = {
            **_fake_provenance()["dataset_bundle"],
            "marginal_tax_rate_settings": {
                "adults": 2,
                "default_adults": 2,
                "delta": 1000.0,
            },
        }

        def simulate(year):
            calls.append(year)
            return {k: v.copy() for k, v in raw.items()}, bundle

        monkeypatch.setattr(national, "_simulate", simulate)
        monkeypatch.setattr(
            "taxuncertainty.analysis.policyengine_budgets._installed_provenance",
            lambda: {
                "bundle_manifest": manifest,
                "package_versions": _fake_provenance()["package_versions"],
                "population_dataset_used": False,
            },
        )
        return calls

    def test_filters_and_reports_uncomputed_rates(self, fake_simulation, tmp_path):
        cache = tmp_path / "records.npz"
        records, provenance = national.extract_person_records(2024, cache)
        # Age 70 and zero earnings are dropped; index 3 has no computed rate.
        # A self-employed-only earner is kept.
        assert provenance["person_records_eligible"] == 5
        assert provenance["person_records_used"] == 4
        assert provenance["rate_not_computed"]["records"] == 1
        assert provenance["rate_not_computed"]["weighted_workers"] == 4.0
        assert list(records.marginal_tax_rate) == [-0.1, 0.25, 0.35, 0.4]
        # Earnings add positive self-employment income; losses are ignored.
        assert list(records.earnings) == [25e3, 50e3, 91e3, 12e3]
        assert provenance["records_sha256"] == records.digest()
        # A second call reads the cache instead of simulating again.
        again, _ = national.extract_person_records(2024, cache)
        assert fake_simulation == [2024]
        assert again.digest() == records.digest()

    def test_rejects_cache_for_another_year(self, fake_simulation, tmp_path):
        """Review finding: a 2024 cache must not be relabeled as 2025."""
        cache = tmp_path / "records.npz"
        national.extract_person_records(2024, cache)
        with pytest.raises(ValueError, match="2025"):
            national.extract_person_records(2025, cache)

    def test_cli_writes_a_loadable_artifact(self, fake_simulation, tmp_path):
        output = tmp_path / "national.json"
        assert national.main(["--output", str(output)]) == 0
        artifact = load_national_estimate(output)
        assert artifact["domain"]["negative_rate"]["records"] == 1
        assert artifact["totals"]["weighted_workers"] == 6.0

    def test_rejects_uncertified_dataset(self, fake_simulation, tmp_path):
        output = tmp_path / "national.json"
        national.main(["--output", str(output)])
        artifact = json.loads(output.read_text())
        artifact["provenance"]["dataset_bundle"]["runtime_dataset_sha256"] = "b" * 64
        artifact["artifact_sha256"] = national.content_sha256(artifact)
        output.write_text(json.dumps(artifact))
        with pytest.raises(ValueError, match="certified"):
            load_national_estimate(output)
