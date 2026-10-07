"""ALGORITHM & ARCHITECTURE BLUEPRINT: NN-DESCENT APPROXIMATE K-NN GRAPH CONSTRUCTION (ALGO-GRAPH-SIM-283)

1. OVERVIEW & OBJECTIVE
NN-Descent constructs an empirical approximate k-Nearest Neighbor (k-NN) graph across high-dimensional
metric datasets with empirical sub-quadratic O(N^{1.14}) scaling. Operates under the principle "a neighbor's
neighbor is likely also a neighbor", iteratively exploring local 2-hop neighborhoods, evaluating candidate
metric distances, and updating fixed-capacity nearest neighbor priority heaps.

2. COMPLEXITY & INVARIANTS
- Space Complexity: O(N * K) storing top-K neighbor lists with distances.
- Time Complexity: O(T_iter * N * K^2 * d) where d is feature dimension.
- Invariants:
  - Each node maintains exactly K closest candidate neighbors tracked in a bounded max-heap / sorted array.
  - Symmetrization ensures reverse edges are explored for bidirectional neighbor propagation.

3. INPUT PARAMETERS:
- points: Mapping[TNode, Sequence[float]] high-dimensional node coordinate vectors.
- k: int number of nearest neighbors per node.
- max_iterations: int propagation refinement rounds.
- rho: float sampling rate / sample proportion of neighbors per iteration.
- delta: float termination threshold for newly discovered edge proportion.

4. OUTPUT PARAMETERS:
- Dict[str, Any] containing:
  - 'knn_graph': Dict[TNode, List[tuple[TNode, float]]] k-nearest neighbor adjacency with distances.
  - 'iterations': int completed iteration rounds.
  - 'total_comparisons': int count of pairwise distance evaluations.

5. AGENT CONTRACT:
- Adherence to zero-inline-comment rule.
- Fully generic node type `TNode`.
"""

from __future__ import annotations

