"""Trace-driven traffic/interruption simulation, not historical measurements.

Replay the occupancy and active-PCI inputs of energy-over-time/Plot3.ipynb.
Assume offered demand is served outside modeled handover interruptions. This
does not run the RF simulator, an optimizer, or a packet-level network model.
"""

import hashlib
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd


DIRECTORY = Path(__file__).resolve().parent
CONFIG = DIRECTORY / "input/simulation.json"
DATA_KIND = "simulated_trace_replay"


def _ordered_trace(frame, columns):
    values = frame[["Time(h)", *columns]].apply(pd.to_numeric, errors="raise")
    values = values.sort_values("Time(h)").reset_index(drop=True)
    if values.empty or not np.isfinite(values.to_numpy()).all():
        raise ValueError("Replay traces must contain finite numeric observations.")
    times = values["Time(h)"].to_numpy() * 3600
    if (np.diff(times) <= 0).any() or times[0] < 0 or times[-1] > 86400:
        raise ValueError("Replay trace times must be unique and lie within the 24-hour day.")
    return times, values[columns].to_numpy()


def _rebalance(assignments, active, rng):
    """Move users from inactive or overfull cells into equally sized cell groups."""
    target = np.full(len(active), len(assignments) // len(active), dtype=int)
    target[:len(assignments) % len(active)] += 1
    move = ~np.isin(assignments, active)
    destinations = []
    for cell, capacity in zip(active, target):
        attached = np.flatnonzero(assignments == cell)
        if len(attached) > capacity:
            move[rng.choice(attached, len(attached) - capacity, replace=False)] = True
        elif len(attached) < capacity:
            destinations.extend([cell] * (capacity - len(attached)))
    movers = np.flatnonzero(move)
    rng.shuffle(movers)
    if len(movers) != len(destinations):
        raise ValueError("Cell reassignment did not conserve users.")
    assignments[movers] = destinations
    return movers


def replay(occupancy, power, config):
    """Integrate user traffic and interruption windows exactly between trace events."""
    interval = config["sample_interval_seconds"]
    if not isinstance(interval, int) or interval <= 0 or 86400 % interval:
        raise ValueError("Sample interval must be a positive integer divisor of 86400.")
    low, high = config["demand_min_mbps"], config["demand_max_mbps"]
    interruption = config["handover_interruption_ms"] / 1000
    if not (np.isfinite([low, high, interruption]).all() and 0 < low <= high and interruption >= 0):
        raise ValueError("Demand limits and interruption duration are invalid.")
    ue_time, ue_values = _ordered_trace(occupancy, ["Connected UEs"])
    ue_counts = np.rint(ue_values[:, 0]).astype(int)
    if (ue_counts <= 0).any():
        raise ValueError("Replay requires at least one connected user throughout the day.")
    pci_columns = [name for name in power if name.startswith("pci_")]
    if not pci_columns:
        raise ValueError("Power trace must contain pci_* columns.")
    power_time, power_values = _ordered_trace(power, pci_columns)
    masks = np.abs(power_values) > 1e-9  # Same active-PCI rule as Plot3.ipynb.
    if (~masks.any(axis=1)).any():
        raise ValueError("Replay requires at least one active cell throughout the day.")
    edges = np.arange(0, 86400 + interval, interval)
    knots = np.unique(np.r_[edges, ue_time, power_time])
    rng = np.random.default_rng(config["random_seed"])
    active = np.flatnonzero(masks[0])
    demands = rng.uniform(low, high, ue_counts[0]) / 1000
    assignments = np.resize(active, len(demands))
    rng.shuffle(assignments)
    outage_end = np.zeros(len(demands))
    totals = np.zeros((len(edges) - 1, 5))  # baseline/lost Gbit, UE/cell seconds, handovers
    events = []

    for start, end in zip(knots[:-1], knots[1:]):
        ue_index = max(0, np.searchsorted(ue_time, start, side="right") - 1)
        power_index = max(0, np.searchsorted(power_time, start, side="right") - 1)
        desired = ue_counts[ue_index]
        new_active = np.flatnonzero(masks[power_index])
        if desired < len(demands):
            keep = np.sort(rng.choice(len(demands), desired, replace=False))
            demands, assignments, outage_end = demands[keep], assignments[keep], outage_end[keep]
        existing = len(demands)
        if desired > existing:
            count = desired - existing
            demands = np.r_[demands, rng.uniform(low, high, count) / 1000]
            assignments = np.r_[assignments, rng.choice(new_active, count)]
            outage_end = np.r_[outage_end, np.zeros(count)]
        handovers = 0
        if not np.array_equal(new_active, active):
            movers = _rebalance(assignments, new_active, rng)
            movers = movers[movers < existing]  # Initial attachment is not a handover.
            handovers = len(movers)
            # Repeated interruptions of the same UE are combined, not double-counted.
            outage_end[movers] = np.maximum(outage_end[movers], start + interruption)
            events.append({
                "time_s": float(start), "time_h": float(start / 3600),
                "active_pci_before": len(active), "active_pci_after": len(new_active),
                "deactivated_pci": len(np.setdiff1d(active, new_active)),
                "activated_pci": len(np.setdiff1d(new_active, active)),
                "connected_ues": len(demands), "simulated_handovers": handovers,
                "data_kind": DATA_KIND,
            })
            active = new_active
        duration = end - start
        baseline_volume = float(demands.sum() * duration)
        lost_volume = float(np.dot(demands, np.clip(outage_end - start, 0, duration)))
        if not 0 <= lost_volume <= baseline_volume * (1 + 1e-12):
            raise ValueError("Simulated lost volume exceeds available traffic.")
        bin_index = int(start // interval)
        totals[bin_index] += [baseline_volume, lost_volume, len(demands) * duration,
                              len(active) * duration, handovers]

    samples = pd.DataFrame({
        "interval_start_s": edges[:-1], "interval_end_s": edges[1:],
        "baseline_gbps": totals[:, 0] / interval,
        "solution_gbps": (totals[:, 0] - totals[:, 1]) / interval,
        "simulated_lost_gbit": totals[:, 1],
        "mean_connected_ues": totals[:, 2] / interval,
        "mean_active_pci": totals[:, 3] / interval,
        "simulated_handovers": totals[:, 4].astype(int),
        "data_kind": DATA_KIND,
    })
    event_columns = ["time_s", "time_h", "active_pci_before", "active_pci_after",
                     "deactivated_pci", "activated_pci", "connected_ues",
                     "simulated_handovers", "data_kind"]
    return samples, pd.DataFrame(events, columns=event_columns)


def generate_inputs(config_path=CONFIG, input_dir=None):
    """Write a repeatable simulated CSV, cell-transition log, and provenance."""
    config_path = Path(config_path)
    config_bytes = config_path.read_bytes()
    config = json.loads(config_bytes)
    sources = {}
    frames = {}
    for key in ("occupancy_source", "power_source"):
        path = (DIRECTORY / config[key]).resolve()
        content = path.read_bytes()
        frames[key] = pd.read_csv(io.BytesIO(content))
        sources[key] = {"path": config[key], "sha256": hashlib.sha256(content).hexdigest()}
    samples, events = replay(frames["occupancy_source"], frames["power_source"], config)
    input_dir = Path(input_dir) if input_dir is not None else DIRECTORY / "input"
    input_dir.mkdir(parents=True, exist_ok=True)
    samples_path = input_dir / "simulated_throughput.csv"
    events_path = input_dir / "simulated_cell_transitions.csv"
    samples.to_csv(samples_path, index=False)
    events.to_csv(events_path, index=False)
    baseline_volume = float((samples.baseline_gbps * config["sample_interval_seconds"]).sum())
    manifest = {
        "data_kind": DATA_KIND,
        "historical_throughput_observations": False,
        "configuration": config,
        "config_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": sources,
        "samples_sha256": hashlib.sha256(samples_path.read_bytes()).hexdigest(),
        "events_sha256": hashlib.sha256(events_path.read_bytes()).hexdigest(),
        "interval_count": len(samples), "duration_seconds": 86400,
        "cell_transition_count": len(events),
        "simulated_handover_count": int(samples.simulated_handovers.sum()),
        "uncalibrated_daily_loss_percent": 100 * float(samples.simulated_lost_gbit.sum()) / baseline_volume,
        "software_versions": {"numpy": np.__version__, "pandas": pd.__version__},
        "assumptions": [
            "Previous-sample occupancy and active-cell states match the as-of alignment in Plot3; first and last states extend to the day endpoints.",
            "Fractional occupancy is rounded to integer users; departing users are selected at random.",
            "Each arriving UE draws a uniform demand within the configured range and retains it until departure.",
            "Demand is fully served outside interruption windows; radio capacity and packet queues are not modeled.",
            "Active-cell transitions rebalance users evenly across active cells, preserving assignments where possible; this is not a replay of the original optimizer.",
            "40.5 ms is a configured interruption assumption from the manuscript, not a newly measured delay.",
            "Cell states and occupancy are archived inputs; UE demands, associations, and handovers are simulated.",
            "Subsequent calibration to 0.71 percent creates an illustrative loss series, not a new physical prediction from the interruption model.",
        ],
    }
    (input_dir / "simulation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return samples_path, manifest
