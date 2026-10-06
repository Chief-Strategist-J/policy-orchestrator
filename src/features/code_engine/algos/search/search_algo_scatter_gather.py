"""
================================================================================
ALGORITHM BLUEPRINT: SCATTER-GATHER (DISTRIBUTED MULTI-SHARD PARALLEL SEARCH)
================================================================================

1. OVERVIEW:
   Scatter-Gather orchestrates parallel query distribution across multiple repository
   shards, nodes, or partitions. Dispatches concurrent requests to active shards,
   collects partial response batches, executes k-way min-heap merging, and isolates
   failing/timed-out shards to prevent cascading query stalls.

2. ARCHITECTURAL PROTOCOL:
   - Scatter: Query is broadcasted to N shard workers in parallel.
   - Local Execution: Each shard executes local filtering/scoring and returns top-K.
   - Gather: Coordinator collects responses, tracks unresponsive/failed shards,
     and merges results via min-heap into a globally sorted array.
   - Completeness Contract: Reports `complete: False` with list of failed shards
     if any shard times out, ensuring consumers never misinterpret partial cluster
     availability as zero matching results.

3. COMPLEXITY ANALYSIS:
   - Time: O(max(Shard_Latency) + K log N) with parallel execution.
   - Space: O(N * K) bounded coordinator buffer.

4. INVARIANTS & ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method/function bodies.
================================================================================
"""

import heapq
from typing import Dict, List, Any, Optional, Tuple


class SearchEngineScatterGatherAlgo:
    """
    --- contract:
      id: ALGO-SRCH-74
      name: SearchEngineScatterGatherAlgo
      version: 1.0.0
      category: search
      complexity:
        time: O(Shards)
        space: O(AggregatedResults)
      pure_function: true
      zero_inline_comments: true
      capability_tags:
      - distributed.scatter_gather
      - search.sharding
      - map_reduce.fanout
      input_schema:
        query: any
      output_schema:
        result: any
    ---
    """

    def gather_and_merge(
        self,
        shard_responses: List[Dict[str, Any]],
        global_limit: int = 50
    ) -> Dict[str, Any]:
        successful_shards: List[str] = []
        failed_shards: List[Dict[str, Any]] = []
        streams_to_merge: List[List[Dict[str, Any]]] = []

        for resp in shard_responses:
            shard_id = str(resp.get("shard_id", "unknown_shard"))
            status = str(resp.get("status", "ok")).lower()

            if status == "ok":
                successful_shards.append(shard_id)
                results = resp.get("results", [])
                if results:
                    streams_to_merge.append(results)
            else:
                failed_shards.append({
                    "shard_id": shard_id,
                    "error": resp.get("error", "timeout_or_unresponsive")
                })

        heap: List[Tuple[Any, int, int]] = []
        for stream_idx, stream in enumerate(streams_to_merge):
            if stream:
                score = stream[0].get("score", stream[0].get("id", 0))
                heapq.heappush(heap, (-score if isinstance(score, (int, float)) else score, stream_idx, 0))

        merged: List[Dict[str, Any]] = []
        while heap and len(merged) < global_limit:
            neg_score, stream_idx, elem_idx = heapq.heappop(heap)
            item = streams_to_merge[stream_idx][elem_idx]
            merged.append(item)

            if elem_idx + 1 < len(streams_to_merge[stream_idx]):
                next_item = streams_to_merge[stream_idx][elem_idx + 1]
                nxt_score = next_item.get("score", next_item.get("id", 0))
                heapq.heappush(heap, (-nxt_score if isinstance(nxt_score, (int, float)) else nxt_score, stream_idx, elem_idx + 1))

        is_complete = len(failed_shards) == 0

        return {
            "total_shards": len(shard_responses),
            "successful_shards_count": len(successful_shards),
            "failed_shards_count": len(failed_shards),
            "is_complete": is_complete,
            "failed_shards": failed_shards,
            "merged_results": merged,
            "result_count": len(merged)
        }

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        shard_responses = payload.get("shard_responses", [])
        limit = int(payload.get("global_limit", 50))

        gathered_summary = self.gather_and_merge(shard_responses, global_limit=limit)

        return {
            "algorithm": "ALGO-SRCH-74",
            "gather_summary": gathered_summary
        }
