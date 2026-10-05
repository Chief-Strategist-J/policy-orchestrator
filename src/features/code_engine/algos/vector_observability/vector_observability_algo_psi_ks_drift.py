"""
================================================================================
ALGORITHM BLUEPRINT: PSI AND KS TESTS ON PROJECTIONS (ALGO-VEC-OBS-170)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Calculates Population Stability Index (PSI) and Kolmogorov-Smirnov (KS) statistic
   on fixed vector projections (e.g. principal axes) to isolate semantic drift.

2. MATHEMATICAL FORMULATION:
   PSI = sum ( (curr% - ref%) * ln(curr% / ref%) )
   KS = max | F_ref(x) - F_curr(x) |
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorObservabilityAlgoPsiKsDrift:
    """
    --- contract:
      id: ALGO-VEC-OBS-170
      name: VectorObservabilityAlgoPsiKsDrift
      category: observability
      complexity: O(N * D + B)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        reference_projections: list[float]
        current_projections: list[float]
        num_bins: int
      output_schema:
        psi_score: float
        ks_statistic: float
        drift_severity: str
        is_actionable_drift: bool
    ---
    """

    @classmethod
    def evaluate(
        cls,
        reference_projections: List[float],
        current_projections: List[float],
        num_bins: int = 10,
    ) -> Dict[str, Any]:
        if not reference_projections or not current_projections or num_bins <= 1:
            return {
                "psi_score": 0.0,
                "ks_statistic": 0.0,
                "drift_severity": "NONE",
                "is_actionable_drift": False,
            }

        ref_sorted = sorted(reference_projections)
        curr_sorted = sorted(current_projections)
        n_ref = len(ref_sorted)
        n_curr = len(curr_sorted)

        min_val = min(ref_sorted[0], curr_sorted[0])
        max_val = max(ref_sorted[-1], curr_sorted[-1])
        if min_val == max_val:
            return {
                "psi_score": 0.0,
                "ks_statistic": 0.0,
                "drift_severity": "NONE",
                "is_actionable_drift": False,
            }

        bin_width = (max_val - min_val) / float(num_bins)
        eps = 1e-4

        ref_counts = [0] * num_bins
        for val in ref_sorted:
            b_idx = min(num_bins - 1, int((val - min_val) / bin_width))
            ref_counts[b_idx] += 1

        curr_counts = [0] * num_bins
        for val in curr_sorted:
            b_idx = min(num_bins - 1, int((val - min_val) / bin_width))
            curr_counts[b_idx] += 1

        psi = 0.0
        for b in range(num_bins):
            p_ref = max(ref_counts[b] / float(n_ref), eps)
            p_curr = max(curr_counts[b] / float(n_curr), eps)
            psi += (p_curr - p_ref) * math.log(p_curr / p_ref)

        all_vals = sorted(list(set(ref_sorted + curr_sorted)))
        ks_stat = 0.0
        idx_r = 0
        idx_c = 0
        for val in all_vals:
            while idx_r < n_ref and ref_sorted[idx_r] <= val:
                idx_r += 1
            while idx_c < n_curr and curr_sorted[idx_c] <= val:
                idx_c += 1
            cdf_r = idx_r / float(n_ref)
            cdf_c = idx_c / float(n_curr)
            diff = abs(cdf_r - cdf_c)
            if diff > ks_stat:
                ks_stat = diff

        severity = "NONE"
        if psi > 0.25 or ks_stat > 0.30:
            severity = "MAJOR"
        elif psi > 0.10 or ks_stat > 0.15:
            severity = "MODERATE"

        return {
            "psi_score": round(psi, 4),
            "ks_statistic": round(ks_stat, 4),
            "drift_severity": severity,
            "is_actionable_drift": severity in ("MODERATE", "MAJOR"),
        }
