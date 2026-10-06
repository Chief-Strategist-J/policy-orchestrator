"""
================================================================================
ALGORITHM BLUEPRINT: ONTOLOGY-BASED QUERY REWRITING (OBDA / OWL 2 QL)
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

class KgAlgoObdaQueryRewriting:
    """
    --- contract:
      id: ALGO-KG-60
      name: KgAlgoObdaQueryRewriting
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Rewriting_Unions)
        space: O(Unions)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - obda.rewriting
      - owl2ql.reasoning
      - query_unfolding
      input_schema:
        query_class: string
        subclass_hierarchy: object
      output_schema:
        algorithm: string
        rewritten_union_queries: array
    ---
    """
    def rewrite_concept_query(self, target_class: str, subclass_hierarchy: Dict[str, List[str]]) -> Dict[str, Any]:
        unfolded = {target_class}
        queue = [target_class]
        while queue:
            curr = queue.pop(0)
            for child in subclass_hierarchy.get(curr, []):
                if child not in unfolded:
                    unfolded.add(child)
                    queue.append(child)
        return {
            "algorithm": "ALGO-KG-60",
            "original_query": target_class,
            "rewritten_union_queries": sorted(list(unfolded)),
        }
