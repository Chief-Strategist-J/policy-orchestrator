from __future__ import annotations

import math
from typing import Any, Callable, Dict, List, Optional, Tuple


class NnAlgoBeamSearchLengthNormalization:
    """
    ---
    contract:
      algo_id: ALGO-NN-98
      name: NnAlgoBeamSearchLengthNormalization
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.beam_search
        - nn.sequence_decoding
        - nn.length_normalization
        - nn.autoregressive
      inputs:
        type: object
        required:
          - bos_id
          - eos_id
        properties:
          bos_id:
            type: integer
            description: Beginning-of-sequence token ID.
          eos_id:
            type: integer
            description: End-of-sequence token ID.
          beam_width:
            type: integer
            description: Number of active candidate hypotheses B >= 1.
          max_steps:
            type: integer
            description: Maximum decoding steps limit.
          alpha:
            type: number
            description: Length penalty exponent alpha.
      outputs:
        type: object
        required:
          - scored_hypotheses
        properties:
          scored_hypotheses:
            type: array
            items:
              type: object
            description: List of top beam candidate hypotheses with normalized log probability scores.
      parameters:
        beam_width: 4
        max_steps: 20
        alpha: 0.6
      input_assumptions:
        - beam_width >= 1
        - max_steps >= 1
        - alpha >= 0.0
      purity: pure
      determinism: deterministic
      idempotency: not_applicable
      reversibility: not_applicable
      side_effects: none
      concurrency_model: thread_safe
      hardware_target: cpu_scalar
      exactness: exact
      error_bound: "Exact top-B beam state traversal"
      uses_model: false
      complexity:
        variables:
          T: maximum decoding steps
          B: beam width
          V: vocabulary size
        time_worst: "O(T * B * V)"
        time_typical: "O(T * B * V)"
        space: "O(T * B)"
      preconditions:
        - input.beam_width >= 1
        - input.max_steps >= 1
        - input.alpha >= 0.0
      postconditions:
        - len(output.scored_hypotheses) <= input.beam_width
      certificate: "Score(y) = \\frac{\\sum_{t=1}^L \\log P(y_t \\mid y_{<t}, x)}{LP(L)}"
      compatible_adapters:
        - ADAPTER-BEAM-DECODER
        - ADAPTER-SEQ2SEQ-GENERATOR
      related_algos:
        - ALGO-NN-95
        - ALGO-NN-96
        - ALGO-NN-97
      references:
        - "https://arxiv.org/abs/1609.08144"
        - "https://arxiv.org/abs/1409.3215"
    ---
    """

    @staticmethod
    def length_penalty(length: int, alpha: float = 0.6) -> float:
        if length < 1:
            raise ValueError(f"Precondition failed: length {length} must be >= 1")
        if alpha < 0.0:
            raise ValueError(f"Precondition failed: alpha {alpha} must be non-negative")
        if alpha == 0.0:
            return 1.0
        return ((5.0 + float(length)) / 6.0) ** alpha

    @staticmethod
    def search(
        step_model_fn: Callable[[List[int]], List[float]],
        bos_id: int,
        eos_id: int,
        beam_width: int = 4,
        max_steps: int = 20,
        alpha: float = 0.6,
    ) -> List[Tuple[List[int], float, float]]:
        if beam_width < 1:
            raise ValueError(f"Precondition failed: beam_width {beam_width} must be >= 1")
        if max_steps < 1:
            raise ValueError(f"Precondition failed: max_steps {max_steps} must be >= 1")
        if alpha < 0.0:
            raise ValueError(f"Precondition failed: alpha {alpha} must be >= 0.0")

        beams: List[Tuple[List[int], float]] = [([bos_id], 0.0)]
        completed: List[Tuple[List[int], float]] = []

        for step in range(max_steps):
            candidates: List[Tuple[List[int], float]] = []

            for tokens, score in beams:
                if tokens[-1] == eos_id:
                    completed.append((tokens, score))
                    continue

                log_probs = step_model_fn(tokens)
                v_size = len(log_probs)

                for v in range(v_size):
                    cand_tokens = tokens + [v]
                    cand_score = score + log_probs[v]
                    candidates.append((cand_tokens, cand_score))

            if not candidates:
                break

            candidates.sort(key=lambda item: item[1], reverse=True)
            beams = []

            for cand_tokens, cand_score in candidates:
                if cand_tokens[-1] == eos_id:
                    completed.append((cand_tokens, cand_score))
                else:
                    beams.append((cand_tokens, cand_score))
                if len(beams) >= beam_width:
                    break

            if len(beams) == 0:
                break

        for b in beams:
            completed.append(b)

        scored_hypotheses: List[Tuple[List[int], float, float]] = []
        for tokens, raw_score in completed:
            seq_len = max(1, len(tokens) - 1)
            lp = NnAlgoBeamSearchLengthNormalization.length_penalty(seq_len, alpha)
            norm_score = raw_score / lp
            scored_hypotheses.append((tokens[1:], norm_score, raw_score))

        scored_hypotheses.sort(key=lambda item: item[1], reverse=True)
        return scored_hypotheses[:beam_width]
