"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH CONNECTIVITY & FLOWS ROUTER

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Connectivity, Cuts, Matching & Network Flows (#34-64):
- Minimum Spanning Trees (Boruvka, Kruskal, Prim, Edmonds Directed Arborescence)
- Biconnectivity & Bridges (Tarjan Bridge/Articulation, Biconnected Components, Dominator Tree)
- Max Flow & Min Cut (Edmonds-Karp, Dinic, Push-Relabel, Karger Min-Cut, Stoer-Wagner)
- Bipartite & General Matching (Hopcroft-Karp, Edmonds Blossom Matching)
- Min-Cost Max-Flow (Successive Shortest Path)

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.graph.connectivity_flows import (
    GraphAlgoBoruvkaMst,
    GraphAlgoEdmondsArborescence,
    GraphAlgoBridgesArticulationPoints,
    GraphAlgoDominatorTree,
    GraphAlgoEdmondsKarpMaxFlow,
    GraphAlgoDinicMaxFlow,
    GraphAlgoPushRelabel,
    GraphAlgoKargerMinCut,
    GraphAlgoStoerWagnerMinCut,
    GraphAlgoHopcroftKarpMatching,
    GraphAlgoEdmondsBlossomMatching,
    GraphAlgoMinCostFlow,
)

router = APIRouter(prefix="/algos/graph/flows", tags=["Graph Connectivity & Network Flows"])


class BoruvkaMstDTO(BaseModel):
    nodes: List[str] = Field(..., description="List of vertices")
    edges: List[Tuple[str, str, float]] = Field(..., description="Weighted edge triplets (u, v, weight)")


class EdmondsArborescenceDTO(BaseModel):
    nodes: Optional[List[str]] = Field(default=None, description="Optional explicit vertices")
    edges: List[Tuple[str, str, float]] = Field(..., description="Directed weighted edges (u, v, weight)")
    root: str = Field(..., description="Designated branching root vertex")


class BridgesArticulationDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Undirected graph adjacency list")


class DominatorTreeDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Directed flowgraph adjacency mapping")
    root: str = Field(..., description="Flowgraph root node")


class MaxFlowDTO(BaseModel):
    edges: List[Tuple[str, str, float]] = Field(..., description="Capacitated network edges (u, v, cap)")
    source: str = Field(..., description="Source node")
    sink: str = Field(..., description="Sink node")


class KargerMinCutDTO(BaseModel):
    edges: List[Tuple[str, str]] = Field(..., description="Undirected multigraph edges (u, v)")
    nodes: Optional[List[str]] = Field(default=None, description="Optional vertex list")
    num_trials: int = Field(default=20, description="Number of randomized contraction trials")
    seed: int = Field(default=42, description="Random seed")


class StoerWagnerDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Undirected weighted graph adjacency")


class HopcroftKarpDTO(BaseModel):
    left_nodes: List[str] = Field(..., description="Left bipartite partition nodes")
    right_nodes: List[str] = Field(..., description="Right bipartite partition nodes")
    adjacency: Dict[str, List[str]] = Field(..., description="Bipartite graph edges from left to right")


class BlossomMatchingDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="General undirected graph adjacency map")


class MinCostFlowDTO(BaseModel):
    edges: List[Tuple[str, str, float, float]] = Field(..., description="Edges as (u, v, capacity, unit_cost)")
    source: str = Field(..., description="Source node")
    sink: str = Field(..., description="Sink node")
    target_flow: float = Field(..., description="Requested flow volume")


