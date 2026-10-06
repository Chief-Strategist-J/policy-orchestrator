"""
================================================================================
ALGORITHM BLUEPRINT: DIJKSTRA'S WEIGHTED SHORTEST PATH ON KNOWLEDGE GRAPH
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph domain algorithm implementing graph querying,
   declarative pattern matching, graph analytics, and description logic reasoning.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Inline Comments: Self-documenting pure methods.
   - Purity & Determinism: Pure functional state transitions.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: Conforming to graph query semantics and polynomial fragments.
   - Space Complexity: Compact working memory and frontier representations.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import heapq
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoDijkstraShortestPath:
    """
    --- contract:
      id: ALGO-KG-66
      name: KgAlgoDijkstraShortestPath
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O((V + E) log V)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - dijkstra.shortest_path
      - weighted.graph
      - min_priority_queue
      input_schema:
        weighted_adj: object
        source: string
      output_schema:
        algorithm: string
        distances: object
    ---
    """
    def compute_distances(self, adj: Dict[str, List[Tuple[str, float]]], source: str) -> Dict[str, Any]:
        distances = {source: 0.0}
        pq = [(0.0, source)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > distances.get(u, float("inf")):
                continue
            for v, weight in adj.get(u, []):
                new_d = d + weight
                if new_d < distances.get(v, float("inf")):
                    distances[v] = new_d
                    heapq.heappush(pq, (new_d, v))
        return {
            "algorithm": "ALGO-KG-66",
            "source": source,
            "distances": {k: round(v, 4) for k, v in distances.items()},
        }
