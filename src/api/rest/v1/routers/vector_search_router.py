"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 VECTOR SEARCH ALGORITHM ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   Encapsulates HTTP REST endpoints for the Vector Search Algorithms
   (ALGO-VEC-SRCH-51 through ALGO-VEC-SRCH-110):
   - Exact kNN Brute-Force & SIMD Distance Kernels (ALGO-VEC-SRCH-51..52)
   - Heap & Radix Top-k Selection (ALGO-VEC-SRCH-53..54)
   - Early Abandoning & Metric Pivot Pruning (ALGO-VEC-SRCH-55..56)
   - Spatial Trees (KD-Tree, Ball Tree, VP-Tree, RP-Forest) (ALGO-VEC-SRCH-57..60)
   - Quantized Indexes (IVF, IVF-PQ, nprobe-tune, IMI) (ALGO-VEC-SRCH-61..64)
   - Proximity Graphs (NSW, HNSW-Search, HNSW-Insert, Beam Search, Vamana, RobustPrune, NSG, CAGRA) (ALGO-VEC-SRCH-65..72)
   - Graph Maintenance (Entry Point, Connectivity Repair, Filtered DiskANN, SPANN) (ALGO-VEC-SRCH-73..76)
   - Locality Sensitive Hashing (Random Hyperplane, Multi-Probe, E2LSH) (ALGO-VEC-SRCH-77..79)
   - Hybrid Search & Fusion (BM25, Sparse-Dense, RRF, Convex Fusion, MMR, Range Search) (ALGO-VEC-SRCH-85..90)
   - Re-ranking & Funnels (MaxSim, Multi-Query, Rescore, Cross-Encoder, Multi-Stage Funnel, LLM Listwise) (ALGO-VEC-SRCH-91..96)
   - Routing, Caching & Distributed Operations (HyDE, Query Routing, Scatter-Gather, Partition Routing, Load Balancer, Hedged Requests, K-Way Merge, Query Cache, Semantic Cache, Batching, Memory Tiering, Disk Scheduler, Admission Control, Autotune) (ALGO-VEC-SRCH-97..110)

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

class VecSearchBruteForceGemmDTO(BaseModel):
    database_vectors: List[List[float]] = Field(..., description="Database vectors matrix (N x D)")
    query_vectors: List[List[float]] = Field(..., description="Query vectors matrix (Q x D)")
    k: int = Field(default=10, description="Top-k neighbors")
    metric: str = Field(default="l2", description="Distance metric ('l2', 'dot', 'cosine')")
    vector_ids: Optional[List[str]] = Field(default=None, description="Optional vector IDs")


class VecSearchSimdDistanceDTO(BaseModel):
    vector_a: List[float] = Field(..., description="First vector")
    vector_b: List[float] = Field(..., description="Second vector")
    metric: str = Field(default="l2", description="Metric ('l2', 'dot', 'cosine', 'hamming')")


class VecSearchHeapTopKDTO(BaseModel):
    candidates: List[Dict[str, Any]] = Field(..., description="Candidate objects")
    k: int = Field(default=10, description="Top-k items")
    score_key: str = Field(default="score", description="Score dictionary key")
    order: str = Field(default="desc", description="Sort order ('desc' or 'asc')")
    id_key: str = Field(default="id", description="ID dictionary key")


class VecSearchRadixTopKDTO(BaseModel):
    scores: List[float] = Field(..., description="Array of scores")
    k: int = Field(default=10, description="Top-k scores")
    ids: Optional[List[str]] = Field(default=None, description="Optional element IDs")
    largest: bool = Field(default=True, description="Pick largest or smallest")


