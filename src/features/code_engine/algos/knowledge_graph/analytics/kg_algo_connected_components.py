"""
================================================================================
ALGORITHM BLUEPRINT: UNION-FIND DISJOINT SET CONNECTED COMPONENTS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph disjoint set union-find algorithm with path compression
   and union by rank to partition undirected graph topologies into maximal connected subgraphs.
   Supports:
   - In-memory node and edge collection partitioning.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Idempotency & Normalization: Output components are deterministically sorted.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V + E * alpha(V)) where alpha is the inverse Ackermann function.
   - Space Complexity: O(V) parent and rank mapping tables.

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

from ....queries.knowledge_graph.analytics.kg_community_queries import (
    FLOW_GET_CONNECTED_COMPONENTS,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoConnectedComponents:
    """
    --- contract:
      id: ALGO-KG-79
      name: KgAlgoConnectedComponents
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E * alpha(V))
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - connected_components
      - union_find
      - disjoint_sets
      - graph_partitioning
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        find_components_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          neighbor_provider:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function or provider resolving undirected adjacent entities.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        find_components:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) undirected/directed edges.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-79).
        component_count:
          type: integer
          description: Number of isolated maximal connected subgraphs.
        components:
          type: array[array[any]]
          description: List of grouped entity components.
    ---
    """

    def find_components_generic(
        self,
        nodes: List[T],
        neighbor_provider: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        if callable(neighbor_provider):
            get_neighbors_fn = neighbor_provider
        else:
            get_neighbors_fn = neighbor_provider.get_neighbors

        parent: Dict[Any, Any] = {}
        rank: Dict[Any, int] = {}
        node_lookup: Dict[Any, T] = {}

        for n in nodes:
            k = node_key(n)
            parent[k] = k
            rank[k] = 0
            node_lookup[k] = n

        def find(i: Any) -> Any:
            path = []
            curr = i
            while parent[curr] != curr:
                path.append(curr)
                curr = parent[curr]
            for node in path:
                parent[node] = curr
            return curr

        def union(i: Any, j: Any) -> None:
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                if rank[root_i] < rank[root_j]:
                    parent[root_i] = root_j
                elif rank[root_i] > rank[root_j]:
                    parent[root_j] = root_i
                else:
                    parent[root_j] = root_i
                    rank[root_i] += 1

        for n in nodes:
            u_key = node_key(n)
            for nbr in get_neighbors_fn(n):
                v_key = node_key(nbr)
                if v_key in parent:
                    union(u_key, v_key)

        comps: Dict[Any, List[Any]] = {}
        for n in nodes:
            k = node_key(n)
            root = find(k)
            comps.setdefault(root, []).append(k)

        sorted_comps = [sorted(c, key=lambda x: str(x)) for c in comps.values()]
        sorted_comps.sort(key=lambda c: (len(c), str(c[0]) if c else ""))

        return {
            "algorithm": "ALGO-KG-79",
            "component_count": len(sorted_comps),
            "components": sorted_comps,
        }

    def find_components_with_store(
        self,
        store: Any,
        node_ids: List[str],
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def get_undirected(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="UNDIRECTED")

        return self.find_components_generic(
            nodes=node_ids,
            neighbor_provider=get_undirected,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_CONNECTED_COMPONENTS",
            "query": FLOW_GET_CONNECTED_COMPONENTS,
            "params": {
                "graph_name": graph_name,
            },
        }

    def find_components(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        adj: Dict[str, List[str]] = {n: [] for n in nodes}
        for u, v in edges:
            if u in adj:
                adj[u].append(v)
            if v in adj:
                adj[v].append(u)

        return self.find_components_generic(
            nodes=nodes,
            neighbor_provider=lambda u: adj.get(u, []),
            key_fn=lambda u: u,
        )
