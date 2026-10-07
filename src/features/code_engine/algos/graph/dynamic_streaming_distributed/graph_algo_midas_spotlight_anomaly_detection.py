"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STREAMING ANOMALY DETECTION MIDAS/SPOTLIGHT (ALGO-GRAPH-TEMP-215)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Microcluster-based Anomaly Detection in Edge Streams (MIDAS / SpotLight).
   Computes real-time streaming edge anomaly scores using chi-squared / Poisson
   statistical deviation tests against decay-weighted historical frequency sketches.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(d) per edge arrival.
   - Space Complexity: O(w * d) constant bounded memory.
   - Purity: Stateful streaming anomaly scorer.

3. INPUT PARAMETERS:
   - `width` (int): Number of count-min sketch columns.
   - `depth` (int): Number of hash rows.
   - `decay_factor` (float): Factor alpha in (0, 1) for historical temporal decay.

4. OUTPUT PARAMETERS:
   - `score_edge(u, v, timestamp)` (float): Continuous anomaly likelihood score (chi-squared statistic).
   - `is_anomaly(u, v, timestamp, threshold)` (bool): Binary anomaly flag based on threshold.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: High scores indicate sudden sudden bursts or structural microcluster deviations.
================================================================================
"""

import hashlib
import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMidasSpotlightAnomalyDetection(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TEMP-215
      name: GraphAlgoMidasSpotlightAnomalyDetection
      version: 1.0.0
      category: graph_temporal
      capability_tags: [graph, streaming, anomaly_detection, midas, spotlight, edge_bursts]
      inputs:
        type: object
        properties:
          width: {type: integer, minimum: 8}
          depth: {type: integer, minimum: 2}
          decay_factor: {type: number, minimum: 0.1, maximum: 1.0}
      outputs:
        type: object
        properties:
          anomaly_score: {type: number}
          is_anomaly: {type: boolean}
      parameters:
        width: {type: integer}
        depth: {type: integer}
      purity: stateful
      determinism: deterministic
      idempotency: non_idempotent
      complexity:
        time: O(d)
        space: O(w * d)
    ---
    """

    def __init__(self, width: int = 256, depth: int = 4, decay_factor: float = 0.5, seed: int = 42) -> None:
        """
        Initialize MIDAS streaming anomaly detection sketches.

        Args:
            width: Count-Min hash columns.
            depth: Count-Min hash rows.
            decay_factor: Historical decay coefficient alpha.
            seed: Hash randomization seed.
        """
        self._w: int = max(8, width)
        self._d: int = max(1, depth)
        self._decay: float = max(0.01, min(1.0, decay_factor))
        self._seed: int = seed

        self._curr_table: List[List[float]] = [[0.0] * self._w for _ in range(self._d)]
        self._hist_table: List[List[float]] = [[0.0] * self._w for _ in range(self._d)]
        self._last_time: Optional[float] = None

    def _hash(self, u: TNode, v: TNode, row: int) -> int:
        s = f"{self._seed}:{row}:{str(u)}->{str(v)}"
        d = hashlib.md5(s.encode("utf-8")).hexdigest()
        return int(d, 16) % self._w

    def score_edge(self, u: TNode, v: TNode, timestamp: float) -> float:
        """
        Compute anomaly score for edge (u, v) arriving at timestamp and update sketches.

        Args:
            u: Source node.
            v: Target node.
            timestamp: Arrival timestamp.

        Returns:
            Chi-squared anomaly score.
        """
        if self._last_time is not None and timestamp > self._last_time:
            self._advance_time()
        self._last_time = timestamp

        score_components = []
        for r in range(self._d):
            c = self._hash(u, v, r)
            a_curr = self._curr_table[r][c] + 1.0
            s_hist = self._hist_table[r][c]

            if s_hist <= 0.0:
                score = (a_curr ** 2) / 1.0
            else:
                expected = s_hist * self._decay
                score = ((a_curr - expected) ** 2) / (expected + 1e-5)
            score_components.append(score)

        final_score = max(score_components) if score_components else 0.0

        for r in range(self._d):
            c = self._hash(u, v, r)
            self._curr_table[r][c] += 1.0

        return float(final_score)

    def _advance_time(self) -> None:
        for r in range(self._d):
            for c in range(self._w):
                self._hist_table[r][c] = self._hist_table[r][c] * self._decay + self._curr_table[r][c]
                self._curr_table[r][c] = 0.0

    def is_anomaly(self, u: TNode, v: TNode, timestamp: float, threshold: float = 10.0) -> bool:
        """
        Check if edge arrival exceeds anomaly threshold.

        Args:
            u: Source node.
            v: Target node.
            timestamp: Arrival timestamp.
            threshold: Anomaly cutoff threshold.

        Returns:
            Boolean anomaly flag.
        """
        score = self.score_edge(u, v, timestamp)
        return score >= threshold
