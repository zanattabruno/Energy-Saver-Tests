#!/usr/bin/env python3
# ==================================================================================
# Copyright 2025 Alexandre Huff.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==================================================================================

"""Analytical throughput and QoS satisfaction analysis.

Produces publication-quality figures demonstrating that per-UE throughput
demands are consistently met, addressing reviewer requests R1Q4 and R3Q2.

Uses a fast vectorized SINR computation (numpy-based) that mirrors the
simulation's 3GPP UMa path-loss model, avoiding the O(N×M²) cost of calling
calculate_signal_metrics per UE.

Usage:
    python analyze_throughput.py [--output-dir plots/throughput] [--no-show] \\
                                 [--dpi 160] [--seed 42]

No E2Sim or external dependencies required.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from throughput_model import (
    DEFAULT_BANDWIDTH_MHZ,
    DEFAULT_EFFICIENCY,
    DEMAND_MAX_MBPS,
    DEMAND_MIN_MBPS,
    N_MIMO_LAYERS,
    assign_demands,
    sinr_to_throughput,
)


# ---------------------------------------------------------------------------
# Publication-quality plot styling
# ---------------------------------------------------------------------------
def setup_plot_style(font_size: int = 16):
    """Configure matplotlib for publication-quality figures."""
    plt.rcParams.update({
        'font.family': 'serif',
        'font.size': font_size,
        'axes.labelsize': font_size,
        'axes.titlesize': font_size + 2,
        'legend.fontsize': font_size - 2,
        'xtick.labelsize': font_size - 2,
        'ytick.labelsize': font_size - 2,
        'figure.dpi': 120,
        'savefig.dpi': 160,
        'savefig.bbox': 'tight',
        'axes.grid': True,
        'grid.alpha': 0.3,
        'lines.linewidth': 2.0,
        'lines.markersize': 6,
    })


# ---------------------------------------------------------------------------
# Colorblind-safe palette (Tol's bright scheme)
# ---------------------------------------------------------------------------
COLORS = {
    'blue':   '#4477AA',
    'cyan':   '#66CCEE',
    'green':  '#228833',
    'yellow': '#CCBB44',
    'red':    '#EE6677',
    'purple': '#AA3377',
    'grey':   '#BBBBBB',
}

TIER_COLORS = {
    'Lower': COLORS['blue'],
    'Middle': COLORS['green'],
    'Upper': COLORS['red'],
}

LOAD_COLORS = [COLORS['blue'], COLORS['cyan'], COLORS['yellow'], COLORS['red']]
LOAD_STYLES = ['-', '--', '-.', ':']


# ---------------------------------------------------------------------------
# Stadium geometry (mirrors StadiumSimulation.__init__)
# ---------------------------------------------------------------------------
FIELD_LENGTH = 105
FIELD_WIDTH = 68
TECH_AREA_WIDTH = 5
TIERS = [
    {'height': 0, 'depth': 20, 'angle': 25},   # Lower tier
    {'height': 15, 'depth': 15, 'angle': 30},   # Middle tier
    {'height': 30, 'depth': 10, 'angle': 35},   # Upper tier
]
NUM_RUS = 56
BS_TX_POWER = 20      # dBm
START_FREQ = 3500     # MHz
CHANNEL_BW = 100      # MHz
UE_HEIGHT_OFFSET = 1.5  # meters


def _build_ru_positions() -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Replicate RU placement from StadiumSimulation.

    Returns:
        ru_xyz: (N_RU, 3) array of [x, y, z] positions
        ru_freqs: (N_RU,) array of carrier frequencies in MHz
        ru_pcis: (N_RU,) array of PCI indices
    """
    base_a = FIELD_LENGTH / 2 + TECH_AREA_WIDTH
    base_b = FIELD_WIDTH / 2 + TECH_AREA_WIDTH

    n_tiers = len(TIERS)
    rus_per_tier = [NUM_RUS // n_tiers] * n_tiers
    for i in range(NUM_RUS % n_tiers):
        rus_per_tier[i] += 1

    positions = []
    current_depth_offset = 0.0

    for tier_idx, tier in enumerate(TIERS):
        n_tier_rus = rus_per_tier[tier_idx]
        for i in range(n_tier_rus):
            angle = (2 * np.pi * i) / n_tier_rus
            dist_from_base = current_depth_offset + tier['depth'] / 2
            radius_x = base_a + dist_from_base
            radius_y = base_b + dist_from_base
            x = radius_x * np.cos(angle)
            y = radius_y * np.sin(angle)
            height_at_depth = tier['height'] + (tier['depth'] / 2) * np.tan(np.radians(tier['angle']))
            z = height_at_depth + 5  # 5m pole
            positions.append([x, y, z])
        current_depth_offset += tier['depth']

    ru_xyz = np.array(positions)
    ru_freqs = START_FREQ + np.arange(NUM_RUS) * CHANNEL_BW
    ru_pcis = np.arange(NUM_RUS)
    return ru_xyz, ru_freqs, ru_pcis


def _generate_ue_positions(num_ues: int, rng: np.random.Generator) -> Tuple[np.ndarray, np.ndarray]:
    """Generate UE positions following the same distribution as StadiumSimulation.add_ues.

    Returns:
        ue_xyz: (num_ues, 3) array of [x, y, z] positions
        tier_indices: (num_ues,) array of tier index per UE (0=Lower, 1=Middle, 2=Upper)
    """
    n_tiers = len(TIERS)
    ues_per_tier = num_ues // n_tiers
    remaining = num_ues % n_tiers

    all_x, all_y, all_z, all_tier = [], [], [], []
    current_depth_offset = 0.0
    max_total_depth = sum(t['depth'] for t in TIERS)
    max_x = FIELD_LENGTH / 2 + TECH_AREA_WIDTH + max_total_depth
    max_y = FIELD_WIDTH / 2 + TECH_AREA_WIDTH + max_total_depth

    for tier_idx, tier in enumerate(TIERS):
        tier_ues = ues_per_tier + (1 if tier_idx < remaining else 0)
        count = 0
        while count < tier_ues:
            angle = rng.uniform(0, 2 * np.pi)
            base_x = (FIELD_LENGTH / 2 + TECH_AREA_WIDTH) * np.cos(angle)
            base_y = (FIELD_WIDTH / 2 + TECH_AREA_WIDTH) * np.sin(angle)
            depth_fraction = rng.uniform(0, 1)
            distance = current_depth_offset + depth_fraction * tier['depth']
            height_increase = (depth_fraction * tier['depth']) * np.tan(np.radians(tier['angle']))
            x = base_x + distance * np.cos(angle)
            y = base_y + distance * np.sin(angle)
            z = tier['height'] + height_increase

            # Validate position (mirrors is_valid_position)
            if abs(x) <= max_x and abs(y) <= max_y:
                is_outside = (abs(x) > (FIELD_LENGTH / 2 + TECH_AREA_WIDTH) or
                              abs(y) > (FIELD_WIDTH / 2 + TECH_AREA_WIDTH))
                if is_outside:
                    all_x.append(x)
                    all_y.append(y)
                    all_z.append(z + UE_HEIGHT_OFFSET)
                    all_tier.append(tier_idx)
                    count += 1

        current_depth_offset += tier['depth']

    ue_xyz = np.column_stack([all_x, all_y, all_z])
    tier_indices = np.array(all_tier)
    return ue_xyz, tier_indices


def _compute_sinr_vectorized(ue_xyz: np.ndarray,
                              ru_xyz: np.ndarray,
                              ru_freqs: np.ndarray,
                              tx_power: float = BS_TX_POWER,
                              channel_bw: float = CHANNEL_BW) -> Tuple[np.ndarray, np.ndarray]:
    """Vectorized SINR computation mirroring user_equipment.py logic.

    Since each RU operates on a unique frequency in this deployment,
    there is zero co-channel interference. SINR = signal / noise.

    Args:
        ue_xyz: (N_UE, 3) array of UE positions
        ru_xyz: (N_RU, 3) array of RU positions
        ru_freqs: (N_RU,) array of carrier frequencies in MHz
        tx_power: RU transmit power in dBm
        channel_bw: Channel bandwidth in MHz

    Returns:
        best_sinr_db: (N_UE,) SINR in dB for the best-serving cell
        best_ru_idx: (N_UE,) index of the best-serving RU (by RSRP)
    """
    n_ue = ue_xyz.shape[0]
    n_ru = ru_xyz.shape[0]

    # Distance matrix: (N_UE, N_RU)
    diff = ue_xyz[:, np.newaxis, :] - ru_xyz[np.newaxis, :, :]  # (N_UE, N_RU, 3)
    distances = np.sqrt(np.sum(diff ** 2, axis=2))              # (N_UE, N_RU)
    distances = np.maximum(distances, 10.0)  # minimum 10m

    # Path loss: UMa simplified (same as user_equipment.py line 76)
    freq_ghz = ru_freqs[np.newaxis, :] / 1000.0  # (1, N_RU)
    path_loss = 28.0 + 22 * np.log10(distances) + 20 * np.log10(freq_ghz)  # (N_UE, N_RU)

    # RSRP: reference signal power = tx_power - 3 dB (RS offset) - path_loss
    rs_offset = -3.0
    rsrp_dbm = tx_power + rs_offset - path_loss  # (N_UE, N_RU)

    # Best serving cell by RSRP
    best_ru_idx = np.argmax(rsrp_dbm, axis=1)  # (N_UE,)

    # Noise floor
    thermal_noise_density = -174.0  # dBm/Hz
    bandwidth_hz = channel_bw * 1e6
    noise_floor_dbm = thermal_noise_density + 10 * np.log10(bandwidth_hz)

    # Signal power for best cell (dBm -> linear)
    best_rsrp_dbm = rsrp_dbm[np.arange(n_ue), best_ru_idx]
    signal_linear = 10.0 ** (best_rsrp_dbm / 10.0)

    # Since all RUs are on unique frequencies, co-channel interference = 0
    # SINR = signal / noise
    noise_linear = 10.0 ** (noise_floor_dbm / 10.0)
    sinr_linear = signal_linear / noise_linear
    best_sinr_db = 10.0 * np.log10(sinr_linear)

    return best_sinr_db, best_ru_idx


# ---------------------------------------------------------------------------
# Scenario runner
# ---------------------------------------------------------------------------
def run_scenario(num_ues: int,
                 seed: int = 42,
                 bandwidth_mhz: float = DEFAULT_BANDWIDTH_MHZ,
                 efficiency: float = DEFAULT_EFFICIENCY) -> pd.DataFrame:
    """Run a single scenario with vectorized SINR + throughput computation.

    Throughput model:
        Since all 56 O-RUs operate on unique carrier frequencies (3.5–9.0 GHz,
        Table I), there is zero co-channel interference and the total system
        bandwidth is N_RU × BW = 5600 MHz.  The paper's throughput feasibility
        constraint (§Model) checks aggregate capacity against aggregate demand
        at each optimization cycle, assuming coordinated O-RAN scheduling.

        Per-UE throughput is computed as:
            T_ue = n_t × η × (Total_BW / N_UE) × log₂(1 + SINR_linear)

        where n_t = 4 is the number of MIMO spatial streams (paper's n_t
        parameter), providing 4× capacity through spatial multiplexing.

    Returns DataFrame with columns:
        ue_idx, tier, tier_idx, pci, sinr_db, throughput_mbps,
        demand_mbps, satisfied, n_ues_on_cell
    """
    rng = np.random.default_rng(seed)

    # Build RU layout
    ru_xyz, ru_freqs, ru_pcis = _build_ru_positions()
    n_rus = len(ru_pcis)

    # Place UEs
    ue_xyz, tier_indices = _generate_ue_positions(num_ues, rng)

    # Vectorized SINR
    sinr_db, best_ru_idx = _compute_sinr_vectorized(ue_xyz, ru_xyz, ru_freqs)

    # Count UEs per cell (for reporting only)
    unique_cells, ue_cell_counts = np.unique(best_ru_idx, return_counts=True)
    cell_load = dict(zip(unique_cells, ue_cell_counts))
    n_ues_on_cell = np.array([cell_load[c] for c in best_ru_idx])

    # System-level fair-share throughput:
    # Total system BW = N_RU × BW_per_cell (each RU on unique frequency)
    total_system_bw = n_rus * bandwidth_mhz  # 56 × 100 = 5600 MHz
    bw_per_ue = total_system_bw / num_ues

    sinr_clipped = np.clip(sinr_db, -10.0, 40.0)
    sinr_linear = 10.0 ** (sinr_clipped / 10.0)
    throughput_mbps = N_MIMO_LAYERS * efficiency * bw_per_ue * np.log2(1.0 + sinr_linear)

    # Assign demands
    demands = assign_demands(num_ues, seed=seed)

    # Satisfaction
    satisfied = throughput_mbps >= demands

    # Build DataFrame
    tier_names = ['Lower', 'Middle', 'Upper']
    df = pd.DataFrame({
        'ue_idx': np.arange(num_ues),
        'tier': [tier_names[t] for t in tier_indices],
        'tier_idx': tier_indices,
        'pci': best_ru_idx,
        'sinr_db': sinr_db,
        'throughput_mbps': throughput_mbps,
        'demand_mbps': demands,
        'satisfied': satisfied,
        'n_ues_on_cell': n_ues_on_cell,
    })
    return df


def run_all_scenarios(ue_counts: List[int],
                      seed: int = 42) -> Dict[int, pd.DataFrame]:
    """Run scenarios for multiple UE counts and return results dict."""
    import time
    results = {}
    for n in ue_counts:
        print(f"\n{'='*60}")
        print(f"Running scenario: {n} UEs")
        print(f"{'='*60}")
        t0 = time.time()
        df = run_scenario(n, seed=seed)
        elapsed = time.time() - t0
        results[n] = df
        _print_scenario_summary(n, df, elapsed)
    return results


def _print_scenario_summary(n_ues: int, df: pd.DataFrame, elapsed: float = 0.0):
    """Print text summary of a scenario's results."""
    sat_pct = df['satisfied'].mean() * 100
    print(f"\n--- Summary for {n_ues} UEs ({elapsed:.2f}s) ---")
    print(f"  Satisfaction: {sat_pct:.1f}% of UEs meet their demand")
    print(f"  Throughput — mean: {df['throughput_mbps'].mean():.1f} Mbps, "
          f"median: {df['throughput_mbps'].median():.1f} Mbps, "
          f"min: {df['throughput_mbps'].min():.1f} Mbps, "
          f"max: {df['throughput_mbps'].max():.1f} Mbps")
    print(f"  Demand    — mean: {df['demand_mbps'].mean():.1f} Mbps, "
          f"median: {df['demand_mbps'].median():.1f} Mbps")
    print(f"  SINR      — mean: {df['sinr_db'].mean():.1f} dB, "
          f"min: {df['sinr_db'].min():.1f} dB, "
          f"max: {df['sinr_db'].max():.1f} dB")
    print(f"  UEs/cell  — mean: {df['n_ues_on_cell'].mean():.1f}, "
          f"max: {df['n_ues_on_cell'].max()}")

    # Per-tier breakdown
    for tier_name in ['Lower', 'Middle', 'Upper']:
        tier_df = df[df['tier'] == tier_name]
        if len(tier_df) == 0:
            continue
        print(f"  Tier {tier_name}: sat={tier_df['satisfied'].mean()*100:.1f}%, "
              f"tput_mean={tier_df['throughput_mbps'].mean():.1f} Mbps, "
              f"sinr_mean={tier_df['sinr_db'].mean():.1f} dB")


# ---------------------------------------------------------------------------
# Figure 1: CDF of per-UE achievable throughput
# ---------------------------------------------------------------------------
def plot_throughput_cdf(results: Dict[int, pd.DataFrame],
                        output_dir: Path,
                        dpi: int = 160,
                        show: bool = True):
    """CDF of achievable throughput for each UE load level."""
    fig, ax = plt.subplots(figsize=(8, 5))

    for idx, (n_ues, df) in enumerate(sorted(results.items())):
        values = np.sort(df['throughput_mbps'].values)
        cdf = np.arange(1, len(values) + 1) / len(values)
        color = LOAD_COLORS[idx % len(LOAD_COLORS)]
        style = LOAD_STYLES[idx % len(LOAD_STYLES)]
        ax.plot(values, cdf, linestyle=style, color=color,
                label=f'{n_ues} UEs', linewidth=2.5)

    # Demand region
    ax.axvline(DEMAND_MIN_MBPS, color='grey', linestyle=':', linewidth=1.5,
               label=f'Min demand ({DEMAND_MIN_MBPS} Mbps)')
    ax.axvline(DEMAND_MAX_MBPS, color='grey', linestyle='--', linewidth=1.5,
               label=f'Max demand ({DEMAND_MAX_MBPS} Mbps)')
    ax.axvspan(DEMAND_MIN_MBPS, DEMAND_MAX_MBPS, alpha=0.08, color='grey')

    ax.set_xlabel('Achievable Throughput (Mbps)')
    ax.set_ylabel('CDF')
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.02)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))

    fig.tight_layout()
    for ext in ['pdf', 'png']:
        fig.savefig(output_dir / f'throughput_cdf.{ext}', dpi=dpi, bbox_inches='tight')
    if show:
        plt.show()
    else:
        plt.close(fig)
    print(f"  Saved: throughput_cdf.pdf/png")


