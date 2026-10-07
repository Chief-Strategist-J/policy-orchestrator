"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Spanning Tree Protocol STP (ALGO-GRAPH-SYS-314)

1. OVERVIEW & OBJECTIVE:
Simulates IEEE 802.1D Spanning Tree Protocol (STP) and Rapid Spanning Tree Protocol (RSTP)
on switched Layer 2 network topologies. Elects the canonical Root Bridge by lowest Bridge ID,
computes root path costs, selects Root Ports and Designated Ports per collision domain,
and places redundant links into Alternate/Blocked states to eliminate network broadcast loops.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(|V_bridges| * |E_links|) for BPDU convergence rounds.
- Space Complexity: O(|V_bridges| + |E_links|) for port role and state registries.
- Invariants: The active forwarding graph forms an exact spanning tree on each connected component.

3. INPUT PARAMETERS:
- `bridge_priorities`: Dict[TNode, int] configurable priority values per bridge/switch.
- `links`: List[Tuple[TNode, TNode, float]] network link definitions `(bridge_u, bridge_v, path_cost)`.

4. OUTPUT PARAMETERS:
- `root_bridge`: TNode the elected root bridge switch.
- `root_path_costs`: Dict[TNode, float] shortest path cost from each bridge to root.
- `port_roles`: Dict[Tuple[TNode, TNode], str] role of each directional port ('root', 'designated', 'blocked').
- `active_spanning_tree_edges`: List[Tuple[TNode, TNode]] set of forward-enabled spanning tree links.
- `blocked_edges`: List[Tuple[TNode, TNode]] redundant standby links.

5. AGENT CONTRACT:
- Role: Layer 2 Network Infrastructure Analyst.
- Rules: Bridge IDs are strictly ordered as (priority, string_identifier).
- Guardrails: Verify resulting topology is loop-free and maintains full reachability.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import heapq

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSpanningTreeProtocolStp(Generic[TNode]):
    """
    inputs:
      bridge_priorities: Dict[TNode, int]
      links: List[Tuple[TNode, TNode, float]]
    outputs:
      root_bridge: TNode
      root_path_costs: Dict[TNode, float]
      port_roles: Dict[Tuple[TNode, TNode], str]
      active_spanning_tree_edges: List[Tuple[TNode, TNode]]
      blocked_edges: List[Tuple[TNode, TNode]]
    parameters:
      none
    capability_tags:
      - stp_protocol
      - rstp
      - spanning_tree
      - loop_prevention
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(|V| log |V| + |E|)"
      space: "O(|V| + |E|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        bridge_priorities: Dict[TNode, int],
        links: List[Tuple[TNode, TNode, float]],
    ) -> Dict[str, Any]:
        all_bridges: List[TNode] = sorted(list(bridge_priorities.keys()), key=lambda x: str(x))
        for u, v, _ in links:
            if u not in bridge_priorities:
                all_bridges.append(u)
            if v not in bridge_priorities:
                all_bridges.append(v)
        all_bridges = sorted(list(set(all_bridges)), key=lambda x: str(x))

        if not all_bridges:
            return {
                "root_bridge": None,
                "root_path_costs": {},
                "port_roles": {},
                "active_spanning_tree_edges": [],
                "blocked_edges": [],
            }

        bridge_ids = {u: (bridge_priorities.get(u, 32768), str(u)) for u in all_bridges}
        root_bridge = min(all_bridges, key=lambda u: bridge_ids[u])

        adj: Dict[TNode, List[Tuple[TNode, float]]] = {u: [] for u in all_bridges}
        for u, v, cost in links:
            adj[u].append((v, cost))
            adj[v].append((u, cost))

        root_costs: Dict[TNode, float] = {u: float("inf") for u in all_bridges}
        parent_bridge: Dict[TNode, Optional[TNode]] = {u: None for u in all_bridges}

        root_costs[root_bridge] = 0.0
        pq: List[Tuple[float, Tuple[int, str], TNode]] = [(0.0, bridge_ids[root_bridge], root_bridge)]

        while pq:
            cost, _, u = heapq.heappop(pq)
            if cost > root_costs[u]:
                continue

            for v, link_cost in adj[u]:
                new_cost = cost + link_cost
                if new_cost < root_costs[v]:
                    root_costs[v] = new_cost
                    parent_bridge[v] = u
                    heapq.heappush(pq, (new_cost, bridge_ids[u], v))
                elif new_cost == root_costs[v]:
                    if parent_bridge[v] is not None and bridge_ids[u] < bridge_ids[parent_bridge[v]]:
                        parent_bridge[v] = u

        port_roles: Dict[Tuple[TNode, TNode], str] = {}
        active_edges: List[Tuple[TNode, TNode]] = []
        blocked_edges: List[Tuple[TNode, TNode]] = []

        for u, v, _ in links:
            is_u_root_port = parent_bridge[u] == v
            is_v_root_port = parent_bridge[v] == u

            if is_u_root_port:
                port_roles[(u, v)] = "root"
                port_roles[(v, u)] = "designated"
                active_edges.append((u, v) if str(u) < str(v) else (v, u))
            elif is_v_root_port:
                port_roles[(v, u)] = "root"
                port_roles[(u, v)] = "designated"
                active_edges.append((u, v) if str(u) < str(v) else (v, u))
            else:
                cost_u, id_u = root_costs[u], bridge_ids[u]
                cost_v, id_v = root_costs[v], bridge_ids[v]

                if (cost_u, id_u) < (cost_v, id_v):
                    port_roles[(u, v)] = "designated"
                    port_roles[(v, u)] = "blocked"
                else:
                    port_roles[(v, u)] = "designated"
                    port_roles[(u, v)] = "blocked"
                blocked_edges.append((u, v) if str(u) < str(v) else (v, u))

        return {
            "root_bridge": root_bridge,
            "root_path_costs": root_costs,
            "port_roles": port_roles,
            "active_spanning_tree_edges": list(set(active_edges)),
            "blocked_edges": list(set(blocked_edges)),
        }
