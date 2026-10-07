"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the Graph and Knowledge Graph Analytics Suite:
   - BFS & DFS graph traversal (ALGO-GRAPH-01, ALGO-GRAPH-02, ALGO-KG-63, ALGO-KG-64)
   - Dijkstra & A* shortest path routing (ALGO-GRAPH-03, ALGO-GRAPH-04, ALGO-KG-66, ALGO-KG-67)
   - Yen's K-Shortest Paths (ALGO-KG-68)
   - PageRank, Personalized PageRank, Degree, Betweenness, Harmonic & HITS Centrality (ALGO-GRAPH-05, ALGO-GRAPH-06, ALGO-KG-73..78)
   - Connected Components, Tarjan SCC, Louvain, Leiden, Label Propagation, K-Core (ALGO-GRAPH-07, ALGO-GRAPH-08, ALGO-KG-79..84)
   - Random Walk, Metapath Traversal, 2-Hop Labeling, Transitive Closure (ALGO-KG-69..72)
   - Subgraph isomorphism pattern matching (ALGO-GRAPH-09)
   - Database pushdown parameterized Cypher/GQL query plan generation endpoints for all algorithms

2. ZERO-INLINE-COMMENT DOCTRINE:
   No inline comments inside functions; all contracts and schemas documented in docblock.
================================================================================
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from ..dependencies import get_code_engine_service
from src.features.code_engine.algos.knowledge_graph.analytics import (
    KgAlgoAstarSearch,
    KgAlgoBfsTraversal,
    KgAlgoBidirectionalBfs,
    KgAlgoBrandesBetweenness,
    KgAlgoClosenessHarmonic,
    KgAlgoConnectedComponents,
    KgAlgoDegreeCentrality,
    KgAlgoDfsTraversal,
    KgAlgoDijkstraShortestPath,
    KgAlgoHitsCentrality,
    KgAlgoKCoreDecomposition,
    KgAlgoLabelPropagation,
    KgAlgoLeidenCommunity,
    KgAlgoLouvainCommunity,
    KgAlgoMetapathTraversal,
    KgAlgoPagerankCentrality,
    KgAlgoPersonalizedPagerank,
    KgAlgoRandomWalkRestart,
    KgAlgoTarjanScc,
    KgAlgoTransitiveClosure,
    KgAlgoTwoHopLabeling,
    KgAlgoYensKShortestPaths,
)

router = APIRouter()

# ==================== Core DTOs ====================

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


# ==================== Query Plan DTOs ====================

class GraphAstarQueryPlanDTO(BaseModel):
    mode: str = Field(default="projected", description="Query mode: 'projected' (GDS catalog) or 'procedure' (APOC)")
    source_id: str = Field(..., description="Unique source node identifier")
    target_id: str = Field(..., description="Unique target destination node identifier")
    graph_name: Optional[str] = Field(default="default_graph", description="Graph catalog name")
    rel_type: Optional[str] = Field(default="CONNECTED_TO", description="Relationship type")
    weight_prop: Optional[str] = Field(default="cost", description="Relationship weight property key")
    latitude_prop: Optional[str] = Field(default="latitude", description="Latitude coordinate key")
    longitude_prop: Optional[str] = Field(default="longitude", description="Longitude coordinate key")


class GraphTraversalQueryPlanDTO(BaseModel):
    start_node: str = Field(..., description="Root node identifier")
    max_depth: int = Field(default=3, description="Maximum traversal depth")


class GraphPairQueryPlanDTO(BaseModel):
    source_id: str = Field(..., description="Source node identifier")
    target_id: str = Field(..., description="Target destination node identifier")


class GraphCatalogQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")


class GraphDijkstraQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    source_id: str = Field(..., description="Source node identifier")
    target_id: Optional[str] = Field(default=None, description="Optional target destination node identifier")


class GraphYensQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    source_id: str = Field(..., description="Source node identifier")
    target_id: str = Field(..., description="Target node identifier")
    k: int = Field(default=3, description="Number of shortest paths to compute")


class GraphPageRankQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    damping_factor: float = Field(default=0.85, description="Damping factor")
    max_iterations: int = Field(default=20, description="Max iterations")
    tolerance: float = Field(default=1e-7, description="Convergence tolerance")


class GraphPersonalizedPageRankQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    seed_node: str = Field(..., description="Seed teleport origin node identifier")
    damping_factor: float = Field(default=0.85, description="Damping factor")
    max_iterations: int = Field(default=20, description="Max iterations")


class GraphDegreeQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    orientation: str = Field(default="NATURAL", description="Relationship orientation (NATURAL, REVERSE, UNDIRECTED)")


class GraphHitsQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    iterations: int = Field(default=15, description="HITS iterations")


class GraphKCoreQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    k: int = Field(default=2, description="Degree threshold k")


class GraphLabelPropagationQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    max_iterations: int = Field(default=10, description="Maximum iterations")


class GraphLouvainQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    max_levels: int = Field(default=10, description="Max hierarchical aggregation levels")
    max_iterations: int = Field(default=15, description="Max iterations per level")


class GraphLeidenQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    max_levels: int = Field(default=10, description="Max levels")
    gamma: float = Field(default=1.0, description="Resolution parameter gamma")


class GraphRandomWalkQueryPlanDTO(BaseModel):
    graph_name: str = Field(default="default_graph", description="GDS graph catalog name")
    start_node: str = Field(..., description="Start origin node")
    walk_length: int = Field(default=500, description="Walk step length")
    walks_per_node: int = Field(default=1, description="Walks per node")
    restart_probability: float = Field(default=0.15, description="Restart probability")


class GraphMetapathQueryPlanDTO(BaseModel):
    start_node: str = Field(..., description="Starting seed node")
    metapath: List[str] = Field(..., description="Ordered sequence of relationship type labels")
    max_hops: int = Field(default=10, description="Max hop traversal limit")


class GraphTransitiveClosureQueryPlanDTO(BaseModel):
    source_id: str = Field(..., description="Origin node identifier")
    max_depth: int = Field(default=5, description="Max reachability depth")


# ==================== Endpoints ====================

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


# ==================== Query Plan Endpoints ====================

