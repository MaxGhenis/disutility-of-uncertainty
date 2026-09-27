"""Reproduce exact illustrative results and the paper's numerical artifacts.

The default pipeline never downloads survey data or reports national welfare
estimates. Run ``python -m taxuncertainty.pipeline --check`` to detect drift.
"""

import argparse
import json
import sys
from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path

import numpy as np

from taxuncertainty.analysis.calibration import (
    Illustration,
    beliefs_with_rmse,
    private_regret_approx,
)
from taxuncertainty.analysis.national import load_national_estimate, national_dataset
from taxuncertainty.analysis.policyengine_budgets import load_household_budget
from taxuncertainty.analysis.rjt_replication import load_replication
from taxuncertainty.analysis.study1_evidence import load_evidence
from taxuncertainty.models.accounting import evaluate_worker
from taxuncertainty.models.beliefs import NormalBeliefs
from taxuncertainty.models.planner import SocialPlanner
from taxuncertainty.models.schedules import (
    BudgetSegment,
    PiecewiseLinearBudget,
    compare_budgets,
)

DATA_DIR = Path(__file__).parent / "data"
# Cross product used to bound the interior approximation's error.
ACCURACY_ELASTICITIES = (0.25, 0.33, 0.50)
ACCURACY_TAX_RATES = (0.25, 0.30, 0.43)
ACCURACY_STD_ERRORS = (0.08, 0.12, 0.15)
RESULTS_PATH = DATA_DIR / "results.json"


