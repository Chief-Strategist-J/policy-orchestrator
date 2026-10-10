from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoSharpnessAwareMinimization:
    """
    ---
    contract:
      algo_id: ALGO-NN-41
      name: NnAlgoSharpnessAwareMinimization
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.optimizer
      - nn.sam
      - nn.generalization
      - nn.flat_minima
      inputs:
        type: object
        properties:
          parameters:
            type: array
            items:
              type: number
            description: Base parameter coordinates theta of length P.
          base_gradients:
            type: array
            items:
              type: number
            description: Unperturbed gradient vector nabla L(theta) of length P.
          perturbed_gradients:
            type: array
            items:
              type: number
            description: Gradient vector evaluated at perturbed coordinates nabla L(theta
              + eps) of length P.
          rho:
            type: number
            default: 0.05
            description: Neighborhood perturbation radius rho > 0.
          lr:
            type: number
            default: 0.01
            description: Step size eta > 0.
        required:
        - parameters
        - base_gradients
        - perturbed_gradients
        additionalProperties: false
      outputs:
        type: object
        properties:
          adversarial_perturbation:
            type: array
            items:
              type: number
            description: Computed adversarial epsilon perturbation of length P.
          updated_parameters:
            type: array
            items:
              type: number
            description: Updated parameter vector theta_{t+1} of length P.
        required:
        - adversarial_perturbation
        - updated_parameters
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
        base_gradients: Sequence[float],
        perturbed_gradients: Sequence[float],
        rho: float = 0.05,
        lr: float = 0.01,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0 or len(base_gradients) != p or len(perturbed_gradients) != p:
            raise ValueError("Precondition failed: buffers must have identical non-zero length P.")
        if rho <= 0.0 or lr <= 0.0:
            raise ValueError("Precondition failed: rho and lr must be > 0.")

        g_norm = math.sqrt(sum(g ** 2 for g in base_gradients))
        scale = rho / (g_norm + 1e-12)

        eps_perturbation = [g * scale for g in base_gradients]
        updated_params = [theta - lr * g_pert for theta, g_pert in zip(parameters, perturbed_gradients)]

        return {
            "adversarial_perturbation": eps_perturbation,
            "updated_parameters": updated_params,
        }
