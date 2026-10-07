"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PER-VERTEX HYPERLOGLOG (ALGO-GRAPH-STRM-209)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Distinct-Neighbor Counting via Per-Vertex HyperLogLog (HLL) sketches.
   Maintains compact, logarithmic-register sketches per node to accurately estimate
   the number of distinct streaming out-neighbors / contacts under continuous edge arrival.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) per edge update, O(m) per cardinality query where m is register count.
   - Space Complexity: O(m) bytes per vertex (e.g. 64 bytes for m=64).
   - Purity: Stateful streaming sketch, deterministic, mergeable via register-wise max.

3. INPUT PARAMETERS:
   - `precision` (int): Number of register index bits (p in 4..16, m = 2^p registers).
   - `seed` (int): Hash randomization seed.

4. OUTPUT PARAMETERS:
   - `add_edge(u, v)` (None): Updates u's HLL sketch with neighbor v.
   - `estimate_distinct_neighbors(u)` (float): Flajolet-Martin / HLL harmonic mean estimate.
   - `merge_vertices(u_target, u_source)` (None): Register-wise maximum union.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Standard error bounded by 1.04 / sqrt(m).
================================================================================
"""

import hashlib
import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDistinctNeighborHyperloglog(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-STRM-209
      name: GraphAlgoDistinctNeighborHyperloglog
      version: 1.0.0
      category: graph_streaming
      capability_tags: [graph, streaming, hyperloglog, distinct_counting, degree_sketch, fan_out]
      inputs:
        type: object
        properties:
          precision: {type: integer, minimum: 4, maximum: 16}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          distinct_neighbors: {type: number}
      parameters:
        precision: {type: integer}
      purity: stateful
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(1) update, O(m) query
        space: O(|V| * 2^p)
    ---
    """

    def __init__(self, precision: int = 6, seed: int = 42) -> None:
        """
        Initialize per-vertex HyperLogLog manager.

        Args:
            precision: Bit precision p, determining m = 2^p registers per vertex.
            seed: Hash randomization seed.
        """
        self._p: int = max(4, min(16, precision))
        self._m: int = 1 << self._p
        self._seed: int = seed
        self._alpha: float = self._get_alpha(self._m)
        self._registers: Dict[TNode, List[int]] = {}

    def _get_alpha(self, m: int) -> float:
        if m == 16:
            return 0.673
        if m == 32:
            return 0.697
        if m == 64:
            return 0.709
        return 0.7213 / (1.0 + 1.079 / m)

    def _hash_value(self, item: Hashable) -> int:
        salt = f"{self._seed}:{str(item)}"
        digest = hashlib.sha256(salt.encode("utf-8")).hexdigest()
        return int(digest, 16) & 0xFFFFFFFFFFFFFFFF

    def _clz(self, val: int, bits: int = 64) -> int:
        if val == 0:
            return bits
        return bits - val.bit_length()

    def add_edge(self, u: TNode, v: TNode, undirected: bool = False) -> None:
        """
        Add edge (u, v) into node sketches.

        Args:
            u: Source vertex.
            v: Target neighbor.
            undirected: If True, also adds u into v's sketch.
        """
        self._add_neighbor(u, v)
        if undirected:
            self._add_neighbor(v, u)

    def _add_neighbor(self, u: TNode, v: TNode) -> None:
        if u not in self._registers:
            self._registers[u] = [0] * self._m
        x = self._hash_value(v)
        j = x >> (64 - self._p)
        remaining_bits = 64 - self._p
        w = x & ((1 << remaining_bits) - 1)
        if w == 0:
            leading_zeros = remaining_bits + 1
        else:
            leading_zeros = remaining_bits - w.bit_length() + 1
        if leading_zeros > self._registers[u][j]:
            self._registers[u][j] = leading_zeros

    def estimate_distinct_neighbors(self, u: TNode) -> float:
        """
        Estimate the count of distinct neighbors for vertex u.

        Args:
            u: Target vertex.

        Returns:
            Estimated distinct cardinality.
        """
        if u not in self._registers:
            return 0.0
        regs = self._registers[u]
        z = sum(2.0 ** (-val) for val in regs)
        raw_est = self._alpha * (self._m ** 2) / z
        if raw_est <= 2.5 * self._m:
            zeros = regs.count(0)
            if zeros != 0:
                return float(self._m * math.log(self._m / zeros))
            return float(raw_est)
        return float(raw_est)

    def merge_vertices(self, u_target: TNode, u_source: TNode) -> None:
        """
        Merge u_source's sketch into u_target's sketch via register-wise maximum.

        Args:
            u_target: Destination vertex sketch.
            u_source: Source vertex sketch.
        """
        if u_source not in self._registers:
            return
        if u_target not in self._registers:
            self._registers[u_target] = [0] * self._m
        for j in range(self._m):
            if self._registers[u_source][j] > self._registers[u_target][j]:
                self._registers[u_target][j] = self._registers[u_source][j]
