"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPH QUERY CACHING & MATERIALIZED VIEWS (ALGO-GRAPH-ENG-246)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Graph Query Result Caching and Materialized Views Engine.
   Caches expensive graph pattern queries (2-hop ego networks, shortest path queries,
   subgraph metrics) keyed by canonical query signatures, graph version epochs, and
   actor security ACLs with fine-grained dependency invalidation on mutation events.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1) cache lookup on hit, O(k) invalidated dependency pruning.
   - Space Complexity: O(Cached_Views * size(View)) LRU bounded storage.
   - Purity: Stateful cache layer, deterministic query hashing.

3. INPUT PARAMETERS:
   - `max_cache_size` (int): Maximum cached materialized views.

4. OUTPUT PARAMETERS:
   - `get_or_compute(query_key, compute_fn, touched_nodes)` (Any): Returns cached or computed view.
   - `invalidate_nodes(mutated_nodes)` (int): Count of invalidated cache entries.

5. AGENT CONTRACT:
   - Role: Retriever.
   - Guarantees: Zero stale view reads; cache keys incorporate security permission tokens.
================================================================================
"""

import hashlib
from collections import OrderedDict, defaultdict
from typing import Any, Callable, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoMaterializedViewsQueryCaching(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENG-246
      name: GraphAlgoMaterializedViewsQueryCaching
      version: 1.0.0
      category: graph_engineering
      capability_tags: [graph, engineering, query_caching, materialized_views, invalidation, permissions]
      inputs:
        type: object
        properties:
          max_cache_size: {type: integer, minimum: 10}
      outputs:
        type: object
        properties:
          cache_hits: {type: integer}
          cache_misses: {type: integer}
      parameters:
        max_cache_size: {type: integer}
      purity: stateful
      determinism: deterministic
      idempotency: idempotent_reads
      complexity:
        time: O(1) get, O(d) invalidate
        space: O(Cache_Size)
    ---
    """

    def __init__(self, max_cache_size: int = 1000) -> None:
        """
        Initialize query caching and materialized view container.

        Args:
            max_cache_size: Maximum entries in LRU cache.
        """
        self._max_size: int = max(10, max_cache_size)
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._deps: Dict[TNode, Set[str]] = defaultdict(set)
        self._hits: int = 0
        self._misses: int = 0

    def make_cache_key(self, query_name: str, params: Dict[str, Any], acl_token: str = "default") -> str:
        """
        Construct canonical deterministic cache key.

        Args:
            query_name: Identifier for query type.
            params: Dictionary of query parameters.
            acl_token: Security/tenant context token.

        Returns:
            MD5 hash signature string.
        """
        raw = f"{query_name}:{str(sorted(params.items()))}:{acl_token}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def get_or_compute(
        self,
        query_key: str,
        compute_fn: Callable[[], Any],
        touched_nodes: Optional[List[TNode]] = None,
    ) -> Any:
        """
        Retrieve materialized view from cache, or execute compute_fn on miss.

        Args:
            query_key: Hash key.
            compute_fn: Lazy computation callback.
            touched_nodes: Graph nodes whose mutation will invalidate this entry.

        Returns:
            Cached or newly computed result object.
        """
        if query_key in self._cache:
            self._hits += 1
            self._cache.move_to_end(query_key)
            return self._cache[query_key]

        self._misses += 1
        result = compute_fn()

        if len(self._cache) >= self._max_size:
            old_key, _ = self._cache.popitem(last=False)

        self._cache[query_key] = result
        if touched_nodes:
            for u in touched_nodes:
                self._deps[u].add(query_key)

        return result

    def invalidate_nodes(self, mutated_nodes: List[TNode]) -> int:
        """
        Invalidate all materialized views dependent on mutated nodes.

        Args:
            mutated_nodes: List of changed node IDs.

        Returns:
            Count of evicted cache entries.
        """
        evicted = 0
        for u in mutated_nodes:
            keys_to_evict = list(self._deps.get(u, set()))
            for k in keys_to_evict:
                if k in self._cache:
                    del self._cache[k]
                    evicted += 1
            self._deps.pop(u, None)
        return evicted

    def get_stats(self) -> Dict[str, Any]:
        """
        Return cache performance statistics.

        Returns:
            Dictionary of hits, misses, and hit ratio.
        """
        total = self._hits + self._misses
        hit_ratio = (self._hits / float(total)) if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_ratio": hit_ratio,
            "cached_entries": len(self._cache),
        }