import math
import random
from typing import Any, Collection, Dict, Generic, Hashable, List, Mapping, Optional, Sequence, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoNnDescentKnnGraph(Generic[TNode]):
    """NN-Descent approximate k-Nearest Neighbor graph builder for arbitrary metrics.

    ```yaml
    contract:
      id: ALGO-GRAPH-SIM-283
      name: GraphAlgoNnDescentKnnGraph
      inputs:
        - name: points
          type: Mapping[TNode, Sequence[float]]
          description: Feature vectors for all candidate nodes.
        - name: k
          type: int
          default: 10
          description: Number of nearest neighbors to retrieve per node.
      outputs:
        - name: result
          type: Dict[str, Any]
          description: Computed k-NN graph with neighbor identifiers and Euclidean distances.
      parameters:
        max_iterations: int (default 15)
        rho: float (default 0.5)
        delta: float (default 0.001)
        seed: int (default 42)
      capability_tags:
        - SIMILARITY_GRAPH
        - NN_DESCENT
        - APPROXIMATE_KNN
        - GRAPH_CONSTRUCTION
      purity: DETERMINISTIC_WITH_SEED
      determinism: HIGH
      idempotency: IDEMPOTENT
      complexity:
        time: O(T * N * K^2 * d)
        space: O(N * K)
    ```
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        points: Mapping[TNode, Sequence[float]],
        k: int = 10,
        max_iterations: int = 15,
        rho: float = 0.5,
        delta: float = 0.001,
        seed: int = 42,
    ) -> Dict[str, Any]:
        """Constructs k-NN graph using iterative local neighborhood propagation."""
        rng = random.Random(seed)
        nodes = list(points.keys())
        n = len(nodes)
        if n == 0:
            return {"knn_graph": {}, "iterations": 0, "total_comparisons": 0}

        actual_k = min(k, n - 1)
        if actual_k <= 0:
            return {"knn_graph": {u: [] for u in nodes}, "iterations": 0, "total_comparisons": 0}

        knn: Dict[TNode, List[Tuple[float, TNode, bool]]] = {}
        for u in nodes:
            candidates = rng.sample([v for v in nodes if v != u], actual_k)
            entries = []
            for v in candidates:
                d = self._euclidean_dist(points[u], points[v])
                entries.append((d, v, True))
            entries.sort(key=lambda x: x[0])
            knn[u] = entries

        total_comparisons = n * actual_k
        iterations_run = 0

        for it in range(max_iterations):
            iterations_run = it + 1
            new_edges = 0

            old_neighbors: Dict[TNode, List[TNode]] = {u: [] for u in nodes}
            new_neighbors: Dict[TNode, List[TNode]] = {u: [] for u in nodes}

            for u in nodes:
                for d, v, is_new in knn[u]:
                    if is_new:
                        new_neighbors[u].append(v)
                        new_neighbors[v].append(u)
                    else:
                        old_neighbors[u].append(v)
                        old_neighbors[v].append(u)

            sampled_new: Dict[TNode, List[TNode]] = {}
            sampled_old: Dict[TNode, List[TNode]] = {}

            for u in nodes:
                new_list = list(set(new_neighbors[u]))
                old_list = list(set(old_neighbors[u]))

                num_new_sample = max(1, int(len(new_list) * rho))
                num_old_sample = max(1, int(len(old_list) * rho))

                sampled_new[u] = rng.sample(new_list, min(len(new_list), num_new_sample)) if new_list else []
                sampled_old[u] = rng.sample(old_list, min(len(old_list), num_old_sample)) if old_list else []

            for u in nodes:
                knn[u] = [(d, v, False) for d, v, _ in knn[u]]

            for u in nodes:
                new_u = sampled_new[u]
                old_u = sampled_old[u]

                for i, v1 in enumerate(new_u):
                    for v2 in new_u[i + 1 :]:
                        if v1 != v2:
                            d = self._euclidean_dist(points[v1], points[v2])
                            total_comparisons += 1
                            if self._try_insert_neighbor(knn[v1], v2, d, actual_k):
                                new_edges += 1
                            if self._try_insert_neighbor(knn[v2], v1, d, actual_k):
                                new_edges += 1

                    for v2 in old_u:
                        if v1 != v2:
                            d = self._euclidean_dist(points[v1], points[v2])
                            total_comparisons += 1
                            if self._try_insert_neighbor(knn[v1], v2, d, actual_k):
                                new_edges += 1
                            if self._try_insert_neighbor(knn[v2], v1, d, actual_k):
                                new_edges += 1

            if new_edges <= delta * n * actual_k:
                break

        final_graph: Dict[TNode, List[Tuple[TNode, float]]] = {}
        for u in nodes:
            final_graph[u] = [(v, d) for d, v, _ in knn[u]]

        return {
            "knn_graph": final_graph,
            "iterations": iterations_run,
            "total_comparisons": total_comparisons,
        }

    def _euclidean_dist(self, p1: Sequence[float], p2: Sequence[float]) -> float:
        """Calculates Euclidean metric distance."""
        s = 0.0
        for x, y in zip(p1, p2):
            diff = float(x) - float(y)
            s += diff * diff
        return math.sqrt(s)

    def _try_insert_neighbor(
        self,
        nbr_list: List[Tuple[float, TNode, bool]],
        v: TNode,
        d: float,
        k: int,
    ) -> bool:
        """Inserts neighbor candidate (d, v) if closer than worst current neighbor."""
        for existing_d, existing_v, _ in nbr_list:
            if existing_v == v:
                return False

        if len(nbr_list) < k:
            nbr_list.append((d, v, True))
            nbr_list.sort(key=lambda x: x[0])
            return True

        if d < nbr_list[-1][0]:
            nbr_list[-1] = (d, v, True)
            nbr_list.sort(key=lambda x: x[0])
            return True

        return False