def model_source_hash():
    root = Path(__file__).parent
    digest = sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(str(path.relative_to(root)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def _scenarios(inputs):
    return [
        ("informed", "No error", NormalBeliefs()),
        ("unbiased", "Unbiased", beliefs_with_rmse(0, inputs.error_rmse)),
        ("bias_minus_3", "Bias -3 pp", beliefs_with_rmse(-0.03, inputs.error_rmse)),
        ("bias_minus_6", "Bias -6 pp", beliefs_with_rmse(-0.06, inputs.error_rmse)),
        ("bias_plus_3", "Bias +3 pp", beliefs_with_rmse(0.03, inputs.error_rmse)),
        ("underestimate_1", "Certain -1 pp", NormalBeliefs(-0.01, 0)),
    ]


def _budget_examples(inputs):
    def linear(slope):
        return PiecewiseLinearBudget(
            (BudgetSegment(0, 100000, slope, upper_closed=True),)
        )

    examples = [
        (
            "Progressive",
            PiecewiseLinearBudget(
                (
                    BudgetSegment(0, 30000, 0.9),
                    BudgetSegment(30000, 100000, 0.65, 7500, upper_closed=True),
                )
            ),
            linear(0.75),
        ),
        (
            "Earnings subsidy",
            PiecewiseLinearBudget(
                (
                    BudgetSegment(0, 15000, 1.2),
                    BudgetSegment(15000, 100000, 0.7, 7500, upper_closed=True),
                )
            ),
            linear(0.8),
        ),
        (
            "Benefit cliff",
            PiecewiseLinearBudget(
                (
                    BudgetSegment(0, 45000, 0.7, 8000, upper_closed=True),
                    BudgetSegment(
                        45000, 100000, 0.7, lower_closed=False, upper_closed=True
                    ),
                )
            ),
            linear(0.7),
        ),
    ]
    return [
        {
            "label": label,
            "status": "synthetic schedule and assumed perceived budget",
            "true_budget": asdict(true),
            "perceived_budget": asdict(perceived),
            "outcome": asdict(
                compare_budgets(true, perceived, inputs.hourly_wage, inputs.preferences)
            ),
        }
        for label, true, perceived in examples
    ]


def _household_fixture():
    path = DATA_DIR / "household_budget.json"
    sample = load_household_budget(path)
    return {
        "status": "executed household model; finite grid, no population estimate",
        "artifact_sha256": json.loads(path.read_text())["artifact_sha256"],
        "package_versions": sample.provenance["package_versions"],
        "configuration": sample.provenance["configuration"],
        "measure": sample.provenance["net_income_measure"],
        "discretization": sample.budget.discretization(),
        "selected_outcomes": [
            {"earnings": y, "net_income": sample.budget.net_income(y)}
            for y in (0, 25000, 50000, 100000)
        ],
    }


def _national_summary():
    """Committed national aggregates, minus the bulky bundle manifest."""
    artifact = load_national_estimate()
    provenance = artifact["provenance"]
    summary = {
        "status": artifact["status"],
        "artifact_sha256": artifact["artifact_sha256"],
        "package_versions": provenance["package_versions"],
        "dataset": national_dataset(provenance),
        "year": provenance["year"],
        "person_records_total": provenance["person_records_total"],
        "person_records_eligible": provenance["person_records_eligible"],
        "person_records_used": provenance["person_records_used"],
        "rate_not_computed": provenance["rate_not_computed"],
        "records_sha256": provenance["records_sha256"],
    }
    for key in (
        "assumptions",
        "domain",
        "totals",
        "subsidy_inclusive",
        "quintiles",
        "mtr_bands",
        "mtr_percentiles",
        "representative_worker",
        "sensitivity",
    ):
        summary[key] = artifact[key]
    return summary


def compute_results(seed=42):
    """Compute scenario results; no file writes and no PolicyEngine import."""
    inputs = Illustration(seed=seed)
    prefs = inputs.preferences
    wages = np.random.default_rng(seed).lognormal(
        np.log(inputs.hourly_wage) - 0.5 * inputs.wage_log_std**2,
        inputs.wage_log_std,
        inputs.synthetic_workers,
    )
    scenarios = []
    for key, label, beliefs in _scenarios(inputs):
        outcome = evaluate_worker(inputs.hourly_wage, inputs.tax_rate, prefs, beliefs)
        scenarios.append(
            {
                "id": key,
                "label": label,
                "beliefs": asdict(beliefs),
                "worker": asdict(outcome),
                "local_private_approximation": private_regret_approx(
                    inputs.earnings,
                    inputs.elasticity,
                    inputs.tax_rate,
                    outcome.realized_rmse**2,
                ),
            }
        )

    planner_results = {}
    for weighting in ("equal", "inverse_wage"):
        planner = SocialPlanner(social_weights=weighting)
        rows = []
        for key, label, beliefs in _scenarios(inputs):
            optimum = planner.optimal_tax_result(wages, prefs, beliefs=beliefs)
            evaluation = asdict(
                planner.evaluate(inputs.tax_rate, wages, prefs, beliefs)
            )
            # Per-worker arrays are not needed for the paper; retain aggregate accounting.
            evaluation.pop("baseline_hours")
            evaluation.pop("expected_hours")
            rows.append(
                {
                    "id": key,
                    "label": label,
                    "optimum": asdict(optimum),
                    "at_reference_tax": evaluation,
                }
            )
        planner_results[weighting] = rows

    sensitivity = []
    for eps in (0.25, 0.33, 0.50):
        altered = replace(inputs, elasticity=eps)
        for sd in (0.08, 0.12, 0.15):
            outcome = evaluate_worker(
                inputs.hourly_wage,
                inputs.tax_rate,
                altered.preferences,
                NormalBeliefs(0, sd),
            )
            sensitivity.append(
                {
                    "elasticity": eps,
                    "std_error": sd,
                    "private_regret": outcome.private_regret,
                    "revenue_change": outcome.revenue_change,
                    "social_loss": outcome.social_loss,
                }
            )

    accuracy = []
    for tax in sorted(
        set(np.linspace(0, 0.99, 100).tolist() + [0, 0.3, 0.8, 0.95, 0.99])
    ):
        # Normalize informed earnings to $55k at EACH rate to compare like scales.
        altered = replace(inputs, tax_rate=tax)
        outcome = evaluate_worker(
            inputs.hourly_wage,
            tax,
            altered.preferences,
            NormalBeliefs(0, inputs.error_rmse),
        )
        latent = private_regret_approx(
            inputs.earnings, inputs.elasticity, tax, inputs.error_rmse**2
        )
        realized = private_regret_approx(
            inputs.earnings, inputs.elasticity, tax, outcome.realized_rmse**2
        )
        accuracy.append(
            {
                "tax_rate": tax,
                "exact_private_regret": outcome.private_regret,
                "latent_moment_approximation": latent,
                "realized_moment_approximation": realized,
                "latent_ratio": latent / outcome.private_regret,
                "realized_ratio": realized / outcome.private_regret,
            }
        )

    # Accuracy of the historical interior formula across the elasticity,
    # error-dispersion and tax-rate ranges the note has used. Informed
    # earnings are normalized to $55,000 in every cell.
    approximation_grid = []
    for eps in ACCURACY_ELASTICITIES:
        for tax in ACCURACY_TAX_RATES:
            altered = replace(inputs, elasticity=eps, tax_rate=tax)
            for sd in ACCURACY_STD_ERRORS:
                outcome = evaluate_worker(
                    inputs.hourly_wage,
                    tax,
                    altered.preferences,
                    NormalBeliefs(0, sd),
                )
                latent = private_regret_approx(inputs.earnings, eps, tax, sd**2)
                approximation_grid.append(
                    {
                        "elasticity": eps,
                        "tax_rate": tax,
                        "std_error": sd,
                        "exact_private_regret": outcome.private_regret,
                        "latent_moment_approximation": latent,
                        "error_pct": 100 * (latent / outcome.private_regret - 1),
                    }
                )

    bias_curve = []
    planner = SocialPlanner()
    for mean in np.linspace(-0.10, 0.10, 21):
        beliefs = beliefs_with_rmse(float(mean), inputs.error_rmse)
        optimum = planner.optimal_tax_result(wages, prefs, beliefs=beliefs)
        bias_curve.append(
            {
                "mean_error": float(mean),
                "std_error": beliefs.std_error,
                "optimal_tax": optimum.tax_rate,
                "at_boundary": optimum.at_boundary,
            }
        )

    unbiased = next(row for row in scenarios if row["id"] == "unbiased")
    high_order = evaluate_worker(
        inputs.hourly_wage,
        inputs.tax_rate,
        prefs,
        NormalBeliefs(0, inputs.error_rmse),
        quadrature_order=512,
    )
    results = {
        "schema_version": 2,
        "status": (
            "illustrative scenarios and a conditional national aggregation; "
            "not an identified national welfare estimate"
        ),
        "provenance": {
            "model_source_sha256": model_source_hash(),
            "method": "deterministic Gauss-Legendre quadrature with explicit censoring atoms",
            "quadrature_order": 256,
            "seed": seed,
            "data_source": "synthetic wage sample; no survey weights",
        },
        "assumptions": inputs.assumptions(),
        "scenarios": scenarios,
        "planner": planner_results,
        "sensitivity": sensitivity,
        "approximation_accuracy": accuracy,
        "approximation_grid": approximation_grid,
        "bias_curve": bias_curve,
        "nonlinear_examples": _budget_examples(inputs),
        "household_fixture": _household_fixture(),
        "national_estimate": _national_summary(),
        "observed_calibration": load_replication(),
        "study1_evidence": load_evidence(),
        "validation": {
            "baseline_private_quadrature_difference": abs(
                high_order.private_regret - unbiased["worker"]["private_regret"]
            ),
            "baseline_social_quadrature_difference": abs(
                high_order.social_loss - unbiased["worker"]["social_loss"]
            ),
        },
    }

    # A single JSON-compatible structure is shared by callers and stored files.
    return json.loads(json.dumps(results, allow_nan=False))


def _json(data):
    return json.dumps(data, indent=2, allow_nan=False) + "\n"


def generate_results(output_path=None, seed=42):
    """Generate the version-2 JSON; national estimates from version 1 are retired."""
    results = compute_results(seed)
    path = Path(output_path) if output_path is not None else RESULTS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_json(results))
    return results


def _table(headers, rows, caption, label):
    lines = [
        "<!-- Generated by taxuncertainty.pipeline; do not edit. -->",
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] + ["---:"] * (len(headers) - 1)) + "|",
    ]
    lines.extend("| " + " | ".join(str(value) for value in row) + " |" for row in rows)
    return "\n".join(lines) + f"\n\n: {caption} {{#{label}}}\n"


