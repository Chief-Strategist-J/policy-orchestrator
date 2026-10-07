"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: POWER LAW DEGREE FIT (ALGO-GRAPH-NET-135)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Clauset-Shalizi-Newman maximum likelihood power law distribution fitting.
   Rigorously fits P(x) ~ x^(-alpha) for heavy-tailed degree sequences.
   Estimates optimal lower cutoff x_min by minimizing the Kolmogorov-Smirnov (KS)
   distance between empirical and continuous power law cumulative distribution functions.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(N log N) sorted degree MLE grid search.
   - Space Complexity: O(N) degree vector.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - degrees: List[int] - Observed degree sequence of the network.

4. OUTPUT PARAMETERS:
   - alpha: float - Maximum likelihood power-law scaling exponent.
   - x_min: int - Optimal minimum degree cutoff threshold.
   - ks_distance: float - Kolmogorov-Smirnov goodness-of-fit test statistic.
   - tail_fraction: float - Fraction of vertices with degree >= x_min.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Positive degree values.
   - Guardrails: Standard MLE formula alpha = 1 + n * (sum ln(x / (x_min - 0.5)))^(-1).
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPowerLawFit(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-135
      name: GraphAlgoPowerLawFit
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, power_law, clauset_shalizi_newman, mle_estimation, heavy_tails]
      inputs:
        type: object
        required: [degrees]
        properties:
          degrees:
            type: array
            items: {type: integer}
      outputs:
        type: object
        required: [alpha, x_min, ks_distance, tail_fraction]
        properties:
          alpha: {type: number}
          x_min: {type: integer}
          ks_distance: {type: number}
          tail_fraction: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(N log N)
        space: O(N)
    ---
    """

    def __init__(self, degrees: List[int]) -> None:
        """
        Initialize the Power Law Fit estimator.

        Args:
            degrees: List of vertex degrees.
        """
        self._degrees: List[int] = sorted([d for d in degrees if d > 0])

    def fit_power_law(self) -> Tuple[float, int, float, float]:
        """
        Fit power law scaling exponent alpha and cutoff x_min via Kolmogorov-Smirnov minimization.

        Returns:
            Tuple of (alpha_exponent, optimal_x_min, min_ks_distance, tail_fraction).
        """
        if not self._degrees:
            return 1.0, 1, 1.0, 0.0

        n_total = len(self._degrees)
        unique_cutoffs = sorted(list(set(self._degrees)))
        best_alpha: float = 2.5
        best_xmin: int = unique_cutoffs[0]
        min_ks: float = float("inf")

        for xmin in unique_cutoffs:
            tail = [x for x in self._degrees if x >= xmin]
            n_tail = len(tail)
            if n_tail < 5:
                break

            sum_log = sum(math.log(float(x) / (float(xmin) - 0.5)) for x in tail)
            if sum_log <= 0:
                continue

            alpha = 1.0 + float(n_tail) / sum_log
            if alpha <= 1.0 or alpha > 5.0:
                continue

            ks: float = 0.0
            for i, x in enumerate(tail):
                emp_cdf = float(i + 1) / float(n_tail)
                theo_cdf = 1.0 - ((float(xmin) / float(x)) ** (alpha - 1.0))
                diff = abs(emp_cdf - theo_cdf)
                if diff > ks:
                    ks = diff

            if ks < min_ks:
                min_ks = ks
                best_alpha = alpha
                best_xmin = xmin

        tail_count = sum(1 for x in self._degrees if x >= best_xmin)
        tail_fraction = float(tail_count) / float(n_total)

        return best_alpha, best_xmin, min_ks, tail_fraction
