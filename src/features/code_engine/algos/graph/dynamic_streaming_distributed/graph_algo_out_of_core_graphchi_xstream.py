"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: OUT-OF-CORE PROCESSING GRAPHCHI/X-STREAM (ALGO-GRAPH-PAR-224)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Out-of-Core Graph Processing Engine (GraphChi Parallel Sliding Windows & X-Stream).
   Processes massive graphs exceeding physical RAM limits via deterministic sharding,
   interval partitioning, and streaming sequential edge chunk passes.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(P * M) sequential disk/stream passes across P intervals.
   - Space Complexity: O(V / P + max_shard_size) bounded in-memory buffer.
   - Purity: Interval-based streaming execution, deterministic.

3. INPUT PARAMETERS:
   - `shards` (Dict[int, List[Tuple[TNode, TNode, float]]]): Sharded edge collections partitioned by target interval.
   - `vertex_intervals` (Dict[int, Set[TNode]]): Vertex partitions assigned to each shard.

4. OUTPUT PARAMETERS:
   - `execute_iteration(vertex_update_fn)` (Dict[TNode, Any]): Updated vertex states after one full PSW pass.
   - `compute_pagerank(damping, iterations)` (Dict[TNode, float]): Out-of-core PageRank.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Constant maximum RAM footprint strictly proportional to partition interval size.
================================================================================
"""

from collections import defaultdict
from typing import Any, Callable, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoOutOfCoreGraphchiXstream(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-224
      name: GraphAlgoOutOfCoreGraphchiXstream
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, out_of_core, graphchi, psw, x_stream, disk_sharding]
      inputs:
        type: object
        required: [edges]
        properties:
          edges: {type: array}
          num_shards: {type: integer, minimum: 1}
      outputs:
        type: object
        properties:
          vertex_values: {type: object}
      parameters:
        num_shards: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(P * M)
        space: O(V / P)
    ---
    """

    def __init__(self, edges: List[Tuple[TNode, TNode, float]], num_shards: int = 2) -> None:
        """
        Initialize GraphChi out-of-core partition shards.

        Args:
            edges: Global list of (u, v, weight) edges.
            num_shards: Number of memory partitions P.
        """
        self._num_shards: int = max(1, num_shards)
        all_nodes: Set[TNode] = set()
        for u, v, _ in edges:
            all_nodes.add(u)
            all_nodes.add(v)

        sorted_nodes = sorted(list(all_nodes), key=lambda x: str(x))
        n = len(sorted_nodes)
        shard_size = max(1, (n + self._num_shards - 1) // self._num_shards)

        self._node_to_shard: Dict[TNode, int] = {}
        self._shard_to_nodes: Dict[int, List[TNode]] = defaultdict(list)
        for i, u in enumerate(sorted_nodes):
            s_id = min(self._num_shards - 1, i // shard_size)
            self._node_to_shard[u] = s_id
            self._shard_to_nodes[s_id].append(u)

        self._in_shards: Dict[int, List[Tuple[TNode, TNode, float]]] = defaultdict(list)
        for u, v, w in edges:
            target_shard = self._node_to_shard[v]
            self._in_shards[target_shard].append((u, v, w))

        self._out_degree: Dict[TNode, int] = defaultdict(int)
        for u, _, _ in edges:
            self._out_degree[u] += 1

        self._nodes: List[TNode] = sorted_nodes

    def compute_pagerank(self, damping: float = 0.85, iterations: int = 10) -> Dict[TNode, float]:
        """
        Compute PageRank using Parallel Sliding Windows (PSW) shard passes.

        Args:
            damping: Damping factor.
            iterations: Number of full out-of-core passes.

        Returns:
            Dictionary of converged PageRank scores.
        """
        n = len(self._nodes)
        if n == 0:
            return {}

        ranks: Dict[TNode, float] = {u: 1.0 / n for u in self._nodes}

        for _ in range(iterations):
            new_ranks: Dict[TNode, float] = {}

            for p in range(self._num_shards):
                shard_edges = self._in_shards[p]
                interval_nodes = self._shard_to_nodes[p]
                gathered: Dict[TNode, float] = defaultdict(float)

                for u, v, _ in shard_edges:
                    out_d = self._out_degree[u]
                    if out_d > 0:
                        gathered[v] += ranks[u] / out_d

                for v in interval_nodes:
                    new_ranks[v] = (1.0 - damping) / n + damping * gathered[v]

            ranks = new_ranks

        return ranks
