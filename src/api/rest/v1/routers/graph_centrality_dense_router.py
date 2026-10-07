"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH CENTRALITY & DENSE STRUCTURES ROUTER

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Centrality Measures & Dense Subgraph Extraction (#65-114):
- Centrality: Brandes Betweenness, Approximate Betweenness, Katz, Eigenvector
- Dense Structures: K-Truss, Bron-Kerbosch Maximal Cliques, Densest Subgraph Peeling, Maximum Clique

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.graph.centrality_dense_structures import (
    GraphAlgoBrandesBetweenness,
    GraphAlgoApproxBetweenness,
    GraphAlgoKatzCentrality,
    GraphAlgoEigenvectorCentrality,
    GraphAlgoBronKerboschCliques,
    GraphAlgoKTrussDecomposition,
    GraphAlgoDensestSubgraph,
    GraphAlgoMaximumClique,
)

router = APIRouter(prefix="/algos/graph/centrality", tags=["Graph Centrality & Dense Structures"])


class AdjacencyGraphDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency list")


class WeightedAdjacencyGraphDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Weighted graph adjacency mapping")
    is_directed: bool = Field(default=False, description="Whether graph is directed")
    normalized: bool = Field(default=True, description="Whether to normalize betweenness scores")


class KatzCentralityDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency list")
    alpha: float = Field(default=0.1, description="Attenuation factor")
    beta: float = Field(default=1.0, description="Exogenous base weight")
    max_iter: int = Field(default=100, description="Max power iterations")
    tol: float = Field(default=1e-6, description="Convergence tolerance")


class EigenvectorCentralityDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency list")
    max_iter: int = Field(default=100, description="Max power iterations")
    tol: float = Field(default=1e-6, description="Convergence tolerance")
    use_non_backtracking: bool = Field(default=False, description="Enable non-backtracking damping")


@router.post("/betweenness")
def betweenness_centrality_endpoint(payload: WeightedAdjacencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoBrandesBetweenness[str](
        adjacency=payload.adjacency,
        is_directed=payload.is_directed,
        normalized=payload.normalized,
    )
    cb, eb = algo.compute_betweenness()
    eb_serializable = {f"{u}:{v}": val for (u, v), val in eb.items()}
    return build_success_envelope(
        data={"vertex_betweenness": cb, "edge_betweenness": eb_serializable},
        trace_id=trace_id,
    )


@router.post("/katz")
def katz_centrality_endpoint(payload: KatzCentralityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoKatzCentrality[str](
        adjacency=payload.adjacency,
        alpha=payload.alpha,
        beta=payload.beta,
        max_iter=payload.max_iter,
        tol=payload.tol,
    )
    scores, iters, converged = algo.compute_centrality()
    return build_success_envelope(
        data={"centrality": scores, "iterations": iters, "converged": converged},
        trace_id=trace_id,
    )


@router.post("/eigenvector")
def eigenvector_centrality_endpoint(payload: EigenvectorCentralityDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoEigenvectorCentrality[str](
        adjacency=payload.adjacency,
        max_iter=payload.max_iter,
        tol=payload.tol,
        use_non_backtracking=payload.use_non_backtracking,
    )
    scores, lambda_max, iters, converged = algo.compute_centrality()
    return build_success_envelope(
        data={
            "eigenvector_centrality": scores,
            "principal_eigenvalue": lambda_max,
            "iterations": iters,
            "converged": converged,
        },
        trace_id=trace_id,
    )


@router.post("/k-truss")
def k_truss_endpoint(payload: AdjacencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoKTrussDecomposition[str](payload.adjacency)
    edge_trussness, max_truss_k, counts = algo.compute_truss_decomposition()
    truss_serializable = {f"{u}:{v}": k for (u, v), k in edge_trussness.items()}
    return build_success_envelope(
        data={"edge_trussness": truss_serializable, "max_truss_k": max_truss_k, "truss_edge_counts": counts},
        trace_id=trace_id,
    )


@router.post("/bron-kerbosch-cliques")
def bron_kerbosch_cliques_endpoint(payload: AdjacencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoBronKerboschCliques[str](payload.adjacency)
    total_count, cliques, max_size = algo.enumerate_maximal_cliques()
    return build_success_envelope(
        data={"total_maximal_cliques": total_count, "maximal_cliques": cliques, "largest_clique_size": max_size},
        trace_id=trace_id,
    )


@router.post("/densest-subgraph")
def densest_subgraph_endpoint(payload: AdjacencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoDensestSubgraph[str](payload.adjacency)
    max_density, nodes, init_density = algo.compute_densest_subgraph()
    return build_success_envelope(
        data={"max_density": max_density, "densest_subgraph_nodes": nodes, "initial_density": init_density},
        trace_id=trace_id,
    )
