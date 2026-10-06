"""
================================================================================
ALGORITHM BLUEPRINT: ENTITY LINKING & KB DISAMBIGUATION RESOLVER
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

from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoEntityLinking:
    """
    --- contract:
      id: ALGO-KG-27
      name: KgAlgoEntityLinking
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
    def link_entities(self, mentions: List[Dict[str, Any]], knowledge_base: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        linked = []
        for m in mentions:
            text = m["text"].lower()
            best_match = None
            for kb_id, kb_entry in knowledge_base.items():
                aliases = [a.lower() for a in kb_entry.get("aliases", [])]
                if text == kb_entry.get("name", "").lower() or text in aliases:
                    best_match = kb_id
                    break
            linked.append({
                "mention": m["text"],
                "kb_id": best_match,
                "is_linked": best_match is not None,
            })
        return {
            "algorithm": "ALGO-KG-27",
            "linked_results": linked,
        }
