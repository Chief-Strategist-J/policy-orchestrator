from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoMultitaskLossBalancing:
    """
    ---
    contract:
      algo_id: ALGO-NN-22
      name: NnAlgoMultitaskLossBalancing
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.loss
        - nn.multitask
        - nn.uncertainty_weighting
        - nn.gradnorm
        - nn.pcgrad
      inputs:
        type: object
        properties:
          losses:
            type: array
            items:
              type: number
            description: Individual task loss values L_k for K tasks.
          log_vars:
            type: array
            items:
              type: number
            description: Learned homoscedastic log-variance parameters s_k = log(sigma_k^2) for K tasks (for uncertainty mode).
          gradients:
            type: array
            items:
              type: array
              items:
                type: number
            description: Task gradient vectors G_k of shape (K, P) with respect to shared parameters (for PCGrad mode).
          mode:
            type: string
            enum:
              - uncertainty
              - pcgrad
            default: uncertainty
            description: Multi-task balancing algorithm to apply.
        required:
          - mode
        additionalProperties: false
      outputs:
        type: object
        properties:
          total_loss:
            type: number
            description: Scalar weighted combined multi-task loss (for uncertainty mode).
          effective_weights:
            type: array
            items:
              type: number
            description: Effective task weighting coefficients w_k of length K.
          projected_gradient:
            type: array
            items:
              type: number
            description: Aggregated conflict-free parameter gradient vector of length P (for PCGrad mode).
        required:
          - effective_weights
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        mode: Literal["uncertainty", "pcgrad"] = "uncertainty",
        losses: Optional[Sequence[float]] = None,
        log_vars: Optional[Sequence[float]] = None,
        gradients: Optional[Sequence[Sequence[float]]] = None,
    ) -> Dict[str, Any]:
        if mode == "uncertainty":
            if losses is None or log_vars is None:
                raise ValueError("Precondition failed: uncertainty mode requires losses and log_vars.")
            k = len(losses)
            if k == 0 or len(log_vars) != k:
                raise ValueError("Precondition failed: losses and log_vars must have matching non-zero length K.")

            total_loss = 0.0
            weights: List[float] = []

            for l_k, s_k in zip(losses, log_vars):
                if l_k < 0.0:
                    raise ValueError(f"Precondition failed: task loss must be non-negative, got {l_k}.")
                # Loss = exp(-s_k) * L_k + 0.5 * s_k
                w_k = math.exp(-s_k)
                weights.append(w_k)
                total_loss += (w_k * l_k + 0.5 * s_k)

            return {
                "total_loss": total_loss,
                "effective_weights": weights,
            }

        elif mode == "pcgrad":
            if gradients is None or len(gradients) == 0:
                raise ValueError("Precondition failed: pcgrad mode requires non-empty gradients matrix.")
            k = len(gradients)
            p = len(gradients[0])

            # Copy gradients
            g_proj = [[float(v) for v in row] for row in gradients]

            for i in range(k):
                for j in range(k):
                    if i != j:
                        # Compute dot product <g_i, g_j>
                        dot = sum(g_proj[i][idx] * gradients[j][idx] for idx in range(p))
                        if dot < 0.0:
                            # Project g_i onto normal plane of g_j: g_i = g_i - (dot / ||g_j||^2) * g_j
                            norm_sq = sum(gradients[j][idx] ** 2 for idx in range(p)) + 1e-12
                            scale = dot / norm_sq
                            for idx in range(p):
                                g_proj[i][idx] -= scale * gradients[j][idx]

            # Aggregate final gradient: sum across all tasks
            final_grad = [sum(g_proj[i][idx] for i in range(k)) for idx in range(p)]

            return {
                "effective_weights": [1.0] * k,
                "projected_gradient": final_grad,
            }
        else:
            raise ValueError(f"Precondition failed: unrecognized mode {mode}")
