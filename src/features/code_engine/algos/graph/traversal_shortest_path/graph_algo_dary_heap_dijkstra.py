"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: D-ARY HEAP DIJKSTRA (ALGO-GRAPH-PATH-25)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Dijkstra's shortest path algorithm parameterized by a d-ary min-heap priority
   queue. By tuning heap branching factor d (e.g. d=4), reduces heap height to
   log_d(V), speeding up decrease-key operations and CPU cache locality on dense
   and high-degree weighted network topologies.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(d * V * log_d(V) + E * log_d(V)).
   - Space Complexity: O(V) for heap and distance arrays.
   - Purity: Pure functional transformation, deterministic, zero side-effects.

3. AGENT CONTRACT:
   - Role: Analyst & Optimizer.
   - Preconditions: Edge weights must be strictly non-negative.
================================================================================
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple, Generic, TypeVar

NodeId = TypeVar("NodeId")


class DaryMinHeap:
    def __init__(self, d: int = 4):
        self.d = max(2, d)
        self.heap: List[Tuple[float, str]] = []
        self.pos_map: Dict[str, int] = {}

    def push_or_decrease(self, node: str, dist: float) -> None:
        if node in self.pos_map:
            idx = self.pos_map[node]
            if dist < self.heap[idx][0]:
                self.heap[idx] = (dist, node)
                self._sift_up(idx)
        else:
            idx = len(self.heap)
            self.heap.append((dist, node))
            self.pos_map[node] = idx
            self._sift_up(idx)

    def pop_min(self) -> Optional[Tuple[float, str]]:
        if not self.heap:
            return None
        min_item = self.heap[0]
        last_item = self.heap.pop()
        del self.pos_map[min_item[1]]

        if self.heap:
            self.heap[0] = last_item
            self.pos_map[last_item[1]] = 0
            self._sift_down(0)

        return min_item

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def _sift_up(self, idx: int) -> None:
        while idx > 0:
            parent_idx = (idx - 1) // self.d
            if self.heap[idx][0] < self.heap[parent_idx][0]:
                self._swap(idx, parent_idx)
                idx = parent_idx
            else:
                break

    def _sift_down(self, idx: int) -> None:
        n = len(self.heap)
        while True:
            min_child_idx = idx
            first_child = self.d * idx + 1
            if first_child >= n:
                break

            for c in range(first_child, min(first_child + self.d, n)):
                if self.heap[c][0] < self.heap[min_child_idx][0]:
                    min_child_idx = c

            if min_child_idx != idx:
                self._swap(idx, min_child_idx)
                idx = min_child_idx
            else:
                break

    def _swap(self, i: int, j: int) -> None:
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
        self.pos_map[self.heap[i][1]] = i
        self.pos_map[self.heap[j][1]] = j


class GraphAlgoDaryHeapDijkstra(Generic[NodeId]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-PATH-25
      name: GraphAlgoDaryHeapDijkstra
      version: 1.0.0
      category: graph_shortest_path
      capability_tags: [graph, shortest_path, dijkstra, d_ary_heap, cache_optimized]
      inputs:
        type: object
        required: [weighted_adjacency, start_node]
        properties:
          weighted_adjacency:
            type: object
            additionalProperties:
              type: array
              items:
                type: object
                required: [target, weight]
                properties:
                  target: {type: string}
                  weight: {type: number}
          start_node: {type: string}
          target_node: {type: string}
      outputs:
        type: object
        required: [distances, parents, shortest_path_to_target]
      parameters:
        d: {type: integer, default: 4}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O((E + d*V) * log_d V)
        space: O(V)
    ---
    """

    @staticmethod
    def compute(
        weighted_adjacency: Dict[str, List[Dict[str, Any]]],
        start_node: str,
        target_node: Optional[str] = None,
        d: int = 4,
    ) -> Dict[str, Any]:
        all_nodes = sorted(list(weighted_adjacency.keys()))
        distances: Dict[str, float] = {n: float("inf") for n in all_nodes}
        parents: Dict[str, Optional[str]] = {n: None for n in all_nodes}

        heap = DaryMinHeap(d=d)
        distances[start_node] = 0.0
        heap.push_or_decrease(start_node, 0.0)

        nodes_settled = 0

        while not heap.is_empty():
            item = heap.pop_min()
            if item is None:
                break
            curr_dist, curr_node = item
            nodes_settled += 1

            if target_node is not None and curr_node == target_node:
                break

            for edge in weighted_adjacency.get(curr_node, []):
                tgt = str(edge["target"])
                wt = max(0.0, float(edge.get("weight", 1.0)))
                new_dist = curr_dist + wt

                if new_dist < distances.get(tgt, float("inf")):
                    distances[tgt] = new_dist
                    parents[tgt] = curr_node
                    heap.push_or_decrease(tgt, new_dist)

        shortest_path: List[str] = []
        if target_node and distances.get(target_node, float("inf")) != float("inf"):
            curr_t = target_node
            while curr_t is not None:
                shortest_path.append(curr_t)
                curr_t = parents.get(curr_t)
            shortest_path = shortest_path[::-1]

        valid_dist = {k: v for k, v in distances.items() if v != float("inf")}

        return {
            "distances": valid_dist,
            "parents": {k: v for k, v in parents.items() if distances.get(k, float("inf")) != float("inf")},
            "shortest_path_to_target": shortest_path,
            "target_distance": valid_dist.get(target_node) if target_node else None,
            "nodes_settled": nodes_settled,
            "d_parameter": d,
        }