class VecSearchEarlyAbandonDTO(BaseModel):
    database_vectors: List[List[float]] = Field(..., description="Database vectors")
    query_vector: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchPivotPruneDTO(BaseModel):
    database_vectors: List[List[float]] = Field(..., description="Database vectors")
    pivots: List[List[float]] = Field(..., description="Reference pivot vectors")
    query_vector: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchKdTreeDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Spatial vectors")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchBallTreeDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Spatial vectors")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    leaf_size: int = Field(default=16, description="Leaf size")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchVpTreeDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Metric vectors")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchRpForestDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    num_trees: int = Field(default=5, description="Number of trees")
    max_leaf_size: int = Field(default=32, description="Max leaf size")
    search_k: int = Field(default=100, description="Nodes to inspect")
    seed: int = Field(default=42, description="Random seed")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchIvfDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    num_clusters: int = Field(default=4, description="Coarse clusters")
    nprobe: int = Field(default=2, description="Centroids to probe")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchIvfPqDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    num_clusters: int = Field(default=4, description="Coarse clusters")
    nprobe: int = Field(default=2, description="Centroids to probe")
    subspaces: int = Field(default=2, description="Sub-vector quantizers")
    codebook_size: int = Field(default=4, description="Codebook centroids")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchNprobeTunerDTO(BaseModel):
    database_vectors: List[List[float]] = Field(..., description="Database vectors")
    sample_queries: List[List[float]] = Field(..., description="Sample queries")
    target_recall: float = Field(default=0.9, description="Target recall")
    k: int = Field(default=5, description="Top-k")
    num_clusters: int = Field(default=8, description="Clusters")
    nprobe_candidates: Optional[List[int]] = Field(default=None, description="Candidates to test")


class VecSearchInvertedMultiIndexDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matches")
    codebook_k1: int = Field(default=4, description="First codebook size")
    codebook_k2: int = Field(default=4, description="Second codebook size")
    max_cells_to_probe: int = Field(default=4, description="Max cells to probe")
    vector_ids: Optional[List[str]] = Field(default=None, description="Vector IDs")


class VecSearchNswDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    max_edges: int = Field(default=6, description="Max edges per node")
    num_attempts: int = Field(default=3, description="Routing attempts")


class VecSearchHnswSearchDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    layers: List[Dict[str, Any]] = Field(..., description="Hierarchical graph layers")
    entry_point: int = Field(default=0, description="Top-layer entry point")
    top_layer: int = Field(default=0, description="Top layer level")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k")
    ef: int = Field(default=16, description="Beam exploration size ef >= k")


class VecSearchHnswInsertDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    m: int = Field(default=4, description="Connections per element")
    ef_construction: int = Field(default=16, description="Construction beam size")
    m_max_0: int = Field(default=8, description="Max connections at layer 0")
    ml: float = Field(default=0.62, description="Layer generation normalization factor")


class VecSearchBeamSearchDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Metric vectors")
    adjacency: Dict[str, List[int]] = Field(..., description="Graph adjacency map")
    start_nodes: List[int] = Field(default=[0], description="Starting entry points")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k")
    ef: int = Field(default=16, description="Beam size ef")


class VecSearchVamanaDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    r_max_degree: int = Field(default=8, description="Max out-degree")
    l_search_list_size: int = Field(default=16, description="Search list size L")
    alpha: float = Field(default=1.2, description="Distance scaling factor alpha")


class VecSearchRobustPruneDTO(BaseModel):
    point: List[float] = Field(..., description="Target reference vector")
    candidate_vectors: List[List[float]] = Field(..., description="Candidate neighbor vectors")
    candidate_ids: Optional[List[int]] = Field(default=None, description="Candidate identifier list")
    alpha: float = Field(default=1.2, description="Diversity threshold parameter alpha")
    r_max_degree: int = Field(default=64, description="Maximum allowed out-degree R")


class VecSearchNsgDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    r_max_degree: int = Field(default=8, description="Max out-degree R")
    candidate_pool_size: int = Field(default=16, description="Initial candidate pool size")


class VecSearchCagraDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    fixed_degree: int = Field(default=6, description="Fixed regular degree")
    search_width: int = Field(default=8, description="Search width")


class VecSearchEntryPointDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    strategy: str = Field(default="query_adaptive", description="Strategy ('medoid', 'multi_seed', 'query_adaptive')")
    num_seeds: int = Field(default=4, description="Number of seed entry points")


class VecSearchConnectivityRepairDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    adjacency: Dict[str, List[int]] = Field(..., description="Graph adjacency map")
    entry_points: List[int] = Field(default=[0], description="Seed entry point indices")


class VecSearchFilteredDiskannDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    labels: List[str] = Field(..., description="Metadata labels per vector")
    query: List[float] = Field(..., description="Query vector")
    target_label: str = Field(..., description="Target metadata label filter")
    k: int = Field(default=5, description="Top-k")
    ef_search: int = Field(default=16, description="Beam exploration size ef")
    r_max_degree: int = Field(default=8, description="Max degree R")


class VecSearchSpannDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    num_centroids: int = Field(default=4, description="Number of centroids")
    nprobe: int = Field(default=2, description="Centroids to probe")
    slack_factor: float = Field(default=1.2, description="Boundary duplication slack epsilon")


class VecSearchRandomHyperplaneLshDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    num_bits: int = Field(default=4, description="Bits per hash table")
    num_tables: int = Field(default=3, description="Number of hash tables")
    seed: int = Field(default=42, description="Random seed")


class VecSearchMultiProbeLshDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    num_bits: int = Field(default=6, description="Number of hyperplane bits")
    probe_budget: int = Field(default=4, description="Multi-probe bucket budget")
    seed: int = Field(default=42, description="Random seed")


class VecSearchE2LshDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: Optional[List[float]] = Field(default=None, description="Query vector")
    k: int = Field(default=5, description="Top-k")
    slot_width_w: float = Field(default=4.0, description="Quantization slot width w")
    num_projections_m: int = Field(default=4, description="Number of projections m")
    num_tables_l: int = Field(default=3, description="Number of tables L")
    seed: int = Field(default=42, description="Random seed")

class VecSearchBM25DTO(BaseModel):
    corpus: List[str] = Field(..., description="Document text corpus")
    query: str = Field(..., description="Query search string")
    k: int = Field(default=5, description="Top-k documents")
    k1: float = Field(default=1.5, description="Term frequency saturation")
    b: float = Field(default=0.75, description="Document length normalization")


class VecSearchSparseDenseHybridDTO(BaseModel):
    dense_results: List[Dict[str, Any]] = Field(..., description="Dense retrieval ranked matches")
    sparse_results: List[Dict[str, Any]] = Field(..., description="Sparse lexical ranked matches")
    alpha: float = Field(default=0.5, description="Dense score weight multiplier")
    k: int = Field(default=5, description="Top-k fused matches")


class VecSearchRRFDTO(BaseModel):
    rankings: List[List[Dict[str, Any]]] = Field(..., description="Ranked candidate lists")
    k_rrf: int = Field(default=60, description="RRF constant")
    top_k: int = Field(default=5, description="Top-k fused candidates")


class VecSearchConvexScoreFusionDTO(BaseModel):
    score_lists: List[List[Dict[str, Any]]] = Field(..., description="Ranked score lists")
    weights: Optional[List[float]] = Field(default=None, description="Per-list convex weights")
    norm_method: str = Field(default="minmax", description="Score normalization method")
    top_k: int = Field(default=5, description="Top-k fused candidates")


class VecSearchMMRDTO(BaseModel):
    candidate_vectors: List[List[float]] = Field(..., description="Candidate embeddings")
    candidate_ids: List[Any] = Field(..., description="Candidate identifiers")
    query_vector: List[float] = Field(..., description="Query embedding vector")
    lambda_mult: float = Field(default=0.7, description="Relevance vs diversity trade-off")
    k: int = Field(default=5, description="Top-k diversified candidates")


class VecSearchRangeSearchDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    query: List[float] = Field(..., description="Query vector")
    radius: float = Field(default=1.0, description="Search distance/similarity radius")
    max_results: int = Field(default=100, description="Maximum matches to return")
    metric: str = Field(default="l2", description="Distance metric")


class VecSearchMaxSimDTO(BaseModel):
    document_token_vectors: List[List[List[float]]] = Field(..., description="Document token embedding matrices")
    query_token_vectors: List[List[float]] = Field(..., description="Query token embedding vectors")
    k: int = Field(default=5, description="Top-k documents")


class VecSearchMultiQueryExpansionDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Corpus vectors")
    expanded_queries: List[List[float]] = Field(..., description="List of expanded query vectors")
    aggregation: str = Field(default="rrf", description="Fusion aggregation method")
    k: int = Field(default=5, description="Top-k candidates")


class VecSearchFullPrecisionRescoreDTO(BaseModel):
    candidate_ids: List[Any] = Field(..., description="Candidate IDs from quantized first stage")
    full_precision_vectors: Dict[str, List[float]] = Field(..., description="Exact vectors keyed by ID")
    query_vector: List[float] = Field(..., description="Query vector")
    metric: str = Field(default="l2", description="Distance metric")
    top_k: int = Field(default=5, description="Top-k rescored candidates")


