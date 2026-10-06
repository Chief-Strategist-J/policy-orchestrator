"""
================================================================================
ALGORITHM BLUEPRINT: DEPTH-FIRST SEARCH (DFS) WITH CYCLE DETECTION
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

from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoDfsTraversal:
    """
    --- contract:
      id: ALGO-KG-64
      name: KgAlgoDfsTraversal
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - dfs.traversal
      - cycle.detection
      - path.discovery
      input_schema:
        adjacency: object
        start_node: string
      output_schema:
        algorithm: string
        traversal_order: array
        has_cycle: boolean
    ---
    """
    def traverse(self, adj: Dict[str, List[str]], start_node: str) -> Dict[str, Any]:
        visited = set()
        in_stack = set()
        order = []
        has_cycle = False

        def dfs(node: str):
            nonlocal has_cycle
            visited.add(node)
            in_stack.add(node)
            order.append(node)
            for neighbor in adj.get(node, []):
                if neighbor in in_stack:
                    has_cycle = True
                elif neighbor not in visited:
                    dfs(neighbor)
            in_stack.remove(node)

        dfs(start_node)
        return {
            "algorithm": "ALGO-KG-64",
            "traversal_order": order,
            "has_cycle": has_cycle,
        }
