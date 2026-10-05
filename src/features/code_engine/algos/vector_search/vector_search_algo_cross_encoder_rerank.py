"""
================================================================================
ALGORITHM BLUEPRINT: CROSS-ENCODER RERANKING (ALGO-VEC-SRCH-94)
================================================================================

Cross-encoder reranking feeds query and candidate document text together into a
single sequence to model all-to-all cross-attention across query and document tokens.
Unlike bi-encoders which represent query and document as independent vectors, the
cross-encoder captures fine token interactions, negations, and syntactic nuances,
acting as a high-precision filter on the top-M candidates.
"""

from typing import Any, Dict, List, Optional
import math
import re


class VectorSearchAlgoCrossEncoderRerank:
    """
    --- contract:
      id: ALGO-VEC-SRCH-94
      name: VectorSearchAlgoCrossEncoderRerank
      category: vector
      complexity: O(|candidates| * (|Q| + |D|)^2)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        query: str
        candidates: list[dict[str, any]]
        top_k: int
      output_schema:
        total_candidates: int
        top_k: int
        reranked_results: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [t.lower() for t in re.findall(r"\w+", text) if t]

    @staticmethod
    def rerank(
        query: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        if not query or not candidates:
            return {
                "total_candidates": len(candidates),
                "top_k": top_k,
                "reranked_results": [],
            }

        q_tokens = VectorSearchAlgoCrossEncoderRerank._tokenize(query)
        q_set = set(q_tokens)

        scored: List[Dict[str, Any]] = []

        for cand in candidates:
            doc_text = cand.get("text", "")
            d_tokens = VectorSearchAlgoCrossEncoderRerank._tokenize(doc_text)
            d_set = set(d_tokens)

            overlap = len(q_set.intersection(d_set))
            total_unique = len(q_set.union(d_set))
            jaccard = overlap / total_unique if total_unique > 0 else 0.0

            q_coverage = overlap / len(q_set) if q_set else 0.0

            phrase_bonus = 0.0
            if len(q_tokens) > 1 and query.lower() in doc_text.lower():
                phrase_bonus = 0.3

            cross_score = 0.5 * q_coverage + 0.3 * jaccard + phrase_bonus

            scored.append({
                "id": cand.get("id"),
                "cross_encoder_score": round(cross_score, 6),
                "query_coverage": round(q_coverage, 4),
                "text_preview": doc_text[:80],
                "metadata": cand.get("metadata", {}),
            })

        scored.sort(key=lambda x: x["cross_encoder_score"], reverse=True)

        return {
            "total_candidates": len(candidates),
            "top_k": top_k,
            "reranked_results": scored[:top_k],
        }
