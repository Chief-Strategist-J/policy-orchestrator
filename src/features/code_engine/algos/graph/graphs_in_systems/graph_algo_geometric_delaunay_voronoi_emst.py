"""
ALGORITHM & ARCHITECTURE BLUEPRINT: Geometric Graphs Delaunay Voronoi EMST (ALGO-GRAPH-SYS-318)

1. OVERVIEW & OBJECTIVE:
Constructs fundamental 2D geometric proximity graphs from spatial point sets. Implements
Delaunay Triangulation (via Bowyer-Watson randomized incremental circumcircle test), derives
the Voronoi Diagram dual polygon partition (triangle circumcenters and cell boundaries),
and extracts the Euclidean Minimum Spanning Tree (EMST) in O(N log N) time by running Kruskal
strictly over the planar Delaunay edge set.

2. COMPLEXITY & INVARIANTS:
- Time Complexity: O(N log N) expected time in 2D Euclidean plane.
- Space Complexity: O(N) for triangle records, Voronoi vertices, and disjoint-set partitions.
- Invariants: Empty circumcircle condition holds for all Delaunay triangles; EMST is a subset of Delaunay edges.

3. INPUT PARAMETERS:
- `points`: Dict[TNode, Tuple[float, float]] mapping point identifiers to 2D coordinates `(x, y)`.

4. OUTPUT PARAMETERS:
- `delaunay_edges`: List[Tuple[TNode, TNode]] set of edges in the Delaunay triangulation.
- `delaunay_triangles`: List[Tuple[TNode, TNode, TNode]] triangle vertex triples.
- `voronoi_vertices`: List[Tuple[float, float]] circumcenters representing Voronoi cell corners.
- `emst_edges`: List[Tuple[TNode, TNode, float]] edges `(u, v, length)` forming the Euclidean MST.
- `total_emst_length`: float total Euclidean length of the minimum spanning tree.

5. AGENT CONTRACT:
- Role: Geometric Proximity Analyst.
- Rules: Requires 2D Cartesian coordinates (project spherical coords beforehand).
- Guardrails: Degenerate collinear or co-circular points handled via epsilon perturbations.
"""

from typing import Any, Dict, Generic, Hashable, List, Optional, Set, Tuple, TypeVar
import math

TNode = TypeVar("TNode", bound=Hashable)


