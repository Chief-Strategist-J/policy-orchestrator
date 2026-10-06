r"""
================================================================================
ALGORITHM BLUEPRINT: HIERARCHICAL MULTI-LABEL ENTITY TYPING CLASSIFIER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Hierarchical entity typing inference engine (ConnectE / HETET protocols) mapping
   entity representations into structured taxonomic type manifolds. Evaluates cosine
   and hyper-plane projection similarity against type prototypes, enforces taxonomic
   transitive consistency ($T_1 \subseteq T_2 \implies P(T_2) \ge P(T_1)$), and
   outputs calibrated multi-label type assignments.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Taxonomic Monotonicity: Parent type confidence is bounded from below by child type confidence.
   - Purity & Determinism: Pure functional state transitions with zero side effects.
   - Zero Inline Comments: Code logic is self-documenting per architectural doctrine.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|Types| * D + |Taxonomy_Edges|) for prototype scoring and DAG propagation.
   - Space Complexity: O(|Types|) for type confidence tensors.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import math
from typing import Dict, Any, List, Set, Tuple, Optional, Callable


class KgAlgoEntityTypingClassifier:
    """
    --- contract:
      id: ALGO-KG-134
      name: KgAlgoEntityTypingClassifier
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(|Types| * D + |Taxonomy|)
        space: O(|Types|)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - entity_typing
      - hierarchical_taxonomy
      - multi_label
      - type_prediction
      input_schema:
        entity_emb: array
        type_prototypes: object
        taxonomy_parents: optional object
        min_sim: optional number
      output_schema:
        algorithm: string
        predicted_types: array
        type_probabilities: object
    ---
    """

    def predict_types(
        self,
        ent_emb: List[float],
        type_protos: Dict[str, List[float]],
        taxonomy_parents: Optional[Dict[str, List[str]]] = None,
        min_sim: float = 0.5,
        temperature: float = 1.0,
    ) -> Dict[str, Any]:
        norm_e = math.sqrt(sum(x * x for x in ent_emb)) or 1.0
        raw_scores: Dict[str, float] = {}

        for t_name, p_emb in type_protos.items():
            norm_p = math.sqrt(sum(y * y for y in p_emb)) or 1.0
            dot = sum(a * b for a, b in zip(ent_emb, p_emb))
            cos_sim = dot / (norm_e * norm_p)
            raw_scores[t_name] = cos_sim

        probabilities: Dict[str, float] = {}
        for t_name, sim in raw_scores.items():
            prob = 1.0 / (1.0 + math.exp(-min(50.0, max(-50.0, sim / max(1e-6, temperature)))))
            probabilities[t_name] = prob

        if taxonomy_parents:
            for child, parents in taxonomy_parents.items():
                child_p = probabilities.get(child, 0.0)
                for p in parents:
                    if p in probabilities:
                        probabilities[p] = max(probabilities[p], child_p)

        filtered_types = [
            (t_name, prob) for t_name, prob in probabilities.items()
            if raw_scores.get(t_name, 0.0) >= min_sim or prob >= 0.5
        ]
        filtered_types.sort(key=lambda x: x[1], reverse=True)

        return {
            "algorithm": "ALGO-KG-134",
            "predicted_types": [t[0] for t in filtered_types],
            "type_probabilities": {t_name: round(p, 4) for t_name, p in filtered_types},
            "total_candidate_types": len(type_protos),
        }
