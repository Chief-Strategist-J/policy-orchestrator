from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Sequence


class NnAlgoSoftmaxStable:
    """
    ---
    contract:
      algo_id: ALGO-NN-07
      name: NnAlgoSoftmaxStable
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.softmax
        - nn.log_softmax
        - nn.log_sum_exp
        - nn.online_softmax
        - nn.temperature_scaling
      inputs:
        type: object
        properties:
          logits:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D input tensor of unnormalized log-probability scores of shape (B, K).
          temperature:
            type: number
            default: 1.0
            description: Temperature parameter T > 0 controlling distribution entropy.
          mode:
            type: string
            enum:
              - standard_stable
              - log_softmax
              - online_streaming
            default: standard_stable
            description: Numerical algorithm mode for softmax computation.
        required:
          - logits
        additionalProperties: false
      outputs:
        type: object
        properties:
          probabilities:
            type: array
            items:
              type: array
              items:
                type: number
            description: Normalized probability distribution P (or log-probabilities if mode is log_softmax) of shape (B, K).
          log_sum_exp:
            type: array
            items:
              type: number
            description: Exact log-sum-exp scalar per row of length B.
          entropy:
            type: array
            items:
              type: number
            description: Shannon entropy H(P) = -sum(p * log(p)) in nats per row of length B.
          jacobian_diagonal:
            type: array
            items:
              type: array
              items:
                type: number
            description: Diagonal elements of the Softmax Jacobian matrix dp_i/dz_i = p_i * (1 - p_i) / T.
          batch_size:
            type: integer
            description: Number of batch items B.
          num_classes:
            type: integer
            description: Number of probability categories K.
        required:
          - probabilities
          - log_sum_exp
          - entropy
          - jacobian_diagonal
          - batch_size
          - num_classes
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - logits is a non-empty 2D array of finite numbers
        - temperature T is finite and strictly positive
        - each row contains K >= 1 classes
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
          B: batch size / number of rows
          K: number of classes / categories
        time_worst: O(B * K)
        time_typical: O(B * K)
        space: O(B * K)
      preconditions:
        - len(input.logits) > 0 and len(input.logits[0]) > 0
        - all rows in logits have identical length
        - all logits values are finite floating-point numbers
        - input.temperature > 0.0 and is finite
      postconditions:
        - len(output.probabilities) == len(input.logits)
        - len(output.probabilities[0]) == len(input.logits[0])
        - if mode != 'log_softmax', all(abs(sum(row) - 1.0) < 1e-6 for row in output.probabilities)
        - all(h >= -1e-9 for h in output.entropy)
      certificate: Exact row-wise probability normalization sum(p_i) == 1.0 and invariant log-sum-exp translation.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-02
        - ALGO-NN-06
        - ALGO-NN-08
      references:
        - bridle1990probabilistic
        - milakov2018online
        - dao2022flashattention
    ---
    """

    @staticmethod
    def forward(
        logits: Sequence[Sequence[float]],
        temperature: float = 1.0,
        mode: Literal["standard_stable", "log_softmax", "online_streaming"] = "standard_stable",
    ) -> Dict[str, Any]:
        if not isinstance(logits, Sequence) or len(logits) == 0:
            raise ValueError("Precondition failed: len(input.logits) > 0")

        k = len(logits[0])
        if k == 0:
            raise ValueError("Precondition failed: len(input.logits[0]) > 0")

        b = len(logits)
        for r_idx, row in enumerate(logits):
            if not isinstance(row, Sequence) or len(row) != k:
                raise ValueError(
                    f"Precondition failed: logits row {r_idx} length {len(row)} != expected {k}"
                )
            for c_idx, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: logits[{r_idx}][{c_idx}] is not finite ({val})"
                    )

        if not isinstance(temperature, (int, float)) or math.isnan(temperature) or math.isinf(temperature) or temperature <= 0.0:
            raise ValueError("Precondition failed: input.temperature > 0.0 and finite")

        inv_t = 1.0 / float(temperature)
        probabilities: List[List[float]] = []
        log_sum_exp_list: List[float] = []
        entropy_list: List[float] = []
        jacobian_diagonal: List[List[float]] = []

        for r_idx in range(b):
            row = [float(z) * inv_t for z in logits[r_idx]]

            if mode == "online_streaming":
                running_max = -float("inf")
                running_sum = 0.0
                for z in row:
                    if z > running_max:
                        running_sum = running_sum * math.exp(running_max - z) + 1.0
                        running_max = z
                    else:
                        running_sum += math.exp(z - running_max)
                m = running_max
                lse = m + math.log(running_sum)
            else:
                m = max(row)
                sum_exp = sum(math.exp(z - m) for z in row)
                lse = m + math.log(sum_exp)

            log_sum_exp_list.append(lse)

            out_row: List[float] = [0.0] * k
            jac_row: List[float] = [0.0] * k
            ent = 0.0

            if mode == "log_softmax":
                for j in range(k):
                    ls_val = row[j] - lse
                    out_row[j] = ls_val
                    p_val = math.exp(ls_val)
                    jac_row[j] = p_val * (1.0 - p_val) * inv_t
                    ent += -p_val * ls_val
            else:
                for j in range(k):
                    ls_val = row[j] - lse
                    p_val = math.exp(ls_val)
                    out_row[j] = p_val
                    jac_row[j] = p_val * (1.0 - p_val) * inv_t
                    if p_val > 1e-30:
                        ent += -p_val * math.log(p_val)

            probabilities.append(out_row)
            entropy_list.append(max(ent, 0.0))
            jacobian_diagonal.append(jac_row)

        return {
            "probabilities": probabilities,
            "log_sum_exp": log_sum_exp_list,
            "entropy": entropy_list,
            "jacobian_diagonal": jacobian_diagonal,
            "batch_size": b,
            "num_classes": k,
        }
