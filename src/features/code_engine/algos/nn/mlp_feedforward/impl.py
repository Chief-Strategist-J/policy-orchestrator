from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoMlpFeedforward:
    """
    ---
    contract:
      algo_id: ALGO-NN-02
      name: NnAlgoMlpFeedforward
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.mlp
        - nn.feedforward
        - nn.universal_approximation
      inputs:
        type: object
        properties:
          input_vector:
            type: array
            items:
              type: number
            description: Input feature vector x in R^d_in.
          weights:
            type: array
            items:
              type: array
              items:
                type: array
                items:
                  type: number
            description: List of weight matrices W^(l) of shape (d_out^(l), d_in^(l)) for each layer l = 1..L.
          biases:
            type: array
            items:
              type: array
              items:
                type: number
            description: List of bias vectors b^(l) of length d_out^(l) for each layer l = 1..L.
          hidden_activation:
            type: string
            enum:
              - relu
              - sigmoid
              - tanh
              - identity
            default: relu
            description: Activation function applied at hidden layers l = 1..L-1.
          output_activation:
            type: string
            enum:
              - identity
              - sigmoid
              - relu
              - tanh
            default: identity
            description: Activation function applied at the final output layer L.
        required:
          - input_vector
          - weights
          - biases
        additionalProperties: false
      outputs:
        type: object
        properties:
          output_vector:
            type: array
            items:
              type: number
            description: Final network activations h^(L) in R^d_out.
          layer_pre_activations:
            type: array
            items:
              type: array
              items:
                type: number
            description: Affine pre-activation vectors z^(l) for each layer l = 1..L.
          layer_activations:
            type: array
            items:
              type: array
              items:
                type: number
            description: Activated hidden state vectors h^(l) for each layer l = 1..L.
          num_layers:
            type: integer
            description: Number of affine layers L.
          layer_dimensions:
            type: array
            items:
              type: integer
            description: Sequence of layer widths [d_0, d_1, ..., d_L].
        required:
          - output_vector
          - layer_pre_activations
          - layer_activations
          - num_layers
          - layer_dimensions
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - input_vector is a non-empty finite 1D sequence of numbers
        - weights and biases contain L >= 1 layers
        - each weight matrix W^(l) has shape (d_out^(l), d_in^(l)) where d_in^(l) matches d_out^(l-1)
        - each bias vector b^(l) has length d_out^(l)
        - all floating-point numbers are finite (not NaN or Inf)
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
          L: number of layers
          d_l: dimension of layer l
          total_ops: sum_{l=1}^L d_l * d_{l-1}
        time_worst: O(sum_{l=1}^L d_l * d_{l-1})
        time_typical: O(sum_{l=1}^L d_l * d_{l-1})
        space: O(sum_{l=0}^L d_l)
      preconditions:
        - len(input.input_vector) > 0
        - len(input.weights) > 0
        - len(input.weights) == len(input.biases)
        - all weights and biases shapes match layer transitions
        - all inputs, weights, and biases contain finite numeric values
      postconditions:
        - len(output.output_vector) == len(input.biases[-1])
        - len(output.layer_activations) == len(input.weights)
        - len(output.layer_pre_activations) == len(input.weights)
        - len(output.layer_dimensions) == len(input.weights) + 1
      certificate: Exact layer-by-layer affine matrix-vector multiply and scalar non-linear evaluation.
      compatible_adapters: []
      related_algos:
        - ALGO-NN-01
        - ALGO-NN-03
        - ALGO-NN-04
        - ALGO-NN-06
      references:
        - cybenko1989approximation
        - hornik1991approximation
    ---
    """

    @staticmethod
    def _apply_activation(val: float, activation: str) -> float:
        if activation == "relu":
            return val if val > 0.0 else 0.0
        elif activation == "sigmoid":
            if val >= 40.0:
                return 1.0
            elif val <= -40.0:
                return 0.0
            return 1.0 / (1.0 + math.exp(-val))
        elif activation == "tanh":
            return math.tanh(val)
        elif activation == "identity":
            return val
        else:
            raise ValueError(f"Unsupported activation: {activation}")

    @staticmethod
    def forward(
        input_vector: Sequence[float],
        weights: Sequence[Sequence[Sequence[float]]],
        biases: Sequence[Sequence[float]],
        hidden_activation: Literal["relu", "sigmoid", "tanh", "identity"] = "relu",
        output_activation: Literal["identity", "sigmoid", "relu", "tanh"] = "identity",
    ) -> Dict[str, Any]:
        """
        Executes a deterministic forward pass of an L-layer Multilayer Perceptron.
        """
        # 1. Precondition validation
        if not isinstance(input_vector, Sequence) or len(input_vector) == 0:
            raise ValueError("Precondition failed: len(input.input_vector) > 0")

        for j, val in enumerate(input_vector):
            if not isinstance(val, (int, float)) or math.isnan(val) or math.isinf(val):
                raise ValueError(f"Precondition failed: input_vector[{j}] must be a finite number (got {val})")

        if not isinstance(weights, Sequence) or len(weights) == 0:
            raise ValueError("Precondition failed: len(input.weights) > 0")

        if not isinstance(biases, Sequence) or len(biases) != len(weights):
            raise ValueError(
                f"Precondition failed: len(input.weights) == len(input.biases) (got {len(weights)} vs {len(biases)})"
            )

        num_layers = len(weights)
        layer_dimensions: List[int] = [len(input_vector)]

        current_in_dim = len(input_vector)
        for l_idx in range(num_layers):
            w_l = weights[l_idx]
            b_l = biases[l_idx]

            if not isinstance(w_l, Sequence) or len(w_l) == 0:
                raise ValueError(f"Precondition failed: layer {l_idx} weight matrix must be non-empty")

            d_out = len(w_l)
            if not isinstance(b_l, Sequence) or len(b_l) != d_out:
                raise ValueError(
                    f"Precondition failed: layer {l_idx} bias length {len(b_l)} does not match output dimension {d_out}"
                )

            for r_idx, row in enumerate(w_l):
                if not isinstance(row, Sequence) or len(row) != current_in_dim:
                    raise ValueError(
                        f"Precondition failed: layer {l_idx} weight row {r_idx} length {len(row)} != expected in_dim {current_in_dim}"
                    )
                for c_idx, w_val in enumerate(row):
                    if not isinstance(w_val, (int, float)) or math.isnan(w_val) or math.isinf(w_val):
                        raise ValueError(
                            f"Precondition failed: layer {l_idx} weight ({r_idx}, {c_idx}) is not finite ({w_val})"
                        )

            for b_idx, b_val in enumerate(b_l):
                if not isinstance(b_val, (int, float)) or math.isnan(b_val) or math.isinf(b_val):
                    raise ValueError(
                        f"Precondition failed: layer {l_idx} bias ({b_idx}) is not finite ({b_val})"
                    )

            layer_dimensions.append(d_out)
            current_in_dim = d_out

        # 2. Forward Propagation
        current_activation: List[float] = [float(x) for x in input_vector]
        layer_pre_activations: List[List[float]] = []
        layer_activations: List[List[float]] = []

        for l_idx in range(num_layers):
            w_l = weights[l_idx]
            b_l = biases[l_idx]
            d_out = len(w_l)
            is_last = l_idx == num_layers - 1
            act_func = output_activation if is_last else hidden_activation

            z_l: List[float] = [0.0] * d_out
            h_l: List[float] = [0.0] * d_out

            for i in range(d_out):
                dot = 0.0
                row = w_l[i]
                for j in range(len(current_activation)):
                    dot += float(row[j]) * current_activation[j]
                z_val = dot + float(b_l[i])
                z_l[i] = z_val
                h_l[i] = NnAlgoMlpFeedforward._apply_activation(z_val, act_func)

            layer_pre_activations.append(z_l)
            layer_activations.append(h_l)
            current_activation = h_l

        return {
            "output_vector": current_activation,
            "layer_pre_activations": layer_pre_activations,
            "layer_activations": layer_activations,
            "num_layers": num_layers,
            "layer_dimensions": layer_dimensions,
        }
