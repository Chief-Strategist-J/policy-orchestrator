"""
================================================================================
ALGORITHM BLUEPRINT: REGULAR PATH QUERIES & PROPERTY PATH TRANSITIVITY
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

class KgAlgoRegularPathQueries:
    """
    --- contract:
      id: ALGO-KG-58
      name: KgAlgoRegularPathQueries
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - regular_path_queries
      - property_paths
      - transitivity.traversal
      input_schema:
        triples: array
        start_node: string
        predicate: string
      output_schema:
        algorithm: string
        reachable_nodes: array
    ---
    """
    def evaluate_plus_path(self, triples: List[Dict[str, str]], start_node: str, predicate: str) -> Dict[str, Any]:
        adj = defaultdict(set)
        for t in triples:
            if t.get("predicate") == predicate:
                adj[t["subject"]].add(t["object"])
        reachable = set()
        queue = deque(adj.get(start_node, set()))
        while queue:
            curr = queue.popleft()
            if curr not in reachable:
                reachable.add(curr)
                for neighbor in adj.get(curr, set()):
                    if neighbor not in reachable:
                        queue.append(neighbor)
        return {
            "algorithm": "ALGO-KG-58",
            "start_node": start_node,
            "predicate_path": f"{predicate}+",
            "reachable_nodes": sorted(list(reachable)),
        }
