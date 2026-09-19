"""Numerical checks using artificial fixtures, never experimental observations."""

import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd


DIRECTORY = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("throughput_plot", DIRECTORY / "plot.py")
plot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(plot)
COLUMNS = ["interval_start_s", "interval_end_s", "baseline_gbps", "solution_gbps"]


def fixture():
    # Two unequal intervals, one boundary halfway through the second hour.
    return pd.DataFrame([[0, 5400, 100, 98], [5400, 86400, 200, 199]], columns=COLUMNS)


class CollectedThroughputTests(unittest.TestCase):
    def test_duration_weighting_and_boundary_split(self):
        frame = plot.aggregate_collected_samples(fixture().iloc[::-1])
        self.assertEqual(frame.raw_baseline_gbps[0], 100)
        self.assertEqual(frame.raw_baseline_gbps[1], 150)
        self.assertEqual(frame.raw_solution_gbps[1], 148.5)
        self.assertEqual(frame.raw_baseline_gbps[2], 200)
        self.assertEqual(frame.raw_baseline_gbps.sum(), 4650)
        self.assertEqual(frame.raw_solution_gbps.sum(), 4624.5)
        np.testing.assert_array_equal(frame.covered_seconds, np.full(24, 3600))

    def test_exact_target_and_preserved_raw_rates(self):
        samples = fixture()
        before = samples.copy(deep=True)
        frame, report = plot.calibrate_collected_samples(samples, 0.71)
        self.assertAlmostEqual(report["raw_daily_reduction_percent"], 100 * 25.5 / 4650)
        self.assertAlmostEqual(report["computed_daily_reduction_percent"], 0.71, places=12)
        from_exported_rates = 100 * (frame.raw_baseline_gbps.sum() -
                                    frame.calibrated_solution_gbps.sum()) / frame.raw_baseline_gbps.sum()
        self.assertAlmostEqual(from_exported_rates, 0.71, places=12)
        self.assertNotAlmostEqual(frame.calibrated_hourly_reduction_percent.mean(), 0.71)
        self.assertEqual(frame.raw_solution_gbps.sum(), 4624.5)
        pd.testing.assert_frame_equal(samples, before)

    def test_subdividing_intervals_does_not_change_hourly_rates(self):
        split = pd.DataFrame([[0, 1800, 100, 98], [1800, 5400, 100, 98],
                              [5400, 86400, 200, 199]], columns=COLUMNS)
        original, _ = plot.calibrate_collected_samples(fixture(), 0.71)
        subdivided, _ = plot.calibrate_collected_samples(split, 0.71)
        pd.testing.assert_frame_equal(original.drop(columns="contributing_intervals"),
                                      subdivided.drop(columns="contributing_intervals"))

    def test_signed_gains_are_preserved(self):
        samples = pd.DataFrame([[0, 3600, 100, 101], [3600, 86400, 100, 99]], columns=COLUMNS)
        frame, report = plot.calibrate_collected_samples(samples, 0.71)
        self.assertLess(frame.calibrated_hourly_reduction_percent[0], 0)
        self.assertGreater(frame.calibrated_solution_gbps[0], 100)
        self.assertAlmostEqual(report["computed_daily_reduction_percent"], 0.71)

    def test_invalid_inputs_are_rejected(self):
        cases = {}
        for label, row, column, value in [
            ("gap", 1, "interval_start_s", 5401),
            ("overlap", 1, "interval_start_s", 5399),
            ("missing start", 0, "interval_start_s", 1),
            ("missing end", 1, "interval_end_s", 86399),
            ("zero duration", 0, "interval_end_s", 0),
            ("nan", 0, "solution_gbps", np.nan),
            ("infinity", 0, "solution_gbps", np.inf),
            ("negative", 0, "solution_gbps", -1),
            ("zero baseline", 0, "baseline_gbps", 0),
        ]:
            changed = fixture().astype(float)
            changed.loc[row, column] = value
            cases[label] = changed
        cases["empty"] = fixture().iloc[:0]
        cases["missing column"] = fixture().drop(columns="solution_gbps")
        cases["duplicate"] = pd.concat([fixture(), fixture().iloc[:1]])
        for label, samples in cases.items():
            with self.subTest(label=label), self.assertRaises(ValueError):
                plot.calibrate_collected_samples(samples, 0.71)

    def test_infeasible_calibration_is_rejected_at_interval_level(self):
        # A one-second total outage needs a large adjustment to reach 0.71%.
        samples = pd.DataFrame([[0, 1, 100, 0], [1, 86400, 100, 100]], columns=COLUMNS)
        with self.assertRaisesRegex(ValueError, "invalid interval throughput"):
            plot.calibrate_collected_samples(samples, 0.71)
        for solution in (100, 101):
            samples = pd.DataFrame([[0, 86400, 100, solution]], columns=COLUMNS)
            with self.assertRaisesRegex(ValueError, "positive observed net loss"):
                plot.calibrate_collected_samples(samples, 0.71)
        for target in (0, -1, 100, np.nan, np.inf):
            with self.subTest(target=target), self.assertRaises(ValueError):
                plot.calibrate_collected_samples(fixture(), target)

    def test_generation_preserves_source_and_records_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "artificial-test-fixture.csv"
            fixture().to_csv(source, index=False)
            original = source.read_bytes()
            report = plot.generate(directory / "out", source)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(report["source_samples_sha256"], hashlib.sha256(original).hexdigest())
            self.assertFalse(report["raw_input_modified"])
            self.assertAlmostEqual(report["computed_daily_reduction_percent"], 0.71)
            self.assertNotIn("calibration_scale", report)
            for suffix in ("csv", "json", "pdf", "png"):
                self.assertGreater((directory / "out" / f"hourly-throughput-loss.{suffix}").stat().st_size, 0)
            saved = json.loads((directory / "out/hourly-throughput-loss.json").read_text())
            self.assertEqual(saved["source_interval_count"], 2)
            exported = pd.read_csv(directory / "out/hourly-throughput-loss.csv")
            self.assertEqual(len(exported), 24)
            self.assertNotIn("calibration_scale", exported.columns)

    def test_missing_source_cannot_fall_back_to_reconstruction(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            with self.assertRaisesRegex(FileNotFoundError, "No collected-data figure was generated"):
                plot.generate(directory / "out", directory / "absent.csv")
            self.assertFalse((directory / "out").exists())

    def test_output_cannot_overwrite_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "hourly-throughput-loss.csv"
            fixture().to_csv(source, index=False)
            original = source.read_bytes()
            with self.assertRaisesRegex(ValueError, "overwrite an input"):
                plot.generate(directory, source)
            self.assertEqual(source.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
