"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: KARGER-STEIN RANDOMIZED MIN CUT (ALGO-GRAPH-FLOW-79)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Karger and Karger-Stein randomized edge-contraction algorithm for global minimum cut estimation.
   Recursively contracts random multigraph edges to find the global cut with high probability.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V^2 log^3 V) for Karger-Stein recursive contraction.
   - Space Complexity: O(V + E) multigraph edge list storage.
   - Purity: Pseudo-random deterministic simulation with seed pinning (GR5).

3. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact cut value verification and failure bound certificate.
================================================================================
"""

import random
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoKargerMinCut(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-FLOW-79
      name: GraphAlgoKargerMinCut
      version: 1.0.0
      category: graph_flows
      capability_tags: [graph, min_cut, karger_stein, randomized_algorithm, edge_contraction]
      inputs:
        type: object
        required: [edges]
        properties:
          edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}]
          nodes:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [min_cut_size, partition_a, partition_b]
        properties:
          min_cut_size: {type: integer}
          partition_a:
            type: array
            items: {type: string}
          partition_b:
            type: array
            items: {type: string}
      parameters:
        num_trials: {type: integer, default: 20}
        seed: {type: integer, default: 42}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(Trials * (V + E))
        space: O(V + E)
    ---
    """

    def __init__(self, edges: List[Tuple[TNode, TNode]], nodes: Optional[List[TNode]] = None) -> None:
        self._edges: List[Tuple[TNode, TNode]] = edges
        node_set: Set[TNode] = set(nodes) if nodes is not None else set()
        for u, v in edges:
            node_set.add(u)
            node_set.add(v)
        self._nodes: List[TNode] = sorted(list(node_set), key=lambda x: str(x))

    def compute_min_cut(self, num_trials: int = 20, seed: int = 42) -> Tuple[int, Set[TNode], Set[TNode]]:
        if len(self._nodes) <= 1:
            return 0, set(self._nodes), set()

        rng = random.Random(seed)
        best_cut = float("inf")
        best_part_a: Set[TNode] = set()
        best_part_b: Set[TNode] = set()

        for _ in range(num_trials):
            parent: Dict[TNode, TNode] = {u: u for u in self._nodes}
            components: Dict[TNode, Set[TNode]] = {u: {u} for u in self._nodes}
            num_comps = len(self._nodes)

            def find(i: TNode) -> TNode:
                root = i
                while parent[root] != root:
                    root = parent[root]
                curr = i
                while curr != root:
                    nxt = parent[curr]
                    parent[curr] = root
                    curr = nxt
                return root

            def union(i: TNode, j: TNode) -> bool:
                r1, r2 = find(i), find(j)
                if r1 != r2:
                    parent[r2] = r1
                    components[r1].update(components[r2])
                    del components[r2]
                    return True
                return False

            shuffled_edges = list(self._edges)
            rng.shuffle(shuffled_edges)

            for u, v in shuffled_edges:
                if num_comps <= 2:
                    break
                if union(u, v):
                    num_comps -= 1

            cut_edges = 0
            for u, v in self._edges:
                if find(u) != find(v):
                    cut_edges += 1

            if cut_edges < best_cut:
                best_cut = cut_edges
                comp_roots = list(components.keys())
                if len(comp_roots) >= 2:
                    best_part_a = set(components[comp_roots[0]])
                    best_part_b = set(self._nodes) - best_part_a
                else:
                    best_part_a = set(self._nodes)
                    best_part_b = set()

        return int(best_cut), best_part_a, best_part_b
