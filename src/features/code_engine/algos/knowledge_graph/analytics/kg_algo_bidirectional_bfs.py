"""
================================================================================
ALGORITHM BLUEPRINT: BIDIRECTIONAL BFS SHORTEST PATH FINDER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph bidirectional breadth-first search finding minimal
   unweighted hop distances between source and target by expanding simultaneous
   forward and backward search frontiers.
   Supports:
   - In-memory execution with native Python adjacency maps.
   - Generic entity types (T) and lazy forward/reverse neighbor generators.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Frontier Collision Guarantee: Halts upon first overlap between forward and reverse frontiers.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(b^(d/2)) where b is average branching factor and d is path distance.
   - Space Complexity: O(b^(d/2)) for dual frontier queues and distance tracking sets.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

from collections import deque
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

from ....queries.knowledge_graph.analytics.kg_traversal_queries import (
    FLOW_GET_BIDIRECTIONAL_BFS_PATH,
    FLOW_GET_PROCEDURE_BIDIRECTIONAL_BFS_PATH,
    FLOW_GET_PROJECTED_BIDIRECTIONAL_BFS_PATH,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoBidirectionalBfs:
    """
    --- contract:
      id: ALGO-KG-65
      name: KgAlgoBidirectionalBfs
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(b^(d/2))
        space: O(b^(d/2))
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - bidirectional_bfs
      - shortest_path
      - frontier.collision
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        find_shortest_path_generic:
          source:
            type: generic[T]
            description: Start source entity instance.
            required: true
          target:
            type: generic[T]
            description: Destination target entity instance.
            required: true
          get_forward_neighbors:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function yielding outgoing adjacent nodes.
            required: true
          get_reverse_neighbors:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function yielding incoming adjacent nodes.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            description: Hashable key extractor for node comparison.
            default: lambda x: x
            required: false
        find_shortest_path:
          fwd:
            type: dict[str, list[str]]
            description: Forward adjacency mapping.
            required: true
          rev:
            type: dict[str, list[str]]
            description: Reverse adjacency mapping.
            required: true
          source:
            type: string
            description: Source node ID.
            required: true
          target:
            type: string
            description: Target node ID.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-65).
        path_found:
          type: boolean
          description: True if a path connects source to target, False otherwise.
        distance:
          type: integer
          description: Minimum hop distance (-1 if unreachable).
        meeting_node:
          type: any
          description: Node entity where forward and backward frontiers intersected.
    ---
    """

    def find_shortest_path_generic(
        self,
        source: T,
        target: T,
        get_forward_neighbors: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        get_reverse_neighbors: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)

        if callable(get_forward_neighbors):
            fwd_fn = get_forward_neighbors
        else:
            fwd_fn = get_forward_neighbors.get_neighbors

        if callable(get_reverse_neighbors):
            rev_fn = get_reverse_neighbors
        else:
            rev_fn = get_reverse_neighbors.get_neighbors

        source_key = node_key(source)
        target_key = node_key(target)

        if source_key == target_key:
            return {
                "algorithm": "ALGO-KG-65",
                "path_found": True,
                "distance": 0,
                "meeting_node": source,
            }

        q_src, q_tgt = deque([source]), deque([target])
        dist_src: Dict[Any, int] = {source_key: 0}
        dist_tgt: Dict[Any, int] = {target_key: 0}

        while q_src and q_tgt:
            curr_s = q_src.popleft()
            curr_s_key = node_key(curr_s)
            for nbr in fwd_fn(curr_s):
                nbr_key = node_key(nbr)
                if nbr_key in dist_tgt:
                    return {
                        "algorithm": "ALGO-KG-65",
                        "path_found": True,
                        "distance": dist_src[curr_s_key] + 1 + dist_tgt[nbr_key],
                        "meeting_node": nbr,
                    }
                if nbr_key not in dist_src:
                    dist_src[nbr_key] = dist_src[curr_s_key] + 1
                    q_src.append(nbr)

            curr_t = q_tgt.popleft()
            curr_t_key = node_key(curr_t)
            for nbr in rev_fn(curr_t):
                nbr_key = node_key(nbr)
                if nbr_key in dist_src:
                    return {
                        "algorithm": "ALGO-KG-65",
                        "path_found": True,
                        "distance": dist_src[nbr_key] + 1 + dist_tgt[curr_t_key],
                        "meeting_node": nbr,
                    }
                if nbr_key not in dist_tgt:
                    dist_tgt[nbr_key] = dist_tgt[curr_t_key] + 1
                    q_tgt.append(nbr)

        return {
            "algorithm": "ALGO-KG-65",
            "path_found": False,
            "distance": -1,
            "meeting_node": None,
        }

    def find_shortest_path_with_store(
        self,
        store: Any,
        source: str,
        target: str,
        rel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        def fwd_neighbors(node_id: str) -> List[str]:
            return [n.id for n in store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")]

        def rev_neighbors(node_id: str) -> List[str]:
            return [n.id for n in store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="INCOMING")]

        return self.find_shortest_path_generic(
            source=source,
            target=target,
            get_forward_neighbors=fwd_neighbors,
            get_reverse_neighbors=rev_neighbors,
            key_fn=lambda u: u,
        )

    def build_procedure_query(
        self,
        source_id: str,
        target_id: str,
        rel_type: str = "CONNECTED_TO",
        weight_prop: str = "weight",
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROCEDURE_BIDIRECTIONAL_BFS_PATH",
            "query": FLOW_GET_PROCEDURE_BIDIRECTIONAL_BFS_PATH,
            "params": {
                "source_id": source_id,
                "target_id": target_id,
                "rel_type": rel_type,
                "weight_prop": weight_prop,
            },
        }

    def build_projected_graph_query(
        self,
        graph_name: str,
        source_id: str,
        target_id: str,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_PROJECTED_BIDIRECTIONAL_BFS_PATH",
            "query": FLOW_GET_PROJECTED_BIDIRECTIONAL_BFS_PATH,
            "params": {
                "graph_name": graph_name,
                "source_id": source_id,
                "target_id": target_id,
            },
        }

    def build_cypher_query(
        self,
        source_id: str,
        target_id: str,
        rel_type: str = "CONNECTED_TO",
        weight_prop: str = "weight",
    ) -> Dict[str, Any]:
        return self.build_procedure_query(
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            weight_prop=weight_prop,
        )

    def find_shortest_path(
        self,
        fwd: Dict[str, List[str]],
        rev: Dict[str, List[str]],
        source: str,
        target: str,
    ) -> Dict[str, Any]:
        return self.find_shortest_path_generic(
            source=source,
            target=target,
            get_forward_neighbors=lambda u: fwd.get(u, []),
            get_reverse_neighbors=lambda u: rev.get(u, []),
            key_fn=lambda u: u,
        )
