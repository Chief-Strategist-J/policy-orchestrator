from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Sequence


class NnAlgoSigmoidTanh:
    """
    ---
    contract:
      algo_id: ALGO-NN-06
      name: NnAlgoSigmoidTanh
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.activation
        - nn.sigmoid
        - nn.tanh
        - nn.saturation_detection
        - nn.log_sigmoid
      inputs:
        type: object
        properties:
          input_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D input pre-activation tensor of shape (N, D).
          variant:
            type: string
            enum:
              - sigmoid
              - tanh
              - log_sigmoid
              - hard_sigmoid
              - hard_tanh
            default: sigmoid
            description: Specific S-shaped bounded activation function.
          saturation_threshold:
            type: number
            default: 0.01
            description: Gradient magnitude threshold below which a unit is flagged as saturated.
        required:
          - input_tensor
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
            description: Activated 2D tensor of shape (N, D).
          gradients:
            type: array
            items:
              type: array
              items:
                type: number
            description: Local analytic first derivatives d(act)/d(input) of shape (N, D).
          saturated_fraction:
            type: number
            description: Fraction of elements whose derivative is strictly below saturation_threshold.
          mean_gradient:
            type: number
            description: Mean analytical gradient magnitude across the entire tensor.
          shape:
            type: array
            items:
              type: integer
            description: Tensor dimensions [N, D].
        required:
          - output_tensor
          - gradients
          - saturated_fraction
          - mean_gradient
          - shape
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - input_tensor is a non-empty 2D array of finite numbers
        - all rows have uniform length
        - saturation_threshold is a positive finite number
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
          N: number of rows / batch size
          D: feature dimension
        time_worst: O(N * D)
        time_typical: O(N * D)
        space: O(N * D)
      preconditions:
        - len(input.input_tensor) > 0 and len(input.input_tensor[0]) > 0
        - all rows in input_tensor have identical length
        - all tensor values and threshold are finite
        - input.saturation_threshold > 0.0
      postconditions:
        - len(output.output_tensor) == len(input.input_tensor)
        - len(output.output_tensor[0]) == len(input.input_tensor[0])
        - 0.0 <= output.saturated_fraction <= 1.0
        - output.mean_gradient >= 0.0
      certificate: Exact algebraic verification of bounded activations and logistic derivative relationships.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-03
        - ALGO-NN-04
        - ALGO-NN-07
      references:
        - hochreiter1997long
        - lecun1998efficient
        - glorot2010understanding
    ---
    """

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[float]],
        variant: Literal["sigmoid", "tanh", "log_sigmoid", "hard_sigmoid", "hard_tanh"] = "sigmoid",
        saturation_threshold: float = 0.01,
    ) -> Dict[str, Any]:
        if not isinstance(input_tensor, Sequence) or len(input_tensor) == 0:
            raise ValueError("Precondition failed: len(input.input_tensor) > 0")

        d = len(input_tensor[0])
        if d == 0:
            raise ValueError("Precondition failed: len(input.input_tensor[0]) > 0")

        n = len(input_tensor)
        for r_idx, row in enumerate(input_tensor):
            if not isinstance(row, Sequence) or len(row) != d:
                raise ValueError(
                    f"Precondition failed: input_tensor row {r_idx} length {len(row)} != expected {d}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: input_tensor[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        if not isinstance(saturation_threshold, (int, float)) or math.isnan(saturation_threshold) or math.isinf(saturation_threshold) or saturation_threshold <= 0.0:
            raise ValueError("Precondition failed: input.saturation_threshold > 0.0 and finite")

        output_tensor: List[List[float]] = []
        gradients: List[List[float]] = []
        total_elements = n * d
        saturated_count = 0
        total_grad_sum = 0.0

        for r_idx in range(n):
            row = input_tensor[r_idx]
            out_row: List[float] = [0.0] * d
            grad_row: List[float] = [0.0] * d

            for c_idx in range(d):
                x = float(row[c_idx])

                if variant == "sigmoid":
                    if x >= 40.0:
                        sig = 1.0
                    elif x <= -40.0:
                        sig = 0.0
                    else:
                        sig = 1.0 / (1.0 + math.exp(-x))
                    out_val = sig
                    grad_val = sig * (1.0 - sig)

                elif variant == "tanh":
                    t = math.tanh(x)
                    out_val = t
                    grad_val = 1.0 - t * t

                elif variant == "log_sigmoid":
                    if x >= 0.0:
                        out_val = -math.log1p(math.exp(-x))
                        grad_val = 1.0 / (1.0 + math.exp(x))
                    else:
                        out_val = x - math.log1p(math.exp(x))
                        grad_val = 1.0 / (1.0 + math.exp(-x))

                elif variant == "hard_sigmoid":
                    val = 0.2 * x + 0.5
                    if val <= 0.0:
                        out_val = 0.0
                        grad_val = 0.0
                    elif val >= 1.0:
                        out_val = 1.0
                        grad_val = 0.0
                    else:
                        out_val = val
                        grad_val = 0.2

                elif variant == "hard_tanh":
                    if x <= -1.0:
                        out_val = -1.0
                        grad_val = 0.0
                    elif x >= 1.0:
                        out_val = 1.0
                        grad_val = 0.0
                    else:
                        out_val = x
                        grad_val = 1.0

                else:
                    raise ValueError(f"Unsupported variant: {variant}")

                out_row[c_idx] = out_val
                grad_row[c_idx] = grad_val
                total_grad_sum += grad_val

                if abs(grad_val) < saturation_threshold:
                    saturated_count += 1

            output_tensor.append(out_row)
            gradients.append(grad_row)

        return {
            "output_tensor": output_tensor,
            "gradients": gradients,
            "saturated_fraction": saturated_count / float(total_elements),
            "mean_gradient": total_grad_sum / float(total_elements),
            "shape": [n, d],
        }
