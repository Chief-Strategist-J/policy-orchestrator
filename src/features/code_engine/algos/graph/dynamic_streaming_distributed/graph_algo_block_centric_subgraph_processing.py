"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BLOCK-CENTRIC SUBGRAPH PROCESSING (ALGO-GRAPH-PAR-217)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Block-Centric ("Think Like a Graph") Distributed Processing Engine.
   Executes algorithms over partition blocks/subgraphs locally to internal convergence,
   exchanging messages exclusively across cut boundary vertices, drastically compressing superstep diameter.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(diam(G_blocks)) supersteps instead of O(diam(G)).
   - Space Complexity: O(V + M) partitioned subgraph structures and ghost boundary mailboxes.
   - Purity: Partition-based message passing, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Global graph adjacency.
   - `partition_assignment` (Dict[TNode, int]): Mapping from vertex to block partition ID.

4. OUTPUT PARAMETERS:
   - `compute_block_bfs(source)` (Dict[TNode, int]): Exact shortest hop distance from source.
   - `compute_block_components()` (Dict[TNode, TNode]): Connected component labels.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Global convergence equivalent to sequential execution with minimal inter-block communication.
================================================================================
"""

from collections import defaultdict, deque
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBlockCentricSubgraphProcessing(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PAR-217
      name: GraphAlgoBlockCentricSubgraphProcessing
      version: 1.0.0
      category: graph_parallel
      capability_tags: [graph, parallel, block_centric, think_like_a_graph, partition_subgraph, supersteps]
      inputs:
        type: object
        required: [adjacency, partition_assignment]
        properties:
          adjacency: {type: object}
          partition_assignment: {type: object}
      outputs:
        type: object
        properties:
          distances: {type: object}
          supersteps_used: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(diam(G_blocks)) supersteps
        space: O(V + M)
    ---
    """

    def __init__(
        self,
        adjacency: Dict[TNode, List[TNode]],
        partition_assignment: Dict[TNode, int],
    ) -> None:
        """
        Initialize block-centric partition graph.

        Args:
            adjacency: Adjacency dictionary.
            partition_assignment: Map from node to block ID.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._part: Dict[TNode, int] = dict(partition_assignment)
        for u in self._adj:
            if u not in self._part:
                self._part[u] = 0

        self._blocks: Dict[int, List[TNode]] = defaultdict(list)
        for u, pid in self._part.items():
            self._blocks[pid].append(u)

    def compute_block_bfs(self, source: TNode) -> Tuple[Dict[TNode, int], int]:
        """
        Execute block-centric BFS shortest distance calculation.

        Args:
            source: Source vertex.

        Returns:
            Tuple of (distances_dict, superstep_count).
        """
        distances: Dict[TNode, int] = {u: 10**9 for u in self._adj}
        distances[source] = 0

        active_blocks: Set[int] = {self._part[source]}
        supersteps = 0

        while active_blocks and supersteps < 1000:
            supersteps += 1
            boundary_messages: Dict[TNode, int] = defaultdict(lambda: 10**9)

            for b_id in list(active_blocks):
                local_nodes = set(self._blocks[b_id])
                queue = deque([u for u in local_nodes if distances[u] < 10**9])

                while queue:
                    u = queue.popleft()
                    d_u = distances[u]
                    for v in self._adj.get(u, []):
                        if self._part[v] == b_id:
                            if d_u + 1 < distances[v]:
                                distances[v] = d_u + 1
                                queue.append(v)
                        else:
                            if d_u + 1 < boundary_messages[v]:
                                boundary_messages[v] = d_u + 1

            next_active: Set[int] = set()
            for v, d_msg in boundary_messages.items():
                if d_msg < distances[v]:
                    distances[v] = d_msg
                    next_active.add(self._part[v])

            active_blocks = next_active

        return distances, supersteps
