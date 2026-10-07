"""
================================================================================
ALGORITHM BLUEPRINT: RANDOM WALK WITH RESTART (RWR) NODE PROXIMITY
================================================================================

1. OVERVIEW & OBJECTIVE:
   Standardized Knowledge Graph stochastic walk simulation computing relative
   topological proximity and affinity scores relative to a designated seed node.
   Supports:
   - In-memory adjacency simulation.
   - Generic entity types (T) and lazy neighbor expansion providers.
   - Database integration via GraphStorePort.
   - Database pushdown parameterized query plan generation.

2. OPERATIONAL INVARIANTS & CONSTRAINTS:
   - Standalone & Self-Contained: Zero required background services or Docker setup.
   - Zero Inline Comments: Self-documenting pure methods per architectural doctrine.
   - Purity & Determinism: Pure functional state transitions with optional seed control.
   - Boundary Handling: Immediate restart upon encountering sink nodes.

3. COMPLEXITY ANALYSIS:
   - Time Complexity: O(Walk_Length) stochastic step state transitions.
   - Space Complexity: O(V) visit frequency accumulation table.

4. ZERO-INLINE-COMMENT DOCTRINE:
   - Zero inline comments inside method bodies.
================================================================================
"""

import random
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

from ....queries.knowledge_graph.analytics.kg_reachability_queries import (
    FLOW_GET_RANDOM_WALK_RESTART,
)



T = TypeVar("T")


@runtime_checkable
class GraphNeighborProvider(Protocol[T]):
    def get_neighbors(self, node: T) -> Iterable[T]:
        ...


class KgAlgoRandomWalkRestart:
    """
    --- contract:
      id: ALGO-KG-69
      name: KgAlgoRandomWalkRestart
      version: 2.0.0
      category: knowledge_graph
      complexity:
        time: O(Walk_Length)
        space: O(V)
      pure_function: true
      zero_inline_comments: true
      standalone_runtime: true
      external_dependencies: none
      capability_tags:
      - random_walk_restart
      - node_proximity
      - graph_sampling
      - stochastic_ranking
      - vendor_agnostic
      - lazy_expansion
      input_schema:
        run_walk_generic:
          start_node:
            type: generic[T]
            description: Initial seed entity for random walk.
            required: true
          neighbor_provider:
            type: union[callable[[generic[T]], iterable[generic[T]]], GraphNeighborProvider[generic[T]]]
            description: Function or provider yielding successor entities.
            required: true
          num_steps:
            type: integer
            default: 500
            required: false
          restart_prob:
            type: number
            default: 0.15
            required: false
          top_k:
            type: integer
            default: 10
            required: false
          key_fn:
            type: callable[[generic[T]], any]
            default: lambda x: x
            required: false
          seed:
            type: integer
            required: false
        run_walk:
          adj:
            type: dict[string, array[string]]
            description: Adjacency dictionary mapping node to its neighbors.
            required: true
          start_node:
            type: string
            description: Seed start node identifier.
            required: true
          num_steps:
            type: integer
            default: 500
            required: false
          restart_prob:
            type: number
            default: 0.15
            required: false
      output_schema:
        algorithm:
          type: string
          description: Canonical algorithm registry identifier (ALGO-KG-69).
        visit_frequencies:
          type: dict[any, float]
          description: Top relative visit probability frequencies.
    ---
    """

    def run_walk_generic(
        self,
        start_node: T,
        neighbor_provider: Union[Callable[[T], Iterable[T]], GraphNeighborProvider[T]],
        num_steps: int = 500,
        restart_prob: float = 0.15,
        top_k: int = 10,
        key_fn: Optional[Callable[[T], Any]] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        node_key = key_fn if key_fn is not None else (lambda x: x)
        if callable(neighbor_provider):
            get_neighbors_fn = neighbor_provider
        else:
            get_neighbors_fn = neighbor_provider.get_neighbors

        rng = random.Random(seed) if seed is not None else random.Random()
        counts: Dict[Any, int] = defaultdict(int)
        curr: T = start_node

        for _ in range(num_steps):
            k = node_key(curr)
            counts[k] += 1
            if rng.random() < restart_prob:
                curr = start_node
            else:
                nbrs = list(get_neighbors_fn(curr))
                if not nbrs:
                    curr = start_node
                else:
                    curr = rng.choice(nbrs)

        total = sum(counts.values()) or 1
        sorted_counts = sorted(counts.items(), key=lambda x: (x[1], str(x[0])), reverse=True)
        top_entries = sorted_counts[:top_k] if top_k > 0 else sorted_counts

        return {
            "algorithm": "ALGO-KG-69",
            "visit_frequencies": {k: round(v / total, 4) for k, v in top_entries},
        }

    def run_walk_with_store(
        self,
        store: Any,
        start_node_id: str,
        num_steps: int = 500,
        restart_prob: float = 0.15,
        top_k: int = 10,
        rel_type: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        def get_out(node_id: str) -> List[str]:
            return store.find_neighbors(node_id=node_id, rel_type=rel_type, direction="OUTGOING")

        return self.run_walk_generic(
            start_node=start_node_id,
            neighbor_provider=get_out,
            num_steps=num_steps,
            restart_prob=restart_prob,
            top_k=top_k,
            key_fn=lambda u: u,
            seed=seed,
        )

    def build_cypher_query(
        self,
        graph_name: str,
        start_node: str,
        walk_length: int = 500,
        walks_per_node: int = 1,
        restart_probability: float = 0.15,
    ) -> Dict[str, Any]:
        return {
            "query_name": "FLOW_GET_RANDOM_WALK_RESTART",
            "query": FLOW_GET_RANDOM_WALK_RESTART,
            "params": {
                "graph_name": graph_name,
                "start_node": start_node,
                "walk_length": walk_length,
                "walks_per_node": walks_per_node,
                "restart_probability": restart_probability,
            },
        }

    def run_walk(
        self,
        adj: Dict[str, List[str]],
        start_node: str,
        num_steps: int = 500,
        restart_prob: float = 0.15,
    ) -> Dict[str, Any]:
        return self.run_walk_generic(
            start_node=start_node,
            neighbor_provider=lambda u: adj.get(u, []),
            num_steps=num_steps,
            restart_prob=restart_prob,
            top_k=10,
            key_fn=lambda u: u,
        )
