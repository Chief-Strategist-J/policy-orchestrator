"""
================================================================================
ALGORITHM BLUEPRINT: PERSONALIZED PAGERANK (PPR) TELEPORTATION ENGINE
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph topic-sensitive structural relevance algorithm
   biasing random walk teleportation toward a targeted set of seed source entities.
   Supports:
   - In-memory power iteration with seed-biased jump vectors.
   - Generic entity types (T) and lazy neighbor expansion callables.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Non-Empty Seed Validation: Returns empty score map if seed set is empty.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Iterations * E) for iterative Markov transitions.
   - Space Complexity: O(V) for rank distributions and in-degree maps.

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
    FLOW_GET_PERSONALIZED_PAGERANK,
)



T = TypeVar("T")


class KgAlgoPersonalizedPagerank:
    """
    --- contract:
      id: ALGO-KG-75
      name: KgAlgoPersonalizedPagerank
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
      - personalized_pagerank
      - topic_sensitive
      - graph_relevance
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_ppr_generic:
          nodes:
            type: array[generic[T]]
            description: Collection of graph entity instances.
            required: true
          seed_nodes:
            type: array[generic[T]]
            description: Priority seed entity subset where random walks restart.
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
            required: false
          max_iter:
            type: integer
            default: 20
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for node dictionary mapping.
            default: lambda x: x
            required: false
        compute_ppr:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) directed edges.
            required: true
          seed_nodes:
            type: array[string]
            description: List of seed node IDs.
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
          description: Canonical algorithm registry identifier (ALGO-KG-75).
        ppr_scores:
          type: dict[any, number]
          description: Map of node key to personalized relevance score.
    ---
    """

    def compute_ppr_generic(
        self,
        nodes: List[T],
        seed_nodes: List[T],
        get_in_neighbors: Callable[[T], Iterable[T]],
        get_out_degree: Callable[[T], int],
        damping: float = 0.85,
        max_iter: int = 20,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        n = len(nodes)
        if n == 0 or not seed_nodes:
            return {"algorithm": "ALGO-KG-75", "ppr_scores": {}}

        seed_keys = {node_key(s) for s in seed_nodes}
        num_seeds = len(seed_keys)
        ranks: Dict[Any, float] = {
            node_key(node): (1.0 / num_seeds if node_key(node) in seed_keys else 0.0)
            for node in nodes
        }

        for _ in range(max_iter):
            new_ranks: Dict[Any, float] = {}
            for node in nodes:
                k = node_key(node)
                base = ((1.0 - damping) / num_seeds) if k in seed_keys else 0.0
                incoming = sum(
                    ranks.get(node_key(src), 0.0) / max(1, get_out_degree(src))
                    for src in get_in_neighbors(node)
                )
                new_ranks[k] = base + damping * incoming
            ranks = new_ranks

        return {
            "algorithm": "ALGO-KG-75",
            "ppr_scores": {k: round(v, 6) for k, v in ranks.items()},
        }

    def compute_ppr_with_store(
        self,
        store: Any,
        node_ids: List[str],
        seed_node_ids: List[str],
        damping: float = 0.85,
        max_iter: int = 20,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def in_neighbors(node_id: str) -> List[str]:
            return [n.id for n in store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="INCOMING")]

        def out_deg(node_id: str) -> int:
            return len(store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING"))

        return self.compute_ppr_generic(
            nodes=node_ids,
            seed_nodes=seed_node_ids,
            get_in_neighbors=in_neighbors,
            get_out_degree=out_deg,
            damping=damping,
            max_iter=max_iter,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        seed_node: str,
        damping_factor: float = 0.85,
        max_iterations: int = 20,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PERSONALIZED_PAGERANK",
            "query": FLOW_GET_PERSONALIZED_PAGERANK,
            "params": {
                "graph_name": graph_name,
                "seed_node": seed_node,
                "damping_factor": damping_factor,
                "max_iterations": max_iterations,
            },
        }

    def compute_ppr(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        seed_nodes: List[str],
        damping: float = 0.85,
        max_iter: int = 20,
    ) -> Dict[str, Any]:
        out_deg = defaultdict(int)
        in_adj = defaultdict(list)
        for u, v in edges:
            out_deg[u] += 1
            in_adj[v].append(u)

        return self.compute_ppr_generic(
            nodes=nodes,
            seed_nodes=seed_nodes,
            get_in_neighbors=lambda u: in_adj.get(u, []),
            get_out_degree=lambda u: out_deg.get(u, 0),
            damping=damping,
            max_iter=max_iter,
            key_fn=lambda u: u,
        )
