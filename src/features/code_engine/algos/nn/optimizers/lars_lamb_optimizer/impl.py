from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoLarsLambOptimizer:
    """
    ---
    contract:
      algo_id: ALGO-NN-37
      name: NnAlgoLarsLambOptimizer
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.optimizer
      - nn.lars
      - nn.lamb
      - nn.large_batch
      - nn.trust_ratio
      inputs:
        type: object
        properties:
          parameters:
            type: array
            items:
              type: number
            description: Parameter vector theta for a layer/tensor of length P.
          gradients:
            type: array
            items:
              type: number
            description: Gradient vector g of length P.
          mode:
            type: string
            enum:
            - lars
            - lamb
            default: lamb
            description: Large-batch optimizer algorithm (LARS vs LAMB).
          exp_avg:
            type: array
            items:
              type: number
            description: First moment buffer m of length P (for LAMB).
          exp_avg_sq:
            type: array
            items:
              type: number
            description: Second moment buffer v of length P (for LAMB).
          step:
            type: integer
            default: 1
            description: Current optimizer step t >= 1.
          lr:
            type: number
            default: 0.001
            description: Learning rate eta > 0.
          weight_decay:
            type: number
            default: 0.01
            description: Weight decay lambda >= 0.
          trust_coefficient:
            type: number
            default: 1.0
            description: Layer-wise trust coefficient phi > 0.
          eps:
            type: number
            default: 1.0e-08
            description: Numerical stability denominator epsilon > 0.
        required:
        - parameters
        - gradients
        additionalProperties: false
      outputs:
        type: object
        properties:
          updated_parameters:
            type: array
            items:
              type: number
            description: Updated parameter vector theta_{t+1} of length P.
          trust_ratio:
            type: number
            description: Computed layer-wise trust ratio r_t = ||theta|| / ||update||.
          updated_exp_avg:
            type: array
            items:
              type: number
            description: Updated first moment buffer m (for LAMB).
          updated_exp_avg_sq:
            type: array
            items:
              type: number
            description: Updated second moment buffer v (for LAMB).
        required:
        - updated_parameters
        - trust_ratio
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
        parameters: Sequence[float],
        gradients: Sequence[float],
        mode: Literal["lars", "lamb"] = "lamb",
        exp_avg: Optional[Sequence[float]] = None,
        exp_avg_sq: Optional[Sequence[float]] = None,
        step: int = 1,
        lr: float = 0.001,
        weight_decay: float = 0.01,
        trust_coefficient: float = 1.0,
        eps: float = 1e-8,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(gradients) != p:
            raise ValueError("Precondition failed: parameters and gradients must have identical non-zero length.")

        w_norm = math.sqrt(sum(w ** 2 for w in parameters))
        new_m: List[float] = []
        new_v: List[float] = []
        raw_updates: List[float] = []

        if mode == "lamb":
            m_buf = exp_avg if exp_avg is not None else [0.0] * p
            v_buf = exp_avg_sq if exp_avg_sq is not None else [0.0] * p
            beta1, beta2 = 0.9, 0.999
            bc1 = 1.0 - (beta1 ** step)
            bc2 = 1.0 - (beta2 ** step)

            for theta, g, m, v in zip(parameters, gradients, m_buf, v_buf):
                m_next = beta1 * m + (1.0 - beta1) * g
                v_next = beta2 * v + (1.0 - beta2) * (g ** 2)
                m_hat = m_next / bc1
                v_hat = v_next / bc2
                r_update = (m_hat / (math.sqrt(v_hat) + eps)) + weight_decay * theta
                raw_updates.append(r_update)
                new_m.append(m_next)
                new_v.append(v_next)
        else:
            for theta, g in zip(parameters, gradients):
                r_update = g + weight_decay * theta
                raw_updates.append(r_update)

        u_norm = math.sqrt(sum(u ** 2 for u in raw_updates))
        if w_norm > 0.0 and u_norm > 0.0:
            trust_ratio = trust_coefficient * (w_norm / u_norm)
        else:
            trust_ratio = 1.0

        new_params = [theta - lr * trust_ratio * u for theta, u in zip(parameters, raw_updates)]

        res: Dict[str, Any] = {
            "updated_parameters": new_params,
            "trust_ratio": trust_ratio,
        }
        if mode == "lamb":
            res["updated_exp_avg"] = new_m
            res["updated_exp_avg_sq"] = new_v
        return res
