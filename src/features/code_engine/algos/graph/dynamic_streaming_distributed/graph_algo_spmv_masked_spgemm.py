"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: SPMV & MASKED SPGEMM (ALGO-GRAPH-PAR-221)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Sparse Matrix-Vector (SpMV) and Masked Sparse Matrix-Matrix (SpGEMM) Engine.
   Executes high-performance sparse graph products with selective Hadamard structural
   masks M: C = (A * B) .* M, avoiding intermediate combinatorial explosion during
   triangle counting, 2-hop metapath enumeration, and structural similarity evaluation.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(nnz(M) * d_avg) for masked SpGEMM vs O(V^3) dense.
   - Space Complexity: O(nnz(A) + nnz(B) + nnz(M)) sparse coordinate storage.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `matrix_a` (Dict[Tuple[TNode, TNode], float]): Sparse coordinate matrix A.
   - `matrix_b` (Dict[Tuple[TNode, TNode], float]): Sparse coordinate matrix B.

4. OUTPUT PARAMETERS:
   - `spmv(matrix_a, vec_x)` (Dict[TNode, float]): Sparse matrix-vector product.
   - `masked_spgemm(matrix_a, matrix_b, mask_m)` (Dict[Tuple[TNode, TNode], float]): Masked matrix-matrix product.
   - `count_triangles_masked(adjacency_matrix)` (int): Exact triangle count via masked trace (L * L) .* L.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Computation is strictly skipped for any coordinate (i, j) outside mask M.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSpmvMaskedSpgemm(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-221
      name: GraphAlgoSpmvMaskedSpgemm
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, spmv, spgemm, masked_spgemm, sparse_linear_algebra, triangles]
      inputs:
        type: object
        properties: {}
      outputs:
        type: object
        properties:
          triangle_count: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(nnz(M) * d)
        space: O(nnz(A) + nnz(B))
    ---
    """

    def __init__(self) -> None:
        """Initialize SpMV and Masked SpGEMM operator instance."""
        pass

    def spmv(self, matrix: Dict[Tuple[TNode, TNode], float], vector: Dict[TNode, float]) -> Dict[TNode, float]:
        """
        Compute y = A * x for sparse matrix A and sparse vector x.

        Args:
            matrix: Map from (row, col) to non-zero weight.
            vector: Map from col to value.

        Returns:
            Result vector y mapping row to scalar.
        """
        out: Dict[TNode, float] = defaultdict(float)
        for (r, c), val in matrix.items():
            if c in vector:
                out[r] += val * vector[c]
        return dict(out)

    def masked_spgemm(
        self,
        matrix_a: Dict[Tuple[TNode, TNode], float],
        matrix_b: Dict[Tuple[TNode, TNode], float],
        mask: Set[Tuple[TNode, TNode]],
    ) -> Dict[Tuple[TNode, TNode], float]:
        """
        Compute C = (A * B) .* M evaluating entries only at coordinates permitted by mask.

        Args:
            matrix_a: Sparse matrix A.
            matrix_b: Sparse matrix B.
            mask: Allowed (i, j) output coordinate set M.

        Returns:
            Result matrix C.
        """
        rows_a: Dict[TNode, Dict[TNode, float]] = defaultdict(dict)
        for (i, k), v in matrix_a.items():
            rows_a[i][k] = v

        cols_b: Dict[TNode, Dict[TNode, float]] = defaultdict(dict)
        for (k, j), v in matrix_b.items():
            cols_b[j][k] = v

        result: Dict[Tuple[TNode, TNode], float] = {}

        for i, j in mask:
            if i in rows_a and j in cols_b:
                row_i = rows_a[i]
                col_j = cols_b[j]
                common_k = set(row_i.keys()).intersection(col_j.keys())
                if common_k:
                    dot = sum(row_i[k] * col_j[k] for k in common_k)
                    if dot != 0.0:
                        result[(i, j)] = dot

        return result

    def count_triangles(self, adj_matrix: Dict[Tuple[TNode, TNode], float]) -> int:
        """
        Count triangles via masked product trace: sum((L * L) .* L) where L is lower triangular.

        Args:
            adj_matrix: Symmetric adjacency matrix of unweighted graph.

        Returns:
            Exact triangle count.
        """
        lower_matrix: Dict[Tuple[TNode, TNode], float] = {}
        for (u, v), w in adj_matrix.items():
            if str(u) > str(v):
                lower_matrix[(u, v)] = 1.0

        mask = set(lower_matrix.keys())
        masked_prod = self.masked_spgemm(lower_matrix, lower_matrix, mask)
        return int(sum(masked_prod.values()))
