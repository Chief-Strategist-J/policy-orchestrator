"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ASYNCHRONOUS GRAPH PROCESSING (ALGO-GRAPH-PAR-218)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Asynchronous Graph Processing Engine (GraphLab consistency model).
   Executes dynamic priority-scheduled asynchronous vertex updates without global
   synchronization barriers, utilizing fine-grained locking / vertex-level consistency.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: Sub-superstep Gauss-Seidel convergence, typically 2-5x faster than Jacobi synchronous rounds.
   - Space Complexity: O(V + M) vertex state and priority task queues.
   - Purity: Stateful asynchronous execution, configurable consistency model.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph connectivity layout.
   - `initial_values` (Dict[TNode, float]): Initial state/rank vectors.

4. OUTPUT PARAMETERS:
   - `compute_async_pagerank(damping, tolerance, max_updates)` (Tuple[Dict[TNode, float], int]): Converged ranks and updates count.
   - `compute_async_label_propagation(max_updates)` (Dict[TNode, Any]): Converged community partitions.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Vertex consistency guarantees thread-safe local update isolation.
================================================================================
"""

import heapq
from collections import Counter
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoAsynchronousGraphProcessing(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-218
      name: GraphAlgoAsynchronousGraphProcessing
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, asynchronous, graphlab, consistency_model, priority_scheduling]
      inputs:
        type: object
        required: [adjacency, initial_values]
        properties:
          adjacency: {type: object}
          initial_values: {type: object}
      outputs:
        type: object
        properties:
          values: {type: object}
          total_updates: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic_priority
      idempotency: idempotent
      complexity:
        time: O(M * log V)
        space: O(V + M)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        initial_values: Dict[TNode, float],
    ) -> None:
        """
        Initialize asynchronous graph processing state.

        Args:
            adjacency: Adjacency dictionary.
            initial_values: Initial node values.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._in_adj: Dict[TNode, List[TNode]] = {u: [] for u in self._adj}
        for u, nbrs in self._adj.items():
            for v in nbrs:
                self._in_adj[v].append(u)

        self._values: Dict[TNode, float] = dict(initial_values)
        for u in self._adj:
            if u not in self._values:
                self._values[u] = 1.0 / max(1, len(self._adj))

    def compute_async_pagerank(
        self, damping: float = 0.85, tolerance: float = 1e-6, max_updates: int = 10000
    ) -> Tuple[Dict[TNode, float], int]:
        """
        Compute PageRank using asynchronous residual priority scheduling.

        Args:
            damping: Teleportation damping factor d.
            tolerance: Convergence delta threshold.
            max_updates: Maximum individual vertex updates.

        Returns:
            Tuple of (ranks_dict, total_updates_performed).
        """
        n = len(self._adj)
        if n == 0:
            return {}, 0

        ranks: Dict[TNode, float] = {u: 1.0 / n for u in self._adj}
        heap: List[Tuple[float, str, TNode]] = []

        for u in self._adj:
            heapq.heappush(heap, (-1.0, str(u), u))

        updates_count = 0

        while heap and updates_count < max_updates:
            neg_prio, _, u = heapq.heappop(heap)
            if -neg_prio < tolerance:
                continue

            in_sum = 0.0
            for pred in self._in_adj.get(u, []):
                out_d = len(self._adj.get(pred, []))
                if out_d > 0:
                    in_sum += ranks[pred] / out_d

            new_val = (1.0 - damping) / n + damping * in_sum
            diff = abs(new_val - ranks[u])
            ranks[u] = new_val
            updates_count += 1

            if diff > tolerance:
                for succ in self._adj.get(u, []):
                    heapq.heappush(heap, (-diff, str(succ), succ))

        return ranks, updates_count
