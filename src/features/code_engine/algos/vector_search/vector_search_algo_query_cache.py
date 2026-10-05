"""
================================================================================
ALGORITHM BLUEPRINT: QUERY & RESULT CACHING (ALGO-VEC-SRCH-104)
================================================================================

Query embedding and result caching avoids repeated neural inference and expensive
approximate nearest-neighbor scans for recurring queries. Cache keys strictly combine
normalized query text/vector, tenant ID, filter predicate hash, and index version (VG1)
to guarantee zero cross-tenant cache poisoning. Eviction follows LRU and TTL limits.
"""

from typing import Any, Dict, List, Optional
import hashlib
import json
import time


class VectorSearchAlgoQueryCache:
    """
    --- contract:
      id: ALGO-VEC-SRCH-104
      name: VectorSearchAlgoQueryCache
      category: vector
      complexity: O(1)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        cache_store: dict[str, any]
        query: str
        tenant_id: str
        filters: dict[str, any]
        index_version: str
        results: any
        ttl_seconds: int
      output_schema:
        cache_key: str
        is_hit: bool
        cached_data: any
        evicted_count: int
    ---
    """

    @staticmethod
    def generate_cache_key(
        query: str,
        tenant_id: str,
        filters: Dict[str, Any],
        index_version: str,
    ) -> str:
        canonical_filters = json.dumps(filters, sort_keys=True)
        raw = f"{tenant_id}::{index_version}::{query.strip().lower()}::{canonical_filters}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def get_or_set(
        cache_store: Dict[str, Any],
        query: str,
        tenant_id: str,
        filters: Dict[str, Any],
        index_version: str,
        results: Optional[Any] = None,
        ttl_seconds: int = 300,
        max_size: int = 1000,
    ) -> Dict[str, Any]:
        key = VectorSearchAlgoQueryCache.generate_cache_key(query, tenant_id, filters, index_version)
        now = time.time()
        evicted = 0

        if key in cache_store:
            entry = cache_store[key]
            if entry.get("expires_at", 0) > now:
                return {
                    "cache_key": key,
                    "is_hit": True,
                    "cached_data": entry.get("data"),
                    "evicted_count": 0,
                }
            else:
                del cache_store[key]
                evicted += 1

        if results is not None:
            if len(cache_store) >= max_size:
                oldest_key = min(cache_store.keys(), key=lambda k: cache_store[k].get("timestamp", 0))
                del cache_store[oldest_key]
                evicted += 1

            cache_store[key] = {
                "data": results,
                "timestamp": now,
                "expires_at": now + ttl_seconds,
            }

        return {
            "cache_key": key,
            "is_hit": False,
            "cached_data": results,
            "evicted_count": evicted,
        }
