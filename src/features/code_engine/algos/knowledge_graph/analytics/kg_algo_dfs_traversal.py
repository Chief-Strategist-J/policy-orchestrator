"""
================================================================================
ALGORITHM BLUEPRINT: DEPTH-FIRST SEARCH (DFS) WITH CYCLE DETECTION
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph recursive depth-first path exploration algorithm
   identifying complete connected branch sequences and detecting directed cycles.
   Supports:
   - In-memory traversal with native Python dictionaries.
   - Generic entity types (T) and lazy neighbor expansion callables.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Exact Cycle Identification: Tracks recursion stack to detect back-edges.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V + E) for standard depth-first exploration.
   - Space Complexity: O(V) for recursion stack and visited tracking sets.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

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
    FLOW_GET_DFS_TRAVERSAL,
    FLOW_GET_PROCEDURE_DFS_TRAVERSAL,
    FLOW_GET_PROJECTED_DFS_TRAVERSAL,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoDfsTraversal:
    """
    --- contract:
      id: ALGO-KG-64
      name: KgAlgoDfsTraversal
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
      - dfs.traversal
      - cycle.detection
      - path.discovery
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
            description: Function yielding adjacent neighbor nodes dynamically.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for node equality.
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
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-64).
        traversal_order:
          type: array[generic[T]]
          description: Sequence of visited nodes in discovery order.
        has_cycle:
          type: boolean
          description: True if a directed cyclic dependency was detected, False otherwise.
    ---
    """

    def traverse_generic(
        self,
        start_node: T,
        get_neighbors: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)

        if callable(get_neighbors):
            neighbor_fn = get_neighbors
        else:
            neighbor_fn = get_neighbors.get_neighbors

        visited: Set[Any] = set()
        in_stack: Set[Any] = set()
        order: List[T] = []
        has_cycle = False

        def dfs(node: T):
            nonlocal has_cycle
            k = node_key(node)
            visited.add(k)
            in_stack.add(k)
            order.append(node)

            for neighbor in neighbor_fn(node):
                n_key = node_key(neighbor)
                if n_key in in_stack:
                    has_cycle = True
                elif n_key not in visited:
                    dfs(neighbor)

            in_stack.remove(k)

        dfs(start_node)
        return {
            "algorithm": "ALGO-KG-64",
            "traversal_order": order,
            "has_cycle": has_cycle,
        }

    def traverse_with_store(
        self,
        store: Any,
        start_node_id: str,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def store_neighbors(node_id: str) -> List[str]:
            return [n.id for n in store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")]

        return self.traverse_generic(
            start_node=start_node_id,
            get_neighbors=store_neighbors,
            key_fn=lambda u: u,
        )

    def build_procedure_query(
        self,
        start_node: str,
        max_depth: int = 10,
        rel_filter: str = ">",
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROCEDURE_DFS_TRAVERSAL",
            "query": FLOW_GET_PROCEDURE_DFS_TRAVERSAL,
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
            "query_name": "FLOW_GET_PROJECTED_DFS_TRAVERSAL",
            "query": FLOW_GET_PROJECTED_DFS_TRAVERSAL,
            "params": {
                "graph_name": graph_name,
                "start_node": start_node,
                "target_nodes": target_nodes or [],
            },
        }

    def build_cypher_query(
        self,
        start_node: str,
        max_depth: int = 10,
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
    ) -> Dict[str, Any]:
        return self.traverse_generic(
            start_node=start_node,
            get_neighbors=lambda u: adj.get(u, []),
            key_fn=lambda u: u,
        )
