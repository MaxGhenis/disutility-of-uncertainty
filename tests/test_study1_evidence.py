"""Integration checks for frozen audit evidence, not new latent-model tests."""

import json
import math
import shutil
from hashlib import sha256
from pathlib import Path

import pytest

from taxuncertainty.analysis.rjt_replication import load_replication
from taxuncertainty.analysis.study1_evidence import (
    AUDIT_COMMIT,
    _one,
    build_evidence,
    digest,
    load_evidence,
    verify_bundle,
)
from taxuncertainty.pipeline import compute_results, paper_artifacts

BUNDLE = Path(__file__).parents[1] / "calibration/study1"


def test_frozen_bundle_and_cache_agree():
    data = build_evidence(BUNDLE)
    assert data == load_evidence()
    assert data["provenance"]["audit_commit"] == AUDIT_COMMIT
    assert len(verify_bundle(BUNDLE)["files"]) == 18
    assert not data["latent_beliefs_identified"]
    assert not data["welfare_input_replaced"]


@pytest.mark.parametrize("name", ["results/selection.csv", "scripts/estimators.py"])
def test_frozen_aggregate_or_estimator_drift_rejected(tmp_path, name):
    shutil.copytree(BUNDLE, tmp_path / "audit")
    target = tmp_path / "audit" / name
    target.write_bytes(target.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="frozen file mismatch"):
        verify_bundle(tmp_path / "audit")


def test_ambiguous_or_missing_cohort_does_not_silently_select():
    row = {"panel": "own_bracket", "min_span": "5000"}
    with pytest.raises(ValueError, match="exactly one"):
        _one([row, row], panel="own_bracket", min_span=5000)
    with pytest.raises(ValueError, match="exactly one"):
        _one([row], panel="own_bracket", min_span=10000)


def test_cache_corruption_and_relabeling_latent_evidence_rejected(tmp_path):
    data = load_evidence()
    data["selection"][3]["sd_error"] = 0.12
    path = tmp_path / "cache.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="checksum mismatch"):
        load_evidence(path)
    data["latent_beliefs_identified"] = True
    data.pop("artifact_sha256")
    data["artifact_sha256"] = digest(data)
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="scope or source mismatch"):
        load_evidence(path)


@pytest.mark.parametrize(
    "case",
    [
        "omitted_consumed_file",
        "source_mapping",
        "rehashed_file",
        "empty_inventory",
        "extra_entry",
    ],
)
def test_rewritten_manifest_cannot_retain_reviewed_identity(tmp_path, case):
    bundle = tmp_path / "bundle"
    shutil.copytree(BUNDLE, bundle)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    name = "results/selection.csv"
    if case in ("omitted_consumed_file", "rehashed_file"):
        path = bundle / name
        raw = path.read_bytes().replace(b"0.450752035248", b"0.123")
        assert raw != path.read_bytes()
        path.write_bytes(raw)
        if case == "omitted_consumed_file":
            del manifest["files"][name]
        else:
            manifest["files"][name].update(
                sha256=sha256(raw).hexdigest(), bytes=len(raw)
            )
    elif case == "source_mapping":
        manifest["files"][name]["source_path"] = "never-reviewed/selection.csv"
    elif case == "empty_inventory":
        manifest["files"] = {}
    else:
        manifest["files"]["unreviewed.csv"] = dict(manifest["files"][name])
        shutil.copyfile(bundle / name, bundle / "unreviewed.csv")
    manifest_path.write_text(json.dumps(manifest))
    for check in (verify_bundle, build_evidence):
        with pytest.raises(ValueError, match="reviewed manifest identity mismatch"):
            check(bundle)


@pytest.mark.parametrize("case", ["scientific_value", "source_mapping", "inventory"])
def test_self_rehashed_cache_cannot_retain_reviewed_identity(tmp_path, case):
    data = load_evidence()
    if case == "scientific_value":
        data["selection"][3]["sd_error"] = 0.123
    elif case == "source_mapping":
        data["provenance"]["frozen_files"]["results/selection.csv"][
            "source_path"
        ] = "never-reviewed/selection.csv"
    else:
        del data["provenance"]["frozen_files"]["results/selection.csv"]
    data.pop("artifact_sha256")
    data["artifact_sha256"] = digest(data)
    path = tmp_path / "cache.json"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="reviewed aggregate identity mismatch"):
        load_evidence(path)


