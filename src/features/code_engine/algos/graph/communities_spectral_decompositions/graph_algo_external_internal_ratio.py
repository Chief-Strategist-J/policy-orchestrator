"""
ALGORITHM & ARCHITECTURE BLUEPRINT: External-Internal (E-I) Index and Community Metrics (ALGO-GRAPH-COMM-167)

1. OVERVIEW & OBJECTIVE:
Computes Krackhardt's External-Internal (E-I) Index, internal edge densities, external edge
densities, and boundary ratio statistics for graph partitions and communities, measuring
group cohesion vs homophily/heterophily.

2. COMPLEXITY & INVARIANTS:
- Space Complexity: O(|V| + |E|) storage for partition sets and edge tallies.
- Time Complexity: O(|E|) single edge-traversal pass.
- Invariants:
  - Krackhardt E-I index = (E - I) / (E + I), where E is external edge count and I is internal edge count.
  - Value ranges from -1.0 (pure internal/cohesive) to +1.0 (pure external/heterophilous).

3. INPUT PARAMETERS:
- `adjacency` (Mapping[TNode, Iterable[TNode]]): Adjacency list representation.
- `partition` (Mapping[TNode, int]): Community or group assignment per vertex.

4. OUTPUT PARAMETERS:
- `GlobalEIResult`: Overall graph-level E-I index, total internal edges, total external edges.
- `Dict[int, CommunityEIMetrics]`: Per-community internal/external metrics.

5. AGENT CONTRACT:
- Role: Social network cohesion and community boundary structure analyst.
- Rules: Support arbitrary community IDs.
- Guardrails: If E + I == 0, returns E-I index of 0.0.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Generic, Hashable, Iterable, Mapping, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


@dataclass(frozen=True)
class CommunityEIMetrics:
    """
    E-I metrics for an individual community.
    """
    community_id: int
    size: int
    internal_edges: int
    external_edges: int
    ei_index: float
    internal_density: float


@dataclass(frozen=True)
class GlobalEIMetrics:
    """
    Global aggregate E-I index and community breakdowns.
    """
    global_ei_index: float
    total_internal_edges: int
    total_external_edges: int
    community_metrics: Dict[int, CommunityEIMetrics]


class ExternalInternalIndexEvaluator(Generic[TNode]):
    """
    Computes Krackhardt E-I index and community boundary density metrics.

    ```yaml
    contract_id: ALGO-GRAPH-COMM-167
    inputs:
      adjacency: Mapping[TNode, Iterable[TNode]]
      partition: Mapping[TNode, int]
    outputs:
      metrics: GlobalEIMetrics
    parameters: {}
    capability_tags:
      - graph
      - community_metrics
      - krackhardt_ei
      - cohesion
      - homophily
    purity: pure
    determinism: deterministic
    idempotency: idempotent
    complexity:
      time: O(|E|)
      space: O(|V| + |E|)
    ```
    """

    def evaluate(
        self,
        adjacency: Mapping[TNode, Iterable[TNode]],
        partition: Mapping[TNode, int],
    ) -> GlobalEIMetrics:
        """
        Calculates group and global E-I indices.

        Args:
            adjacency: Graph adjacency map.
            partition: Mapping from node to group/community ID.

        Returns:
            GlobalEIMetrics with overall and per-community metrics.
        """
        comm_nodes: Dict[int, Set[TNode]] = defaultdict(set)
        for node, c_id in partition.items():
            comm_nodes[c_id].add(node)

        internal_counts: Dict[int, int] = defaultdict(int)
        external_counts: Dict[int, int] = defaultdict(int)

        seen_edges: Set[Tuple[TNode, TNode]] = set()
        total_internal = 0
        total_external = 0

        for u, neighbors in adjacency.items():
            if u not in partition:
                continue
            c_u = partition[u]
            for v in neighbors:
                if v not in partition:
                    continue
                c_v = partition[v]
                edge = (min(u, v, key=lambda x: str(x)), max(u, v, key=lambda x: str(x)))
                if edge in seen_edges:
                    continue
                seen_edges.add(edge)

                if c_u == c_v:
                    internal_counts[c_u] += 1
                    total_internal += 1
                else:
                    external_counts[c_u] += 1
                    external_counts[c_v] += 1
                    total_external += 1

        total_edges = total_internal + total_external
        global_ei = (total_external - total_internal) / total_edges if total_edges > 0 else 0.0

        comm_metrics: Dict[int, CommunityEIMetrics] = {}
        for c_id, nodes in comm_nodes.items():
            i_cnt = internal_counts[c_id]
            e_cnt = external_counts[c_id]
            c_tot = i_cnt + e_cnt
            ei = (e_cnt - i_cnt) / c_tot if c_tot > 0 else 0.0
            n = len(nodes)
            max_internal = n * (n - 1) // 2
            density = (i_cnt / max_internal) if max_internal > 0 else 0.0

            comm_metrics[c_id] = CommunityEIMetrics(
                community_id=c_id,
                size=n,
                internal_edges=i_cnt,
                external_edges=e_cnt,
                ei_index=ei,
                internal_density=density,
            )

        return GlobalEIMetrics(
            global_ei_index=global_ei,
            total_internal_edges=total_internal,
            total_external_edges=total_external,
            community_metrics=comm_metrics,
        )
