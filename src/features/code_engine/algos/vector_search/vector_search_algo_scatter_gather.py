"""
================================================================================
ALGORITHM BLUEPRINT: SHARDED SCATTER-GATHER SEARCH (ALGO-VEC-SRCH-99)
================================================================================

Scatter-gather distributed search broadcasts query requests in parallel to all
independent index shards. Each shard executes local top-k candidate scoring and returns
its ranked partition results. The coordinator gathers shard responses, performs
k-way heap merging, deduplicates vectors across replicated/boundary nodes, and returns
the globally optimal top-k.
"""

from typing import Any, Dict, List, Optional
import heapq


class VectorSearchAlgoScatterGather:
    """
    --- contract:
      id: ALGO-VEC-SRCH-99
      name: VectorSearchAlgoScatterGather
      category: vector
      complexity: O(S_shards + S * k log S)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        shard_results: list[list[dict[str, any]]]
        top_k: int
      output_schema:
        total_shards: int
        total_candidates_gathered: int
        top_k: int
        global_results: list[dict[str, any]]
    ---
    """

    @staticmethod
    def scatter_gather_merge(
        shard_results: List[List[Dict[str, Any]]],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        if not shard_results:
            return {
                "total_shards": 0,
                "total_candidates_gathered": 0,
                "top_k": top_k,
                "global_results": [],
            }

        seen_ids = set()
        candidates: List[Dict[str, Any]] = []

        for shard_idx, res_list in enumerate(shard_results):
            for item in res_list:
                item_id = item.get("id")
                if item_id in seen_ids:
                    continue
                seen_ids.add(item_id)
                enriched = dict(item)
                enriched["origin_shard"] = shard_idx
                candidates.append(enriched)

        is_distance = any("distance" in c for c in candidates)
        if is_distance:
            candidates.sort(key=lambda x: x.get("distance", float("inf")))
        else:
            candidates.sort(key=lambda x: x.get("score", -float("inf")), reverse=True)

        return {
            "total_shards": len(shard_results),
            "total_candidates_gathered": len(candidates),
            "top_k": top_k,
            "global_results": candidates[:top_k],
        }
