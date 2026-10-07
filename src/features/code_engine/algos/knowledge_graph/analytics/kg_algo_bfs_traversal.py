"""
================================================================================
ALGORITHM BLUEPRINT: BREADTH-FIRST SEARCH (BFS) KNOWLEDGE GRAPH TRAVERSAL
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph level-order traversal algorithm exploring graph
   neighborhoods radially up to a parameterized maximum depth boundary.
   Supports:
   - In-memory traversal with native Python structures.
   - Generic entity types (T) and lazy neighbor expansion callables.
   - Integration with any third-party graph database via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Optimal Depth Bounding: Level tracking strictly respects max_depth limit.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V + E) for standard breadth-first exploration.
   - Space Complexity: O(V) for frontier queue and visited depth mapping.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import deque
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
    FLOW_GET_BFS_TRAVERSAL,
    FLOW_GET_PROCEDURE_BFS_TRAVERSAL,
    FLOW_GET_PROJECTED_BFS_TRAVERSAL,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoBfsTraversal:
    """
    --- contract:
      id: ALGO-KG-63
      name: KgAlgoBfsTraversal
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - bfs.traversal
      - shortest_hop
      - graph.search
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        traverse_generic:
          start_node:
            type: generic[T]
            description: Starting traversal node or model instance.
            required: true
          get_neighbors:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function yielding unweighted neighboring nodes dynamically or provider instance.
            required: true
          max_depth:
            type: integer
            default: 3
            description: Maximum hop distance from start_node.
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for custom node types.
            default: lambda x: x
            required: false
        traverse:
          adj:
            type: dict[str, list[str]]
            description: In-memory adjacency list mapping node IDs to list of neighbor IDs.
            required: true
          start_node:
            type: string
            description: Start node identifier string.
            required: true
          max_depth:
            type: integer
            default: 3
            description: Maximum exploration depth.
            required: false
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-63).
        visited_count:
          type: integer
          description: Total number of reachable nodes within depth limit.
        visited_nodes:
          type: array[generic[T]]
          description: Ordered collection of discovered nodes.
        depth_levels:
          type: dict[any, integer]
          description: Map of node key to minimum hop depth from start node.
    ---
    """

    def traverse_generic(
        self,
        start_node: T,
        get_neighbors: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        max_depth: int = 3,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)

        if callable(get_neighbors):
            neighbor_fn = get_neighbors
        else:
            neighbor_fn = get_neighbors.get_neighbors

        start_key = node_key(start_node)
        visited_depth: Dict[Any, int] = {start_key: 0}
        visited_nodes: List[T] = [start_node]
        queue = deque([(start_node, 0)])

        while queue:
            curr, depth = queue.popleft()
            if depth < max_depth:
                for neighbor in neighbor_fn(curr):
                    n_key = node_key(neighbor)
                    if n_key not in visited_depth:
                        visited_depth[n_key] = depth + 1
                        visited_nodes.append(neighbor)
                        queue.append((neighbor, depth + 1))

        return {
            "algorithm": "ALGO-KG-63",
            "visited_count": len(visited_nodes),
            "visited_nodes": visited_nodes,
            "depth_levels": visited_depth,
        }

    def traverse_with_store(
        self,
        store: Any,
        start_node_id: str,
        max_depth: int = 3,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def store_neighbors(node_id: str) -> List[str]:
            neighbor_nodes = store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")
            return [n.id for n in neighbor_nodes]

        return self.traverse_generic(
            start_node=start_node_id,
            get_neighbors=store_neighbors,
            max_depth=max_depth,
            key_fn=lambda u: u,
        )

    def build_procedure_query(
        self,
        start_node: str,
        max_depth: int = 3,
        rel_filter: str = ">",
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROCEDURE_BFS_TRAVERSAL",
            "query": FLOW_GET_PROCEDURE_BFS_TRAVERSAL,
            "params": {
                "start_node": start_node,
                "max_depth": max_depth,
                "rel_filter": rel_filter,
            },
        }

    def build_projected_graph_query(
        self,
        graph_name: str,
        start_node: str,
        target_nodes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROJECTED_BFS_TRAVERSAL",
            "query": FLOW_GET_PROJECTED_BFS_TRAVERSAL,
            "params": {
                "graph_name": graph_name,
                "start_node": start_node,
                "target_nodes": target_nodes or [],
            },
        }

    def build_cypher_query(
        self,
        start_node: str,
        max_depth: int = 3,
        rel_filter: str = ">",
    ) -> Dict[str, Any]:
        return self.build_procedure_query(
            start_node=start_node,
            max_depth=max_depth,
            rel_filter=rel_filter,
        )

    def traverse(
        self,
        adj: Dict[str, List[str]],
        start_node: str,
        max_depth: int = 3,
    ) -> Dict[str, Any]:
        res = self.traverse_generic(
            start_node=start_node,
            get_neighbors=lambda u: adj.get(u, []),
            max_depth=max_depth,
            key_fn=lambda u: u,
        )
        return {
            "algorithm": "ALGO-KG-63",
            "visited_count": res["visited_count"],
            "visited_nodes": sorted(list(res["depth_levels"].keys())),
            "depth_levels": res["depth_levels"],
        }
