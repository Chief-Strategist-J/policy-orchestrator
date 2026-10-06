"""
================================================================================
ALGORITHM BLUEPRINT: LOUVAIN GRAPH MODULARITY COMMUNITY DETECTION
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

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoLouvainCommunity:
    """
    --- contract:
      id: ALGO-KG-81
      name: KgAlgoLouvainCommunity
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V log V)
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - louvain.community
      - modularity.optimization
      - clustering
      input_schema:
        nodes: array
        edges: array
      output_schema:
        algorithm: string
        community_count: integer
        communities: array
    ---
    """
    def detect_communities(self, nodes: List[str], edges: List[Tuple[str, str]]) -> Dict[str, Any]:
        adj = defaultdict(list)
        for u, v in edges: adj[u].append(v); adj[v].append(u)
        communities = {n: i for i, n in enumerate(nodes)}
        for _ in range(3):
            for n in nodes:
                nbr_comms = defaultdict(int)
                for nbr in adj[n]:
                    nbr_comms[communities[nbr]] += 1
                if nbr_comms:
                    best_comm = max(nbr_comms.items(), key=lambda x: x[1])[0]
                    communities[n] = best_comm
        groups = defaultdict(list)
        for n, c in communities.items(): groups[c].append(n)
        return {
            "algorithm": "ALGO-KG-81",
            "community_count": len(groups),
            "communities": [sorted(g) for g in groups.values()],
        }
