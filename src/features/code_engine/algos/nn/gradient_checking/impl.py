from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence


class NnAlgoGradientChecking:
    """
    ---
    contract:
      algo_id: ALGO-NN-26
      name: NnAlgoGradientChecking
      version: 1.0.0
      category: nn
      capability_tags:
      - nn.autodiff
      - nn.gradient_checking
      - nn.finite_differences
      - nn.verification
      inputs:
        type: object
        properties:
          parameters:
            type: array
            items:
              type: number
            description: Parameter coordinate vector theta of length P at which to evaluate
              gradients.
          analytic_gradients:
            type: array
            items:
              type: number
            description: Backpropagated analytic gradient vector g_analytic of length
              P.
          loss_values_plus:
            type: array
            items:
              type: number
            description: Perturbed forward loss values L(theta + epsilon * e_i) of length
              P.
          loss_values_minus:
            type: array
            items:
              type: number
            description: Perturbed forward loss values L(theta - epsilon * e_i) of length
              P.
          epsilon:
            type: number
            default: 1.0e-06
            description: Finite difference perturbation step epsilon > 0.
          tolerance:
            type: number
            default: 1.0e-05
            description: Relative error tolerance threshold for declaring gradient validity.
        required:
        - parameters
        - analytic_gradients
        - loss_values_plus
        - loss_values_minus
        additionalProperties: false
      outputs:
        type: object
        properties:
          is_correct:
            type: boolean
            description: Whether all relative errors satisfy relative_error <= tolerance.
          max_relative_error:
            type: number
            description: Maximum observed relative error across all parameters.
          numerical_gradients:
            type: array
            items:
              type: number
            description: Central finite difference estimated gradients g_num of length
              P.
          relative_errors:
            type: array
            items:
              type: number
            description: Per-coordinate relative errors of length P.
        required:
        - is_correct
        - max_relative_error
        - numerical_gradients
        - relative_errors
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
        analytic_gradients: Sequence[float],
        loss_values_plus: Sequence[float],
        loss_values_minus: Sequence[float],
        epsilon: float = 1e-6,
        tolerance: float = 1e-5,
    ) -> Dict[str, Any]:
        p = len(parameters)
        if p == 0:
            raise ValueError("Precondition failed: parameters list cannot be empty.")
        if len(analytic_gradients) != p or len(loss_values_plus) != p or len(loss_values_minus) != p:
            raise ValueError("Precondition failed: all input vectors must have identical length P.")
        if epsilon <= 0.0:
            raise ValueError(f"Precondition failed: epsilon must be > 0, got {epsilon}.")
        if tolerance <= 0.0:
            raise ValueError(f"Precondition failed: tolerance must be > 0, got {tolerance}.")

        numerical_grads: List[float] = []
        relative_errors: List[float] = []
        max_rel_error = 0.0
        all_passed = True

        for i in range(p):
            l_plus = loss_values_plus[i]
            l_minus = loss_values_minus[i]
            g_num = (l_plus - l_minus) / (2.0 * epsilon)
            g_ana = analytic_gradients[i]

            diff = abs(g_ana - g_num)
            scale = max(abs(g_ana), abs(g_num), 1e-8)
            rel_err = diff / scale

            numerical_grads.append(g_num)
            relative_errors.append(rel_err)

            if rel_err > max_rel_error:
                max_rel_error = rel_err
            if rel_err > tolerance:
                all_passed = False

        return {
            "is_correct": all_passed,
            "max_relative_error": max_rel_error,
            "numerical_gradients": numerical_grads,
            "relative_errors": relative_errors,
        }
