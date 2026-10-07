"""ALGORITHM & ARCHITECTURE BLUEPRINT: CONDITIONAL RANDOM FIELDS (LINEAR-CHAIN & GRAPH CRFS) (ALGO-GRAPH-PGM-276)

1. OVERVIEW & OBJECTIVE
Discriminative probabilistic modeling for structured sequence and graph labeling. Computes conditional
probability P(Y|X) using feature functions conditioned on observed sequence X, executing exact forward-backward
inference for marginal likelihood calculation and dynamic programming Viterbi decoding for maximum-scoring sequence predictions.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(T * |K| + |K|^2) where T is sequence length, K is label domain size.
- Time Complexity: O(T * |K|^2) for forward-backward and Viterbi passes.
- Invariants:
  - Transition score matrices are added in log-space to unary emission potentials.
  - Forward-backward alpha/beta variables are numerically scaled to eliminate exponent overflow.

3. INPUT PARAMETERS:
- emission_scores: Sequence[Sequence[float]] sequence of length T with |K| emission scores per step.
- transition_matrix: Sequence[Sequence[float]] |K| x |K| state-to-state transition compatibility matrix.
- start_scores: Optional[Sequence[float]] initial state prior scores.
- end_scores: Optional[Sequence[float]] final state ending scores.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'viterbi_path': List[int] optimal state sequence maximizing total path score.
  - 'viterbi_score': float maximum path potential score.
  - 'log_partition': float log-normalizer log Z(X) of conditional probability.
  - 'node_marginals': List[List[float]] posterior state distribution per sequence token.

5. AGENT CONTRACT:
- Implemented with pure standard libraries and log-sum-exp stabilization.
- Zero inline comments.
"""

from __future__ import annotations

import math
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoConditionalRandomFieldsCrf(Generic[TNode]):
    """Linear-Chain Conditional Random Field (CRF) inference and Viterbi decoding.

    ```yaml
    contract:
      id: ALGO-GRAPH-PGM-276
      name: GraphAlgoConditionalRandomFieldsCrf
      inputs:
        - name: emission_scores
          type: Sequence[Sequence[float]]
          description: Sequence of unary potential vectors (T x K).
        - name: transition_matrix
          type: Sequence[Sequence[float]]
          description: Binary transition compatibility matrix (K x K).
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Viterbi best path, path score, log partition function, and per-token marginals.
      parameters:
        start_scores: Optional[Sequence[float]] (default None)
        end_scores: Optional[Sequence[float]] (default None)
      capability_tags:
        - PGM
        - CRF
        - SEQUENCE_LABELING
        - FORWARD_BACKWARD
        - VITERBI
      purity: PURE
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T * |K|^2)
        space: O(T * |K| + |K|^2)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        emission_scores: Sequence[Sequence[float]],
        transition_matrix: Sequence[Sequence[float]],
        start_scores: Optional[Sequence[float]] = None,
        end_scores: Optional[Sequence[float]] = None,
    ) -> Dict[str, Any]:
        """Runs Forward-Backward and Viterbi decoding over CRF sequence potentials."""
        t_len = len(emission_scores)
        if t_len == 0:
            return {
                "viterbi_path": [],
                "viterbi_score": 0.0,
                "log_partition": 0.0,
                "node_marginals": [],
            }

        k = len(transition_matrix)
        starts = list(start_scores) if start_scores is not None else [0.0] * k
        ends = list(end_scores) if end_scores is not None else [0.0] * k

        viterbi_scores: List[List[float]] = [[0.0] * k for _ in range(t_len)]
        backpointers: List[List[int]] = [[0] * k for _ in range(t_len)]

        for s in range(k):
            viterbi_scores[0][s] = starts[s] + emission_scores[0][s]

        for t in range(1, t_len):
            for curr_s in range(k):
                best_score = -1e18
                best_prev = 0
                for prev_s in range(k):
                    score = viterbi_scores[t - 1][prev_s] + transition_matrix[prev_s][curr_s]
                    if score > best_score:
                        best_score = score
                        best_prev = prev_s
                viterbi_scores[t][curr_s] = best_score + emission_scores[t][curr_s]
                backpointers[t][curr_s] = best_prev

        best_final_score = -1e18
        best_last_state = 0
        for s in range(k):
            total_end = viterbi_scores[t_len - 1][s] + ends[s]
            if total_end > best_final_score:
                best_final_score = total_end
                best_last_state = s

        viterbi_path = [0] * t_len
        viterbi_path[-1] = best_last_state
        for t in range(t_len - 1, 0, -1):
            viterbi_path[t - 1] = backpointers[t][viterbi_path[t]]

        alpha: List[List[float]] = [[0.0] * k for _ in range(t_len)]
        for s in range(k):
            alpha[0][s] = starts[s] + emission_scores[0][s]

        for t in range(1, t_len):
            for curr_s in range(k):
                arr = [alpha[t - 1][prev_s] + transition_matrix[prev_s][curr_s] for prev_s in range(k)]
                alpha[t][curr_s] = self._log_sum_exp(arr) + emission_scores[t][curr_s]

        final_alphas = [alpha[t_len - 1][s] + ends[s] for s in range(k)]
        log_z = self._log_sum_exp(final_alphas)

        beta: List[List[float]] = [[0.0] * k for _ in range(t_len)]
        for s in range(k):
            beta[t_len - 1][s] = ends[s]

        for t in range(t_len - 2, -1, -1):
            for curr_s in range(k):
                arr = [
                    transition_matrix[curr_s][next_s] + emission_scores[t + 1][next_s] + beta[t + 1][next_s]
                    for next_s in range(k)
                ]
                beta[t][curr_s] = self._log_sum_exp(arr)

        marginals: List[List[float]] = []
        for t in range(t_len):
            log_m = [alpha[t][s] + beta[t][s] - log_z for s in range(k)]
            m_probs = [math.exp(v) for v in log_m]
            sum_p = sum(m_probs)
            if sum_p > 0.0:
                marginals.append([p / sum_p for p in m_probs])
            else:
                marginals.append([1.0 / float(k)] * k)

        return {
            "viterbi_path": viterbi_path,
            "viterbi_score": best_final_score,
            "log_partition": log_z,
            "node_marginals": marginals,
        }

    def _log_sum_exp(self, arr: Sequence[float]) -> float:
        """Numerically stable log-sum-exp."""
        if not arr:
            return -1e18
        max_val = max(arr)
        if max_val <= -1e17:
            return -1e18
        sum_exp = sum(math.exp(v - max_val) for v in arr)
        return max_val + math.log(sum_exp)
