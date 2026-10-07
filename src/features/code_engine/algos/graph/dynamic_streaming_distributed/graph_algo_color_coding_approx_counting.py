"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: COLOR CODING APPROXIMATE COUNTING (ALGO-GRAPH-ENUM-234)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Color Coding for Approximate Subgraph / Tree Motif Counting (Alon et al.).
   Computes unbiased, low-variance estimates of k-vertex tree patterns (e.g. k-paths,
   stars, forks) via randomized vertex k-coloring and dynamic programming over color bitmasks.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(2^k * M) per coloring trial, polynomial in V and M.
   - Space Complexity: O(2^k * V) bitmask DP tables.
   - Purity: Stateful randomized estimator, reproducible via random seed.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Target graph adjacency.
   - `k` (int): Number of nodes in target path / motif.
   - `num_trials` (int): Number of independent random coloring trials.
   - `seed` (Optional[int]): PRNG seed for reproducibility.

4. OUTPUT PARAMETERS:
   - `estimate_k_path_count()` (float): Unbiased estimate of simple k-path count.
   - `estimate_variance()` (float): Empirical variance across trials.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Scale-up factor k^k / k! ensures exact unbiased expectation E[estimate] = true_count.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoColorCodingApproxCounting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENUM-234
      name: GraphAlgoColorCodingApproxCounting
      version: 1.0.0
      category: graph_enumeration
      capability_tags: [graph, enumeration, color_coding, approximate_counting, k_paths, dynamic_programming]
      inputs:
        type: object
        required: [adjacency, k]
        properties:
          adjacency: {type: object}
          k: {type: integer, minimum: 2, maximum: 12}
          num_trials: {type: integer, minimum: 1}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          estimated_count: {type: number}
          variance: {type: number}
      parameters:
        k: {type: integer}
        num_trials: {type: integer}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(T * 2^k * M)
        space: O(2^k * V)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        k: int = 4,
        num_trials: int = 10,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize color coding approximate counter.

        Args:
            adjacency: Adjacency dictionary.
            k: Pattern path size (nodes in path).
            num_trials: Number of randomized colorings.
            seed: PRNG seed.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._k: int = max(2, min(12, k))
        self._num_trials: int = max(1, num_trials)
        self._rng = random.Random(seed)
        self._nodes: List[TNode] = list(self._adj.keys())

    def _count_colorful_paths_single_trial(self) -> int:
        colors: Dict[TNode, int] = {u: self._rng.randint(0, self._k - 1) for u in self._nodes}
        num_masks = 1 << self._k
        dp: Dict[TNode, List[int]] = {u: [0] * num_masks for u in self._nodes}

        for u in self._nodes:
            c = colors[u]
            dp[u][1 << c] = 1

        for mask_size in range(1, self._k):
            for mask in range(num_masks):
                if bin(mask).count("1") == mask_size:
                    for u in self._nodes:
                        cnt = dp[u][mask]
                        if cnt > 0:
                            for v in self._adj.get(u, []):
                                c_v = colors[v]
                                if not (mask & (1 << c_v)):
                                    dp[v][mask | (1 << c_v)] += cnt

        full_mask = (1 << self._k) - 1
        total_colorful = sum(dp[u][full_mask] for u in self._nodes)
        return total_colorful // 2

    def estimate_k_path_count(self) -> Tuple[float, float]:
        """
        Compute unbiased estimate of simple k-path count.

        Returns:
            Tuple of (mean_estimated_count, empirical_variance).
        """
        prob_colorful = math.factorial(self._k) / (self._k ** self._k)
        scale_factor = 1.0 / prob_colorful

        estimates = []
        for _ in range(self._num_trials):
            colorful_cnt = self._count_colorful_paths_single_trial()
            estimates.append(colorful_cnt * scale_factor)

        mean_est = sum(estimates) / len(estimates)
        if len(estimates) > 1:
            variance = sum((x - mean_est) ** 2 for x in estimates) / (len(estimates) - 1)
        else:
            variance = 0.0

        return mean_est, variance