def paper_artifacts(results):
    """Return generated text files, used identically by render and --check."""
    scenarios = results["scenarios"]
    lookup = {row["id"]: row for row in scenarios}
    inverse = {row["id"]: row for row in results["planner"]["inverse_wage"]}
    empirical = results["observed_calibration"]
    study1, study2 = empirical["study1"], empirical["study2"]
    audit = results["study1_evidence"]
    native = audit["native_checks"]
    screened = audit["selection"][3]
    own = next(r for r in audit["slope_diagnostics"] if r["panel"] == "own_bracket")
    repeat = audit["repeated"]
    numbers = {
        "unbiased_private": f'{lookup["unbiased"]["worker"]["private_regret"]:.2f}',
        "unbiased_revenue_loss": f'{-lookup["unbiased"]["worker"]["revenue_change"]:.2f}',
        "unbiased_social": f'{lookup["unbiased"]["worker"]["social_loss"]:.2f}',
        "small_bias_private": f'{lookup["underestimate_1"]["worker"]["private_regret"]:.2f}',
        "small_bias_revenue": f'{lookup["underestimate_1"]["worker"]["revenue_change"]:.2f}',
        "small_bias_social_gain": f'{-lookup["underestimate_1"]["worker"]["social_loss"]:.2f}',
        "optimal_informed": f'{100*inverse["informed"]["optimum"]["tax_rate"]:.2f}',
        "optimal_unbiased": f'{100*inverse["unbiased"]["optimum"]["tax_rate"]:.2f}',
        "optimal_bias_minus_3": f'{100*inverse["bias_minus_3"]["optimum"]["tax_rate"]:.2f}',
        "model_hash": results["provenance"]["model_source_sha256"][:12],
        "rjt_respondents": str(study2["table4_primary"]["n"]),
        "rjt_archive_hash": empirical["provenance"]["archive_sha256"][:12],
        "s1_archive_people": f'{native["archive_respondents"]:,}',
        "s1_archive_rows": f'{native["archive_forecasts"]:,}',
        "s1_people": f'{native["primary_respondents"]:,}',
        "s1_rows": f'{native["primary_forecasts"]:,}',
        "s1_reused_rows": f'{native["retained_estimates_rows"]:,}',
        "s1_reused_columns": str(native["retained_numeric_columns_exactly_matched"]),
        "s1_compatible_100": str(
            next(
                r["compatible"]
                for r in audit["affine_compatibility"]
                if r["dollar_cap"] == 100
            )
        ),
        "s1_incidental_repeat_gap": f'{audit["pair_repeats"]["duplicate_income_outcome_ranges"]["max"]:,.0f}',
        "s1_float_changes": str(native["processed_differences_only_float32"]),
        "s1_other_changes": str(native["processed_differences_beyond_float32"]),
        "s1_other_people": str(native["respondents_changed_beyond_float32"]),
        "s1_outside": str(native["local_outside_own_bracket"]),
        "s1_nonaffine": str(own["observed_nonlinear_gt_005"]),
        "s1_affine_candidate_n": f'{own["n_ge3_distinct"]:,}',
        "s1_nominal_departure": f'{own["nominal_max_deviation"]["max"]:,.2f}',
        "s1_phaseout_rows": str(native["within_bracket_phaseout_forecasts"]),
        "s1_phaseout_discrepancy": f'{audit["independent_arithmetic"]["nominal_departure_minus_stored_phaseout_tax_max_abs_dollars"]:.7f}',
        "s1_selected_n": f'{screened["n"]:,}',
        "s1_selected_income": f'{screened["median_income"]:,.0f}',
        "s1_original_income": f'{audit["selection"][0]["median_income"]:,.0f}',
        "s1_selected_bias": f'{100*screened["mean_error"]:.2f}',
        "s1_minimum_cap": f'{audit["affine_compatibility"][0]["median_minimum_dollar_error"]:,.2f}',
        "s1_repeat_n": f'{repeat["n"]:,}',
        "s1_repeat_covariance": f'{10000*repeat["covariance"]:.2f}',
        "s1_repeat_se": f'{10000*repeat["covariance_jackknife_se"]:.2f}',
        "s1_repeat_correlation": f'{repeat["correlation"]:.7f}',
        "s1_repeat_var_a": f'{repeat["var_a"]:.10f}',
        "s1_repeat_var_b": f'{repeat["var_b"]:.10f}',
        "s1_repeat_covariance_fraction": f'{repeat["covariance"]:.10f}',
        "s1_pair_radius": f'{100*audit["selection"][0]["median_box_radius_100"]:.2f}',
        "s1_selected_radius": f'{100*screened["median_box_radius_100"]:.2f}',
        "s1_full_main_sd": f'{100*audit["full_range_processing_sd"]["taxguessmain"]:.2f}',
        "s1_full_unwinsorized_sd": f'{100*audit["full_range_processing_sd"]["taxguessds"]:.2f}',
        "s1_full_tgw5_sd": f'{100*audit["full_range_processing_sd"]["tgw5"]:.2f}',
    }

    numbers.update(_national_numbers(results))

    def money(value):
        # Different numerical backends can leave roundoff of either sign at an
        # exact zero. Normalize its displayed cents, preserving raw accounting.
        formatted = f"{value:,.2f}"
        return "0.00" if formatted == "-0.00" else formatted

    selected_accuracy = [
        row
        for row in results["approximation_accuracy"]
        if row["tax_rate"] in (0, 0.3, 0.8, 0.95, 0.99)
    ]
    artifacts = {
        "_variables.yml": _json(numbers),
        "generated/study1-selection.md": _table(
            ["Income design", "N", "Median span ($)", "Error SD (pp)"],
            [
                [
                    label,
                    f'{row["n"]:,}',
                    f'{row["median_span"]:,.0f}',
                    f'{100*row["sd_error"]:,.2f}',
                ]
                for label, row in zip(
                    (
                        "Own-income pair",
                        "Native local",
                        "Own bracket: 3+, affine",
                        "Own bracket: 4+, affine, span 5k+",
                        "Own bracket: 4+, affine, span 10k+",
                        "All 14 random draws",
                    ),
                    audit["selection"],
                )
            ],
            "Study 1 finite-design signed slope errors using processed forecasts. Counts 3+/4+ mean distinct observed incomes; span cutoffs are dollars. The observed affine screen requires at least three incomes and maximum stored-tax OLS residual at most \\$0.05. Equal respondent mass; SD denominator N. No slope clipping or latent-noise correction.",
            "tbl-study1-selection",
        ),
        "generated/study1-affine.md": _table(
            ["Cap per answer ($)", "Compatible / N", "Share (%)", "Median width (pp)"],
            [
                [
                    f'{r["dollar_cap"]:,}',
                    f'{r["compatible"]:,} / {r["respondents"]:,}',
                    f'{100*r["compatible"]/r["respondents"]:.1f}',
                    f'{100*r["median_width_among_compatible"]:.2f}',
                ]
                for r in audit["affine_compatibility"]
            ],
            "Compatibility with some affine forecast function and an assumed uniform dollar-error cap in the 2,470-person screened sample. Width is the feasible slope-set width among compatible respondents only; shares are not identified belief types.",
            "tbl-study1-affine",
        ),
        "generated/study1-covariance.md": _table(
            ["Assumed error correlation", "Implied common-target SD (pp)"],
            [
                [
                    f'{r["assumed_error_correlation"]:.7f}',
                    f'{100*r["implied_common_target_sd"]:.2f}',
                ]
                for r in audit["correlated_error_sensitivity"][::2]
            ],
            "Conditional second-moment decompositions for N=1,986. Errors are assumed orthogonal to the same latent target. The last row uses the observed correlation, displayed rounded; the exact zero-variance identity does not hold at a literal correlation of 0.100000. These are sensitivities, not estimates of error correlation or latent variance.",
            "tbl-study1-covariance",
        ),
        "generated/empirical-noise.md": _table(
            [
                "Assumed noise RMSE cap (pp)",
                "Latent bias outer (pp)",
                "Latent RMSE outer (pp)",
            ],
            [
                [f'{100*row["noise_rmse_max"]:.0f}']
                + [
                    f"{100*row[key][0]:.2f} to {100*row[key][1]:.2f}"
                    for key in ("latent_bias_outer", "latent_rmse_outer")
                ]
                for row in study2["measurement_noise_sensitivity"]["rows"]
            ],
            "Conditional measurement-noise sensitivity for the primary author-support sample. Caps are assumptions, not data estimates. Noise may be biased and correlated with latent error. Ranges are conservative and need not be jointly attainable; no finite latent upper bound follows without a noise bound.",
            "tbl-empirical-noise",
        ),
        "generated/empirical-benchmarks.md": _table(
            ["Replication target", "N forecasts/choices", "Coefficient", "SE"],
            [
                [
                    "Study 1 local scale",
                    study1["table1_pooled_panels"]["local"]["forecasts"],
                    f'{study1["table1_pooled_panels"]["local"]["coefficient"]:.5f}',
                    f'{study1["table1_pooled_panels"]["local"]["clustered_standard_error"]:.5f}',
                ]
            ]
            + [
                [
                    f"Study 2 {key}",
                    study2["table4_primary"]["n"],
                    f'{study2["table4_primary"]["coefficients"][key]:.5f}',
                    f'{study2["table4_primary"]["standard_errors"][key]:.5f}',
                ]
                for key in ("ATR", "MTR", "constant")
            ],
            "Independent native-archive reproduction of selected Table 1 and Table 4 benchmarks in Rees-Jones and Taubinsky (2020). Study 1 uses respondent-clustered SEs; Study 2 uses classical OLS SEs. The Study 1 panel includes 4,197 respondents.",
            "tbl-empirical-benchmarks",
        ),
        "generated/empirical-intervals.md": _table(
            ["Convention/sample", "Bias (pp)", "RMSE (pp)", "SD outer (pp)"],
            [
                [label]
                + [
                    f"{100*bounds[key][0]:.2f} to {100*bounds[key][1]:.2f}"
                    for key in ("bias", "rmse", "sd_outer")
                ]
                for label, bounds in (
                    ("Primary, author support", study2["interval_bounds"]["author"]),
                    ("Primary, payoff only", study2["interval_bounds"]["payoff"]),
                    (
                        "Include final-attention failures",
                        study2["include_final_attention_interval_bounds"],
                    ),
                )
            ],
            "Observed signed-error identification bounds under monetary-choice rationalization, in percentage points. Primary sample N=3,130; final-attention reinclusion N=3,603 with author support. Bounds are marginal, not joint or confidence intervals; SD bounds are conservative. No bound removes response noise or establishes population transport.",
            "tbl-empirical-intervals",
        ),
        "generated/scenarios.md": _table(
            ["Scenario", "Private loss", "Revenue change", "Social loss"],
            [
                [
                    row["label"],
                    money(row["worker"]["private_regret"]),
                    money(row["worker"]["revenue_change"]),
                    money(row["worker"]["social_loss"]),
                ]
                for row in scenarios
            ],
            "Illustrative annual dollar effects per worker at a true rate of 30%. Negative social loss means a gain; revenue is rebated and valued equally.",
            "tbl-scenarios",
        ),
        "generated/beliefs.md": _table(
            ["Scenario", "Latent mean (pp)", "Latent SD (pp)", "Latent RMSE (pp)"],
            [
                [
                    row["label"],
                    f'{100*row["beliefs"]["mean_error"]:.2f}',
                    f'{100*row["beliefs"]["std_error"]:.2f}',
                    f'{100*row["worker"]["latent_rmse"]:.2f}',
                ]
                for row in scenarios
            ],
            "Assumed belief distributions before censoring. Realized moments after censoring are recorded separately in the results JSON.",
            "tbl-beliefs",
        ),
        "generated/planner.md": _table(
            ["Scenario", "Equal weights (%)", "Inverse-wage weights (%)"],
            [
                [
                    row["label"],
                    f'{100*row["optimum"]["tax_rate"]:.2f}',
                    f'{100*inverse[row["id"]]["optimum"]["tax_rate"]:.2f}',
                ]
                for row in results["planner"]["equal"]
            ],
            "Best linear tax rates on the specified grid over 0% to 80%. Zero is a search boundary, not a claim about an unconstrained optimum.",
            "tbl-planner",
        ),
        "generated/accuracy.md": _table(
            [
                "True rate (%)",
                "Exact private loss",
                "Latent approximation",
                "Approx./exact",
            ],
            [
                [
                    f'{100*row["tax_rate"]:.0f}',
                    money(row["exact_private_regret"]),
                    money(row["latent_moment_approximation"]),
                    f'{row["latent_ratio"]:.2f}',
                ]
                for row in selected_accuracy
            ],
            "Approximation diagnostic in dollars, with informed earnings normalized to $55,000 separately at each true rate. The approximation uses the latent second moment; the exact model censors perceived rates.",
            "tbl-accuracy",
        ),
        "generated/sensitivity.md": _table(
            ["Elasticity", "SD 8 pp", "SD 12 pp", "SD 15 pp"],
            [
                [f"{eps:.2f}"]
                + [
                    money(
                        next(
                            row["social_loss"]
                            for row in results["sensitivity"]
                            if row["elasticity"] == eps and row["std_error"] == sd
                        )
                    )
                    for sd in (0.08, 0.12, 0.15)
                ]
                for eps in (0.25, 0.33, 0.5)
            ],
            "Illustrative social losses per worker in dollars under mean-zero latent errors and equal valuation of rebated revenue. These are scenario variations, not confidence bounds.",
            "tbl-sensitivity",
        ),
        "generated/nonlinear.md": _table(
            ["True budget", "Private loss", "Revenue change", "Social loss"],
            [
                [
                    row["label"],
                    money(row["outcome"]["private_regret"]),
                    money(row["outcome"]["revenue_change"]),
                    money(row["outcome"]["social_loss"]),
                ]
                for row in results["nonlinear_examples"]
            ],
            "Synthetic nonlinear examples, dollars. True and perceived budgets and exact choices are stored in the results; these are not statutory schedules.",
            "tbl-nonlinear",
        ),
        "generated/household.md": _table(
            ["Earnings", "Household net income"],
            [
                [money(row["earnings"]), money(row["net_income"])]
                for row in results["household_fixture"]["selected_outcomes"]
            ],
            "Selected actual PolicyEngine outcomes for the specified 2024 Texas household, in dollars. Health benefits are excluded; some other noncash benefits are included.",
            "tbl-household",
        ),
    }
    artifacts.update(_national_tables(results, money))
    return artifacts


