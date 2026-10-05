"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TOP-K SELECTION WITH A HEAP (ALGO-VEC-SRCH-53)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Maintains the top-k highest-scoring or lowest-distance candidates during an
   iterative or streaming vector scan (#53). Provides bounded O(k) memory usage
   and O(N log k) computational complexity, preventing memory bloat when scanning
   millions of candidate vectors.

2. ALGORITHMIC MECHANICS:
   - For distance minimization (L2): Uses a max-heap of size k storing (-dist, id, item).
     If the current candidate distance is strictly less than the worst in the heap,
     it replaces the root.
   - For score maximization (Dot/Cosine): Uses a min-heap of size k storing (score, id, item).
     If the candidate score is higher than the lowest in the heap, replaces the root.
   - Deterministic Tie-Breaking: When scores/distances match, breaks ties deterministically
     by lexicographical item ID.
   - Output: Extracts and sorts the k elements in final ascending distance or descending score.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Memory Safety: Bounded to exactly k elements at any point during iteration.
================================================================================
"""

from __future__ import annotations
import heapq
from typing import Any, Dict, List, Optional, Tuple, Union


class VectorSearchAlgoHeapTopK:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-53
      name: VectorSearchAlgoHeapTopK
      version: 1.0.0
      category: vector
      capability_tags: [vector, topk, heap, bounded_memory, priority_queue]
      inputs:
        type: object
        required: [candidates]
        properties:
          candidates:
            type: array
            items: {type: object}
          k: {type: integer, default: 10}
          score_key: {type: string, default: score}
          order: {type: string, enum: [asc, desc], default: desc}
          id_key: {type: string, default: id}
      outputs:
        type: object
        required: [k, order, total_candidates, top_k]
        properties:
          k: {type: integer}
          order: {type: string}
          score_key: {type: string}
          total_candidates: {type: integer}
          top_k:
            type: array
            items: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N log k)
        space: O(k)
      preconditions:
        - input.k > 0
      postconditions:
        - len(output.top_k) <= input.k
      compatible_adapters:
        - ADAPTER-HEAP-CANDIDATES
    ---
    """

    @classmethod
    def select_top_k(
        cls,
        candidates: List[Dict[str, Any]],
        k: int = 10,
        score_key: str = "score",
        order: str = "desc",
        id_key: str = "id",
    ) -> Dict[str, Any]:
        if k <= 0:
            return {"k": k, "order": order, "score_key": score_key, "total_candidates": len(candidates), "top_k": []}

        is_desc = order.lower() == "desc"
        heap: List[Tuple[float, str, Dict[str, Any]]] = []

        for idx, item in enumerate(candidates):
            raw_val = item.get(score_key, 0.0)
            score = float(raw_val)
            item_id = str(item.get(id_key, idx))

            if is_desc:
                effective_score = score
                if len(heap) < k:
                    heapq.heappush(heap, (effective_score, item_id, item))
                else:
                    if (effective_score, item_id) > (heap[0][0], heap[0][1]):
                        heapq.heapreplace(heap, (effective_score, item_id, item))
            else:
                effective_score = -score
                if len(heap) < k:
                    heapq.heappush(heap, (effective_score, item_id, item))
                else:
                    if (effective_score, item_id) > (heap[0][0], heap[0][1]):
                        heapq.heapreplace(heap, (effective_score, item_id, item))

        extracted = []
        while heap:
            eff_s, item_id, item = heapq.heappop(heap)
            real_s = eff_s if is_desc else -eff_s
            extracted.append((real_s, item_id, item))

        if is_desc:
            extracted.sort(key=lambda x: (-x[0], x[1]))
        else:
            extracted.sort(key=lambda x: (x[0], x[1]))

        result_items = [entry[2] for entry in extracted]

        return {
            "k": k,
            "order": "desc" if is_desc else "asc",
            "score_key": score_key,
            "total_candidates": len(candidates),
            "top_k": result_items,
        }
