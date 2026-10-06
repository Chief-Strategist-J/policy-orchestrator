"""
================================================================================
ALGORITHM BLUEPRINT: SKOS CONCEPT SCHEME & TAXONOMIC HIERARCHY
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

class KgAlgoSkosConcept:
    """
    --- contract:
      id: ALGO-KG-06
      name: KgAlgoSkosConcept
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
    def build_taxonomy(self, relations: List[Dict[str, str]]) -> Dict[str, Any]:
        broader = defaultdict(set)
        narrower = defaultdict(set)
        concepts = set()
        for r in relations:
            s, p, o = r["subject"], r["predicate"], r["object"]
            concepts.add(s)
            concepts.add(o)
            if p == "skos:broader":
                broader[s].add(o)
                narrower[o].add(s)
            elif p == "skos:narrower":
                narrower[s].add(o)
                broader[o].add(s)
        top_concepts = [c for c in concepts if not broader[c]]
        return {
            "algorithm": "ALGO-KG-06",
            "concept_count": len(concepts),
            "top_concepts": sorted(top_concepts),
            "broader_map": {k: sorted(list(v)) for k, v in broader.items()},
            "narrower_map": {k: sorted(list(v)) for k, v in narrower.items()},
        }
