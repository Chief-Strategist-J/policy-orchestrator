from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoEarlyStoppingCheckpointing:
    """
    ---
    contract:
      algo_id: ALGO-NN-60
      name: NnAlgoEarlyStoppingCheckpointing
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.regularization
        - nn.early_stopping
        - nn.checkpointing
        - nn.model_averaging
      inputs:
        type: object
        properties:
          validation_history:
            type: array
            items:
              type: number
            description: Sequential array of validation metric evaluations across training checkpoints.
          checkpoint_weights:
            type: array
            items:
              type: array
              items:
                type: number
            description: List of flattened parameter weight vectors corresponding to each evaluation step.
          patience:
            type: integer
            default: 3
            description: Number of consecutive evaluations without improvement before stopping.
          min_delta:
            type: number
            default: 0.0001
            description: Minimum absolute change in metric to qualify as an improvement.
          mode:
            type: string
            enum:
              - min
              - max
            default: min
            description: Metric optimization direction ('min' for loss/error, 'max' for accuracy/score).
          top_k_average:
            type: integer
            default: 1
            description: Number of top-performing checkpoints to average for final ensemble weights.
        required:
          - validation_history
          - checkpoint_weights
      outputs:
        type: object
        properties:
          best_step:
            type: integer
            description: 0-indexed step corresponding to the best validation performance.
          best_metric:
            type: number
            description: Best recorded validation metric value.
          stopped_step:
            type: integer
            description: Step at which training terminated (either early stopped or finished).
          is_early_stopped:
            type: boolean
            description: True if training was halted before exhausting validation history due to patience exhaustion.
          selected_checkpoint:
            type: array
            items:
              type: number
            description: Weights of the single best checkpoint.
          averaged_checkpoint:
            type: array
            items:
              type: number
            description: Parameter weights averaged across top-K checkpoints.
        required:
          - best_step
          - best_metric
          - stopped_step
          - is_early_stopped
          - selected_checkpoint
          - averaged_checkpoint
      parameters: {}
      input_assumptions:
        - validation_history must be a non-empty 1D array of numbers.
        - checkpoint_weights must be a non-empty 2D array with length matching validation_history and uniform parameter dimension P >= 1.
        - patience must be >= 1.
        - min_delta must be >= 0.0.
        - top_k_average must satisfy 1 <= top_k_average <= len(validation_history).
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
          N: number of evaluation steps
          P: parameter count in checkpoint
          K: top-K checkpoints to average
        time_worst: O(N * P + N log N)
        time_typical: O(N * P)
        space: O(P)
      preconditions:
        - len(validation_history) > 0
        - len(checkpoint_weights) == len(validation_history)
        - len(checkpoint_weights[0]) > 0
        - all(len(w) == len(checkpoint_weights[0]) for w in checkpoint_weights)
        - patience >= 1
        - min_delta >= 0.0
        - mode in ["min", "max"]
        - 1 <= top_k_average <= len(validation_history)
      postconditions:
        - 0 <= output.best_step < len(validation_history)
        - 0 <= output.stopped_step < len(validation_history)
        - len(output.selected_checkpoint) == len(checkpoint_weights[0])
        - len(output.averaged_checkpoint) == len(checkpoint_weights[0])
      certificate: none
      compatible_adapters: []
      related_algos:
        - ALGO-NN-58
        - ALGO-NN-60
      references:
        - prechelt1998early
        - izmailov2018averaging
    ---
    """

    @staticmethod
    def evaluate_and_select(
        validation_history: Sequence[float],
        checkpoint_weights: Sequence[Sequence[float]],
        patience: int = 3,
        min_delta: float = 1e-4,
        mode: Literal["min", "max"] = "min",
        top_k_average: int = 1,
    ) -> Dict[str, Any]:
        if not validation_history:
            raise ValueError("Precondition failed: validation_history must be non-empty.")
        N = len(validation_history)

        if len(checkpoint_weights) != N or not checkpoint_weights[0]:
            raise ValueError("Precondition failed: checkpoint_weights length must match validation_history.")
        P = len(checkpoint_weights[0])

        for w in checkpoint_weights:
            if len(w) != P:
                raise ValueError("Precondition failed: all checkpoint vectors must have identical length P.")

        if patience < 1:
            raise ValueError("Precondition failed: patience must be >= 1.")
        if min_delta < 0.0:
            raise ValueError("Precondition failed: min_delta must be >= 0.0.")
        if mode not in ["min", "max"]:
            raise ValueError("Precondition failed: mode must be 'min' or 'max'.")
        if not (1 <= top_k_average <= N):
            raise ValueError("Precondition failed: top_k_average must satisfy 1 <= K <= N.")

        best_metric = validation_history[0]
        best_step = 0
        bad_steps = 0
        stopped_step = N - 1
        is_early_stopped = False

        recorded_checkpoints: List[tuple[int, float]] = []

        for step in range(N):
            metric = validation_history[step]
            recorded_checkpoints.append((step, metric))

            improved = False
            if mode == "min":
                if metric < best_metric - min_delta:
                    improved = True
            else:
                if metric > best_metric + min_delta:
                    improved = True

            if improved:
                best_metric = metric
                best_step = step
                bad_steps = 0
            else:
                bad_steps += 1
                if bad_steps >= patience:
                    stopped_step = step
                    is_early_stopped = True
                    break

        selected_ckpt = [float(x) for x in checkpoint_weights[best_step]]

        # Sort evaluated checkpoints up to stopped_step
        evaluated = recorded_checkpoints[: stopped_step + 1]
        if mode == "min":
            evaluated.sort(key=lambda item: item[1])
        else:
            evaluated.sort(key=lambda item: item[1], reverse=True)

        k_eff = min(top_k_average, len(evaluated))
        top_k_steps = [item[0] for item in evaluated[:k_eff]]

        averaged_ckpt = [0.0] * P
        for step_idx in top_k_steps:
            for p in range(P):
                averaged_ckpt[p] += checkpoint_weights[step_idx][p]
        for p in range(P):
            averaged_ckpt[p] /= float(k_eff)

        return {
            "best_step": best_step,
            "best_metric": best_metric,
            "stopped_step": stopped_step,
            "is_early_stopped": is_early_stopped,
            "selected_checkpoint": selected_ckpt,
            "averaged_checkpoint": averaged_ckpt,
        }
