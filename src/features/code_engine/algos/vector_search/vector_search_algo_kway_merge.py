"""
================================================================================
ALGORITHM BLUEPRINT: K-WAY MERGE OF SHARD RESULTS (ALGO-VEC-SRCH-103)
================================================================================

k-way heap merge combines pre-sorted candidate lists from multiple distributed shards
into a single globally sorted top-k output list. A heap of size equal to the number
of shards tracks the best current candidate per stream. At each step, the global
optimum is emitted and replaced with the next element from that shard, maintaining
O(k log S) complexity while deduplicating boundary-duplicated items.
"""

from typing import Any, Dict, List, Optional
import heapq


class VectorSearchAlgoKWayMerge:
    """
    --- contract:
      id: ALGO-VEC-SRCH-103
      name: VectorSearchAlgoKWayMerge
      category: vector
      complexity: O(k log S_shards)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        shard_sorted_lists: list[list[dict[str, any]]]
        k: int
        is_distance: bool
      output_schema:
        shard_count: int
        k: int
        merged_results: list[dict[str, any]]
    ---
    """

    @staticmethod
    def merge(
        shard_sorted_lists: List[List[Dict[str, Any]]],
        k: int = 5,
        is_distance: bool = True,
    ) -> Dict[str, Any]:
        if not shard_sorted_lists:
            return {"shard_count": 0, "k": k, "merged_results": []}

        heap: List[Any] = []
        for shard_idx, items in enumerate(shard_sorted_lists):
            if items:
                val = items[0].get("distance" if is_distance else "score", 0.0)
                sort_key = val if is_distance else -val
                heapq.heappush(heap, (sort_key, shard_idx, 0, items[0]))

        merged: List[Dict[str, Any]] = []
        seen_ids = set()

        while heap and len(merged) < k:
            sort_key, shard_idx, item_idx, item = heapq.heappop(heap)
            item_id = item.get("id")

            if item_id not in seen_ids:
                seen_ids.add(item_id)
                merged.append(item)

            next_idx = item_idx + 1
            if next_idx < len(shard_sorted_lists[shard_idx]):
                next_item = shard_sorted_lists[shard_idx][next_idx]
                next_val = next_item.get("distance" if is_distance else "score", 0.0)
                next_sort_key = next_val if is_distance else -next_val
                heapq.heappush(heap, (next_sort_key, shard_idx, next_idx, next_item))

        return {
            "shard_count": len(shard_sorted_lists),
            "k": k,
            "merged_results": merged,
        }
