"""
================================================================================
ALGORITHM BLUEPRINT: BRANDES FAST BETWEENNESS CENTRALITY ALGORITHM
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph structural bottleneck identification algorithm
   computing Brandes betweenness centrality by accumulating shortest path pair-
   dependencies across all graph vertices.
   Supports:
   - In-memory accumulation using BFS traversal stacks and path-count buffers.
   - Generic entity types (T) and lazy neighbor expansion callables.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Undirected Normalization: Scores normalized by 2.0 factor for undirected graphs.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V * E) for unweighted graphs via single-source BFS passes.
   - Space Complexity: O(V + E) for predecessor lists and pair-dependency tracking.

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
    FLOW_GET_BETWEENNESS_CENTRALITY,
)



T = TypeVar("T")


class KgAlgoBrandesBetweenness:
    """
    --- contract:
      id: ALGO-KG-76
      name: KgAlgoBrandesBetweenness
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V * E)
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - brandes.betweenness
      - shortest_path.accumulation
      - bottleneck.detection
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_betweenness_generic:
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
        compute_betweenness:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of undirected graph edges.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-76).
        betweenness:
          type: dict[any, number]
          description: Normalized betweenness centrality scores per node.
    ---
    """

    def compute_betweenness_generic(
        self,
        nodes: List[T],
        get_neighbors: Callable[[T], Iterable[T]],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        node_map: Dict[Any, T] = {node_key(n): n for n in nodes}
        cb: Dict[Any, float] = {node_key(n): 0.0 for n in nodes}

        for s in nodes:
            s_key = node_key(s)
            stack: List[T] = []
            pred: Dict[Any, List[T]] = {node_key(w): [] for w in nodes}
            sigma: Dict[Any, int] = {node_key(w): 0 for w in nodes}
            dist: Dict[Any, int] = {node_key(w): -1 for w in nodes}

            sigma[s_key] = 1
            dist[s_key] = 0
            q = deque([s])

            while q:
                v = q.popleft()
                v_key = node_key(v)
                stack.append(v)

                for w in get_neighbors(v):
                    w_key = node_key(w)
                    if w_key not in dist:
                        dist[w_key] = -1
                        sigma[w_key] = 0
                        pred[w_key] = []

                    if dist[w_key] < 0:
                        dist[w_key] = dist[v_key] + 1
                        q.append(w)
                    if dist[w_key] == dist[v_key] + 1:
                        sigma[w_key] += sigma[v_key]
                        pred[w_key].append(v)

            delta: Dict[Any, float] = {node_key(w): 0.0 for w in nodes}
            while stack:
                w = stack.pop()
                w_key = node_key(w)
                for v in pred[w_key]:
                    v_key = node_key(v)
                    delta[v_key] += (sigma[v_key] / max(1, sigma[w_key])) * (1.0 + delta[w_key])
                if w_key != s_key:
                    cb[w_key] += delta[w_key]

        return {
            "algorithm": "ALGO-KG-76",
            "betweenness": {k: round(v / 2.0, 4) for k, v in cb.items()},
        }

    def compute_betweenness_with_store(
        self,
        store: Any,
        node_ids: List[str],
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def store_neighbors(node_id: str) -> List[str]:
            return [n.id for n in store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")]

        return self.compute_betweenness_generic(
            nodes=node_ids,
            get_neighbors=store_neighbors,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_BETWEENNESS_CENTRALITY",
            "query": FLOW_GET_BETWEENNESS_CENTRALITY,
            "params": {
                "graph_name": graph_name,
            },
        }

    def compute_betweenness(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        return self.compute_betweenness_generic(
            nodes=nodes,
            get_neighbors=lambda u: adj.get(u, []),
            key_fn=lambda u: u,
        )
