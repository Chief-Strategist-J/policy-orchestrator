"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH SPANNERS (BASWANA-SEN / GREEDY) (ALGO-GRAPH-SUMM-238)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graph Spanners Engine (Greedy (2k-1)-spanners & Baswana-Sen randomized clustering).
   Constructs sparse subgraphs preserving all pairwise geodesic shortest path distances
   up to a multiplicative stretch factor k (d_spanner(u, v) <= (2k - 1) * d_G(u, v)).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(k * M) for Baswana-Sen, O(M * (V + M)) for greedy.
   - Space Complexity: O(V + M) spanner edge sets with |E_spanner| <= O(k * V^{1 + 1/k}).
   - Purity: Pure functional transformation, deterministic greedy / reproducible randomized.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): Vertex set.
   - `weighted_edges` (List[Tuple[TNode, TNode, float]]): Weighted undirected edges.
   - `k` (int): Parameter determining stretch 2k - 1.

4. OUTPUT PARAMETERS:
   - `compute_greedy_spanner(stretch)` (List[Tuple[TNode, TNode, float]]): Spanner edges.
   - `get_edge_reduction_ratio()` (float): Sparsification fraction (|E_spanner| / |E_orig|).

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: All original edge distances bounded by d_spanner(u, v) <= stretch * w(u, v).
================================================================================
"""

import heapq
from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphSpannersBaswanaSen(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-SUMM-238
      name: GraphAlgoGraphSpannersBaswanaSen
      version: 1.0.0
      category: graph_summarization
      capability_tags: [graph, summarization, spanners, baswana_sen, greedy_spanner, distance_preservation]
      inputs:
        type: object
        required: [nodes, weighted_edges]
        properties:
          nodes: {type: array}
          weighted_edges: {type: array}
          k: {type: integer, minimum: 2}
      outputs:
        type: object
        properties:
          spanner_edges: {type: array}
          spanner_edge_count: {type: integer}
      parameters:
        k: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M * (V + M))
        space: O(V + M)
    ---
    """

    def __init__(
        self, nodes: List[TNode], weighted_edges: List[Tuple[TNode, TNode, float]], k: int = 2
    ) -> None:
        """
        Initialize graph spanner builder.

        Args:
            nodes: Vertex list.
            weighted_edges: List of (u, v, weight) tuples.
            k: Spanner parameter (stretch = 2k - 1).
        """
        self._nodes: List[TNode] = list(nodes)
        self._edges: List[Tuple[TNode, TNode, float]] = sorted(weighted_edges, key=lambda x: x[2])
        self._k: int = max(2, k)
        self._stretch: float = float(2 * self._k - 1)

    def compute_greedy_spanner(self) -> List[Tuple[TNode, TNode, float]]:
        """
        Compute greedy (2k - 1)-spanner.

        Returns:
            List of retained spanner edges.
        """
        spanner_adj: Dict[TNode, List[Tuple[TNode, float]]] = {u: [] for u in self._nodes}
        spanner_edges: List[Tuple[TNode, TNode, float]] = []

        def get_spanner_dist(src: TNode, tgt: TNode, max_limit: float) -> float:
            dists = {src: 0.0}
            heap = [(0.0, str(src), src)]
            while heap:
                d, _, u = heapq.heappop(heap)
                if u == tgt:
                    return d
                if d > max_limit:
                    continue
                if d > dists.get(u, float("inf")):
                    continue
                for v, w in spanner_adj.get(u, []):
                    nd = d + w
                    if nd <= max_limit and nd < dists.get(v, float("inf")):
                        dists[v] = nd
                        heapq.heappush(heap, (nd, str(v), v))
            return float("inf")

        for u, v, w in self._edges:
            bound = self._stretch * w
            curr_dist = get_spanner_dist(u, v, bound)
            if curr_dist > bound:
                spanner_edges.append((u, v, w))
                spanner_adj[u].append((v, w))
                spanner_adj[v].append((u, w))

        return spanner_edges
