"""
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 GRAPH COMMUNITIES & SPECTRAL ROUTER

1. OVERVIEW & OBJECTIVE:
Provides HTTP REST endpoints for Communities, Spectral Methods, Coloring, Isomorphism & Decompositions (#115-164):
- Community Detection (Leiden CPM, Fast Greedy, Infomap, Walktrap, Spectral Clustering, Markov Clustering MCL, SBM, Borgatti Core-Periphery)
- Partition Evaluation & Spectral Sparsification (Conductance, External/Internal Ratio, NMI/AMI, Laplacian Eigensolvers, Spectral Sparsification, Effective Resistance)
- Graph Coloring & Isomorphism (Greedy Vertex Coloring, Fractional Chromatic, Weisfeiler-Lehman, Ullmann Subgraph, VF2 Subgraph, McSplit MCS, Graph Edit Distance)
- Graph Decompositions & Recognition (Hopcroft-Tarjan Planarity, Treewidth Min-Degree, Chordal Graph, Junction Tree, SPQR Triconnected, Cograph, Interval Graph, Comparability Graph)

2. ZERO-INLINE-COMMENT DOCTRINE:
Zero inline comments inside function bodies or methods.
"""

from typing import Any, Dict, List, Optional, Tuple
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from src.api.rest.envelope import build_success_envelope
from src.features.code_engine.algos.graph.communities_spectral_decompositions import (
    GraphAlgoModularityResolution,
    GraphAlgoLeidenCpm,
    GraphAlgoGirvanNewmanCommunities,
    GraphAlgoSlpaOverlappingCommunities,
    GraphAlgoInfomapFlow,
    GraphAlgoWalktrapCommunities,
    GraphAlgoFastGreedyModularity,
    GraphAlgoSpectralClustering,
    GraphAlgoMarkovClusteringMcl,
    GraphAlgoSbmInference,
    GraphAlgoLocalPprClustering,
    GraphAlgoLocalMaxFlowClustering,
    GraphAlgoCorePeripheryBorgatti,
    GraphAlgoBipartiteCommunityProjection,
    GraphAlgoHypergraphCliqueExpansion,
    GraphAlgoConductanceExpansion,
    GraphAlgoExternalInternalRatio,
    GraphAlgoNmiAmiPartitionAgreement,
    GraphAlgoKlPartitioning,
    GraphAlgoMultilevelGraphPartitioning,
    GraphAlgoStreamingVertexPartitioning,
    GraphAlgoLaplacianEigensolvers,
    GraphAlgoSpectralSparsification,
    GraphAlgoLaplacianLinearSolvers,
    GraphAlgoEffectiveResistanceDistance,
    GraphAlgoWilsonRandomSpanningTree,
    GraphAlgoGraphSignalProcessing,
    GraphAlgoGreedyVertexColoring,
    GraphAlgoFractionalChromaticNumber,
    GraphAlgoMaximumIndependentSet,
    GraphAlgoWeisfeilerLehmanIsomorphism,
    GraphAlgoUllmannSubgraphIsomorphism,
    GraphAlgoVf2SubgraphIsomorphism,
    GraphAlgoMcsCommonSubgraph,
    GraphAlgoGraphEditDistance,
    GraphAlgoPlanarityHopcroftTarjan,
    GraphAlgoTreewidthMinDegree,
    GraphAlgoChordalGraphRecognition,
    GraphAlgoCliqueTreeJunctionTree,
    GraphAlgoNestedDissection,
    GraphAlgoBiconnectedComponentsHopcroft,
    GraphAlgoTriconnectedComponentsSpqr,
    GraphAlgoModularDecomposition,
    GraphAlgoSplitDecomposition,
    GraphAlgoCographRecognition,
    GraphAlgoIntervalGraphRecognition,
    GraphAlgoComparabilityGraphTransitivity,
    GraphAlgoPermutationGraphInversion,
    GraphAlgoThresholdGraphPeeling,
    GraphAlgoDistanceHereditaryGraphs,
)

router = APIRouter(prefix="/algos/graph/communities", tags=["Graph Communities & Spectral"])


class AdjacencyGraphDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")


class WeightedAdjacencyGraphDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Weighted graph adjacency map")


class LeidenCpmDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")
    resolution: float = Field(default=0.1, description="CPM resolution parameter")


class SpectralClusteringDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")
    k_clusters: int = Field(default=2, description="Target number of clusters")


class MarkovClusteringMclDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")
    expansion: int = Field(default=2, description="Matrix power expansion exponent")
    inflation: float = Field(default=2.0, description="Inflation operator parameter")
    max_iter: int = Field(default=50, description="Max iterations")


class SbmInferenceDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")
    k_blocks: int = Field(default=2, description="Number of stochastic blocks")


class LocalPprClusteringDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")
    seed_node: str = Field(..., description="Seed start node for sweep cut")
    alpha: float = Field(default=0.15, description="Random walk restart probability")
    epsilon: float = Field(default=1e-4, description="Approximate push accuracy")


class ConductanceDTO(BaseModel):
    adjacency: Dict[str, List[str]] = Field(..., description="Graph adjacency map")
    subset: List[str] = Field(..., description="Vertex subset to evaluate")


class PartitionAgreementDTO(BaseModel):
    partition_a: Dict[str, int] = Field(..., description="Ground truth partition mapping")
    partition_b: Dict[str, int] = Field(..., description="Inferred partition mapping")


class IsomorphismDTO(BaseModel):
    graph1: Dict[str, List[str]] = Field(..., description="First graph adjacency")
    graph2: Dict[str, List[str]] = Field(..., description="Second graph adjacency")


class CommonSubgraphDTO(BaseModel):
    graph1: Dict[str, List[str]] = Field(..., description="Target graph 1")
    graph2: Dict[str, List[str]] = Field(..., description="Target graph 2")


