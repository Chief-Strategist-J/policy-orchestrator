from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoGatedLinearUnits:
    """
    ---
    contract:
      algo_id: ALGO-NN-08
      name: NnAlgoGatedLinearUnits
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.gated_linear_units
        - nn.swiglu
        - nn.geglu
        - nn.reglu
        - nn.glu
        - nn.feedforward_block
      inputs:
        type: object
        properties:
          input_batch:
            type: array
            items:
              type: array
              items:
                type: number
            description: Input feature matrix X of shape (B, d_in).
          weights_gate:
            type: array
            items:
              type: array
              items:
                type: number
            description: Gate projection weight matrix W_gate (or W_2) of shape (d_hidden, d_in).
          weights_up:
            type: array
            items:
              type: array
              items:
                type: number
            description: Up projection weight matrix W_up (or W_1) of shape (d_hidden, d_in).
          weights_down:
            type: array
            items:
              type: array
              items:
                type: number
            description: Optional down projection weight matrix W_down (or W_3) of shape (d_out, d_hidden).
          variant:
            type: string
            enum:
              - swiglu
              - geglu
              - reglu
              - glu
            default: swiglu
            description: Specific gating activation function.
        required:
          - input_batch
          - weights_gate
          - weights_up
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
            description: Gated transformed batch of shape (B, d_out) or (B, d_hidden) if weights_down is null.
          gate_activations:
            type: array
            items:
              type: array
              items:
                type: number
            description: Activated gate matrix act(X W_gate^T) of shape (B, d_hidden).
          gated_intermediate:
            type: array
            items:
              type: array
              items:
                type: number
            description: Elementwise product (X W_up^T) * act(X W_gate^T) of shape (B, d_hidden).
          parameter_budget_ratio:
            type: number
            description: Ratio of hidden dimension relative to standard MLP 4x expansion for equal parameter parity.
          dimensions:
            type: array
            items:
              type: integer
            description: Dimension summary [B, d_in, d_hidden, d_out].
        required:
          - output_batch
          - gate_activations
          - gated_intermediate
          - parameter_budget_ratio
          - dimensions
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - input_batch is a non-empty 2D array of shape (B, d_in)
        - weights_gate and weights_up both have shape (d_hidden, d_in)
        - weights_down if provided has shape (d_out, d_hidden)
        - all numerical entries are finite floating-point numbers
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
          d_h: hidden dimension
          d_out: output dimension
        time_worst: O(B * d_h * (2 * d_in + d_out))
        time_typical: O(B * d_h * (2 * d_in + d_out))
        space: O(B * (d_h + d_out))
      preconditions:
        - len(input.input_batch) > 0 and len(input.input_batch[0]) > 0
        - len(input.weights_gate) > 0 and len(input.weights_gate[0]) == len(input.input_batch[0])
        - len(input.weights_up) == len(input.weights_gate) and len(input.weights_up[0]) == len(input.weights_gate[0])
        - input.weights_down is None or (len(input.weights_down) > 0 and len(input.weights_down[0]) == len(input.weights_gate))
      postconditions:
        - len(output.output_batch) == len(input.input_batch)
        - len(output.gate_activations[0]) == len(input.weights_gate)
        - len(output.gated_intermediate[0]) == len(input.weights_gate)
      certificate: Algebraic verification of bilinear Hadamard product (X W_up^T) * act(X W_gate^T).
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-03
        - ALGO-NN-04
        - ALGO-NN-05
        - ALGO-NN-06
      references:
        - "https://doi.org/search?q=dauphin2017language"
        - "https://doi.org/search?q=shazeer2020glu"
        - "https://doi.org/search?q=touvron2023llama"
    ---
    """

    @staticmethod
    def _act(x: float, variant: str) -> float:
        if variant == "swiglu":
            if x >= 40.0:
                sig = 1.0
            elif x <= -40.0:
                sig = 0.0
            else:
                sig = 1.0 / (1.0 + math.exp(-x))
            return x * sig
        elif variant == "geglu":
            phi = 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
            return x * phi
        elif variant == "reglu":
            return x if x > 0.0 else 0.0
        elif variant == "glu":
            if x >= 40.0:
                return 1.0
            elif x <= -40.0:
                return 0.0
            return 1.0 / (1.0 + math.exp(-x))
        else:
            raise ValueError(f"Unsupported variant: {variant}")

    @staticmethod
    def forward(
        input_batch: Sequence[Sequence[float]],
        weights_gate: Sequence[Sequence[float]],
        weights_up: Sequence[Sequence[float]],
        weights_down: Optional[Sequence[Sequence[float]]] = None,
        variant: Literal["swiglu", "geglu", "reglu", "glu"] = "swiglu",
    ) -> Dict[str, Any]:
        if not isinstance(input_batch, Sequence) or len(input_batch) == 0:
            raise ValueError("Precondition failed: len(input.input_batch) > 0")

        d_in = len(input_batch[0])
        if d_in == 0:
            raise ValueError("Precondition failed: len(input.input_batch[0]) > 0")

        b = len(input_batch)
        for r_idx, row in enumerate(input_batch):
            if not isinstance(row, Sequence) or len(row) != d_in:
                raise ValueError(
                    f"Precondition failed: input_batch row {r_idx} length {len(row)} != expected {d_in}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: input_batch[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        if not isinstance(weights_gate, Sequence) or len(weights_gate) == 0:
            raise ValueError("Precondition failed: len(input.weights_gate) > 0")

        d_h = len(weights_gate)
        for r_idx, row in enumerate(weights_gate):
            if not isinstance(row, Sequence) or len(row) != d_in:
                raise ValueError(
                    f"Precondition failed: weights_gate row {r_idx} length {len(row)} != expected {d_in}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: weights_gate[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        if not isinstance(weights_up, Sequence) or len(weights_up) != d_h:
            raise ValueError(
                f"Precondition failed: len(input.weights_up) {len(weights_up) if isinstance(weights_up, Sequence) else 0} != d_h {d_h}"
            )

        for r_idx, row in enumerate(weights_up):
            if not isinstance(row, Sequence) or len(row) != d_in:
                raise ValueError(
                    f"Precondition failed: weights_up row {r_idx} length {len(row)} != expected {d_in}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: weights_up[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        d_out = d_h
        if weights_down is not None:
            if not isinstance(weights_down, Sequence) or len(weights_down) == 0:
                raise ValueError("Precondition failed: weights_down must be non-empty when provided")
            d_out = len(weights_down)
            for r_idx, row in enumerate(weights_down):
                if not isinstance(row, Sequence) or len(row) != d_h:
                    raise ValueError(
                        f"Precondition failed: weights_down row {r_idx} length {len(row)} != expected d_h {d_h}"
                    )
                for c_idx, val in enumerate(row):
                    if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                        raise ValueError(
                            f"Precondition failed: weights_down[{r_idx}][{c_idx}] is not finite ({val})"
                        )

        gate_activations: List[List[float]] = []
        gated_intermediate: List[List[float]] = []
        output_batch: List[List[float]] = []

        for b_i in range(b):
            x_row = input_batch[b_i]
            gate_row: List[float] = [0.0] * d_h
            inter_row: List[float] = [0.0] * d_h

            for j in range(d_h):
                dot_g = 0.0
                dot_u = 0.0
                w_g_row = weights_gate[j]
                w_u_row = weights_up[j]
                for k in range(d_in):
                    xk = float(x_row[k])
                    dot_g += xk * float(w_g_row[k])
                    dot_u += xk * float(w_u_row[k])

                act_g = NnAlgoGatedLinearUnits._act(dot_g, variant)
                gate_row[j] = act_g
                inter_row[j] = dot_u * act_g

            gate_activations.append(gate_row)
            gated_intermediate.append(inter_row)

            if weights_down is not None:
                out_row: List[float] = [0.0] * d_out
                for o_idx in range(d_out):
                    w_d_row = weights_down[o_idx]
                    dot_d = 0.0
                    for j in range(d_h):
                        dot_d += inter_row[j] * float(w_d_row[j])
                    out_row[o_idx] = dot_d
                output_batch.append(out_row)
            else:
                output_batch.append(inter_row)

        param_budget_ratio = (2.0 / 3.0)

        return {
            "output_batch": output_batch,
            "gate_activations": gate_activations,
            "gated_intermediate": gated_intermediate,
            "parameter_budget_ratio": param_budget_ratio,
            "dimensions": [b, d_in, d_h, d_out],
        }
