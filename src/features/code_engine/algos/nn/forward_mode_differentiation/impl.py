from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoForwardModeDifferentiation:
    """
    ---
    contract:
      algo_id: ALGO-NN-25
      name: NnAlgoForwardModeDifferentiation
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.autodiff
      - nn.forward_mode
      - nn.jvp
      - nn.dual_numbers
      inputs:
        type: object
        properties:
          primal_inputs:
            type: array
            items:
              type: number
            description: Input primal vector x of length N.
          tangent_inputs:
            type: array
            items:
              type: number
            description: Input perturbation tangent vector v of length N (direction for
              JVP).
          operations:
            type: array
            items:
              type: object
              properties:
                op:
                  type: string
                  enum:
                  - square
                  - sin
                  - exp
                  - relu
                  - linear_combination
                parent_indices:
                  type: array
                  items:
                    type: integer
                weights:
                  type: array
                  items:
                    type: number
            description: Sequence of forward primal-tangent operations.
        required:
        - primal_inputs
        - tangent_inputs
        additionalProperties: false
      outputs:
        type: object
        properties:
          primal_outputs:
            type: array
            items:
              type: number
            description: Evaluated primal outputs f(x).
          tangent_outputs:
            type: array
            items:
              type: number
            description: Evaluated directional derivative J * v (Jacobian-Vector Product).
        required:
        - primal_outputs
        - tangent_outputs
        additionalProperties: false
      parameters: {}
      input_assumptions:
      - Input tensors and parameters satisfy dimensionality and finite numerical bounds.
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: Standard IEEE-754 floating point precision
      uses_model: false
      complexity:
        variables:
          N: tensor/parameter dimension
        time_worst: O(N)
        time_typical: O(N)
        space: O(N)
      preconditions:
      - Input tensors are non-empty and conform to defined mathematical shapes.
      postconditions:
      - Output values and arrays are populated without NaN or infinite values.
      certificate: Exact implementation matching analytical mathematical derivation.
      compatible_adapters: []
      related_algos: []
      references:
      - https://arxiv.org/
    ---
    """

    @staticmethod
    def forward(
        primal_inputs: Sequence[float],
        tangent_inputs: Sequence[float],
        operations: Optional[Sequence[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        n = len(primal_inputs)
        if n == 0:
            raise ValueError("Precondition failed: primal_inputs cannot be empty.")
        if len(tangent_inputs) != n:
            raise ValueError(f"Precondition failed: tangent length ({len(tangent_inputs)}) must match primal length ({n}).")

        primals = list(primal_inputs)
        tangents = list(tangent_inputs)

        if operations is None or len(operations) == 0:
            out_p: List[float] = []
            out_t: List[float] = []
            for x, v in zip(primals, tangents):
                p_val = x ** 2 + math.sin(x)
                t_val = (2.0 * x + math.cos(x)) * v
                out_p.append(p_val)
                out_t.append(t_val)
            return {"primal_outputs": out_p, "tangent_outputs": out_t}

        for op_dict in operations:
            op = op_dict.get("op", "square")
            parents = op_dict.get("parent_indices", [0])
            w = op_dict.get("weights", [1.0] * len(parents))

            p0 = primals[parents[0]]
            t0 = tangents[parents[0]]

            if op == "square":
                p_new = p0 ** 2
                t_new = 2.0 * p0 * t0
            elif op == "sin":
                p_new = math.sin(p0)
                t_new = math.cos(p0) * t0
            elif op == "exp":
                p_new = math.exp(p0)
                t_new = p_new * t0
            elif op == "relu":
                p_new = max(0.0, p0)
                t_new = t0 if p0 > 0.0 else 0.0
            elif op == "linear_combination":
                p_new = sum(w[k] * primals[parents[k]] for k in range(len(parents)))
                t_new = sum(w[k] * tangents[parents[k]] for k in range(len(parents)))
            else:
                raise ValueError(f"Precondition failed: unsupported forward op {op}")

            primals.append(p_new)
            tangents.append(t_new)

        return {
            "primal_outputs": primals,
            "tangent_outputs": tangents,
        }