@router.post("/algos/graph/astar-query-plan")
def graph_astar_query_plan_endpoint(payload: GraphAstarQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = KgAlgoAstarSearch()
    if payload.mode == "procedure":
        res = algo.build_procedure_query(
            source_id=payload.source_id,
            target_id=payload.target_id,
            rel_type=payload.rel_type or "CONNECTED_TO",
            weight_prop=payload.weight_prop or "cost",
            lat_prop=payload.latitude_prop or "latitude",
            lon_prop=payload.longitude_prop or "longitude",
        )
    else:
        res = algo.build_projected_graph_query(
            graph_name=payload.graph_name or "default_graph",
            source_id=payload.source_id,
            target_id=payload.target_id,
            latitude_prop=payload.latitude_prop or "latitude",
            longitude_prop=payload.longitude_prop or "longitude",
            weight_prop=payload.weight_prop or "cost",
        )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/bfs-query-plan")
def graph_bfs_query_plan_endpoint(payload: GraphTraversalQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoBfsTraversal().build_cypher_query(start_node=payload.start_node, max_depth=payload.max_depth)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/dfs-query-plan")
def graph_dfs_query_plan_endpoint(payload: GraphTraversalQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoDfsTraversal().build_cypher_query(start_node=payload.start_node, max_depth=payload.max_depth)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/bidirectional-bfs-query-plan")
def graph_bidirectional_bfs_query_plan_endpoint(payload: GraphPairQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoBidirectionalBfs().build_cypher_query(source_id=payload.source_id, target_id=payload.target_id)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/dijkstra-query-plan")
def graph_dijkstra_query_plan_endpoint(payload: GraphDijkstraQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoDijkstraShortestPath().build_cypher_query(
        graph_name=payload.graph_name,
        source_id=payload.source_id,
        target_id=payload.target_id,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/yens-query-plan")
def graph_yens_query_plan_endpoint(payload: GraphYensQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoYensKShortestPaths().build_cypher_query(
        graph_name=payload.graph_name,
        source_id=payload.source_id,
        target_id=payload.target_id,
        k=payload.k,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/pagerank-query-plan")
def graph_pagerank_query_plan_endpoint(payload: GraphPageRankQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoPagerankCentrality().build_cypher_query(
        graph_name=payload.graph_name,
        damping_factor=payload.damping_factor,
        max_iterations=payload.max_iterations,
        tolerance=payload.tolerance,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/personalized-pagerank-query-plan")
def graph_personalized_pagerank_query_plan_endpoint(payload: GraphPersonalizedPageRankQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoPersonalizedPagerank().build_cypher_query(
        graph_name=payload.graph_name,
        seed_node=payload.seed_node,
        damping_factor=payload.damping_factor,
        max_iterations=payload.max_iterations,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/degree-centrality-query-plan")
def graph_degree_centrality_query_plan_endpoint(payload: GraphDegreeQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoDegreeCentrality().build_cypher_query(
        graph_name=payload.graph_name,
        orientation=payload.orientation,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/betweenness-query-plan")
def graph_betweenness_query_plan_endpoint(payload: GraphCatalogQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoBrandesBetweenness().build_cypher_query(graph_name=payload.graph_name)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/harmonic-closeness-query-plan")
def graph_harmonic_closeness_query_plan_endpoint(payload: GraphCatalogQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoClosenessHarmonic().build_cypher_query(graph_name=payload.graph_name)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/hits-centrality-query-plan")
def graph_hits_centrality_query_plan_endpoint(payload: GraphHitsQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoHitsCentrality().build_cypher_query(graph_name=payload.graph_name, iterations=payload.iterations)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/connected-components-query-plan")
def graph_connected_components_query_plan_endpoint(payload: GraphCatalogQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoConnectedComponents().build_cypher_query(graph_name=payload.graph_name)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/tarjan-scc-query-plan")
def graph_tarjan_scc_query_plan_endpoint(payload: GraphCatalogQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoTarjanScc().build_cypher_query(graph_name=payload.graph_name)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/louvain-query-plan")
def graph_louvain_query_plan_endpoint(payload: GraphLouvainQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoLouvainCommunity().build_cypher_query(
        graph_name=payload.graph_name,
        max_levels=payload.max_levels,
        max_iterations=payload.max_iterations,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/leiden-query-plan")
def graph_leiden_query_plan_endpoint(payload: GraphLeidenQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoLeidenCommunity().build_cypher_query(
        graph_name=payload.graph_name,
        max_levels=payload.max_levels,
        gamma=payload.gamma,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/label-propagation-query-plan")
def graph_label_propagation_query_plan_endpoint(payload: GraphLabelPropagationQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoLabelPropagation().build_cypher_query(
        graph_name=payload.graph_name,
        max_iterations=payload.max_iterations,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/k-core-query-plan")
def graph_k_core_query_plan_endpoint(payload: GraphKCoreQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoKCoreDecomposition().build_cypher_query(
        graph_name=payload.graph_name,
        k=payload.k,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/random-walk-query-plan")
def graph_random_walk_query_plan_endpoint(payload: GraphRandomWalkQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoRandomWalkRestart().build_cypher_query(
        graph_name=payload.graph_name,
        start_node=payload.start_node,
        walk_length=payload.walk_length,
        walks_per_node=payload.walks_per_node,
        restart_probability=payload.restart_probability,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/metapath-query-plan")
def graph_metapath_query_plan_endpoint(payload: GraphMetapathQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoMetapathTraversal().build_cypher_query(
        start_node=payload.start_node,
        metapath=payload.metapath,
        max_hops=payload.max_hops,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/two-hop-query-plan")
def graph_two_hop_query_plan_endpoint(payload: GraphPairQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoTwoHopLabeling().build_cypher_query(
        source_id=payload.source_id,
        target_id=payload.target_id,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/graph/transitive-closure-query-plan")
def graph_transitive_closure_query_plan_endpoint(payload: GraphTransitiveClosureQueryPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    res = KgAlgoTransitiveClosure().build_cypher_query(
        source_id=payload.source_id,
        max_depth=payload.max_depth,
    )
    return build_success_envelope(data=res, trace_id=trace_id)
