"""
================================================================================
ALGORITHM BLUEPRINT: DIJKSTRA'S WEIGHTED SHORTEST PATH ON KNOWLEDGE GRAPH
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph single-source shortest path algorithm computing
   minimal cumulative weighted distances to all reachable nodes across directed
   and undirected graphs with non-negative edge costs.
   Supports:
   - In-memory execution using native min-priority heaps.
   - Generic entity types (T) and lazy weighted neighbor generators.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Non-Negative Edge Weights: Assumes edge weights >= 0.0.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O((V + E) log V) with binary min-heap priority frontier.
   - Space Complexity: O(V) for distance table and priority queue allocations.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import heapq
import itertools
from typing import (
    Dict,
    Any,
    List,
    Set,
    Tuple,
    Optional,
    Callable,
    Generic,
    TypeVar,
    Union,
    Iterable,
    Protocol,
    runtime_checkable,
)

from ....queries.knowledge_graph.analytics.kg_traversal_queries import (
    FLOW_GET_DIJKSTRA_SHORTEST_PATH,
    FLOW_GET_PROCEDURE_DIJKSTRA_SHORTEST_PATH,
    FLOW_GET_PROJECTED_DIJKSTRA_SHORTEST_PATH,
)



T = TypeVar("T")


@runtime_checkable
class GraphWeightedNeighborProvider(Protocol[T]):
    def get_weighted_neighbors(self, node: T) -> Iterable[Tuple[T, float]]:
        ...


class KgAlgoDijkstraShortestPath:
    """
    --- contract:
      id: ALGO-KG-66
      name: KgAlgoDijkstraShortestPath
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O((V + E) log V)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - dijkstra.shortest_path
      - weighted.graph
      - min_priority_queue
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_distances_generic:
          source:
            type: generic[T]
            description: Source starting entity or model instance.
            required: true
          get_neighbors:
            type: union[callable[[generic[T]], iterable[tuple[generic[T], float]]], GraphWeightedNeighborProvider[generic[T]]]
            description: Function yielding (neighbor, weight) tuples dynamically.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for node distance mapping.
            default: lambda x: x
            required: false
        compute_distances:
          adj:
            type: dict[str, list[tuple[str, float]]]
            description: Adjacency dictionary mapping node to (target, weight) list.
            required: true
          source:
            type: string
            description: Source node ID string.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-66).
        source:
          type: any
          description: Starting source node entity or identifier.
        distances:
          type: dict[any, number]
          description: Minimal accumulated distance map from source to all reachable nodes.
    ---
    """

    def compute_distances_generic(
        self,
        source: T,
        get_neighbors: Union[Callable[[T], Iterable[Tuple[T, float]]], GraphWeightedNeighborProvider[T]],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)

        if callable(get_neighbors):
            neighbor_fn = get_neighbors
        else:
            neighbor_fn = get_neighbors.get_weighted_neighbors

        source_key = node_key(source)
        distances: Dict[Any, float] = {source_key: 0.0}
        counter = itertools.count()
        pq: List[Tuple[float, int, T]] = [(0.0, next(counter), source)]

        while pq:
            d, _, u = heapq.heappop(pq)
            u_key = node_key(u)
            if d > distances.get(u_key, float("inf")):
                continue

            for v, weight in neighbor_fn(u):
                v_key = node_key(v)
                new_d = d + float(weight)
                if new_d < distances.get(v_key, float("inf")):
                    distances[v_key] = new_d
                    heapq.heappush(pq, (new_d, next(counter), v))

        return {
            "algorithm": "ALGO-KG-66",
            "source": source,
            "distances": {k: round(v, 4) for k, v in distances.items()},
        }

    def compute_distances_with_store(
        self,
        store: Any,
        source_id: str,
        rel_type: Optional[str] = None,
        weight_property: str = "weight",
    ) -> Dict[str, Any]:
        def store_neighbors(node_id: str) -> List[Tuple[str, float]]:
            neighbor_nodes = store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")
            return [(n.id, float(n.properties.get(weight_property, 1.0))) for n in neighbor_nodes]

        return self.compute_distances_generic(
            source=source_id,
            get_neighbors=store_neighbors,
            key_fn=lambda u: u,
        )

    def build_projected_graph_query(
        self,
        graph_name: str,
        source_id: str,
        target_id: Optional[str] = None,
        weight_prop: str = "cost",
    ) -> Dict[str, Any]:
        if target_id is not None:
            return {
                "query_name": "FLOW_GET_PROJECTED_DIJKSTRA_SHORTEST_PATH",
                "query": FLOW_GET_PROJECTED_DIJKSTRA_SHORTEST_PATH,
                "params": {
                    "graph_name": graph_name,
                    "source_id": source_id,
                    "target_id": target_id,
                    "weight_prop": weight_prop,
                },
            }
        return {
            "query_name": "FLOW_GET_DIJKSTRA_SHORTEST_PATH",
            "query": FLOW_GET_DIJKSTRA_SHORTEST_PATH,
            "params": {
                "graph_name": graph_name,
                "source_id": source_id,
                "weight_prop": weight_prop,
            },
        }

    def build_procedure_query(
        self,
        source_id: str,
        target_id: str,
        rel_type: str = "CONNECTED_TO",
        weight_prop: str = "weight",
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROCEDURE_DIJKSTRA_SHORTEST_PATH",
            "query": FLOW_GET_PROCEDURE_DIJKSTRA_SHORTEST_PATH,
            "params": {
                "source_id": source_id,
                "target_id": target_id,
                "rel_type": rel_type,
                "weight_prop": weight_prop,
            },
        }

    def build_cypher_query(
        self,
        graph_name: str,
        source_id: str,
        target_id: Optional[str] = None,
        weight_prop: str = "cost",
    ) -> Dict[str, Any]:
        return self.build_projected_graph_query(
            graph_name=graph_name,
            source_id=source_id,
            target_id=target_id,
            weight_prop=weight_prop,
        )

    def compute_distances(
        self,
        adj: Dict[str, List[Tuple[str, float]]],
        source: str,
    ) -> Dict[str, Any]:
        return self.compute_distances_generic(
            source=source,
            get_neighbors=lambda u: adj.get(u, []),
            key_fn=lambda u: u,
        )