def _billions(value):
    return f"{value / 1e9:,.1f}"


def _effect(value):
    """Verb and unsigned billions, so prose reads correctly for either sign."""
    return ("adds" if value >= 0 else "subtracts"), _billions(abs(value))


def _national_numbers(results):
    """Inline values for the national aggregation and approximation grid."""
    nat = results["national_estimate"]
    totals, domain = nat["totals"], nat["domain"]
    workers = totals["weighted_workers"]
    all_workers = sum(d["weighted_workers"] for d in domain.values())
    rep = nat["representative_worker"]
    second, social = rep["second_order"], rep["social_loss"]
    top = nat["quintiles"][-1]
    grid = results["approximation_grid"]
    worst = min(grid, key=lambda row: row["error_pct"])
    baseline = next(
        row
        for row in grid
        if (row["elasticity"], row["tax_rate"], row["std_error"]) == (0.33, 0.3, 0.12)
    )
    former = next(
        row
        for row in grid
        if (row["elasticity"], row["tax_rate"], row["std_error"]) == (0.5, 0.43, 0.15)
    )
    pct_in = nat["mtr_percentiles"]["in_domain"]
    social_range = [row["social_loss"] for row in nat["sensitivity"]]
    earnings_shares = [
        100 * row["social_loss"] / row["total_earnings"] for row in nat["quintiles"]
    ]
    rate_settings = nat["dataset"]["marginal_tax_rate_settings"]
    return {
        "national_rate_adults": str(rate_settings["adults"]),
        "national_default_rate_adults": str(rate_settings["default_adults"]),
        "national_not_computed": f'{nat["rate_not_computed"]["records"]:,}',
        "national_quintile_share_min": f"{min(earnings_shares):.2f}",
        "national_quintile_share_max": f"{max(earnings_shares):.2f}",
        "national_year": str(nat["year"]),
        "national_records": f'{nat["person_records_used"]:,}',
        "national_workers_m": f"{workers / 1e6:,.1f}",
        "national_social_bn": _billions(totals["social_loss"]),
        "national_private_bn": _billions(totals["private_regret"]),
        "national_revenue_loss_bn": _billions(-totals["revenue_change"]),
        "national_second_order_bn": _billions(totals["second_order"]),
        "national_social_per_worker": f'{totals["social_loss"] / workers:,.0f}',
        "national_private_per_worker": f'{totals["private_regret"] / workers:,.0f}',
        "national_social_ratio": f'{totals["social_loss"] / totals["private_regret"]:.2f}',
        "national_inclusive_social_bn": _billions(
            nat["subsidy_inclusive"]["social_loss"]
        ),
        "national_negative_share": f'{100 * domain["negative_rate"]["weighted_workers"] / all_workers:.1f}',
        "national_cliff_share": f'{100 * domain["rate_at_least_one"]["weighted_workers"] / all_workers:.2f}',
        "national_excluded_workers_m": f"{(all_workers - workers) / 1e6:,.1f}",
        "national_top_quintile_share": f'{100 * top["social_loss"] / totals["social_loss"]:.1f}',
        "national_social_min_bn": _billions(min(social_range)),
        "national_social_max_bn": _billions(max(social_range)),
        "rep_mean_earnings": f'{rep["mean_earnings"]:,.0f}',
        "rep_mean_rate": f'{100 * rep["mean_marginal_rate"]:.1f}',
        **{
            f"rep_{name}_{key}": value
            for name, terms in (("second_order", second), ("social", social))
            for key, value in (
                ("at_means_bn", _billions(terms["at_means"])),
                (
                    "direction",
                    (
                        "exceeds"
                        if terms["population"] >= terms["at_means"]
                        else "falls short of"
                    ),
                ),
                (
                    "gap_pct",
                    f'{100 * abs(terms["population"] / terms["at_means"] - 1):.1f}',
                ),
                ("dispersion_verb", _effect(terms["rate_dispersion"])[0]),
                ("dispersion_bn", _effect(terms["rate_dispersion"])[1]),
                ("covariance_verb", _effect(terms["covariance"])[0]),
                ("covariance_bn", _effect(terms["covariance"])[1]),
            )
        },
        **{f"mtr_{k}": f"{v:.2f}" for k, v in pct_in.items()},
        "approx_baseline_error": f'{-baseline["error_pct"]:.2f}',
        "approx_worst_error": f'{-worst["error_pct"]:.2f}',
        "approx_worst_elasticity": f'{worst["elasticity"]:.2f}',
        "approx_worst_tax": f'{100 * worst["tax_rate"]:.0f}',
        "approx_worst_sd": f'{100 * worst["std_error"]:.0f}',
        "approx_former_extreme_error": f'{-former["error_pct"]:.2f}',
        "approx_max_overstatement": f'{max(row["error_pct"] for row in grid):.2f}',
    }