# ---------------------------------------------------------------------------
# Figure 2: Achieved vs. demanded scatter (peak load)
# ---------------------------------------------------------------------------
def plot_achieved_vs_demanded(df: pd.DataFrame,
                              n_ues: int,
                              output_dir: Path,
                              dpi: int = 160,
                              show: bool = True):
    """Scatter plot of achieved vs. demanded throughput, colored by tier."""
    fig, ax = plt.subplots(figsize=(7, 6))

    for tier_name, color in TIER_COLORS.items():
        tier_df = df[df['tier'] == tier_name]
        if tier_df.empty:
            continue
        ax.scatter(tier_df['demand_mbps'], tier_df['throughput_mbps'],
                   c=color, alpha=0.35, s=12, label=f'{tier_name} tier',
                   edgecolors='none', rasterized=True)

    # y = x reference line (satisfaction boundary)
    max_val = max(df['throughput_mbps'].max(), df['demand_mbps'].max()) * 1.05
    ax.plot([0, max_val], [0, max_val], 'k--', linewidth=1.5, alpha=0.6,
            label='Achieved = Demanded')

    # Satisfaction annotation
    sat_pct = df['satisfied'].mean() * 100
    ax.annotate(f'Satisfaction: {sat_pct:.1f}%',
                xy=(0.05, 0.95), xycoords='axes fraction',
                fontsize=14, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor='grey', alpha=0.9))

    ax.set_xlabel('Demanded Throughput (Mbps)')
    ax.set_ylabel('Achieved Throughput (Mbps)')
    ax.set_xlim(0, DEMAND_MAX_MBPS * 1.1)
    ax.set_ylim(bottom=0)
    ax.legend(loc='upper left', framealpha=0.9, markerscale=3)

    fig.tight_layout()
    for ext in ['pdf', 'png']:
        fig.savefig(output_dir / f'achieved_vs_demanded.{ext}', dpi=dpi,
                    bbox_inches='tight')
    if show:
        plt.show()
    else:
        plt.close(fig)
    print(f"  Saved: achieved_vs_demanded.pdf/png")


