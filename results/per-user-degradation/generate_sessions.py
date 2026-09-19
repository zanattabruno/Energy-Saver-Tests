"""Generate the daily user-session input for paper Figure 14."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd


DIRECTORY = Path(__file__).resolve().parent
ENGINE_PATH = DIRECTORY.parent / "throughput-loss/simulate.py"
spec = importlib.util.spec_from_file_location("handover_replay", ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)


def user_metrics(users, prefix="session_"):
    selected = users.loc[users[prefix + "connected_seconds"] > 0].copy()
    seconds = selected[prefix + "connected_seconds"]
    baseline = selected[prefix + "baseline_gbit"]
    lost = selected[prefix + "lost_gbit"]
    if (baseline <= 0).any() or (lost < 0).any() or (lost > baseline).any():
        raise ValueError("Invalid per-user traffic-volume accounting.")
    return pd.DataFrame({
        "ue_id": selected.ue_id,
        "connected_seconds": seconds,
        "baseline_gbit": baseline,
        "solution_gbit": baseline - lost,
        "lost_gbit": lost,
        "baseline_mbps": 1000 * baseline / seconds,
        "solution_mbps": 1000 * (baseline - lost) / seconds,
        "loss_percent": 100 * lost / baseline,
        "simulated_handovers": selected[prefix + "handovers"].astype(int),
        "data_kind": "modeled_handover_only_user_session",
    }).reset_index(drop=True)


def generate(input_dir, config_path=engine.CONFIG):
    input_dir, config_path = Path(input_dir), Path(config_path)
    config = json.loads(config_path.read_text())
    sources, frames = {}, {}
    for name in ("occupancy_source", "power_source"):
        source = (engine.DIRECTORY / config[name]).resolve()
        sources[name] = {"path": str(source), "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
        frames[name] = pd.read_csv(source)
    samples, events, users = engine.replay(frames["occupancy_source"], frames["power_source"], config,
                                          return_users=True)
    day = user_metrics(users)
    np.testing.assert_allclose(day.baseline_gbit.sum(),
                               samples.baseline_gbps.sum() * config["sample_interval_seconds"], rtol=1e-12)
    np.testing.assert_allclose(day.lost_gbit.sum(), samples.simulated_lost_gbit.sum(), rtol=1e-12)
    if day.simulated_handovers.sum() != events.simulated_handovers.sum():
        raise ValueError("Per-user handovers do not match the aggregate replay.")
    input_dir.mkdir(parents=True, exist_ok=True)
    source_csv = input_dir / "whole_day_sessions.csv"
    day.to_csv(source_csv, index=False)
    report = {
        "data_kind": "trace_driven_handover_only_user_sessions",
        "historical_per_user_measurements": False,
        "configuration": config,
        "configuration_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "engine_sha256": hashlib.sha256(ENGINE_PATH.read_bytes()).hexdigest(),
        "sources": sources,
        "output_csv_sha256": hashlib.sha256(source_csv.read_bytes()).hexdigest(),
        "user_sessions": len(day),
        "baseline_volume_gbit": float(day.baseline_gbit.sum()),
        "lost_volume_gbit": float(day.lost_gbit.sum()),
        "daily_aggregate_loss_percent": float(100 * day.lost_gbit.sum() / day.baseline_gbit.sum()),
        "assumptions": [
            "Archived occupancy and active-cell states are held until the next sample, with endpoint extension.",
            "Occupancy is rounded to integers. Departures are random and arrivals receive new synthetic session IDs.",
            "Each session draws a constant uniform demand within the configured bounds and random seed.",
            "Baseline serves demand without interruption. The solution serves the same demand except during modeled handovers.",
            "Cell-state transitions rebalance users evenly, rather than replaying original optimizer or RF associations.",
            "Overlapping interruptions are integrated as their union and truncated at departure or day end.",
            "Interference, cell-capacity deficits, scheduling and retransmissions are outside this model.",
        ],
        "versions": {"numpy": np.__version__, "pandas": pd.__version__},
    }
    source_csv.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=DIRECTORY / "input")
    args = parser.parse_args()
    result = generate(args.input_dir)
    print(f"Generated {result['user_sessions']:,} sessions in {args.input_dir}")
