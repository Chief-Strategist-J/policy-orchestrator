"""
================================================================================
ALGORITHM BLUEPRINT: CLOSENESS AND HARMONIC CENTRALITY METRICS
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph distance-reciprocal accessibility metric computing
   Harmonic Centrality to quantify the speed of information dissemination from
   each node to all other reachable and disconnected graph components.
   Supports:
   - In-memory BFS-driven harmonic reciprocal sum calculations.
   - Generic entity types (T) and lazy neighbor expansion callables.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Disconnected Graph Robustness: Infinite distances gracefully evaluate to 1/inf = 0.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V * (V + E)) for all-pairs single-source shortest path sweeps.
   - Space Complexity: O(V) for BFS queues and hop-distance maps.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import deque, defaultdict
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

from ....queries.knowledge_graph.analytics.kg_centrality_queries import (
    FLOW_GET_HARMONIC_CLOSENESS,
)



T = TypeVar("T")


class KgAlgoClosenessHarmonic:
    """
    --- contract:
      id: ALGO-KG-77
      name: KgAlgoClosenessHarmonic
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V * (V + E))
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - closeness_centrality
      - harmonic_centrality
      - graph_distances
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_harmonic_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          get_neighbors:
            type: callable[[generic[T]], iterable[generic[T]]]
            description: Function yielding adjacent nodes dynamically.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for node dictionary mapping.
            default: lambda x: x
            required: false
        compute_harmonic:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of undirected or bidirectional edges.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-77).
        harmonic_scores:
          type: dict[any, number]
          description: Map of node key to harmonic centrality score.
    ---
    """

    def compute_harmonic_generic(
        self,
        nodes: List[T],
        get_neighbors: Callable[[T], Iterable[T]],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        scores: Dict[Any, float] = {}

        for s in nodes:
            s_key = node_key(s)
            dist: Dict[Any, int] = {s_key: 0}
            q = deque([s])

            while q:
                curr = q.popleft()
                curr_dist = dist[node_key(curr)]
                for nbr in get_neighbors(curr):
                    nbr_key = node_key(nbr)
                    if nbr_key not in dist:
                        dist[nbr_key] = curr_dist + 1
                        q.append(nbr)

            harmonic = sum(
                1.0 / d for nbr_k, d in dist.items() if nbr_k != s_key and d > 0
            )
            scores[s_key] = round(harmonic, 4)

        return {
            "algorithm": "ALGO-KG-77",
            "harmonic_scores": scores,
        }

    def compute_harmonic_with_store(
        self,
        store: Any,
        node_ids: List[str],
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def store_neighbors(node_id: str) -> List[str]:
            return [n.id for n in store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")]

        return self.compute_harmonic_generic(
            nodes=node_ids,
            get_neighbors=store_neighbors,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_HARMONIC_CLOSENESS",
            "query": FLOW_GET_HARMONIC_CLOSENESS,
            "params": {
                "graph_name": graph_name,
            },
        }

    def compute_harmonic(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        return self.compute_harmonic_generic(
            nodes=nodes,
            get_neighbors=lambda u: adj.get(u, []),
            key_fn=lambda u: u,
        )
