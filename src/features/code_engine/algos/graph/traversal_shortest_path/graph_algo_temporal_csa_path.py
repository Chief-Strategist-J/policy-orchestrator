"""Connection Scan Algorithm (CSA) for Temporal Networks and Transit Schedules.

Finds the earliest arrival time and reconstructed temporal itinerary across time-stamped connections
in single-pass linear time by scanning sorted departure connections.
"""

from typing import Dict, Generic, Hashable, List, NamedTuple, Optional, Tuple, TypeVar

TNode = TypeVar("TNode", bound=Hashable)


class TemporalConnection(NamedTuple):
    dep_node: Hashable
    arr_node: Hashable
    dep_time: float
    arr_time: float
    trip_id: str


class GraphAlgoTemporalCsaPath(Generic[TNode]):
    """
    ---
    contract: ALGO-GRAPH-PATH-49
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(|C| log |C|) for sorting + O(|C|) scan
      space: O(|V| + |C|)
    ---
    """

    def __init__(self, connections: List[TemporalConnection]) -> None:
        self._connections: List[TemporalConnection] = sorted(
            connections, key=lambda c: (c.dep_time, c.arr_time, str(c.dep_node))
        )
        self._nodes: set[Hashable] = set()
        for c in self._connections:
            self._nodes.add(c.dep_node)
            self._nodes.add(c.arr_node)

    def earliest_arrival(
        self,
        source: TNode,
        target: TNode,
        start_time: float,
    ) -> Tuple[float, List[TemporalConnection]]:
        if source == target:
            return start_time, []

        earliest_arr: Dict[Hashable, float] = {u: float("inf") for u in self._nodes}
        in_connection: Dict[Hashable, Optional[TemporalConnection]] = {u: None for u in self._nodes}
        earliest_arr[source] = start_time

        for conn in self._connections:
            if conn.dep_time < start_time:
                continue
            if conn.dep_time >= earliest_arr.get(conn.dep_node, float("inf")):
                if conn.arr_time < earliest_arr.get(conn.arr_node, float("inf")):
                    earliest_arr[conn.arr_node] = conn.arr_time
                    in_connection[conn.arr_node] = conn

        if earliest_arr.get(target, float("inf")) == float("inf"):
            return float("inf"), []

        itinerary: List[TemporalConnection] = []
        curr: Hashable = target
        while curr != source and in_connection.get(curr) is not None:
            conn = in_connection[curr]
            if conn is None:
                break
            itinerary.append(conn)
            curr = conn.dep_node

        itinerary.reverse()
        return earliest_arr[target], itinerary
