"""
================================================================================
ALGORITHM BLUEPRINT: IN/OUT DEGREE CENTRALITY METRIC GENERATOR
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph structural degree connectivity algorithm computing
   exact inbound and outbound degree prestige indices across directed entities.
   Supports:
   - In-memory degree accumulation.
   - Generic entity types (T) and lazy degree calculation callables.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Complete Vertex Inclusion: Every node present in input collection initialized to 0.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V + E) linear scan over nodes and directed incident edges.
   - Space Complexity: O(V) for in-degree and out-degree accumulator tables.

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
    FLOW_GET_DEGREE_CENTRALITY,
)



T = TypeVar("T")


class KgAlgoDegreeCentrality:
    """
    --- contract:
      id: ALGO-KG-73
      name: KgAlgoDegreeCentrality
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
      - degree_centrality
      - graph_metrics
      - hub_analysis
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_centrality_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          get_in_degree:
            type: callable[[generic[T]], integer]
            description: Function returning in-degree count for a node.
            required: true
          get_out_degree:
            type: callable[[generic[T]], integer]
            description: Function returning out-degree count for a node.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for node dictionary mapping.
            default: lambda x: x
            required: false
        compute_centrality:
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
          description: Canonical algorithm registry identifier (ALGO-KG-73).
        in_degrees:
          type: dict[any, integer]
          description: Inbound edge counts per node.
        out_degrees:
          type: dict[any, integer]
          description: Outbound edge counts per node.
    ---
    """

    def compute_centrality_generic(
        self,
        nodes: List[T],
        get_in_degree: Callable[[T], int],
        get_out_degree: Callable[[T], int],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        in_deg: Dict[Any, int] = {}
        out_deg: Dict[Any, int] = {}

        for n in nodes:
            k = node_key(n)
            in_deg[k] = int(get_in_degree(n))
            out_deg[k] = int(get_out_degree(n))

        return {
            "algorithm": "ALGO-KG-73",
            "in_degrees": in_deg,
            "out_degrees": out_deg,
        }

    def compute_centrality_with_store(
        self,
        store: Any,
        node_ids: List[str],
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def in_deg(node_id: str) -> int:
            return len(store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="INCOMING"))

        def out_deg(node_id: str) -> int:
            return len(store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING"))

        return self.compute_centrality_generic(
            nodes=node_ids,
            get_in_degree=in_deg,
            get_out_degree=out_deg,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        orientation: str = "NATURAL",
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_DEGREE_CENTRALITY",
            "query": FLOW_GET_DEGREE_CENTRALITY,
            "params": {
                "graph_name": graph_name,
                "orientation": orientation,
            },
        }

    def compute_centrality(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
    ) -> Dict[str, Any]:
        in_deg = defaultdict(int)
        out_deg = defaultdict(int)
        for n in nodes:
            in_deg[n] = 0
            out_deg[n] = 0
        for u, v in edges:
            out_deg[u] += 1
            in_deg[v] += 1

        return self.compute_centrality_generic(
            nodes=nodes,
            get_in_degree=lambda u: in_deg[u],
            get_out_degree=lambda u: out_deg[u],
            key_fn=lambda u: u,
        )
