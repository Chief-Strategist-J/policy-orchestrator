from __future__ import annotations

import math
from typing import Any, Dict, List, Literal, Optional, Sequence


class NnAlgoCtcLoss:
    """
    ---
    contract:
      algo_id: ALGO-NN-20
      name: NnAlgoCtcLoss
      version: 1.0.0
      category: nn
      capability_tags:
        - nn.loss
        - nn.ctc
        - nn.speech_recognition
        - nn.sequence_alignment
      inputs:
        type: object
        properties:
          log_probs:
            type: array
            items:
              type: array
              items:
                type: number
            description: Log-probabilities log P of shape (T, C) where T is input time frames and C is vocabulary size including blank.
          targets:
            type: array
            items:
              type: integer
            description: Target label sequence l of length L.
          blank:
            type: integer
            default: 0
            description: Index of the CTC blank symbol in [0, C-1].
        required:
          - log_probs
          - targets
        additionalProperties: false
      outputs:
        type: object
        properties:
          loss:
            type: number
            description: Connectionist Temporal Classification negative log-likelihood loss.
          forward_log_lattice:
            type: array
            items:
              type: array
              items:
                type: number
            description: Forward dynamic programming log-probabilities alpha of shape (T, 2L+1).
          input_length:
            type: integer
            description: Input frame length T.
          target_length:
            type: integer
            description: Target label length L.
        required:
          - loss
          - input_length
          - target_length
        additionalProperties: false
    ---
    """

    @staticmethod
    def forward(
        log_probs: Sequence[Sequence[float]],
        targets: Sequence[int],
        blank: int = 0,
    ) -> Dict[str, Any]:
        t_len = len(log_probs)
        l_len = len(targets)
        if t_len == 0:
            raise ValueError("Precondition failed: log_probs sequence cannot be empty.")
        c = len(log_probs[0])
        if not (0 <= blank < c):
            raise ValueError(f"Precondition failed: blank index {blank} out of bounds [0, {c-1}].")
        if t_len < l_len:
            raise ValueError(
                f"Precondition failed: input length T ({t_len}) must be >= target length L ({l_len})."
            )

        # Build modified target sequence l_prime with blanks interleaved: length 2L + 1
        l_prime: List[int] = []
        for lab in targets:
            if not (0 <= lab < c):
                raise ValueError(f"Precondition failed: target label {lab} out of bounds [0, {c-1}].")
            l_prime.append(blank)
            l_prime.append(lab)
        l_prime.append(blank)
        s_len = len(l_prime)  # 2L + 1

        NEG_INF = -1e30

        def log_sum_exp_pair(a: float, b: float) -> float:
            if a <= NEG_INF:
                return b
            if b <= NEG_INF:
                return a
            m = max(a, b)
            return m + math.log(math.exp(a - m) + math.exp(b - m))

        def log_sum_exp_trio(a: float, b: float, c_: float) -> float:
            return log_sum_exp_pair(log_sum_exp_pair(a, b), c_)

        # Forward dynamic programming table: alpha[t][s]
        alpha = [[NEG_INF] * s_len for _ in range(t_len)]

        # Initialization at t = 0
        alpha[0][0] = log_probs[0][l_prime[0]]
        if s_len > 1:
            alpha[0][1] = log_probs[0][l_prime[1]]

        # Dynamic programming forward recurrence
        for t in range(1, t_len):
            for s in range(s_len):
                sym = l_prime[s]
                # Option 1: self-loop alpha[t-1][s]
                term1 = alpha[t - 1][s]
                # Option 2: transition from s-1
                term2 = alpha[t - 1][s - 1] if s > 0 else NEG_INF
                # Option 3: skip blank transition from s-2 (if not blank and not repeated label)
                if s >= 2 and sym != blank and l_prime[s] != l_prime[s - 2]:
                    term3 = alpha[t - 1][s - 2]
                else:
                    term3 = NEG_INF

                prev_log_sum = log_sum_exp_trio(term1, term2, term3)
                if prev_log_sum > NEG_INF:
                    alpha[t][s] = prev_log_sum + log_probs[t][sym]
                else:
                    alpha[t][s] = NEG_INF

        # Total forward probability is sum of ending in blank or final label at t = T-1
        final_blank = alpha[t_len - 1][s_len - 1]
        final_label = alpha[t_len - 1][s_len - 2] if s_len >= 2 else NEG_INF
        total_log_prob = log_sum_exp_pair(final_blank, final_label)

        if total_log_prob <= NEG_INF:
            loss_val = float("inf")
        else:
            loss_val = -total_log_prob

        return {
            "loss": loss_val,
            "forward_log_lattice": alpha,
            "input_length": t_len,
            "target_length": l_len,
        }