def _national_tables(results, money):
    nat = results["national_estimate"]
    totals = nat["totals"]

    def per_worker(row, key):
        return money(row[key] / row["weighted_workers"])

    quintiles = _table(
        [
            "Quintile",
            "Mean earnings ($)",
            "Mean MTR (%)",
            "Private loss",
            "Revenue change",
            "Social loss",
            "Social loss (% of earnings)",
            "Share of social loss (%)",
        ],
        [
            [
                row["quintile"],
                f'{row["total_earnings"] / row["weighted_workers"]:,.0f}',
                f'{100 * row["mean_marginal_rate"]:.1f}',
                per_worker(row, "private_regret"),
                per_worker(row, "revenue_change"),
                per_worker(row, "social_loss"),
                f'{100 * row["social_loss"] / row["total_earnings"]:.2f}',
                f'{100 * row["social_loss"] / totals["social_loss"]:.1f}',
            ]
            for row in nat["quintiles"]
        ],
        "Conditional national aggregation by earnings quintile of in-domain workers. Dollar columns are annual amounts per worker; quintile totals are sums of per-person amounts, so shares add to 100%. Assumes the illustrative elasticity and mean-zero 12-point latent errors censored to [0, 1].",
        "tbl-national-quintiles",
    )

    def band_label(row):
        lo, hi = row["rate_min"], row["rate_max_exclusive"]
        if lo is None:
            return "Below 0%"
        if hi is None:
            return f"{100 * lo:.0f}% or more"
        return f"{100 * lo:.0f}% to {100 * hi:.0f}%"

    bands = _table(
        [
            "Marginal rate",
            "Workers (m)",
            "Private loss (\\$bn)",
            "Revenue change (\\$bn)",
            "Social loss (\\$bn)",
            "Taylor approx. (\\$bn)",
        ],
        [
            [band_label(row), f'{row["weighted_workers"] / 1e6:,.1f}']
            + (
                [
                    _billions(row[key])
                    for key in (
                        "private_regret",
                        "revenue_change",
                        "social_loss",
                        "second_order",
                    )
                ]
                if "private_regret" in row
                else ["not evaluated"] * 4
            )
            for row in nat["mtr_bands"]
        ],
        "National totals by PolicyEngine marginal tax rate, which is never clipped. Rates below zero lie outside the default perceived-rate bounds; rates of 100% or more imply zero informed hours on a linear budget, contradicting positive observed earnings. Neither group enters the main estimate.",
        "tbl-national-bands",
    )
    sensitivity = _table(
        ["Elasticity", "SD 8 pp", "SD 12 pp", "SD 15 pp"],
        [
            [f"{eps:.2f}"]
            + [
                _billions(
                    next(
                        row["social_loss"]
                        for row in nat["sensitivity"]
                        if row["elasticity"] == eps and row["std_error"] == sd
                    )
                )
                for sd in (0.08, 0.12, 0.15)
            ]
            for eps in (0.25, 0.33, 0.5)
        ],
        "Conditional national social loss in billions of dollars per year across assumed elasticities and mean-zero latent error dispersions. These are scenario variations, not confidence bounds.",
        "tbl-national-sensitivity",
    )
    grid = results["approximation_grid"]
    accuracy = _table(
        ["Elasticity", "SD (pp)", "Rate 25%", "Rate 30%", "Rate 43%"],
        [
            [f"{eps:.2f}", f"{100 * sd:.0f}"]
            + [
                f'{next(r["error_pct"] for r in grid if (r["elasticity"], r["std_error"], r["tax_rate"]) == (eps, sd, tax)):+.2f}'
                for tax in ACCURACY_TAX_RATES
            ]
            for eps in ACCURACY_ELASTICITIES
            for sd in ACCURACY_STD_ERRORS
        ],
        "Error of the interior approximation, in percent of exact expected private regret; negative values understate. Perceived rates are censored to [0, 1], so the latent second moment overstates realized errors at low rates.",
        "tbl-approximation-grid",
    )
    return {
        "generated/national-quintiles.md": quintiles,
        "generated/national-bands.md": bands,
        "generated/national-sensitivity.md": sensitivity,
        "generated/approximation-grid.md": accuracy,
    }


