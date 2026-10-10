from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLayerBackpropagation:
    """
    ---
    contract:
      algo_id: ALGO-NN-24
      name: NnAlgoLayerBackpropagation
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.backpropagation
        - nn.linear
        - nn.chain_rule
        - nn.gradient_flow
      inputs:
        type: object
        properties:
          inputs:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input activation matrix X of shape (B, D_in).
          weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Weight matrix W of shape (D_out, D_in).
          output_grad:
            type: array
            items:
              type: array
              items:
                type: number
            description: Incoming upstream gradient dL/dY of shape (B, D_out).
          activation:
            type: string
            enum: [linear, relu, sigmoid, tanh]
            default: linear
            description: Forward post-activation applied to Y = X W^T + b.
          pre_activations:
            type: array
            items:
              type: array
              items:
                type: number
            description: Stored pre-activation values Z = X W^T + b of shape (B, D_out) (for nonlinear activations).
        required:
          - inputs
          - weights
          - output_grad
        additionalProperties: false
      outputs:
        type: object
        properties:
          grad_inputs:
            type: array
            items:
              type: array
              items:
                type: number
            description: Propagated gradient with respect to inputs dL/dX of shape (B, D_in).
          grad_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Parameter gradient with respect to weights dL/dW of shape (D_out, D_in).
          grad_bias:
            type: array
            items:
              type: number
            description: Parameter gradient with respect to bias dL/db of length D_out.
        required:
          - grad_inputs
          - grad_weights
          - grad_bias
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        inputs: Sequence[Sequence[float]],
        weights: Sequence[Sequence[float]],
        output_grad: Sequence[Sequence[float]],
        activation: Literal["linear", "relu", "sigmoid", "tanh"] = "linear",
        pre_activations: Optional[Sequence[Sequence[float]]] = None,
    ) -> Dict[str, Any]:
        b = len(inputs)
        if b == 0:
            raise ValueError("Precondition failed: inputs batch cannot be empty.")
        d_in = len(inputs[0])
        d_out = len(weights)
        if len(weights[0]) != d_in:
            raise ValueError(f"Precondition failed: weights shape ({d_out}, {len(weights[0])}) incompatible with input D_in={d_in}.")
        if len(output_grad) != b or len(output_grad[0]) != d_out:
            raise ValueError(f"Precondition failed: output_grad shape incompatible with batch B={b}, D_out={d_out}.")

        delta_z: List[List[float]] = []
        for i in range(b):
            row_delta: List[float] = []
            for j in range(d_out):
                dy = output_grad[i][j]
                if activation == "linear":
                    dz = dy
                elif activation == "relu":
                    z_val = pre_activations[i][j] if pre_activations else dy
                    dz = dy if z_val > 0.0 else 0.0
                elif activation == "sigmoid":
                    z_val = pre_activations[i][j] if pre_activations else 0.0
                    sig = 1.0 / (1.0 + math.exp(-z_val))
                    dz = dy * sig * (1.0 - sig)
                elif activation == "tanh":
                    z_val = pre_activations[i][j] if pre_activations else 0.0
                    th = math.tanh(z_val)
                    dz = dy * (1.0 - th * th)
                else:
                    raise ValueError(f"Precondition failed: unknown activation {activation}")
                row_delta.append(dz)
            delta_z.append(row_delta)

        grad_inputs = [[sum(delta_z[i][j] * weights[j][k] for j in range(d_out)) for k in range(d_in)] for i in range(b)]

        grad_weights = [[sum(delta_z[i][j] * inputs[i][k] for i in range(b)) for k in range(d_in)] for j in range(d_out)]

        grad_bias = [sum(delta_z[i][j] for i in range(b)) for j in range(d_out)]

        return {
            "grad_inputs": grad_inputs,
            "grad_weights": grad_weights,
            "grad_bias": grad_bias,
        }
