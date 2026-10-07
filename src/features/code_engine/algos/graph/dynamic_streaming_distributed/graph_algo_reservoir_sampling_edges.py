"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RESERVOIR SAMPLING OF EDGES (ALGO-GRAPH-STRM-210)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Algorithm R / Algorithm L streaming reservoir sampling of graph edges.
   Maintains an exact, unbiased uniform random sample of size k over an infinite or
   unbounded stream of edges (u, v, w) in O(1) time per edge and O(k) memory.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) per stream edge update.
   - Space Complexity: O(k) reservoir sample slots.
   - Purity: Stateful PRNG-driven streaming sampler, reproducible via random seed.

3. INPUT PARAMETERS:
   - `capacity` (int): Maximum reservoir size k.
   - `seed` (Optional[int]): Random number generator seed.

4. OUTPUT PARAMETERS:
   - `add_edge(u, v, weight)` (bool): Returns True if edge entered the reservoir.
   - `get_sample()` (List[Tuple[TNode, TNode, float]]): Current unbiased uniform edge sample.
   - `estimate_total_stream_size()` (int): Number of edges processed so far.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Each edge seen in stream has exact inclusion probability min(1, k / t).
================================================================================
"""

import random
from typing import Generic, Hashable, List, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoReservoirSamplingEdges(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-STRM-210
      name: GraphAlgoReservoirSamplingEdges
      version: 1.0.0
      category: graph_streaming
      capability_tags: [graph, streaming, reservoir_sampling, uniform_sample, bounded_memory]
      inputs:
        type: object
        properties:
          capacity: {type: integer, minimum: 1}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          sample_size: {type: integer}
          total_edges: {type: integer}
      parameters:
        capacity: {type: integer}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: non_idempotent
      complexity:
        time: O(1) per update
        space: O(k)
    ---
    """

    def __init__(self, capacity: int = 1000, seed: Optional[int] = 42) -> None:
        """
        Initialize the edge reservoir sampler.

        Args:
            capacity: Maximum reservoir capacity k.
            seed: PRNG seed for reproducibility.
        """
        self._capacity: int = max(1, capacity)
        self._rng = random.Random(seed)
        self._reservoir: List[Tuple[TNode, TNode, float]] = []
        self._total_seen: int = 0

    def add_edge(self, u: TNode, v: TNode, weight: float = 1.0) -> bool:
        """
        Ingest an edge into the streaming reservoir.

        Args:
            u: Source node.
            v: Target node.
            weight: Edge weight attribute.

        Returns:
            True if edge was retained or replaced an element in reservoir, False otherwise.
        """
        self._total_seen += 1
        edge_tuple = (u, v, weight)
        if len(self._reservoir) < self._capacity:
            self._reservoir.append(edge_tuple)
            return True
        j = self._rng.randint(0, self._total_seen - 1)
        if j < self._capacity:
            self._reservoir[j] = edge_tuple
            return True
        return False

    def get_sample(self) -> List[Tuple[TNode, TNode, float]]:
        """
        Retrieve current snapshot of the edge reservoir.

        Returns:
            List of sampled edge tuples (u, v, weight).
        """
        return list(self._reservoir)

    def estimate_total_stream_size(self) -> int:
        """
        Return the total number of edges observed in stream.

        Returns:
            Integer total edge count.
        """
        return self._total_seen

    def get_sampling_fraction(self) -> float:
        """
        Return current empirical sampling probability k / t.

        Returns:
            Sampling ratio in range (0.0, 1.0].
        """
        if self._total_seen == 0:
            return 1.0
        return min(1.0, len(self._reservoir) / float(self._total_seen))
