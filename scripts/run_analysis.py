#!/usr/bin/env python3
"""Reproducible analysis runner for uncertainty blocks (1)–(4).

Generates figures and a JSON/CSV summary into a results directory.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import List, Tuple, Dict

import numpy as np
import matplotlib.pyplot as plt

from taxuncertainty.models.utility import CobbDouglasUtility
from taxuncertainty.analysis.uncertainty import UncertaintyAnalysis


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_json(obj: Dict, path: str) -> None:
    with open(path, "w") as f:
        json.dump(obj, f, indent=2)


def save_csv(rows: List[Dict], path: str) -> None:
    if not rows:
        with open(path, "w") as f:
            f.write("\n")
        return
    keys = list(rows[0].keys())
    with open(path, "w") as f:
        f.write(",".join(keys) + "\n")
        for r in rows:
            f.write(",".join(str(r[k]) for k in keys) + "\n")


def symmetric_tax_scenarios(mean: float, sd: float) -> Tuple[List[float], List[float]]:
    zs = np.array([-1.5, -0.5, 0.0, 0.5, 1.5])
    probs = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
    rates = [float(np.clip(mean + sd * z, 0.0, 1.0)) for z in zs]
    return rates, probs.tolist()


def block1_bias_curve(
    ua: UncertaintyAnalysis,
    wage: float,
    true_tax: float,
    bias_max: float,
    n_points: int,
    transfers: float,
    total_hours: float,
) -> Dict:
    biases = np.linspace(-bias_max, bias_max, n_points)
    abs_losses = []
    pct_losses = []
    for b in biases:
        loss, loss_pct = ua.utility_loss_from_bias(
            wage, true_tax, b, transfers, total_hours
        )
        abs_losses.append(loss)
        pct_losses.append(loss_pct)

    return {
        "bias": biases.tolist(),
        "loss_abs": abs_losses,
        "loss_pct": pct_losses,
    }


def block2_uncertainty_curve(
    ua: UncertaintyAnalysis,
    wage: float,
    tax_mean: float,
    sd_max: float,
    n_points: int,
    transfers: float,
    total_hours: float,
    grid: int,
) -> Dict:
    sds = np.linspace(0.0, sd_max, n_points)
    loss_eu = []  # EU-maximizing labor
    loss_expect = []  # optimize under expected tax

    for sd in sds:
        rates, probs = symmetric_tax_scenarios(tax_mean, sd)
        # Perfect info baseline
        u_certain = ua.expected_utility_with_certainty(
            wage, rates, probs, transfers, total_hours
        )
        # Expected-tax optimization
        u_uncertain_expect = ua.expected_utility_with_uncertainty(
            wage, rates, probs, transfers, total_hours
        )
        # EU-maximization
        u_uncertain_eu, _ = ua.expected_utility_with_uncertainty_eu_max(
            wage, rates, probs, transfers, total_hours, grid
        )

        def pct_loss(u):
            return (u_certain - u) / u_certain * 100.0 if u_certain > 0 else 0.0

        loss_expect.append(pct_loss(u_uncertain_expect))
        loss_eu.append(pct_loss(u_uncertain_eu))

    return {
        "sd": sds.tolist(),
        "loss_pct_eu": loss_eu,
        "loss_pct_expected_rule": loss_expect,
    }


def block3_two_worker(
    ua: UncertaintyAnalysis,
    wage1: float,
    wage2: float,
    tax_mean: float,
    sd: float,
    total_hours: float,
    grid: int,
) -> Dict:
    rates, probs = symmetric_tax_scenarios(tax_mean, sd)
    w_certain, w_uncertain, loss = ua.two_worker_planner_misperception(
        (wage1, wage2), tax_mean, rates, probs, total_hours, grid
    )
    return {
        "welfare_certain": w_certain,
        "expected_welfare_uncertain": w_uncertain,
        "welfare_loss": loss,
    }


def block3_welfare_vs_tax(
    ua: UncertaintyAnalysis,
    wage1: float,
    wage2: float,
    tax_min: float,
    tax_max: float,
    n_grid: int,
    sd: float,
    total_hours: float,
) -> Dict:
    tax_grid = np.linspace(tax_min, tax_max, n_grid)
    certain = []
    uncertain = []
    for t in tax_grid:
        # Certain welfare
        v_certain = ua._closed_form_demogrant_certain(np.array([wage1, wage2]), t, total_hours)
        wbar = np.mean([
            ua.choice_solver.indirect_utility(wage1, t, v_certain, total_hours),
            ua.choice_solver.indirect_utility(wage2, t, v_certain, total_hours),
        ])
        certain.append(wbar)

        # Uncertain welfare (expected)
        rates, probs = symmetric_tax_scenarios(t, sd)
        wbar_c, wbar_u, _ = ua.two_worker_planner_misperception(
            (wage1, wage2), t, rates, probs, total_hours
        )
        uncertain.append(wbar_u)

    return {"tax": tax_grid.tolist(), "welfare_certain": certain, "welfare_uncertain": uncertain}


def block4_opt_tax_vs_uncertainty(
    ua: UncertaintyAnalysis,
    wage_samples: np.ndarray,
    sd_max: float,
    n_points: int,
    search_low: float,
    search_high: float,
    grid_tax: int,
) -> Dict:
    sds = np.linspace(0.0, sd_max, n_points)
    opt_certain = []
    opt_uncertain = []
    welfare_certain = []
    welfare_uncertain = []
    for sd in sds:
        res = ua.optimal_tax_rate(
            wage_samples=wage_samples,
            tax_rate_uncertainty=float(sd),
            search_range=(search_low, search_high),
            n_grid=grid_tax,
        )
        opt_certain.append(float(res.optimal_tax_certain))
        opt_uncertain.append(float(res.optimal_tax_uncertain))
        welfare_certain.append(float(res.expected_utility_certain))
        welfare_uncertain.append(float(res.expected_utility_uncertain))

    return {
        "sd": sds.tolist(),
        "opt_tax_certain": opt_certain,
        "opt_tax_uncertain": opt_uncertain,
        "welfare_certain": welfare_certain,
        "welfare_uncertain": welfare_uncertain,
    }


def plot_block1(data: Dict, outdir: str) -> None:
    plt.figure(figsize=(6, 4))
    plt.plot(data["bias"], data["loss_pct"], label="Utility loss (%)")
    plt.axvline(0, color="k", linewidth=0.8, alpha=0.5)
    plt.xlabel("Bias in perceived tax rate")
    plt.ylabel("Utility loss (% of correct info)")
    plt.title("Block 1: Utility loss vs. bias")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "block1_bias_loss.png"), dpi=150)
    plt.close()


def plot_block2(data: Dict, outdir: str) -> None:
    plt.figure(figsize=(6, 4))
    plt.plot(data["sd"], data["loss_pct_eu"], label="EU-max labor")
    plt.plot(data["sd"], data["loss_pct_expected_rule"], label="Expected-tax rule", linestyle="--")
    plt.xlabel("Tax uncertainty (standard deviation)")
    plt.ylabel("Utility loss (%)")
    plt.title("Block 2: Utility loss vs. uncertainty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "block2_uncertainty_loss.png"), dpi=150)
    plt.close()


def plot_block3(data: Dict, outdir: str) -> None:
    plt.figure(figsize=(6, 4))
    plt.plot(data["tax"], data["welfare_certain"], label="Certain")
    plt.plot(data["tax"], data["welfare_uncertain"], label="Uncertain (EU,h*)")
    plt.xlabel("Tax rate")
    plt.ylabel("Average welfare")
    plt.title("Block 3: Welfare vs. tax (two workers)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "block3_two_worker_welfare.png"), dpi=150)
    plt.close()


def plot_block4(data: Dict, outdir: str) -> None:
    # Optimal tax vs sd
    plt.figure(figsize=(6, 4))
    plt.plot(data["sd"], data["opt_tax_certain"], label="Optimal tax (certain)")
    plt.plot(data["sd"], data["opt_tax_uncertain"], label="Optimal tax (uncertain)")
    plt.xlabel("Tax uncertainty (sd)")
    plt.ylabel("Optimal tax rate")
    plt.title("Block 4: Optimal tax vs. uncertainty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "block4_opt_tax_vs_sd.png"), dpi=150)
    plt.close()

    # Welfare vs sd
    plt.figure(figsize=(6, 4))
    plt.plot(data["sd"], data["welfare_certain"], label="Welfare (certain)")
    plt.plot(data["sd"], data["welfare_uncertain"], label="Welfare (uncertain)")
    plt.xlabel("Tax uncertainty (sd)")
    plt.ylabel("Average welfare")
    plt.title("Block 4: Welfare vs. uncertainty")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, "block4_welfare_vs_sd.png"), dpi=150)
    plt.close()


def main() -> None:
    ap = argparse.ArgumentParser(description="Run uncertainty analysis blocks (1)–(4)")
    ap.add_argument("--outdir", default=None, help="Output directory (default: results/timestamp)")
    ap.add_argument("--seed", type=int, default=42)

    # Preferences and environment
    ap.add_argument("--a", type=float, default=0.5, help="Leisure exponent (a>0)")
    ap.add_argument("--b", type=float, default=0.5, help="Consumption exponent (b>0)")
    ap.add_argument("--T", type=float, default=24.0, help="Total hours available")
    ap.add_argument("--grid", type=int, default=241, help="Labor grid points for EU-max")

    # Block 1 params
    ap.add_argument("--wage", type=float, default=20.0)
    ap.add_argument("--true-tax", type=float, default=0.3)
    ap.add_argument("--bias-max", type=float, default=0.3)
    ap.add_argument("--bias-n", type=int, default=121)
    ap.add_argument("--transfers", type=float, default=0.0)

    # Block 2 params
    ap.add_argument("--uncertainty-sd-max", type=float, default=0.2)
    ap.add_argument("--uncertainty-n", type=int, default=25)

    # Block 3 params
    ap.add_argument("--wage2", type=float, default=40.0)
    ap.add_argument("--two-worker-sd", type=float, default=0.1)
    ap.add_argument("--tax-min", type=float, default=0.05)
    ap.add_argument("--tax-max", type=float, default=0.6)
    ap.add_argument("--tax-n", type=int, default=40)

    # Block 4 params
    ap.add_argument("--pop-n", type=int, default=2000)
    ap.add_argument("--wage-median", type=float, default=20.0)
    ap.add_argument("--wage-sigma", type=float, default=0.5)
    ap.add_argument("--opt-sd-max", type=float, default=0.2)
    ap.add_argument("--opt-sd-n", type=int, default=9)
    ap.add_argument("--opt-tax-low", type=float, default=0.05)
    ap.add_argument("--opt-tax-high", type=float, default=0.6)
    ap.add_argument("--opt-tax-grid", type=int, default=40)
    ap.add_argument("--use-policyengine", action="store_true", help="Use PolicyEngine-US to sample wages (if available)")

    args = ap.parse_args()

    np.random.seed(args.seed)

    outdir = args.outdir or os.path.join(
        "results", datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    ensure_dir(outdir)

    # Initialize model
    utility = CobbDouglasUtility(args.a, args.b)
    ua = UncertaintyAnalysis(utility)

    # Block 1
    block1 = block1_bias_curve(
        ua,
        wage=args.wage,
        true_tax=args.true_tax,
        bias_max=args.bias_max,
        n_points=args.bias_n,
        transfers=args.transfers,
        total_hours=args.T,
    )
    plot_block1(block1, outdir)

    # Block 2
    block2 = block2_uncertainty_curve(
        ua,
        wage=args.wage,
        tax_mean=args.true_tax,
        sd_max=args.uncertainty_sd_max,
        n_points=args.uncertainty_n,
        transfers=args.transfers,
        total_hours=args.T,
        grid=args.grid,
    )
    plot_block2(block2, outdir)

    # Block 3 (single point) and curve over tax
    block3 = block3_two_worker(
        ua,
        wage1=args.wage,
        wage2=args.wage2,
        tax_mean=args.true_tax,
        sd=args.two_worker_sd,
        total_hours=args.T,
        grid=args.grid,
    )

    block3_curve = block3_welfare_vs_tax(
        ua,
        wage1=args.wage,
        wage2=args.wage2,
        tax_min=args.tax_min,
        tax_max=args.tax_max,
        n_grid=args.tax_n,
        sd=args.two_worker_sd,
        total_hours=args.T,
    )
    plot_block3(block3_curve, outdir)

    # Block 4: Distribution of wages
    wages = None
    if args.use_policyengine:
        try:
            from taxuncertainty.data.policyengine_integration import PolicyEngineData  # type: ignore

            pe = PolicyEngineData()
            wages = pe.get_wage_distribution(n_samples=args.pop_n)
            print(f"Sampled wages from PolicyEngine-US: n={len(wages)}")
        except Exception as e:
            print(f"Warning: PolicyEngine-US not available or failed ({e}); falling back to lognormal wages.")

    if wages is None:
        mu = np.log(args.wage_median)
        wages = np.random.lognormal(mean=mu, sigma=args.wage_sigma, size=args.pop_n)
    block4 = block4_opt_tax_vs_uncertainty(
        ua,
        wage_samples=wages,
        sd_max=args.opt_sd_max,
        n_points=args.opt_sd_n,
        search_low=args.opt_tax_low,
        search_high=args.opt_tax_high,
        grid_tax=args.opt_tax_grid,
    )
    plot_block4(block4, outdir)

    # Summaries
    summary = {
        "seed": args.seed,
        "preferences": {"a": args.a, "b": args.b, "T": args.T},
        "block1": {
            "wage": args.wage,
            "true_tax": args.true_tax,
            "transfers": args.transfers,
            "bias_max": args.bias_max,
        },
        "block2": {
            "wage": args.wage,
            "tax_mean": args.true_tax,
            "sd_max": args.uncertainty_sd_max,
        },
        "block3": {
            "wages": [args.wage, args.wage2],
            "tax_mean": args.true_tax,
            "sd": args.two_worker_sd,
        },
        "block4": {
            "pop_n": args.pop_n,
            "wage_median": args.wage_median,
            "wage_sigma": args.wage_sigma,
            "sd_max": args.opt_sd_max,
            "search_range": [args.opt_tax_low, args.opt_tax_high],
        },
    }
    save_json(summary, os.path.join(outdir, "summary.json"))

    # Save key series as CSVs
    save_csv(
        [
            {"bias": b, "loss_pct": lp, "loss_abs": la}
            for b, lp, la in zip(
                block1["bias"], block1["loss_pct"], block1["loss_abs"]
            )
        ],
        os.path.join(outdir, "block1_bias_loss.csv"),
    )
    save_csv(
        [
            {"sd": s, "loss_pct_eu": l1, "loss_pct_expected_rule": l2}
            for s, l1, l2 in zip(
                block2["sd"], block2["loss_pct_eu"], block2["loss_pct_expected_rule"]
            )
        ],
        os.path.join(outdir, "block2_uncertainty_loss.csv"),
    )
    save_csv(
        [
            {"tax": t, "welfare_certain": wc, "welfare_uncertain": wu}
            for t, wc, wu in zip(
                block3_curve["tax"], block3_curve["welfare_certain"], block3_curve["welfare_uncertain"]
            )
        ],
        os.path.join(outdir, "block3_two_worker_welfare.csv"),
    )
    save_csv(
        [
            {
                "sd": s,
                "opt_tax_certain": oc,
                "opt_tax_uncertain": ou,
                "welfare_certain": wc,
                "welfare_uncertain": wu,
            }
            for s, oc, ou, wc, wu in zip(
                block4["sd"],
                block4["opt_tax_certain"],
                block4["opt_tax_uncertain"],
                block4["welfare_certain"],
                block4["welfare_uncertain"],
            )
        ],
        os.path.join(outdir, "block4_opt_tax_vs_sd.csv"),
    )

    print(f"Wrote outputs to: {outdir}")


if __name__ == "__main__":
    main()