def generate_figures(results, paper_dir):
    """Export publication figures with Matplotlib; no interactive runtime needed."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.hashsalt": "taxuncertainty-v2",
        }
    )
    folder = Path(paper_dir) / "generated"
    folder.mkdir(parents=True, exist_ok=True)
    selected = [
        row
        for row in results["scenarios"]
        if row["id"] in ("unbiased", "bias_minus_3", "bias_plus_3")
    ]
    fig, ax = plt.subplots(figsize=(7.1, 3.7), layout="constrained")
    positions = np.arange(len(selected))
    for offset, key, label, color in [
        (-0.25, "private_regret", "Private loss", "#346888"),
        (0, "revenue_change", "Revenue change", "#649178"),
        (0.25, "social_loss", "Social loss", "#a45345"),
    ]:
        ax.bar(
            positions + offset,
            [row["worker"][key] for row in selected],
            0.23,
            label=label,
            color=color,
        )
    ax.axhline(0, color="#444444", linewidth=0.8)
    ax.set_xticks(positions, [row["label"] for row in selected])
    ax.set_ylabel("Annual dollars per worker")
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.16))
    fig.savefig(folder / "welfare.png", dpi=190)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.4), layout="constrained")
    curve = results["bias_curve"]
    informed = results["planner"]["inverse_wage"][0]["optimum"]["tax_rate"]
    axes[0].plot(
        [row["mean_error"] * 100 for row in curve],
        [row["optimal_tax"] * 100 for row in curve],
        color="#346888",
        lw=2,
    )
    axes[0].axhline(informed * 100, color="#777777", ls="--", label="Informed optimum")
    axes[0].set_xlabel("Latent mean error (percentage points)")
    axes[0].set_ylabel("Optimal linear tax (%)")
    axes[0].legend(frameon=False, fontsize=8)
    accuracy = results["approximation_accuracy"]
    for key, label, color, style in [
        ("latent_ratio", "Latent moment", "#a45345", "-"),
        ("realized_ratio", "Realized moment", "#346888", "--"),
    ]:
        axes[1].plot(
            [row["tax_rate"] * 100 for row in accuracy],
            [row[key] for row in accuracy],
            label=label,
            color=color,
            ls=style,
        )
    axes[1].axhline(1, color="#777777", lw=0.8)
    axes[1].set_xlabel("True tax rate (%)")
    axes[1].set_ylabel("Approximate / exact private loss")
    axes[1].legend(frameon=False, fontsize=8)
    fig.savefig(folder / "robustness.png", dpi=190)
    plt.close(fig)
    (folder / "figures.json").write_text(
        _json(
            {
                "model_source_sha256": results["provenance"]["model_source_sha256"],
                "seed": results["provenance"]["seed"],
                "files": {
                    name: sha256((folder / name).read_bytes()).hexdigest()
                    for name in ("welfare.png", "robustness.png")
                },
            }
        )
    )


def _equivalent(left, right):
    if isinstance(left, dict) and isinstance(right, dict):
        return left.keys() == right.keys() and all(
            _equivalent(left[key], right[key]) for key in left
        )
    if isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        return len(left) == len(right) and all(
            _equivalent(a, b) for a, b in zip(left, right)
        )
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return bool(np.isclose(left, right, rtol=1e-9, atol=1e-7))
    return left == right


def check_artifacts(results, output_path, paper_dir):
    """Check numerical and rendered-text provenance, returning stale paths."""
    output_path = Path(output_path)
    stale = []
    if not output_path.exists() or not _equivalent(
        json.loads(output_path.read_text()), results
    ):
        stale.append(str(output_path))
    parameter_path = output_path.with_name("parameters.yaml")
    if not parameter_path.exists() or not _equivalent(
        json.loads(parameter_path.read_text()), results["assumptions"]
    ):
        stale.append(str(parameter_path))
    if paper_dir is not None:
        paper_dir = Path(paper_dir)
        for name, text in paper_artifacts(results).items():
            path = paper_dir / name
            if not path.exists() or path.read_text() != text:
                stale.append(str(path))
        manifest = paper_dir / "generated/figures.json"
        expected = {
            "model_source_sha256": results["provenance"]["model_source_sha256"],
            "seed": results["provenance"]["seed"],
        }
        recorded = json.loads(manifest.read_text()) if manifest.exists() else {}
        if any(recorded.get(key) != value for key, value in expected.items()):
            stale.append(str(manifest))
        for name in ("welfare.png", "robustness.png"):
            path = paper_dir / "generated" / name
            if not path.exists() or sha256(
                path.read_bytes()
            ).hexdigest() != recorded.get("files", {}).get(name):
                stale.append(str(path))
    return stale


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if committed numerical/text artifacts differ",
    )
    parser.add_argument("--output", type=Path, default=RESULTS_PATH)
    parser.add_argument("--paper-dir", type=Path, default=Path("paper"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)
    results = compute_results(args.seed)
    if args.check:
        stale = check_artifacts(results, args.output, args.paper_dir)
        if stale:
            print("Stale generated artifacts:\n" + "\n".join(stale), file=sys.stderr)
            return 1
        print("Numerical results, generated paper text, and figure provenance agree.")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(_json(results))
    args.output.with_name("parameters.yaml").write_text(_json(results["assumptions"]))
    for name, text in paper_artifacts(results).items():
        path = args.paper_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    generate_figures(results, args.paper_dir)
    print(
        f"Generated illustrative results in {args.output} and {args.paper_dir}/generated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
