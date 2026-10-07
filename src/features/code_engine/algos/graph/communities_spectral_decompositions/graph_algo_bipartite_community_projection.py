"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Barber Bipartite Modularity Community Detection (ALGO-GRAPH-COMM-164)

1. OVERVIEW & OBJECTIVE:
Detect communities in bipartite networks using Barber's modularity formulation, optimizing
the allocation of two disjoint vertex sets (e.g., users and items) into shared or linked
community clusters without projecting to unipartite graphs.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for adjacency, degree vectors, and community labels.
- Time Complexity: O(iterations * |E|) for bipartite modularity optimization passes.
- Invariants:
  - Vertices are partitioned into two disjoint bipartite sets (U and V).
  - Cross-set modularity matrix B_ij = A_ij - (k_u * d_v) / m is evaluated.

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Undirected bipartite adjacency representation.
- `set_u` (Iterable[TNode]): Primary node partition.
- `set_v` (Iterable[TNode]): Secondary disjoint node partition.
- `max_iterations` (int): Maximum optimization passes (default: 50).

4. OUTPUT PARAMETERS:
- `Dict[TNode, int]`: Community assignment mapping for all vertices across both bipartite sets.
- `float`: Final Barber modularity score (Q_b).

5. AGENT CONTRACT:
- Role: Community detection analyst for two-mode / bipartite interaction networks.
- Rules: Enforce strict partition verification (no within-set edges).
- Guardrails: Non-bipartite edges raise ValueError.
"""

from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class BipartiteCommunityResult(Generic[TNode]):
    """
    Result container for bipartite community partitioning.
    """
    assignments: Dict[TNode, int]
    modularity: float
    num_communities: int


class BipartiteCommunityDetector(Generic[TNode]):
    """
    Implements Barber's bipartite modularity optimization.

    ```yaml
    contract_id: ALGO-GRAPH-COMM-164
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      set_u: Iterable[TNode]
      set_v: Iterable[TNode]
    outputs:
      result: BipartiteCommunityResult[TNode]
    parameters:
      max_iterations: int
    capability_tags:
      - graph
      - bipartite
      - community_detection
      - modularity
    purity: deterministic
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(iterations * |E|)
      space: O(|V| + |E|)
    ```
    """

    def __init__(self, max_iterations: int = 50) -> None:
        """
        Args:
            max_iterations: Maximum optimization iterations.
        """
        self._max_iterations = max_iterations

    def detect(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        set_u: Iterable[TNode],
        set_v: Iterable[TNode],
    ) -> BipartiteCommunityResult[TNode]:
        """
        Optimizes bipartite community modularity according to Barber's objective.

        Args:
            adjacency: Graph adjacency map.
            set_u: Nodes in partition U.
            set_v: Nodes in partition V.

        Returns:
            BipartiteCommunityResult containing node assignments and Barber modularity.
        """
        u_nodes: Set[TNode] = set(set_u)
        v_nodes: Set[TNode] = set(set_v)
        if u_nodes.intersection(v_nodes):
            raise ValueError("Bipartite node sets U and V must be disjoint.")

        adj: Dict[TNode, Set[TNode]] = {u: set(adjacency.get(u, ())) for u in u_nodes | v_nodes}
        
        for u in u_nodes:
            for neighbor in adj[u]:
                if neighbor not in v_nodes:
                    raise ValueError(f"Edge {u} -> {neighbor} violates bipartite structure.")

        m_edges: int = sum(len(adj[u]) for u in u_nodes)
        if m_edges == 0:
            all_nodes = list(u_nodes | v_nodes)
            return BipartiteCommunityResult(
                assignments={node: idx for idx, node in enumerate(all_nodes)},
                modularity=0.0,
                num_communities=len(all_nodes),
            )

        deg_u: Dict[TNode, int] = {u: len(adj[u]) for u in u_nodes}
        deg_v: Dict[TNode, int] = {v: len(adj[v]) for v in v_nodes}

        assignments: Dict[TNode, int] = {}
        for idx, u in enumerate(sorted(u_nodes, key=lambda x: str(x))):
            assignments[u] = idx
        for v in v_nodes:
            assignments[v] = 0

        for _ in range(self._max_iterations):
            changed = False
            for v in v_nodes:
                comm_weights: Dict[int, float] = {}
                for u in adj[v]:
                    c = assignments[u]
                    comm_weights[c] = comm_weights.get(c, 0.0) + 1.0 - (deg_u[u] * deg_v[v]) / m_edges
                if comm_weights:
                    best_c = max(comm_weights.items(), key=lambda item: item[1])[0]
                    if assignments[v] != best_c:
                        assignments[v] = best_c
                        changed = True

            for u in u_nodes:
                comm_weights = {}
                for v in adj[u]:
                    c = assignments[v]
                    comm_weights[c] = comm_weights.get(c, 0.0) + 1.0 - (deg_u[u] * deg_v[v]) / m_edges
                if comm_weights:
                    best_c = max(comm_weights.items(), key=lambda item: item[1])[0]
                    if assignments[u] != best_c:
                        assignments[u] = best_c
                        changed = True

            if not changed:
                break

        q_b = self._compute_barber_modularity(adj, u_nodes, v_nodes, assignments, deg_u, deg_v, m_edges)
        unique_comms = set(assignments.values())
        return BipartiteCommunityResult(
            assignments=assignments,
            modularity=q_b,
            num_communities=len(unique_comms),
        )

    def _compute_barber_modularity(
        self,
        adj: Dict[TNode, Set[TNode]],
        u_nodes: Set[TNode],
        v_nodes: Set[TNode],
        assignments: Dict[TNode, int],
        deg_u: Dict[TNode, int],
        deg_v: Dict[TNode, int],
        m_edges: int,
    ) -> float:
        score = 0.0
        for u in u_nodes:
            cu = assignments[u]
            du = deg_u[u]
            for v in v_nodes:
                if assignments[v] == cu:
                    a_uv = 1.0 if v in adj[u] else 0.0
                    score += a_uv - (du * deg_v[v]) / m_edges
        return score / m_edges
