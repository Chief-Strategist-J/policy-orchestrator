"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: STEINER TREE 2-APPROXIMATION (ALGO-GRAPH-TREE-65)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Steiner Tree 2-Approximation using Kou-Markowsky-Berman (KMB) metric closure.
   Connects a designated subset of terminal vertices at near-minimal edge cost (<= 2 * OPT)
   using all-pairs terminal shortest paths, metric MST, and leaf-pruning reduction.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(|Terminals| * (E + V log V)) metric Dijkstra passes.
   - Space Complexity: O(V + E) subgraph and MST storage.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Optimizer & Analyst.
   - Guarantees: Solution weight is certified <= 2 * OPT_STEINER.
================================================================================
"""

import heapq
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from src.features.code_engine.algos.graph.connectivity_flows.graph_algo_kruskal_mst import GraphAlgoKruskalMst

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSteinerTreeApprox(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TREE-65
      name: GraphAlgoSteinerTreeApprox
      version: 1.0.0
      category: graph_trees
      capability_tags: [graph, steiner_tree, approximation_algorithm, metric_closure, kmb]
      inputs:
        type: object
        required: [adjacency, terminals]
        properties:
          adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: array
                items: [{type: string}, {type: number}]
          terminals:
            type: array
            items: {type: string}
      outputs:
        type: object
        required: [total_weight, steiner_edges]
        properties:
          total_weight: {type: number}
          steiner_edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}]
      parameters:
        terminals:
          type: array
          items: {type: string}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(|Terminals| * (E + V log V))
        space: O(V + E)
    ---
    """

    def __init__(self, adjacency: Dict[TNode, List[Tuple[TNode, float]]]) -> None:
        self._adj: Dict[TNode, List[Tuple[TNode, float]]] = {
            u: list(edges) for u, edges in adjacency.items()
        }
        for u in list(self._adj.keys()):
            for v, _ in self._adj[u]:
                if v not in self._adj:
                    self._adj[v] = []

    def _dijkstra(self, src: TNode) -> Tuple[Dict[TNode, float], Dict[TNode, Optional[TNode]]]:
        dist: Dict[TNode, float] = {u: float("inf") for u in self._adj}
        prev: Dict[TNode, Optional[TNode]] = {u: None for u in self._adj}
        dist[src] = 0.0
        pq: List[Tuple[float, str, TNode]] = [(0.0, str(src), src)]

        while pq:
            d, _, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, w in self._adj.get(u, []):
                if dist[u] + w < dist.get(v, float("inf")):
                    dist[v] = dist[u] + w
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], str(v), v))

        return dist, prev

    def _get_path(self, target: TNode, prev: Dict[TNode, Optional[TNode]]) -> List[TNode]:
        path: List[TNode] = []
        curr: Optional[TNode] = target
        while curr is not None:
            path.append(curr)
            curr = prev.get(curr)
        path.reverse()
        return path

    def compute_steiner_tree(
        self, terminals: List[TNode]
    ) -> Tuple[float, List[Tuple[TNode, TNode, float]]]:
        term_list = sorted(list(set(terminals)), key=lambda x: str(x))
        if len(term_list) <= 1:
            return 0.0, []

        shortest_paths: Dict[Tuple[TNode, TNode], List[TNode]] = {}
        closure_edges: List[Tuple[TNode, TNode, float]] = []

        for i in range(len(term_list)):
            t1 = term_list[i]
            dist, prev = self._dijkstra(t1)
            for j in range(i + 1, len(term_list)):
                t2 = term_list[j]
                d = dist.get(t2, float("inf"))
                if d < float("inf"):
                    closure_edges.append((t1, t2, d))
                    shortest_paths[(t1, t2)] = self._get_path(t2, prev)

        kruskal = GraphAlgoKruskalMst[TNode](closure_edges, term_list)
        _, mst_closure_edges = kruskal.compute_mst()

        subgraph_edges: Set[Tuple[TNode, TNode]] = set()
        edge_weight_map: Dict[Tuple[TNode, TNode], float] = {}
        for u in self._adj:
            for v, w in self._adj[u]:
                edge_weight_map[(u, v)] = w
                edge_weight_map[(v, u)] = w

        for u, v, _ in mst_closure_edges:
            pair = (u, v) if (u, v) in shortest_paths else (v, u)
            path = shortest_paths.get(pair, [])
            for k in range(len(path) - 1):
                p_u, p_v = path[k], path[k + 1]
                if str(p_u) < str(p_v):
                    subgraph_edges.add((p_u, p_v))
                else:
                    subgraph_edges.add((p_v, p_u))

        sub_edge_list: List[Tuple[TNode, TNode, float]] = [
            (u, v, edge_weight_map.get((u, v), 1.0)) for u, v in subgraph_edges
        ]

        sub_nodes: Set[TNode] = set()
        for u, v, _ in sub_edge_list:
            sub_nodes.add(u)
            sub_nodes.add(v)

        sub_kruskal = GraphAlgoKruskalMst[TNode](sub_edge_list, list(sub_nodes))
        _, final_mst = sub_kruskal.compute_mst()

        adj_tree: Dict[TNode, Dict[TNode, float]] = {u: {} for u in sub_nodes}
        for u, v, w in final_mst:
            adj_tree[u][v] = w
            adj_tree[v][u] = w

        term_set = set(term_list)
        pruned = True
        while pruned:
            pruned = False
            leaves = [u for u in list(adj_tree.keys()) if len(adj_tree[u]) == 1 and u not in term_set]
            for leaf in leaves:
                parent = next(iter(adj_tree[leaf].keys()))
                del adj_tree[parent][leaf]
                del adj_tree[leaf]
                pruned = True

        result_edges: List[Tuple[TNode, TNode, float]] = []
        total_weight = 0.0
        seen_edges: Set[Tuple[TNode, TNode]] = set()

        for u in adj_tree:
            for v, w in adj_tree[u].items():
                edge_key = (u, v) if str(u) < str(v) else (v, u)
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    result_edges.append((edge_key[0], edge_key[1], w))
                    total_weight += w

        return total_weight, result_edges
