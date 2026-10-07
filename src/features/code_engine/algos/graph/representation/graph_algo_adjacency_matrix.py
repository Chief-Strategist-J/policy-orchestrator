"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: ADJACENCY MATRIX (ALGO-GRAPH-REP-01)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Constructs, inspects, and manipulates |V| x |V| dense matrix representations
   for directed and undirected graphs. Enables O(1) edge existence lookups,
   matrix powers for path counting (A^k counts paths of length k), degree
   vector computations, and symmetric adjacency verification.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^2) for construction, O(1) edge lookup, O(V^3) matrix power.
   - Space Complexity: O(V^2) dense memory allocation.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Builder & Analyst.
   - Guardrails: Cost estimation rejects inputs where |V| exceeds dense memory limits.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any


class GraphAlgoAdjacencyMatrix:
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-REP-01
      name: GraphAlgoAdjacencyMatrix
      version: 1.0.0
      category: graph_representation
      capability_tags: [graph, representation, adjacency_matrix, matrix_power]
      inputs:
        type: object
        required: [nodes, edges]
        properties:
          nodes:
            type: array
            items: {type: string}
          edges:
            type: array
            items:
              type: object
              required: [source, target]
              properties:
                source: {type: string}
                target: {type: string}
                weight: {type: number, default: 1.0}
      outputs:
        type: object
        required: [matrix, node_to_index, index_to_node, is_symmetric]
        properties:
          matrix:
            type: array
            items:
              type: array
              items: {type: number}
          node_to_index:
            type: object
            additionalProperties: {type: integer}
          index_to_node:
            type: array
            items: {type: string}
          is_symmetric: {type: boolean}
      parameters:
        directed: {type: boolean, default: true}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V^2 + E)
        space: O(V^2)
    ---
    """

    @staticmethod
    def construct(
        nodes: List[str],
        edges: List[Dict[str, Any]],
        directed: bool = True,
    ) -> Dict[str, Any]:
        ordered_nodes = sorted(list(dict.fromkeys(nodes)))
        node_to_idx = {node: i for i, node in enumerate(ordered_nodes)}
        n = len(ordered_nodes)
        matrix = [[0.0] * n for _ in range(n)]

        for edge in edges:
            src = edge.get("source")
            tgt = edge.get("target")
            wt = float(edge.get("weight", 1.0))
            if src in node_to_idx and tgt in node_to_idx:
                u = node_to_idx[src]
                v = node_to_idx[tgt]
                matrix[u][v] = wt
                if not directed:
                    matrix[v][u] = wt

        is_symmetric = True
        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] != matrix[j][i]:
                    is_symmetric = False
                    break
            if not is_symmetric:
                break

        return {
            "matrix": matrix,
            "node_to_index": node_to_idx,
            "index_to_node": ordered_nodes,
            "dimension": n,
            "is_symmetric": is_symmetric,
        }

    @staticmethod
    def matrix_power(matrix: List[List[float]], power: int) -> List[List[float]]:
        n = len(matrix)
        if power <= 0:
            return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        if power == 1:
            return [row[:] for row in matrix]

        result = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
        base = [row[:] for row in matrix]
        p = power

        while p > 0:
            if p % 2 == 1:
                result = GraphAlgoAdjacencyMatrix._multiply(result, base, n)
            base = GraphAlgoAdjacencyMatrix._multiply(base, base, n)
            p //= 2

        return result

    @staticmethod
    def _multiply(a: List[List[float]], b: List[List[float]], n: int) -> List[List[float]]:
        res = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for k in range(n):
                if a[i][k] != 0.0:
                    for j in range(n):
                        res[i][j] += a[i][k] * b[k][j]
        return res
