"""
================================================================================
ALGORITHM BLUEPRINT: BATCHING WITH DYNAMIC PADDING (ALGO-VEC-TRFM-14)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Sorts input token sequences by length before forming mini-batches, dynamically
   padding each batch only to its local maximum length rather than the global model
   maximum limit. Generates strict attention masks and calculates pad waste reduction.

2. ARCHITECTURAL ROLE:
   Transformer role (Layer 1). Eliminates up to 70% of wasteful padding FLOPs during
   offline corpus embedding ingestion.

3. EXECUTION FLOW:
   a. Receive a collection of token ID lists.
   b. Sort indices by sequence length (bucket sorting or argsort).
   c. Group sorted sequences into fixed-size mini-batches.
   d. For each batch, pad sequences to the longest sequence in that batch.
   e. Construct binary attention masks (1 for valid token, 0 for pad).
   f. Record original sequence order to permit inverse-permutation un-sorting.
================================================================================
"""

from typing import Any, Dict, List, Optional


class VectorTransformAlgoDynamicPaddingBatching:
    """
    --- contract:
      id: ALGO-VEC-TRFM-14
      name: VectorTransformAlgoDynamicPaddingBatching
      category: transform
      complexity: O(N log N + N * max_batch_len)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        token_sequences: list[list[int]]
        batch_size: int
        pad_token_id: int
      output_schema:
        total_sequences: int
        total_batches: int
        padding_waste_reduction_pct: float
        batches: list[dict[str, any]]
    ---
    """

    @staticmethod
    def batch_and_pad(
        token_sequences: List[List[int]],
        batch_size: int = 16,
        pad_token_id: int = 0,
    ) -> Dict[str, Any]:
        if not token_sequences:
            return {
                "total_sequences": 0,
                "total_batches": 0,
                "padding_waste_reduction_pct": 0.0,
                "batches": [],
            }

        n = len(token_sequences)
        sorted_indices = sorted(range(n), key=lambda i: len(token_sequences[i]))

        batches: List[Dict[str, Any]] = []
        global_max_len = max(len(s) for s in token_sequences)

        dynamic_total_pads = 0
        static_total_pads = 0

        for b_start in range(0, n, batch_size):
            b_indices = sorted_indices[b_start : b_start + batch_size]
            b_seqs = [token_sequences[i] for i in b_indices]
            b_max_len = max(len(s) for s in b_seqs)

            padded_sequences: List[List[int]] = []
            attention_masks: List[List[int]] = []

            for s in b_seqs:
                pad_len = b_max_len - len(s)
                dynamic_total_pads += pad_len
                static_total_pads += (global_max_len - len(s))

                padded_seq = list(s) + [pad_token_id] * pad_len
                att_mask = [1] * len(s) + [0] * pad_len

                padded_sequences.append(padded_seq)
                attention_masks.append(att_mask)

            batches.append({
                "batch_id": len(batches),
                "batch_size": len(b_seqs),
                "max_sequence_length": b_max_len,
                "original_indices": b_indices,
                "padded_sequences": padded_sequences,
                "attention_masks": attention_masks,
            })

        waste_reduction = (
            round((1.0 - (dynamic_total_pads / max(1, static_total_pads))) * 100.0, 2)
            if static_total_pads > 0
            else 0.0
        )

        return {
            "total_sequences": n,
            "total_batches": len(batches),
            "padding_waste_reduction_pct": waste_reduction,
            "batches": batches,
        }
