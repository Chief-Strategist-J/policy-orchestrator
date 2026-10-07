"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: CURRENT FLOW & RESISTANCE CENTRALITY (ALGO-GRAPH-CENT-112)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Random-walk current-flow betweenness and closeness centrality via electrical network
   analogy. Models edges as unit-conductance resistors, computes potential differences
   using Laplacian pseudo-inverse / Gaussian elimination, and accumulates effective
   resistances and current throughput across all source-sink node pairs.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^3) exact Laplacian pseudo-inverse solve.
   - Space Complexity: O(V^2) resistance and potential matrix storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Connected undirected graph adjacency.

4. OUTPUT PARAMETERS:
   - current_flow_betweenness: Dict[TNode, float] - Expected current throughput betweenness.
   - current_flow_closeness: Dict[TNode, float] - Inverse total effective resistance closeness.
   - effective_resistances: Dict[Tuple[TNode, TNode], float] - Resistance distance matrix.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Input must be a connected undirected graph.
   - Guardrails: Handles single-node or disconnected graphs gracefully.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoCurrentFlowCentrality(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-CENT-112
      name: GraphAlgoCurrentFlowCentrality
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, centrality, current_flow, random_walk_betweenness, effective_resistance, laplacian]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [current_flow_betweenness, current_flow_closeness, effective_resistances]
        properties:
          current_flow_betweenness: {type: object}
          current_flow_closeness: {type: object}
          effective_resistances: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^3)
        space: O(V^2)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Current Flow Centrality engine.

        Args:
            adjacency: Undirected connected graph adjacency.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _invert_matrix(self, matrix: List[List[float]]) -> List[List[float]]:
        n = len(matrix)
        augmented = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(matrix)]
        for i in range(n):
            pivot = i
            for r in range(i + 1, n):
                if abs(augmented[r][i]) > abs(augmented[pivot][i]):
                    pivot = r
            augmented[i], augmented[pivot] = augmented[pivot], augmented[i]
            diag = augmented[i][i]
            if abs(diag) < 1e-12:
                continue
            for c in range(2 * n):
                augmented[i][c] /= diag
            for r in range(n):
                if r != i:
                    factor = augmented[r][i]
                    for c in range(2 * n):
                        augmented[r][c] -= factor * augmented[i][c]
        return [[augmented[i][j + n] for j in range(n)] for i in range(n)]

    def compute_centrality(self) -> Tuple[Dict[TNode, float], Dict[TNode, float], Dict[Tuple[TNode, TNode], float]]:
        """
        Compute current-flow betweenness and closeness metrics.

        Returns:
            Tuple of (betweenness_map, closeness_map, effective_resistances_map).
        """
        n = len(self._nodes)
        if n <= 1:
            return {u: 0.0 for u in self._nodes}, {u: 0.0 for u in self._nodes}, {}

        idx = {u: i for i, u in enumerate(self._nodes)}
        laplacian = [[0.0] * n for _ in range(n)]
        for u in self._nodes:
            u_idx = idx[u]
            deg = len(self._adj.get(u, []))
            laplacian[u_idx][u_idx] = float(deg)
            for v in self._adj.get(u, []):
                v_idx = idx[v]
                laplacian[u_idx][v_idx] -= 1.0

        sub_n = n - 1
        sub_l = [[laplacian[i][j] for j in range(sub_n)] for i in range(sub_n)]
        sub_inv = self._invert_matrix(sub_l)

        c_inv = [[0.0] * n for _ in range(n)]
        for i in range(sub_n):
            for j in range(sub_n):
                c_inv[i][j] = sub_inv[i][j]

        eff_res: Dict[Tuple[TNode, TNode], float] = {}
        for i in range(n):
            for j in range(n):
                u, v = self._nodes[i], self._nodes[j]
                r_uv = c_inv[i][i] + c_inv[j][j] - 2.0 * c_inv[i][j]
                eff_res[(u, v)] = max(0.0, r_uv)

        closeness: Dict[TNode, float] = {}
        for i, u in enumerate(self._nodes):
            total_r = sum(eff_res[(u, v)] for v in self._nodes if u != v)
            closeness[u] = (float(n - 1) / total_r) if total_r > 0 else 0.0

        betweenness: Dict[TNode, float] = {u: 0.0 for u in self._nodes}
        for s_idx, s in enumerate(self._nodes):
            for t_idx in range(s_idx + 1, n):
                t = self._nodes[t_idx]
                potentials = [c_inv[i][s_idx] - c_inv[i][t_idx] for i in range(n)]
                for k, mid_node in enumerate(self._nodes):
                    if k == s_idx or k == t_idx:
                        continue
                    current_through_k = 0.0
                    for nbr in self._adj.get(mid_node, []):
                        nbr_idx = idx[nbr]
                        current_through_k += abs(potentials[k] - potentials[nbr_idx])
                    betweenness[mid_node] += 0.5 * current_through_k

        denom = float(n * (n - 1) * 0.5) if n > 2 else 1.0
        norm_betweenness = {u: val / denom for u, val in betweenness.items()}

        return norm_betweenness, closeness, eff_res
