"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: COUNT-MIN & TCM GRAPH SKETCHES (ALGO-GRAPH-STRM-208)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Count-Min and Topological Count-Min (TCM) sketch streaming graph algorithms.
   Maintains fixed-size 2D hash frequency matrices for estimating edge frequencies
   and vertex incident degrees in high-throughput graph streams with provable (eps, delta) error bounds.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(d) per edge stream update, O(d) per frequency query.
   - Space Complexity: O(w * d) integers, strictly sublinear O(1) w.r.t total stream volume.
   - Purity: Stateful streaming sketch, deterministic hashing, zero side-effects.

3. INPUT PARAMETERS:
   - `width` (int): Number of buckets per hash row (w = ceil(e / epsilon)).
   - `depth` (int): Number of independent hash rows (d = ceil(ln(1 / delta))).
   - `seed` (int): Base random seed for hash salting.

4. OUTPUT PARAMETERS:
   - `estimate_edge_frequency(u, v)` (int): Min-count estimate of edge (u, v) frequency.
   - `estimate_vertex_degree(u)` (int): Aggregate frequency of all edges incident to u.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Conservative upper bound guarantee (estimate >= exact frequency).
================================================================================
"""

import hashlib
import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCountMinTcmGraphSketch(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-STRM-208
      name: GraphAlgoCountMinTcmGraphSketch
      version: 1.0.0
      category: graph_streaming
      capability_tags: [graph, streaming, count_min, tcm_sketch, edge_frequency, degree_estimation]
      inputs:
        type: object
        properties:
          width: {type: integer, minimum: 1}
          depth: {type: integer, minimum: 1}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          edge_frequency: {type: integer}
          vertex_degree: {type: integer}
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

    def __init__(self, width: int = 128, depth: int = 5, seed: int = 42) -> None:
        """
        Initialize Count-Min / TCM 2D sketch matrices.

        Args:
            width: Number of buckets per row.
            depth: Number of hash functions / depth levels.
            seed: Salt base seed.
        """
        self._width: int = max(4, width)
        self._depth: int = max(1, depth)
        self._seed: int = seed
        self._table: List[List[int]] = [[0] * self._width for _ in range(self._depth)]
        self._vertex_table: List[List[int]] = [[0] * self._width for _ in range(self._depth)]
        self._total_updates: int = 0

    def _hash_edge(self, u: TNode, v: TNode, row_idx: int) -> int:
        salt = f"{self._seed}:{row_idx}:{str(u)}->{str(v)}"
        digest = hashlib.md5(salt.encode("utf-8")).hexdigest()
        return int(digest, 16) % self._width

    def _hash_vertex(self, u: TNode, row_idx: int) -> int:
        salt = f"{self._seed}:v:{row_idx}:{str(u)}"
        digest = hashlib.md5(salt.encode("utf-8")).hexdigest()
        return int(digest, 16) % self._width

    def update_edge(self, u: TNode, v: TNode, count: int = 1) -> None:
        """
        Update sketch with an arriving edge stream tuple.

        Args:
            u: Source vertex.
            v: Target vertex.
            count: Frequency increment.
        """
        if count <= 0:
            return
        for r in range(self._depth):
            c = self._hash_edge(u, v, r)
            self._table[r][c] += count
            cu = self._hash_vertex(u, r)
            self._vertex_table[r][cu] += count
        self._total_updates += count

    def estimate_edge_frequency(self, u: TNode, v: TNode) -> int:
        """
        Retrieve conservative point estimate of edge frequency.

        Args:
            u: Source vertex.
            v: Target vertex.

        Returns:
            Minimum frequency across all hash rows.
        """
        min_val = float("inf")
        for r in range(self._depth):
            c = self._hash_edge(u, v, r)
            val = self._table[r][c]
            if val < min_val:
                min_val = val
        return int(min_val) if min_val != float("inf") else 0

    def estimate_vertex_degree(self, u: TNode) -> int:
        """
        Retrieve conservative point estimate of vertex degree.

        Args:
            u: Target vertex.

        Returns:
            Minimum aggregate degree across all hash rows.
        """
        min_val = float("inf")
        for r in range(self._depth):
            c = self._hash_vertex(u, r)
            val = self._vertex_table[r][c]
            if val < min_val:
                min_val = val
        return int(min_val) if min_val != float("inf") else 0

    def get_error_bounds(self) -> Dict[str, float]:
        """
        Compute theoretical (epsilon, delta) error bounds.

        Returns:
            Dictionary containing theoretical epsilon additive error factor and delta confidence.
        """
        epsilon = math.e / self._width
        delta = 1.0 / math.exp(self._depth)
        return {"epsilon": epsilon, "delta": delta, "total_updates": float(self._total_updates)}
