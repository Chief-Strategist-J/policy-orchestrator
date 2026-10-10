from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoWeightTying:
    """
    ---
    contract:
      algo_id: ALGO-NN-12
      name: NnAlgoWeightTying
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.weight_tying
        - nn.embedding
        - nn.lm_head
        - nn.parameter_efficiency
        - nn.regularization
      inputs:
        type: object
        properties:
          hidden_states:
            type: array
            items:
              type: array
              items:
                type: number
            description: Final layer hidden states H of shape (B, D) where B is batch/tokens and D is model dimension.
          embedding_matrix:
            type: array
            items:
              type: array
              items:
                type: number
            description: Shared input embedding matrix E of shape (V, D) where V is vocabulary size.
          output_bias:
            type: array
            items:
              type: number
            description: Optional vocabulary logit bias vector b of length V.
          scale_by_sqrt_d:
            type: boolean
            default: false
            description: Whether to scale logits by 1/sqrt(D) (or sqrt(D)) before projection.
          mode:
            type: string
            enum:
              - tied_forward_logits
              - tied_gradient_accumulation
            default: tied_forward_logits
            description: Forward logit generation vs tied weight gradient accumulation across input and output paths.
          input_gradients:
            type: array
            items:
              type: array
              items:
                type: number
            description: Gradient of loss with respect to input embeddings dL/dE_in of shape (V, D).
          output_gradients:
            type: array
            items:
              type: array
              items:
                type: number
            description: Gradient of loss with respect to output projection weights dL/dE_out of shape (V, D).
        required:
          - hidden_states
          - embedding_matrix
        additionalProperties: false
      outputs:
        type: object
        properties:
          logits:
            type: array
            items:
              type: array
              items:
                type: number
            description: Output unnormalized vocabulary logits of shape (B, V).
          tied_gradients:
            type: array
            items:
              type: array
              items:
                type: number
            description: Accumulated total gradient dL/dE = dL/dE_in + dL/dE_out of shape (V, D).
          parameters_saved:
            type: integer
            description: Number of parameters saved by sharing the embedding matrix (V * D).
          vocabulary_size:
            type: integer
            description: Total vocabulary size V.
          embedding_dimension:
            type: integer
            description: Embedding dimension D.
        required:
          - logits
          - parameters_saved
          - vocabulary_size
          - embedding_dimension
        additionalProperties: false
      parameters: {}
      input_assumptions:
        - Embedding matrix E has shape (V, D) with V >= 1, D >= 1.
        - Hidden states H has shape (B, D) matching the column dimension of E.
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
          B: batch size / token count
          V: vocabulary size
          D: embedding dimension
        time_worst: O(B * V * D)
        time_typical: same
        space: O(B * V)
      preconditions:
        - len(input.hidden_states) > 0
        - len(input.embedding_matrix) > 0
        - len(input.hidden_states[0]) == len(input.embedding_matrix[0])
      postconditions:
        - len(output.logits) == len(input.hidden_states)
        - len(output.logits[0]) == len(input.embedding_matrix)
        - output.parameters_saved == len(input.embedding_matrix) * len(input.embedding_matrix[0])
      certificate: Exact transposition matrix product matching and parameter savings V * D.
      compatible_adapters:
        - ADAPTER-VECTOR-FEATURE-MATRIX
      related_algos:
        - ALGO-NN-03
        - ALGO-NN-09
      references:
        - "https://doi.org/search?q=press2017tying"
        - "https://doi.org/search?q=inan2016tying"
    ---
    """

    @staticmethod
    def forward(
        hidden_states: Sequence[Sequence[float]],
        embedding_matrix: Sequence[Sequence[float]],
        output_bias: Optional[Sequence[float]] = None,
        scale_by_sqrt_d: bool = False,
        mode: Literal["tied_forward_logits", "tied_gradient_accumulation"] = "tied_forward_logits",
        input_gradients: Optional[Sequence[Sequence[float]]] = None,
        output_gradients: Optional[Sequence[Sequence[float]]] = None,
    ) -> Dict[str, Any]:
        if not hidden_states or len(hidden_states) == 0:
            raise ValueError("Precondition failed: len(input.hidden_states) > 0")
        if not embedding_matrix or len(embedding_matrix) == 0:
            raise ValueError("Precondition failed: len(input.embedding_matrix) > 0")

        b_size = len(hidden_states)
        d_model = len(hidden_states[0])
        v_size = len(embedding_matrix)
        d_embed = len(embedding_matrix[0])

        if d_model != d_embed:
            raise ValueError(
                f"Precondition failed: hidden dimension {d_model} != embedding dimension {d_embed}"
            )

        if output_bias is not None and len(output_bias) != v_size:
            raise ValueError(
                f"Precondition failed: output_bias length {len(output_bias)} != vocabulary size {v_size}"
            )

        scale_factor = (1.0 / math.sqrt(d_model)) if scale_by_sqrt_d else 1.0
        logits: List[List[float]] = []

        for b in range(b_size):
            h_row = hidden_states[b]
            row_logits: List[float] = []
            for v in range(v_size):
                e_row = embedding_matrix[v]
                dot = sum(float(h_row[k]) * float(e_row[k]) for k in range(d_model))
                dot *= scale_factor
                if output_bias is not None:
                    dot += float(output_bias[v])
                row_logits.append(dot)
            logits.append(row_logits)

        tied_gradients: Optional[List[List[float]]] = None
        if mode == "tied_gradient_accumulation":
            if input_gradients is None or output_gradients is None:
                raise ValueError("Precondition failed: input_gradients and output_gradients required for accumulation")
            if len(input_gradients) != v_size or len(output_gradients) != v_size:
                raise ValueError("Precondition failed: gradient shape mismatch with vocabulary size")

            tied_gradients = []
            for v in range(v_size):
                grad_row = [
                    float(input_gradients[v][k]) + float(output_gradients[v][k])
                    for k in range(d_model)
                ]
                tied_gradients.append(grad_row)

        parameters_saved = v_size * d_model

        return {
            "logits": logits,
            "tied_gradients": tied_gradients,
            "parameters_saved": parameters_saved,
            "vocabulary_size": v_size,
            "embedding_dimension": d_model,
        }
