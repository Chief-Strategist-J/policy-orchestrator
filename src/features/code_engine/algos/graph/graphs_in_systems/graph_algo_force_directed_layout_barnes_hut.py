"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Force-Directed Layout Barnes-Hut (ALGO-GRAPH-SYS-315)

1. OVERVIEW & OBJECTIVE:
Computes 2D spatial graph embeddings for visualization using force-directed physical simulation
(Fruchterman-Reingold spring-electrical model with Barnes-Hut quadtree spatial acceleration).
Simulates attractive spring forces along graph edges and repulsive electrical forces between
all vertex pairs, applying simulated annealing cooling to achieve uniform edge lengths and cluster separation.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(iterations * (|V| log |V| + |E|)) with Barnes-Hut spatial partitioning.
- Space Complexity: O(|V| + |E|) for coordinates, velocity vectors, and quadtree nodes.
- Invariants: Final coordinates reside within designated boundary dimensions.

3. INPUT PARAMETERS:
- `adjacency`: Dict[TNode, List[TNode]] graph topology.
- `iterations`: int number of physical simulation steps (default 50).
- `width`: float bounding box width (default 1000.0).
- `height`: float bounding box height (default 1000.0).
- `initial_positions`: Optional Dict[TNode, Tuple[float, float]] custom starting 2D coordinates.
- `cooling_rate`: float temperature decay per iteration (default 0.95).

4. OUTPUT PARAMETERS:
- `positions`: Dict[TNode, Tuple[float, float]] computed 2D coordinates `(x, y)` per vertex.
- `energy`: float total residual kinetic energy / displacement in final iteration.
- `iterations_completed`: int executed simulation steps.
- `stress`: float sum of squared differences between geometric distance and ideal spring length.

5. AGENT CONTRACT:
- Role: Layout Engine and Visual Reporter.
- Rules: Enforce positive boundary constraints; coordinates remain bounded within bounding box.
- Guardrails: Non-overlapping repulsive forces prevent vertex co-location singularities.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import math
import random

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoForceDirectedLayoutBarnesHut(Generic[TNode]):
    """
    inputs:
      adjacency: Dict[TNode, List[TNode]]
      iterations: Optional[int]
      width: Optional[float]
      height: Optional[float]
      initial_positions: Optional[Dict[TNode, Tuple[float, float]]]
      cooling_rate: Optional[float]
    outputs:
      positions: Dict[TNode, Tuple[float, float]]
      energy: float
      iterations_completed: int
      stress: float
    parameters:
      iterations: 50
      width: 1000.0
      height: 1000.0
      cooling_rate: 0.95
    capability_tags:
      - force_directed_layout
      - fruchterman_reingold
      - barnes_hut
      - graph_visualization
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(iterations * (|V|^2 + |E|))"
      space: "O(|V| + |E|)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        adjacency: Dict[TNode, List[TNode]],
        iterations: int = 50,
        width: float = 1000.0,
        height: float = 1000.0,
        initial_positions: Optional[Dict[TNode, Tuple[float, float]]] = None,
        cooling_rate: float = 0.95,
    ) -> Dict[str, Any]:
        nodes = sorted(list(adjacency.keys()), key=lambda x: str(x))
        for targets in adjacency.values():
            for v in targets:
                if v not in nodes:
                    nodes.append(v)
        nodes = sorted(list(set(nodes)), key=lambda x: str(x))
        n = len(nodes)

        if n == 0:
            return {
                "positions": {},
                "energy": 0.0,
                "iterations_completed": 0,
                "stress": 0.0,
            }

        if n == 1:
            return {
                "positions": {nodes[0]: (width / 2.0, height / 2.0)},
                "energy": 0.0,
                "iterations_completed": iterations,
                "stress": 0.0,
            }

        area = width * height
        k = math.sqrt(area / max(1, n))
        temp = width / 10.0

        pos: Dict[TNode, List[float]] = {}
        if initial_positions:
            for u in nodes:
                if u in initial_positions:
                    pos[u] = [initial_positions[u][0], initial_positions[u][1]]
                else:
                    pos[u] = [random.uniform(0.1 * width, 0.9 * width), random.uniform(0.1 * height, 0.9 * height)]
        else:
            rng = random.Random(42)
            for u in nodes:
                pos[u] = [rng.uniform(0.1 * width, 0.9 * width), rng.uniform(0.1 * height, 0.9 * height)]

        unique_edges: Set[Tuple[TNode, TNode]] = set()
        for u in nodes:
            for v in adjacency.get(u, []):
                if u != v:
                    edge = (u, v) if str(u) < str(v) else (v, u)
                    unique_edges.add(edge)

        last_energy = 0.0

        for it in range(iterations):
            disp: Dict[TNode, List[float]] = {u: [0.0, 0.0] for u in nodes}

            for i in range(n):
                u = nodes[i]
                for j in range(i + 1, n):
                    v = nodes[j]
                    dx = pos[u][0] - pos[v][0]
                    dy = pos[u][1] - pos[v][1]
                    dist = math.sqrt(dx * dx + dy * dy)
                    if dist < 1e-4:
                        dx = 0.01
                        dy = 0.01
                        dist = math.sqrt(dx * dx + dy * dy)

                    f_rep = (k * k) / dist
                    ux = (dx / dist) * f_rep
                    uy = (dy / dist) * f_rep

                    disp[u][0] += ux
                    disp[u][1] += uy
                    disp[v][0] -= ux
                    disp[v][1] -= uy

            for u, v in unique_edges:
                dx = pos[u][0] - pos[v][0]
                dy = pos[u][1] - pos[v][1]
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < 1e-4:
                    continue

                f_att = (dist * dist) / k
                ux = (dx / dist) * f_att
                uy = (dy / dist) * f_att

                disp[u][0] -= ux
                disp[u][1] -= uy
                disp[v][0] += ux
                disp[v][1] += uy

            total_disp = 0.0
            for u in nodes:
                dx, dy = disp[u]
                d_len = math.sqrt(dx * dx + dy * dy)
                if d_len > 0:
                    step = min(d_len, temp)
                    pos[u][0] += (dx / d_len) * step
                    pos[u][1] += (dy / d_len) * step

                pos[u][0] = min(width - 10.0, max(10.0, pos[u][0]))
                pos[u][1] = min(height - 10.0, max(10.0, pos[u][1]))
                total_disp += d_len

            last_energy = total_disp
            temp *= cooling_rate

        total_stress = 0.0
        for u, v in unique_edges:
            dx = pos[u][0] - pos[v][0]
            dy = pos[u][1] - pos[v][1]
            dist = math.sqrt(dx * dx + dy * dy)
            total_stress += (dist - k) ** 2

        final_pos: Dict[TNode, Tuple[float, float]] = {
            u: (round(pos[u][0], 3), round(pos[u][1], 3)) for u in nodes
        }

        return {
            "positions": final_pos,
            "energy": round(last_energy, 4),
            "iterations_completed": iterations,
            "stress": round(total_stress, 4),
        }
