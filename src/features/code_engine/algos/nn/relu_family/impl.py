from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoReluFamily:
    """
    ---
    contract:
      algo_id: ALGO-NN-04
      name: NnAlgoReluFamily
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.activation
        - nn.relu
        - nn.leaky_relu
        - nn.prelu
        - nn.elu
        - nn.selu
      inputs:
        type: object
        properties:
          input_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D input tensor of shape (N, D) representing pre-activations.
          variant:
            type: string
            enum:
              - relu
              - leaky_relu
              - prelu
              - elu
              - selu
            default: relu
            description: Specific non-linear activation variant within the ReLU family.
          alpha:
            type: number
            default: 0.01
            description: Slope parameter for negative inputs in leaky_relu and scale for elu.
          prelu_weights:
            type: array
            items:
              type: number
            description: Channel-wise learned slope parameters of length D for prelu variant.
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
          active_fraction:
            type: number
            description: Ratio of strictly positive activations (x > 0) across all tensor elements.
          dead_fraction:
            type: number
            description: Ratio of zero or saturating negative activations across all elements.
          shape:
            type: array
            items:
              type: integer
            description: Dimensions of output tensor [N, D].
        required:
          - output_tensor
          - gradients
          - active_fraction
          - dead_fraction
          - shape
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - input_tensor is a non-empty 2D array of finite numbers
        - alpha is finite and non-negative
        - if variant is prelu, prelu_weights must have length matching tensor feature dimension D
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
          N: batch size / number of rows
          D: feature dimension / number of columns
        time_worst: O(N * D)
        time_typical: O(N * D)
        space: O(N * D)
      preconditions:
        - len(input.input_tensor) > 0 and len(input.input_tensor[0]) > 0
        - all rows in input_tensor have identical length
        - all tensor values and alpha parameters are finite
        - if variant == 'prelu', len(input.prelu_weights) == len(input.input_tensor[0])
      postconditions:
        - len(output.output_tensor) == len(input.input_tensor)
        - len(output.output_tensor[0]) == len(input.input_tensor[0])
        - 0.0 <= output.active_fraction <= 1.0
        - 0.0 <= output.dead_fraction <= 1.0
        - abs((output.active_fraction + output.dead_fraction) - 1.0) < 1e-9
      certificate: Component-wise verification of piecewise continuous activation boundaries and analytic derivatives.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-03
        - ALGO-NN-05
        - ALGO-NN-06
      references:
        - "https://doi.org/search?q=nair2010rectified"
        - "https://doi.org/search?q=maas2013rectifier"
        - "https://doi.org/10.1109/ICCV.2015.123"
        - "https://doi.org/search?q=clevert2015fast"
        - "https://doi.org/search?q=klambauer2017self"
    ---
    """

    _SELU_LAMBDA = 1.0507009873554804934193349852946
    _SELU_ALPHA = 1.6732632423543772848170429916717

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[float]],
        variant: Literal["relu", "leaky_relu", "prelu", "elu", "selu"] = "relu",
        alpha: float = 0.01,
        prelu_weights: Optional[Sequence[float]] = None,
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

        if not isinstance(alpha, (int, float)) or math.isnan(alpha) or math.isinf(alpha):
            raise ValueError("Precondition failed: alpha must be a finite number")

        if variant == "prelu":
            if prelu_weights is None or len(prelu_weights) != d:
                raise ValueError(
                    f"Precondition failed: prelu_weights length {len(prelu_weights) if prelu_weights else 0} != expected dimension {d}"
                )
            for j, pw in enumerate(prelu_weights):
                if not isinstance(pw, (int, float)) or math.isnan(pw) or math.isinf(pw):
                    raise ValueError(
                        f"Precondition failed: prelu_weights[{j}] is not finite ({pw})"
                    )

        output_tensor: List[List[float]] = []
        gradients: List[List[float]] = []
        active_count = 0
        total_count = n * d

        for r_idx in range(n):
            row = input_tensor[r_idx]
            out_row: List[float] = [0.0] * d
            grad_row: List[float] = [0.0] * d

            for c_idx in range(d):
                x = float(row[c_idx])
                if variant == "relu":
                    if x > 0.0:
                        out_val = x
                        grad_val = 1.0
                        active_count += 1
                    else:
                        out_val = 0.0
                        grad_val = 0.0
                elif variant == "leaky_relu":
                    if x > 0.0:
                        out_val = x
                        grad_val = 1.0
                        active_count += 1
                    else:
                        out_val = alpha * x
                        grad_val = alpha
                elif variant == "prelu":
                    a_c = float(prelu_weights[c_idx])
                    if x > 0.0:
                        out_val = x
                        grad_val = 1.0
                        active_count += 1
                    else:
                        out_val = a_c * x
                        grad_val = a_c
                elif variant == "elu":
                    if x > 0.0:
                        out_val = x
                        grad_val = 1.0
                        active_count += 1
                    else:
                        exp_val = math.exp(max(x, -50.0))
                        out_val = alpha * (exp_val - 1.0)
                        grad_val = alpha * exp_val
                elif variant == "selu":
                    lam = NnAlgoReluFamily._SELU_LAMBDA
                    alp = NnAlgoReluFamily._SELU_ALPHA
                    if x > 0.0:
                        out_val = lam * x
                        grad_val = lam
                        active_count += 1
                    else:
                        exp_val = math.exp(max(x, -50.0))
                        out_val = lam * alp * (exp_val - 1.0)
                        grad_val = lam * alp * exp_val
                else:
                    raise ValueError(f"Unsupported variant: {variant}")

                out_row[c_idx] = out_val
                grad_row[c_idx] = grad_val

            output_tensor.append(out_row)
            gradients.append(grad_row)

        active_fraction = active_count / float(total_count)
        dead_fraction = 1.0 - active_fraction

        return {
            "output_tensor": output_tensor,
            "gradients": gradients,
            "active_fraction": active_fraction,
            "dead_fraction": dead_fraction,
            "shape": [n, d],
        }
