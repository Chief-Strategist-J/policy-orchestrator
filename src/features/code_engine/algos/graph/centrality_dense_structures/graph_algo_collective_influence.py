"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: COLLECTIVE INFLUENCE & SPREADER RANKING (ALGO-GRAPH-CENT-114)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Collective Influence (CI) and K-Shell Coreness spreader ranking algorithm.
   Identifies minimal sets of influential spreaders capable of dismantling the
   giant connected component under optimal percolation.
   Evaluates CI_ell(v) = (deg(v) - 1) * sum_{u in Ball_ell(v)} (deg(u) - 1).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * d^ell) neighborhood sphere expansion.
   - Space Complexity: O(V) metric storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - radius_ell: int - Collective Influence boundary ball radius ell (default: 2).

4. OUTPUT PARAMETERS:
   - collective_influence: Dict[TNode, float] - CI score per vertex at radius ell.
   - k_shell_coreness: Dict[TNode, int] - K-shell coreness decomposition level.
   - top_spreaders: List[TNode] - Vertices ranked in descending order of CI.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph input.
   - Guardrails: Non-local ball expansion prunes self-loops and back-edges.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCollectiveInfluence(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-114
      name: GraphAlgoCollectiveInfluence
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, collective_influence, spreader_ranking, percolation, k_shell]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          radius_ell: {type: integer, default: 2}
      outputs:
        type: object
        required: [collective_influence, k_shell_coreness, top_spreaders]
        properties:
          collective_influence: {type: object}
          k_shell_coreness: {type: object}
          top_spreaders: {type: array, items: {type: string}}
      parameters:
        radius_ell: {type: integer, default: 2}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * d^L)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], radius_ell: int = 2) -> None:
        """
        Initialize the Collective Influence analyzer.

        Args:
            adjacency: Undirected graph adjacency.
            radius_ell: Boundary ball radius parameter ell (default: 2).
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._ell: int = radius_ell
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _compute_k_shell(self) -> Dict[TNode, int]:
        degrees = {u: len(self._adj.get(u, [])) for u in self._nodes}
        curr_adj = {u: set(self._adj.get(u, [])) for u in self._nodes}
        coreness: Dict[TNode, int] = {}
        k: int = 0
        remaining = set(self._nodes)

        while remaining:
            k += 1
            while True:
                to_remove = [u for u in remaining if degrees[u] <= k]
                if not to_remove:
                    break
                for u in to_remove:
                    coreness[u] = k
                    remaining.remove(u)
                    for nbr in curr_adj[u]:
                        if nbr in remaining:
                            curr_adj[nbr].remove(u)
                            degrees[nbr] -= 1

        return coreness

    def compute_metrics(self) -> Tuple[Dict[TNode, float], Dict[TNode, int], List[TNode]]:
        """
        Compute Collective Influence and K-Shell Coreness rankings.

        Returns:
            Tuple of (collective_influence_dict, k_shell_coreness_dict, ranked_top_spreaders).
        """
        degrees: Dict[TNode, int] = {u: len(self._adj.get(u, [])) for u in self._nodes}
        ci: Dict[TNode, float] = {}

        for u in self._nodes:
            deg_u = degrees[u]
            if deg_u <= 1:
                ci[u] = 0.0
                continue

            dist: Dict[TNode, int] = {u: 0}
            q: Deque[TNode] = deque([u])
            frontier_nodes: List[TNode] = []

            while q:
                curr = q.popleft()
                d = dist[curr]
                if d == self._ell:
                    frontier_nodes.append(curr)
                    continue

                for v in self._adj.get(curr, []):
                    if v not in dist:
                        dist[v] = d + 1
                        q.append(v)

            sum_reduced_deg = sum(max(0, degrees[v] - 1) for v in frontier_nodes)
            ci[u] = float(deg_u - 1) * float(sum_reduced_deg)

        coreness = self._compute_k_shell()
        top_spreaders = sorted(self._nodes, key=lambda x: (-ci[x], -coreness[x], str(x)))

        return ci, coreness, top_spreaders
