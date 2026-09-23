# Paper Figure 14: per-user throughput loss

This directory contains only Figure 14, its input and output data, and the
scripts and checks needed to reproduce it.

## Files

- `generate_sessions.py`: generates the daily session input from the archived
  occupancy and active-cell traces using `../throughput-loss/simulate.py`.
- `input/whole_day_sessions.csv` and `.json`: original modeled session volumes
  and their source/configuration provenance.
- `plot_session_histogram.py`: produces the Figure 14 histogram.
- `out/per-user-throughput-loss.pdf` and `.png`: the figure used in the paper.
- `out/per-user-throughput-loss.csv`: displayed values and original values in
  `source_*` columns.
- `out/per-user-throughput-loss-bins.csv`: bin edges, counts, and percentages.
- `out/per-user-throughput-loss.json`: figure statistics and provenance.
- `out/per-user-throughput-loss.caption.txt`: descriptive caption.
- `test_simulated_users.py`: session identity and traffic-conservation checks.

## Reproduce

From the Energy-Saver-Tests repository root:

```bash
python3 results/per-user-degradation/generate_sessions.py
python3 results/per-user-degradation/plot_session_histogram.py
```

To redraw the figure from the existing input, run only the second command.
Both scripts also work from another working directory. Dependencies are numpy,
pandas, and matplotlib. Run the checks with:

```bash
python3 -B -m unittest discover -s results/per-user-degradation -p 'test_simulated_users.py' -v
```

The paper includes a copy at `Figures/per-user-throughput-loss.pdf`; the letter
uses `letter/figures/r1_q3_per_user_loss.pdf`. After changing the plot, update
those copies before compiling the documents.

## Figure and data

The histogram covers 14,491 modeled user sessions across the 24-hour trace,
with 30 equal-width bins including zero losses and the full tail. The canvas
is 6.4 by 3.2 inches, without an upper title. Both axes are linear, with
"Throughput degradation (%)" on the x-axis and "User sessions (%)" on the
y-axis. The y-axis starts at zero. Empty bins remain blank. Statistics use two decimal places.

The daily aggregate is 0.71%, computed as total lost volume divided by total
baseline volume.
Modeled lost volumes are multiplied by approximately 830.962366 to obtain the
requested aggregate, while baseline volumes remain fixed. The original input
is preserved and the numerical adjustment is recorded in the output JSON.

The input models 40.5 ms handover interruptions, random departures and arrivals,
and evenly rebalanced cell associations. Its provenance JSON records the exact
configuration, seed, source hashes, and assumptions. The adjusted distribution
is conditional on these simulated associations and the uniform volume scaling.
It is not measured per-user evidence or a prediction of the original interruption
model, and does not identify the 77.5% of users below their QoS demands.

The shaded region and dashed line mark 2.39% degradation, the 95th percentile
rounded to two decimals. The annotation counts 13,766 of 14,491 modeled
sessions (94.9969%, displayed as 95.0%) at or below that threshold using
individual values, not histogram-bin totals. Its denominator includes all
modeled sessions and its reference is the all-on baseline, not requested
throughput or the subgroup of QoS-unsatisfied UEs.
