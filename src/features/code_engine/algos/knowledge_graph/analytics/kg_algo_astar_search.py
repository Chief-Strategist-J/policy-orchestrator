"""
================================================================================
ALGORITHM BLUEPRINT: A* HEURISTIC-GUIDED GRAPH PATH SEARCH
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph heuristic pathfinding algorithm executing optimal
   shortest-path discovery across directed/undirected weighted graphs.
   Supports:
   - In-memory execution using native Python structures (zero external dependencies).
   - Lazy neighbor expansion for large-scale external databases (Neo4j, Memgraph,
     SQL, GraphQL, REST APIs) without requiring Docker or daemon setups.
   - Dynamic heuristic functions for custom machine learning / embedding models.
   - Database pushdown query generation for in-database graph analytics engines.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services, docker containers,
     or vendor-locked libraries for core algorithm execution.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions with no side-effects.
   - Optimality Guarantee: Guarantees shortest path if heuristic is admissible
     (h(n) <= true cost) and consistent / monotonic.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(E + V log V) in worst-case with binary min-heap frontier.
   - Space Complexity: O(V) for frontier priority queue, distance maps, and closed set.

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

from ....queries.knowledge_graph.analytics.kg_astar_queries import (
    FLOW_GET_PROJECTED_ASTAR_SHORTEST_PATH,
    FLOW_GET_PROCEDURE_ASTAR_SHORTEST_PATH,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_weighted_neighbors(self, node: T) -> Iterable[Tuple[T, float]]:
        ...


class KgAlgoAstarSearch:

    """
    --- contract:
      id: ALGO-KG-67
      name: KgAlgoAstarSearch
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(E + V log V)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - astar.search
      - heuristic.pathfinding
      - goal_directed
      - vendor_agnostic
      - lazy_expansion
      - custom_models
      input_schema:
        search_generic:
          source:
            type: generic[T]
            description: Start entity identifier or custom model instance.
            required: true
          target:
            type: union[generic[T], callable[[generic[T]], bool]]
            description: Destination entity instance or goal validation predicate.
            required: true
          get_neighbors:
            type: union[callable[[generic[T]], iterable[tuple[generic[T], float]]], GraphNeighborProvider[generic[T]]]
            description: Function yielding (neighbor_node, edge_cost) pairs dynamically or provider instance.
            required: true
          heuristic_fn:
            type: callable[[generic[T]], float]
            description: Admissible heuristic function estimating remaining cost to target.
            default: lambda x: 0.0 (Dijkstra fallback)
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            description: Unique hashable key extractor for custom node types or models.
            default: lambda x: x
            required: false
        search:
          adj:
            type: dict[str, list[tuple[str, float]]]
            description: In-memory adjacency list mapping node IDs to (neighbor, weight).
            required: true
          h_map:
            type: dict[str, float]
            description: Precomputed static heuristic map mapping node IDs to estimated cost.
            required: true
          source:
            type: string
            description: Source node identifier string.
            required: true
          target:
            type: string
            description: Target node identifier string.
            required: true
        build_projected_graph_query:
          graph_name:
            type: string
            description: Identifier of the in-memory projected graph catalog.
            required: true
          source_id:
            type: string
            description: Unique start node identifier.
            required: true
          target_id:
            type: string
            description: Unique destination target node identifier.
            required: true
          latitude_prop:
            type: string
            default: latitude
            required: false
          longitude_prop:
            type: string
            default: longitude
            required: false
          weight_prop:
            type: string
            default: cost
            required: false
        build_procedure_query:
          source_id:
            type: string
            description: Unique start node identifier.
            required: true
          target_id:
            type: string
            description: Unique destination target node identifier.
            required: true
          rel_type:
            type: string
            default: CONNECTED_TO
            required: false
          weight_prop:
            type: string
            default: weight
            required: false
          lat_prop:
            type: string
            default: latitude
            required: false
          lon_prop:
            type: string
            default: longitude
            required: false
      output_schema:
        search_result:
          algorithm:
            type: string
            description: Canonical algorithm registry identifier (ALGO-KG-67).
          found:
            type: boolean
            description: True if an optimal path to target was discovered, False otherwise.
          cost:
            type: number
            description: Total accumulated path cost (float('inf') if unreachable).
          path:
            type: array[generic[T]]
            description: Ordered sequence of visited nodes from source to target.
        query_plan_result:
          query_name:
            type: string
            description: Standardized FLOW_* named query constant identifier.
          query:
            type: string
            description: Fully parameterized Cypher/GQL query string.
          params:
            type: dict[str, any]
            description: Key-value map of runtime parameters.
    ---
    """
    def search_generic(
        self,
        source: T,
        target: Union[T, Callable[[T], bool]],
        get_neighbors: Union[Callable[[T], Iterable[Tuple[T, float]]], GraphNeighborProvider[T]],
        heuristic_fn: Optional[Callable[[T], float]] = None,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        h_func = heuristic_fn if heuristic_fn is not None else (lambda x: 0.0)
        is_goal: Callable[[T], bool] = (lambda x: x == target) if not callable(target) else target

        if callable(get_neighbors):
            neighbor_fn = get_neighbors
        else:
            neighbor_fn = get_neighbors.get_weighted_neighbors

        source_key = node_key(source)
        start_h = float(h_func(source))



        counter = itertools.count()
        pq: List[Tuple[float, float, int, T, List[T]]] = [
            (start_h, 0.0, next(counter), source, [source])
        ]
        g_scores: Dict[Any, float] = {source_key: 0.0}
        closed_set: Set[Any] = set()

        while pq:
            f, g, _, current_node, path = heapq.heappop(pq)
            curr_key = node_key(current_node)

            if is_goal(current_node):
                return {
                    "algorithm": "ALGO-KG-67",
                    "found": True,
                    "cost": g,
                    "path": path,
                }

            if curr_key in closed_set:
                continue

            if g > g_scores.get(curr_key, float("inf")):
                continue

            closed_set.add(curr_key)

            for neighbor, weight in neighbor_fn(current_node):
                n_key = node_key(neighbor)
                if n_key in closed_set:
                    continue

                tentative_g = g + float(weight)
                if tentative_g < g_scores.get(n_key, float("inf")):
                    g_scores[n_key] = tentative_g
                    h_val = float(h_func(neighbor))
                    new_f = tentative_g + h_val
                    heapq.heappush(
                        pq,
                        (new_f, tentative_g, next(counter), neighbor, path + [neighbor]),
                    )

        return {
            "algorithm": "ALGO-KG-67",
            "found": False,
            "cost": float("inf"),
            "path": [],
        }

    def search_with_store(
        self,
        store: Any,
        source_id: str,
        target_id: str,
        rel_type: Optional[str] = None,
        weight_property: str = "weight",
        heuristic_fn: Optional[Callable[[str], float]] = None,
    ) -> Dict[str, Any]:
        def store_neighbors(node_id: str) -> List[Tuple[str, float]]:
            neighbor_nodes = store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")
            return [
                (n.id, float(n.properties.get(weight_property, 1.0)))
                for n in neighbor_nodes
            ]

        return self.search_generic(
            source=source_id,
            target=target_id,
            get_neighbors=store_neighbors,
            heuristic_fn=heuristic_fn,
            key_fn=lambda u: u,
        )


    def search(
        self,
        adj: Dict[str, List[Tuple[str, float]]],
        h_map: Dict[str, float],
        source: str,
        target: str,
    ) -> Dict[str, Any]:
        return self.search_generic(
            source=source,
            target=target,
            get_neighbors=lambda u: adj.get(u, []),
            heuristic_fn=lambda u: h_map.get(u, 0.0),
            key_fn=lambda u: u,
        )

    def build_projected_graph_query(
        self,
        graph_name: str,
        source_id: str,
        target_id: str,
        latitude_prop: str = "latitude",
        longitude_prop: str = "longitude",
        weight_prop: str = "cost",
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROJECTED_ASTAR_SHORTEST_PATH",
            "query": FLOW_GET_PROJECTED_ASTAR_SHORTEST_PATH,
            "params": {
                "graph_name": graph_name,
                "source_id": source_id,
                "target_id": target_id,
                "latitude_prop": latitude_prop,
                "longitude_prop": longitude_prop,
                "weight_prop": weight_prop,
            },
        }

    def build_procedure_query(
        self,
        source_id: str,
        target_id: str,
        rel_type: str = "CONNECTED_TO",
        weight_prop: str = "weight",
        lat_prop: str = "latitude",
        lon_prop: str = "longitude",
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROCEDURE_ASTAR_SHORTEST_PATH",
            "query": FLOW_GET_PROCEDURE_ASTAR_SHORTEST_PATH,
            "params": {
                "source_id": source_id,
                "target_id": target_id,
                "rel_type": rel_type,
                "weight_prop": weight_prop,
                "lat_prop": lat_prop,
                "lon_prop": lon_prop,
            },
        }

    def build_neo4j_gds_query(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.build_projected_graph_query(*args, **kwargs)

    def build_neo4j_apoc_query(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.build_procedure_query(*args, **kwargs)




