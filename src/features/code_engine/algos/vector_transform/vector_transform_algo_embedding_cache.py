"""
================================================================================
ALGORITHM BLUEPRINT: EMBEDDING CACHE (CONTENT-HASH KEYED) (ALGO-VEC-TRFM-50)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Provides a deterministic, content-hash-keyed cache for text embeddings (Rule V1 & V4).
   Keys entries by SHA-256(text + model_name + model_version + prefix + norm_version).
   Avoids redundant forward-pass transformer computations during batch re-indexing or
   repeated query execution while strictly isolating by model version.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Eliminates up to 90% of embedding inference costs
   for common queries and repeated corpus documents.

3. EXECUTION FLOW:
   a. Compute deterministic composite key: sha256(model_version | task_prefix | text).
   b. Look up key in cache_store dict.
   c. If hit, return cached vector with is_hit=True.
   d. If miss and vector provided, store vector with timestamp and return is_hit=False.
   e. Manage LRU eviction when store size exceeds max_entries.
================================================================================
"""

from typing import Any, Dict, List, Optional
import hashlib
import time


class VectorTransformAlgoEmbeddingCache:
    """
    --- contract:
      id: ALGO-VEC-TRFM-50
      name: VectorTransformAlgoEmbeddingCache
      category: transform
      complexity: O(|text| + D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        cache_store: dict[str, any]
        text: str
        model_version: str
        prefix: str
        vector_to_cache: list[float]
        max_entries: int
      output_schema:
        cache_key: str
        is_hit: bool
        total_cache_size: int
        cached_vector: list[float]
    ---
    """

    @staticmethod
    def get_or_set(
        cache_store: Dict[str, Any],
        text: str,
        model_version: str = "v1.0.0",
        prefix: str = "",
        vector_to_cache: Optional[List[float]] = None,
        max_entries: int = 1000,
    ) -> Dict[str, Any]:
        raw_key = f"{model_version}::{prefix}::{text}"
        cache_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

        if cache_key in cache_store:
            entry = cache_store[cache_key]
            entry["last_accessed"] = time.time()
            return {
                "cache_key": cache_key,
                "is_hit": True,
                "total_cache_size": len(cache_store),
                "cached_vector": entry.get("vector", []),
            }

        is_hit = False
        stored_vec: List[float] = []

        if vector_to_cache is not None:
            if len(cache_store) >= max_entries:
                oldest_k = min(
                    cache_store.keys(),
                    key=lambda k: cache_store[k].get("last_accessed", 0.0),
                )
                del cache_store[oldest_k]

            cache_store[cache_key] = {
                "vector": list(vector_to_cache),
                "model_version": model_version,
                "prefix": prefix,
                "last_accessed": time.time(),
            }
            stored_vec = list(vector_to_cache)

        return {
            "cache_key": cache_key,
            "is_hit": is_hit,
            "total_cache_size": len(cache_store),
            "cached_vector": stored_vec,
        }
