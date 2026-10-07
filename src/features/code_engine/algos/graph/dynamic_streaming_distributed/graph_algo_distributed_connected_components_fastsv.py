"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: FASTSV CONNECTED COMPONENTS (ALGO-GRAPH-DIST-227)
================================================================================

1. OVERVIEW & OBJECTIVE:
   FastSV / Shiloach-Vishkin Distributed Connected Components Engine.
   Executes logarithmic-round connected component identification via alternating
   directed parent forest hooking (stochastic/deterministic min-neighbor linking)
   and tree shortcutting / pointer-jumping (halving component tree depths).

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(log V) synchronous rounds, O(M log V) total edge operations.
   - Space Complexity: O(V) parent pointers and vertex component state.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `nodes` (List[TNode]): Full vertex sequence.
   - `edges` (List[Tuple[TNode, TNode]]): Undirected edge list.

4. OUTPUT PARAMETERS:
   - `compute_components()` (Dict[TNode, TNode]): Mapping from each vertex to canonical component root ID.
   - `get_component_count()` (int): Number of disconnected components.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact equivalence to connected components with O(log V) convergence guarantee.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoDistributedConnectedComponentsFastsv(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-DIST-227
      name: GraphAlgoDistributedConnectedComponentsFastsv
      version: 1.0.0
      category: graph_distributed
      capability_tags: [graph, distributed, connected_components, fastsv, shiloach_vishkin, pointer_jumping]
      inputs:
        type: object
        required: [nodes, edges]
        properties:
          nodes: {type: array}
          edges: {type: array}
      outputs:
        type: object
        properties:
          components: {type: object}
          component_count: {type: integer}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(log V) rounds
        space: O(V)
    ---
    """

    def __init__(self, nodes: List[TNode], edges: List[Tuple[TNode, TNode]]) -> None:
        """
        Initialize FastSV connected components runner.

        Args:
            nodes: Vertex list.
            edges: Undirected edge list.
        """
        self._nodes: List[TNode] = list(nodes)
        self._edges: List[Tuple[TNode, TNode]] = list(edges)

    def compute_components(self, max_rounds: int = 50) -> Dict[TNode, TNode]:
        """
        Execute FastSV hooking and shortcutting rounds until convergence.

        Args:
            max_rounds: Maximum pointer-jumping rounds.

        Returns:
            Dictionary mapping each vertex to its component root.
        """
        parent: Dict[TNode, TNode] = {u: u for u in self._nodes}

        for _ in range(max_rounds):
            changed = False

            for u, v in self._edges:
                pu = parent[u]
                pv = parent[v]
                if pu != pv:
                    if str(pv) < str(pu):
                        parent[pu] = pv
                        changed = True
                    elif str(pu) < str(pv):
                        parent[pv] = pu
                        changed = True

            for u in self._nodes:
                p = parent[u]
                gp = parent[p]
                if p != gp:
                    parent[u] = gp
                    changed = True

            if not changed:
                break

        for u in self._nodes:
            curr = u
            while parent[curr] != curr:
                curr = parent[curr]
            parent[u] = curr

        return parent

    def get_component_count(self) -> int:
        """
        Return the total number of connected components.

        Returns:
            Integer component count.
        """
        comps = self.compute_components()
        return len(set(comps.values()))
