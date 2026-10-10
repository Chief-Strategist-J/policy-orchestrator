"""Beam Search with Length Normalization Penalty for Sequence Generation.

Formal Mathematical YAML Contract:
----------------------------------
contract:
  name: beam_search_length_normalization
  category: neural_network_architecture
  subcategory: sequence_models
  id: ALGO-NN-98
  equation: |
    \\text{Score}(\\mathbf{y}) = \\frac{\\sum_{t=1}^L \\log P(y_t \\mid y_{<t}, \\mathbf{x})}{\\text{LP}(L)}
    \\text{LP}(L) = \\frac{(5 + L)^\\alpha}{(5 + 1)^\\alpha} \\quad \\text{or} \\quad L^\\alpha
    \\mathcal{H}_t = \\text{Top-B}\\left( \\{ (\\mathbf{y} \\circ v, \\text{score} + \\log P(v \\mid \\mathbf{y})) \\mid \\mathbf{y} \\in \\mathcal{H}_{t-1}, v \\in \\mathcal{V} \\} \\right)
  domain:
    beam_width: B >= 1
    length_penalty_alpha: "\\alpha \\in [0.0, 1.5]"
    vocabulary_size: V
  properties:
    heuristic_pruned_search: true
    length_bias_correction: true
    top_b_hypothesis_tracking: true
    deterministic_reproducible: true
"""

from typing import List, Tuple, Dict, Any, Optional, Callable
import math


class BeamSearchLengthNormalization:
    """Beam Search decoder with polynomial / GNMT length normalization penalties."""

    @staticmethod
    def length_penalty(length: int, alpha: float = 0.6) -> float:
        """Compute GNMT length normalization penalty divisor.

        Formula: LP(L) = ((5 + L) / 6)^alpha

        Args:
            length: Sequence token length L >= 1.
            alpha: Length penalty weight (0.0 = no penalty, 1.0 = full linear penalty).

        Returns:
            Scalar normalization divisor > 0.
        """
        assert length >= 1, "Length must be >= 1."
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
        alpha: float = 0.6
    ) -> List[Tuple[List[int], float, float]]:
        """Execute full Beam Search rollout with length normalization.

        Args:
            step_model_fn: Function mapping current token history [y_1, ..., y_{t-1}] to next-token log-probs of length V.
            bos_id: Beginning-of-sequence token ID.
            eos_id: End-of-sequence token ID.
            beam_width: Number of active candidate hypotheses B.
            max_steps: Maximum generation sequence length.
            alpha: Length normalization exponent.

        Returns:
            List of completed or active hypotheses sorted by normalized score:
            [(tokens, normalized_score, raw_log_prob), ...]
        """
        assert beam_width >= 1, "Beam width must be >= 1."

        # Hypothesis format: (token_list, cumulative_log_prob)
        beams: List[Tuple[List[int], float]] = [([bos_id], 0.0)]
        completed: List[Tuple[List[int], float]] = []

        for step in range(max_steps):
            candidates: List[Tuple[List[int], float]] = []

            for tokens, score in beams:
                # If hypothesis already ended with EOS, carry over directly
                if tokens[-1] == eos_id:
                    completed.append((tokens, score))
                    continue

                # Query next token log-probabilities
                log_probs = step_model_fn(tokens)
                v_size = len(log_probs)

                # Expand with all vocabulary options
                for v in range(v_size):
                    cand_tokens = tokens + [v]
                    cand_score = score + log_probs[v]
                    candidates.append((cand_tokens, cand_score))

            if not candidates:
                break

            # Sort candidates by raw score descending and prune to top-B
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

        # Move any remaining active beams to completed list
        for b in beams:
            completed.append(b)

        # Normalize scores by length penalty
        scored_hypotheses = []
        for tokens, raw_score in completed:
            # Exclude BOS from length calculation
            seq_len = max(1, len(tokens) - 1)
            lp = BeamSearchLengthNormalization.length_penalty(seq_len, alpha)
            norm_score = raw_score / lp
            scored_hypotheses.append((tokens[1:], norm_score, raw_score))

        # Sort by normalized score descending
        scored_hypotheses.sort(key=lambda item: item[1], reverse=True)
        return scored_hypotheses[:beam_width]
