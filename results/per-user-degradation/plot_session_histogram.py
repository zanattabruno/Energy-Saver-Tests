"""Plot a modeled per-user loss distribution with a specified daily aggregate."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, LogLocator, MaxNLocator, NullLocator
import numpy as np
import pandas as pd


DIRECTORY = Path(__file__).resolve().parent
OUTPUT_NAME = "per-user-throughput-loss"
DAILY_LOSS_PERCENT = 0.71


def generate(source, output_dir):
    source, output_dir = Path(source), Path(output_dir)
    frame = pd.read_csv(source)
    required = ["baseline_gbit", "lost_gbit", "connected_seconds"]
    if frame.empty or not set(required).issubset(frame):
        raise ValueError("Expected per-user traffic volumes and connected durations.")
    values = frame[required].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError("Traffic volumes and durations must be finite and nonnegative.")
    if (frame.baseline_gbit <= 0).any() or (frame.connected_seconds <= 0).any():
        raise ValueError("Every session needs positive baseline volume and duration.")
    if (frame.lost_gbit > frame.baseline_gbit).any():
        raise ValueError("Input loss exceeds baseline volume.")
    source_aggregate = float(100 * frame.lost_gbit.sum() / frame.baseline_gbit.sum())
    if source_aggregate <= 0:
        raise ValueError("The source needs positive modeled loss to define its distribution.")
    multiplier = DAILY_LOSS_PERCENT / source_aggregate
    for column in ("lost_gbit", "solution_gbit", "solution_mbps", "loss_percent"):
        if column in frame:
            frame["source_" + column] = frame[column]
    frame["lost_gbit"] = frame.lost_gbit * multiplier
    if (frame.lost_gbit > frame.baseline_gbit).any():
        raise ValueError("The specified daily aggregate would exceed an individual user's baseline volume.")
    frame["solution_gbit"] = frame.baseline_gbit - frame.lost_gbit
    frame["solution_mbps"] = 1000 * frame.solution_gbit / frame.connected_seconds
    frame["loss_percent"] = 100 * frame.lost_gbit / frame.baseline_gbit
    frame["data_kind"] = "modeled_loss_distribution_with_target_aggregate"
    losses = (100 * frame.lost_gbit / frame.baseline_gbit).to_numpy()
    aggregate = float(100 * frame.lost_gbit.sum() / frame.baseline_gbit.sum())
    np.testing.assert_allclose(aggregate, DAILY_LOSS_PERCENT, rtol=1e-12, atol=1e-12)
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = output_dir / OUTPUT_NAME
    frame.to_csv(stem.with_suffix(".csv"), index=False)
    # Match the original daily panel's 30 bins, with the horizontal scale
    # following the displayed losses. All users, including the full tail, remain.
    edges = np.linspace(0, losses.max() * (1 + 1e-9), 31)
    width = float(edges[1] - edges[0])
    counts, _ = np.histogram(losses, edges)
    if counts.sum() != len(frame):
        raise ValueError("Histogram bounds excluded users.")
    percentages = 100 * counts / len(frame)
    pd.DataFrame({"left_percent": edges[:-1], "right_percent": edges[1:],
                  "user_count": counts, "users_percent": percentages}).to_csv(
                      output_dir / f"{OUTPUT_NAME}-bins.csv", index=False)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    nonempty = counts > 0
    lower_limit = 10 ** np.floor(np.log10(percentages[nonempty].min() / 2))
    ax.set_yscale("log")
    # Empty bins stay blank, and each bar top retains its actual percentage.
    ax.bar(edges[:-1][nonempty], percentages[nonempty] - lower_limit,
           bottom=lower_limit, width=width, align="edge", color="#4477AA",
           edgecolor="white", linewidth=0.65, zorder=3)
    ax.set_xlim(0, edges[-1])
    ax.set_ylim(lower_limit, 100)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 5, 10]))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%g"))
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=7))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%g%%"))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.set_xlabel("Throughput loss relative to baseline (%)", labelpad=9)
    ax.set_ylabel("Users in each cohort (%)", labelpad=9)
    ax.grid(axis="y", color="#E3E6E9", zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.text(0.97, 0.93,
            f"Daily aggregate loss: {aggregate:.2f}%\n"
            f"95th percentile: {np.quantile(losses, 0.95):.2f}%",
            transform=ax.transAxes, ha="right", va="top", fontsize=10,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.9})
    fig.tight_layout()
    fig.savefig(stem.with_suffix(".pdf"), bbox_inches="tight", metadata={
        "Title": "Per-user throughput-loss distribution",
        "Subject": "Simulated loss distribution with lost volumes uniformly adjusted to a 0.71% daily aggregate",
        "CreationDate": None, "ModDate": None})
    fig.savefig(stem.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.close(fig)
    report = {
        "data_kind": "modeled_loss_distribution_with_target_aggregate",
        "source": str(source.resolve()),
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "output_csv_sha256": hashlib.sha256(stem.with_suffix(".csv").read_bytes()).hexdigest(),
        "user_sessions": len(frame),
        "daily_aggregate_loss_percent": aggregate,
        "source_daily_aggregate_loss_percent": source_aggregate,
        "target_daily_aggregate_loss_percent": DAILY_LOSS_PERCENT,
        "loss_volume_multiplier": multiplier,
        "method": "Multiply modeled user lost volumes by target/source aggregate; keep baseline volumes fixed.",
        "mean_individual_loss_percent": float(losses.mean()),
        "median_individual_loss_percent": float(np.median(losses)),
        "p95_individual_loss_percent": float(np.quantile(losses, 0.95)),
        "maximum_individual_loss_percent": float(losses.max()),
        "zero_loss_users_percent": float(100 * (losses == 0).mean()),
        "bin_width_percentage_points": width,
        "histogram_bin_count": len(counts),
        "individual_loss_formula": "100 * lost_gbit / baseline_gbit",
        "aggregate_formula": "100 * sum(lost_gbit) / sum(baseline_gbit)",
        "limitations": [
            "The target aggregate is imposed. Agreement with it is not independent experimental validation.",
            "Adjusted losses are not predictions of the original 40.5 ms interruption model.",
            "The distribution is conditional on simulated user associations and handover interruptions.",
            "No measured individual losses or 77.5% QoS-unsatisfied subgroup are identified.",
            "The daily aggregate is weighted by baseline data volume and differs from the mean individual percentage loss.",
        ],
    }
    stem.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    stem.with_suffix(".caption.txt").write_text(
        "Distribution of per-user throughput reductions across the 24-hour trace, "
        "with a logarithmic vertical axis and empty bins left blank. "
        "Session lost volumes are uniformly adjusted to a daily aggregate of 0.71%. "
        "The annotations report the volume-weighted daily aggregate and the 95th percentile of individual loss. User associations "
        "are simulated, and radio-capacity deficits are outside this model.\n"
    )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DIRECTORY / "input/whole_day_sessions.csv")
    parser.add_argument("--output-dir", type=Path, default=DIRECTORY / "out")
    args = parser.parse_args()
    report = generate(args.input, args.output_dir)
    print(json.dumps(report, indent=2))
