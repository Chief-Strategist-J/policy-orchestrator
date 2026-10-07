"""
================================================================================
ALGORITHM BLUEPRINT: LABEL PROPAGATION ALGORITHM (LPA) GRAPH PARTITIONING
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph semi-supervised community detection and partition
   propagation algorithm iteratively assigning dominant neighbor community memberships.
   Supports:
   - In-memory node and edge collection partitioning.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Early Termination: Terminates upon label convergence across all non-seeded nodes.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Iterations * (V + E)) per propagation cycle.
   - Space Complexity: O(V) for community label tables and neighbor degree frequency maps.

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
    FLOW_GET_LABEL_PROPAGATION,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoLabelPropagation:
    """
    --- contract:
      id: ALGO-KG-83
      name: KgAlgoLabelPropagation
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Iter * E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - label_propagation
      - semi_supervised
      - community_detection
      - graph_partitioning
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        propagate_labels_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          neighbor_provider:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function or provider resolving adjacent entities.
            required: true
          initial_labels:
            type: dict[any, string]
            description: Seed labels mapped by entity key.
            required: true
          max_iter:
            type: integer
            default: 10
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        propagate_labels:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) edges.
            required: true
          initial_labels:
            type: dict[string, string]
            description: Seed labels per node.
            required: true
          max_iter:
            type: integer
            default: 10
            required: false
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-83).
        assigned_labels:
          type: dict[any, string]
          description: Map of entity keys to converged community label strings.
    ---
    """

    def propagate_labels_generic(
        self,
        nodes: List[T],
        neighbor_provider: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        initial_labels: Dict[Any, str],
        max_iter: int = 10,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        if callable(neighbor_provider):
            get_neighbors_fn = neighbor_provider
        else:
            get_neighbors_fn = neighbor_provider.get_neighbors

        node_map: Dict[Any, T] = {node_key(n): n for n in nodes}
        labels: Dict[Any, str] = dict(initial_labels)

        for n in nodes:
            k = node_key(n)
            if k not in labels:
                labels[k] = f"unlabeled_{k}"

        for _ in range(max_iter):
            changed = False
            for n in nodes:
                k = node_key(n)
                if k in initial_labels:
                    continue

                counts: Dict[str, int] = defaultdict(int)
                for nbr in get_neighbors_fn(n):
                    nbr_k = node_key(nbr)
                    if nbr_k in labels:
                        counts[labels[nbr_k]] += 1

                if counts:
                    top_label = max(counts.items(), key=lambda x: (x[1], x[0]))[0]
                    if top_label != labels[k]:
                        labels[k] = top_label
                        changed = True

            if not changed:
                break

        return {
            "algorithm": "ALGO-KG-83",
            "assigned_labels": labels,
        }

    def propagate_labels_with_store(
        self,
        store: Any,
        node_ids: List[str],
        initial_labels: Dict[str, str],
        max_iter: int = 10,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def get_undirected(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="UNDIRECTED")

        return self.propagate_labels_generic(
            nodes=node_ids,
            neighbor_provider=get_undirected,
            initial_labels=initial_labels,
            max_iter=max_iter,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        max_iterations: int = 10,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_LABEL_PROPAGATION",
            "query": FLOW_GET_LABEL_PROPAGATION,
            "params": {
                "graph_name": graph_name,
                "max_iterations": max_iterations,
            },
        }

    def propagate_labels(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        initial_labels: Dict[str, str],
        max_iter: int = 10,
    ) -> Dict[str, Any]:
        adj: Dict[str, List[str]] = {n: [] for n in nodes}
        for u, v in edges:
            if u in adj:
                adj[u].append(v)
            if v in adj:
                adj[v].append(u)

        return self.propagate_labels_generic(
            nodes=nodes,
            neighbor_provider=lambda u: adj.get(u, []),
            initial_labels=initial_labels,
            max_iter=max_iter,
            key_fn=lambda u: u,
        )
