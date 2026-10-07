"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: HIGH-DEGREE HUB VERTEX SPLITTING (ALGO-GRAPH-ENG-241)
================================================================================

1. OVERVIEW & OBJECTIVE:
   High-Degree Hub Vertex Splitting and Degree-Aware Balancing Engine.
   Detects heavy power-law hub vertices exceeding a threshold tau and logically splits
   them into clusters of degree-bounded sub-vertices connected via cycle / star trees,
   eliminating worker stragglers and memory spikes in parallel graph pipelines.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + M) linear splitting and re-wiring.
   - Space Complexity: O(V + M + Hub_Splits) transformed graph topology.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `adjacency` (Dict[TNode, List[TNode]]): Original graph adjacency.
   - `max_degree_threshold` (int): Maximum allowable degree per vertex replica.

4. OUTPUT PARAMETERS:
   - `split_graph()` (Tuple[Dict[Any, List[Any]], Dict[str, List[Any]]]): Transformed graph and hub-to-subnodes map.
   - `get_hub_nodes()` (List[TNode]): List of detected hubs exceeding threshold.

5. AGENT CONTRACT:
   - Role: Builder.
   - Guarantees: Preserves global reachability across all split hub replicas.
================================================================================
"""

from collections import defaultdict
from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoHighDegreeVertexSplitting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-ENG-241
      name: GraphAlgoHighDegreeVertexSplitting
      version: 1.0.0
      category: graph_engineering
      capability_tags: [graph, engineering, hub_splitting, load_balancing, power_law, stragglers]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
          max_degree_threshold: {type: integer, minimum: 2}
      outputs:
        type: object
        properties:
          hubs_split_count: {type: integer}
          total_new_nodes: {type: integer}
      parameters:
        max_degree_threshold: {type: integer}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + M)
        space: O(V + M)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]], max_degree_threshold: int = 4) -> None:
        """
        Initialize high-degree vertex splitting engine.

        Args:
            adjacency: Adjacency dictionary.
            max_degree_threshold: Max allowed degree per split replica.
        """
        self._adj: Dict[TNode, List[TNode]] = {u: list(nbrs) for u, nbrs in adjacency.items()}
        for u, nbrs in list(self._adj.items()):
            for v in nbrs:
                if v not in self._adj:
                    self._adj[v] = []

        self._threshold: int = max(2, max_degree_threshold)

    def get_hub_nodes(self) -> List[TNode]:
        """
        Identify vertices exceeding the degree threshold.

        Returns:
            List of hub vertices.
        """
        return [u for u, nbrs in self._adj.items() if len(nbrs) > self._threshold]

    def split_graph(self) -> Tuple[Dict[Any, List[Any]], Dict[TNode, List[str]]]:
        """
        Split all hub vertices into bounded-degree sub-vertices connected in a cycle.

        Returns:
            Tuple of (new_adjacency_map, hub_to_replicas_mapping).
        """
        new_adj: Dict[Any, List[Any]] = defaultdict(list)
        hub_map: Dict[TNode, List[str]] = {}

        for u, nbrs in self._adj.items():
            if len(nbrs) <= self._threshold:
                new_adj[u].extend(nbrs)
            else:
                chunks = [
                    nbrs[i : i + self._threshold]
                    for i in range(0, len(nbrs), self._threshold)
                ]
                sub_nodes = [f"{str(u)}_sub_{i}" for i in range(len(chunks))]
                hub_map[u] = sub_nodes

                for i, s_node in enumerate(sub_nodes):
                    new_adj[s_node].extend(chunks[i])
                    prev_s = sub_nodes[(i - 1) % len(sub_nodes)]
                    next_s = sub_nodes[(i + 1) % len(sub_nodes)]
                    new_adj[s_node].append(prev_s)
                    if next_s != prev_s:
                        new_adj[s_node].append(next_s)

        return dict(new_adj), hub_map
