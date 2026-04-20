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

"""Throughput computation utilities for post-hoc QoS analysis.

Maps per-UE SINR values to achievable throughput using Shannon capacity with
a practical NR efficiency factor, consistent with the paper's bandwidth-capacity
constraint model.

References:
    - Shannon bound: C = BW × log₂(1 + SNR)
    - Practical NR efficiency η ≈ 0.65–0.75 accounts for cyclic prefix,
      DMRS, control channels, and other overhead (3GPP TS 38.214)
    - Channel bandwidth: 100 MHz per cell (Table I in the paper)
"""

import numpy as np
from typing import List, Optional


# ---------------------------------------------------------------------------
# Constants (from the paper's Table I and simulation parameters)
# ---------------------------------------------------------------------------
DEFAULT_BANDWIDTH_MHZ = 100     # Channel bandwidth per cell
DEFAULT_EFFICIENCY = 0.70       # Practical NR efficiency factor (η)
N_MIMO_LAYERS = 4               # Number of MIMO spatial streams (n_t from paper)
SINR_FLOOR_DB = -10.0           # Minimum practical SINR
SINR_CAP_DB = 40.0              # Cap to avoid unrealistic throughput
DEMAND_MIN_MBPS = 0.5           # Minimum demanded throughput (paper §Metrics)
DEMAND_MAX_MBPS = 25.0          # Maximum demanded throughput (paper §Metrics)


def sinr_to_throughput(sinr_db: float,
                       bandwidth_mhz: float = DEFAULT_BANDWIDTH_MHZ,
                       efficiency: float = DEFAULT_EFFICIENCY,
                       mimo_layers: int = N_MIMO_LAYERS) -> float:
    """Compute achievable throughput from SINR using Shannon capacity.

    T = n_t × η × BW × log₂(1 + SINR_linear)

    where n_t is the number of MIMO spatial streams (layers).

    Args:
        sinr_db: SINR in dB for the UE–cell link.
        bandwidth_mhz: Channel bandwidth in MHz (default 100 MHz).
        efficiency: Practical efficiency factor η (default 0.70).
        mimo_layers: Number of MIMO spatial streams (default 4, from paper's n_t).

    Returns:
        Achievable throughput in Mbps.
    """
    # Clip SINR to practical range
    sinr_db_clipped = np.clip(sinr_db, SINR_FLOOR_DB, SINR_CAP_DB)
    sinr_linear = 10.0 ** (sinr_db_clipped / 10.0)
    throughput_mbps = mimo_layers * efficiency * bandwidth_mhz * np.log2(1.0 + sinr_linear)
    return float(throughput_mbps)


def sinr_to_spectral_efficiency(sinr_db: float,
                                efficiency: float = DEFAULT_EFFICIENCY) -> float:
    """Compute spectral efficiency from SINR.

    SE = η × log₂(1 + SINR_linear)   [bps/Hz]

    Args:
        sinr_db: SINR in dB.
        efficiency: Practical efficiency factor η.

    Returns:
        Spectral efficiency in bps/Hz.
    """
    sinr_db_clipped = np.clip(sinr_db, SINR_FLOOR_DB, SINR_CAP_DB)
    sinr_linear = 10.0 ** (sinr_db_clipped / 10.0)
    return float(efficiency * np.log2(1.0 + sinr_linear))


def assign_demands(n_ues: int,
                   min_mbps: float = DEMAND_MIN_MBPS,
                   max_mbps: float = DEMAND_MAX_MBPS,
                   seed: Optional[int] = None) -> np.ndarray:
    """Draw per-UE demanded throughput from uniform [min, max].

    Args:
        n_ues: Number of UEs.
        min_mbps: Minimum demand in Mbps.
        max_mbps: Maximum demand in Mbps.
        seed: Random seed for reproducibility.

    Returns:
        Array of demanded throughput values in Mbps, shape (n_ues,).
    """
    rng = np.random.default_rng(seed)
    return rng.uniform(min_mbps, max_mbps, size=n_ues)


def compute_fair_share_throughput(sinr_db_values: List[float],
                                 bandwidth_mhz: float = DEFAULT_BANDWIDTH_MHZ,
                                 efficiency: float = DEFAULT_EFFICIENCY) -> List[float]:
    """Compute per-UE throughput under equal resource sharing within a cell.

    Each UE gets 1/N of the cell's bandwidth, where N is the number of UEs
    sharing the cell.

    T_ue = η × (BW / N) × log₂(1 + SINR_linear)

    Args:
        sinr_db_values: List of SINR values in dB for all UEs on the cell.
        bandwidth_mhz: Total channel bandwidth in MHz.
        efficiency: Practical efficiency factor η.

    Returns:
        List of per-UE throughput values in Mbps.
    """
    n_ues = len(sinr_db_values)
    if n_ues == 0:
        return []

    bw_per_ue = bandwidth_mhz / n_ues
    return [sinr_to_throughput(sinr, bw_per_ue, efficiency)
            for sinr in sinr_db_values]


def compute_cell_throughputs(cell_sinr_map: dict,
                             bandwidth_mhz: float = DEFAULT_BANDWIDTH_MHZ,
                             efficiency: float = DEFAULT_EFFICIENCY) -> dict:
    """Compute fair-share throughput for all UEs grouped by cell.

    Args:
        cell_sinr_map: Dict mapping cell_id -> list of (ue_index, sinr_db).
        bandwidth_mhz: Channel bandwidth in MHz per cell.
        efficiency: Practical efficiency factor η.

    Returns:
        Dict mapping ue_index -> throughput_mbps.
    """
    result = {}
    for cell_id, ue_sinr_list in cell_sinr_map.items():
        n_ues = len(ue_sinr_list)
        if n_ues == 0:
            continue
        bw_per_ue = bandwidth_mhz / n_ues
        for ue_idx, sinr_db in ue_sinr_list:
            result[ue_idx] = sinr_to_throughput(sinr_db, bw_per_ue, efficiency)
    return result
