"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Sugiyama Hierarchical Layout (ALGO-GRAPH-SYS-316)

1. OVERVIEW & OBJECTIVE:
Implements the Sugiyama layered graph drawing framework for directed graphs.
Executes four sequential architectural stages:
1. Cycle Removal (Feedback Arc Set reversal via DFS topological coloring).
2. Layer Assignment (Longest path layering from source nodes).
3. Dummy Node Insertion (Subdividing long edges spanning multiple layers into unit spans).
4. Crossing Reduction & Coordinate Assignment (Barycentric layer ordering and grid placement).

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(|V| + |E| * layers) for layering and barycentric crossing reduction.
- Space Complexity: O(|V| + |E_dummy|) for layered grid and dummy vertex structures.
- Invariants: All normalized edges flow strictly downward across adjacent layers.

3. INPUT PARAMETERS:
- `adjacency`: Dict[TNode, List[TNode]] directed graph topology.
- `layer_distance`: float vertical spacing between layers (default 100.0).
- `node_distance`: float horizontal spacing between vertices within a layer (default 80.0).
- `sweeps`: int number of barycentric crossing reduction passes (default 4).

4. OUTPUT PARAMETERS:
- `node_positions`: Dict[TNode, Tuple[float, float]] assigned `(x, y)` coordinates for original vertices.
- `layer_assignment`: Dict[TNode, int] layer index per original vertex.
- `reversed_edges`: List[Tuple[TNode, TNode]] edges reversed during cycle elimination.
- `dummy_nodes`: List[str] generated dummy transition vertices.
- `edge_crossings`: int total edge crossing count in the final layout.

