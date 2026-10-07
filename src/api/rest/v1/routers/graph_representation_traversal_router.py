"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH REPRESENTATION & TRAVERSAL ROUTER

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Graph Representation & Traversal Algorithms (#1-33):
- Adjacency Matrix, CSR/CSC, Edge List COO, Incidence Hypergraph, Dynamic Adjacency, WebGraph Compression, K2 Tree, Bitmap Adjacency, RCM Reordering, Vertex ID Mapping, Multigraph Typed Index, Hierarchical Coarsening
- Direction-Optimizing BFS, Iterative Classified DFS, IDDFS, Lex-BFS, Bipartite Verification, Johnson Cycle Enumeration, DAG Shortest/Longest Paths, ALT, Contraction Hierarchies, Hub Labeling, Suurballe Disjoint Paths, Resource Constrained Shortest Path, Pareto Shortest Path, Widest Bottleneck Path, Karp Min-Mean Cycle, Temporal CSA, RAPTOR Routing, Parallel Frontier BFS

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.graph.representation import (
    GraphAlgoAdjacencyMatrix,
    GraphAlgoCsrCsc,
    GraphAlgoEdgeListCoo,
    GraphAlgoIncidenceHypergraph,
    GraphAlgoDynamicAdjacency,
    GraphAlgoWebGraphCompression,
    GraphAlgoK2Tree,
    GraphAlgoBitmapAdjacency,
    GraphAlgoRcmReordering,
    GraphAlgoVertexIdMapping,
    GraphAlgoMultigraphTypedIndex,
    GraphAlgoHierarchicalCoarsening,
)
from src.features.code_engine.algos.graph.traversal_shortest_path import (
    GraphAlgoDirectionOptimizingBfs,
    GraphAlgoIterativeDfsClassified,
    GraphAlgoIddfs,
    GraphAlgoLexBfs,
    GraphAlgoBipartiteTest,
    GraphAlgoJohnsonCycleEnumeration,
    GraphAlgoDagShortestLongestPath,
    GraphAlgoAltShortestPath,
    GraphAlgoContractionHierarchies,
    GraphAlgoHubLabeling,
    GraphAlgoSuurballeDisjointPaths,
    GraphAlgoResourceConstrainedShortestPath,
    GraphAlgoParetoShortestPath,
    GraphAlgoWidestBottleneckPath,
    GraphAlgoKarpMinMeanCycle,
    GraphAlgoTemporalCsaPath,
    GraphAlgoRaptorRouting,
    GraphAlgoParallelBfs,
)

router = APIRouter(prefix="/algos/graph/traversal", tags=["Graph Traversal & Representation"])


class AdjacencyMatrixDTO(BaseModel):
    num_nodes: int = Field(..., description="Number of vertices")
    edges: List[Tuple[int, int]] = Field(..., description="List of (u, v) edge pairs")
    weights: Optional[List[float]] = Field(default=None, description="Optional edge weights")
    directed: bool = Field(default=False, description="Whether edges are directed")


class CsrCscDTO(BaseModel):
    num_nodes: int = Field(..., description="Number of vertices")
    edges: List[Tuple[int, int, float]] = Field(..., description="Weighted edge triplets (u, v, weight)")


class DynamicAdjacencyDTO(BaseModel):
    operations: List[Dict[str, Any]] = Field(..., description="Sequence of insert_edge, delete_edge, insert_vertex operations")


class K2TreeDTO(BaseModel):
    size: int = Field(..., description="Matrix coordinate dimension")
    points: List[Tuple[int, int]] = Field(..., description="List of 2D non-zero coordinate points (r, c)")
    k: int = Field(default=2, description="Branching factor")


class RcmReorderingDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Adjacency list of the graph")


class DirectionOptimizingBfsDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")
    source: str = Field(..., description="Source traversal start node")
    alpha: float = Field(default=14.0, description="Top-down to bottom-up threshold ratio")
    beta: float = Field(default=24.0, description="Bottom-up to top-down threshold ratio")


class ContractionHierarchiesDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Directed weighted adjacency list")
    source: str = Field(..., description="Query source vertex")
    target: str = Field(..., description="Query target vertex")


class HubLabelingDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Directed weighted adjacency list")
    source: str = Field(..., description="Query source vertex")
    target: str = Field(..., description="Query target vertex")


class SuurballeDisjointPathsDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Directed non-negative link topology")
    source: str = Field(..., description="Source vertex")
    target: str = Field(..., description="Target vertex")
    k: int = Field(default=2, description="Number of edge-disjoint paths required")


class ParetoShortestPathDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, List[float]]]] = Field(..., description="Multi-objective edge adjacency mapping")
    source: str = Field(..., description="Source node")
    target: str = Field(..., description="Destination target node")
    max_front_size: int = Field(default=50, description="Pareto front maximum size threshold")


class WidestBottleneckPathDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Adjacency with edge capacities")
    source: str = Field(..., description="Source node")
    target: str = Field(..., description="Destination target node")


class TemporalCsaDTO(BaseModel):
    timetable_connections: List[Tuple[str, str, float, float]] = Field(..., description="Connection tuples (dep_stop, arr_stop, dep_time, arr_time)")
    source: str = Field(..., description="Departure stop")
    target: str = Field(..., description="Arrival destination stop")
    departure_time: float = Field(..., description="Earliest departure time")


class RaptorRoutingDTO(BaseModel):
    routes: Dict[str, List[str]] = Field(..., description="Transit route definitions mapping route_id to ordered sequence of stops")
    timetables: Dict[str, List[List[float]]] = Field(..., description="Timetable departure trips per route")
    source: str = Field(..., description="Source departure station")
    target: str = Field(..., description="Target arrival station")
    departure_time: float = Field(..., description="Initial query departure timestamp")
    max_rounds: int = Field(default=4, description="Maximum transit transfer stages")


@router.post("/adjacency-matrix")
def adjacency_matrix_endpoint(payload: AdjacencyMatrixDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoAdjacencyMatrix(num_nodes=payload.num_nodes, directed=payload.directed)
    for i, (u, v) in enumerate(payload.edges):
        w = payload.weights[i] if payload.weights else 1.0
        algo.add_edge(u, v, w)
    return build_success_envelope(
        data={
            "num_nodes": algo.num_nodes,
            "density": algo.density(),
            "in_degrees": [algo.in_degree(i) for i in range(algo.num_nodes)],
            "out_degrees": [algo.out_degree(i) for i in range(algo.num_nodes)],
        },
        trace_id=trace_id,
    )


@router.post("/csr-csc")
def csr_csc_endpoint(payload: CsrCscDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoCsrCsc(num_nodes=payload.num_nodes, edges=payload.edges)
    return build_success_envelope(
        data={
            "num_nodes": algo.num_nodes,
            "num_edges": algo.num_edges,
            "row_ptrs": algo.row_ptrs,
            "col_indices": algo.col_indices,
            "values": algo.values,
        },
        trace_id=trace_id,
    )


@router.post("/dynamic-adjacency")
def dynamic_adjacency_endpoint(payload: DynamicAdjacencyDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoDynamicAdjacency[str]()
    for op in payload.operations:
        action = op.get("action")
        if action == "add_vertex":
            algo.add_vertex(op["vertex"])
        elif action == "add_edge":
            algo.add_edge(op["source"], op["target"], op.get("weight", 1.0))
        elif action == "remove_edge":
            algo.remove_edge(op["source"], op["target"])
        elif action == "remove_vertex":
            algo.remove_vertex(op["vertex"])
    return build_success_envelope(
        data={
            "vertex_count": algo.vertex_count(),
            "edge_count": algo.edge_count(),
            "vertices": list(algo.vertices()),
        },
        trace_id=trace_id,
    )


@router.post("/k2-tree")
def k2_tree_endpoint(payload: K2TreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoK2Tree(points=payload.points, size=payload.size, k=payload.k)
    return build_success_envelope(
        data={
            "tree_bits": algo.bit_vector,
            "leaves": algo.leaves,
            "height": algo.height,
        },
        trace_id=trace_id,
    )


@router.post("/rcm-reordering")
def rcm_reordering_endpoint(payload: RcmReorderingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoRcmReordering[str](payload.adjacency)
    ordering = algo.compute_rcm_order()
    bandwidth = algo.compute_bandwidth(ordering)
    return build_success_envelope(
        data={"rcm_ordering": ordering, "bandwidth": bandwidth},
        trace_id=trace_id,
    )


@router.post("/direction-optimizing-bfs")
def direction_optimizing_bfs_endpoint(payload: DirectionOptimizingBfsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    nodes = sorted(list(payload.adjacency.keys()))
    in_adj = {u: [] for u in nodes}
    for u, nbrs in payload.adjacency.items():
        for v in nbrs:
            if v not in in_adj:
                in_adj[v] = []
            in_adj[v].append(u)
    res = GraphAlgoDirectionOptimizingBfs.traverse(
        nodes=nodes,
        out_adjacency=payload.adjacency,
        in_adjacency=in_adj,
        start_node=payload.source,
        alpha=payload.alpha,
        beta=payload.beta,
    )
    return build_success_envelope(
        data=res,
        trace_id=trace_id,
    )


@router.post("/contraction-hierarchies")
def contraction_hierarchies_endpoint(payload: ContractionHierarchiesDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    ch = GraphAlgoContractionHierarchies[str](payload.adjacency)
    dist, path = ch.query(payload.source, payload.target)
    return build_success_envelope(
        data={"distance": dist, "path": path},
        trace_id=trace_id,
    )


@router.post("/hub-labeling")
def hub_labeling_endpoint(payload: HubLabelingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    hl = GraphAlgoHubLabeling[str](payload.adjacency)
    dist, hub = hl.query(payload.source, payload.target)
    return build_success_envelope(
        data={"distance": dist, "connecting_hub": hub},
        trace_id=trace_id,
    )


@router.post("/suurballe-disjoint-paths")
def suurballe_disjoint_paths_endpoint(payload: SuurballeDisjointPathsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoSuurballeDisjointPaths[str](payload.adjacency)
    paths = algo.find_disjoint_paths(payload.source, payload.target, k=payload.k)
    return build_success_envelope(
        data={"disjoint_paths": paths, "path_count": len(paths)},
        trace_id=trace_id,
    )


@router.post("/pareto-shortest-path")
def pareto_shortest_path_endpoint(payload: ParetoShortestPathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    pareto = GraphAlgoParetoShortestPath[str](payload.adjacency)
    front = pareto.find_pareto_front(payload.source, payload.target, max_front_size=payload.max_front_size)
    return build_success_envelope(
        data={"pareto_front": [(list(cost), path) for cost, path in front]},
        trace_id=trace_id,
    )


@router.post("/widest-bottleneck-path")
def widest_bottleneck_path_endpoint(payload: WidestBottleneckPathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    widest = GraphAlgoWidestBottleneckPath[str](payload.adjacency)
    cap, path = widest.find_widest_path(payload.source, payload.target)
    return build_success_envelope(
        data={"bottleneck_capacity": cap, "path": path},
        trace_id=trace_id,
    )


@router.post("/temporal-csa")
def temporal_csa_endpoint(payload: TemporalCsaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    csa = GraphAlgoTemporalCsaPath[str](payload.timetable_connections)
    earliest_arr, journey = csa.find_earliest_arrival(
        source=payload.source,
        target=payload.target,
        dep_time=payload.departure_time,
    )
    return build_success_envelope(
        data={"earliest_arrival": earliest_arr, "journey": journey},
        trace_id=trace_id,
    )


@router.post("/raptor-routing")
def raptor_routing_endpoint(payload: RaptorRoutingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    raptor = GraphAlgoRaptorRouting[str](
        routes=payload.routes,
        timetables=payload.timetables,
    )
    earliest_arr = raptor.earliest_arrival(
        source=payload.source,
        target=payload.target,
        dep_time=payload.departure_time,
        max_rounds=payload.max_rounds,
    )
    return build_success_envelope(
        data={"earliest_arrival": earliest_arr},
        trace_id=trace_id,
    )