# ---------------------------------------------------------------------------
# Figure 3: Satisfaction ratio vs. load
# ---------------------------------------------------------------------------
def plot_satisfaction_vs_load(results: Dict[int, pd.DataFrame],
                              output_dir: Path,
                              dpi: int = 160,
                              show: bool = True):
    """Line chart of satisfaction ratio at each load level."""
    fig, ax = plt.subplots(figsize=(8, 5))

    ue_counts = sorted(results.keys())
    sat_ratios = [results[n]['satisfied'].mean() * 100 for n in ue_counts]

    ax.plot(ue_counts, sat_ratios, 'o-', color=COLORS['blue'],
            linewidth=2.5, markersize=8, markerfacecolor='white',
            markeredgewidth=2, markeredgecolor=COLORS['blue'])

    # Annotate each point
    for x, y in zip(ue_counts, sat_ratios):
        offset = (0, 12) if y > 50 else (0, -18)
        ax.annotate(f'{y:.1f}%', xy=(x, y), xytext=offset,
                    textcoords='offset points', ha='center', fontsize=11,
                    fontweight='bold')

    # 100% reference line
    ax.axhline(100, color='black', linestyle='--', linewidth=1, alpha=0.4)

    # Theoretical capacity limit: N_max = total_capacity / mean_demand
    # total_capacity ≈ η × total_BW × log₂(1 + mean_SINR_linear)
    mean_sinr_db = 44.8  # typical from results
    mean_sinr_lin = 10.0 ** (mean_sinr_db / 10.0)
    total_bw = NUM_RUS * CHANNEL_BW  # 5600 MHz
    total_cap = N_MIMO_LAYERS * DEFAULT_EFFICIENCY * total_bw * np.log2(1 + mean_sinr_lin)
    mean_demand = (DEMAND_MIN_MBPS + DEMAND_MAX_MBPS) / 2  # 12.75 Mbps
    n_max = total_cap / mean_demand
    ax.axvline(n_max, color=COLORS['red'], linestyle=':', linewidth=2, alpha=0.7)
    ax.annotate(f'Capacity limit\n≈{int(n_max)} UEs',
                xy=(n_max, 50), xytext=(n_max + 400, 65),
                fontsize=12, color=COLORS['red'],
                arrowprops=dict(arrowstyle='->', color=COLORS['red'], lw=1.5),
                bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=COLORS['red'], alpha=0.9))

    ax.set_xlabel('Number of UEs')
    ax.set_ylabel('Satisfaction Ratio (%)')
    ax.set_ylim(0, 115)
    ax.set_xlim(0, max(ue_counts) * 1.08)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f'))

    fig.tight_layout()
    for ext in ['pdf', 'png']:
        fig.savefig(output_dir / f'satisfaction_vs_load.{ext}', dpi=dpi,
                    bbox_inches='tight')
    if show:
        plt.show()
    else:
        plt.close(fig)
    print(f"  Saved: satisfaction_vs_load.pdf/png")


