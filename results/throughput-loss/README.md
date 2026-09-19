# Offline reconstruction of hourly throughput loss

This figure is generated offline from archived experiment inputs and published
throughput summaries. The **hourly values are constructed by calibration**.
They are not recovered hourly measurements or independent validation of the
reported 0.71% reduction.

## Generate the figure

Use `Plot.ipynb`, or run from the repository root:

```bash
python3 results/throughput-loss/plot.py
```

The script also works from another working directory. Its Python dependencies
are listed in `requirements.txt`. Outputs are written to `out/`:

- `hourly-throughput-loss.pdf` and `.png`: the figure, styled after manuscript
  Fig. 11 and `results/xApp-handover/Plot4.ipynb`.
- `hourly-throughput-loss.csv`: 24 hourly pairs, explicitly identified as a
  synthetic calibrated illustration.
- `hourly-throughput-loss.json`: source hashes, construction coefficients,
  verified statistics, software versions, and limitations.

The figure uses the same sans-serif font, white background, gray grid and frame,
blue bars, numerical annotations, and 14-point axis/title text as Fig. 11.
The reference line uses its red accent. No uncertainty bars are inferred from
the reconstruction.

To export identical copies for the response letter:

```bash
python3 results/throughput-loss/plot.py --letter-dir "/path/to/paper/letter/figures"
```

## Inputs and provenance

The occupancy input is `../energy-over-time/input.csv`, archived with the
experiments at revision `c188d3d0c6323962284d5ca58e5bcba0b5842b8d`. Its expected
SHA-256 is `6980ccdf0e24f9c4353fe1ea6be4ab2522f7360c79275db4dc6fbdd3f7cfe69a`.
This is the connected-user profile used as an experimental input, not an hourly
throughput measurement.

`input/aggregated_throughput_with_handovers.pdf` is an unchanged copy of the
manuscript's Fig. 13(a). `input/published_throughput_summary.json` contains its
means, quartiles, and whisker endpoints, extracted from vector geometry, together
with the PDF hash and extraction coordinates. The generator verifies that hash.
These inputs are included so this result can be generated in a standalone clone
of Energy-Saver-Tests.

## Reconstruction and interpretation

For each scenario, 24 sorted values are built from the published summaries.
Order-statistic indices 0, 5, 6, 11, 12, 17, 18, and 23 are anchored to the lower
whisker, Q1, Q1, median, median, Q3, Q3, and upper whisker. The remaining values
are interpolated and blended toward monotone bounds to match the published mean.
This preserves both means, quartiles, and whisker endpoints.

The occupancy trace is integrated over complete hours with piecewise-linear
interpolation and constant endpoint extension. Both reconstructed throughput
distributions are paired by rank and assigned to hours in increasing order of
mean occupancy. That ordering is an assumption, not recovered chronology.

For hourly means `B_h` and `S_h`, the hourly reduction is
`100 * (B_h - S_h) / B_h`. The daily reduction is
`100 * (sum(B_h) - sum(S_h)) / sum(B_h)`, which gives **0.7073416911%**, rounded
to **0.71%**. It is a baseline-volume-weighted aggregate, not the unweighted mean
of the hourly percentages.

The agreement is imposed by calibration. Many temporal allocations share these
summaries. The reconstruction does not identify handover events, individual
losses, or actual peak-hour performance, and does not change the paper's
40.5 ms interruption assumption.
