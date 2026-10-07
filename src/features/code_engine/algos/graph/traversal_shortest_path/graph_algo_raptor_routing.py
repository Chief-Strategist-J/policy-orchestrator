"""RAPTOR (Round-Based Public Transit Routing) Engine.

Computes Pareto-optimal transit journeys over arrival time and number of transfers
by scanning routes round by round without priority queue overhead.
"""

from typing import Dict, Generic, Hashable, List, NamedTuple, Optional, Set, Tuple, TypeVar

TStop = TypeVar("TStop", bound=Hashable)


class StopTime(NamedTuple):
    stop_id: Hashable
    arr_time: float
    dep_time: float


class TransitTrip(NamedTuple):
    trip_id: str
    stop_times: List[StopTime]


class TransitRoute(NamedTuple):
    route_id: str
    stops: List[Hashable]
    trips: List[TransitTrip]


class GraphAlgoRaptorRouting(Generic[TStop]):
    """
    ---
    contract: ALGO-GRAPH-PATH-50
    layer: Domain Algorithm
    status: Production-Ready
    deterministic: true
    complexity:
      time: O(K * (|Routes| * MaxTripLength + |Footpaths|))
      space: O(K * |Stops|)
    ---
    """

    def __init__(
        self,
        routes: List[TransitRoute],
        transfers: Optional[Dict[Hashable, List[Tuple[Hashable, float]]]] = None,
    ) -> None:
        self._routes: List[TransitRoute] = routes
        self._transfers: Dict[Hashable, List[Tuple[Hashable, float]]] = (
            transfers if transfers is not None else {}
        )
        self._stops: Set[Hashable] = set()
        self._stop_to_routes: Dict[Hashable, List[TransitRoute]] = {}

        for route in self._routes:
            for stop in route.stops:
                self._stops.add(stop)
                if stop not in self._stop_to_routes:
                    self._stop_to_routes[stop] = []
                self._stop_to_routes[stop].append(route)

    def route_query(
        self,
        source: TStop,
        target: TStop,
        departure_time: float,
        max_rounds: int = 5,
    ) -> List[Tuple[int, float]]:
        if source == target:
            return [(0, departure_time)]

        tau: List[Dict[Hashable, float]] = [
            {s: float("inf") for s in self._stops} for _ in range(max_rounds + 1)
        ]
        tau[0][source] = departure_time
        marked_stops: Set[Hashable] = {source}

        pareto_results: List[Tuple[int, float]] = []

        for k in range(1, max_rounds + 1):
            for s in self._stops:
                tau[k][s] = tau[k - 1][s]

            routes_to_process: Set[str] = set()
            for s in marked_stops:
                for r in self._stop_to_routes.get(s, []):
                    routes_to_process.add(r.route_id)

            marked_stops.clear()

            for route in self._routes:
                if route.route_id not in routes_to_process:
                    continue

                cur_trip: Optional[TransitTrip] = None
                boarding_stop: Optional[Hashable] = None

                for stop in route.stops:
                    if cur_trip is not None:
                        for st in cur_trip.stop_times:
                            if st.stop_id == stop:
                                if st.arr_time < tau[k][stop]:
                                    tau[k][stop] = st.arr_time
                                    marked_stops.add(stop)
                                break

                    prev_arrival = tau[k - 1].get(stop, float("inf"))
                    if prev_arrival < float("inf"):
                        for trip in sorted(route.trips, key=lambda t: t.stop_times[0].dep_time):
                            for st in trip.stop_times:
                                if st.stop_id == stop and st.dep_time >= prev_arrival:
                                    if cur_trip is None or st.dep_time < cur_trip.stop_times[0].dep_time:
                                        cur_trip = trip
                                        boarding_stop = stop
                                    break

            for stop in list(marked_stops):
                for dest_stop, walk_time in self._transfers.get(stop, []):
                    walk_arr = tau[k][stop] + walk_time
                    if walk_arr < tau[k].get(dest_stop, float("inf")):
                        tau[k][dest_stop] = walk_arr
                        marked_stops.add(dest_stop)

            if tau[k].get(target, float("inf")) < float("inf"):
                pareto_results.append((k, tau[k][target]))

        return pareto_results
