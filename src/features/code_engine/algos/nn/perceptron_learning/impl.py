from __future__ import annotations

import math
from typing import Any, Dict, List, Optional


class NnAlgoPerceptronLearning:
    """
    ---
    contract:
      algo_id: ALGO-NN-01
      name: NnAlgoPerceptronLearning
      version: 1.0.0
      category: nn
      capability_tags:
        - neural_network
        - classification
        - linear_model
        - supervised_learning
        - perceptron
      inputs:
        type: object
        required:
          - features
          - labels
        properties:
          features:
            type: array
            items:
              type: array
              items:
                type: number
            description: 2D array of training feature vectors of shape (N, d).
          labels:
            type: array
            items:
              type: integer
              enum: [0, 1]
            description: 1D array of binary target labels of length N (elements in {0, 1}).
          learning_rate:
            type: number
            default: 1.0
            minimum: 0.0
            exclusiveMinimum: true
            description: Learning rate eta > 0.
          max_epochs:
            type: integer
            default: 100
            minimum: 1
            description: Maximum number of training epochs E >= 1.
          initial_weights:
            type: array
            items:
              type: number
            description: Optional initial weight vector of dimension d.
          initial_bias:
            type: number
            description: Optional initial scalar bias.
      outputs:
        type: object
        required:
          - weights
          - bias
          - converged
          - epochs_trained
          - total_updates
          - final_error_count
          - margin
        properties:
          weights:
            type: array
            items:
              type: number
            description: Learned weight vector w of length d.
          bias:
            type: number
            description: Learned scalar bias b.
          converged:
            type: boolean
            description: True if all training samples are separated with zero error within max_epochs.
          epochs_trained:
            type: integer
            minimum: 1
            description: Number of epochs executed.
          total_updates:
            type: integer
            minimum: 0
            description: Total count of weight update steps performed across all epochs.
          final_error_count:
            type: integer
            minimum: 0
            description: Number of misclassified samples in the final epoch.
          margin:
            type:
              - number
              - "null"
            description: Geometric classification margin min_i y_i' (w . x_i + b) / ||w|| if converged else null.
      parameters: {}
      input_assumptions:
        - features is non-empty with uniform dimension d >= 1
        - labels length matches features length N >= 1
        - labels contain only binary values 0 or 1
        - learning_rate is a finite positive float
        - max_epochs is an integer >= 1
        - feature and weight values are finite real numbers
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "0 errors on linearly separable data within (R / gamma)^2 updates; bounded by max_epochs otherwise"
      uses_model: false
      complexity:
        variables:
          N: number of training samples
          d: dimension of input features
          E: number of epochs executed (bounded by max_epochs)
        time_worst: O(E * N * d)
        time_typical: O(E * N * d)
        space: O(d)
      preconditions:
        - len(input.features) > 0
        - len(input.features) == len(input.labels)
        - len(input.features[0]) > 0
        - all(len(row) == len(input.features[0]) for row in input.features)
        - all(all(not math.isnan(v) and not math.isinf(v) for v in row) for row in input.features)
        - all(y in (0, 1) for y in input.labels)
        - input.learning_rate > 0 and not math.isnan(input.learning_rate) and not math.isinf(input.learning_rate)
        - input.max_epochs >= 1
        - input.initial_weights is None or (len(input.initial_weights) == len(input.features[0]) and all(not math.isnan(v) and not math.isinf(v) for v in input.initial_weights))
        - input.initial_bias is None or (not math.isnan(input.initial_bias) and not math.isinf(input.initial_bias))
      postconditions:
        - len(output.weights) == len(input.features[0])
        - output.epochs_trained >= 1 and output.epochs_trained <= input.max_epochs
        - output.total_updates >= 0
        - output.final_error_count >= 0
        - (not output.converged) or (output.final_error_count == 0)
      certificate: "hyperplane separating all samples: for all i in [0..N-1], ((2*labels[i]-1) * (sum(weights[j]*features[i][j]) + bias)) >= 0 when converged is True"
      compatible_adapters:
        - ADAPTER-VECTOR-FEATURE-MATRIX
        - ADAPTER-BINARY-CLASSIFIER
      related_algos:
        - ALGO-NN-02
        - ALGO-CLASSICAL-ML-01
      references:
        - rosenblatt1958perceptron
        - novikoff1962convergence
        - minsky1969perceptrons
    ---
    """

    @staticmethod
    def train(
        features: List[List[float]],
        labels: List[int],
        learning_rate: float = 1.0,
        max_epochs: int = 100,
        initial_weights: Optional[List[float]] = None,
        initial_bias: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Train a binary perceptron using Rosenblatt's mistake-driven learning rule.

        Parameters
        ----------
        features : List[List[float]]
            Training feature matrix of shape (N, d).
        labels : List[int]
            Binary ground-truth labels in {0, 1} of length N.
        learning_rate : float, default=1.0
            Gradient step multiplier eta > 0.
        max_epochs : int, default=100
            Maximum number of complete dataset passes E >= 1.
        initial_weights : Optional[List[float]], default=None
            Initial weight vector of dimension d. Defaults to all zeros.
        initial_bias : Optional[float], default=None
            Initial scalar bias. Defaults to 0.0.

        Returns
        -------
        Dict[str, Any]
            Dictionary containing learned weights, bias, convergence status,
            training metrics, and geometric margin.
        """
        # --- Precondition Validation ---
        if not features or len(features) == 0:
            raise ValueError("Precondition failed: len(input.features) > 0")

        if len(features) != len(labels):
            raise ValueError("Precondition failed: len(input.features) == len(input.labels)")

        d = len(features[0])
        if d == 0:
            raise ValueError("Precondition failed: len(input.features[0]) > 0")

        for i, row in enumerate(features):
            if len(row) != d:
                raise ValueError(
                    f"Precondition failed: all(len(row) == len(input.features[0])) (row {i} length {len(row)} != {d})"
                )
            for j, val in enumerate(row):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: feature values must be finite numbers (row {i}, col {j} is {val})"
                    )

        for i, y in enumerate(labels):
            if y not in (0, 1):
                raise ValueError(f"Precondition failed: all(y in (0, 1)) (labels[{i}] is {y})")

        if not isinstance(learning_rate, (int, float)) or learning_rate <= 0.0 or math.isnan(learning_rate) or math.isinf(learning_rate):
            raise ValueError("Precondition failed: input.learning_rate > 0 and finite")

        if not isinstance(max_epochs, int) or max_epochs < 1:
            raise ValueError("Precondition failed: input.max_epochs >= 1 (integer)")

        if initial_weights is not None:
            if len(initial_weights) != d:
                raise ValueError(
                    f"Precondition failed: len(input.initial_weights) == {d} (got {len(initial_weights)})"
                )
            for j, val in enumerate(initial_weights):
                if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                    raise ValueError(
                        f"Precondition failed: initial_weights must be finite (index {j} is {val})"
                    )
            weights: List[float] = [float(w) for w in initial_weights]
        else:
            weights = [0.0] * d

        if initial_bias is not None:
            if not isinstance(initial_bias, (int, float)) or math.isnan(initial_bias) or math.isinf(initial_bias):
                raise ValueError("Precondition failed: initial_bias must be a finite number")
            bias: float = float(initial_bias)
        else:
            bias = 0.0

        n_samples = len(features)
        total_updates = 0
        converged = False
        epochs_trained = 0
        final_error_count = 0

        # --- Training Loop ---
        for epoch in range(1, max_epochs + 1):
            epochs_trained = epoch
            epoch_errors = 0

            for i in range(n_samples):
                x = features[i]
                target = labels[i]

                # Activation: z = w . x + b
                z = sum(w_j * float(x_j) for w_j, x_j in zip(weights, x)) + bias
                y_hat = 1 if z > 0.0 else 0

                error = target - y_hat
                if error != 0:
                    epoch_errors += 1
                    total_updates += 1
                    # Perceptron update rule:
                    # w <- w + eta * (target - y_hat) * x
                    # b <- b + eta * (target - y_hat)
                    step = float(learning_rate) * float(error)
                    weights = [w_j + step * float(x_j) for w_j, x_j in zip(weights, x)]
                    bias = bias + step

            final_error_count = epoch_errors
            if epoch_errors == 0:
                converged = True
                break

        # --- Margin Calculation ---
        margin: Optional[float] = None
        if converged:
            norm_sq = sum(w_j * w_j for w_j in weights)
            if norm_sq > 0.0:
                norm_w = math.sqrt(norm_sq)
                margins: List[float] = []
                for i in range(n_samples):
                    x = features[i]
                    y = labels[i]
                    y_signed = 1.0 if y == 1 else -1.0
                    z = sum(w_j * float(x_j) for w_j, x_j in zip(weights, x)) + bias
                    margins.append((y_signed * z) / norm_w)
                margin = min(margins)

        return {
            "weights": weights,
            "bias": bias,
            "converged": converged,
            "epochs_trained": epochs_trained,
            "total_updates": total_updates,
            "final_error_count": final_error_count,
            "margin": margin,
        }
