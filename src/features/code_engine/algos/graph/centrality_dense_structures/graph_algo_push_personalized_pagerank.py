"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: PUSH PERSONALIZED PAGERANK (ALGO-GRAPH-CENT-103)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Andersen-Chung-Lang (ACL) forward-push approximate personalized PageRank.
   Computes local personalized PageRank around a seed vertex in time proportional
   to 1 / (alpha * epsilon), independent of total graph size.
   Maintains reserve and estimate vectors and lazily discharges residuals.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(1 / (alpha * epsilon)) bounded push operations.
   - Space Complexity: O(1 / (alpha * epsilon)) non-zero entries.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Directed or undirected graph adjacency.
   - seed: TNode - Source vertex from which personalized relevance is measured.
   - alpha: float - Teleportation probability (default: 0.15).
   - epsilon: float - Residual push threshold (default: 1e-4).

4. OUTPUT PARAMETERS:
   - probabilities: Dict[TNode, float] - Approximate personalized PageRank vector.
   - residuals: Dict[TNode, float] - Remaining undistributed mass per vertex.
   - push_count: int - Total number of push operations executed.

5. AGENT CONTRACT:
   - Role: Analyst and Retriever.
   - Preconditions: Seed vertex must exist in the graph.
   - Guardrails: Push condition r(u) >= epsilon * deg(u) guarantees bounded L1 error.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoPushPersonalizedPageRank(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-103
      name: GraphAlgoPushPersonalizedPageRank
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, ppr, local_push, andersen_chung_lang, graphrag]
      inputs:
        type: object
        required: [adjacency, seed]
        properties:
          adjacency: {type: object}
          seed: {type: string}
          alpha: {type: number, default: 0.15}
          epsilon: {type: number, default: 0.0001}
      outputs:
        type: object
        required: [probabilities, residuals, push_count]
        properties:
          probabilities: {type: object}
          residuals: {type: object}
          push_count: {type: integer}
      parameters:
        alpha: {type: number, default: 0.15}
        epsilon: {type: number, default: 0.0001}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(1 / (alpha * epsilon))
        space: O(1 / (alpha * epsilon))
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        alpha: float = 0.15,
        epsilon: float = 1e-4,
    ) -> None:
        """
        Initialize the forward push personalized PageRank solver.

        Args:
            adjacency: Graph adjacency mapping each node to a list of out-neighbors.
            alpha: Teleportation probability (default: 0.15).
            epsilon: Push resolution threshold (default: 1e-4).
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._alpha: float = alpha
        self._eps: float = epsilon

    def compute_ppr(self, seed: TNode) -> Tuple[Dict[TNode, float], Dict[TNode, float], int]:
        """
        Compute approximate personalized PageRank vector from the given seed.

        Args:
            seed: Source vertex for personalized teleportation.

        Returns:
            Tuple of (probabilities_map, residuals_map, total_pushes).
        """
        p: Dict[TNode, float] = {}
        r: Dict[TNode, float] = {seed: 1.0}
        q: Deque[TNode] = deque([seed])
        in_queue: Set[TNode] = {seed}
        push_count: int = 0

        while q:
            u = q.popleft()
            in_queue.remove(u)
            deg_u = len(self._adj.get(u, []))
            r_u = r.get(u, 0.0)

            threshold = self._eps * max(1, deg_u)
            if r_u < threshold:
                continue

            p[u] = p.get(u, 0.0) + self._alpha * r_u
            push_mass = (1.0 - self._alpha) * r_u
            r[u] = 0.0
            push_count += 1

            if deg_u > 0:
                share = push_mass / float(deg_u)
                for v in self._adj[u]:
                    r[v] = r.get(v, 0.0) + share
                    deg_v = len(self._adj.get(v, []))
                    if r[v] >= self._eps * max(1, deg_v) and v not in in_queue:
                        q.append(v)
                        in_queue.add(v)
            else:
                r[seed] = r.get(seed, 0.0) + push_mass
                if r[seed] >= self._eps * max(1, len(self._adj.get(seed, []))) and seed not in in_queue:
                    q.append(seed)
                    in_queue.add(seed)

        return p, {k: v for k, v in r.items() if v > 0}, push_count
