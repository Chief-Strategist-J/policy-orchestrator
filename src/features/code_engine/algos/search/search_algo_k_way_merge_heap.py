"""
================================================================================
ALGORITHM BLUEPRINT: K-WAY MERGE WITH MIN-HEAP (UNION & DEDUPLICATION)
================================================================================

1. OVERVIEW:
   K-Way Merge combines K sorted streams, shards, or posting lists into a single
   globally sorted output using a priority queue (min-heap). Essential for
   scatter-gather multi-shard index searches, external sorting, and deduplicating
   parallel search hits.

2. MATHEMATICAL & ALGORITHMIC FORMULATION:
   - Input: K sorted lists L_0, L_1, ..., L_{K-1}.
   - Priority Queue (Min-Heap): Stores (value, list_index, element_index).
   - Execution Loop:
       1. Initialize heap with head element (L_i[0], i, 0) from each non-empty list.
       2. While heap is not empty:
           a. Pop smallest element (val, i, idx).
           b. If val != last_emitted_val (deduplication filter):
               emit val (along with provenance metadata).
           c. If idx + 1 < len(L_i):
               push (L_i[idx + 1], i, idx + 1) onto heap.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(N * log K) where N is total items across all lists and K is list count.
   - Space Complexity: O(K) heap memory.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside function bodies.
================================================================================
"""

import heapq
from typing import Dict, List, Any, Optional, Tuple


class SearchEngineKWayMergeHeapAlgo:
    """
    --- contract:
      id: ALGO-SRCH-67
      name: SearchEngineKWayMergeHeapAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(TotalPostings * log K)
        space: O(K)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - posting.k_way_merge
      - heap.priority_queue
      - search.multi_term
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def merge_k_lists(self, lists: List[List[Dict[str, Any]]], deduplicate: bool = True) -> List[Dict[str, Any]]:
        heap: List[Tuple[Any, int, int]] = []

        for list_idx, lst in enumerate(lists):
            if lst:
                val = lst[0].get("sort_key", lst[0].get("id", lst[0])) if isinstance(lst[0], dict) else lst[0]
                heapq.heappush(heap, (val, list_idx, 0))

        merged: List[Dict[str, Any]] = []
        last_val = None

        while heap:
            val, list_idx, elem_idx = heapq.heappop(heap)
            raw_item = lists[list_idx][elem_idx]

            if not deduplicate or val != last_val:
                if isinstance(raw_item, dict):
                    item_copy = dict(raw_item)
                    item_copy["_stream_id"] = list_idx
                    merged.append(item_copy)
                else:
                    merged.append({"value": raw_item, "_stream_id": list_idx})
                last_val = val

            if elem_idx + 1 < len(lists[list_idx]):
                next_raw = lists[list_idx][elem_idx + 1]
                next_val = next_raw.get("sort_key", next_raw.get("id", next_raw)) if isinstance(next_raw, dict) else next_raw
                heapq.heappush(heap, (next_val, list_idx, elem_idx + 1))

        return merged

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        streams_raw = payload.get("streams", [])
        deduplicate = bool(payload.get("deduplicate", True))

        parsed_streams: List[List[Any]] = []
        for st in streams_raw:
            if isinstance(st, list):
                parsed_streams.append(st)

        merged_results = self.merge_k_lists(parsed_streams, deduplicate=deduplicate)

        total_input_items = sum(len(s) for s in parsed_streams)

        return {
            "algorithm": "ALGO-SRCH-67",
            "stream_count": len(parsed_streams),
            "total_input_elements": total_input_items,
            "deduplicate": deduplicate,
            "merged_output": merged_results,
            "merged_count": len(merged_results)
        }
