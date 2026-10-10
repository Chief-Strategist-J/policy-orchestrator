from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoGradientCheckpointing:
    """
    ---
    contract:
      algo_id: ALGO-NN-27
      name: NnAlgoGradientCheckpointing
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.autodiff
        - nn.gradient_checkpointing
        - nn.memory_optimization
        - nn.recomputation
      inputs:
        type: object
        properties:
          num_layers:
            type: integer
            description: Total number of sequential layers L in the network.
          segment_size:
            type: integer
            default: 0
            description: Number of layers per checkpointed segment k (0 computes optimal sqrt(L)).
          initial_activation:
            type: number
            description: Scalar input value x_0 to feed into layer sequence.
        required:
          - num_layers
          - initial_activation
        additionalProperties: false
      outputs:
        type: object
        properties:
          checkpoints:
            type: array
            items:
              type: number
            description: Saved checkpoint activations at segment boundaries.
          final_output:
            type: number
            description: Final forward output x_L.
          checkpoint_indices:
            type: array
            items:
              type: integer
            description: Layer indices where activations were stored in memory.
          memory_saved_ratio:
            type: number
            description: Theoretical memory reduction ratio relative to standard full caching (1 - sqrt(L)/L).
        required:
          - checkpoints
          - final_output
          - checkpoint_indices
          - memory_saved_ratio
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        num_layers: int,
        initial_activation: float,
        segment_size: int = 0,
    ) -> Dict[str, Any]:
        if num_layers <= 0:
            raise ValueError(f"Precondition failed: num_layers must be > 0, got {num_layers}.")

        k = segment_size if segment_size > 0 else max(1, int(math.isqrt(num_layers)))

        checkpoints: List[float] = []
        checkpoint_indices: List[int] = []

        curr = initial_activation
        for layer_idx in range(num_layers):
            if layer_idx % k == 0:
                checkpoints.append(curr)
                checkpoint_indices.append(layer_idx)
            curr = math.tanh(0.9 * curr + 0.1)

        mem_saved = 1.0 - (len(checkpoints) / float(num_layers))

        return {
            "checkpoints": checkpoints,
            "final_output": curr,
            "checkpoint_indices": checkpoint_indices,
            "memory_saved_ratio": max(0.0, mem_saved),
        }