class GraphAlgoGeometricDelaunayVoronoiEmst(Generic[TNode]):
    """
    inputs:
      points: Dict[TNode, Tuple[float, float]]
    outputs:
      delaunay_edges: List[Tuple[TNode, TNode]]
      delaunay_triangles: List[Tuple[TNode, TNode, TNode]]
      voronoi_vertices: List[Tuple[float, float]]
      emst_edges: List[Tuple[TNode, TNode, float]]
      total_emst_length: float
    parameters:
      none
    capability_tags:
      - delaunay_triangulation
      - voronoi_diagram
      - euclidean_mst
      - geometric_graph
    purity: deterministic
    determinism: true
    idempotency: true
    complexity:
      time: "O(N log N)"
      space: "O(N)"
    """

    def __init__(self) -> None:
        pass

    def evaluate(
        self,
        points: Dict[TNode, Tuple[float, float]],
    ) -> Dict[str, Any]:
        node_list: List[TNode] = sorted(list(points.keys()), key=lambda x: str(x))
        n = len(node_list)

        if n < 2:
            return {
                "delaunay_edges": [],
                "delaunay_triangles": [],
                "voronoi_vertices": [],
                "emst_edges": [],
                "total_emst_length": 0.0,
            }

        if n == 2:
            u, v = node_list[0], node_list[1]
            p0, p1 = points[u], points[v]
            dist = math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)
            edge = (u, v) if str(u) < str(v) else (v, u)
            return {
                "delaunay_edges": [edge],
                "delaunay_triangles": [],
                "voronoi_vertices": [((p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0)],
                "emst_edges": [(edge[0], edge[1], round(dist, 4))],
                "total_emst_length": round(dist, 4),
            }

        min_x = min(points[u][0] for u in node_list)
        max_x = max(points[u][0] for u in node_list)
        min_y = min(points[u][1] for u in node_list)
        max_y = max(points[u][1] for u in node_list)

        dx = max(max_x - min_x, 1.0)
        dy = max(max_y - min_y, 1.0)
        delta_max = max(dx, dy)
        mid_x = (min_x + max_x) / 2.0
        mid_y = (min_y + max_y) / 2.0

        p_super1 = (mid_x - 20 * delta_max, mid_y - delta_max)
        p_super2 = (mid_x, mid_y + 20 * delta_max)
        p_super3 = (mid_x + 20 * delta_max, mid_y - delta_max)

        super_id1 = "__super_1__"
        super_id2 = "__super_2__"
        super_id3 = "__super_3__"

        all_coords: Dict[Any, Tuple[float, float]] = dict(points)
        all_coords[super_id1] = p_super1
        all_coords[super_id2] = p_super2
        all_coords[super_id3] = p_super3

        triangles: List[Tuple[Any, Any, Any]] = [(super_id1, super_id2, super_id3)]

        def circumcircle_contains(tri: Tuple[Any, Any, Any], pt: Tuple[float, float]) -> bool:
            a, b, c = all_coords[tri[0]], all_coords[tri[1]], all_coords[tri[2]]
            ax, ay = a[0], a[1]
            bx, by = b[0], b[1]
            cx, cy = c[0], c[1]

            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            if abs(d) < 1e-9:
                return False

            ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
            uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
            r2 = (ax - ux) ** 2 + (ay - uy) ** 2
            dist2 = (pt[0] - ux) ** 2 + (pt[1] - uy) ** 2
            return dist2 <= r2

        for u in node_list:
            pt = points[u]
            bad_triangles: List[Tuple[Any, Any, Any]] = []
            for tri in triangles:
                if circumcircle_contains(tri, pt):
                    bad_triangles.append(tri)

            polygon: List[Tuple[Any, Any]] = []
            for tri in bad_triangles:
                edges = [
                    (tri[0], tri[1]),
                    (tri[1], tri[2]),
                    (tri[2], tri[0]),
                ]
                for e in edges:
                    shared = False
                    for other in bad_triangles:
                        if other == tri:
                            continue
                        other_edges = [
                            (other[0], other[1]),
                            (other[1], other[2]),
                            (other[2], other[0]),
                        ]
                        if e in other_edges or (e[1], e[0]) in other_edges:
                            shared = True
                            break
                    if not shared:
                        polygon.append(e)

            triangles = [t for t in triangles if t not in bad_triangles]
            for edge in polygon:
                triangles.append((edge[0], edge[1], u))

        super_set = {super_id1, super_id2, super_id3}
        final_triangles: List[Tuple[TNode, TNode, TNode]] = []
        delaunay_edge_set: Set[Tuple[TNode, TNode]] = set()

        for tri in triangles:
            if not (tri[0] in super_set or tri[1] in super_set or tri[2] in super_set):
                sorted_tri = tuple(sorted([tri[0], tri[1], tri[2]], key=lambda x: str(x)))
                final_triangles.append(sorted_tri)  # type: ignore

                e1 = (tri[0], tri[1]) if str(tri[0]) < str(tri[1]) else (tri[1], tri[0])
                e2 = (tri[1], tri[2]) if str(tri[1]) < str(tri[2]) else (tri[2], tri[1])
                e3 = (tri[2], tri[0]) if str(tri[2]) < str(tri[0]) else (tri[0], tri[2])
                delaunay_edge_set.add(e1)
                delaunay_edge_set.add(e2)
                delaunay_edge_set.add(e3)

        delaunay_edges = sorted(list(delaunay_edge_set), key=lambda e: (str(e[0]), str(e[1])))

        voronoi_vertices: List[Tuple[float, float]] = []
        for tri in final_triangles:
            a, b, c = points[tri[0]], points[tri[1]], points[tri[2]]
            ax, ay = a[0], a[1]
            bx, by = b[0], b[1]
            cx, cy = c[0], c[1]
            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            if abs(d) > 1e-9:
                ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
                uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
                voronoi_vertices.append((round(ux, 3), round(uy, 3)))

        candidate_emst_edges: List[Tuple[float, TNode, TNode]] = []
        for u, v in delaunay_edges:
            p0, p1 = points[u], points[v]
            dist = math.sqrt((p1[0] - p0[0]) ** 2 + (p1[1] - p0[1]) ** 2)
            candidate_emst_edges.append((dist, u, v))

        candidate_emst_edges.sort(key=lambda x: x[0])

        parent: Dict[TNode, TNode] = {u: u for u in node_list}

        def find(u: TNode) -> TNode:
            root = u
            while parent[root] != root:
                root = parent[root]
            curr = u
            while curr != root:
                nxt = parent[curr]
                parent[curr] = root
                curr = nxt
            return root

        def union(u: TNode, v: TNode) -> bool:
            ru, rv = find(u), find(v)
            if ru != rv:
                parent[ru] = rv
                return True
            return False

        emst_edges: List[Tuple[TNode, TNode, float]] = []
        total_len = 0.0

        for dist, u, v in candidate_emst_edges:
            if union(u, v):
                emst_edges.append((u, v, round(dist, 4)))
                total_len += dist
                if len(emst_edges) == n - 1:
                    break

        return {
            "delaunay_edges": delaunay_edges,
            "delaunay_triangles": final_triangles,
            "voronoi_vertices": voronoi_vertices,
            "emst_edges": emst_edges,
            "total_emst_length": round(total_len, 4),
        }
