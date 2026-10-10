from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoResidualConnection:
    """
    ---
    contract:
      algo_id: ALGO-NN-10
      name: NnAlgoResidualConnection
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.residual
        - nn.skip_connection
        - nn.residual_scaling
        - nn.projection_shortcut
        - nn.gradient_highway
      inputs:
        type: object
        properties:
          identity_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input identity/skip tensor x of shape (B, D_in).
          sublayer_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: Sublayer output transformation F(x) of shape (B, D_out).
          projection_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Optional linear projection matrix W_proj of shape (D_out, D_in) for dimension matching.
          scaling_factor:
            type: number
            default: 1.0
            description: Branch scaling multiplier alpha applied to F(x) (e.g. 1.0, 1/sqrt(2), or DeepNorm alpha).
          topology:
            type: string
            enum:
              - standard_add
              - scaled_add
              - gated_residual
            default: standard_add
            description: Residual combination topology.
          gate_weights:
            type: array
            items:
              type: number
            description: Optional learned scalar gate parameter vector of length D_out for gated_residual topology.
        required:
          - identity_tensor
          - sublayer_tensor
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
            description: Output residual tensor y = Proj(x) + alpha * F(x) of shape (B, D_out).
          identity_gradient_jacobian:
            type: array
            items:
              type: array
              items:
                type: number
            description: Identity shortcut Jacobian component dy/dx proving direct gradient highway (identity matrix or W_proj).
          has_projection:
            type: boolean
            description: True if a projection shortcut was computed, False if identity passthrough.
          batch_size:
            type: integer
            description: Number of batch rows B.
          feature_dim:
            type: integer
            description: Output feature dimension D_out.
        required:
          - output_tensor
          - identity_gradient_jacobian
          - has_projection
          - batch_size
          - feature_dim
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - identity_tensor and sublayer_tensor are non-empty 2D arrays of finite numbers
        - both tensors share identical batch size B >= 1
        - if D_in != D_out, projection_weights of shape (D_out, D_in) must be provided
        - scaling_factor is a finite positive number
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
          D_in: input dimension
          D_out: output dimension
        time_worst: O(B * D_out * (1 + (D_in if has_proj else 0)))
        time_typical: O(B * D_out)
        space: O(B * D_out)
      preconditions:
        - len(input.identity_tensor) > 0 and len(input.identity_tensor[0]) > 0
        - len(input.sublayer_tensor) == len(input.identity_tensor) and len(input.sublayer_tensor[0]) > 0
        - if len(input.identity_tensor[0]) != len(input.sublayer_tensor[0]): len(input.projection_weights) == len(input.sublayer_tensor[0]) and len(input.projection_weights[0]) == len(input.identity_tensor[0])
        - input.scaling_factor > 0.0 and is finite
      postconditions:
        - len(output.output_tensor) == len(input.identity_tensor)
        - len(output.output_tensor[0]) == len(input.sublayer_tensor[0])
        - output.feature_dim == len(input.sublayer_tensor[0])
      certificate: Exact vector addition y_i = x_i + alpha * F(x)_i with direct unit gradient identity flow.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-03
        - ALGO-NN-08
      references:
        - he2016deep
        - he2016identity
        - wang2022deepnorm
    ---
    """

    @staticmethod
    def forward(
        identity_tensor: Sequence[Sequence[float]],
        sublayer_tensor: Sequence[Sequence[float]],
        projection_weights: Optional[Sequence[Sequence[float]]] = None,
        scaling_factor: float = 1.0,
        topology: Literal["standard_add", "scaled_add", "gated_residual"] = "standard_add",
        gate_weights: Optional[Sequence[float]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(identity_tensor, Sequence) or len(identity_tensor) == 0:
            raise ValueError("Precondition failed: len(input.identity_tensor) > 0")

        d_in = len(identity_tensor[0])
        if d_in == 0:
            raise ValueError("Precondition failed: len(input.identity_tensor[0]) > 0")

        b = len(identity_tensor)
        for r_idx, row in enumerate(identity_tensor):
            if not isinstance(row, Sequence) or len(row) != d_in:
                raise ValueError(
                    f"Precondition failed: identity_tensor row {r_idx} length {len(row)} != expected {d_in}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: identity_tensor[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        if not isinstance(sublayer_tensor, Sequence) or len(sublayer_tensor) != b:
            raise ValueError(
                f"Precondition failed: len(input.sublayer_tensor) {len(sublayer_tensor) if isinstance(sublayer_tensor, Sequence) else 0} != batch size {b}"
            )

        d_out = len(sublayer_tensor[0])
        if d_out == 0:
            raise ValueError("Precondition failed: len(input.sublayer_tensor[0]) > 0")

        for r_idx, row in enumerate(sublayer_tensor):
            if not isinstance(row, Sequence) or len(row) != d_out:
                raise ValueError(
                    f"Precondition failed: sublayer_tensor row {r_idx} length {len(row)} != expected {d_out}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: sublayer_tensor[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        if not isinstance(scaling_factor, (int, float)) or math.isnan(scaling_factor) or math.isinf(scaling_factor) or scaling_factor <= 0.0:
            raise ValueError("Precondition failed: input.scaling_factor > 0.0 and finite")

        has_projection = False
        if d_in != d_out:
            if projection_weights is None:
                raise ValueError(
                    f"Precondition failed: dimension mismatch d_in={d_in} != d_out={d_out} requires projection_weights"
                )
            has_projection = True
        elif projection_weights is not None:
            has_projection = True

        if has_projection:
            if not isinstance(projection_weights, Sequence) or len(projection_weights) != d_out:
                raise ValueError(
                    f"Precondition failed: projection_weights length {len(projection_weights) if projection_weights else 0} != d_out {d_out}"
                )
            for r_idx, row in enumerate(projection_weights):
                if not isinstance(row, Sequence) or len(row) != d_in:
                    raise ValueError(
                        f"Precondition failed: projection_weights row {r_idx} length {len(row)} != d_in {d_in}"
                    )
                for c_idx, val in enumerate(row):
                    if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                        raise ValueError(
                            f"Precondition failed: projection_weights[{r_idx}][{c_idx}] is not finite ({val})"
                        )

        if topology == "gated_residual":
            if gate_weights is None or len(gate_weights) != d_out:
                raise ValueError(
                    f"Precondition failed: gate_weights length {len(gate_weights) if gate_weights else 0} != d_out {d_out}"
                )
            for g_idx, g_val in enumerate(gate_weights):
                if not isinstance(g_val, (int, float)) or math.isnan(g_val) or math.isinf(g_val):
                    raise ValueError(f"Precondition failed: gate_weights[{g_idx}] is not finite ({g_val})")

        output_tensor: List[List[float]] = []
        alpha = float(scaling_factor) if topology != "standard_add" else 1.0

        for b_i in range(b):
            x_row = identity_tensor[b_i]
            fx_row = sublayer_tensor[b_i]
            out_row: List[float] = [0.0] * d_out

            if has_projection:
                proj_x: List[float] = [0.0] * d_out
                for j in range(d_out):
                    w_row = projection_weights[j]  # type: ignore[index]
                    dot = 0.0
                    for k in range(d_in):
                        dot += float(x_row[k]) * float(w_row[k])
                    proj_x[j] = dot
                id_vec = proj_x
            else:
                id_vec = [float(v) for v in x_row]

            for j in range(d_out):
                fx_val = float(fx_row[j])
                if topology == "gated_residual":
                    gw = float(gate_weights[j])  # type: ignore[index]
                    out_row[j] = id_vec[j] + gw * fx_val
                else:
                    out_row[j] = id_vec[j] + alpha * fx_val

            output_tensor.append(out_row)

        if has_projection:
            jacobian: List[List[float]] = [[float(v) for v in row] for row in projection_weights]  # type: ignore[union-attr]
        else:
            jacobian = [[1.0 if i == j else 0.0 for j in range(d_in)] for i in range(d_in)]

        return {
            "output_tensor": output_tensor,
            "identity_gradient_jacobian": jacobian,
            "has_projection": has_projection,
            "batch_size": b,
            "feature_dim": d_out,
        }
