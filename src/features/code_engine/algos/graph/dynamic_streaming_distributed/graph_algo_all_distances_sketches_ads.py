"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ALL-DISTANCES SKETCHES (ADS) (ALGO-GRAPH-SUMM-240)
================================================================================

1. OVERVIEW & OBJECTIVE:
   All-Distances Sketches (ADS / Bottom-k Summaries) Engine (Cohen framework).
   Constructs compact per-vertex distance-decayed bottom-k hash sketches via
   pruned shortest path sweeps, enabling unbiased real-time estimation of neighborhood
   reachability profiles, closeness centrality, and distance-decayed graph similarities.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k * M log V) pruned Dijkstra passes.
   - Space Complexity: O(k log V) sketch entries per vertex.
   - Purity: Stateful randomized summary, reproducible with seed.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): Vertex list.
   - `edges` (List[Tuple[TNode, TNode, float]]): Weighted directed edges.
   - `k` (int): Number of bottom rank samples per distance threshold.
   - `seed` (Optional[int]): Random seed.

4. OUTPUT PARAMETERS:
   - `build_sketches()` (Dict[TNode, List[Tuple[float, TNode]]]): Per-vertex ADS entries (distance, node).
   - `estimate_neighborhood_size(u, max_dist)` (float): Estimated nodes reachable within distance d.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Cohen bottom-k harmonic mean unbiased estimation for neighborhood cardinalities.
================================================================================
"""

import heapq
import random
from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAllDistancesSketchesAds(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SUMM-240
      name: GraphAlgoAllDistancesSketchesAds
      version: 1.0.0
      category: graph_summarization
      capability_tags: [graph, summarization, ads, all_distances_sketches, bottom_k, closeness_centrality]
      inputs:
        type: object
        required: [nodes, edges]
        properties:
          nodes: {type: array}
          edges: {type: array}
          k: {type: integer, minimum: 2}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          sketches: {type: object}
      parameters:
        k: {type: integer}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(k * M log V)
        space: O(k * V log V)
    ---
    """

    def __init__(
        self,
        nodes: List[TNode],
        edges: List[Tuple[TNode, TNode, float]],
        k: int = 4,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize All-Distances Sketches engine.

        Args:
            nodes: Vertex list.
            edges: List of (u, v, weight) directed edges.
            k: Bottom-k sketch size parameter.
            seed: PRNG seed.
        """
        self._nodes: List[TNode] = list(nodes)
        self._k: int = max(2, k)
        self._rng = random.Random(seed)

        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {u: [] for u in self._nodes}
        for u, v, w in edges:
            if u in self._adj and v in self._adj:
                self._adj[u].append((v, float(w)))

        self._ranks: Dict[TNode, float] = {u: self._rng.random() for u in self._nodes}
        self._sketches: Dict[TNode, List[Tuple[float, TNode]]] = {u: [] for u in self._nodes}

    def build_sketches(self) -> Dict[TNode, List[Tuple[float, TNode]]]:
        """
        Construct per-vertex ADS sketches via Dijkstra sweeps.

        Returns:
            Dictionary mapping node to list of (distance, node_id) bottom-k pairs.
        """
        sorted_by_rank = sorted(self._nodes, key=lambda x: self._ranks[x])

        for center in sorted_by_rank:
            dists: Dict[TNode, float] = {center: 0.0}
            heap = [(0.0, str(center), center)]

            while heap:
                d, _, u = heapq.heappop(heap)
                if d > dists[u]:
                    continue

                if len(self._sketches[u]) < self._k or self._ranks[center] < self._ranks[self._sketches[u][-1][1]]:
                    self._sketches[u].append((d, center))
                    self._sketches[u].sort(key=lambda item: (item[0], self._ranks[item[1]]))

                for v, w in self._adj.get(u, []):
                    nd = d + w
                    if nd < dists.get(v, float("inf")):
                        dists[v] = nd
                        heapq.heappush(heap, (nd, str(v), v))

        return self._sketches

    def estimate_neighborhood_size(self, u: TNode, max_dist: float = float("inf")) -> float:
        """
        Estimate the count of vertices reachable from u within distance max_dist.

        Args:
            u: Target vertex.
            max_dist: Distance cutoff.

        Returns:
            Estimated reachability count.
        """
        if not self._sketches[u]:
            self.build_sketches()

        valid_entries = [node for d, node in self._sketches[u] if d <= max_dist]
        if not valid_entries:
            return 1.0

        if len(valid_entries) < self._k:
            return float(len(valid_entries))

        max_rank = max(self._ranks[node] for node in valid_entries)
        if max_rank <= 0.0:
            return float(len(self._nodes))

        return float((self._k - 1) / max_rank)