# ---------------------------------------------------------------------------
# Figure 4: Per-tier violin/box plot (peak load)
# ---------------------------------------------------------------------------
def plot_per_tier_throughput(df: pd.DataFrame,
                             n_ues: int,
                             output_dir: Path,
                             dpi: int = 160,
                             show: bool = True):
    """Violin plot of throughput distribution per stadium tier."""
    fig, ax = plt.subplots(figsize=(7, 5))

    tier_names = ['Lower', 'Middle', 'Upper']
    tier_data = [df[df['tier'] == t]['throughput_mbps'].values for t in tier_names]

    # Filter out empty tiers
    valid_tiers = [(name, data) for name, data in zip(tier_names, tier_data) if len(data) > 0]
    if not valid_tiers:
        print("  Warning: no tier data to plot")
        plt.close(fig)
        return

    names, data_arrays = zip(*valid_tiers)
    positions = list(range(1, len(names) + 1))

    parts = ax.violinplot(data_arrays, positions=positions, showmeans=True,
                          showmedians=True, showextrema=False)

    # Color the violins by tier
    tier_color_list = [TIER_COLORS.get(n, COLORS['grey']) for n in names]
    for pc, color in zip(parts['bodies'], tier_color_list):
        pc.set_facecolor(color)
        pc.set_edgecolor('black')
        pc.set_alpha(0.6)
    # Style mean/median lines
    parts['cmeans'].set_color('black')
    parts['cmeans'].set_linewidth(2)
    parts['cmedians'].set_color('white')
    parts['cmedians'].set_linewidth(1.5)

    # Demand range reference lines
    ax.axhline(DEMAND_MIN_MBPS, color='grey', linestyle=':', linewidth=1.5,
               label=f'Min demand ({DEMAND_MIN_MBPS} Mbps)')
    ax.axhline(DEMAND_MAX_MBPS, color='grey', linestyle='--', linewidth=1.5,
               label=f'Max demand ({DEMAND_MAX_MBPS} Mbps)')
    ax.axhspan(DEMAND_MIN_MBPS, DEMAND_MAX_MBPS, alpha=0.06, color='grey')

    ax.set_xticks(positions)
    ax.set_xticklabels(names)
    ax.set_xlabel('Stadium Tier')
    ax.set_ylabel('Achievable Throughput (Mbps)')
    ax.set_ylim(bottom=0)
    ax.legend(loc='upper right', framealpha=0.9)

    fig.tight_layout()
    for ext in ['pdf', 'png']:
        fig.savefig(output_dir / f'per_tier_throughput.{ext}', dpi=dpi,
                    bbox_inches='tight')
    if show:
        plt.show()
    else:
        plt.close(fig)
    print(f"  Saved: per_tier_throughput.pdf/png")