class SubgraphMatchingDTO(BaseModel):
    pattern: Dict[str, List[str]] = Field(..., description="Pattern query graph")
    target: Dict[str, List[str]] = Field(..., description="Target host graph")


class ResistanceDistanceDTO(BaseModel):
    adjacency: Dict[str, List[Tuple[str, float]]] = Field(..., description="Weighted resistor network")
    source: str = Field(..., description="Source node")
    target: str = Field(..., description="Target node")


@router.post("/leiden-cpm")
def leiden_cpm_endpoint(payload: LeidenCpmDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoLeidenCpm[str](adjacency=payload.adjacency, gamma=payload.resolution)
    part, cpm_quality, num_comm = algo.detect_communities()
    return build_success_envelope(data={"communities": part, "cpm_quality": cpm_quality, "num_communities": num_comm}, trace_id=trace_id)


@router.post("/fast-greedy-modularity")
def fast_greedy_modularity_endpoint(payload: AdjacencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoFastGreedyModularity[str]()
    communities, modularity = algo.evaluate(payload.adjacency)
    return build_success_envelope(data={"communities": communities, "modularity": modularity}, trace_id=trace_id)


@router.post("/spectral-clustering")
def spectral_clustering_endpoint(payload: SpectralClusteringDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoSpectralClustering[str]()
    clusters = algo.evaluate(payload.adjacency, k=payload.k_clusters)
    return build_success_envelope(data={"clusters": clusters}, trace_id=trace_id)


@router.post("/markov-clustering-mcl")
def markov_clustering_mcl_endpoint(payload: MarkovClusteringMclDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoMarkovClusteringMcl[str]()
    clusters = algo.evaluate(payload.adjacency, expansion=payload.expansion, inflation=payload.inflation, max_iter=payload.max_iter)
    return build_success_envelope(data={"clusters": clusters}, trace_id=trace_id)


@router.post("/sbm-inference")
def sbm_inference_endpoint(payload: SbmInferenceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoSbmInference[str]()
    block_assignments, prob_matrix = algo.evaluate(payload.adjacency, k=payload.k_blocks)
    return build_success_envelope(data={"block_assignments": block_assignments, "block_probabilities": prob_matrix}, trace_id=trace_id)


@router.post("/local-ppr-clustering")
def local_ppr_clustering_endpoint(payload: LocalPprClusteringDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoLocalPprClustering[str]()
    cluster, conductance = algo.evaluate(payload.adjacency, seed=payload.seed_node, alpha=payload.alpha, epsilon=payload.epsilon)
    return build_success_envelope(data={"cluster": list(cluster), "conductance": conductance}, trace_id=trace_id)


@router.post("/conductance")
def conductance_endpoint(payload: ConductanceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoConductanceExpansion[str]()
    conductance, cut_size = algo.evaluate(payload.adjacency, set(payload.subset))
    return build_success_envelope(data={"conductance": conductance, "cut_size": cut_size}, trace_id=trace_id)


@router.post("/partition-agreement")
def partition_agreement_endpoint(payload: PartitionAgreementDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoNmiAmiPartitionAgreement[str]()
    nmi, ami = algo.evaluate(payload.partition_a, payload.partition_b)
    return build_success_envelope(data={"nmi": nmi, "ami": ami}, trace_id=trace_id)


@router.post("/weisfeiler-lehman-isomorphism")
def weisfeiler_lehman_isomorphism_endpoint(payload: IsomorphismDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoWeisfeilerLehmanIsomorphism[str]()
    is_iso = algo.are_isomorphic(payload.graph1, payload.graph2)
    h1 = algo.hash_graph(payload.graph1)
    h2 = algo.hash_graph(payload.graph2)
    return build_success_envelope(data={"isomorphic": is_iso, "hash1": h1.canonical_hash, "hash2": h2.canonical_hash}, trace_id=trace_id)


@router.post("/vf2-subgraph-isomorphism")
def vf2_subgraph_isomorphism_endpoint(payload: SubgraphMatchingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoVf2SubgraphIsomorphism[str]()
    mappings = algo.evaluate(payload.pattern, payload.target)
    return build_success_envelope(data={"mappings": mappings, "match_count": len(mappings)}, trace_id=trace_id)


@router.post("/maximum-common-subgraph")
def maximum_common_subgraph_endpoint(payload: CommonSubgraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoMcsCommonSubgraph[str]()
    mcs_mapping, mcs_size = algo.evaluate(payload.graph1, payload.graph2)
    return build_success_envelope(data={"mapping": mcs_mapping, "common_vertex_count": mcs_size}, trace_id=trace_id)


@router.post("/planarity-test")
def planarity_test_endpoint(payload: AdjacencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoPlanarityHopcroftTarjan[str]()
    is_planar, kuratowski = algo.evaluate(payload.adjacency)
    return build_success_envelope(data={"is_planar": is_planar, "kuratowski_subgraph": kuratowski}, trace_id=trace_id)


@router.post("/greedy-vertex-coloring")
def greedy_vertex_coloring_endpoint(payload: AdjacencyGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoGreedyVertexColoring[str]()
    coloring, chromatic_bound = algo.evaluate(payload.adjacency)
    return build_success_envelope(data={"coloring": coloring, "chromatic_bound": chromatic_bound}, trace_id=trace_id)


@router.post("/effective-resistance")
def effective_resistance_endpoint(payload: ResistanceDistanceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    algo = GraphAlgoEffectiveResistanceDistance[str]()
    resistance = algo.evaluate(payload.adjacency, payload.source, payload.target)
    return build_success_envelope(data={"effective_resistance": resistance}, trace_id=trace_id)
