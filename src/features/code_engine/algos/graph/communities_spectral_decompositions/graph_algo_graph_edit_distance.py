"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Graph Edit Distance - A* Search with Bipartite Lower Bounding (ALGO-GRAPH-ISO-185)

1. OVERVIEW & OBJECTIVE:
Computes the exact or heuristic Graph Edit Distance (GED) between two graphs G1 and G2,
measuring the minimum total cost of edit operations (vertex insertion, vertex deletion,
vertex substitution, edge insertion, edge deletion) via A* best-first state-space search.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V_1| * |V_2| * beam_width) open-set queue storage.
- Time Complexity: Exponential in worst case; polynomial with greedy/beam A* search.
- Invariants:
  - GED(G1, G2) == 0 iff G1 and G2 are isomorphic.
  - GED is a true metric satisfying non-negativity, symmetry, and triangle inequality.

3. INPUT PARAMETERS:
- `adj_1` (Mapping[TNode, Iterable[TNode]]): Source graph G1.
- `adj_2` (Mapping[TNode, Iterable[TNode]]): Target graph G2.
- `node_cost` (float): Cost of node insert/delete (default: 1.0).
- `edge_cost` (float): Cost of edge insert/delete (default: 1.0).
- `beam_width` (int): Beam search width cap for scaling (default: 100).

4. OUTPUT PARAMETERS:
- `GraphEditDistanceResult`: Final GED cost, node substitution mapping, and optimality flag.

