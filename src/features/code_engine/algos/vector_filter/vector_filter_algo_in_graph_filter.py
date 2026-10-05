"""
================================================================================
ALGORITHM BLUEPRINT: VECTOR IN-GRAPH FILTERING (ACORN-STYLE) (ALGO-VEC-FLTR-82)
================================================================================

ACORN-style in-graph filtering performs proximity graph traversal while strictly
enforcing metadata filter constraints. When traversing candidate nodes, neighbors
that fail the filter are traversed across 2-hop connectivity bridges so the allowed
subgraph remains navigable even when significant proportions of vertices are masked.
Only nodes passing the predicate are eligible for top-k output insertion.
"""

from typing import Any, Dict, List, Set, Tuple
import heapq
import math


class VectorFilterAlgoInGraphFilter:
    """
    --- contract:
      id: ALGO-VEC-FLTR-82
      name: VectorFilterAlgoInGraphFilter
      category: filter
      complexity: O(L * M_eff * D)
      pure_function: true
      zero_inline_comments: true
      input_schema:
        vectors: list[list[float]]
        metadata: list[dict[str, any]]
        adjacency: dict[str, list[int]]
        entry_point: int
        query: list[float]
        filters: dict[str, any]
        k: int
        ef_search: int
      output_schema:
        total_visited: int
        allowed_evaluated: int
        filtered_bypassed: int
        neighbors: list[dict[str, any]]
    ---
    """

    @staticmethod
    def _matches_filters(item_meta: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        for key, expected in filters.items():
            if key not in item_meta:
                return False
            val = item_meta[key]
            if isinstance(expected, list):
                if val not in expected:
                    return False
            elif val != expected:
                return False
        return True

    @staticmethod
    def search(
        vectors: List[List[float]],
        metadata: List[Dict[str, Any]],
        adjacency: Dict[str, List[int]],
        entry_point: int,
        query: List[float],
        filters: Dict[str, Any],
        k: int = 5,
        ef_search: int = 16,
    ) -> Dict[str, Any]:
        if not vectors or not query or entry_point >= len(vectors):
            return {
                "total_visited": 0,
                "allowed_evaluated": 0,
                "filtered_bypassed": 0,
                "neighbors": [],
            }

        dim = len(query)

        def dist(u: int) -> float:
            vec = vectors[u]
            return math.sqrt(sum((vec[d] - query[d]) ** 2 for d in range(min(dim, len(vec)))))

        visited: Set[int] = {entry_point}
        candidates: List[Tuple[float, int]] = [(dist(entry_point), entry_point)]
        allowed_results: List[Tuple[float, int]] = []

        allowed_count = 0
        bypassed_count = 0

        if VectorFilterAlgoInGraphFilter._matches_filters(metadata[entry_point], filters):
            allowed_count += 1
            heapq.heappush(allowed_results, (-candidates[0][0], entry_point))
        else:
            bypassed_count += 1

        while candidates:
            curr_dist, curr_node = heapq.heappop(candidates)
            if allowed_results and curr_dist > -allowed_results[0][0] and len(allowed_results) >= ef_search:
                break

            nbrs = adjacency.get(str(curr_node), adjacency.get(curr_node, []))
            for nbr in nbrs:
                if nbr not in visited and nbr < len(vectors):
                    visited.add(nbr)
                    d = dist(nbr)
                    heapq.heappush(candidates, (d, nbr))

                    passes = VectorFilterAlgoInGraphFilter._matches_filters(metadata[nbr], filters)
                    if passes:
                        allowed_count += 1
                        heapq.heappush(allowed_results, (-d, nbr))
                        if len(allowed_results) > ef_search:
                            heapq.heappop(allowed_results)
                    else:
                        bypassed_count += 1
                        sec_nbrs = adjacency.get(str(nbr), adjacency.get(nbr, []))
                        for s_nbr in sec_nbrs:
                            if s_nbr not in visited and s_nbr < len(vectors):
                                visited.add(s_nbr)
                                s_d = dist(s_nbr)
                                heapq.heappush(candidates, (s_d, s_nbr))
                                if VectorFilterAlgoInGraphFilter._matches_filters(metadata[s_nbr], filters):
                                    allowed_count += 1
                                    heapq.heappush(allowed_results, (-s_d, s_nbr))
                                    if len(allowed_results) > ef_search:
                                        heapq.heappop(allowed_results)

        final_list = [(-neg_d, node_id) for neg_d, node_id in allowed_results]
        final_list.sort(key=lambda x: x[0])
        top_k = final_list[:k]

        return {
            "total_visited": len(visited),
            "allowed_evaluated": allowed_count,
            "filtered_bypassed": bypassed_count,
            "neighbors": [
                {"id": node_id, "distance": d, "metadata": metadata[node_id]}
                for d, node_id in top_k
            ],
        }
