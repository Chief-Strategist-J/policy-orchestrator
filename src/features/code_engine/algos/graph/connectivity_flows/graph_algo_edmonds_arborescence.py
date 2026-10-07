"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: EDMONDS DIRECTED ARBORESCENCE (ALGO-GRAPH-TREE-64)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Chu-Liu/Edmonds directed minimum spanning arborescence algorithm.
   Computes the minimum-weight directed spanning tree rooted at a designated root vertex
   using recursive cycle contraction, weight re-normalization, and cycle expansion.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * E) recursive contraction.
   - Space Complexity: O(V + E) auxiliary memory.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. INPUT PARAMETERS:
   - edges: List[Tuple[TNode, TNode, float]] - Directed weighted edge triplets (source, target, weight).
   - nodes: Optional[List[TNode]] - Explicit list of vertices (inferred from edges if omitted).
   - root: TNode - Designated root vertex for the directed spanning tree.

4. OUTPUT PARAMETERS:
   - total_weight: float - Total sum of weights of selected arborescence edges (inf if unreachable).
   - arborescence_edges: List[Tuple[TNode, TNode, float]] - List of directed edges forming the minimum arborescence.

5. AGENT CONTRACT:
   - Role: Optimizer.
   - Preconditions: All nodes must be reachable from root node.
   - Guardrails: Cycle tracking ensures finite recursive descent.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoEdmondsArborescence(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-64
      name: GraphAlgoEdmondsArborescence
      version: 1.0.0
      category: graph_connectivity_trees
      capability_tags: [graph, directed_spanning_tree, arborescence, chu_liu_edmonds, cycle_contraction]
      inputs:
        type: object
        required: [edges, root]
        properties:
          edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}]
          nodes:
            type: array
            items: {type: string}
          root: {type: string}
      outputs:
        type: object
        required: [total_weight, arborescence_edges]
        properties:
          total_weight: {type: number}
          arborescence_edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}]
      parameters:
        root: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * E)
        space: O(V + E)
    ---
    """

    def __init__(self, edges: List[Tuple[TNode, TNode, float]], nodes: Optional[List[TNode]] = None) -> None:
        """
        Initialize the Edmonds directed arborescence solver.

        Args:
            edges: Directed weighted edges as (source, target, weight) triplets.
            nodes: Optional explicit list of vertices.
        """
        self._edges: List[Tuple[TNode, TNode, float]] = edges
        node_set: Set[TNode] = set(nodes) if nodes is not None else set()
        for u, v, _ in edges:
            node_set.add(u)
            node_set.add(v)
        self._nodes: List[TNode] = sorted(list(node_set), key=lambda x: str(x))

    def compute_arborescence(self, root: TNode) -> Tuple[float, List[Tuple[TNode, TNode, float]]]:
        """
        Compute the minimum directed spanning arborescence rooted at the given node.

        Args:
            root: Root vertex from which all other vertices must be reachable.

        Returns:
            A tuple of (total_weight, arborescence_edges).
        """
        return self._edmonds(self._nodes, self._edges, root)

    def _edmonds(
        self,
        nodes: List[TNode],
        edges: List[Tuple[TNode, TNode, float]],
        root: TNode,
    ) -> Tuple[float, List[Tuple[TNode, TNode, float]]]:
        min_in: Dict[TNode, Tuple[TNode, float]] = {}
        for u, v, w in edges:
            if v == root:
                continue
            if v not in min_in or w < min_in[v][1]:
                min_in[v] = (u, w)

        if len(min_in) < len(nodes) - 1:
            return float("inf"), []

        cycle_nodes: Optional[List[TNode]] = None
        visited: Dict[TNode, int] = {u: 0 for u in nodes}
        cycle_detector_parent: Dict[TNode, TNode] = {v: u for v, (u, _) in min_in.items()}

        for n in nodes:
            if n == root or visited[n] != 0:
                continue
            curr: Optional[TNode] = n
            path: List[TNode] = []
            while curr is not None and curr != root and visited.get(curr, 0) == 0:
                visited[curr] = 1
                path.append(curr)
                curr = cycle_detector_parent.get(curr)

            if curr is not None and curr in path:
                idx = path.index(curr)
                cycle_nodes = path[idx:]
                break

            for p in path:
                visited[p] = 2

        if cycle_nodes is None:
            total = sum(w for _, w in min_in.values())
            res_edges = [(u, v, w) for v, (u, w) in min_in.items()]
            return total, res_edges

        cycle_set = set(cycle_nodes)
        super_node = cycle_nodes[0]
        new_nodes = [u for u in nodes if u not in cycle_set] + [super_node]

        cycle_edge_weights: Dict[TNode, float] = {v: min_in[v][1] for v in cycle_nodes}

        new_edges: List[Tuple[TNode, TNode, float]] = []
        edge_orig_map: Dict[Tuple[TNode, TNode, float], Tuple[TNode, TNode, float]] = {}

        for u, v, w in edges:
            if u in cycle_set and v in cycle_set:
                continue
            src = super_node if u in cycle_set else u
            tgt = super_node if v in cycle_set else v
            if src == tgt:
                continue
            new_w = w
            if v in cycle_set:
                new_w = w - cycle_edge_weights[v]
            trans_edge = (src, tgt, new_w)
            new_edges.append(trans_edge)
            edge_orig_map[trans_edge] = (u, v, w)

        cost_prime, arb_prime = self._edmonds(new_nodes, new_edges, root)
        if cost_prime == float("inf"):
            return float("inf"), []

        entering_cycle_target: Optional[TNode] = None
        final_edges: List[Tuple[TNode, TNode, float]] = []

        for e_prime in arb_prime:
            orig_u, orig_v, orig_w = edge_orig_map[e_prime]
            final_edges.append((orig_u, orig_v, orig_w))
            if orig_v in cycle_set:
                entering_cycle_target = orig_v

        for v in cycle_nodes:
            if v != entering_cycle_target:
                u, w = min_in[v]
                final_edges.append((u, v, w))

        total_weight = sum(w for _, _, w in final_edges)
        return total_weight, final_edges
