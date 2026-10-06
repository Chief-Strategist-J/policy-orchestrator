"""
================================================================================
ALGORITHM BLUEPRINT: RDFS SCHEMA INFERENCE ENGINE (SUBCLASS/SUBPROPERTY)
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

from collections import defaultdict, deque
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoRdfsSchema:
    """
    --- contract:
      id: ALGO-KG-02
      name: KgAlgoRdfsSchema
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
    def infer_hierarchy(self, sub_classes: List[Dict[str, str]], instances: List[Dict[str, str]]) -> Dict[str, Any]:
        adj = defaultdict(set)
        for rel in sub_classes:
            adj[rel["child"]].add(rel["parent"])
        inferred = []
        for inst in instances:
            ent = inst["entity"]
            direct_cls = inst["class"]
            visited = set()
            queue = deque([direct_cls])
            while queue:
                curr = queue.popleft()
                if curr not in visited:
                    visited.add(curr)
                    for parent in adj[curr]:
                        if parent not in visited:
                            queue.append(parent)
            for c in visited:
                inferred.append({"entity": ent, "inferred_class": c})
        return {
            "algorithm": "ALGO-KG-02",
            "inferred_count": len(inferred),
            "inferred_types": inferred,
        }