class VecSearchCrossEncoderRerankDTO(BaseModel):
    query: str = Field(..., description="Query string")
    candidates: List[Dict[str, Any]] = Field(..., description="First-stage retrieved candidates")
    top_k: int = Field(default=5, description="Top-k reranked candidates")


class VecSearchMultiStageFunnelDTO(BaseModel):
    stage1_candidates: List[Dict[str, Any]] = Field(..., description="Stage 1 coarse candidate set")
    stage2_top_m: int = Field(default=20, description="Stage 2 rescore pool size")
    stage3_top_k: int = Field(default=5, description="Stage 3 final pool size")


class VecSearchLLMListwiseRerankDTO(BaseModel):
    query: str = Field(..., description="User query")
    candidates: List[Dict[str, Any]] = Field(..., description="Candidate passages with id and text")
    simulated_llm_response: Optional[str] = Field(default=None, description="Simulated LLM ranking output")
    top_k: int = Field(default=5, description="Top-k reranked candidates")


class VecSearchHyDEDTO(BaseModel):
    corpus_vectors: List[List[float]] = Field(..., description="Document vectors")
    query_vector: List[float] = Field(..., description="Original query vector")
    hypothetical_vectors: List[List[float]] = Field(..., description="Vectors of hypothetical answer passages")
    query_weight: float = Field(default=0.5, description="Original query weight")
    k: int = Field(default=5, description="Top-k candidates")


class VecSearchQueryRoutingDTO(BaseModel):
    query: str = Field(..., description="Incoming user query")
    available_routes: Dict[str, Any] = Field(..., description="Available routes and route metadata")


class VecSearchScatterGatherDTO(BaseModel):
    shard_results: Dict[str, List[Dict[str, Any]]] = Field(..., description="Results per shard")
    top_k: int = Field(default=5, description="Global top-k results")


class VecSearchPartitionAwareRoutingDTO(BaseModel):
    centroids: List[List[float]] = Field(..., description="Partition cluster centroids")
    centroid_to_shard_map: Dict[str, str] = Field(..., description="Centroid index to shard map")
    query_vector: List[float] = Field(..., description="Query vector")
    num_target_shards: int = Field(default=2, description="Number of target shards to query")


class VecSearchReplicationLoadBalancerDTO(BaseModel):
    replicas: List[Dict[str, Any]] = Field(..., description="List of replica node status objects")
    strategy: str = Field(default="least_loaded", description="Selection strategy: round_robin, least_loaded, lowest_latency")
    counter: int = Field(default=0, description="Round-robin sequence counter")


class VecSearchHedgedRequestsDTO(BaseModel):
    primary_latency_ms: float = Field(..., description="Observed primary replica latency in ms")
    backup_latency_ms: float = Field(..., description="Backup replica latency in ms")
    hedge_delay_threshold_ms: float = Field(default=50.0, description="Hedge trigger delay in ms")
    is_read_only: bool = Field(default=True, description="Whether request is strictly read-only")


class VecSearchKWayMergeDTO(BaseModel):
    shard_sorted_lists: List[List[Dict[str, Any]]] = Field(..., description="Sorted result lists from each shard")
    k: int = Field(default=5, description="Global top-k items")
    is_distance: bool = Field(default=False, description="True if lower score indicates better match")


class VecSearchQueryCacheDTO(BaseModel):
    cache_store: Dict[str, Any] = Field(default_factory=dict, description="In-memory cache dict")
    query: str = Field(..., description="Query string")
    tenant_id: str = Field(..., description="Tenant identifier")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Query filters")
    index_version: str = Field(..., description="Vector index version")
    results: Optional[List[Dict[str, Any]]] = Field(default=None, description="Search results to cache")
    ttl_seconds: int = Field(default=300, description="Cache entry TTL")
    max_size: int = Field(default=1000, description="Maximum cache size")


class VecSearchSemanticCacheDTO(BaseModel):
    cached_entries: List[Dict[str, Any]] = Field(..., description="List of cached query objects with embedding")
    query_vector: List[float] = Field(..., description="Query embedding vector")
    tenant_id: str = Field(..., description="Tenant identifier")
    similarity_threshold: float = Field(default=0.95, description="Cosine similarity hit threshold")


