"""
================================================================================
ALGORITHM BLUEPRINT: RULE-BASED COREFERENCE PRONOUN RESOLVER
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

import re
from typing import Dict, Any, List, Set, Tuple, Optional, Callable

class KgAlgoCoreferenceResolution:
    """
    --- contract:
      id: ALGO-KG-28
      name: KgAlgoCoreferenceResolution
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
    PRONOUNS = {"he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their"}

    def resolve_pronouns(self, sentences: List[str]) -> Dict[str, Any]:
        resolved = []
        last_subject = None
        for s in sentences:
            tokens = s.split()
            new_tokens = []
            sentence_subject = None
            for t in tokens:
                clean_t = t.lower().strip(".,!?;:")
                raw_token = t.strip(".,!?;:")
                if clean_t in self.PRONOUNS and last_subject:
                    new_tokens.append(f"[{last_subject}]")
                else:
                    if raw_token and raw_token[0].isupper() and sentence_subject is None:
                        sentence_subject = raw_token
                    new_tokens.append(t)
            if sentence_subject:
                last_subject = sentence_subject
            resolved.append(" ".join(new_tokens))
        return {
            "algorithm": "ALGO-KG-28",
            "resolved_sentences": resolved,
        }
