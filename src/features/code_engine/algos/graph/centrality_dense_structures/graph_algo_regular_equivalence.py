"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REGULAR EQUIVALENCE & REGE (ALGO-GRAPH-ROLE-119)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Regular equivalence and REGE iterative role similarity algorithm.
   Evaluates regular equivalence: two vertices are regularly equivalent if they
   connect to equivalent classes of neighbors, regardless of whether their neighborhood sets overlap.
   Converges to coarsest partition consistent with role patterns.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(iterations * V^2 * d_avg^2) iterative matching updates.
   - Space Complexity: O(V^2) pairwise equivalence matrix.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Directed graph adjacency list.
   - max_iter: int - Iteration rounds for REGE convergence (default: 10).
   - tol: float - Max difference convergence tolerance (default: 1e-3).

4. OUTPUT PARAMETERS:
   - equivalence_matrix: Dict[Tuple[TNode, TNode], float] - Regular equivalence score in [0.0, 1.0].
   - equivalence_classes: Dict[int, List[TNode]] - Disjoint clusters of regularly equivalent nodes.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Non-empty directed graph.
   - Guardrails: Thresholding at 0.95 extracts crisp structural equivalence classes.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoRegularEquivalence(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ROLE-119
      name: GraphAlgoRegularEquivalence
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, structural_roles, regular_equivalence, rege, role_similarity, partition_refinement]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          max_iter: {type: integer, default: 10}
          tol: {type: number, default: 0.001}
      outputs:
        type: object
        required: [equivalence_matrix, equivalence_classes]
        properties:
          equivalence_matrix: {type: object}
          equivalence_classes: {type: object}
      parameters:
        max_iter: {type: integer, default: 10}
        tol: {type: number, default: 0.001}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(K * V^2 * d^2)
        space: O(V^2)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        max_iter: int = 10,
        tol: float = 1e-3,
    ) -> None:
        """
        Initialize the Regular Equivalence engine.

        Args:
            adjacency: Graph adjacency dictionary.
            max_iter: Maximum REGE iterations.
            tol: Tolerance threshold.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._max_iter: int = max_iter
        self._tol: float = tol
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def compute_equivalence(self, class_threshold: float = 0.9) -> Tuple[Dict[Tuple[TNode, TNode], float], Dict[int, List[TNode]]]:
        """
        Compute REGE regular equivalence matrix and clustered equivalence classes.

        Args:
            class_threshold: Similarity cutoff for clustering into equivalence classes.

        Returns:
            Tuple of (pairwise_similarity_map, equivalence_classes_dict).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, {}

        m: Dict[Tuple[TNode, TNode], float] = {(u, v): 1.0 for u in self._nodes for v in self._nodes}

        for _ in range(self._max_iter):
            next_m: Dict[Tuple[TNode, TNode], float] = {}
            max_delta: float = 0.0

            for i in range(n):
                for j in range(i, n):
                    u, v = self._nodes[i], self._nodes[j]
                    if u == v:
                        next_m[(u, v)] = 1.0
                        continue

                    nbrs_u = self._adj.get(u, [])
                    nbrs_v = self._adj.get(v, [])

                    if not nbrs_u and not nbrs_v:
                        val = 1.0
                    elif not nbrs_u or not nbrs_v:
                        val = 0.0
                    else:
                        match_uv = sum(max(m.get((nu, nv), 0.0) for nv in nbrs_v) for nu in nbrs_u)
                        match_vu = sum(max(m.get((nv, nu), 0.0) for nu in nbrs_u) for nv in nbrs_v)
                        max_possible = max(len(nbrs_u), len(nbrs_v))
                        val = (match_uv + match_vu) / (2.0 * max_possible)

                    next_m[(u, v)] = val
                    next_m[(v, u)] = val

                    delta = abs(val - m.get((u, v), 1.0))
                    if delta > max_delta:
                        max_delta = delta

            m = next_m
            if max_delta < self._tol:
                break

        visited: Set[TNode] = set()
        classes: Dict[int, List[TNode]] = {}
        class_id: int = 0

        for u in self._nodes:
            if u not in visited:
                c_members: List[TNode] = [u]
                visited.add(u)
                for v in self._nodes:
                    if v not in visited and m.get((u, v), 0.0) >= class_threshold:
                        c_members.append(v)
                        visited.add(v)
                classes[class_id] = c_members
                class_id += 1

        return m, classes