class VecSearchQueryBatchingDTO(BaseModel):
    pending_queries: List[Dict[str, Any]] = Field(..., description="List of pending query objects")
    max_batch_size: int = Field(default=32, description="Maximum batch size")
    max_latency_ms: float = Field(default=5.0, description="Maximum wait window in ms")


class VecSearchMemoryTieringDTO(BaseModel):
    components: List[Dict[str, Any]] = Field(..., description="Index memory components")
    ram_budget_mb: float = Field(default=1024.0, description="Total RAM budget in MB")


class VecSearchDiskIOSchedulerDTO(BaseModel):
    requested_node_ids: List[int] = Field(..., description="Graph node IDs to read from disk")
    bytes_per_node: int = Field(default=4096, description="Bytes per node record")
    cached_nodes: Optional[List[int]] = Field(default=None, description="Node IDs already cached in RAM")
    page_size_bytes: int = Field(default=4096, description="Underlying OS page size in bytes")
    max_batch_size: int = Field(default=16, description="Maximum concurrent beam read batch")


class VecSearchAdmissionControlDTO(BaseModel):
    current_tokens: float = Field(default=100.0, description="Tokens currently in bucket")
    max_tokens: float = Field(default=100.0, description="Bucket capacity")
    refill_rate_per_sec: float = Field(default=10.0, description="Token refill rate per second")
    last_refill_timestamp: float = Field(default=0.0, description="Timestamp of last token refill")
    current_concurrency: int = Field(default=0, description="Currently active concurrent requests")
    max_concurrency: int = Field(default=50, description="Max allowed concurrent requests")
    request_cost: float = Field(default=1.0, description="Cost of current request in tokens")
    now: float = Field(default=1.0, description="Current unix timestamp")


class VecSearchSearchAutotuneDTO(BaseModel):
    ground_truth_topk: List[int] = Field(..., description="Ground-truth exact neighbor IDs")
    parameter_evaluations: List[Dict[str, Any]] = Field(..., description="Evaluations across parameter settings")
    target_recall: float = Field(default=0.95, description="Target recall threshold")

