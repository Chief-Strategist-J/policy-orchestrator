"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the 9 Layer 1 Graph Algorithms
   (ALGO-GRAPH-01 through ALGO-GRAPH-09):
   - BFS & DFS graph traversal (ALGO-GRAPH-01, ALGO-GRAPH-02)
   - Dijkstra & A* shortest path routing (ALGO-GRAPH-03, ALGO-GRAPH-04)
   - PageRank & Degree Centrality analysis (ALGO-GRAPH-05, ALGO-GRAPH-06)
   - Connected Components & Tarjan SCC detection (ALGO-GRAPH-07, ALGO-GRAPH-08)
   - Subgraph isomorphism pattern matching (ALGO-GRAPH-09)

2. ZERO-INLINE-COMMENT DOCTRINE:
   No inline comments inside functions; all contracts and schemas documented in docblock.
================================================================================
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from ..dependencies import get_code_engine_service

router = APIRouter()

class GraphBfsDTO(BaseModel):
    adjacency_list: Dict[str, List[str]] = Field(..., description="Graph adjacency list")
    start_node: str = Field(..., description="Starting traversal node")
    max_depth: int = Field(default=-1, description="Maximum traversal depth (-1 for unlimited)")


class GraphDfsDTO(BaseModel):
    adjacency_list: Dict[str, List[str]] = Field(..., description="Graph adjacency list")
    start_node: str = Field(..., description="Starting traversal node")
    max_depth: int = Field(default=-1, description="Maximum traversal depth (-1 for unlimited)")


class GraphDijkstraDTO(BaseModel):
    weighted_edges: List[Dict[str, Any]] = Field(..., description="List of {source, target, weight} objects")
    start_node: str = Field(..., description="Starting node")
    target_node: Optional[str] = Field(default=None, description="Optional target destination node")


class GraphAstarDTO(BaseModel):
    weighted_edges: List[Dict[str, Any]] = Field(..., description="List of {source, target, weight} objects")
    start_node: str = Field(..., description="Starting node")
    target_node: str = Field(..., description="Destination target node")
    heuristics: Optional[Dict[str, float]] = Field(default=None, description="Node heuristic estimates to target")


class GraphPageRankDTO(BaseModel):
    adjacency_list: Dict[str, List[str]] = Field(..., description="Graph adjacency list")
    damping_factor: float = Field(default=0.85, description="Random teleport damping factor")
    max_iterations: int = Field(default=100, description="Maximum power iterations")
    tolerance: float = Field(default=1e-6, description="Convergence threshold")


class GraphDegreeCentralityDTO(BaseModel):
    adjacency_list: Dict[str, List[str]] = Field(..., description="Graph adjacency list")
    normalized: bool = Field(default=True, description="Normalize scores by (N-1)")


class GraphConnectedComponentsDTO(BaseModel):
    edges: List[List[str]] = Field(..., description="List of [u, v] undirected edge pairs")
    nodes: Optional[List[str]] = Field(default=None, description="Optional full node list including isolated nodes")


class GraphTarjanSccDTO(BaseModel):
    adjacency_list: Dict[str, List[str]] = Field(..., description="Directed graph adjacency list")


class GraphSubgraphMatchDTO(BaseModel):
    target_graph: Dict[str, List[str]] = Field(..., description="Target host graph adjacency list")
    pattern_graph: Dict[str, List[str]] = Field(..., description="Pattern query graph adjacency list")
    max_matches: int = Field(default=100, description="Maximum matching mappings to return")

@router.post("/algos/graph/bfs")
def graph_bfs_endpoint(payload: GraphBfsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-01", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/dfs")
def graph_dfs_endpoint(payload: GraphDfsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-02", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/dijkstra")
def graph_dijkstra_endpoint(payload: GraphDijkstraDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-03", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/astar")
def graph_astar_endpoint(payload: GraphAstarDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-04", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/pagerank")
def graph_pagerank_endpoint(payload: GraphPageRankDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-05", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/degree-centrality")
def graph_degree_centrality_endpoint(payload: GraphDegreeCentralityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-06", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/connected-components")
def graph_connected_components_endpoint(payload: GraphConnectedComponentsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-07", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/tarjan-scc")
def graph_tarjan_scc_endpoint(payload: GraphTarjanSccDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-08", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/subgraph-match")
def graph_subgraph_match_endpoint(payload: GraphSubgraphMatchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-GRAPH-09", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)