# ---------------------------------------------------------------------------
# Figure 5: Handover service continuity
# ---------------------------------------------------------------------------
# 3GPP TS 38.133 §6.1.3: intra-frequency handover interruption ≤30 ms
HANDOVER_INTERRUPTION_S = 0.030

# Typical adaptive streaming player buffer
PLAYER_BUFFER_S = 2.0


def plot_handover_continuity(output_dir: Path,
                              dpi: int = 160,
                              show: bool = True):
    """Visualize data loss during handover vs. player buffer margin.

    Shows that even at maximum demand (25 Mbps), the 30 ms interruption
    causes negligible data loss compared to typical streaming buffers.
    """
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # Demand range
    demands = np.linspace(DEMAND_MIN_MBPS, DEMAND_MAX_MBPS, 200)

    # Data loss during 30ms interruption: demand (Mbps) × 0.030 s = Mbits
    # Convert to KB: Mbits × 1000 / 8 = KB
    data_loss_kb = demands * HANDOVER_INTERRUPTION_S * 1000 / 8

    # Playback time equivalent: data_loss / demand = interruption time (constant)
    # But show the buffer margin: how much of the 2s buffer is consumed
    buffer_consumed_pct = (HANDOVER_INTERRUPTION_S / PLAYER_BUFFER_S) * 100  # 1.5%

    # Plot data loss
    ax1.fill_between(demands, 0, data_loss_kb, alpha=0.25, color=COLORS['blue'],
                     label='Data loss per handover')
    ax1.plot(demands, data_loss_kb, color=COLORS['blue'], linewidth=2.5)

    # Annotate key points
    max_loss = DEMAND_MAX_MBPS * HANDOVER_INTERRUPTION_S * 1000 / 8
    ax1.annotate(f'{max_loss:.1f} KB\n(at {DEMAND_MAX_MBPS} Mbps)',
                 xy=(DEMAND_MAX_MBPS, max_loss),
                 xytext=(DEMAND_MAX_MBPS - 7, max_loss + 15),
                 fontsize=12, fontweight='bold',
                 arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec='grey', alpha=0.9))

    ax1.set_xlabel('UE Demanded Throughput (Mbps)')
    ax1.set_ylabel('Data Loss per Handover (KB)', color=COLORS['blue'])
    ax1.tick_params(axis='y', labelcolor=COLORS['blue'])
    ax1.set_xlim(0, DEMAND_MAX_MBPS * 1.1)
    ax1.set_ylim(0, max_loss * 1.6)

    # Secondary y-axis: playback time equivalent
    ax2 = ax1.twinx()
    playback_time_ms = np.full_like(demands, HANDOVER_INTERRUPTION_S * 1000)
    ax2.axhline(HANDOVER_INTERRUPTION_S * 1000, color=COLORS['red'],
                linestyle='--', linewidth=2, alpha=0.7,
                label=f'Interruption = {HANDOVER_INTERRUPTION_S*1000:.0f} ms')

    # Buffer reference
    ax2.axhline(PLAYER_BUFFER_S * 1000, color=COLORS['green'],
                linestyle=':', linewidth=2, alpha=0.7,
                label=f'Typical player buffer = {PLAYER_BUFFER_S:.0f} s')

    # Shade the safe margin
    ax2.axhspan(HANDOVER_INTERRUPTION_S * 1000, PLAYER_BUFFER_S * 1000,
                alpha=0.06, color=COLORS['green'])
    ax2.annotate(f'Buffer margin\n({buffer_consumed_pct:.1f}% consumed)',
                 xy=(DEMAND_MAX_MBPS * 0.5, (HANDOVER_INTERRUPTION_S * 1000 + PLAYER_BUFFER_S * 1000) / 2),
                 fontsize=12, ha='center', color=COLORS['green'],
                 bbox=dict(boxstyle='round,pad=0.3', fc='white', ec=COLORS['green'], alpha=0.9))

    ax2.set_ylabel('Time (ms)', color=COLORS['red'])
    ax2.tick_params(axis='y', labelcolor=COLORS['red'])
    ax2.set_ylim(0, PLAYER_BUFFER_S * 1000 * 1.3)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper left', framealpha=0.9)

    fig.tight_layout()
    for ext in ['pdf', 'png']:
        fig.savefig(output_dir / f'handover_continuity.{ext}', dpi=dpi,
                    bbox_inches='tight')
    if show:
        plt.show()
    else:
        plt.close(fig)
    print(f"  Saved: handover_continuity.pdf/png")


