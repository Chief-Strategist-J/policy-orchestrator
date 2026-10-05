"""
================================================================================
ALGORITHM BLUEPRINT: SEMANTIC CACHE (ALGO-VEC-SRCH-105)
================================================================================

Semantic caching identifies semantically equivalent user queries by comparing the
incoming query vector against an index of previously cached queries. If the highest
cosine similarity exceeds a strict calibrated threshold (e.g. >= 0.92), the stored
response is returned immediately. Semantic caches are strictly partitioned by
tenant_id and access scope (VG1) to prevent unauthorized information leakage.
"""

from typing import Any, Dict, List, Optional
import math


class VectorSearchAlgoSemanticCache:
    """
    --- contract:
      id: ALGO-VEC-SRCH-105
      name: VectorSearchAlgoSemanticCache
      category: vector
      complexity: O(N_cached * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        cached_entries: list[dict[str, any]]
        query_vector: list[float]
        tenant_id: str
        similarity_threshold: float
      output_schema:
        is_hit: bool
        best_similarity: float
        cached_response: any
        matched_entry_id: any
    ---
    """

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        dim = min(len(a), len(b))
        if dim == 0:
            return 0.0
        dot = sum(a[i] * b[i] for i in range(dim))
        norm_a = math.sqrt(sum(a[i] ** 2 for i in range(dim)))
        norm_b = math.sqrt(sum(b[i] ** 2 for i in range(dim)))
        denom = norm_a * norm_b
        return dot / denom if denom > 1e-12 else 0.0

    @staticmethod
    def lookup(
        cached_entries: List[Dict[str, Any]],
        query_vector: List[float],
        tenant_id: str,
        similarity_threshold: float = 0.92,
    ) -> Dict[str, Any]:
        if not cached_entries or not query_vector:
            return {
                "is_hit": False,
                "best_similarity": 0.0,
                "cached_response": None,
                "matched_entry_id": None,
            }

        best_sim = -1.0
        best_entry = None

        for entry in cached_entries:
            if entry.get("tenant_id") != tenant_id:
                continue

            c_vec = entry.get("vector", [])
            sim = VectorSearchAlgoSemanticCache._cosine_similarity(query_vector, c_vec)
            if sim > best_sim:
                best_sim = sim
                best_entry = entry

        is_hit = best_sim >= similarity_threshold and best_entry is not None

        return {
            "is_hit": is_hit,
            "best_similarity": round(best_sim, 6) if best_sim >= 0 else 0.0,
            "cached_response": best_entry.get("response") if is_hit else None,
            "matched_entry_id": best_entry.get("id") if is_hit else None,
        }
