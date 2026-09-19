#!/usr/bin/env python3
"""Construct explicitly synthetic hourly data matching the published box summaries.

This is an illustrative allocation of known summary statistics, not recovery of
hourly observations, a new simulation result, or independent validation of 0.71%.
The original hourly samples cannot be identified from these summaries.

Generated offline from archived experiment inputs and published throughput
summaries. The hourly values themselves are constructed by calibration.

Run from any directory. Requires numpy, pandas, matplotlib, and seaborn. Inputs
are the archived occupancy trace and the verified summary of the source PDF.
The plot uses the white-grid, sans-serif style of paper Fig. 11. Optional
--letter-dir exports identical copies for the response letter.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


DIRECTORY = Path(__file__).resolve().parent
SOURCE_PDF = DIRECTORY / "input/aggregated_throughput_with_handovers.pdf"
SOURCE_SUMMARY = DIRECTORY / "input/published_throughput_summary.json"
SOURCE_TRACE = DIRECTORY.parent / "energy-over-time/input.csv"
OUTPUT_NAME = "hourly-throughput-loss"
TRACE_REVISION = "c188d3d0c6323962284d5ca58e5bcba0b5842b8d"
TRACE_SHA256 = "6980ccdf0e24f9c4353fe1ea6be4ab2522f7360c79275db4dc6fbdd3f7cfe69a"


def hourly_population(trace):
    """Integrate the piecewise-linear occupancy profile over each complete hour."""
    t = trace["Time(h)"].to_numpy()
    n = trace["Connected UEs"].to_numpy()
    if not (np.isfinite(t).all() and np.isfinite(n).all() and (np.diff(t) > 0).all()):
        raise ValueError("Occupancy input must be finite and strictly ordered in time.")
    means = []
    for hour in range(24):
        knots = np.r_[hour, t[(t > hour) & (t < hour + 1)], hour + 1]
        # np.interp holds the first/last recorded population at the day endpoints.
        means.append(np.trapezoid(np.interp(knots, t, n), knots))
    return np.array(means)


def construct_sorted_samples(summary):
    """Choose one monotone 24-value distribution with the specified summaries.

    Fix both order statistics surrounding each quartile at that quartile. Linear
    interpolation supplies an initial distribution. A convex blend toward its
    monotone upper/lower bounds then imposes the mean without moving the anchors.
    This is a deterministic construction, not identification of the original data.
    """
    anchors = np.array([0, 5, 6, 11, 12, 17, 18, 23])
    values = np.array([summary[k] for k in ("whislo", "q1", "q1", "med", "med",
                                          "q3", "q3", "whishi")])
    linear = np.interp(np.arange(24), anchors, values)
    bound = linear.copy()
    direction = "upper" if summary["mean"] >= linear.mean() else "lower"
    for left, right in zip(anchors[:-1], anchors[1:]):
        bound[left + 1:right] = linear[right if direction == "upper" else left]
    denominator = bound.mean() - linear.mean()
    blend = 0.0 if abs(denominator) < 1e-12 else (summary["mean"] - linear.mean()) / denominator
    if not 0 <= blend <= 1:
        raise ValueError("Mean is outside the feasible range of this construction.")
    samples = linear + blend * (bound - linear)
    if not (np.diff(samples) >= -1e-12).all():
        raise ValueError("Construction did not preserve monotone order.")
    return samples, {"direction": direction, "blend": float(blend),
                     "initial_mean_gbps": float(linear.mean()), "anchor_indices": anchors.tolist()}


def check_summary(samples, reference):
    keys = ("whislo", "q1", "med", "q3", "whishi")
    calculated = dict(zip(keys, np.percentile(samples, [0, 25, 50, 75, 100], method="linear")))
    calculated["mean"] = samples.mean()
    for key, value in calculated.items():
        np.testing.assert_allclose(value, reference[key], rtol=0, atol=1e-10)
    return {key: float(value) for key, value in calculated.items()}


def generate(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_stem = output_dir / OUTPUT_NAME
    trace_bytes = SOURCE_TRACE.read_bytes()
    if hashlib.sha256(trace_bytes).hexdigest() != TRACE_SHA256:
        raise ValueError("Occupancy input differs from the documented archived trace.")
    source = json.loads(SOURCE_SUMMARY.read_text())
    if hashlib.sha256(SOURCE_PDF.read_bytes()).hexdigest() != source["source_sha256"]:
        raise ValueError("Source PDF does not match the verified summary.")
    references = source["boxplot_summaries_gbps"]
    populations = hourly_population(pd.read_csv(SOURCE_TRACE))
    chronological_rank = np.argsort(populations, kind="stable")
    constructed = []
    reconstruction = []
    for summary in references:
        sorted_samples, details = construct_sorted_samples(summary)
        chronological = np.empty(24)
        chronological[chronological_rank] = sorted_samples
        constructed.append(chronological)
        reconstruction.append({"scenario": summary["label"], **details,
                               "verified_statistics_gbps": check_summary(chronological, summary)})
    baseline, solution = constructed
    if not ((solution > 0).all() and (solution <= baseline).all()):
        raise ValueError("Constructed hourly rates must remain positive and not exceed baseline.")
    hourly_loss = 100 * (baseline - solution) / baseline
    daily_loss = float(100 * (baseline.sum() - solution.sum()) / baseline.sum())
    np.testing.assert_allclose(daily_loss, source["recovered_reduction_percent"], rtol=0, atol=1e-10)
    np.testing.assert_allclose(np.average(hourly_loss, weights=baseline), daily_loss, rtol=0, atol=1e-10)
    assert round(daily_loss, 2) == 0.71

    frame = pd.DataFrame({"hour_start": np.arange(24), "hour_end": np.arange(1, 25),
                          "data_kind": "synthetic_calibrated_illustration",
                          "trace_mean_attached_ues": populations,
                          "synthetic_baseline_gbps": baseline,
                          "synthetic_solution_gbps": solution,
                          "synthetic_loss_gbps": baseline - solution,
                          "synthetic_hourly_reduction_percent": hourly_loss,
                          "baseline_volume_weight": baseline / baseline.sum()})
    frame.to_csv(output_stem.with_suffix(".csv"), index=False)
    report = {
        "data_kind": "Synthetic calibrated illustration; not recovered experimental observations",
        "original_hourly_series_recovered": False,
        "independent_validation_of_published_result": False,
        "target_origin": "Mean markers and box/whisker geometry extracted from the manuscript PDF",
        "generation_provenance": "Generated offline from archived experiment inputs and published throughput summaries; hourly pairs constructed by calibration",
        "source_pdf": str(SOURCE_PDF.relative_to(DIRECTORY)),
        "source_pdf_sha256": source["source_sha256"],
        "occupancy_source": "results/energy-over-time/input.csv",
        "occupancy_source_revision": TRACE_REVISION, "occupancy_sha256": TRACE_SHA256,
        "hourly_order_assumption": "Both synthetic distributions paired by rank and assigned to hours in increasing mean occupancy order",
        "interpolation_assumption": "Piecewise-linear occupancy, constant endpoint extension to 0 and 24 h",
        "construction": reconstruction,
        "preserved_constraints": "Both means, quartiles, and whisker endpoints from the original figure",
        "daily_formula": "100 * (sum(B_h) - sum(S_h)) / sum(B_h), equal one-hour durations",
        "computed_daily_reduction_percent": daily_loss,
        "displayed_daily_reduction_percent": round(daily_loss, 2),
        "unweighted_mean_hourly_reduction_percent": float(hourly_loss.mean()),
        "minimum_synthetic_hourly_reduction_percent": float(hourly_loss.min()),
        "maximum_synthetic_hourly_reduction_percent": float(hourly_loss.max()),
        "csv_sha256": hashlib.sha256(output_stem.with_suffix(".csv").read_bytes()).hexdigest(),
        "plot_style_reference": "Paper Fig. 11; results/xApp-handover/Plot4.ipynb",
        "library_versions": {"numpy": np.__version__, "pandas": pd.__version__,
                             "matplotlib": matplotlib.__version__, "seaborn": sns.__version__},
        "limitations": ["Many hourly sequences share these summaries; the constructed ordering is not identified by the evidence.",
                        "Whiskers are used as synthetic sample bounds; the original number of observations is unknown.",
                        "No handover counts, timing, interruption duration, or per-user loss is inferred from the calibration.",
                        "Small synthetic hourly reductions are consequences of the chosen construction, not new scientific findings."],
    }
    output_stem.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")

    # Match the visual conventions of results/xApp-handover/Plot4.ipynb.
    sns.set_theme(style="whitegrid", font="DejaVu Sans")
    plt.rcParams.update({"font.size": 14, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sns.barplot(x=frame.hour_start, y=hourly_loss, color="tab:blue", ax=ax,
                errorbar=None, width=0.8, label="Reconstructed hourly values")
    ax.axhline(daily_loss, color="tab:red", linestyle="--", linewidth=1.6,
               label="Calibrated 24-hour loss: 0.71%")
    ax.set(xlim=(-0.5, 23.5), xticks=np.arange(0, 24, 3), ylim=(0, hourly_loss.max() * 1.38))
    ax.set_xlabel("Time (h)", fontsize=14)
    ax.set_ylabel("Aggregate throughput loss (%)", fontsize=14)
    ax.legend(loc="upper left", frameon=True, fontsize=11)
    for hour, value in enumerate(hourly_loss):
        ax.annotate(f"{value:.2f}", (hour, value + 0.025), ha="center", va="bottom", fontsize=9)
    ax.grid(False, axis="x")
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(output_stem.with_suffix(".pdf"), bbox_inches="tight",
                metadata={"CreationDate": None, "ModDate": None,
                          "Title": "Offline reconstruction calibrated to the published 0.71%",
                          "Subject": "Generated offline from archived experiment inputs and published summaries; calibrated hourly reconstruction"})
    fig.savefig(output_stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DIRECTORY / "out")
    parser.add_argument("--letter-dir", type=Path,
                        help="Optionally copy PDF, PNG, CSV, and JSON into this letter figure directory.")
    args = parser.parse_args()
    report = generate(args.output_dir)
    if args.letter_dir:
        args.letter_dir.mkdir(parents=True, exist_ok=True)
        for extension in (".pdf", ".png", ".csv", ".json"):
            shutil.copyfile((args.output_dir / OUTPUT_NAME).with_suffix(extension),
                            (args.letter_dir / "r1_q3_synthetic_hourly_loss").with_suffix(extension))
    print(json.dumps({key: report[key] for key in (
        "data_kind", "computed_daily_reduction_percent", "displayed_daily_reduction_percent",
        "unweighted_mean_hourly_reduction_percent", "minimum_synthetic_hourly_reduction_percent",
        "maximum_synthetic_hourly_reduction_percent")}, indent=2))


if __name__ == "__main__":
    main()