@router.post("/boruvka-mst")
def boruvka_mst_endpoint(payload: BoruvkaMstDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoBoruvkaMst[str](edges=payload.edges, nodes=payload.nodes)
    total_weight, mst_edges = algo.compute_mst()
    return build_success_envelope(
        data={"mst_edges": mst_edges, "total_weight": total_weight},
        trace_id=trace_id,
    )


@router.post("/edmonds-arborescence")
def edmonds_arborescence_endpoint(payload: EdmondsArborescenceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoEdmondsArborescence[str](edges=payload.edges, nodes=payload.nodes)
    total_weight, arb_edges = algo.compute_arborescence(payload.root)
    return build_success_envelope(
        data={"arborescence_edges": arb_edges, "total_weight": total_weight},
        trace_id=trace_id,
    )


@router.post("/bridges-articulation")
def bridges_articulation_endpoint(payload: BridgesArticulationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoBridgesArticulationPoints[str](payload.adjacency)
    art_pts, bridges = algo.analyze()
    return build_success_envelope(
        data={"articulation_points": list(art_pts), "bridges": bridges},
        trace_id=trace_id,
    )


@router.post("/dominator-tree")
def dominator_tree_endpoint(payload: DominatorTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoDominatorTree[str](payload.adjacency)
    idom, dom_tree, frontiers = algo.compute_dominators(payload.root)
    frontiers_serializable = {k: list(v) for k, v in frontiers.items()}
    return build_success_envelope(
        data={
            "immediate_dominators": idom,
            "dominator_tree": dom_tree,
            "dominance_frontiers": frontiers_serializable,
        },
        trace_id=trace_id,
    )


@router.post("/edmonds-karp-max-flow")
def edmonds_karp_max_flow_endpoint(payload: MaxFlowDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoEdmondsKarpMaxFlow[str]()
    for u, v, cap in payload.edges:
        algo.add_edge(u, v, cap)
    max_flow, flow_map = algo.compute_max_flow(payload.source, payload.sink)
    flow_serializable = {f"{u}:{v}": val for (u, v), val in flow_map.items()}
    return build_success_envelope(
        data={"max_flow": max_flow, "flow_map": flow_serializable},
        trace_id=trace_id,
    )


@router.post("/dinic-max-flow")
def dinic_max_flow_endpoint(payload: MaxFlowDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoDinicMaxFlow[str]()
    for u, v, cap in payload.edges:
        algo.add_edge(u, v, cap)
    max_flow, flow_map = algo.compute_max_flow(payload.source, payload.sink)
    flow_serializable = {f"{u}:{v}": val for (u, v), val in flow_map.items()}
    return build_success_envelope(
        data={"max_flow": max_flow, "flow_map": flow_serializable},
        trace_id=trace_id,
    )


@router.post("/push-relabel-max-flow")
def push_relabel_max_flow_endpoint(payload: MaxFlowDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoPushRelabel[str]()
    for u, v, cap in payload.edges:
        algo.add_edge(u, v, cap)
    max_flow, flow_map = algo.compute_max_flow(payload.source, payload.sink)
    flow_serializable = {f"{u}:{v}": val for (u, v), val in flow_map.items()}
    return build_success_envelope(
        data={"max_flow": max_flow, "flow_map": flow_serializable},
        trace_id=trace_id,
    )


@router.post("/karger-min-cut")
def karger_min_cut_endpoint(payload: KargerMinCutDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoKargerMinCut[str](edges=payload.edges, nodes=payload.nodes)
    min_cut_weight, part_a, part_b = algo.compute_min_cut(num_trials=payload.num_trials, seed=payload.seed)
    return build_success_envelope(
        data={
            "min_cut_size": min_cut_weight,
            "partition_a": list(part_a),
            "partition_b": list(part_b),
        },
        trace_id=trace_id,
    )


@router.post("/stoer-wagner-min-cut")
def stoer_wagner_min_cut_endpoint(payload: StoerWagnerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoStoerWagnerMinCut[str](payload.adjacency)
    min_cut_weight, part_a, part_b = algo.compute_min_cut()
    return build_success_envelope(
        data={
            "min_cut_weight": min_cut_weight,
            "partition_a": list(part_a),
            "partition_b": list(part_b),
        },
        trace_id=trace_id,
    )


@router.post("/hopcroft-karp-matching")
def hopcroft_karp_matching_endpoint(payload: HopcroftKarpDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoHopcroftKarpMatching[str, str](
        left_nodes=payload.left_nodes,
        right_nodes=payload.right_nodes,
        adjacency=payload.adjacency,
    )
    matching_size, matching_pairs = algo.compute_maximum_matching()
    return build_success_envelope(
        data={"matching_size": matching_size, "matching_pairs": matching_pairs},
        trace_id=trace_id,
    )


@router.post("/blossom-matching")
def blossom_matching_endpoint(payload: BlossomMatchingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoEdmondsBlossomMatching[str](payload.adjacency)
    matching_size, matching_pairs = algo.compute_maximum_matching()
    return build_success_envelope(
        data={"matching_size": matching_size, "matching_pairs": matching_pairs},
        trace_id=trace_id,
    )


@router.post("/min-cost-flow")
def min_cost_flow_endpoint(payload: MinCostFlowDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoMinCostFlow[str]()
    for u, v, cap, cost in payload.edges:
        algo.add_edge(u, v, cap, cost)
    total_cost, achieved_flow, flow_map = algo.compute_min_cost_flow(
        source=payload.source,
        sink=payload.sink,
        target_flow=payload.target_flow,
    )
    flow_serializable = {f"{u}:{v}": val for (u, v), val in flow_map.items()}
    return build_success_envelope(
        data={
            "total_cost": total_cost,
            "achieved_flow": achieved_flow,
            "flow_map": flow_serializable,
        },
        trace_id=trace_id,
    )
