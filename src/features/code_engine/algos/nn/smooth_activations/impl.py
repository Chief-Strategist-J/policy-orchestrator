from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Sequence


class NnAlgoSmoothActivations:
    """
    ---
    contract:
      algo_id: ALGO-NN-05
      name: NnAlgoSmoothActivations
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.activation
        - nn.gelu
        - nn.silu
        - nn.swish
        - nn.mish
        - nn.smooth_activations
      inputs:
        type: object
        properties:
          input_tensor:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D tensor of shape (N, D) representing pre-activations.
          variant:
            type: string
            enum:
              - gelu_exact
              - gelu_tanh
              - silu
              - mish
            default: gelu_exact
            description: Specific non-monotonic smooth activation function.
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
            description: Analytic first derivatives d(act)/d(input) of shape (N, D).
          min_activation:
            type: number
            description: Minimum activation value across all tensor elements (demonstrating bounded negative dip).
          shape:
            type: array
            items:
              type: integer
            description: Dimensions of output tensor [N, D].
        required:
          - output_tensor
          - gradients
          - min_activation
          - shape
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - input_tensor is a non-empty 2D array of finite numbers
        - all rows have uniform length
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
        - all tensor values are finite floating-point numbers
      postconditions:
        - len(output.output_tensor) == len(input.input_tensor)
        - len(output.output_tensor[0]) == len(input.input_tensor[0])
        - output.min_activation >= -0.5
      certificate: Exact analytic calculation of smooth transcendental functions and derivatives.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-04
        - ALGO-NN-06
        - ALGO-NN-08
      references:
        - hendrycks2016gaussian
        - elfwing2018sigmoid
        - misra2019mish
    ---
    """

    _SQRT_2_OVER_PI = 0.7978845608028654
    _GELU_COEFF = 0.044715

    @staticmethod
    def _sigmoid(x: float) -> float:
        if x >= 40.0:
            return 1.0
        elif x <= -40.0:
            return 0.0
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def _softplus(x: float) -> float:
        if x > 30.0:
            return x
        elif x < -30.0:
            return math.exp(x)
        return math.log1p(math.exp(x))

    @staticmethod
    def forward(
        input_tensor: Sequence[Sequence[float]],
        variant: Literal["gelu_exact", "gelu_tanh", "silu", "mish"] = "gelu_exact",
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

        output_tensor: List[List[float]] = []
        gradients: List[List[float]] = []
        min_act = float("inf")

        for r_idx in range(n):
            row = input_tensor[r_idx]
            out_row: List[float] = [0.0] * d
            grad_row: List[float] = [0.0] * d

            for c_idx in range(d):
                x = float(row[c_idx])

                if variant == "gelu_exact":
                    phi = 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
                    pdf = (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x * x)
                    out_val = x * phi
                    grad_val = phi + x * pdf

                elif variant == "gelu_tanh":
                    u = NnAlgoSmoothActivations._SQRT_2_OVER_PI * (x + NnAlgoSmoothActivations._GELU_COEFF * (x**3))
                    tanh_u = math.tanh(u)
                    out_val = 0.5 * x * (1.0 + tanh_u)
                    sech2_u = 1.0 - tanh_u**2
                    du_dx = NnAlgoSmoothActivations._SQRT_2_OVER_PI * (1.0 + 3.0 * NnAlgoSmoothActivations._GELU_COEFF * (x**2))
                    grad_val = 0.5 * (1.0 + tanh_u) + 0.5 * x * sech2_u * du_dx

                elif variant == "silu":
                    sig = NnAlgoSmoothActivations._sigmoid(x)
                    out_val = x * sig
                    grad_val = sig + x * sig * (1.0 - sig)

                elif variant == "mish":
                    sp = NnAlgoSmoothActivations._softplus(x)
                    tanh_sp = math.tanh(sp)
                    out_val = x * tanh_sp
                    sig_x = NnAlgoSmoothActivations._sigmoid(x)
                    sech2_sp = 1.0 - tanh_sp**2
                    grad_val = tanh_sp + x * sech2_sp * sig_x

                else:
                    raise ValueError(f"Unsupported variant: {variant}")

                out_row[c_idx] = out_val
                grad_row[c_idx] = grad_val
                if out_val < min_act:
                    min_act = out_val

            output_tensor.append(out_row)
            gradients.append(grad_row)

        return {
            "output_tensor": output_tensor,
            "gradients": gradients,
            "min_activation": min_act,
            "shape": [n, d],
        }
