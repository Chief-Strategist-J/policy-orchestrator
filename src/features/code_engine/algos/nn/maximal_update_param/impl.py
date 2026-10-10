from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoMaximalUpdateParam:
    """
    ---
    contract:
      algo_id: ALGO-NN-50
      name: NnAlgoMaximalUpdateParam
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.scaling
        - nn.mup
        - nn.hyperparameter_transfer
        - nn.infinite_width
      inputs:
        type: object
        properties:
          base_width:
            type: integer
            description: Proxy model base hidden width n_0 >= 1.
          target_width:
            type: integer
            description: Target scaled model hidden width n >= 1.
          base_lr:
            type: number
            description: Optimal learning rate eta_0 tuned on proxy model.
          layer_type:
            type: string
            enum: [input_embedding, hidden_weight, output_head]
            default: hidden_weight
            description: Specific architectural layer role in muP framework.
        required:
          - base_width
          - target_width
          - base_lr
        additionalProperties: false
      outputs:
        type: object
        properties:
          scaled_lr:
            type: number
            description: Scaled learning rate eta for target width.
          init_std_multiplier:
            type: number
            description: Scaling multiplier for weight initialization standard deviation.
          width_ratio:
            type: number
            description: Hidden dimension ratio n / n_0.
        required:
          - scaled_lr
          - init_std_multiplier
          - width_ratio
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        base_width: int,
        target_width: int,
        base_lr: float,
        layer_type: Literal["input_embedding", "hidden_weight", "output_head"] = "hidden_weight",
    ) -> Dict[str, Any]:
        if base_width < 1 or target_width < 1:
            raise ValueError("Precondition failed: widths must be >= 1.")
        if base_lr <= 0.0:
            raise ValueError(f"Precondition failed: base_lr must be > 0, got {base_lr}.")

        ratio = float(target_width) / float(base_width)

        if layer_type == "hidden_weight":
            scaled_lr = base_lr / ratio
            init_std = 1.0 / math.sqrt(ratio)
        elif layer_type == "input_embedding":
            scaled_lr = base_lr
            init_std = 1.0
        elif layer_type == "output_head":
            scaled_lr = base_lr / ratio
            init_std = 1.0 / ratio
        else:
            raise ValueError(f"Precondition failed: unknown layer_type {layer_type}")

        return {
            "scaled_lr": scaled_lr,
            "init_std_multiplier": init_std,
            "width_ratio": ratio,
        }
