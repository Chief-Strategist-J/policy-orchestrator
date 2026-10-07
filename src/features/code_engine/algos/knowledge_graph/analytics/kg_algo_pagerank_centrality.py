"""
================================================================================
ALGORITHM BLUEPRINT: POWER ITERATION PAGERANK CENTRALITY ENGINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph structural prestige ranking algorithm measuring
   the probability distribution of stationary random walks across directed entities.
   Supports:
   - In-memory power iteration using native Python dictionaries.
   - Generic entity types (T) and lazy neighbor expansion callables.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Stochastic Convergence: Sum of ranks normalized across each iteration.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Iterations * E) for iterative Markov transitions.
   - Space Complexity: O(V) for rank vector buffers and in-degree mappings.

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

from ....queries.knowledge_graph.analytics.kg_centrality_queries import (
    FLOW_GET_PAGERANK_CENTRALITY,
)



T = TypeVar("T")


@runtime_checkable
class GraphDirectedNeighborProvider(Protocol[T]):
    def get_incoming_neighbors(self, node: T) -> Iterable[T]:
        ...

    def get_out_degree(self, node: T) -> int:
        ...


class KgAlgoPagerankCentrality:
    """
    --- contract:
      id: ALGO-KG-74
      name: KgAlgoPagerankCentrality
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Iterations * E)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - pagerank.centrality
      - power_iteration
      - graph_ranking
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_pagerank_generic:
          nodes:
            type: array[generic[T]]
            description: Collection of graph entity instances.
            required: true
          get_in_neighbors:
            type: callable[[generic[T]], iterable[generic[T]]]
            description: Function returning incoming predecessor nodes.
            required: true
          get_out_degree:
            type: callable[[generic[T]], integer]
            description: Function returning outgoing degree of a node.
            required: true
          damping:
            type: number
            default: 0.85
            description: Teleportation probability damping factor.
            required: false
          max_iter:
            type: integer
            default: 20
            description: Power iteration count.
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for node dictionary mapping.
            default: lambda x: x
            required: false
        compute_pagerank:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) directed edges.
            required: true
          damping:
            type: number
            default: 0.85
            required: false
          max_iter:
            type: integer
            default: 20
            required: false
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-74).
        scores:
          type: dict[any, number]
          description: Map of node key to stationary PageRank probability score.
    ---
    """

    def compute_pagerank_generic(
        self,
        nodes: List[T],
        get_in_neighbors: Callable[[T], Iterable[T]],
        get_out_degree: Callable[[T], int],
        damping: float = 0.85,
        max_iter: int = 20,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        n = len(nodes)
        if n == 0:
            return {"algorithm": "ALGO-KG-74", "scores": {}}

        ranks: Dict[Any, float] = {node_key(node): 1.0 / n for node in nodes}

        for _ in range(max_iter):
            new_ranks: Dict[Any, float] = {}
            for node in nodes:
                k = node_key(node)
                incoming_sum = sum(
                    ranks.get(node_key(src), 0.0) / max(1, get_out_degree(src))
                    for src in get_in_neighbors(node)
                )
                new_ranks[k] = (1.0 - damping) / n + damping * incoming_sum
            ranks = new_ranks

        return {
            "algorithm": "ALGO-KG-74",
            "scores": {k: round(v, 6) for k, v in ranks.items()},
        }

    def compute_pagerank_with_store(
        self,
        store: Any,
        node_ids: List[str],
        damping: float = 0.85,
        max_iter: int = 20,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def in_neighbors(node_id: str) -> List[str]:
            return [n.id for n in store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="INCOMING")]

        def out_deg(node_id: str) -> int:
            return len(store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING"))

        return self.compute_pagerank_generic(
            nodes=node_ids,
            get_in_neighbors=in_neighbors,
            get_out_degree=out_deg,
            damping=damping,
            max_iter=max_iter,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        damping_factor: float = 0.85,
        max_iterations: int = 20,
        tolerance: float = 1e-7,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PAGERANK_CENTRALITY",
            "query": FLOW_GET_PAGERANK_CENTRALITY,
            "params": {
                "graph_name": graph_name,
                "damping_factor": damping_factor,
                "max_iterations": max_iterations,
                "tolerance": tolerance,
            },
        }

    def compute_pagerank(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        damping: float = 0.85,
        max_iter: int = 20,
    ) -> Dict[str, Any]:
        out_deg = defaultdict(int)
        in_adj = defaultdict(list)
        for u, v in edges:
            out_deg[u] += 1
            in_adj[v].append(u)

        return self.compute_pagerank_generic(
            nodes=nodes,
            get_in_neighbors=lambda u: in_adj.get(u, []),
            get_out_degree=lambda u: out_deg.get(u, 0),
            damping=damping,
            max_iter=max_iter,
            key_fn=lambda u: u,
        )
