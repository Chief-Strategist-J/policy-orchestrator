"""
================================================================================
ALGORITHM BLUEPRINT: IRI AND CURIE PREFIX NAMESPACE RESOLVER
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

class KgAlgoIriNamespaces:
    """
    --- contract:
      id: ALGO-KG-01
      name: KgAlgoIriNamespaces
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
    def __init__(self, prefixes: Optional[Dict[str, str]] = None):
        self.prefixes = prefixes or {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "owl": "http://www.w3.org/2002/07/owl#",
            "schema": "https://schema.org/",
            "skos": "http://www.w3.org/2004/02/skos/core#",
        }

    def expand_curie(self, curie: str) -> str:
        if ":" in curie and not curie.startswith("http://") and not curie.startswith("https://"):
            prefix, local = curie.split(":", 1)
            if prefix in self.prefixes:
                return f"{self.prefixes[prefix]}{local}"
        return curie

    def compact_iri(self, iri: str) -> str:
        for prefix, uri in self.prefixes.items():
            if iri.startswith(uri):
                return f"{prefix}:{iri[len(uri):]}"
        return iri
