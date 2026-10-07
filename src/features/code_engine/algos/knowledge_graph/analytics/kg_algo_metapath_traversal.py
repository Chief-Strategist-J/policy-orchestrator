"""
================================================================================
ALGORITHM BLUEPRINT: HETEROGENEOUS METAPATH-CONSTRAINED GRAPH TRAVERSAL
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph schema-directed multi-hop relational path explorer
   computing reachable entity frontiers constrained by an ordered sequence of edge types.
   Supports:
   - In-memory typed edge traversal.
   - Generic entity types (T) and lazy typed neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Deterministic Output: Target nodes sorted lexicographically.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Frontier_Size * Average_Typed_Degree) per metapath step.
   - Space Complexity: O(Frontier_Size) active state memory.

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

from ....queries.knowledge_graph.analytics.kg_reachability_queries import (
    FLOW_GET_METAPATH_TRAVERSAL,
)



T = TypeVar("T")


@runtime_checkable
class TypedNeighborProvider(Protocol[T]):
    def get_typed_neighbors(self, node: T, rel_type: str) -> Iterable[T]:
        ...


class KgAlgoMetapathTraversal:
    """
    --- contract:
      id: ALGO-KG-70
      name: KgAlgoMetapathTraversal
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Frontier * Step_Degree)
        space: O(Frontier)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - metapath.traversal
      - heterogeneous.graph
      - schema_constrained
      - relational_walk
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        traverse_metapath_generic:
          start_nodes:
            type: array[generic[T]]
            description: Initial seed entity frontier.
            required: true
          get_typed_neighbors:
            type: callable[[generic[T], string], iterable[generic[T]]]
            description: Function yielding successors matching a relationship type.
            required: true
          metapath:
            type: array[string]
            description: Sequence of relationship type names to traverse in order.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        traverse_metapath:
          edges:
            type: array[object]
            description: List of typed edge dicts with keys (source, target, type).
            required: true
          start_nodes:
            type: array[string]
            description: Initial seed node identifiers.
            required: true
          metapath:
            type: array[string]
            description: Sequence of edge type strings.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-70).
        metapath:
          type: array[string]
          description: Input relationship traversal sequence.
        target_nodes:
          type: array[any]
          description: Sorted list of reachable target entity keys.
    ---
    """

    def traverse_metapath_generic(
        self,
        start_nodes: List[T],
        get_typed_neighbors: Callable[[T, str], Iterable[T]],
        metapath: List[str],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        frontier_entities: List[T] = list(start_nodes)

        for rel_type in metapath:
            next_frontier_entities: List[T] = []
            seen_keys: Set[Any] = set()
            for curr_entity in frontier_entities:
                for nbr_entity in get_typed_neighbors(curr_entity, rel_type):
                    k = node_key(nbr_entity)
                    if k not in seen_keys:
                        seen_keys.add(k)
                        next_frontier_entities.append(nbr_entity)
            frontier_entities = next_frontier_entities

        target_keys = [node_key(n) for n in frontier_entities]
        sorted_targets = sorted(list(set(target_keys)), key=lambda x: str(x))

        return {
            "algorithm": "ALGO-KG-70",
            "metapath": metapath,
            "target_nodes": sorted_targets,
        }

    def traverse_metapath_with_store(
        self,
        store: Any,
        start_node_ids: List[str],
        metapath: List[str],
    ) -> Dict[str, Any]:
        def get_typed(node_id: str, rel_type: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")

        return self.traverse_metapath_generic(
            start_nodes=start_node_ids,
            get_typed_neighbors=get_typed,
            metapath=metapath,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        start_node: str,
        metapath: List[str],
        max_hops: int = 10,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_METAPATH_TRAVERSAL",
            "query": FLOW_GET_METAPATH_TRAVERSAL,
            "params": {
                "start_node": start_node,
                "metapath": metapath,
                "max_hops": max_hops,
            },
        }

    def traverse_metapath(
        self,
        edges: List[Dict[str, str]],
        start_nodes: List[str],
        metapath: List[str],
    ) -> Dict[str, Any]:
        def get_typed_edge(u: str, rel_type: str) -> List[str]:
            return [
                e["target"]
                for e in edges
                if e.get("source") == u and e.get("type") == rel_type and "target" in e
            ]

        return self.traverse_metapath_generic(
            start_nodes=start_nodes,
            get_typed_neighbors=get_typed_edge,
            metapath=metapath,
            key_fn=lambda u: u,
        )