@router.post("/algos/vector-search/gemm")
def vector_search_gemm_endpoint(payload: VecSearchBruteForceGemmDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-51", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/simd-dist")
def vector_search_simd_dist_endpoint(payload: VecSearchSimdDistanceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-52", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/topk")
def vector_search_topk_endpoint(payload: VecSearchHeapTopKDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-53", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/radix-topk")
def vector_search_radix_topk_endpoint(payload: VecSearchRadixTopKDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-54", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/early-abandon")
def vector_search_early_abandon_endpoint(payload: VecSearchEarlyAbandonDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-55", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/pivot-prune")
def vector_search_pivot_prune_endpoint(payload: VecSearchPivotPruneDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-56", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/kdtree")
def vector_search_kdtree_endpoint(payload: VecSearchKdTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-57", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/ball-tree")
def vector_search_ball_tree_endpoint(payload: VecSearchBallTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-58", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/vptree")
def vector_search_vptree_endpoint(payload: VecSearchVpTreeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-59", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/rp-forest")
def vector_search_rp_forest_endpoint(payload: VecSearchRpForestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-60", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/ivf")
def vector_search_ivf_endpoint(payload: VecSearchIvfDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-61", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/ivf-pq")
def vector_search_ivf_pq_endpoint(payload: VecSearchIvfPqDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-62", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/nprobe-tune")
def vector_search_nprobe_tune_endpoint(payload: VecSearchNprobeTunerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-63", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/imi")
def vector_search_imi_endpoint(payload: VecSearchInvertedMultiIndexDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-64", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/nsw")
def vector_search_nsw_endpoint(payload: VecSearchNswDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-65", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/hnsw-search")
def vector_search_hnsw_search_endpoint(payload: VecSearchHnswSearchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-66", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/hnsw-insert")
def vector_search_hnsw_insert_endpoint(payload: VecSearchHnswInsertDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-67", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/beam-search")
def vector_search_beam_search_endpoint(payload: VecSearchBeamSearchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-68", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/vamana")
def vector_search_vamana_endpoint(payload: VecSearchVamanaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-69", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/robust-prune")
def vector_search_robust_prune_endpoint(payload: VecSearchRobustPruneDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-70", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/nsg")
def vector_search_nsg_endpoint(payload: VecSearchNsgDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-71", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/cagra")
def vector_search_cagra_endpoint(payload: VecSearchCagraDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-72", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/entry-point")
def vector_search_entry_point_endpoint(payload: VecSearchEntryPointDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-73", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/connectivity-repair")
def vector_search_connectivity_repair_endpoint(payload: VecSearchConnectivityRepairDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-74", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/filtered-diskann")
def vector_search_filtered_diskann_endpoint(payload: VecSearchFilteredDiskannDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-75", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/spann")
def vector_search_spann_endpoint(payload: VecSearchSpannDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-76", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/random-hyperplane-lsh")
def vector_search_random_hyperplane_lsh_endpoint(payload: VecSearchRandomHyperplaneLshDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-77", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/multi-probe-lsh")
def vector_search_multi_probe_lsh_endpoint(payload: VecSearchMultiProbeLshDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-78", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/e2lsh")
def vector_search_e2lsh_endpoint(payload: VecSearchE2LshDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-79", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)

@router.post("/algos/vector-search/bm25")
def vector_search_bm25_endpoint(payload: VecSearchBM25DTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-85", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/sparse-dense-hybrid")
def vector_search_sparse_dense_hybrid_endpoint(payload: VecSearchSparseDenseHybridDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-86", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/rrf")
def vector_search_rrf_endpoint(payload: VecSearchRRFDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-87", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/convex-score-fusion")
def vector_search_convex_score_fusion_endpoint(payload: VecSearchConvexScoreFusionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-88", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/mmr")
def vector_search_mmr_endpoint(payload: VecSearchMMRDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-89", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/range-search")
def vector_search_range_search_endpoint(payload: VecSearchRangeSearchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-90", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/maxsim")
def vector_search_maxsim_endpoint(payload: VecSearchMaxSimDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-91", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/multi-query-expansion")
def vector_search_multi_query_expansion_endpoint(payload: VecSearchMultiQueryExpansionDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-92", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/full-precision-rescore")
def vector_search_full_precision_rescore_endpoint(payload: VecSearchFullPrecisionRescoreDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-93", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/cross-encoder-rerank")
def vector_search_cross_encoder_rerank_endpoint(payload: VecSearchCrossEncoderRerankDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-94", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/multi-stage-funnel")
def vector_search_multi_stage_funnel_endpoint(payload: VecSearchMultiStageFunnelDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-95", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/llm-listwise-rerank")
def vector_search_llm_listwise_rerank_endpoint(payload: VecSearchLLMListwiseRerankDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-96", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/hyde")
def vector_search_hyde_endpoint(payload: VecSearchHyDEDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-97", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/query-routing")
def vector_search_query_routing_endpoint(payload: VecSearchQueryRoutingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-98", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/scatter-gather")
def vector_search_scatter_gather_endpoint(payload: VecSearchScatterGatherDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-99", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/partition-aware-routing")
def vector_search_partition_aware_routing_endpoint(payload: VecSearchPartitionAwareRoutingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-100", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/replication-load-balancer")
def vector_search_replication_load_balancer_endpoint(payload: VecSearchReplicationLoadBalancerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-101", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/hedged-requests")
def vector_search_hedged_requests_endpoint(payload: VecSearchHedgedRequestsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-102", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/kway-merge")
def vector_search_kway_merge_endpoint(payload: VecSearchKWayMergeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-103", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/query-cache")
def vector_search_query_cache_endpoint(payload: VecSearchQueryCacheDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-104", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/semantic-cache")
def vector_search_semantic_cache_endpoint(payload: VecSearchSemanticCacheDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-105", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/query-batching")
def vector_search_query_batching_endpoint(payload: VecSearchQueryBatchingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-106", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/memory-tiering")
def vector_search_memory_tiering_endpoint(payload: VecSearchMemoryTieringDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-107", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/disk-io-scheduler")
def vector_search_disk_io_scheduler_endpoint(payload: VecSearchDiskIOSchedulerDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-108", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/admission-control")
def vector_search_admission_control_endpoint(payload: VecSearchAdmissionControlDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-109", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-search/search-autotune")
def vector_search_search_autotune_endpoint(payload: VecSearchSearchAutotuneDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-SRCH-110", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)
