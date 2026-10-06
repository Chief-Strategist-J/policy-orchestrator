"""
================================================================================
ALGORITHM BLUEPRINT: NODE PROPERTY INVERTED FULL-TEXT INDEX
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

class KgAlgoPropertyFulltextIndex:
    """
    --- contract:
      id: ALGO-KG-01
      name: KgAlgoPropertyFulltextIndex
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
        self.index = defaultdict(set)

    def index_node(self, node_id: str, properties: Dict[str, Any]):
        for prop_name, prop_val in properties.items():
            if isinstance(prop_val, str):
                tokens = prop_val.lower().split()
                for tok in tokens:
                    self.index[tok].add(node_id)

    def search(self, query: str) -> List[str]:
        tokens = query.lower().split()
        if not tokens:
            return []
        hits = self.index.get(tokens[0], set())
        for tok in tokens[1:]:
            hits = hits.intersection(self.index.get(tok, set()))
        return sorted(list(hits))
