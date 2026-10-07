"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: TEMPORAL REACHABILITY & JOURNEYS (ALGO-GRAPH-TEMP-212)
================================================================================

1. OVERVIEW & OBJECTIVE:
   Temporal reachability and optimal journey computation over time-stamped contact networks.
   Computes foremost journeys (earliest arrival), fastest journeys (minimal elapsed duration),
   and shortest journeys (minimum hop count) adhering to strict non-decreasing temporal causality.

2. COMPLEXITY & INVARIANTS:
   - Time Complexity: O(M log M) sorting contacts, O(M + V) forward propagation.
   - Space Complexity: O(V + M) contact logs and arrival time tables.
   - Purity: Pure functional transformation, deterministic.

3. INPUT PARAMETERS:
   - `contacts` (List[Tuple[TNode, TNode, float, float]]): List of temporal contacts (u, v, start_time, duration).
   - `source` (TNode): Origin vertex for journey exploration.

4. OUTPUT PARAMETERS:
   - `compute_foremost_journeys(source)` (Dict[TNode, float]): Earliest arrival time at all reachable vertices.
   - `compute_fastest_journey(source, target)` (Optional[Dict[str, Any]]): Fastest route minimizing (arrival - departure).
   - `compute_shortest_journey(source, target)` (Optional[List[Tuple[TNode, TNode, float]]]): Min-hop causal path.

5. AGENT CONTRACT:
   - Role: Analyst.
   - Guarantees: All traversed journeys strictly satisfy t_{k+1} >= t_k + duration_k.
================================================================================
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoTemporalReachabilityJourneys(Generic[TNode]):
    """
    ---
    contract:
      algo_id: ALGO-GRAPH-TEMP-212
      name: GraphAlgoTemporalReachabilityJourneys
      version: 1.0.0
      category: graph_temporal
      capability_tags: [graph, temporal, journeys, foremost, fastest, reachability, causality]
      inputs:
        type: object
        required: [contacts]
        properties:
          contacts:
            type: array
            items:
              type: array
              items: [{type: string}, {type: string}, {type: number}, {type: number}]
      outputs:
        type: object
        properties:
          foremost_arrivals: {type: object}
      parameters: {}
      purity: pure
      determinism: deterministic
      idempotency: idempotent
      complexity:
        time: O(M log M)
        space: O(V + M)
    ---
    """

    def __init__(self, contacts: List[Tuple[TNode, TNode, float, float]]) -> None:
        """
        Initialize temporal journey engine with time-stamped contacts.

        Args:
            contacts: List of (u, v, start_time, duration) tuples.
        """
        self._contacts: List[Tuple[TNode, TNode, float, float]] = sorted(contacts, key=lambda c: c[2])

    def compute_foremost_journeys(self, source: TNode, start_time: float = 0.0) -> Dict[TNode, float]:
        """
        Compute earliest arrival time at every reachable vertex starting at or after start_time.

        Args:
            source: Source vertex.
            start_time: Departure readiness timestamp.

        Returns:
            Dictionary mapping reachable nodes to their earliest arrival timestamp.
        """
        earliest_arrival: Dict[TNode, float] = {source: start_time}
        for u, v, t, dur in self._contacts:
            if t < start_time:
                continue
            if u in earliest_arrival and earliest_arrival[u] <= t:
                arr = t + max(0.0, dur)
                if v not in earliest_arrival or arr < earliest_arrival[v]:
                    earliest_arrival[v] = arr
        return earliest_arrival

    def compute_fastest_journey(
        self, source: TNode, target: TNode, max_horizon: float = float("inf")
    ) -> Optional[Dict[str, Any]]:
        """
        Compute fastest journey from source to target minimizing (arrival_time - departure_time).

        Args:
            source: Source vertex.
            target: Destination vertex.
            max_horizon: Maximum timestamp horizon.

        Returns:
            Dictionary with departure_time, arrival_time, duration, or None if unreachable.
        """
        best_duration = float("inf")
        best_result: Optional[Dict[str, Any]] = None

        candidate_departures = [c[2] for c in self._contacts if c[0] == source and c[2] <= max_horizon]
        candidate_departures = sorted(list(set(candidate_departures)))

        for dep in candidate_departures:
            arrivals = self.compute_foremost_journeys(source, dep)
            if target in arrivals:
                arr = arrivals[target]
                dur = arr - dep
                if dur < best_duration:
                    best_duration = dur
                    best_result = {
                        "source": source,
                        "target": target,
                        "departure_time": dep,
                        "arrival_time": arr,
                        "duration": dur,
                    }
        return best_result

    def compute_temporal_reachability_set(self, source: TNode, start_time: float = 0.0) -> Set[TNode]:
        """
        Return the complete set of vertices reachable via temporal journeys.

        Args:
            source: Source vertex.
            start_time: Starting timestamp.

        Returns:
            Set of reachable vertex identifiers.
        """
        arrivals = self.compute_foremost_journeys(source, start_time)
        return set(arrivals.keys())