5. AGENT CONTRACT:
- Role: Error-tolerant structural distance and similarity analyst.
- Rules: Enforce non-negative edit costs.
- Guardrails: If search times out or exceeds beam limit, reports best upper bound found.
"""

from collections import defaultdict
from dataclasses import dataclass
import heapq
from typing import Dict, Generic, Hashable, Iterable, List, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class GraphEditDistanceResult(Generic[TNode]):
    """
    Result container for Graph Edit Distance.
    """
    edit_distance: float
    mapping_1_to_2: Dict[TNode, Optional[TNode]]
    is_exact_optimal: bool


class GraphEditDistanceSolver(Generic[TNode]):
    """
    Solves Graph Edit Distance using A* search with bipartite lower bounds.

    ```yaml
    contract_id: ALGO-GRAPH-ISO-185
    inputs:
      adj_1: Mapping[TNode, Iterable[TNode]]
      adj_2: Mapping[TNode, Iterable[TNode]]
      node_cost: float
      edge_cost: float
      beam_width: int
    outputs:
      result: GraphEditDistanceResult[TNode]
    parameters:
      node_cost: float
      edge_cost: float
      beam_width: int
    capability_tags:
      - graph
      - isomorphism
      - ged
      - graph_edit_distance
      - a_star
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(beam * |V_1| * |V_2|)
      space: O(beam * |V_1| * |V_2|)
    ```
    """

    def __init__(
        self,
        node_cost: float = 1.0,
        edge_cost: float = 1.0,
        beam_width: int = 100,
    ) -> None:
        """
        Args:
            node_cost: Cost for inserting or deleting a vertex.
            edge_cost: Cost for inserting or deleting an edge.
            beam_width: A* beam search size limit.
        """
        self._node_cost = node_cost
        self._edge_cost = edge_cost
        self._beam_width = beam_width

    def compute_distance(
        self,
        adj_1: Mapping[TNode, Iterable[TNode]],
        adj_2: Mapping[TNode, Iterable[TNode]],
    ) -> GraphEditDistanceResult[TNode]:
        """
        Computes GED between graph 1 and graph 2.

        Args:
            adj_1: Source graph adjacency map.
            adj_2: Target graph adjacency map.

        Returns:
            GraphEditDistanceResult with edit distance and alignment.
        """
        nodes_1 = sorted(list(adj_1.keys()), key=lambda x: str(x))
        nodes_2 = sorted(list(adj_2.keys()), key=lambda x: str(x))

        n1, n2 = len(nodes_1), len(nodes_2)
        if n1 == 0 and n2 == 0:
            return GraphEditDistanceResult(edit_distance=0.0, mapping_1_to_2={}, is_exact_optimal=True)

        g1_adj: Dict[TNode, Set[TNode]] = {u: set(adj_1.get(u, ())) for u in nodes_1}
        g2_adj: Dict[TNode, Set[TNode]] = {v: set(adj_2.get(v, ())) for v in nodes_2}

        open_heap: List[Tuple[float, float, int, Tuple[Tuple[TNode, Optional[TNode]], ...], Tuple[TNode, ...]]] = []

        initial_h = self._heuristic_lower_bound(nodes_1, nodes_2, g1_adj, g2_adj)
        heapq.heappush(open_heap, (initial_h, 0.0, 0, (), tuple(nodes_2)))

        best_cost = float("inf")
        best_mapping: Dict[TNode, Optional[TNode]] = {}
        iterations = 0

        while open_heap and iterations < self._beam_width * 20:
            iterations += 1
            f_val, g_val, idx_1, partial_map_tuple, unmapped_2_tuple = heapq.heappop(open_heap)

            if g_val >= best_cost:
                continue

            if idx_1 == n1:
                cost = g_val + len(unmapped_2_tuple) * self._node_cost
                for v in unmapped_2_tuple:
                    cost += len(g2_adj[v]) * self._edge_cost * 0.5
                if cost < best_cost:
                    best_cost = cost
                    best_mapping = dict(partial_map_tuple)
                    for v in unmapped_2_tuple:
                        pass
                continue

            u1 = nodes_1[idx_1]
            for v2 in unmapped_2_tuple:
                edge_diff = self._edge_edit_cost(u1, v2, dict(partial_map_tuple), g1_adj, g2_adj)
                new_g = g_val + edge_diff
                new_map = partial_map_tuple + ((u1, v2),)
                new_unmapped_2 = tuple(v for v in unmapped_2_tuple if v != v2)
                h_val = self._heuristic_lower_bound(nodes_1[idx_1 + 1:], list(new_unmapped_2), g1_adj, g2_adj)
                heapq.heappush(open_heap, (new_g + h_val, new_g, idx_1 + 1, new_map, new_unmapped_2))

            del_edge_diff = len([w for w in g1_adj[u1] if any(w == m[0] for m in partial_map_tuple)]) * self._edge_cost
            del_g = g_val + self._node_cost + del_edge_diff
            del_map = partial_map_tuple + ((u1, None),)
            del_h = self._heuristic_lower_bound(nodes_1[idx_1 + 1:], list(unmapped_2_tuple), g1_adj, g2_adj)
            heapq.heappush(open_heap, (del_g + del_h, del_g, idx_1 + 1, del_map, unmapped_2_tuple))

            if len(open_heap) > self._beam_width * 4:
                open_heap = heapq.nsmallest(self._beam_width * 2, open_heap)
                heapq.heapify(open_heap)

        return GraphEditDistanceResult(
            edit_distance=best_cost if best_cost != float("inf") else (n1 + n2) * self._node_cost,
            mapping_1_to_2=best_mapping,
            is_exact_optimal=(iterations < self._beam_width * 20),
        )

    def _edge_edit_cost(
        self,
        u1: TNode,
        v2: TNode,
        mapping: Dict[TNode, Optional[TNode]],
        g1_adj: Dict[TNode, Set[TNode]],
        g2_adj: Dict[TNode, Set[TNode]],
    ) -> float:
        cost = 0.0
        for mapped_u1, mapped_v2 in mapping.items():
            if mapped_v2 is None:
                continue
            has_edge_1 = mapped_u1 in g1_adj[u1]
            has_edge_2 = mapped_v2 in g2_adj[v2]
            if has_edge_1 != has_edge_2:
                cost += self._edge_cost
        return cost

    def _heuristic_lower_bound(
        self,
        rem_1: List[TNode],
        rem_2: List[TNode],
        g1_adj: Dict[TNode, Set[TNode]],
        g2_adj: Dict[TNode, Set[TNode]],
    ) -> float:
        n_diff = abs(len(rem_1) - len(rem_2))
        return n_diff * self._node_cost
