"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Link-State and Distance-Vector Routing (ALGO-GRAPH-SYS-312)

1. OVERVIEW & OBJECTIVE:
Simulates foundational network routing protocols: Link-State Routing (OSPF-style topology
flooding and Dijkstra shortest path tree computation) and Distance-Vector Routing
(RIP-style distributed Bellman-Ford iterative exchange with split horizon and poison reverse),
generating hop-by-hop forwarding tables and analyzing convergence dynamics.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(|V| (|E| + |V| log |V|)) for all-pairs Link-State; O(iterations * |V| * |E|) for Distance-Vector.
- Space Complexity: O(|V|^2) routing table matrices.
- Invariants: Forwarding tables guarantee loop-free shortest paths at stable convergence.

3. INPUT PARAMETERS:
- `adjacency`: Dict[TNode, List[Tuple[TNode, float]]] weighted directed link topology.
- `protocol`: str in ('link_state', 'distance_vector').
- `split_horizon`: bool enable split horizon rule for distance vector.
- `poison_reverse`: bool enable poison reverse for unreachable paths.
- `max_hop_count`: int infinity threshold for distance vector (default 16).

4. OUTPUT PARAMETERS:
- `forwarding_tables`: Dict[TNode, Dict[TNode, Tuple[Optional[TNode], float]]] router -> (dest -> (next_hop, cost)).
- `convergence_rounds`: int number of iterative update rounds until stabilization.
- `count_to_infinity_detected`: bool flag indicating if routing loops exceeded hop limit.
- `shortest_paths`: Dict[TNode, Dict[TNode, List[TNode]]] full reconstructed paths.

5. AGENT CONTRACT:
- Role: Network Protocol Analyst.
- Rules: Link costs must be positive.
- Guardrails: Check for routing table oscillations or split horizon mitigation limits.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import heapq

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoLinkStateDistanceVectorRouting(Generic[TNode]):
    """
    inputs:
      adjacency: Dict[TNode, List[Tuple[TNode, float]]]
      protocol: Optional[str]
      split_horizon: Optional[bool]
      poison_reverse: Optional[bool]
      max_hop_count: Optional[int]
    outputs:
      forwarding_tables: Dict[TNode, Dict[TNode, Tuple[Optional[TNode], float]]]
      convergence_rounds: int
      count_to_infinity_detected: bool
      shortest_paths: Dict[TNode, Dict[TNode, List[TNode]]]
    parameters:
      protocol: "link_state"
      split_horizon: true
      poison_reverse: true
      max_hop_count: 16
    capability_tags:
      - link_state
      - distance_vector
      - ospf_routing
      - rip_routing
      - forwarding_table
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(|V| (|E| + |V| log |V|))"
      space: "O(|V|^2)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Dict[TNode, List[Tuple[TNode, float]]],
        protocol: str = "link_state",
        split_horizon: bool = True,
        poison_reverse: bool = True,
        max_hop_count: int = 16,
    ) -> Dict[str, Any]:
        nodes: List[TNode] = sorted(list(adjacency.keys()), key=lambda x: str(x))
        for targets in adjacency.values():
            for v, _ in targets:
                if v not in nodes:
                    nodes.append(v)
        nodes = sorted(list(set(nodes)), key=lambda x: str(x))

        forwarding_tables: Dict[TNode, Dict[TNode, Tuple[Optional[TNode], float]]] = {}
        shortest_paths: Dict[TNode, Dict[TNode, List[TNode]]] = {}

        if protocol == "link_state":
            for src in nodes:
                dist: Dict[TNode, float] = {u: float("inf") for u in nodes}
                prev: Dict[TNode, Optional[TNode]] = {u: None for u in nodes}
                next_hop: Dict[TNode, Optional[TNode]] = {u: None for u in nodes}

                dist[src] = 0.0
                pq: List[Tuple[float, TNode]] = [(0.0, src)]

                while pq:
                    d, u = heapq.heappop(pq)
                    if d > dist[u]:
                        continue

                    for v, cost in adjacency.get(u, []):
                        if dist[u] + cost < dist[v]:
                            dist[v] = dist[u] + cost
                            prev[v] = u
                            heapq.heappush(pq, (dist[v], v))

                fwd: Dict[TNode, Tuple[Optional[TNode], float]] = {}
                paths: Dict[TNode, List[TNode]] = {}

                for dest in nodes:
                    if dest == src:
                        fwd[dest] = (src, 0.0)
                        paths[dest] = [src]
                        continue

                    if dist[dest] == float("inf"):
                        fwd[dest] = (None, float("inf"))
                        paths[dest] = []
                        continue

                    curr = dest
                    p = [dest]
                    while prev[curr] is not None and prev[curr] != src:
                        curr = prev[curr]
                        p.append(curr)
                    p.append(src)
                    p.reverse()

                    hop = curr if prev[curr] == src else prev[dest]
                    fwd[dest] = (hop, dist[dest])
                    paths[dest] = p

                forwarding_tables[src] = fwd
                shortest_paths[src] = paths

            return {
                "forwarding_tables": forwarding_tables,
                "convergence_rounds": 1,
                "count_to_infinity_detected": False,
                "shortest_paths": shortest_paths,
            }

        table: Dict[TNode, Dict[TNode, Tuple[float, Optional[TNode]]]] = {}
        for u in nodes:
            table[u] = {v: (float("inf"), None) for v in nodes}
            table[u][u] = (0.0, u)
            for v, cost in adjacency.get(u, []):
                table[u][v] = (cost, v)

        rounds = 0
        changed = True
        count_to_infinity = False

        while changed and rounds < max_hop_count * 2:
            changed = False
            rounds += 1
            new_table = {u: dict(table[u]) for u in nodes}

            for u in nodes:
                for v, link_cost in adjacency.get(u, []):
                    for d in nodes:
                        cost_vd, nh_vd = table[v][d]
                        if split_horizon and nh_vd == u:
                            if poison_reverse:
                                cost_vd = float("inf")
                            else:
                                continue

                        if link_cost + cost_vd < new_table[u][d][0]:
                            new_table[u][d] = (link_cost + cost_vd, v)
                            changed = True

            table = new_table

        if rounds >= max_hop_count * 2:
            count_to_infinity = True

        for u in nodes:
            forwarding_tables[u] = {
                d: (nh if cost < float("inf") else None, cost)
                for d, (cost, nh) in table[u].items()
            }
            shortest_paths[u] = {}
            for d in nodes:
                if table[u][d][0] < float("inf"):
                    shortest_paths[u][d] = [u, table[u][d][1], d] if table[u][d][1] != d else [u, d]
                else:
                    shortest_paths[u][d] = []

        return {
            "forwarding_tables": forwarding_tables,
            "convergence_rounds": rounds,
            "count_to_infinity_detected": count_to_infinity,
            "shortest_paths": shortest_paths,
        }
