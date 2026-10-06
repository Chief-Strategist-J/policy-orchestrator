"""
================================================================================
ALGORITHM BLUEPRINT: CLOSENESS AND HARMONIC CENTRALITY METRICS
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

from collections import deque, defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoClosenessHarmonic:
    """
    --- contract:
      id: ALGO-KG-77
      name: KgAlgoClosenessHarmonic
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V * (V + E))
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - closeness_centrality
      - harmonic_centrality
      - graph_distances
      input_schema:
        nodes: array
        edges: array
      output_schema:
        algorithm: string
        harmonic_scores: object
    ---
    """
    def compute_harmonic(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        adj = defaultdict(list)
        for u, v in edges: adj[u].append(v); adj[v].append(u)
        scores = {}
        for s in nodes:
            dist = {s: 0}
            q = deque([s])
            while q:
                curr = q.popleft()
                for nbr in adj[curr]:
                    if nbr not in dist:
                        dist[nbr] = dist[curr] + 1
                        q.append(nbr)
            harmonic = sum(1.0 / d for nbr, d in dist.items() if nbr != s and d > 0)
            scores[s] = round(harmonic, 4)
        return {
            "algorithm": "ALGO-KG-77",
            "harmonic_scores": scores,
        }
