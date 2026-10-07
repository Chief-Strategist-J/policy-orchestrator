"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: WALKTRAP RANDOM-WALK CLUSTERING (ALGO-GRAPH-COMM-156)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Walktrap hierarchical agglomerative community detection algorithm (Pons-Latapy).
   Computes vertex distance matrices based on t-step random walk transition probabilities:
   r_ij = sqrt(sum_k (P_ik^t - P_jk^t)^2 / deg(k)).
   Merges adjacent communities that minimize the within-community Ward distance delta sigma,
   producing a hierarchical dendrogram cut at maximum modularity Q.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(m * n^2) worst-case / O(n^2 log n) on sparse graphs.
   - Space Complexity: O(V^2) transition probability matrix.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Graph adjacency list.
   - t_steps: int - Random walk step length t (default: 3).

4. OUTPUT PARAMETERS:
   - best_partition: Dict[TNode, int] - Optimal community assignment maximizing modularity.
   - max_modularity: float - Peak modularity achieved.
   - num_communities: int - Final community count.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Connected undirected graph.
   - Guardrails: Degree normalization 1 / deg(k) accounts for hub vertex stationary traffic.
================================================================================
"""

import math
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoWalktrapCommunities(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-COMM-156
      name: GraphAlgoWalktrapCommunities
      version: 1.0.0
      category: graph_communities_spectral
      capability_tags: [graph, communities, walktrap, random_walk_distance, agglomerative_clustering, ward_distance]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          t_steps: {type: integer, default: 3}
      outputs:
        type: object
        required: [best_partition, max_modularity, num_communities]
        properties:
          best_partition: {type: object}
          max_modularity: {type: number}
          num_communities: {type: integer}
      parameters:
        t_steps: {type: integer, default: 3}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(n^2 log n)
        space: O(V^2)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], t_steps: int = 3) -> None:
        """
        Initialize the Walktrap community detector.

        Args:
            adjacency: Graph adjacency dictionary.
            t_steps: Random walk step length t (default: 3).
        """
        self._adj: Dict[TNode, Set[TNode]] = {u: set(nbrs) for u, nbrs in adjacency.items()}
        self._t: int = t_steps
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _mat_mul(self, a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
        n = len(a)
        c = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if a[i][k] != 0:
                    for j in range(n):
                        c[i][j] += a[i][k] * b[k][j]
        return c

    def detect_communities(self) -> Tuple[Dict[TNode, int], float, int]:
        """
        Execute Walktrap agglomerative clustering.

        Returns:
            Tuple of (best_partition_map, max_modularity_q, num_communities).
        """
        n = len(self._nodes)
        if n == 0:
            return {}, 0.0, 0
        if n == 1:
            return {self._nodes[0]: 0}, 0.0, 1

        idx = {u: i for i, u in enumerate(self._nodes)}
        degrees = [len(self._adj.get(u, set())) for u in self._nodes]
        total_edges = sum(degrees) // 2

        p_mat = [[0.0] * n for _ in range(n)]
        for u in self._nodes:
            u_i = idx[u]
            deg = degrees[u_i]
            if deg > 0:
                for v in self._adj.get(u, set()):
                    p_mat[u_i][idx[v]] = 1.0 / float(deg)

        pt = list(p_mat)
        for _ in range(self._t - 1):
            pt = self._mat_mul(pt, p_mat)

        dist: Dict[Tuple[int, int], float] = {}
        for i in range(n):
            for j in range(i + 1, n):
                sq_sum = 0.0
                for k in range(n):
                    deg_k = degrees[k]
                    if deg_k > 0:
                        diff = pt[i][k] - pt[j][k]
                        sq_sum += (diff * diff) / float(deg_k)
                d_val = math.sqrt(sq_sum)
                dist[(i, j)] = d_val
                dist[(j, i)] = d_val

        communities: Dict[int, Set[TNode]] = {i: {self._nodes[i]} for i in range(n)}
        best_part: Dict[TNode, int] = {u: i for i, u in enumerate(self._nodes)}
        best_q: float = -1.0

        def _compute_q(comm_map: Dict[int, Set[TNode]]) -> float:
            if total_edges == 0:
                return 0.0
            two_m = float(2 * total_edges)
            q = 0.0
            for members in comm_map.values():
                e_c = 0
                k_c = sum(len(self._adj.get(u, set())) for u in members)
                m_list = list(members)
                for i in range(len(m_list)):
                    for j in range(i + 1, len(m_list)):
                        if m_list[j] in self._adj.get(m_list[i], set()):
                            e_c += 1
                q += (float(e_c) / float(total_edges)) - ((float(k_c) / two_m) ** 2)
            return q

        best_q = _compute_q(communities)

        while len(communities) > 1:
            comm_keys = list(communities.keys())
            best_pair = None
            min_merge_dist = float("inf")

            for i in range(len(comm_keys)):
                c1 = comm_keys[i]
                for j in range(i + 1, len(comm_keys)):
                    c2 = comm_keys[j]
                    adjacent = any(v in self._adj.get(u, set()) for u in communities[c1] for v in communities[c2])
                    if not adjacent:
                        continue

                    avg_d = sum(dist[(idx[u], idx[v])] for u in communities[c1] for v in communities[c2])
                    avg_d /= float(len(communities[c1]) * len(communities[c2]))
                    if avg_d < min_merge_dist:
                        min_merge_dist = avg_d
                        best_pair = (c1, c2)

            if best_pair is None:
                c1, c2 = comm_keys[0], comm_keys[1]
            else:
                c1, c2 = best_pair

            communities[c1] = communities[c1] | communities[c2]
            del communities[c2]

            curr_q = _compute_q(communities)
            if curr_q > best_q:
                best_q = curr_q
                best_part = {}
                for c_id, members in enumerate(communities.values()):
                    for u in members:
                        best_part[u] = c_id

        unique_c = sorted(list(set(best_part.values())))
        compact = {old: new for new, old in enumerate(unique_c)}
        final_part = {u: compact[best_part[u]] for u in self._nodes}

        return final_part, best_q, len(unique_c)
