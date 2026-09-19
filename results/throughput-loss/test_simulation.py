"""Conservation and provenance tests for the trace-driven traffic simulation."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

DIRECTORY = Path(__file__).resolve().parent
modules = {}
for name in ("simulate", "plot"):
    spec = importlib.util.spec_from_file_location(name, DIRECTORY / f"{name}.py")
    modules[name] = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modules[name])
simulate, plot = modules["simulate"], modules["plot"]


class TraceReplayTests(unittest.TestCase):
    def setUp(self):
        self.config = {"sample_interval_seconds": 900, "random_seed": 42,
                       "demand_min_mbps": 10, "demand_max_mbps": 10,
                       "handover_interruption_ms": 40.5}
        self.occupancy = pd.DataFrame({"Time(h)": [0, 24], "Connected UEs": [2, 2]})

    def test_unchanged_cells_do_not_create_loss(self):
        power = pd.DataFrame({"Time(h)": [0, 24], "pci_0": [20, 20], "pci_1": [20, 20]})
        samples, events = simulate.replay(self.occupancy, power, self.config)
        np.testing.assert_allclose(samples.baseline_gbps, 0.02)
        np.testing.assert_array_equal(samples.baseline_gbps, samples.solution_gbps)
        self.assertEqual(samples.simulated_lost_gbit.sum(), 0)
        self.assertEqual(samples.simulated_handovers.sum(), 0)
        self.assertTrue(events.empty)

    def test_interruption_is_split_across_interval_boundary(self):
        power = pd.DataFrame({"Time(h)": [0, 3599.99 / 3600],
                              "pci_0": [20, 20], "pci_1": [20, 0]})
        samples, events = simulate.replay(self.occupancy, power, self.config)
        self.assertEqual(events.simulated_handovers.sum(), 1)
        self.assertAlmostEqual(samples.simulated_lost_gbit.sum(), 0.01 * 0.0405, places=12)
        self.assertAlmostEqual(samples.simulated_lost_gbit.iloc[3], 0.01 * 0.01, places=12)
        self.assertAlmostEqual(samples.simulated_lost_gbit.iloc[4], 0.01 * 0.0305, places=12)
        self.assertAlmostEqual(samples.mean_active_pci.iloc[4], 1)

    def test_overlapping_interruptions_are_not_double_counted(self):
        power = pd.DataFrame({"Time(h)": [0, 3599.99 / 3600, 1],
                              "pci_0": [20, 20, 0], "pci_1": [20, 0, 20]})
        samples, _ = simulate.replay(self.occupancy, power, self.config)
        self.assertEqual(samples.simulated_handovers.sum(), 3)
        self.assertAlmostEqual(samples.simulated_lost_gbit.sum(), 0.01 * (0.0505 + 0.0405), places=12)

    def test_reporting_resolution_preserves_total_volume(self):
        occupancy = pd.DataFrame({"Time(h)": [0.1, 6.7, 19.2], "Connected UEs": [20, 30, 10]})
        power = pd.DataFrame({"Time(h)": [0.2, 4.34, 16.8],
                              "pci_0": [20, 20, 20], "pci_1": [20, 0, 20]})
        config = {**self.config, "demand_min_mbps": 0.5, "demand_max_mbps": 25}
        coarse, coarse_events = simulate.replay(occupancy, power, config)
        fine, fine_events = simulate.replay(occupancy, power, {**config, "sample_interval_seconds": 60})
        self.assertAlmostEqual(coarse.baseline_gbps.sum() * 900, fine.baseline_gbps.sum() * 60, places=8)
        self.assertAlmostEqual(coarse.simulated_lost_gbit.sum(), fine.simulated_lost_gbit.sum(), places=12)
        pd.testing.assert_frame_equal(coarse_events, fine_events)
        expected_users = 20 * 6.7 + 30 * (19.2 - 6.7) + 10 * (24 - 19.2)
        self.assertAlmostEqual(coarse.mean_connected_ues.sum() / 4, expected_users)

    def test_archived_replay_is_reproducible_and_calibrated(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first, first_manifest = simulate.generate_inputs(input_dir=root / "one")
            second, second_manifest = simulate.generate_inputs(input_dir=root / "two")
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(first_manifest, second_manifest)
            samples = pd.read_csv(first)
            self.assertEqual(len(samples), 96)
            self.assertEqual(samples.interval_start_s.iloc[0], 0)
            self.assertEqual(samples.interval_end_s.iloc[-1], 86400)
            self.assertTrue((samples.solution_gbps <= samples.baseline_gbps).all())
            report = plot.generate(root / "out", first, simulation_metadata=first_manifest)
            self.assertAlmostEqual(report["computed_daily_reduction_percent"], 0.71, places=12)
            self.assertEqual(report["input_kind"], "simulated_trace_replay")
            exported = pd.read_csv(root / "out/hourly-throughput-loss.csv")
            self.assertTrue(exported.data_kind.str.startswith("simulated_").all())
            self.assertIn("simulated_baseline_gbps", exported)
            self.assertNotIn("raw_baseline_gbps", exported)
            self.assertNotIn("calibration_scale", report)
            # The Plot3 cell timeline is integrated exactly, including endpoint extension.
            config = json.loads(simulate.CONFIG.read_text())
            power = pd.read_csv(DIRECTORY / config["power_source"])
            times = power["Time(h)"].to_numpy() * 3600
            counts = power.filter(regex="^pci_").abs().gt(1e-9).sum(axis=1).to_numpy()
            expected = counts[0] * times[0] + np.dot(counts, np.diff(np.r_[times, 86400]))
            self.assertAlmostEqual(exported.mean_active_pci.sum() * 3600, expected, places=7)


if __name__ == "__main__":
    unittest.main()
