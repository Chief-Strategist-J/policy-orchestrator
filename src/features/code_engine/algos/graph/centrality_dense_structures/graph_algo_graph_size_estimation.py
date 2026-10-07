"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH SIZE ESTIMATION FROM SAMPLES (ALGO-GRAPH-SAMP-150)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graph population size and edge volume estimator from partial samples using:
   - Birthday Paradox collision counting: N_est ~ k^2 / (2 * collisions).
   - Lincoln-Petersen capture-recapture: N_est ~ (n_1 * n_2) / m_overlap.
   - Chapman bias-corrected capture-recapture.
   Estimates total unseen graph scale in O(sqrt(N)) sample queries.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(sample_size) sample comparison.
   - Space Complexity: O(sample_size) observed sample hashes.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - sample_1: List[TNode] - First independent vertex sample.
   - sample_2: Optional[List[TNode]] - Second independent vertex sample (for capture-recapture).
   - collision_count: Optional[int] - Observed duplicate draws in single-sample birthday stream.

4. OUTPUT PARAMETERS:
   - lincoln_petersen_estimate: Optional[float] - Capture-recapture total population size N.
   - chapman_estimate: Optional[float] - Small-sample bias corrected estimate ((n1+1)(n2+1)/(m+1) - 1).
   - collision_estimate: Optional[float] - Birthday paradox collision estimate.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Independent samples.
   - Guardrails: Avoids division by zero when overlap is 0 by returning conservative lower bounds.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphSizeEstimation(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SAMP-150
      name: GraphAlgoGraphSizeEstimation
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, sampling, size_estimation, capture_recapture, lincoln_petersen, birthday_paradox, collision_counting]
      inputs:
        type: object
        required: [sample_1]
        properties:
          sample_1: {type: array, items: {type: string}}
          sample_2: {type: array, items: {type: string}}
          collision_count: {type: integer}
      outputs:
        type: object
        required: []
        properties:
          lincoln_petersen_estimate: {type: number}
          chapman_estimate: {type: number}
          collision_estimate: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(S)
        space: O(S)
    ---
    """

    def __init__(
        self,
        sample_1: List[TNode],
        sample_2: Optional[List[TNode]] = None,
        collision_count: Optional[int] = None,
    ) -> None:
        """
        Initialize the Graph Size Estimator.

        Args:
            sample_1: First sample list of node identifiers.
            sample_2: Optional second sample for capture-recapture.
            collision_count: Optional collision count observed.
        """
        self._s1: List[TNode] = sample_1
        self._s2: Optional[List[TNode]] = sample_2
        self._collisions: Optional[int] = collision_count

    def estimate_size(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Compute Lincoln-Petersen, Chapman, and Collision-based population size estimates.

        Returns:
            Tuple of (lincoln_petersen_est, chapman_est, collision_est).
        """
        n1 = len(self._s1)
        lp_est: Optional[float] = None
        chapman_est: Optional[float] = None
        collision_est: Optional[float] = None

        if self._s2 is not None:
            n2 = len(self._s2)
            overlap = len(set(self._s1) & set(self._s2))

            if overlap > 0:
                lp_est = float(n1 * n2) / float(overlap)
            else:
                lp_est = float(n1 + n2)

            chapman_est = (float(n1 + 1) * float(n2 + 1) / float(overlap + 1)) - 1.0

        if self._collisions is not None and self._collisions > 0:
            k = float(n1)
            collision_est = (k ** 2) / (2.0 * float(self._collisions))
        elif len(self._s1) > 0:
            unique_count = len(set(self._s1))
            coll = len(self._s1) - unique_count
            if coll > 0:
                k = float(len(self._s1))
                collision_est = (k ** 2) / (2.0 * float(coll))

        return lp_est, chapman_est, collision_est
