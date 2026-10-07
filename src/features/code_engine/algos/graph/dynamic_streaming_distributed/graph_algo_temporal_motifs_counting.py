"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: DELTA-TEMPORAL MOTIFS COUNTING (ALGO-GRAPH-TEMP-213)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Delta-Temporal Motifs Counting Engine (Paranjape et al. framework).
   Enumerates small ordered subgraph interaction patterns (2-node ping-pongs,
   3-node feedforward loops, transitive chains) occurring strictly within a maximum
   delta time window over timestamped edge streams.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M * d_avg) for 2-edge and 3-edge motifs.
   - Space Complexity: O(M) timestamped buffer and indexed neighbor logs.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `edges` (List[Tuple[TNode, TNode, float]]): Timestamped directed edges (u, v, timestamp).
   - `delta` (float): Maximum allowed time window between first and last edge of a motif.

4. OUTPUT PARAMETERS:
   - `count_two_hop_bursts()` (int): Count of sequential 2-edge motifs u -> v -> w within delta.
   - `count_ping_pong_bursts()` (int): Count of reciprocity bursts u -> v then v -> u within delta.
   - `count_temporal_triangles()` (int): Count of closed 3-edge triangles within delta.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: Exact motif counts bounded strictly by t_{end} - t_{start} <= delta.
================================================================================
"""

from collections import defaultdict
from typing import Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoTemporalMotifsCounting(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TEMP-213
      name: GraphAlgoTemporalMotifsCounting
      version: 1.0.0
      category: graph_temporal
      capability_tags: [graph, temporal, motifs, paranjape, subgraph_patterns, temporal_bursts]
      inputs:
        type: object
        required: [edges, delta]
        properties:
          edges:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}]
          delta: {type: number, minimum: 0}
      outputs:
        type: object
        properties:
          two_hop_count: {type: integer}
          ping_pong_count: {type: integer}
          triangle_count: {type: integer}
      parameters:
        delta: {type: number}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M * d_avg)
        space: O(M)
    ---
    """

    def __init__(self, edges: List[Tuple[TNode, TNode, float]], delta: float = 60.0) -> None:
        """
        Initialize temporal motifs engine.

        Args:
            edges: List of (u, v, timestamp) directed interactions.
            delta: Temporal window span.
        """
        self._edges: List[Tuple[TNode, TNode, float]] = sorted(edges, key=lambda x: x[2])
        self._delta: float = max(0.0, float(delta))

    def count_two_hop_bursts(self) -> int:
        """
        Count occurrences of 2-hop sequences: u -> v at t1, then v -> w at t2, with 0 < t2 - t1 <= delta.

        Returns:
            Integer count of 2-hop causal transitions.
        """
        count = 0
        incoming: Dict[TNode, List[Tuple[TNode, float]]] = defaultdict(list)
        for u, v, t in self._edges:
            cutoff = t - self._delta
            if v in incoming:
                incoming[v] = [item for item in incoming[v] if item[1] >= cutoff]
            if u in incoming:
                valid_prev = [item for item in incoming[u] if cutoff <= item[1] < t and item[0] != v]
                count += len(valid_prev)
            incoming[v].append((u, t))
        return count

    def count_ping_pong_bursts(self) -> int:
        """
        Count occurrences of reciprocity bursts: u -> v at t1, then v -> u at t2 with 0 < t2 - t1 <= delta.

        Returns:
            Integer count of ping-pong reply events.
        """
        count = 0
        last_directed: Dict[Tuple[TNode, TNode], List[float]] = defaultdict(list)
        for u, v, t in self._edges:
            cutoff = t - self._delta
            reverse_pair = (v, u)
            if reverse_pair in last_directed:
                valid_replies = [ts for ts in last_directed[reverse_pair] if cutoff <= ts < t]
                count += len(valid_replies)
            directed_pair = (u, v)
            last_directed[directed_pair] = [ts for ts in last_directed[directed_pair] if ts >= cutoff]
            last_directed[directed_pair].append(t)
        return count

    def count_temporal_triangles(self) -> int:
        """
        Count closed temporal triangle motifs (e.g. u->v, v->w, w->u or u->v, u->w, v->w) within delta.

        Returns:
            Integer count of temporal triangles.
        """
        count = 0
        m = len(self._edges)
        for i in range(m):
            u1, v1, t1 = self._edges[i]
            for j in range(i + 1, m):
                u2, v2, t2 = self._edges[j]
                if t2 - t1 > self._delta:
                    break
                for k in range(j + 1, m):
                    u3, v3, t3 = self._edges[k]
                    if t3 - t1 > self._delta:
                        break
                    nodes = {u1, v1, u2, v2, u3, v3}
                    if len(nodes) == 3:
                        edges_set = {(u1, v1), (u2, v2), (u3, v3)}
                        if len(edges_set) == 3:
                            count += 1
        return count
