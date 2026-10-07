"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DISTRIBUTED BFS WITH 2D PARTITIONING (ALGO-GRAPH-DIST-225)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Distributed 2D Grid Partitioned BFS Engine.
   Splits graph adjacency matrix across a sqrt(P) x sqrt(P) processor mesh,
   executing expand phases along processor columns and fold/reduction phases along
   processor rows to reduce cluster network message volume to O(V / sqrt(P)) per step.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + M) aggregate work, O(diam(G)) synchronized supersteps.
   - Space Complexity: O((V + M) / P) per processor tile.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): List of all nodes.
   - `edges` (List[Tuple[TNode, TNode]]): Directed graph edges.
   - `grid_dim` (int): Dimension of 2D processor grid (P = grid_dim^2).

4. OUTPUT PARAMETERS:
   - `compute_bfs(source)` (Dict[TNode, int]): Shortest hop distance from source to all reachable nodes.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact shortest distance matching sequential BFS with 2D distributed communication pattern.
================================================================================
"""

import math
from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDistributedBfs2dPartitioning(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DIST-225
      name: GraphAlgoDistributedBfs2dPartitioning
      version: 1.0.0
      category: graph_distributed
      capability_tags: [graph, distributed, 2d_partitioning, bfs, processor_grid, graph500]
      inputs:
        type: object
        required: [nodes, edges]
        properties:
          nodes: {type: array}
          edges: {type: array}
          grid_dim: {type: integer, minimum: 1}
      outputs:
        type: object
        properties:
          distances: {type: object}
      parameters:
        grid_dim: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + M)
        space: O((V + M) / P)
    ---
    """

    def __init__(self, nodes: List[TNode], edges: List[Tuple[TNode, TNode]], grid_dim: int = 2) -> None:
        """
        Initialize 2D grid partitioned distributed graph.

        Args:
            nodes: List of vertices.
            edges: List of directed edges.
            grid_dim: Processor grid dimension R = C = grid_dim.
        """
        self._nodes: List[TNode] = list(nodes)
        self._grid_dim: int = max(1, grid_dim)
        self._node_to_idx: Dict[TNode, int] = {u: i for i, u in enumerate(self._nodes)}
        self._n: int = len(self._nodes)

        block_size = max(1, (self._n + self._grid_dim - 1) // self._grid_dim)
        self._block_size = block_size

        self._tiles: Dict[Tuple[int, int], List[Tuple[int, int]]] = defaultdict(list)
        for u, v in edges:
            if u in self._node_to_idx and v in self._node_to_idx:
                u_idx = self._node_to_idx[u]
                v_idx = self._node_to_idx[v]
                col = min(self._grid_dim - 1, u_idx // block_size)
                row = min(self._grid_dim - 1, v_idx // block_size)
                self._tiles[(row, col)].append((u_idx, v_idx))

    def compute_bfs(self, source: TNode) -> Dict[TNode, int]:
        """
        Execute 2D-partitioned distributed BFS.

        Args:
            source: Source vertex.

        Returns:
            Dictionary mapping reached nodes to hop distances.
        """
        if source not in self._node_to_idx:
            return {}

        src_idx = self._node_to_idx[source]
        distances: Dict[int, int] = {src_idx: 0}
        frontier: Set[int] = {src_idx}
        depth = 0

        while frontier:
            depth += 1
            col_frontiers: Dict[int, Set[int]] = defaultdict(set)
            for u_idx in frontier:
                col = min(self._grid_dim - 1, u_idx // self._block_size)
                col_frontiers[col].add(u_idx)

            row_candidates: Dict[int, Set[int]] = defaultdict(set)
            for (r, c), edge_list in self._tiles.items():
                active_col = col_frontiers[c]
                if active_col:
                    for u_idx, v_idx in edge_list:
                        if u_idx in active_col and v_idx not in distances:
                            row_candidates[r].add(v_idx)

            next_frontier: Set[int] = set()
            for r, cands in row_candidates.items():
                for v_idx in cands:
                    if v_idx not in distances:
                        distances[v_idx] = depth
                        next_frontier.add(v_idx)

            frontier = next_frontier

        return {self._nodes[idx]: d for idx, d in distances.items()}
