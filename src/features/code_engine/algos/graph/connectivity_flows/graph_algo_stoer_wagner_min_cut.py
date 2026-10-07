"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STOER-WAGNER GLOBAL MIN CUT (ALGO-GRAPH-FLOW-78)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Stoer-Wagner algorithm for finding the global minimum cut in an undirected weighted graph
   without pre-specifying source and sink vertices, using maximum adjacency search phases.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(V * E + V^2 log V) across V-1 minimum cut phases.
   - Space Complexity: O(V^2) adjacency matrix and contracted node tracking.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst.
   - Preconditions: Undirected graph with non-negative edge weights.
================================================================================
"""

from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoStoerWagnerMinCut(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-FLOW-78
      name: GraphAlgoStoerWagnerMinCut
      version: 1.0.0
      category: graph_flows
      capability_tags: [graph, min_cut, stoer_wagner, global_min_cut, maximum_adjacency_search]
      inputs:
        type: object
        required: [adjacency]
        properties:
          adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: array
                items: [{type: string}, {type: number}]
      outputs:
        type: object
        required: [min_cut_weight, partition_a, partition_b]
        properties:
          min_cut_weight: {type: number}
          partition_a:
            type: array
            items: {type: string}
          partition_b:
            type: array
            items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(V * E + V^2 log V)
        space: O(V^2)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._nodes: List[TNode] = sorted(list(adjacency.keys()), key=lambda x: str(x))
        self._adj: Dict[Tuple[TNode, TNode], float] = {}

        for u in self._nodes:
            for v, w in adjacency[u]:
                if v not in self._nodes:
                    self._nodes.append(v)
                self._adj[(u, v)] = self._adj.get((u, v), 0.0) + w
                self._adj[(v, u)] = self._adj.get((v, u), 0.0) + w

        self._nodes.sort(key=lambda x: str(x))

    def compute_min_cut(self) -> Tuple[float, Set[TNode], Set[TNode]]:
        if len(self._nodes) < 2:
            return 0.0, set(self._nodes), set()

        nodes = list(self._nodes)
        groups: Dict[TNode, Set[TNode]] = {u: {u} for u in nodes}
        matrix: Dict[Tuple[TNode, TNode], float] = dict(self._adj)

        min_cut = float("inf")
        best_partition: Set[TNode] = set()
        all_nodes_set = set(self._nodes)

        while len(nodes) > 1:
            added: List[TNode] = []
            weights: Dict[TNode, float] = {u: 0.0 for u in nodes}

            for _ in range(len(nodes)):
                best_u = max(
                    [u for u in nodes if u not in added],
                    key=lambda x: (weights[x], str(x)),
                )
                added.append(best_u)
                for v in nodes:
                    if v not in added:
                        weights[v] += matrix.get((best_u, v), 0.0)

            s, t = added[-2], added[-1]
            cut_val = weights[t]

            if cut_val < min_cut:
                min_cut = cut_val
                best_partition = set(groups[t])

            groups[s].update(groups[t])
            for v in nodes:
                if v != s and v != t:
                    w_sv = matrix.get((s, v), 0.0) + matrix.get((t, v), 0.0)
                    matrix[(s, v)] = w_sv
                    matrix[(v, s)] = w_sv
                    if (t, v) in matrix:
                        del matrix[(t, v)]
                    if (v, t) in matrix:
                        del matrix[(v, t)]

            nodes.remove(t)

        return min_cut, best_partition, all_nodes_set - best_partition
