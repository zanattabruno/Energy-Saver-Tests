"""Check conservation and identities before using a modeled user distribution."""

import unittest

import numpy as np
import pandas as pd

from generate_sessions import engine, user_metrics


class UserAccountingTests(unittest.TestCase):
    def setUp(self):
        self.config = {"sample_interval_seconds": 900, "random_seed": 42,
                       "demand_min_mbps": 10, "demand_max_mbps": 10,
                       "handover_interruption_ms": 40.5}
        self.occupancy = pd.DataFrame({"Time(h)": [0, 24], "Connected UEs": [2, 2]})

    def test_constant_cells_have_zero_loss(self):
        power = pd.DataFrame({"Time(h)": [0, 24], "pci_0": [20, 20], "pci_1": [20, 20]})
        samples, events, users = engine.replay(self.occupancy, power, self.config, return_users=True)
        metrics = user_metrics(users, "session_")
        self.assertEqual(len(metrics), 2)
        np.testing.assert_allclose(metrics.connected_seconds, 86400)
        np.testing.assert_array_equal(metrics.loss_percent, 0)
        self.assertTrue(events.empty)

    def test_overlaps_and_interval_boundary_conserve_each_user(self):
        power = pd.DataFrame({"Time(h)": [0, 3599.99 / 3600, 1],
                              "pci_0": [20, 20, 0], "pci_1": [20, 0, 20]})
        samples, events, users = engine.replay(self.occupancy, power, self.config, return_users=True)
        np.testing.assert_allclose(np.sort(users.session_lost_gbit), [0.01 * 0.0405, 0.01 * 0.0505])
        self.assertAlmostEqual(users.session_lost_gbit.sum(), samples.simulated_lost_gbit.sum())
        self.assertEqual(users.session_handovers.sum(), 3)
        self.assertEqual(users.session_handovers.sum(), events.simulated_handovers.sum())

    def test_turnover_keeps_unique_ids_and_clips_departure(self):
        occupancy = pd.DataFrame({"Time(h)": [0, 1, 2], "Connected UEs": [2, 1, 3]})
        power = pd.DataFrame({"Time(h)": [0, 3599.99 / 3600],
                              "pci_0": [20, 0], "pci_1": [0, 20]})
        samples, events, users = engine.replay(occupancy, power, self.config, return_users=True)
        self.assertEqual(len(users), 4)
        self.assertTrue(users.ue_id.is_unique)
        np.testing.assert_allclose(np.sort(users.session_connected_seconds), [3600, 79200, 79200, 86400])
        self.assertAlmostEqual(users.session_lost_gbit.sum(), 0.01 * (0.01 + 0.0405), places=11)
        peak = user_metrics(users, "peak_")
        self.assertEqual(len(peak), 3)
        np.testing.assert_allclose(peak.connected_seconds, 22 * 3600)
        self.assertAlmostEqual(users.session_baseline_gbit.sum(), samples.baseline_gbps.sum() * 900)

    def test_user_recording_preserves_replay_and_reporting_resolution(self):
        occupancy = pd.DataFrame({"Time(h)": [0.1, 6.7, 19.2], "Connected UEs": [20, 30, 10]})
        power = pd.DataFrame({"Time(h)": [0.2, 4.34, 16.8],
                              "pci_0": [20, 20, 20], "pci_1": [20, 0, 20]})
        samples, events = engine.replay(occupancy, power, self.config)
        extended_samples, extended_events, users = engine.replay(occupancy, power, self.config, return_users=True)
        pd.testing.assert_frame_equal(samples, extended_samples)
        pd.testing.assert_frame_equal(events, extended_events)
        _, _, fine_users = engine.replay(occupancy, power, {**self.config, "sample_interval_seconds": 60}, return_users=True)
        pd.testing.assert_frame_equal(users, fine_users, check_exact=False, rtol=1e-10, atol=1e-10)


if __name__ == "__main__":
    unittest.main()
