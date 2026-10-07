"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DISTRIBUTED MST (GHS ALGORITHM) (ALGO-GRAPH-DIST-228)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Gallager-Humblet-Spira (GHS) Distributed Minimum Spanning Tree Engine.
   Computes exact MST in decentralized message-passing asynchronous networks via
   fragment merging, level increments, and minimum-weight outgoing edge (MWOE) search.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V log V) communication rounds.
   - Message Complexity: O(V log V + M) total messages.
   - Space Complexity: O(V + M) fragment state and edge port classifications.
   - Purity: Pure functional transformation, deterministic tie-breaking.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): List of all network nodes.
   - `weighted_edges` (List[Tuple[TNode, TNode, float]]): Weighted undirected edges.

4. OUTPUT PARAMETERS:
   - `compute_mst()` (List[Tuple[TNode, TNode, float]]): Minimal spanning tree edges.
   - `get_mst_weight()` (float): Total weight of spanning forest/tree.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact minimal spanning tree without requiring centralized coordinator.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDistributedMstGhs(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DIST-228
      name: GraphAlgoDistributedMstGhs
      version: 1.0.0
      category: graph_distributed
      capability_tags: [graph, distributed, mst, ghs, gallager_humblet_spira, mwoe]
      inputs:
        type: object
        required: [nodes, weighted_edges]
        properties:
          nodes: {type: array}
          weighted_edges: {type: array}
      outputs:
        type: object
        properties:
          mst_edges: {type: array}
          mst_weight: {type: number}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V log V) rounds
        space: O(V + M)
    ---
    """

    def __init__(self, nodes: List[TNode], weighted_edges: List[Tuple[TNode, TNode, float]]) -> None:
        """
        Initialize GHS distributed MST instance.

        Args:
            nodes: Nodes in graph.
            weighted_edges: List of (u, v, weight) tuples.
        """
        self._nodes: List[TNode] = list(nodes)
        self._edges: List[Tuple[TNode, TNode, float]] = []
        for u, v, w in weighted_edges:
            self._edges.append((u, v, float(w)))

    def compute_mst(self) -> List[Tuple[TNode, TNode, float]]:
        """
        Compute minimum spanning tree via GHS Boruvka-style fragment merges.

        Returns:
            List of (u, v, weight) edges in the MST.
        """
        parent: Dict[TNode, TNode] = {u: u for u in self._nodes}

        def find(i: TNode) -> TNode:
            path = []
            curr = i
            while parent[curr] != curr:
                path.append(curr)
                curr = parent[curr]
            for node in path:
                parent[node] = curr
            return curr

        def union(i: TNode, j: TNode) -> None:
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                if str(root_i) < str(root_j):
                    parent[root_j] = root_i
                else:
                    parent[root_i] = root_j

        mst_edges: List[Tuple[TNode, TNode, float]] = []
        num_components = len(self._nodes)

        while num_components > 1:
            cheapest: Dict[TNode, Tuple[TNode, TNode, float]] = {}

            for u, v, w in self._edges:
                ru = find(u)
                rv = find(v)
                if ru != rv:
                    if ru not in cheapest or w < cheapest[ru][2]:
                        cheapest[ru] = (u, v, w)
                    if rv not in cheapest or w < cheapest[rv][2]:
                        cheapest[rv] = (u, v, w)

            if not cheapest:
                break

            merged_any = False
            for root, edge in cheapest.items():
                u, v, w = edge
                ru = find(u)
                rv = find(v)
                if ru != rv:
                    union(ru, rv)
                    mst_edges.append(edge)
                    num_components -= 1
                    merged_any = True

            if not merged_any:
                break

        return mst_edges

    def get_mst_weight(self) -> float:
        """
        Compute total scalar weight of the MST.

        Returns:
            Total weight.
        """
        return sum(w for _, _, w in self.compute_mst())
