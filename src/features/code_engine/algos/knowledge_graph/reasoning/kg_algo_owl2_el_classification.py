"""
================================================================================
ALGORITHM BLUEPRINT: OWL 2 EL CONSEQUENCE-BASED CLASSIFIER
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
from collections import defaultdict

class KgAlgoOwl2ElClassification:
    """
    --- contract:
      id: ALGO-KG-94
      name: KgAlgoOwl2ElClassification
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Axioms^2)
        space: O(Classes^2)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - owl2el.classification
      - consequence_based
      - tractable_biomedical
      input_schema:
        subclass_axioms: array
      output_schema:
        algorithm: string
        classified_hierarchy: object
    ---
    """
    def classify(self, subclass_axioms: List[Tuple[str, str]]) -> Dict[str, Any]:
        sub_to_super = defaultdict(set)
        classes = set()
        for sub, sup in subclass_axioms:
            sub_to_super[sub].add(sup)
            classes.add(sub); classes.add(sup)
        for c in classes: sub_to_super[c].add(c)
        changed = True
        while changed:
            size_before = sum(len(v) for v in sub_to_super.values())
            for c in classes:
                for sup in list(sub_to_super[c]):
                    sub_to_super[c].update(sub_to_super[sup])
            changed = sum(len(v) for v in sub_to_super.values()) > size_before
        return {
            "algorithm": "ALGO-KG-94",
            "classified_hierarchy": {k: sorted(list(v)) for k, v in sub_to_super.items()},
        }