5. AGENT CONTRACT:
- Role: Visual Graph Layout Engine.
- Rules: Maintain visual distinction for reversed cycle edges.
- Guardrails: Handle disconnected components and self-loops gracefully.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
from collections import defaultdict, deque

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoSugiyamaHierarchicalLayout(Generic[TNode]):
    """
    inputs:
      adjacency: Dict[TNode, List[TNode]]
      layer_distance: Optional[float]
      node_distance: Optional[float]
      sweeps: Optional[int]
    outputs:
      node_positions: Dict[TNode, Tuple[float, float]]
      layer_assignment: Dict[TNode, int]
      reversed_edges: List[Tuple[TNode, TNode]]
      dummy_nodes: List[str]
      edge_crossings: int
    parameters:
      layer_distance: 100.0
      node_distance: 80.0
      sweeps: 4
    capability_tags:
      - sugiyama_layout
      - hierarchical_drawing
      - crossing_reduction
      - dag_visualization
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(|V| + |E| * layers)"
      space: "O(|V| + |E_dummy|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Dict[TNode, List[TNode]],
        layer_distance: float = 100.0,
        node_distance: float = 80.0,
        sweeps: int = 4,
    ) -> Dict[str, Any]:
        all_nodes: List[TNode] = sorted(list(adjacency.keys()), key=lambda x: str(x))
        for targets in adjacency.values():
            for v in targets:
                if v not in all_nodes:
                    all_nodes.append(v)
        all_nodes = sorted(list(set(all_nodes)), key=lambda x: str(x))

        if not all_nodes:
            return {
                "node_positions": {},
                "layer_assignment": {},
                "reversed_edges": [],
                "dummy_nodes": [],
                "edge_crossings": 0,
            }

        color: Dict[TNode, int] = {u: 0 for u in all_nodes}
        reversed_edges: List[Tuple[TNode, TNode]] = []
        dag_adj: Dict[TNode, List[TNode]] = {u: [] for u in all_nodes}

        def dfs_cycle(u: TNode) -> None:
            color[u] = 1
            for v in adjacency.get(u, []):
                if u == v:
                    continue
                if color[v] == 1:
                    reversed_edges.append((u, v))
                elif color[v] == 0:
                    dag_adj[u].append(v)
                    dfs_cycle(v)
                else:
                    dag_adj[u].append(v)
            color[u] = 2

        for u in all_nodes:
            if color[u] == 0:
                dfs_cycle(u)

        in_deg: Dict[TNode, int] = {u: 0 for u in all_nodes}
        for u in all_nodes:
            for v in dag_adj[u]:
                in_deg[v] = in_deg.get(v, 0) + 1

        topo_order: List[TNode] = []
        q: deque[TNode] = deque([u for u in all_nodes if in_deg[u] == 0])

        while q:
            u = q.popleft()
            topo_order.append(u)
            for v in dag_adj[u]:
                in_deg[v] -= 1
                if in_deg[v] == 0:
                    q.append(v)

        for u in all_nodes:
            if u not in topo_order:
                topo_order.append(u)

        layer_assign: Dict[TNode, int] = {u: 0 for u in all_nodes}
        for u in topo_order:
            for v in dag_adj[u]:
                layer_assign[v] = max(layer_assign[v], layer_assign[u] + 1)

        layers: Dict[int, List[Any]] = defaultdict(list)
        for u in all_nodes:
            layers[layer_assign[u]].append(u)

        max_layer = max(layer_assign.values()) if layer_assign else 0
        dummy_nodes: List[str] = []
        extended_adj: Dict[Any, List[Any]] = {u: [] for u in all_nodes}

        dummy_counter = 0
        for u in all_nodes:
            for v in dag_adj[u]:
                span = layer_assign[v] - layer_assign[u]
                if span <= 1:
                    extended_adj[u].append(v)
                else:
                    prev = u
                    for l in range(layer_assign[u] + 1, layer_assign[v]):
                        dummy_id = f"__dummy_{dummy_counter}__"
                        dummy_counter += 1
                        dummy_nodes.append(dummy_id)
                        layers[l].append(dummy_id)
                        extended_adj[prev].append(dummy_id)
                        extended_adj[dummy_id] = []
                        prev = dummy_id
                    extended_adj[prev].append(v)

        for _ in range(sweeps):
            for l in range(1, max_layer + 1):
                prev_layer = layers[l - 1]
                pos_map = {node: idx for idx, node in enumerate(prev_layer)}

                def barycenter(node: Any) -> float:
                    preds = [p for p in prev_layer if node in extended_adj.get(p, [])]
                    if not preds:
                        return float(pos_map.get(node, 0))
                    return sum(pos_map[p] for p in preds) / len(preds)

                layers[l].sort(key=lambda node: (barycenter(node), str(node)))

        node_positions: Dict[TNode, Tuple[float, float]] = {}
        for l in range(max_layer + 1):
            nodes_in_l = layers[l]
            k_nodes = len(nodes_in_l)
            offset = -((k_nodes - 1) * node_distance) / 2.0
            for idx, node in enumerate(nodes_in_l):
                x_coord = offset + idx * node_distance
                y_coord = l * layer_distance
                if node in all_nodes:
                    node_positions[node] = (round(x_coord, 2), round(y_coord, 2))

        crossings = 0
        for l in range(max_layer):
            l1 = layers[l]
            l2 = layers[l + 1]
            edges_between: List[Tuple[int, int]] = []
            pos2 = {node: idx for idx, node in enumerate(l2)}
            for idx1, u in enumerate(l1):
                for v in extended_adj.get(u, []):
                    if v in pos2:
                        edges_between.append((idx1, pos2[v]))

            for i in range(len(edges_between)):
                for j in range(i + 1, len(edges_between)):
                    u1, v1 = edges_between[i]
                    u2, v2 = edges_between[j]
                    if (u1 < u2 and v1 > v2) or (u1 > u2 and v1 < v2):
                        crossings += 1

        return {
            "node_positions": node_positions,
            "layer_assignment": layer_assign,
            "reversed_edges": reversed_edges,
            "dummy_nodes": dummy_nodes,
            "edge_crossings": crossings,
        }
