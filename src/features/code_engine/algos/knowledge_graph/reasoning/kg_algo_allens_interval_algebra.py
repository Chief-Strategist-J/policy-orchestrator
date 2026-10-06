"""
================================================================================
ALGORITHM BLUEPRINT: ALLEN'S 13 TEMPORAL INTERVAL RELATIONS REASONER
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

class KgAlgoAllensIntervalAlgebra:
    """
    --- contract:
      id: ALGO-KG-99
      name: KgAlgoAllensIntervalAlgebra
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(1)
        space: O(1)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - allens.interval_algebra
      - temporal_reasoning
      - interval_calculus
      input_schema:
        interval_a: array
        interval_b: array
      output_schema:
        algorithm: string
        relation: string
    ---
    """
    def determine_relation(self, int_a: Tuple[float, float], int_b: Tuple[float, float]) -> str:
        s1, e1 = int_a
        s2, e2 = int_b
        if e1 < s2: return "BEFORE"
        if e2 < s1: return "AFTER"
        if e1 == s2: return "MEETS"
        if e2 == s1: return "MET_BY"
        if s1 == s2 and e1 == e2: return "EQUALS"
        if s1 == s2 and e1 < e2: return "STARTS"
        if s1 == s2 and e1 > e2: return "STARTED_BY"
        if s1 > s2 and e1 == e2: return "FINISHES"
        if s1 < s2 and e1 == e2: return "FINISHED_BY"
        if s1 > s2 and e1 < e2: return "DURING"
        if s1 < s2 and e1 > e2: return "CONTAINS"
        if s1 < s2 and e1 > s2 and e1 < e2: return "OVERLAPS"
        if s1 > s2 and s1 < e2 and e1 > e2: return "OVERLAPPED_BY"
        return "UNKNOWN"
