from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoDenseHighwayConnection:
    """
    ---
    contract:
      algo_id: ALGO-NN-11
      name: NnAlgoDenseHighwayConnection
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.densenet
        - nn.highway
        - nn.dense_connectivity
        - nn.feature_reuse
        - nn.gated_skip
      inputs:
        type: object
        properties:
          layer_inputs:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: List of L feature maps/tensors X_0, X_1, ..., X_{L-1} each of shape (B, D_l).
          current_layer_output:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output tensor H(X) of current transformation of shape (B, D_out).
          mode:
            type: string
            enum:
              - densenet_concat
              - highway_gated
            default: densenet_concat
            description: Dense connectivity mode (feature map concatenation vs highway gating).
          gate_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Weight matrix W_T of shape (D_out, D_in) for highway transform gate T(X).
          gate_bias:
            type: array
            items:
              type: number
            description: Optional bias vector b_T of shape (D_out) for highway transform gate.
          carry_bias_init:
            type: number
            default: -2.0
            description: Initial negative bias for highway gate ensuring carry gate 1-T(x) dominates initially.
        required:
          - layer_inputs
        additionalProperties: false
      outputs:
        type: object
        properties:
          output_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Combined output tensor of shape (B, sum(D_l) + D_out) for DenseNet or (B, D_out) for Highway.
          total_channels:
            type: integer
            description: Total aggregated channel count across all concatenated layers.
          mode:
            type: string
            description: Executed mode identifier.
          gate_activations:
            type: array
            items:
              type: array
              items:
                type: number
            description: Evaluated transform gate activations T(X) if mode is highway_gated.
        required:
          - output_tensor
          - total_channels
          - mode
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - All input tensors share an identical batch dimension B >= 1.
        - Channel dimensions D_l are positive integers.
        - For highway_gated mode, D_in == D_out or gate_weights is provided for affine projection.
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: n/a
      uses_model: false
      complexity:
        variables:
          B: batch size
          L: number of previous layer tensors
          D_total: sum of channel dimensions across all concatenated layers
          D_in: input channel dimension for highway
          D_out: output channel dimension for highway
        time_worst: O(B * D_total) for densenet; O(B * D_in * D_out) for highway
        time_typical: same
        space: O(B * D_total) for densenet; O(B * D_out) for highway
      preconditions:
        - len(input.layer_inputs) > 0
        - all(len(x) == len(input.layer_inputs[0]) for x in input.layer_inputs)
        - all(len(row) > 0 for x in input.layer_inputs for row in x)
      postconditions:
        - len(output.output_tensor) == len(input.layer_inputs[0])
        - output.total_channels > 0
      certificate: Exact concatenation tensor shape matching and bounded highway gate range [0, 1].
      compatible_adapters:
        - ADAPTER-VECTOR-FEATURE-MATRIX
      related_algos:
        - ALGO-NN-10
      references:
        - huang2017densenet
        - srivastava2015highway
    ---
    """

    @staticmethod
    def forward(
        layer_inputs: Sequence[Sequence[Sequence[float]]],
        current_layer_output: Optional[Sequence[Sequence[float]]] = None,
        mode: Literal["densenet_concat", "highway_gated"] = "densenet_concat",
        gate_weights: Optional[Sequence[Sequence[float]]] = None,
        gate_bias: Optional[Sequence[float]] = None,
        carry_bias_init: float = -2.0,
    ) -> Dict[str, Any]:
        # --- Precondition Validation ---
        if not layer_inputs or len(layer_inputs) == 0:
            raise ValueError("Precondition failed: len(input.layer_inputs) > 0")

        batch_size = len(layer_inputs[0])
        if batch_size == 0:
            raise ValueError("Precondition failed: batch_size > 0")

        for idx, tensor in enumerate(layer_inputs):
            if len(tensor) != batch_size:
                raise ValueError(
                    f"Precondition failed: tensor {idx} batch size {len(tensor)} != {batch_size}"
                )
            for r_idx, row in enumerate(tensor):
                if len(row) == 0:
                    raise ValueError(
                        f"Precondition failed: tensor {idx} row {r_idx} is empty"
                    )
                for val in row:
                    if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                        raise ValueError(f"Precondition failed: non-finite value {val} in layer_inputs")

        if mode == "densenet_concat":
            # Concatenate along channel dimension D for each sample b
            all_tensors = list(layer_inputs)
            if current_layer_output is not None:
                if len(current_layer_output) != batch_size:
                    raise ValueError(
                        f"Precondition failed: current_layer_output batch {len(current_layer_output)} != {batch_size}"
                    )
                all_tensors.append(current_layer_output)

            output_tensor: List[List[float]] = []
            for b in range(batch_size):
                combined_row: List[float] = []
                for t in all_tensors:
                    combined_row.extend([float(v) for v in t[b]])
                output_tensor.append(combined_row)

            total_channels = len(output_tensor[0])
            return {
                "output_tensor": output_tensor,
                "total_channels": total_channels,
                "mode": mode,
                "gate_activations": None,
            }

        elif mode == "highway_gated":
            if current_layer_output is None:
                raise ValueError("Precondition failed: current_layer_output required for highway_gated")
            if len(current_layer_output) != batch_size:
                raise ValueError("Precondition failed: current_layer_output batch size mismatch")

            input_x = layer_inputs[-1]  # Primary skip source
            d_in = len(input_x[0])
            d_out = len(current_layer_output[0])

            # Transform gate: T(x) = sigmoid(x W_T^T + b_T)
            gate_activations: List[List[float]] = []
            output_tensor = []

            for b in range(batch_size):
                x_b = input_x[b]
                h_b = current_layer_output[b]
                t_row: List[float] = []
                y_row: List[float] = []

                for j in range(d_out):
                    if gate_weights is not None:
                        # Compute dot product
                        dot = sum(float(gate_weights[j][k]) * float(x_b[k]) for k in range(d_in))
                    else:
                        if d_in != d_out:
                            raise ValueError("Precondition failed: d_in != d_out requires gate_weights")
                        dot = float(x_b[j])

                    bias_term = float(gate_bias[j]) if gate_bias is not None else float(carry_bias_init)
                    z = dot + bias_term

                    # Numerically stable sigmoid: T(z)
                    if z >= 0:
                        t_val = 1.0 / (1.0 + math.exp(-z))
                    else:
                        t_val = math.exp(z) / (1.0 + math.exp(z))

                    t_row.append(t_val)
                    # Highway output: y = T(x) * H(x) + (1 - T(x)) * x
                    x_val = float(x_b[j]) if d_in == d_out else 0.0
                    y_val = t_val * float(h_b[j]) + (1.0 - t_val) * x_val
                    y_row.append(y_val)

                gate_activations.append(t_row)
                output_tensor.append(y_row)

            return {
                "output_tensor": output_tensor,
                "total_channels": d_out,
                "mode": mode,
                "gate_activations": gate_activations,
            }
        else:
            raise ValueError(f"Unknown mode: {mode}")
