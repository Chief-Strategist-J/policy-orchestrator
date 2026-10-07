"""
================================================================================
ALGORITHM BLUEPRINT: 2-HOP COVER LABELING REACHABILITY INDEX
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph 2-hop hub cover reachability index resolver
   determining whether directed path exists from u to v via intersection of
   out-labels L_out(u) and in-labels L_in(v).
   Supports:
   - In-memory 2-hop label set intersection.
   - Generic entity types (T).
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions.
   - Reflexivity: Node is always trivially reachable to itself (u == v -> True).

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(|L_out(u)| + |L_in(v)|) set intersection.
   - Space Complexity: O(1) auxiliary lookup overhead.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

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

from ....queries.knowledge_graph.analytics.kg_reachability_queries import (
    FLOW_GET_TWO_HOP_REACHABILITY,
)



T = TypeVar("T")


class KgAlgoTwoHopLabeling:
    """
    --- contract:
      id: ALGO-KG-71
      name: KgAlgoTwoHopLabeling
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(|Lin| * |Lout|)
        space: O(1)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - two_hop_labeling
      - reachability.index
      - fast_query
      - hub_cover
      - vendor_agnostic
      input_schema:
        is_reachable_generic:
          l_out:
            type: dict[any, set[any]]
            description: Outgoing hub cover labels per entity key.
            required: true
          l_in:
            type: dict[any, set[any]]
            description: Incoming hub cover labels per entity key.
            required: true
          u:
            type: generic[T]
            description: Source entity node.
            required: true
          v:
            type: generic[T]
            description: Target entity node.
            required: true
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
        is_reachable:
          l_out:
            type: dict[string, set[string]]
            description: Outgoing hub cover sets.
            required: true
          l_in:
            type: dict[string, set[string]]
            description: Incoming hub cover sets.
            required: true
          u:
            type: string
            description: Source node ID.
            required: true
          v:
            type: string
            description: Target node ID.
            required: true
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-71).
        is_reachable:
          type: boolean
          description: Truth value indicating directed reachability from u to v.
    ---
    """

    def is_reachable_generic(
        self,
        l_out: Dict[Any, Set[Any]],
        l_in: Dict[Any, Set[Any]],
        u: T,
        v: T,
        key_fn: Optional[Callable[[T], Any]] = None,
    ) -> bool:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        u_key = node_key(u)
        v_key = node_key(v)

        if u_key == v_key:
            return True

        out_hubs = l_out.get(u_key, set())
        in_hubs = l_in.get(v_key, set())

        return bool(out_hubs.intersection(in_hubs))

    def is_reachable_with_store(
        self,
        store: Any,
        source_id: str,
        target_id: str,
    ) -> bool:
        if source_id == target_id:
            return True

        out_nbrs = set(store.find_neighbors(node_id=source_id, direction="OUTGOING"))
        in_nbrs = set(store.find_neighbors(node_id=target_id, direction="INCOMING"))

        if target_id in out_nbrs:
            return True

        return bool(out_nbrs.intersection(in_nbrs))

    def build_cypher_query(
        self,
        source_id: str,
        target_id: str,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_TWO_HOP_REACHABILITY",
            "query": FLOW_GET_TWO_HOP_REACHABILITY,
            "params": {
                "source_id": source_id,
                "target_id": target_id,
            },
        }

    def is_reachable(
        self,
        l_out: Dict[str, Set[str]],
        l_in: Dict[str, Set[str]],
        u: str,
        v: str,
    ) -> bool:
        return self.is_reachable_generic(
            l_out=l_out,
            l_in=l_in,
            u=u,
            v=v,
            key_fn=lambda x: x,
        )
