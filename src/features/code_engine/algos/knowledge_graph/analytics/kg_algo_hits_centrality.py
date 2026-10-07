"""
================================================================================
ALGORITHM BLUEPRINT: HITS (HUBS & AUTHORITIES) CENTRALITY ALGORITHM
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph mutually recursive prestige algorithm computing
   authority scores (value of content) and hub scores (value of links pointing to authorities).
   Supports:
   - In-memory edge list accumulation.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Normalization: L2 Euclidean norm applied across iterations to prevent score explosion.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Iterations * (V + E)) per normalization epoch.
   - Space Complexity: O(V) working tables for hub and authority scores.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import defaultdict
import math
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
    FLOW_GET_HITS_CENTRALITY,
)



T = TypeVar("T")


@runtime_checkable
class DirectedNeighborProvider(Protocol[T]):
    def get_outgoing_neighbors(self, node: T) -> Iterable[T]:
        ...

    def get_incoming_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoHitsCentrality:
    """
    --- contract:
      id: ALGO-KG-78
      name: KgAlgoHitsCentrality
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
      - hits.centrality
      - hubs_authorities
      - web_graph
      - link_analysis
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        compute_hits_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          get_outgoing:
            type: callable[[generic[T]], iterable[generic[T]]]
            description: Function yielding outbound successor nodes.
            required: true
          get_incoming:
            type: callable[[generic[T]], iterable[generic[T]]]
            description: Function yielding inbound predecessor nodes.
            required: true
          iterations:
            type: integer
            default: 15
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        compute_hits:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) directed edges.
            required: true
          iterations:
            type: integer
            default: 15
            required: false
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-78).
        hubs:
          type: dict[any, float]
          description: Normalized hub prestige ratings per entity.
        authorities:
          type: dict[any, float]
          description: Normalized authority quality ratings per entity.
    ---
    """

    def compute_hits_generic(
        self,
        nodes: List[T],
        get_outgoing: Callable[[T], Iterable[T]],
        get_incoming: Callable[[T], Iterable[T]],
        iterations: int = 15,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        hubs: Dict[Any, float] = {node_key(n): 1.0 for n in nodes}
        auth: Dict[Any, float] = {node_key(n): 1.0 for n in nodes}

        in_map: Dict[Any, List[Any]] = {}
        out_map: Dict[Any, List[Any]] = {}
        for n in nodes:
            k = node_key(n)
            in_map[k] = [node_key(src) for src in get_incoming(n)]
            out_map[k] = [node_key(tgt) for tgt in get_outgoing(n)]

        for _ in range(iterations):
            for n in nodes:
                k = node_key(n)
                auth[k] = sum(hubs.get(src, 0.0) for src in in_map[k])
            norm_a = math.sqrt(sum(a * a for a in auth.values())) or 1.0
            for k in auth:
                auth[k] /= norm_a

            for n in nodes:
                k = node_key(n)
                hubs[k] = sum(auth.get(tgt, 0.0) for tgt in out_map[k])
            norm_h = math.sqrt(sum(h * h for h in hubs.values())) or 1.0
            for k in hubs:
                hubs[k] /= norm_h

        return {
            "algorithm": "ALGO-KG-78",
            "hubs": {k: round(v, 4) for k, v in hubs.items()},
            "authorities": {k: round(v, 4) for k, v in auth.items()},
        }

    def compute_hits_with_store(
        self,
        store: Any,
        node_ids: List[str],
        rel_type: Optional[str] = None,
        iterations: int = 15,
    ) -> Dict[str, Any]:
        def get_out(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")

        def get_in(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="INCOMING")

        return self.compute_hits_generic(
            nodes=node_ids,
            get_outgoing=get_out,
            get_incoming=get_in,
            iterations=iterations,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        iterations: int = 15,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_HITS_CENTRALITY",
            "query": FLOW_GET_HITS_CENTRALITY,
            "params": {
                "graph_name": graph_name,
                "iterations": iterations,
            },
        }

    def compute_hits(
        self,
        nodes: List[str],
        edges: List[Tuple[str, str]],
        iterations: int = 15,
    ) -> Dict[str, Any]:
        out_adj = defaultdict(list)
        in_adj = defaultdict(list)
        for u, v in edges:
            out_adj[u].append(v)
            in_adj[v].append(u)

        return self.compute_hits_generic(
            nodes=nodes,
            get_outgoing=lambda u: out_adj[u],
            get_incoming=lambda u: in_adj[u],
            iterations=iterations,
            key_fn=lambda u: u,
        )
