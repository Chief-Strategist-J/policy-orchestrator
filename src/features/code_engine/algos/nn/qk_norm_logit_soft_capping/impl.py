from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoQkNormLogitSoftCapping:
    """
    ---
    contract:
      algo_id: ALGO-NN-57
      name: NnAlgoQkNormLogitSoftCapping
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.normalization
        - nn.attention
        - nn.qk_norm
        - nn.soft_capping
        - nn.llm_stability
      inputs:
        type: object
        properties:
          queries:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D Query activation matrix Q of shape (N_q, D).
          keys:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D Key activation matrix K of shape (N_k, D).
          scale:
            type: number
            default: 0.0
            description: Attention temperature scaling factor (if <= 0, automatically computed as 1 / sqrt(D)).
          qk_norm:
            type: string
            enum:
              - none
              - rmsnorm
              - layernorm
            default: rmsnorm
            description: Normalization type applied to queries and keys across head dimension D.
          gamma:
            type: array
            items:
              type: number
            description: Learned gain parameter vector of length D (if empty, defaults to vector of 1.0s).
          soft_cap_threshold:
            type: number
            default: 50.0
            description: Soft-capping asymptote threshold c > 0 (if <= 0, soft-capping is disabled).
          eps:
            type: number
            default: 0.000001
            description: Numerical stability regularizer epsilon > 0.
        required:
          - queries
          - keys
      outputs:
        type: object
        properties:
          attention_logits:
            type: array
            items:
              type: array
              items:
                type: number
            description: Attention logit matrix of shape (N_q, N_k).
          normalized_queries:
            type: array
            items:
              type: array
              items:
                type: number
            description: Normalized query tensor of shape (N_q, D).
          normalized_keys:
            type: array
            items:
              type: array
              items:
                type: number
            description: Normalized key tensor of shape (N_k, D).
        required:
          - attention_logits
          - normalized_queries
          - normalized_keys
      parameters: {}
      input_assumptions:
        - queries must be a non-empty 2D array of shape (N_q, D) with N_q >= 1 and D >= 1.
        - keys must be a non-empty 2D array of shape (N_k, D) with matching head dimension D.
        - qk_norm must be one of ['none', 'rmsnorm', 'layernorm'].
        - If gamma is provided, its length must equal D.
        - eps must be strictly positive.
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: any
      exactness: exact
      error_bound: n/a
      uses_model: false
      complexity:
        variables:
          N_q: query sequence length
          N_k: key sequence length
          D: head dimension
        time_worst: O(N_q * D + N_k * D + N_q * N_k * D)
        time_typical: O(N_q * D + N_k * D + N_q * N_k * D)
        space: O(N_q * N_k + (N_q + N_k) * D)
      preconditions:
        - len(queries) > 0 and len(queries[0]) > 0
        - len(keys) > 0 and len(keys[0]) > 0
        - all(len(row) == len(queries[0]) for row in queries)
        - all(len(row) == len(queries[0]) for row in keys)
        - qk_norm in ["none", "rmsnorm", "layernorm"]
        - eps > 0
      postconditions:
        - len(output.attention_logits) == len(queries)
        - len(output.attention_logits[0]) == len(keys)
        - len(output.normalized_queries) == len(queries)
        - len(output.normalized_keys) == len(keys)
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-52
        - ALGO-NN-53
        - ALGO-NN-56
      references:
        - deghani2023scaling
        - gemma2024technical
    ---
    """

    @staticmethod
    def _norm_vector(
        vec: Sequence[float],
        norm_type: str,
        gamma: Sequence[float],
        eps: float,
    ) -> List[float]:
        D = len(vec)
        if norm_type == "none":
            return list(vec)
        elif norm_type == "rmsnorm":
            ms = sum(x * x for x in vec) / float(D)
            rms_val = math.sqrt(ms + eps)
            return [gamma[j] * (vec[j] / rms_val) for j in range(D)]
        elif norm_type == "layernorm":
            m = sum(vec) / float(D)
            v = sum((x - m) ** 2 for x in vec) / float(D)
            std_val = math.sqrt(v + eps)
            return [gamma[j] * ((vec[j] - m) / std_val) for j in range(D)]
        return list(vec)

    @staticmethod
    def compute(
        queries: Sequence[Sequence[float]],
        keys: Sequence[Sequence[float]],
        scale: float = 0.0,
        qk_norm: Literal["none", "rmsnorm", "layernorm"] = "rmsnorm",
        gamma: Optional[Sequence[float]] = None,
        soft_cap_threshold: float = 50.0,
        eps: float = 1e-6,
    ) -> Dict[str, Any]:
        if not queries or not queries[0]:
            raise ValueError("Precondition failed: queries must be non-empty 2D array.")
        if not keys or not keys[0]:
            raise ValueError("Precondition failed: keys must be non-empty 2D array.")

        N_q = len(queries)
        D = len(queries[0])
        N_k = len(keys)

        for row in queries:
            if len(row) != D:
                raise ValueError("Precondition failed: inconsistent row length in queries.")
        for row in keys:
            if len(row) != D:
                raise ValueError("Precondition failed: key dimension must match query dimension D.")

        if qk_norm not in ["none", "rmsnorm", "layernorm"]:
            raise ValueError("Precondition failed: qk_norm must be 'none', 'rmsnorm', or 'layernorm'.")
        if eps <= 0.0:
            raise ValueError("Precondition failed: eps must be strictly positive.")

        gamma_vec = list(gamma) if gamma is not None and len(gamma) > 0 else [1.0] * D
        if len(gamma_vec) != D:
            raise ValueError("Precondition failed: gamma length must match head dimension D.")

        eff_scale = scale if scale > 0.0 else (1.0 / math.sqrt(float(D)))

        # Normalize Queries and Keys
        norm_q = [
            NnAlgoQkNormLogitSoftCapping._norm_vector(queries[i], qk_norm, gamma_vec, eps)
            for i in range(N_q)
        ]
        norm_k = [
            NnAlgoQkNormLogitSoftCapping._norm_vector(keys[j], qk_norm, gamma_vec, eps)
            for j in range(N_k)
        ]

        # Compute dot-product logits
        logits: List[List[float]] = [[0.0] * N_k for _ in range(N_q)]
        for i in range(N_q):
            for j in range(N_k):
                raw_dot = sum(norm_q[i][d] * norm_k[j][d] for d in range(D))
                scaled_score = raw_dot * eff_scale

                if soft_cap_threshold > 0.0:
                    # Soft-capping: c * tanh(score / c)
                    capped_score = soft_cap_threshold * math.tanh(scaled_score / soft_cap_threshold)
                    logits[i][j] = capped_score
                else:
                    logits[i][j] = scaled_score

        return {
            "attention_logits": logits,
            "normalized_queries": norm_q,
            "normalized_keys": norm_k,
        }
