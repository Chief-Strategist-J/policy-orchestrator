"""
================================================================================
ALGORITHM BLUEPRINT: WARSHALL TRANSITIVE CLOSURE REACHABILITY MATRIX
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

from collections import defaultdict, deque
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoTransitiveClosure:
    """
    --- contract:
      id: ALGO-KG-72
      name: KgAlgoTransitiveClosure
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V * (V + E))
        space: O(V^2)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - transitive_closure
      - warshall.reachability
      - complete_closure
      input_schema:
        adj: object
      output_schema:
        algorithm: string
        closure_pairs_count: integer
        reachability_map: object
    ---
    """
    def compute_closure(self, adj: Dict[str, List[str]]) -> Dict[str, Any]:
        closure = {}
        for u in adj:
            visited = set()
            queue = deque(adj[u])
            while queue:
                curr = queue.popleft()
                if curr not in visited:
                    visited.add(curr)
                    for nbr in adj.get(curr, []):
                        if nbr not in visited:
                            queue.append(nbr)
            closure[u] = sorted(list(visited))
        total_pairs = sum(len(v) for v in closure.values())
        return {
            "algorithm": "ALGO-KG-72",
            "closure_pairs_count": total_pairs,
            "reachability_map": closure,
        }
