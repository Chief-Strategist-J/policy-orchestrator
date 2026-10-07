"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DISTRIBUTED TRIANGLE COUNTING (ALGO-GRAPH-DIST-226)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Distributed Triangle Counting Engine.
   Computes exact global and local triangle counts across partitioned edge distributions
   by applying degree-ordered directed acyclic orientation (u -> v iff deg(u) < deg(v))
   and batched edge-iterator neighbor list intersections.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M^1.5) aggregate operations across nodes.
   - Space Complexity: O(V + M) partitioned forward adjacency sets.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `edges` (List[Tuple[TNode, TNode]]): Undirected graph edge list.
   - `num_partitions` (int): Number of simulated distributed compute partitions.

4. OUTPUT PARAMETERS:
   - `count_global_triangles()` (int): Total number of unique 3-cliques.
   - `count_local_triangles()` (Dict[TNode, int]): Per-vertex triangle participation counts.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Degree orientation eliminates all duplicate triangle enumeration across shards.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDistributedTriangleCounting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DIST-226
      name: GraphAlgoDistributedTriangleCounting
      version: 1.0.0
      category: graph_distributed
      capability_tags: [graph, distributed, triangle_counting, degree_orientation, edge_iterator]
      inputs:
        type: object
        required: [edges]
        properties:
          edges: {type: array}
          num_partitions: {type: integer, minimum: 1}
      outputs:
        type: object
        properties:
          global_triangles: {type: integer}
          local_triangles: {type: object}
      parameters:
        num_partitions: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M^1.5)
        space: O(V + M)
    ---
    """

    def __init__(self, edges: List[Tuple[TNode, TNode]], num_partitions: int = 4) -> None:
        """
        Initialize distributed triangle counting structures.

        Args:
            edges: List of undirected (u, v) edge pairs.
            num_partitions: Number of virtual distributed partitions.
        """
        self._num_parts: int = max(1, num_partitions)
        self._deg: Dict[TNode, int] = defaultdict(int)

        clean_edges: Set[Tuple[TNode, TNode]] = set()
        for u, v in edges:
            if u != v:
                pair = (u, v) if str(u) < str(v) else (v, u)
                if pair not in clean_edges:
                    clean_edges.add(pair)
                    self._deg[u] += 1
                    self._deg[v] += 1

        self._forward_adj: Dict[TNode, Set[TNode]] = defaultdict(set)
        for u, v in clean_edges:
            if self._deg[u] < self._deg[v] or (self._deg[u] == self._deg[v] and str(u) < str(v)):
                self._forward_adj[u].add(v)
            else:
                self._forward_adj[v].add(u)

        self._sharded_edges: Dict[int, List[Tuple[TNode, TNode]]] = defaultdict(list)
        for u, neighbors in self._forward_adj.items():
            for v in neighbors:
                p_id = hash((str(u), str(v))) % self._num_parts
                self._sharded_edges[p_id].append((u, v))

    def count_global_triangles(self) -> int:
        """
        Count global triangles across all distributed edge partitions.

        Returns:
            Integer total triangle count.
        """
        total = 0
        for p_id in range(self._num_parts):
            for u, v in self._sharded_edges[p_id]:
                u_nbrs = self._forward_adj.get(u, set())
                v_nbrs = self._forward_adj.get(v, set())
                common = u_nbrs.intersection(v_nbrs)
                total += len(common)
        return total

    def count_local_triangles(self) -> Dict[TNode, int]:
        """
        Compute per-vertex local triangle participation counts.

        Returns:
            Dictionary mapping node to its triangle count.
        """
        local_counts: Dict[TNode, int] = defaultdict(int)
        for p_id in range(self._num_parts):
            for u, v in self._sharded_edges[p_id]:
                u_nbrs = self._forward_adj.get(u, set())
                v_nbrs = self._forward_adj.get(v, set())
                common = u_nbrs.intersection(v_nbrs)
                for w in common:
                    local_counts[u] += 1
                    local_counts[v] += 1
                    local_counts[w] += 1
        return dict(local_counts)
