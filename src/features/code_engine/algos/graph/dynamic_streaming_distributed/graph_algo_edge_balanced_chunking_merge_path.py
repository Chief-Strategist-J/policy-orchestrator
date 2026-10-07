"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EDGE-BALANCED CHUNKING & MERGE-PATH (ALGO-GRAPH-ENG-242)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Edge-Balanced Chunking and Merge-Path Work Balancing Engine.
   Partitions irregular graph edge workloads across P threads or workers by computing
   prefix sums over vertex degree sequences, guaranteeing each worker receives
   an approximately equal workload of ~ M / P edges even under extreme degree skew.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V) prefix sum construction, O(P log V) binary search chunking.
   - Space Complexity: O(V) prefix sum degree arrays.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Graph topological layout.
   - `num_workers` (int): Number of target workers/threads P.

4. OUTPUT PARAMETERS:
   - `compute_edge_balanced_chunks()` (List[Dict[str, Any]]): Worker chunk intervals and edge counts.
   - `get_imbalance_ratio()` (float): Max worker edges / Mean worker edges.

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: Worker edge variance bounded strictly within max_degree(G).
================================================================================
"""

import bisect
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEdgeBalancedChunkingMergePath(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENG-242
      name: GraphAlgoEdgeBalancedChunkingMergePath
      version: 1.0.0
      category: graph_engineering
      capability_tags: [graph, engineering, load_balancing, edge_chunking, merge_path, prefix_sum]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          num_workers: {type: integer, minimum: 1}
      outputs:
        type: object
        properties:
          chunks: {type: array}
          imbalance_ratio: {type: number}
      parameters:
        num_workers: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + P log V)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], num_workers: int = 4) -> None:
        """
        Initialize edge-balanced chunking engine.

        Args:
            adjacency: Adjacency map.
            num_workers: Number of partitions P.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._num_workers: int = max(1, num_workers)
        self._nodes: List[TNode] = sorted(list(self._adj.keys()), key=lambda x: str(x))
        self._degrees: List[int] = [len(self._adj[u]) for u in self._nodes]

        self._prefix_sums: List[int] = [0]
        for d in self._degrees:
            self._prefix_sums.append(self._prefix_sums[-1] + d)

        self._total_edges: int = self._prefix_sums[-1]

    def compute_edge_balanced_chunks(self) -> List[Dict[str, Any]]:
        """
        Divide vertex range into P edge-balanced chunks via prefix sum binary searches.

        Returns:
            List of worker chunk specifications.
        """
        if not self._nodes:
            return []

        target_per_worker = self._total_edges / float(self._num_workers)
        chunks: List[Dict[str, Any]] = []
        curr_start_idx = 0

        for w in range(self._num_workers):
            target_edge_cum = int(round((w + 1) * target_per_worker))
            if w == self._num_workers - 1:
                end_idx = len(self._nodes)
            else:
                end_idx = bisect.bisect_left(self._prefix_sums, target_edge_cum) - 1
                end_idx = max(curr_start_idx + 1, min(len(self._nodes), end_idx))

            chunk_nodes = self._nodes[curr_start_idx:end_idx]
            edge_count = self._prefix_sums[end_idx] - self._prefix_sums[curr_start_idx]

            chunks.append({
                "worker_id": w,
                "start_node_idx": curr_start_idx,
                "end_node_idx": end_idx,
                "nodes": chunk_nodes,
                "edge_count": edge_count,
            })

            curr_start_idx = end_idx
            if curr_start_idx >= len(self._nodes):
                break

        return chunks

    def get_imbalance_ratio(self) -> float:
        """
        Compute maximum worker load over average worker load.

        Returns:
            Imbalance ratio >= 1.0.
        """
        chunks = self.compute_edge_balanced_chunks()
        if not chunks:
            return 1.0
        edge_counts = [c["edge_count"] for c in chunks]
        mean_edges = sum(edge_counts) / len(edge_counts)
        if mean_edges == 0:
            return 1.0
        return max(edge_counts) / mean_edges