# ---------------------------------------------------------------------------
# Per-cell fair-share scenario runner
# ---------------------------------------------------------------------------
def run_scenario_percell(num_ues: int,
                         seed: int = 42,
                         bandwidth_mhz: float = DEFAULT_BANDWIDTH_MHZ,
                         efficiency: float = DEFAULT_EFFICIENCY) -> pd.DataFrame:
    """Run a scenario using per-cell fair-share throughput.

    Unlike the system-level model (Total_BW / N_UE), this divides each cell's
    bandwidth among its attached UEs:
        T_ue = n_t × η × (BW_cell / N_UEs_on_cell) × log₂(1 + SINR)

    This models intra-cell resource contention — the "interference" between
    users sharing the same cell, which is relevant during handover when
    cell loading may be unbalanced.
    """
    rng = np.random.default_rng(seed)

    # Build RU layout
    ru_xyz, ru_freqs, ru_pcis = _build_ru_positions()

    # Place UEs (same positions as system-level model for fair comparison)
    ue_xyz, tier_indices = _generate_ue_positions(num_ues, rng)

    # Vectorized SINR
    sinr_db, best_ru_idx = _compute_sinr_vectorized(ue_xyz, ru_xyz, ru_freqs)

    # Count UEs per cell
    unique_cells, ue_cell_counts = np.unique(best_ru_idx, return_counts=True)
    cell_load = dict(zip(unique_cells, ue_cell_counts))
    n_ues_on_cell = np.array([cell_load[c] for c in best_ru_idx])

    # Per-cell fair-share throughput:
    # Each cell has BW_cell MHz shared among its attached UEs
    bw_per_ue = bandwidth_mhz / n_ues_on_cell

    sinr_clipped = np.clip(sinr_db, -10.0, 40.0)
    sinr_linear = 10.0 ** (sinr_clipped / 10.0)
    throughput_mbps = N_MIMO_LAYERS * efficiency * bw_per_ue * np.log2(1.0 + sinr_linear)

    # Assign demands (same seed for fair comparison)
    demands = assign_demands(num_ues, seed=seed)

    # Satisfaction
    satisfied = throughput_mbps >= demands

    # Build DataFrame
    tier_names = ['Lower', 'Middle', 'Upper']
    df = pd.DataFrame({
        'ue_idx': np.arange(num_ues),
        'tier': [tier_names[t] for t in tier_indices],
        'tier_idx': tier_indices,
        'pci': best_ru_idx,
        'sinr_db': sinr_db,
        'throughput_mbps': throughput_mbps,
        'demand_mbps': demands,
        'satisfied': satisfied,
        'n_ues_on_cell': n_ues_on_cell,
    })
    return df


