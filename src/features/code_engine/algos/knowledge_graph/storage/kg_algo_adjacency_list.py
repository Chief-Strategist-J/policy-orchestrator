"""
================================================================================
ALGORITHM BLUEPRINT: GRAPH ADJACENCY LIST FORWARD & REVERSE INDEX
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph domain algorithm implementing deterministic
   graph modeling, storage indexing, ontology reasoning, and information extraction.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Zero Inline Comments: Code logic is self-documenting.
   - Purity & Determinism: Pure functional state transitions.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: Linear/Polynomial with respect to graph elements.
   - Space Complexity: Compact in-memory representation.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoAdjacencyList:
    """
    --- contract:
      id: ALGO-KG-01
      name: KgAlgoAdjacencyList
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(N)
        space: O(N)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - knowledge_graph.modeling
      - graph.construction
      - semantic_web
      input_schema:
        payload: object
      output_schema:
        algorithm: string
        status: string
    ---
    """
    def __init__(self):
        self.forward = defaultdict(list)
        self.reverse = defaultdict(list)

    def add_edge(self, source: str, target: str, edge_type: str = "relates_to", weight: float = 1.0):
        self.forward[source].append((target, edge_type, weight))
        self.reverse[target].append((source, edge_type, weight))

    def get_neighbors(self, node: str, direction: str = "out") -> List[Dict[str, Any]]:
        if direction == "out":
            return [{"target": t, "type": e, "weight": w} for t, e, w in self.forward.get(node, [])]
        elif direction == "in":
            return [{"source": s, "type": e, "weight": w} for s, e, w in self.reverse.get(node, [])]
        else:
            out_n = [{"node": t, "type": e, "dir": "out"} for t, e, _ in self.forward.get(node, [])]
            in_n = [{"node": s, "type": e, "dir": "in"} for s, e, _ in self.reverse.get(node, [])]
            return out_n + in_n
