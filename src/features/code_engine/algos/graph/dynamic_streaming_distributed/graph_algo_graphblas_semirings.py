"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: GRAPHBLAS SEMIRINGS & ALGEBRA (ALGO-GRAPH-PAR-220)
================================================================================

1. OVERVIEW & OBJECTIVE:
   GraphBLAS Matrix Algebraic Engine for Graph Analytics.
   Formulates graph traversal, paths, and connectivity as sparse matrix-vector (SpMV)
   and sparse matrix-matrix (SpGEMM) multiplications over algebraic semirings
   (Boolean (LOR, LAND), Tropical (MIN, PLUS), Standard (PLUS, TIMES)).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(nnz(A)) per sparse matrix-vector product.
   - Space Complexity: O(nnz(A) + n) compressed sparse matrix representations.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): Node sequence defining dimension indices.
   - `edges` (List[Tuple[TNode, TNode, float]]): Weighted directed edges.

4. OUTPUT PARAMETERS:
   - `spmv_tropical_min_plus(vector)` (Dict[TNode, float]): Tropical matrix-vector step.
   - `spmv_boolean_or_and(vector)` (Dict[TNode, bool]): Boolean matrix-vector step.
   - `compute_shortest_paths_tropical(source, max_hops)` (Dict[TNode, float]): Shortest paths via repeated tropical products.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact equivalence to GraphBLAS C-API specification algebraic axioms.
================================================================================
"""

from typing import Callable, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGraphblasSemirings(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-220
      name: GraphAlgoGraphblasSemirings
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, graphblas, semiring, tropical_semiring, sparse_blas]
      inputs:
        type: object
        required: [nodes, edges]
        properties:
          nodes: {type: array}
          edges: {type: array}
      outputs:
        type: object
        properties:
          distances: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(nnz(A))
        space: O(V + M)
    ---
    """

    def __init__(self, nodes: List[TNode], edges: List[Tuple[TNode, TNode, float]]) -> None:
        """
        Initialize GraphBLAS sparse matrix structure.

        Args:
            nodes: List of vertices.
            edges: List of (u, v, weight) triples.
        """
        self._nodes: List[TNode] = list(nodes)
        self._node_to_idx: Dict[TNode, int] = {u: i for i, u in enumerate(self._nodes)}
        self._n: int = len(self._nodes)
        self._adj_entries: List[Tuple[int, int, float]] = []

        for u, v, w in edges:
            if u in self._node_to_idx and v in self._node_to_idx:
                self._adj_entries.append((self._node_to_idx[u], self._node_to_idx[v], float(w)))

    def spmv_tropical_min_plus(self, vector: Dict[TNode, float]) -> Dict[TNode, float]:
        """
        Compute y = A^T ._min_plus x (one step of Bellman-Ford/Dijkstra relaxation).

        Args:
            vector: Sparse input vector x mapping nodes to distance.

        Returns:
            Output vector y.
        """
        out_vec: Dict[int, float] = {}
        for u_idx, v_idx, w in self._adj_entries:
            u_node = self._nodes[u_idx]
            if u_node in vector:
                cand = vector[u_node] + w
                if v_idx not in out_vec or cand < out_vec[v_idx]:
                    out_vec[v_idx] = cand
        return {self._nodes[i]: val for i, val in out_vec.items()}

    def spmv_boolean_or_and(self, vector: Dict[TNode, bool]) -> Dict[TNode, bool]:
        """
        Compute y = A^T ._lor_land x (one step of BFS reachability).

        Args:
            vector: Sparse boolean vector mapping nodes to active status.

        Returns:
            Output boolean vector.
        """
        out_vec: Dict[int, bool] = {}
        for u_idx, v_idx, _ in self._adj_entries:
            u_node = self._nodes[u_idx]
            if vector.get(u_node, False):
                out_vec[v_idx] = True
        return {self._nodes[i]: True for i in out_vec}

    def compute_shortest_paths_tropical(self, source: TNode, max_hops: int = 100) -> Dict[TNode, float]:
        """
        Compute shortest paths from source via repeated tropical SpMV operations.

        Args:
            source: Source vertex.
            max_hops: Maximum relaxation rounds.

        Returns:
            Dictionary of shortest path distances.
        """
        dists: Dict[TNode, float] = {source: 0.0}
        for _ in range(max_hops):
            updated = self.spmv_tropical_min_plus(dists)
            changed = False
            for v, d in updated.items():
                if v not in dists or d < dists[v]:
                    dists[v] = d
                    changed = True
            if not changed:
                break
        return dists
