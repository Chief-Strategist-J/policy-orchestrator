"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH EMBEDDINGS & GNN ROUTER

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Embeddings, Advanced GNNs, Probabilistic Graphical Models & Causal Discovery (#215-300):
- Graph Representation & Embeddings (Spectral Embedding, LINE Proximity, Struc2Vec, HOPE, NetMF, ProNE)
- GNN Architectures (GIN Isomorphism, APPNP, SGC, Heterophily H2GCN, Positional/Structural Encodings, GraphMAE)
- Probabilistic Graphical Models & Inference (Belief Propagation, Loopy BP, Variable Elimination, Gibbs Sampling, Mean-Field Variational)
- Causal Discovery & Graphical Models (Bayesian Network Structure Learning, Bayes-Ball D-Separation, PC/FCI Causal Discovery, Do-Calculus Backdoor/Frontdoor, Graphical Lasso)
- Program Analysis & Ranking (TextRank, Harmonic Label Propagation, Andersen Points-To Analysis, Steensgaard Points-To Analysis)

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.graph.embeddings_gnn_learning import (
    GraphAlgoAdjacencySpectralEmbedding,
    GraphAlgoLineProximityEmbedding,
    GraphAlgoStruc2vecRoleEmbedding,
    GraphAlgoHopeDirectedEmbedding,
    GraphAlgoGrarepMultihopEmbedding,
    GraphAlgoNetmfMatrixFactorization,
    GraphAlgoProneSpectralPropagation,
    GraphAlgoPartitionedBiggraphEmbedding,
    GraphAlgoGraphAutoencoderGae,
    GraphAlgoGinIsomorphismNetwork,
    GraphAlgoAppnpPersonalizedPropagation,
    GraphAlgoSgcSimplifiedConvolution,
    GraphAlgoHeterophilyH2gcnGprgnn,
    GraphAlgoPositionalStructuralEncodings,
    GraphAlgoHigherOrderSubgraphGnn,
    GraphAlgoEquivariantGeometricGnn,
    GraphAlgoGraphmaeMaskedPretraining,
    GraphAlgoLayerwiseNeighborSampling,
    GraphAlgoBeliefPropagationTree,
    GraphAlgoLoopyBeliefPropagation,
    GraphAlgoMaxProductViterbiDecoding,
    GraphAlgoJunctionTreeInference,
    GraphAlgoVariableEliminationPgm,
    GraphAlgoGibbsSamplingPgm,
    GraphAlgoMeanFieldVariationalInference,
    GraphAlgoConditionalRandomFieldsCrf,
    GraphAlgoFactorGraphsMessagePassing,
    GraphAlgoBayesianNetworkStructureLearning,
    GraphAlgoDSeparationBayesBall,
    GraphAlgoConstraintCausalDiscoveryPcFci,
    GraphAlgoDoCalculusBackdoorFrontdoor,
    GraphAlgoGraphicalLassoPrecision,
    GraphAlgoNnDescentKnnGraph,
    GraphAlgoSimilarityGraphConstruction,
    GraphAlgoTextrankKeywordSentenceRanking,
    GraphAlgoHarmonicLabelPropagation,
    GraphAlgoPixieRandomWalkRecommendation,
    GraphAlgoP3alphaRp3betaRecommenders,
    GraphAlgoPathRankingAlgorithmPra,
    GraphAlgoHetesimMetapathRelevance,
    GraphAlgoPathsimMetapathSimilarity,
    GraphAlgoIsorankSpectralAlignment,
    GraphAlgoRegalEmbeddingAlignment,
    GraphAlgoGromovWassersteinMatching,
    GraphAlgoProximityGraphAnnRng,
    GraphAlgoNavigabilityKleinbergRouting,
    GraphAlgoIfdsIdeDataflowAnalysis,
    GraphAlgoCflDyckReachability,
    GraphAlgoAndersenPointsToAnalysis,
    GraphAlgoSteensgaardPointsToAnalysis,
)

router = APIRouter(prefix="/algos/graph/embeddings", tags=["Graph Embeddings & GNNs"])


class TextRankDTO(BaseModel):
    tokens_or_sentences: List[str] = Field(..., description="Ordered tokens or sentences")
    window_size: int = Field(default=3, description="Context co-occurrence sliding window")
    damping: float = Field(default=0.85, description="PageRank damping factor")
    max_iterations: int = Field(default=100, description="Max power iterations")
    tolerance: float = Field(default=1e-6, description="Convergence tolerance threshold")


class DSeparationDTO(BaseModel):
    dag_adjacency: Dict[str, List[str]] = Field(..., description="DAG adjacency mapping")
    set_x: List[str] = Field(..., description="Query variable set X")
    set_y: List[str] = Field(..., description="Query variable set Y")
    conditioning_set: List[str] = Field(..., description="Conditioned evidence variable set Z")


class AndersenPointsToDTO(BaseModel):
    statements: List[Tuple[str, str, Optional[str]]] = Field(
        ...,
        description="List of pointer statements: ('addr', p, x), ('copy', p, q), ('load', p, q), ('store', p, q)",
    )


class SteensgaardPointsToDTO(BaseModel):
    statements: List[Tuple[str, str, Optional[str]]] = Field(
        ...,
        description="List of pointer statements: ('addr', p, x), ('copy', p, q), ('load', p, q), ('store', p, q)",
    )


class HarmonicLabelPropDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency structure")
    labeled_nodes: Dict[str, int] = Field(..., description="Ground truth labels for known seeds")


class SpectralEmbeddingDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency structure")
    dimensions: int = Field(default=8, description="Target latent embedding dimension")


@router.post("/textrank")
def textrank_endpoint(payload: TextRankDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoTextrankKeywordSentenceRanking[str]()
    res = algo.evaluate(
        tokens_or_sentences=payload.tokens_or_sentences,
        window_size=payload.window_size,
        damping=payload.damping,
        max_iterations=payload.max_iterations,
        tolerance=payload.tolerance,
    )
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/d-separation")
def d_separation_endpoint(payload: DSeparationDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoDSeparationBayesBall[str]()
    res = algo.evaluate(
        dag_adjacency=payload.dag_adjacency,
        set_x=payload.set_x,
        set_y=payload.set_y,
        conditioning_set=payload.conditioning_set,
    )
    return build_success_envelope(
        data={
            "is_d_separated": res["is_d_separated"],
            "reachable_nodes": list(res["reachable_nodes"]),
            "connected_target_nodes": res["connected_target_nodes"],
        },
        trace_id=trace_id,
    )


@router.post("/andersen-points-to")
def andersen_points_to_endpoint(payload: AndersenPointsToDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoAndersenPointsToAnalysis[str]()
    res = algo.evaluate(payload.statements)
    pts_serializable = {k: list(v) for k, v in res["points_to_sets"].items()}
    graph_serializable = {k: list(v) for k, v in res["constraint_graph"].items()}
    return build_success_envelope(
        data={
            "points_to_sets": pts_serializable,
            "constraint_graph": graph_serializable,
            "iterations": res["iterations"],
        },
        trace_id=trace_id,
    )


@router.post("/steensgaard-points-to")
def steensgaard_points_to_endpoint(payload: SteensgaardPointsToDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoSteensgaardPointsToAnalysis[str]()
    res = algo.evaluate(payload.statements)
    pts_serializable = {k: list(v) if isinstance(v, (set, list)) else v for k, v in res["points_to_sets"].items()}
    return build_success_envelope(
        data={"points_to_sets": pts_serializable, "equivalence_classes": res.get("equivalence_classes", {})},
        trace_id=trace_id,
    )


@router.post("/harmonic-label-propagation")
def harmonic_label_propagation_endpoint(payload: HarmonicLabelPropDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoHarmonicLabelPropagation[str]()
    predictions = algo.evaluate(payload.adjacency, payload.labeled_nodes)
    return build_success_envelope(data={"predicted_labels": predictions}, trace_id=trace_id)
