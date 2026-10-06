"""
================================================================================
ALGORITHM BLUEPRINT: INDEX-VERSIONED QUERY RESULT CACHE
================================================================================

1. OVERVIEW:
   Caches search query results using compound cryptographic keys formed by
   normalizing the query string, hashing the active repository commit / index version,
   and scoping the search path. When code is edited or re-indexed, the version token
   automatically shifts, causing subsequent queries to naturally bypass stale cache
   entries without requiring complex distributed cache invalidation sweeps.

2. KEY GENERATION FORMULA:
   - Normalized Query: Whitespace canonicalized, lowercase operators, trimmed flags.
   - Cache Key: SHA256(normalized_query + ":" + index_version + ":" + scope_path).
   - Eviction: Least-Recently-Used (LRU) policy when max entry count is reached.

3. COMPLEXITY ANALYSIS:
   - Lookup Time: O(1) hash table lookup.
   - Space Complexity: O(C * M) where C is cache capacity and M is average response size.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import hashlib
from collections import OrderedDict
from typing import Dict, List, Any, Optional, Tuple


class SearchEngineIndexVersionedCacheAlgo:
    """
    Implements an LRU query result cache with commit/index-versioned key derivation.
    """

    def __init__(self, capacity: int = 1000) -> None:
        self._capacity: int = max(10, capacity)
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._hits: int = 0
        self._misses: int = 0

    def canonicalize_query(self, query: str, scope: str = "") -> str:
        """
        Normalizes query tokens and whitespace.
        """
        tokens = query.strip().split()
        normalized_q = " ".join(tokens)
        normalized_scope = scope.strip().lower()
        return f"{normalized_q}@@{normalized_scope}"

    def compute_cache_key(self, query: str, index_version: str, scope: str = "") -> str:
        """
        Derives an immutable cache key from query, version, and scope.
        """
        canonical_str = self.canonicalize_query(query, scope)
        raw_key = f"{canonical_str}##{index_version}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:24]

    def get(self, query: str, index_version: str, scope: str = "") -> Tuple[bool, Optional[Any]]:
        """
        Looks up cached query result.
        """
        key = self.compute_cache_key(query, index_version, scope)
        if key in self._cache:
            self._cache.move_to_end(key)
            self._hits += 1
            return True, self._cache[key]["data"]
        self._misses += 1
        return False, None

    def put(self, query: str, index_version: str, data: Any, scope: str = "") -> str:
        """
        Caches a query result, evicting oldest item if capacity is exceeded.
        """
        key = self.compute_cache_key(query, index_version, scope)
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = {
            "query": query,
            "index_version": index_version,
            "scope": scope,
            "data": data
        }
        if len(self._cache) > self._capacity:
            self._cache.popitem(last=False)
        return key

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes cache lookup or put operations.
        """
        action = str(payload.get("action", "get")).lower()
        query = str(payload.get("query", ""))
        version = str(payload.get("index_version", "v1.0"))
        scope = str(payload.get("scope", ""))
        payload_data = payload.get("data")

        key = self.compute_cache_key(query, version, scope)
        found = False
        val = None

        if action == "put" and payload_data is not None:
            self.put(query, version, payload_data, scope=scope)
            found = True
            val = payload_data
        else:
            found, val = self.get(query, version, scope=scope)

        total_lookups = self._hits + self._misses
        hit_ratio = round((self._hits / total_lookups) * 100, 2) if total_lookups > 0 else 0.0

        return {
            "algorithm": "ALGO-SRCH-76",
            "action": action,
            "cache_key": key,
            "cache_hit": found,
            "value": val,
            "stats": {
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio_pct": hit_ratio,
                "current_size": len(self._cache),
                "capacity": self._capacity
            }
        }
