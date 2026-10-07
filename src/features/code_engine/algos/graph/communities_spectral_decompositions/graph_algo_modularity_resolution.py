"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: MODULARITY & RESOLUTION SWEEP (ALGO-GRAPH-COMM-151)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Newman-Girvan modularity evaluation and Reichardt-Bornholdt resolution parameter gamma sweeping.
   Computes partition modularity Q = (1 / 2m) * sum_{ij} [A_ij - gamma * (k_i * k_j) / 2m] * delta(c_i, c_j).
   Identifies resolution limits and tracks partition stability across resolution scales gamma.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m) linear-time partition modularity evaluation.
   - Space Complexity: O(V + C) community membership indices.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.
   - partition: Dict[TNode, int] - Node to community ID assignment map.
   - gamma: float - Resolution parameter (default: 1.0).

4. OUTPUT PARAMETERS:
   - modularity_q: float - Modularity score in [-0.5, 1.0].
   - internal_edges: Dict[int, int] - Count of internal edges per community.
   - community_degrees: Dict[int, int] - Sum of degrees per community.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph with at least one edge.
   - Guardrails: Handles single-community or all-singleton partitions without division errors.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoModularityResolution(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-151
      name: GraphAlgoModularityResolution
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, modularity, resolution_limit, reichardt_bornholdt, partition_quality]
      inputs:
        type: object
        required: [adjacency, partition]
        properties:
          adjacency: {type: object}
          partition: {type: object}
          gamma: {type: number, default: 1.0}
      outputs:
        type: object
        required: [modularity_q, internal_edges, community_degrees]
        properties:
          modularity_q: {type: number}
          internal_edges: {type: object}
          community_degrees: {type: object}
      parameters:
        gamma: {type: number, default: 1.0}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m)
        space: O(V + C)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        partition: Dict[TNode, int],
        gamma: float = 1.0,
    ) -> None:
        """
        Initialize the Modularity Resolution evaluator.

        Args:
            adjacency: Graph adjacency dictionary.
            partition: Mapping of node to community identifier.
            gamma: Resolution parameter.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._part: Dict[TNode, int] = partition
        self._gamma: float = gamma
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def evaluate_modularity(self) -> Tuple[float, Dict[int, int], Dict[int, int]]:
        """
        Compute Newman-Girvan modularity Q at resolution gamma.

        Returns:
            Tuple of (modularity_q, internal_edges_dict, community_degrees_dict).
        """
        degrees: Dict[TNode, int] = {u: len(self._adj.get(u, set())) for u in self._nodes}
        total_edges: int = sum(degrees.values()) // 2
        if total_edges == 0:
            return 0.0, {}, {}

        two_m = float(2 * total_edges)
        internal_e: Dict[int, int] = {}
        comm_deg: Dict[int, int] = {}

        for u in self._nodes:
            c_u = self._part.get(u, -1)
            comm_deg[c_u] = comm_deg.get(c_u, 0) + degrees[u]
            for v in self._adj.get(u, set()):
                if str(u) < str(v) and self._part.get(v, -1) == c_u:
                    internal_e[c_u] = internal_e.get(c_u, 0) + 1

        q: float = 0.0
        for c in comm_deg:
            e_c = float(internal_e.get(c, 0))
            k_c = float(comm_deg[c])
            q += (e_c / float(total_edges)) - self._gamma * ((k_c / two_m) ** 2)

        return q, internal_e, comm_deg