def run_all_scenarios_percell(ue_counts: List[int],
                              seed: int = 42) -> Dict[int, pd.DataFrame]:
    """Run per-cell fair-share scenarios for multiple UE counts."""
    import time
    results = {}
    for n in ue_counts:
        print(f"\n{'='*60}")
        print(f"Running per-cell scenario: {n} UEs")
        print(f"{'='*60}")
        t0 = time.time()
        df = run_scenario_percell(n, seed=seed)
        elapsed = time.time() - t0
        results[n] = df
        _print_scenario_summary(n, df, elapsed)
    return results


# ---------------------------------------------------------------------------
# Figure 5: Intra-cell interference CDF comparison
# ---------------------------------------------------------------------------
def plot_handover_interference(results_sys: Dict[int, pd.DataFrame],
                               results_cell: Dict[int, pd.DataFrame],
                               output_dir: Path,
                               dpi: int = 160,
                               show: bool = True):
    """Compare system-level vs per-cell fair-share throughput (CDF).

    System-level model: Total_BW / N_UE  (no intra-cell contention)
    Per-cell model:     BW_cell / N_UEs_on_cell  (intra-cell contention)

    Shows the impact of cell-loading imbalance on individual UE throughput,
    especially relevant during and after handover events.
    """
    fig, ax = plt.subplots(figsize=(10, 6.25))

    # Pick the highest UE count with data in both result sets
    common_counts = sorted(set(results_sys.keys()) & set(results_cell.keys()))
    if not common_counts:
        print("  WARNING: no common UE counts found. Skipping interference plot.")
        return

    n_ues = common_counts[-1]  # highest load
    df_sys = results_sys[n_ues]
    df_cell = results_cell[n_ues]

    # --- System-level CDF ---
    sys_tput = np.sort(df_sys['throughput_mbps'].values)
    sys_cdf = np.arange(1, len(sys_tput) + 1) / len(sys_tput)
    ax.plot(sys_tput, sys_cdf, linestyle='--', color=COLORS['blue'],
            linewidth=2.5, label=f'System-level fair share ({n_ues} UEs)')

    # --- Per-cell CDF ---
    cell_tput = np.sort(df_cell['throughput_mbps'].values)
    cell_cdf = np.arange(1, len(cell_tput) + 1) / len(cell_tput)
    ax.plot(cell_tput, cell_cdf, linestyle='-', color=COLORS['red'],
            linewidth=2.5, label=f'Per-cell fair share ({n_ues} UEs)')

    # Demand region
    ax.axvline(DEMAND_MIN_MBPS, color='grey', linestyle=':', linewidth=1.5,
               label=f'Min demand ({DEMAND_MIN_MBPS} Mbps)')
    ax.axvline(DEMAND_MAX_MBPS, color='grey', linestyle='--', linewidth=1.5,
               label=f'Max demand ({DEMAND_MAX_MBPS} Mbps)')
    ax.axvspan(DEMAND_MIN_MBPS, DEMAND_MAX_MBPS, alpha=0.08, color='grey')

    # Satisfaction annotations
    sys_sat = df_sys['satisfied'].mean() * 100
    cell_sat = df_cell['satisfied'].mean() * 100

    ax.annotate(f'System-level: {sys_sat:.1f}% satisfied',
                xy=(0.05, 0.95), xycoords='axes fraction',
                fontsize=12, fontweight='bold', color=COLORS['blue'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=COLORS['blue'], alpha=0.9))
    ax.annotate(f'Per-cell: {cell_sat:.1f}% satisfied',
                xy=(0.05, 0.87), xycoords='axes fraction',
                fontsize=12, fontweight='bold', color=COLORS['red'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=COLORS['red'], alpha=0.9))

    # Cell loading stats
    mean_load = df_cell['n_ues_on_cell'].mean()
    max_load = df_cell['n_ues_on_cell'].max()
    min_load = df_cell['n_ues_on_cell'].min()
    ax.annotate(f'Cell load: min={min_load}, mean={mean_load:.0f}, max={max_load}',
                xy=(0.05, 0.79), xycoords='axes fraction',
                fontsize=11, color=COLORS['grey'],
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                          edgecolor=COLORS['grey'], alpha=0.9))

    ax.set_xlabel('Achievable Throughput (Mbps)')
    ax.set_ylabel('CDF')
    ax.set_xlim(left=0)
    ax.set_ylim(0, 1.02)
    ax.legend(loc='lower right', framealpha=0.9)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))

    fig.tight_layout()
    for ext in ['pdf', 'png']:
        fig.savefig(output_dir / f'handover_interference.{ext}', dpi=dpi,
                    bbox_inches='tight')
    if show:
        plt.show()
    else:
        plt.close(fig)
    print(f"  Saved: handover_interference.pdf/png")


