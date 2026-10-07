"""
================================================================================
ALGORITHM BLUEPRINT: TARJAN'S STRONGLY CONNECTED COMPONENTS (SCC)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph single-pass linear-time depth-first search
   partitioning directed graph topologies into maximal strongly connected subgraphs.
   Supports:
   - In-memory node and edge collection partitioning.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Idempotency & Normalization: Output SCCs are deterministically ordered.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V + E) single DFS traversal.
   - Space Complexity: O(V) for recursion stack, discovery index, and lowlink tables.

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
    FLOW_GET_STRONGLY_CONNECTED_COMPONENTS,
)



T = TypeVar("T")


@runtime_checkable
class DirectedNeighborProvider(Protocol[T]):
    def get_outgoing_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoTarjanScc:
    """
    --- contract:
      id: ALGO-KG-80
      name: KgAlgoTarjanScc
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
      - tarjan_scc
      - strongly_connected_components
      - directed_graph
      - cycle_decomposition
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_scc_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          get_outgoing:
            type: callable[[generic[T]], iterable[generic[T]]]
            description: Function yielding outbound directed neighbors.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        compute_scc:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) directed edges.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-80).
        scc_count:
          type: integer
          description: Number of isolated maximal strongly connected components.
        scc_list:
          type: array[array[any]]
          description: List of discovered SCC groups.
    ---
    """

    def compute_scc_generic(
        self,
        nodes: List[T],
        get_outgoing: Callable[[T], Iterable[T]],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        index = 0
        indices: Dict[Any, int] = {}
        lowlink: Dict[Any, int] = {}
        on_stack: Set[Any] = set()
        stack: List[Any] = []
        sccs: List[List[Any]] = []

        node_map: Dict[Any, T] = {node_key(n): n for n in nodes}

        def strongconnect(k: Any) -> None:
            nonlocal index
            indices[k] = index
            lowlink[k] = index
            index += 1
            stack.append(k)
            on_stack.add(k)

            n_entity = node_map.get(k)
            if n_entity is not None:
                for nbr in get_outgoing(n_entity):
                    nbr_k = node_key(nbr)
                    if nbr_k not in indices:
                        if nbr_k not in node_map:
                            node_map[nbr_k] = nbr
                        strongconnect(nbr_k)
                        lowlink[k] = min(lowlink[k], lowlink[nbr_k])
                    elif nbr_k in on_stack:
                        lowlink[k] = min(lowlink[k], indices[nbr_k])

            if lowlink[k] == indices[k]:
                scc: List[Any] = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == k:
                        break
                scc_sorted = sorted(scc, key=lambda x: str(x))
                sccs.append(scc_sorted)

        for n in nodes:
            k = node_key(n)
            if k not in indices:
                strongconnect(k)

        sccs.sort(key=lambda c: (len(c), str(c[0]) if c else ""))

        return {
            "algorithm": "ALGO-KG-80",
            "scc_count": len(sccs),
            "scc_list": sccs,
        }

    def compute_scc_with_store(
        self,
        store: Any,
        node_ids: List[str],
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def get_out(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")

        return self.compute_scc_generic(
            nodes=node_ids,
            get_outgoing=get_out,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_STRONGLY_CONNECTED_COMPONENTS",
            "query": FLOW_GET_STRONGLY_CONNECTED_COMPONENTS,
            "params": {
                "graph_name": graph_name,
            },
        }

    def compute_scc(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)

        return self.compute_scc_generic(
            nodes=nodes,
            get_outgoing=lambda u: adj[u],
            key_fn=lambda u: u,
        )