def test_cache_identity_allows_json_formatting_without_changed_content(tmp_path):
    data = load_evidence()
    path = tmp_path / "cache.json"
    path.write_text(json.dumps(data, sort_keys=True, separators=(",", ":")))
    assert load_evidence(path) == data


def test_source_selection_processing_and_pooled_benchmarks_match():
    data = load_evidence()
    native = data["native_checks"]
    assert native["primary_respondents"] * 16 == native["primary_forecasts"]
    assert native["retained_estimates_rows"] == 14 * native["primary_respondents"]
    assert native["retained_numeric_columns_exactly_matched"] == 31
    assert native["processing_changed_forecasts"] == (
        native["processed_differences_only_float32"]
        + native["processed_differences_beyond_float32"]
    )
    own = next(r for r in data["slope_diagnostics"] if r["panel"] == "own_bracket")
    assert own["n_ge3_distinct"] - own["observed_nonlinear_gt_005"] == 3458
    for panel, old in load_replication()["study1"]["table1_pooled_panels"].items():
        new = data["pooled_benchmarks"][panel]
        assert new["n"] == old["forecasts"]
        assert new["coefficient"] == pytest.approx(old["coefficient"], abs=1e-12)
        assert new["cluster_se"] == pytest.approx(
            old["clustered_standard_error"], abs=1e-12
        )


def test_affine_counts_and_units_use_the_exact_screened_sample():
    data = load_evidence()
    chosen = data["selection"][3]
    assert chosen["n"] == 2470
    assert chosen["min_distinct"] == 4
    assert chosen["min_span_dollars"] == 5000
    assert chosen["observed_affine_screen"]
    assert 100 * chosen["sd_error"] == pytest.approx(45.0752035248)
    assert chosen["median_income"] == 62237
    rows = data["affine_compatibility"]
    assert [r["compatible"] for r in rows] == [424, 555, 1084, 1411, 2132]
    assert all(r["respondents"] == chosen["n"] for r in rows)
    assert 100 * rows[1]["median_width_among_compatible"] == pytest.approx(
        1.50983278602
    )


def test_covariance_sensitivity_preserves_moments_and_exact_threshold():
    data = load_evidence()
    repeat = data["repeated"]
    va, vb, c = (repeat[k] for k in ("var_a", "var_b", "covariance"))
    assert repeat["n"] == 1986
    assert c / math.sqrt(va * vb) == pytest.approx(repeat["correlation"], abs=1e-12)
    assert 10000 * c == pytest.approx(309.050060868)
    assert 10000 * repeat["covariance_jackknife_se"] == pytest.approx(152.545365453)
    for row in data["correlated_error_sensitivity"]:
        v, rho = row["implied_common_target_variance"], row["assumed_error_correlation"]
        assert 0 <= v <= min(va, vb)
        assert v + rho * math.sqrt((va - v) * (vb - v)) == pytest.approx(c, abs=1e-12)
        assert row["implied_common_target_sd"] ** 2 == pytest.approx(v, abs=1e-12)
    assert (
        data["correlated_error_sensitivity"][-1]["implied_common_target_variance"] == 0
    )
    # Literal 0.100000 does not reproduce these moments at zero target variance.
    assert abs(0.1 * math.sqrt(va * vb) - c) > 0.00008


def test_paper_uses_evidence_and_does_not_change_welfare_or_study2():
    results = compute_results()
    assert results["scenarios"][1]["beliefs"]["std_error"] == 0.12
    assert results["observed_calibration"] == load_replication()
    original = paper_artifacts(results)
    assert "555 / 2,470" in original["generated/study1-affine.md"]
    assert "0.1002613" in original["generated/study1-covariance.md"]
    assert "45.08" in original["generated/study1-selection.md"]
    results["study1_evidence"]["affine_compatibility"][1]["compatible"] = 554
    results["study1_evidence"]["repeated"]["covariance"] = 0.02
    changed = paper_artifacts(results)
    assert "554 / 2,470" in changed["generated/study1-affine.md"]
    assert json.loads(changed["_variables.yml"])["s1_repeat_covariance"] == "200.00"
    for name in (
        "scenarios",
        "beliefs",
        "empirical-intervals",
        "empirical-noise",
        "empirical-benchmarks",
    ):
        assert changed[f"generated/{name}.md"] == original[f"generated/{name}.md"]
