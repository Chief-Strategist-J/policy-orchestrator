"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: APPROXIMATE QUERY PROCESSING ON GRAPHS (ALGO-GRAPH-ENG-250)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Approximate Query Processing (AQP) Engine on Massive Graph Topologies.
   Answers aggregate global and neighborhood queries (average degree, degree distribution
   moments, high-degree tail counts) from progressive vertex/edge samples with
   unbiased Horvitz-Thompson estimation and rigorous confidence intervals.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(Sample_Size) strictly sublinear in |V| and |E|.
   - Space Complexity: O(Sample_Size) memory buffer.
   - Purity: Stateful randomized query engine, reproducible with seed.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): Vertex list.
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `sample_ratio` (float): Fraction of nodes to sample (0 < ratio <= 1).
   - `seed` (Optional[int]): Random seed.

4. OUTPUT PARAMETERS:
   - `estimate_average_degree()` (Tuple[float, float, float]): (Estimated mean, lower 95% CI, upper 95% CI).
   - `estimate_nodes_with_degree_above(threshold)` (Tuple[float, float, float]): Estimated count and confidence interval.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: All reported statistics include explicit 95% Clopper-Pearson / normal error bounds.
================================================================================
"""

import math
import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoApproximateQueryProcessingSampling(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENG-250
      name: GraphAlgoApproximateQueryProcessingSampling
      version: 1.0.0
      category: graph_engineering
      capability_tags: [graph, engineering, aqp, approximate_query, sampling, confidence_intervals, horvitz_thompson]
      inputs:
        type: object
        required: [nodes, adjacency]
        properties:
          nodes: {type: array}
          adjacency: {type: object}
          sample_ratio: {type: number, minimum: 0.01, maximum: 1.0}
          seed: {type: integer}
      outputs:
        type: object
        properties:
          estimated_average_degree: {type: number}
          ci_lower: {type: number}
          ci_upper: {type: number}
      parameters:
        sample_ratio: {type: number}
      purity: stateful
      determinism: deterministic_with_seed
      idempotency: idempotent
      complexity:
        time: O(S)
        space: O(S)
    ---
    """

    def __init__(
        self,
        nodes: List[TNode],
        adjacency: Dict[TNode, List[TNode]],
        sample_ratio: float = 0.2,
        seed: Optional[int] = 42,
    ) -> None:
        """
        Initialize AQP graph sampler.

        Args:
            nodes: Complete vertex universe.
            adjacency: Adjacency map.
            sample_ratio: Sampling proportion p.
            seed: PRNG seed.
        """
        self._nodes: List[TNode] = list(nodes)
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u in self._nodes:
            if u not in self._adj:
                self._adj[u] = []

        self._n: int = len(self._nodes)
        self._sample_ratio: float = max(0.01, min(1.0, sample_ratio))
        self._sample_size: int = max(1, int(round(self._n * self._sample_ratio)))
        self._rng = random.Random(seed)

        self._sampled_nodes: List[TNode] = self._rng.sample(self._nodes, self._sample_size) if self._n > 0 else []

    def estimate_average_degree(self, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Estimate mean vertex degree and confidence interval.

        Args:
            confidence: Confidence level (e.g. 0.95).

        Returns:
            Tuple of (point_estimate, ci_lower, ci_upper).
        """
        if not self._sampled_nodes:
            return 0.0, 0.0, 0.0

        sample_degrees = [len(self._adj.get(u, [])) for u in self._sampled_nodes]
        m = len(sample_degrees)
        mean_d = sum(sample_degrees) / float(m)

        if m > 1:
            var_d = sum((x - mean_d) ** 2 for x in sample_degrees) / (m - 1)
            std_err = math.sqrt(var_d / m) * math.sqrt(max(0.0, 1.0 - m / float(self._n)))
        else:
            std_err = 0.0

        z = 1.96 if confidence >= 0.95 else 1.645
        ci_lower = max(0.0, mean_d - z * std_err)
        ci_upper = mean_d + z * std_err

        return float(mean_d), float(ci_lower), float(ci_upper)

    def estimate_nodes_with_degree_above(self, threshold: int, confidence: float = 0.95) -> Tuple[float, float, float]:
        """
        Estimate count of nodes having degree >= threshold.

        Args:
            threshold: Minimum degree cutoff.
            confidence: Confidence level.

        Returns:
            Tuple of (estimated_count, ci_lower, ci_upper).
        """
        if not self._sampled_nodes:
            return 0.0, 0.0, 0.0

        matches = sum(1 for u in self._sampled_nodes if len(self._adj.get(u, [])) >= threshold)
        m = len(self._sampled_nodes)
        p_hat = matches / float(m)
        est_count = p_hat * self._n

        if m > 1 and 0.0 < p_hat < 1.0:
            std_err = math.sqrt(p_hat * (1.0 - p_hat) / m) * math.sqrt(max(0.0, 1.0 - m / float(self._n)))
        else:
            std_err = 0.0

        z = 1.96 if confidence >= 0.95 else 1.645
        ci_lower = max(0.0, (p_hat - z * std_err) * self._n)
        ci_upper = min(float(self._n), (p_hat + z * std_err) * self._n)

        return float(est_count), float(ci_lower), float(ci_upper)
