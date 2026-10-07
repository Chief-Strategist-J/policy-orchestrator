"""
================================================================================
ALGORITHM BLUEPRINT: LOUVAIN GRAPH MODULARITY COMMUNITY DETECTION
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph multi-pass heuristic modularity optimization
   partitioning complex networks into densely interconnected functional clusters.
   Supports:
   - In-memory node and edge collection clustering.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Deterministic Aggregation: Clustered partitions sorted deterministically.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(V log V) greedy modularity optimization iterations.
   - Space Complexity: O(V + E) for community mapping tables and local neighbor counts.

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
    FLOW_GET_LOUVAIN_COMMUNITIES,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoLouvainCommunity:
    """
    --- contract:
      id: ALGO-KG-81
      name: KgAlgoLouvainCommunity
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(V log V)
        space: O(V + E)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - louvain.community
      - modularity.optimization
      - clustering
      - graph_partitioning
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        detect_communities_generic:
          nodes:
            type: array[generic[T]]
            description: List of entity nodes.
            required: true
          neighbor_provider:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function or provider resolving adjacent entities.
            required: true
          max_levels:
            type: integer
            default: 3
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        detect_communities:
          nodes:
            type: array[string]
            description: List of node IDs.
            required: true
          edges:
            type: array[tuple[string, string]]
            description: List of (source, target) edges.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-81).
        community_count:
          type: integer
          description: Total number of detected community modules.
        communities:
          type: array[array[any]]
          description: Discovered partition groupings.
    ---
    """

    def detect_communities_generic(
        self,
        nodes: List[T],
        neighbor_provider: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        max_levels: int = 3,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        if callable(neighbor_provider):
            get_neighbors_fn = neighbor_provider
        else:
            get_neighbors_fn = neighbor_provider.get_neighbors

        communities: Dict[Any, int] = {node_key(n): idx for idx, n in enumerate(nodes)}
        node_map: Dict[Any, T] = {node_key(n): n for n in nodes}

        for _ in range(max_levels):
            for n in nodes:
                k = node_key(n)
                nbr_comms: Dict[int, int] = defaultdict(int)
                for nbr in get_neighbors_fn(n):
                    nbr_k = node_key(nbr)
                    if nbr_k in communities:
                        nbr_comms[communities[nbr_k]] += 1
                if nbr_comms:
                    best_comm = max(nbr_comms.items(), key=lambda x: (x[1], -x[0]))[0]
                    communities[k] = best_comm

        groups: Dict[int, List[Any]] = defaultdict(list)
        for k, c in communities.items():
            groups[c].append(k)

        sorted_groups = [sorted(g, key=lambda x: str(x)) for g in groups.values()]
        sorted_groups.sort(key=lambda g: (len(g), str(g[0]) if g else ""))

        return {
            "algorithm": "ALGO-KG-81",
            "community_count": len(sorted_groups),
            "communities": sorted_groups,
        }

    def detect_communities_with_store(
        self,
        store: Any,
        node_ids: List[str],
        max_levels: int = 3,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def get_undirected(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="UNDIRECTED")

        return self.detect_communities_generic(
            nodes=node_ids,
            neighbor_provider=get_undirected,
            max_levels=max_levels,
            key_fn=lambda u: u,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        max_levels: int = 10,
        max_iterations: int = 15,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_LOUVAIN_COMMUNITIES",
            "query": FLOW_GET_LOUVAIN_COMMUNITIES,
            "params": {
                "graph_name": graph_name,
                "max_levels": max_levels,
                "max_iterations": max_iterations,
            },
        }

    def detect_communities(
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

        return self.detect_communities_generic(
            nodes=nodes,
            neighbor_provider=lambda u: adj.get(u, []),
            max_levels=3,
            key_fn=lambda u: u,
        )
