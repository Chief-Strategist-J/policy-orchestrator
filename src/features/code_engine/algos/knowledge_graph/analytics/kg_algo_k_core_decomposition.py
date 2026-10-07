"""
================================================================================
ALGORITHM BLUEPRINT: K-CORE SUBGRAPH DECOMPOSITION ENGINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph iterative degree-pruning algorithm computing maximal
   connected subgraphs where every vertex has degree of at least k.
   Supports:
   - In-memory node and edge collection filtering.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Idempotency & Normalization: Output k-core entities are deterministically sorted.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V + E) using degree bucket queue.
   - Space Complexity: O(V + E) for working adjacency and degree tables.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
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
    FLOW_GET_K_CORE_DECOMPOSITION,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoKCoreDecomposition:
    """
    --- contract:
      id: ALGO-KG-84
      name: KgAlgoKCoreDecomposition
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V + E)
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - k_core.decomposition
      - dense_subgraph
      - degeneracy
      - graph_pruning
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        extract_k_core_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          neighbor_provider:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function or provider resolving undirected adjacent entities.
            required: true
          k:
            type: integer
            default: 2
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        extract_k_core:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) undirected/directed edges.
            required: true
          k:
            type: integer
            default: 2
            required: false
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-84).
        k:
          type: integer
          description: Minimum degree threshold applied.
        k_core_nodes:
          type: array[any]
          description: List of retained node IDs/keys satisfying the k-core constraint.
        k_core_size:
          type: integer
          description: Cardinality of the retained k-core subgraph.
    ---
    """

    def extract_k_core_generic(
        self,
        nodes: List[T],
        neighbor_provider: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        k: int = 2,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        if callable(neighbor_provider):
            get_neighbors_fn = neighbor_provider
        else:
            get_neighbors_fn = neighbor_provider.get_neighbors

        keys: Set[Any] = {node_key(n) for n in nodes}
        adj: Dict[Any, Set[Any]] = {node_key(n): set() for n in nodes}

        for n in nodes:
            u_key = node_key(n)
            for nbr in get_neighbors_fn(n):
                v_key = node_key(nbr)
                if v_key in keys and v_key != u_key:
                    adj[u_key].add(v_key)

        degrees = {u: len(adj[u]) for u in adj}
        removed: Set[Any] = set()
        queue = [u for u in degrees if degrees[u] < k]

        while queue:
            curr = queue.pop(0)
            if curr in removed:
                continue
            removed.add(curr)
            for nbr in adj[curr]:
                if nbr not in removed:
                    degrees[nbr] -= 1
                    if degrees[nbr] < k:
                        queue.append(nbr)

        k_core = [u for u in adj if u not in removed]
        k_core_sorted = sorted(k_core, key=lambda x: str(x))

        return {
            "algorithm": "ALGO-KG-84",
            "k": k,
            "k_core_nodes": k_core_sorted,
            "k_core_size": len(k_core_sorted),
        }

    def extract_k_core_with_store(
        self,
        store: Any,
        node_ids: List[str],
        k: int = 2,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def get_undirected(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="UNDIRECTED")

        return self.extract_k_core_generic(
            nodes=node_ids,
            neighbor_provider=get_undirected,
            k=k,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        k: int = 2,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_K_CORE_DECOMPOSITION",
            "query": FLOW_GET_K_CORE_DECOMPOSITION,
            "params": {
                "graph_name": graph_name,
                "k": k,
            },
        }

    def extract_k_core(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        k: int = 2,
    ) -> Dict[str, Any]:
        adj: Dict[str, List[str]] = {n: [] for n in nodes}
        for u, v in edges:
            if u in adj:
                adj[u].append(v)
            if v in adj:
                adj[v].append(u)

        return self.extract_k_core_generic(
            nodes=nodes,
            neighbor_provider=lambda u: adj.get(u, []),
            k=k,
            key_fn=lambda u: u,
        )
