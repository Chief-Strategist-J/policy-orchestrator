"""
================================================================================
ALGORITHM BLUEPRINT: APACHE TINKERPOP GREMLIN STEP TRAVERSAL PIPELINE
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

class KgAlgoGremlinTraversal:
    """
    --- contract:
      id: ALGO-KG-54
      name: KgAlgoGremlinTraversal
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Steps * Degree)
        space: O(Frontier)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - gremlin.traversal
      - tinkerpop.pipeline
      - step.executor
      input_schema:
        edges: array
        start_nodes: array
      output_schema:
        algorithm: string
        current_frontier: array
    ---
    """
    def __init__(self, edges: List[Dict[str, Any]], current_frontier: List[str]):
        self.edges = edges
        self.frontier = list(current_frontier)

    def out(self, edge_label: Optional[str] = None) -> "KgAlgoGremlinTraversal":
        next_frontier = []
        for curr in self.frontier:
            for e in self.edges:
                if e.get("source") == curr and (edge_label is None or e.get("type") == edge_label):
                    next_frontier.append(e.get("target"))
        self.frontier = next_frontier
        return self

    def values(self, prop_name: str, node_props: Dict[str, Dict[str, Any]]) -> List[Any]:
        return [node_props.get(nid, {}).get(prop_name) for nid in self.frontier if nid in node_props]

    def to_list(self) -> List[str]:
        return self.frontier
