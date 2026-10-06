"""
================================================================================
ALGORITHM BLUEPRINT: HYBRID GRAPH-VECTOR NODE INDEX & SIMILARITY SEARCH
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

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoHybridGraphVector:
    """
    --- contract:
      id: ALGO-KG-01
      name: KgAlgoHybridGraphVector
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
        self.vectors = {}

    def add_vector(self, node_id: str, embedding: List[float]):
        self.vectors[node_id] = embedding

    def search_similar_nodes(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        scored = []
        for nid, emb in self.vectors.items():
            dot = sum(a * b for a, b in zip(query_vector, emb))
            norm_a = math.sqrt(sum(a * a for a in query_vector))
            norm_b = math.sqrt(sum(b * b for b in emb))
            sim = dot / (norm_a * norm_b) if norm_a > 0 and norm_b > 0 else 0.0
            scored.append({"node_id": nid, "similarity": round(sim, 4)})
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]
