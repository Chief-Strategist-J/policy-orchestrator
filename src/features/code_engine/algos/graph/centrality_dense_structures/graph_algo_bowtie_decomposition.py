"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: BOW-TIE DECOMPOSITION (ALGO-GRAPH-NET-140)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Directed Bow-Tie topological structure decomposition algorithm (Broder et al.).
   Partitions the vertices of a directed graph into 6 canonical macroscopic flow regions:
   - CORE: Giant Strongly Connected Component (SCC).
   - IN: Vertices capable of reaching CORE (upstream feeders).
   - OUT: Vertices reachable from CORE (downstream consumers).
   - TUBES: Direct paths connecting IN to OUT bypassing CORE.
   - TENDRILS: Vertices reachable from IN or reaching OUT without intersecting CORE.
   - DISCONNECTED: Isolated components completely detached from the giant structure.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V + E) Tarjan SCC plus multi-source forward/backward BFS.
   - Space Complexity: O(V) disjoint component sets.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - adjacency: Dict[TNode, List[TNode]] - Directed graph adjacency list.

4. OUTPUT PARAMETERS:
   - core_nodes: List[TNode] - Vertices in the giant strongly connected core.
   - in_nodes: List[TNode] - Upstream source vertices reaching the core.
   - out_nodes: List[TNode] - Downstream sink vertices reachable from the core.
   - tubes_nodes: List[TNode] - Conduit vertices passing from IN to OUT bypassing CORE.
   - tendrils_nodes: List[TNode] - Hanging branch vertices off IN or OUT.
   - disconnected_nodes: List[TNode] - Unconnected peripheral components.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Directed network.
   - Guardrails: The 6 partitions are strictly pairwise disjoint and sum to all V.
================================================================================
"""

from collections import deque
from typing import Deque, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoBowtieDecomposition(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-NET-140
      name: GraphAlgoBowtieDecomposition
      version: 1.0.0
      category: graph_centrality_dense
      capability_tags: [graph, network_measures, bowtie_decomposition, macro_structure, core_in_out, flow_analysis]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency: {type: object}
      outputs:
        type: object
        required: [core_nodes, in_nodes, out_nodes, tubes_nodes, tendrils_nodes, disconnected_nodes]
        properties:
          core_nodes: {type: array, items: {type: string}}
          in_nodes: {type: array, items: {type: string}}
          out_nodes: {type: array, items: {type: string}}
          tubes_nodes: {type: array, items: {type: string}}
          tendrils_nodes: {type: array, items: {type: string}}
          disconnected_nodes: {type: array, items: {type: string}}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V + E)
        space: O(V)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[TNode]]) -> None:
        """
        Initialize the Bow-Tie Decomposition engine.

        Args:
            adjacency: Directed graph adjacency dictionary.
        """
        self._adj: Dict[TNode, List[TNode]] = adjacency
        self._nodes: List[TNode] = sorted(list(self._collect_all_nodes()), key=lambda x: str(x))

        self._rev_adj: Dict[TNode, List[TNode]] = {u: [] for u in self._nodes}
        for u, neighbors in self._adj.items():
            for v in neighbors:
                if v in self._rev_adj:
                    self._rev_adj[v].append(u)

    def _collect_all_nodes(self) -> Set[TNode]:
        nodes: Set[TNode] = set(self._adj.keys())
        for u in self._adj:
            for v in self._adj[u]:
                nodes.add(v)
        return nodes

    def _find_sccs(self) -> List[Set[TNode]]:
        index = 0
        indices: Dict[TNode, int] = {}
        lowlinks: Dict[TNode, int] = {}
        stack: List[TNode] = []
        on_stack: Set[TNode] = set()
        sccs: List[Set[TNode]] = []

        def _strongconnect(u: TNode) -> None:
            nonlocal index
            indices[u] = index
            lowlinks[u] = index
            index += 1
            stack.append(u)
            on_stack.add(u)

            for v in self._adj.get(u, []):
                if v not in indices:
                    _strongconnect(v)
                    lowlinks[u] = min(lowlinks[u], lowlinks[v])
                elif v in on_stack:
                    lowlinks[u] = min(lowlinks[u], indices[v])

            if lowlinks[u] == indices[u]:
                scc = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.add(w)
                    if w == u:
                        break
                sccs.append(scc)

        for node in self._nodes:
            if node not in indices:
                _strongconnect(node)

        return sccs

    def _reach(self, sources: Set[TNode], adj: Dict[TNode, List[TNode]]) -> Set[TNode]:
        visited: Set[TNode] = set(sources)
        q: Deque[TNode] = deque(list(sources))
        while q:
            u = q.popleft()
            for v in adj.get(u, []):
                if v not in visited:
                    visited.add(v)
                    q.append(v)
        return visited

    def compute_decomposition(self) -> Tuple[
        List[TNode], List[TNode], List[TNode], List[TNode], List[TNode], List[TNode]
    ]:
        """
        Partition directed graph into CORE, IN, OUT, TUBES, TENDRILS, and DISCONNECTED.

        Returns:
            Tuple of (core_nodes, in_nodes, out_nodes, tubes_nodes, tendrils_nodes, disconnected_nodes).
        """
        if not self._nodes:
            return [], [], [], [], [], []

        sccs = self._find_sccs()
        giant_scc = max(sccs, key=lambda s: len(s)) if sccs else set()

        reach_forward = self._reach(giant_scc, self._adj)
        reach_backward = self._reach(giant_scc, self._rev_adj)

        core = giant_scc
        in_part = reach_backward - core
        out_part = reach_forward - core

        reach_from_in = self._reach(in_part, self._adj)
        reach_to_out = self._reach(out_part, self._rev_adj)

        tubes = (reach_from_in & reach_to_out) - core - in_part - out_part
        tendrils = ((reach_from_in | reach_to_out) - core - in_part - out_part) - tubes

        assigned = core | in_part | out_part | tubes | tendrils
        disconnected = set(self._nodes) - assigned

        def _sort(s: Set[TNode]) -> List[TNode]:
            return sorted(list(s), key=lambda x: str(x))

        return _sort(core), _sort(in_part), _sort(out_part), _sort(tubes), _sort(tendrils), _sort(disconnected)
