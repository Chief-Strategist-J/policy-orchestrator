"""
================================================================================
ALGORITHM BLUEPRINT: BRANDES FAST BETWEENNESS CENTRALITY ALGORITHM
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

class KgAlgoBrandesBetweenness:
    """
    --- contract:
      id: ALGO-KG-76
      name: KgAlgoBrandesBetweenness
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V * E)
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - brandes.betweenness
      - shortest_path.accumulation
      - bottleneck.detection
      input_schema:
        nodes: array
        edges: array
      output_schema:
        algorithm: string
        betweenness: object
    ---
    """
    def compute_betweenness(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        cb = {n: 0.0 for n in nodes}
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v); adj[v].append(u)
        for s in nodes:
            stack = []
            pred = {w: [] for w in nodes}
            sigma = {w: 0 for w in nodes}; sigma[s] = 1
            dist = {w: -1 for w in nodes}; dist[s] = 0
            q = deque([s])
            while q:
                v = q.popleft()
                stack.append(v)
                for w in adj[v]:
                    if dist[w] < 0:
                        dist[w] = dist[v] + 1
                        q.append(w)
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)
            delta = {w: 0.0 for w in nodes}
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
                if w != s:
                    cb[w] += delta[w]
        return {
            "algorithm": "ALGO-KG-76",
            "betweenness": {k: round(v / 2.0, 4) for k, v in cb.items()},
        }
