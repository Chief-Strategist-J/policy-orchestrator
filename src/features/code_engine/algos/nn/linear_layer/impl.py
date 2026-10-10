from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLinearAffineLayer:
    """
    ---
    contract:
      algo_id: ALGO-NN-03
      name: NnAlgoLinearAffineLayer
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.linear
        - nn.affine
        - nn.initialization
        - nn.fan_in_fan_out
      inputs:
        type: object
        properties:
          input_batch:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input batch matrix X of shape (B, d_in).
          weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: Weight matrix W of shape (d_out, d_in).
          bias:
            type: array
            items:
              type: number
            description: Optional bias vector b of shape (d_out). Defaults to zero vector if null.
          init_mode:
            type: string
            enum:
              - kaiming_uniform
              - kaiming_normal
              - glorot_uniform
              - glorot_normal
              - lecun_uniform
              - lecun_normal
            default: glorot_uniform
            description: Variance scaling initialization scheme to compute fan-in/fan-out theoretical parameters.
        required:
          - input_batch
          - weights
        additionalProperties: false
      outputs:
        type: object
        properties:
          output_batch:
            type: array
            items:
              type: array
              items:
                type: number
            description: Affine transformed output matrix Y = X W^T + b of shape (B, d_out).
          fan_in:
            type: integer
            description: Number of input features d_in.
          fan_out:
            type: integer
            description: Number of output features d_out.
          batch_size:
            type: integer
            description: Number of samples in batch B.
          theoretical_variance:
            type: number
            description: Theoretical weight variance under the specified initialization scheme.
          theoretical_bound:
            type: number
            description: Theoretical uniform sampling bound [-limit, limit] if uniform init mode selected, else null.
        required:
          - output_batch
          - fan_in
          - fan_out
          - batch_size
          - theoretical_variance
          - theoretical_bound
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - input_batch is a non-empty 2D matrix of shape (B, d_in) where B >= 1, d_in >= 1
        - weights is a 2D matrix of shape (d_out, d_in) where d_out >= 1
        - bias is either null or a 1D vector of length d_out
        - all numerical values are finite floating-point numbers
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
          d_in: input dimension
          d_out: output dimension
        time_worst: O(B * d_in * d_out)
        time_typical: O(B * d_in * d_out)
        space: O(B * d_out)
      preconditions:
        - len(input.input_batch) > 0 and len(input.input_batch[0]) > 0
        - len(input.weights) > 0 and len(input.weights[0]) == len(input.input_batch[0])
        - input.bias is None or len(input.bias) == len(input.weights)
        - all matrix rows have uniform length and finite numeric entries
      postconditions:
        - len(output.output_batch) == len(input.input_batch)
        - len(output.output_batch[0]) == len(input.weights)
        - output.fan_in == len(input.weights[0])
        - output.fan_out == len(input.weights)
      certificate: Exact algebraic matrix-matrix multiplication with component-wise bias summation.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-04
        - ALGO-NN-08
        - ALGO-NN-10
      references:
        - "https://proceedings.mlr.press/v9/glorot10a.html"
        - "https://doi.org/10.1109/ICCV.2015.123"
        - "https://doi.org/search?q=lecun1998efficient"
    ---
    """

    @staticmethod
    def _compute_init_stats(
        fan_in: int,
        fan_out: int,
        mode: str,
    ) -> tuple[float, Optional[float]]:
        if mode == "glorot_uniform":
            var = 2.0 / float(fan_in + fan_out)
            bound = math.sqrt(3.0 * var)
            return var, bound
        elif mode == "glorot_normal":
            var = 2.0 / float(fan_in + fan_out)
            return var, None
        elif mode == "kaiming_uniform":
            var = 2.0 / float(fan_in)
            bound = math.sqrt(3.0 * var)
            return var, bound
        elif mode == "kaiming_normal":
            var = 2.0 / float(fan_in)
            return var, None
        elif mode == "lecun_uniform":
            var = 1.0 / float(fan_in)
            bound = math.sqrt(3.0 * var)
            return var, bound
        elif mode == "lecun_normal":
            var = 1.0 / float(fan_in)
            return var, None
        else:
            raise ValueError(f"Unsupported init_mode: {mode}")

    @staticmethod
    def forward(
        input_batch: Sequence[Sequence[float]],
        weights: Sequence[Sequence[float]],
        bias: Optional[Sequence[float]] = None,
        init_mode: Literal[
            "kaiming_uniform",
            "kaiming_normal",
            "glorot_uniform",
            "glorot_normal",
            "lecun_uniform",
            "lecun_normal",
        ] = "glorot_uniform",
    ) -> Dict[str, Any]:
        """
        Executes deterministic affine transformation Y = X W^T + b.
        """
        if not isinstance(input_batch, Sequence) or len(input_batch) == 0:
            raise ValueError("Precondition failed: len(input.input_batch) > 0")

        d_in = len(input_batch[0])
        if d_in == 0:
            raise ValueError("Precondition failed: len(input.input_batch[0]) > 0")

        batch_size = len(input_batch)
        for r_idx, row in enumerate(input_batch):
            if not isinstance(row, Sequence) or len(row) != d_in:
                raise ValueError(
                    f"Precondition failed: input_batch row {r_idx} length {len(row)} != expected d_in {d_in}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: input_batch[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        if not isinstance(weights, Sequence) or len(weights) == 0:
            raise ValueError("Precondition failed: len(input.weights) > 0")

        d_out = len(weights)
        for r_idx, row in enumerate(weights):
            if not isinstance(row, Sequence) or len(row) != d_in:
                raise ValueError(
                    f"Precondition failed: weights row {r_idx} length {len(row)} != expected d_in {d_in}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: weights[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        b_vec: List[float]
        if bias is not None:
            if not isinstance(bias, Sequence) or len(bias) != d_out:
                raise ValueError(
                    f"Precondition failed: len(input.bias) {len(bias)} != expected d_out {d_out}"
                )
            for b_idx, b_val in enumerate(bias):
                if not isinstance(b_val, (int, float)) or math.isnan(b_val) or math.isinf(b_val):
                    raise ValueError(
                        f"Precondition failed: bias[{b_idx}] is not finite ({b_val})"
                    )
            b_vec = [float(b) for b in bias]
        else:
            b_vec = [0.0] * d_out

        output_batch: List[List[float]] = []
        for b_i in range(batch_size):
            x_row = input_batch[b_i]
            y_row: List[float] = [0.0] * d_out
            for j in range(d_out):
                w_row = weights[j]
                dot = 0.0
                for k in range(d_in):
                    dot += float(x_row[k]) * float(w_row[k])
                y_row[j] = dot + b_vec[j]
            output_batch.append(y_row)

        var, bound = NnAlgoLinearAffineLayer._compute_init_stats(d_in, d_out, init_mode)

        return {
            "output_batch": output_batch,
            "fan_in": d_in,
            "fan_out": d_out,
            "batch_size": batch_size,
            "theoretical_variance": var,
            "theoretical_bound": bound,
        }
