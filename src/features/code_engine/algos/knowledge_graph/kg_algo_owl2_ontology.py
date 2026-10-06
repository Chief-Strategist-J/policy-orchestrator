"""
================================================================================
ALGORITHM BLUEPRINT: OWL 2 AXIOMS & PROPERTY RESTRICTION VALIDATOR
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

class KgAlgoOwl2Ontology:
    """
    --- contract:
      id: ALGO-KG-03
      name: KgAlgoOwl2Ontology
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
    def check_axioms(self, facts: List[Dict[str, str]], disjoint_pairs: List[Tuple[str, str]], functional_props: List[str]) -> Dict[str, Any]:
        violations = []
        prop_vals = {}
        for f in facts:
            s, p, o = f["subject"], f["predicate"], f["object"]
            if p in functional_props:
                key = (s, p)
                if key in prop_vals and prop_vals[key] != o:
                    violations.append(f"FunctionalPropertyConflict:{p} on {s} has multiple values: {prop_vals[key]}, {o}")
                else:
                    prop_vals[key] = o
        types_by_subject = {}
        for f in facts:
            if f["predicate"] in ("rdf:type", "type"):
                types_by_subject.setdefault(f["subject"], set()).add(f["object"])
        for s, types in types_by_subject.items():
            for c1, c2 in disjoint_pairs:
                if c1 in types and c2 in types:
                    violations.append(f"DisjointClassesViolation:{s} cannot be both {c1} and {c2}")
        return {
            "algorithm": "ALGO-KG-03",
            "valid": len(violations) == 0,
            "violations": violations,
            "checked_facts_count": len(facts),
        }