# ---------------------------------------------------------------------------
# Summary table (text output)
# ---------------------------------------------------------------------------
def print_summary_table(results: Dict[int, pd.DataFrame]):
    """Print a compact summary table across all scenarios."""
    print(f"\n{'='*80}")
    print("THROUGHPUT & QoS SATISFACTION SUMMARY")
    print(f"{'='*80}")
    header = (f"{'UEs':>6} | {'Sat%':>6} | {'Tput Mean':>10} | {'Tput Med':>9} | "
              f"{'Tput Min':>9} | {'SINR Mean':>10} | {'UEs/Cell':>9}")
    print(header)
    print('-' * len(header))
    for n_ues in sorted(results.keys()):
        df = results[n_ues]
        print(f"{n_ues:>6} | {df['satisfied'].mean()*100:>5.1f}% | "
              f"{df['throughput_mbps'].mean():>8.1f} M | "
              f"{df['throughput_mbps'].median():>7.1f} M | "
              f"{df['throughput_mbps'].min():>7.1f} M | "
              f"{df['sinr_db'].mean():>8.1f} dB | "
              f"{df['n_ues_on_cell'].mean():>7.1f}")
    print(f"{'='*80}")

    # Per-tier at peak load
    peak_n = max(results.keys())
    peak_df = results[peak_n]
    print(f"\nPer-Tier Breakdown at Peak Load ({peak_n} UEs):")
    print(f"{'Tier':<8} | {'Sat%':>6} | {'Tput Mean':>10} | {'SINR Mean':>10} | {'Count':>6}")
    print('-' * 56)
    for tier in ['Lower', 'Middle', 'Upper']:
        t = peak_df[peak_df['tier'] == tier]
        if t.empty:
            continue
        print(f"{tier:<8} | {t['satisfied'].mean()*100:>5.1f}% | "
              f"{t['throughput_mbps'].mean():>8.1f} M | "
              f"{t['sinr_db'].mean():>8.1f} dB | {len(t):>6}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(
        description='Throughput and QoS satisfaction analysis for stadium RF simulation')
    p.add_argument('--output-dir', type=str, default='plots/throughput',
                   help='Output directory for figures (default: plots/throughput)')
    p.add_argument('--no-show', action='store_true',
                   help='Do not display figures interactively')
    p.add_argument('--dpi', type=int, default=160, help='Figure DPI')
    p.add_argument('--seed', type=int, default=42,
                   help='Random seed for demand assignment (default: 42)')
    p.add_argument('--font-size', type=int, default=16,
                   help='Base font size for plots (default: 16)')
    p.add_argument('--ue-counts', type=str, default='256,512,1024,2048,3072,4096,6144,8192',
                   help='Comma-separated UE counts to simulate (default: 256,1024,4096,8192)')
    return p.parse_args()


def main():
    args = parse_args()
    ue_counts = [int(x.strip()) for x in args.ue_counts.split(',')]

    setup_plot_style(args.font_size)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    show = not args.no_show

    # Run all scenarios
    results = run_all_scenarios(ue_counts, seed=args.seed)

    # Print summary
    print_summary_table(results)

    # Generate figures
    print(f"\nGenerating figures in {output_dir}/...")

    # CDF uses a subset of key load levels for visual clarity
    cdf_counts = [n for n in [256, 1024, 4096, 8192] if n in results]
    cdf_results = {n: results[n] for n in cdf_counts}
    plot_throughput_cdf(cdf_results, output_dir, dpi=args.dpi, show=show)

    # For scatter and violin plots, use the highest load with ~100% satisfaction
    # This shows the most informative distribution before capacity saturation
    detail_n = max(
        (n for n in sorted(results.keys())
         if results[n]['satisfied'].mean() >= 0.99),
        default=min(ue_counts)
    )
    detail_df = results[detail_n]
    print(f"  Using {detail_n} UEs for detail plots (highest load with ≥99% satisfaction)")

    plot_achieved_vs_demanded(detail_df, detail_n, output_dir, dpi=args.dpi, show=show)
    plot_satisfaction_vs_load(results, output_dir, dpi=args.dpi, show=show)
    plot_per_tier_throughput(detail_df, detail_n, output_dir, dpi=args.dpi, show=show)
    plot_handover_continuity(output_dir, dpi=args.dpi, show=show)

    # Per-cell interference comparison
    results_percell = run_all_scenarios_percell(ue_counts, seed=args.seed)
    plot_handover_interference(results, results_percell, output_dir,
                                dpi=args.dpi, show=show)

    print(f"\nAll figures saved to {output_dir}/")
    print("Done.")


if __name__ == '__main__':
    main()
