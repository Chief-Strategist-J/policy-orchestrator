"""
================================================================================
ALGORITHM BLUEPRINT: WARSHALL TRANSITIVE CLOSURE REACHABILITY MATRIX
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph all-pairs directed reachability closure engine
   computing the complete set of reachable downstream vertices for every origin node.
   Supports:
   - In-memory adjacency closure computation.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Deterministic Ordering: Reachability sets sorted deterministically.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V * (V + E)) via BFS search from each vertex.
   - Space Complexity: O(V^2) for the complete reachability matrix.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict, deque
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
    FLOW_GET_TRANSITIVE_CLOSURE,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoTransitiveClosure:
    """
    --- contract:
      id: ALGO-KG-72
      name: KgAlgoTransitiveClosure
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V * (V + E))
        space: O(V^2)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - transitive_closure
      - warshall.reachability
      - complete_closure
      - all_pairs_reachability
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_closure_generic:
          nodes:
            type: array[generic[T]]
            description: List of origin entities.
            required: true
          neighbor_provider:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function or provider resolving outbound adjacent entities.
            required: true
          max_depth:
            type: integer
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        compute_closure:
          adj:
            type: dict[string, array[string]]
            description: Directed adjacency map.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-72).
        closure_pairs_count:
          type: integer
          description: Total count of (u, v) reachability pairs.
        reachability_map:
          type: dict[any, array[any]]
          description: Mapping of each source entity key to sorted reachable entity keys.
    ---
    """

    def compute_closure_generic(
        self,
        nodes: List[T],
        neighbor_provider: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        max_depth: Optional[int] = None,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        if callable(neighbor_provider):
            get_neighbors_fn = neighbor_provider
        else:
            get_neighbors_fn = neighbor_provider.get_neighbors

        closure: Dict[Any, List[Any]] = {}

        for origin in nodes:
            u_key = node_key(origin)
            visited_keys: Set[Any] = set()
            queue: deque = deque([(origin, 0)])

            while queue:
                curr_entity, depth = queue.popleft()
                if max_depth is not None and depth >= max_depth:
                    continue

                for nbr_entity in get_neighbors_fn(curr_entity):
                    v_key = node_key(nbr_entity)
                    if v_key not in visited_keys:
                        visited_keys.add(v_key)
                        queue.append((nbr_entity, depth + 1))

            closure[u_key] = sorted(list(visited_keys), key=lambda x: str(x))

        total_pairs = sum(len(targets) for targets in closure.values())

        return {
            "algorithm": "ALGO-KG-72",
            "closure_pairs_count": total_pairs,
            "reachability_map": closure,
        }

    def compute_closure_with_store(
        self,
        store: Any,
        node_ids: List[str],
        max_depth: Optional[int] = None,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def get_out(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")

        return self.compute_closure_generic(
            nodes=node_ids,
            neighbor_provider=get_out,
            max_depth=max_depth,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        source_id: str,
        max_depth: int = 5,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_TRANSITIVE_CLOSURE",
            "query": FLOW_GET_TRANSITIVE_CLOSURE,
            "params": {
                "source_id": source_id,
                "max_depth": max_depth,
            },
        }

    def compute_closure(
        self,
        adj: Dict[str, List[str]],
        max_depth: Optional[int] = None,
    ) -> Dict[str, Any]:
        nodes = list(adj.keys())
        return self.compute_closure_generic(
            nodes=nodes,
            neighbor_provider=lambda u: adj.get(u, []),
            max_depth=max_depth,
            key_fn=lambda u: u,
        )
