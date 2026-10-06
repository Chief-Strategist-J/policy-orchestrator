"""
AXIOMATIC CONTRADICTION AND DISJOINTNESS AUDITOR
Implementation Module for KgAlgoConsistencyAuditor (ALGO-KG-191).

Strict Zero-Inline-Comment Doctrine enforced.
"""
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoConsistencyAuditor:
    """
    --- contract:
      id: ALGO-KG-191
      name: KgAlgoConsistencyAuditor
      version: 1.0.0
      category: knowledge_graph
      complexity:
        time: O(Entities * Disjoint_Rules)
        space: O(Inconsistencies)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - consistency_audit
      - disjoint_class_check
      - contradiction_scanner
      input_schema:
        entity_classes: object
        disjoint_pairs: array
      output_schema:
        algorithm: string
        consistent: boolean
        contradictions: array
    ---
    """
    def audit_consistency(self, entity_classes: Dict[str, List[str]], disjoint_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        contradictions: List[Dict[str, Any]] = []
        for ent_id, classes in entity_classes.items():
            class_set = set(classes)
            for c1, c2 in disjoint_pairs:
                if c1 in class_set and c2 in class_set:
                    contradictions.append({
                        "entity": ent_id,
                        "disjoint_classes": [c1, c2],
                        "issue": f"Entity belongs to disjoint classes {c1} and {c2}",
                    })
        return {
            "algorithm": "ALGO-KG-191",
            "consistent": len(contradictions) == 0,
            "contradiction_count": len(contradictions),
            "contradictions": contradictions,
        }
