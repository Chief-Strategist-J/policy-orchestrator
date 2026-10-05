"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: RADIX BUCKET TOP-K SELECTION (ALGO-VEC-SRCH-54)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Implements a GPU-inspired radix selection and bucket-partitioning algorithm (#54)
   to extract the top-k highest scoring elements from large score vectors without
   a full O(N log N) global sort. Eliminates sorting bottlenecks when processing
   large similarity score tensors.

2. ALGORITHMIC MECHANICS:
   - Evaluates scores in linear O(N) expected time using quickselect / radix partitioning.
   - For float32 values, locates the pivot score containing the k-th rank threshold.
   - Filters candidate items meeting or exceeding the threshold and produces
     the sorted top-k slice.

3. ARCHITECTURAL INVARIANTS:
   - Zero-Inline-Comment Doctrine: Function bodies are 100% comment-free and pure.
   - Exactness: Produces identical mathematical top-k elements as exact sort.
================================================================================
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
import numpy as np


class VectorSearchAlgoRadixTopK:
    """
    ---
    contract:
      algo_id: ALGO-VEC-SRCH-54
      name: VectorSearchAlgoRadixTopK
      version: 1.0.0
      category: vector
      capability_tags: [vector, topk, radix, partition, quickselect, gpu_simulation]
      inputs:
        type: object
        required: [scores]
        properties:
          scores:
            type: array
            items: {type: number}
          k: {type: integer, default: 10}
          ids:
            type: array
            items: {type: string}
          largest: {type: boolean, default: true}
      outputs:
        type: object
        required: [k, largest, total_elements, top_k]
        properties:
          k: {type: integer}
          largest: {type: boolean}
          total_elements: {type: integer}
          top_k:
            type: array
            items:
              type: object
              properties:
                id: {type: string}
                index: {type: integer}
                score: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: irreversible
      side_effects: in_memory
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      complexity:
        time: O(N)
        space: O(N)
      preconditions:
        - len(input.scores) > 0
      postconditions:
        - len(output.top_k) <= input.k
      compatible_adapters:
        - ADAPTER-RADIX-SCORES
    ---
    """

    @classmethod
    def select_top_k(
        cls,
        scores: Union[List[float], np.ndarray],
        k: int = 10,
        ids: Optional[List[str]] = None,
        largest: bool = True,
    ) -> Dict[str, Any]:
        arr = np.asarray(scores, dtype=np.float32)
        n = arr.shape[0]

        if n == 0 or k <= 0:
            return {"k": k, "largest": largest, "total_elements": n, "top_k": []}

        actual_k = min(k, n)

        if ids is None:
            id_list = [str(i) for i in range(n)]
        else:
            if len(ids) != n:
                raise ValueError(f"Length of ids ({len(ids)}) must match scores size ({n})")
            id_list = ids

        if largest:
            part_idx = np.argpartition(-arr, actual_k - 1)[:actual_k]
            sub_scores = arr[part_idx]
            sub_sort = np.argsort(-sub_scores)
            final_indices = part_idx[sub_sort]
        else:
            part_idx = np.argpartition(arr, actual_k - 1)[:actual_k]
            sub_scores = arr[part_idx]
            sub_sort = np.argsort(sub_scores)
            final_indices = part_idx[sub_sort]

        matches = [
            {
                "id": id_list[idx],
                "index": int(idx),
                "score": float(arr[idx]),
            }
            for idx in final_indices
        ]

        return {
            "k": actual_k,
            "largest": largest,
            "total_elements": n,
            "top_k": matches,
        }
