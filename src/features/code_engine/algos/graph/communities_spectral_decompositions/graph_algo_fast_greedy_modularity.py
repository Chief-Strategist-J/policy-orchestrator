"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CLASET-NEWMAN-MOORE FAST GREEDY (ALGO-GRAPH-COMM-157)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Clauset-Newman-Moore (CNM) fast greedy modularity maximization algorithm.
   Maintains a sparse matrix of modularity delta gains Delta Q_ij = 2 * (e_ij - a_i * a_j)
   and a max-heap of community pairs to agglomerate communities in O(m * d * log n) time.
   Constructs a dendrogram of community merges and identifies the global maximum modularity partition.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m * d * log n) fast max-heap agglomeration.
   - Space Complexity: O(V + E) delta Q sparse map.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Undirected graph adjacency list.

4. OUTPUT PARAMETERS:
   - best_partition: Dict[TNode, int] - Optimal community assignment map.
   - max_modularity: float - Maximum modularity Q achieved.
   - num_communities: int - Number of communities in the best partition.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph with at least one edge.
   - Guardrails: Max-heap updates maintain Delta Q consistency upon community merges.
================================================================================
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoFastGreedyModularity(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-157
      name: GraphAlgoFastGreedyModularity
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, clauset_newman_moore, fast_greedy, modularity_maximization, agglomerative]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [best_partition, max_modularity, num_communities]
        properties:
          best_partition: {type: object}
          max_modularity: {type: number}
          num_communities: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(m * d * log n)
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Fast Greedy Modularity optimizer.

        Args:
            adjacency: Graph adjacency dictionary.
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def detect_communities(self) -> Tuple[Dict[TNode, int], float, int]:
        """
        Execute Clauset-Newman-Moore fast greedy modularity agglomeration.

        Returns:
            Tuple of (best_partition_map, max_modularity_q, num_communities).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, 0.0, 0
        if n == 1:
            return {self._nodes[0]: 0}, 0.0, 1

        degrees: Dict[TNode, int] = {u: len(self._adj.get(u, set())) for u in self._nodes}
        total_edges = sum(degrees.values()) // 2
        if total_edges == 0:
            return {u: i for i, u in enumerate(self._nodes)}, 0.0, n

        two_m = float(2 * total_edges)
        a: Dict[int, float] = {i: float(degrees[self._nodes[i]]) / two_m for i in range(n)}

        delta_q: Dict[Tuple[int, int], float] = {}
        heap: List[Tuple[float, int, int]] = []

        for i in range(n):
            u = self._nodes[i]
            for v in self._adj.get(u, set()):
                j = self._nodes.index(v)
                if i < j:
                    dq = (1.0 / float(total_edges)) - 2.0 * (a[i] * a[j])
                    delta_q[(i, j)] = dq
                    heapq.heappush(heap, (-dq, i, j))

        communities: Dict[int, Set[TNode]] = {i: {self._nodes[i]} for i in range(n)}
        active_comms: Set[int] = set(range(n))
        curr_q: float = sum(- (a[i] ** 2) for i in range(n))
        best_q: float = curr_q
        best_part: Dict[TNode, int] = {u: i for i, u in enumerate(self._nodes)}

        while len(active_comms) > 1 and heap:
            neg_dq, i, j = heapq.heappop(heap)
            dq = -neg_dq

            if i not in active_comms or j not in active_comms:
                continue

            curr_q += dq
            communities[i] = communities[i] | communities[j]
            active_comms.remove(j)
            del communities[j]
            a[i] += a[j]

            if curr_q > best_q:
                best_q = curr_q
                best_part = {}
                for c_id, members in enumerate(communities.values()):
                    for u in members:
                        best_part[u] = c_id

            for k in active_comms:
                if k == i:
                    continue
                pair_ik = (min(i, k), max(i, k))
                pair_jk = (min(j, k), max(j, k))

                dq_ik = delta_q.get(pair_ik, None)
                dq_jk = delta_q.get(pair_jk, None)

                if dq_ik is not None and dq_jk is not None:
                    new_dq = dq_ik + dq_jk
                elif dq_ik is not None:
                    new_dq = dq_ik - 2.0 * a[j] * a[k]
                elif dq_jk is not None:
                    new_dq = dq_jk - 2.0 * a[i] * a[k]
                else:
                    continue

                delta_q[pair_ik] = new_dq
                heapq.heappush(heap, (-new_dq, pair_ik[0], pair_ik[1]))

        unique_c = sorted(list(set(best_part.values())))
        compact = {old: new for new, old in enumerate(unique_c)}
        final_part = {u: compact[best_part[u]] for u in self._nodes}

        return final_part, best_q, len(unique_c)
