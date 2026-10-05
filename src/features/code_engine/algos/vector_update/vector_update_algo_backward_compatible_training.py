"""
================================================================================
ALGORITHM BLUEPRINT: BACKWARD-COMPATIBLE TRAINING (BCT) (ALGO-VEC-UPD-151)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Measures cross-model compatibility between new-model query vectors and legacy
   document embeddings to enable zero-downtime gradual re-embedding migrations.
================================================================================
"""

import math
from typing import Any, Dict, List, Optional


class VectorUpdateAlgoBackwardCompatibleTraining:
    """
    --- contract:
      id: ALGO-VEC-UPD-151
      name: VectorUpdateAlgoBackwardCompatibleTraining
      category: update
      complexity: O(Q * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        new_query_vectors: list[list[float]]
        legacy_doc_vectors: list[list[float]]
        ground_truth_relevance_pairs: list[list[int]]
        min_acceptable_compatibility_recall: float
      output_schema:
        cross_model_recall: float
        compatibility_verified: bool
        mean_cross_similarity: float
    ---
    """

    @staticmethod
    def _cos(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1e-12
        nb = math.sqrt(sum(x * x for x in b)) or 1e-12
        return dot / (na * nb)

    @classmethod
    def evaluate_compatibility(
        cls,
        new_query_vectors: List[List[float]],
        legacy_doc_vectors: List[List[float]],
        ground_truth_relevance_pairs: Optional[List[List[int]]] = None,
        min_acceptable_compatibility_recall: float = 0.85,
    ) -> Dict[str, Any]:
        sims = []
        hits = 0
        pairs = ground_truth_relevance_pairs or []

        for q_idx, q in enumerate(new_query_vectors):
            ranked = []
            for d_idx, d in enumerate(legacy_doc_vectors):
                if len(q) == len(d):
                    s = cls._cos(q, d)
                    ranked.append((s, d_idx))
                    sims.append(s)
            ranked.sort(key=lambda x: x[0], reverse=True)
            top_docs = [x[1] for x in ranked[:5]]
            for p in pairs:
                if p[0] == q_idx and p[1] in top_docs:
                    hits += 1

        rec = (hits / len(pairs)) if pairs else 1.0
        mean_sim = (sum(sims) / len(sims)) if sims else 0.0

        return {
            "cross_model_recall": round(rec, 4),
            "compatibility_verified": rec >= min_acceptable_compatibility_recall,
            "mean_cross_similarity": round(mean_sim, 4),
        }
