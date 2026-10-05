"""
================================================================================
ALGORITHM & ARCHITECTURE BLUEPRINT: REST API V1 ROUTER
================================================================================

1. OVERVIEW & OBJECTIVE:
   This module provides HTTP REST endpoints for the Policy Orchestrator:
   - System Core:
     • GET  /api/v1/health: Readiness and liveness probing.
     • POST /api/v1/rag/search: Grounded semantic search over policy markdown rules.
     • POST /api/v1/rag/index: Trigger full re-indexing of policy knowledge base.
     • POST /api/v1/agent/run: Execute autonomous AI Agent policy reasoning workflow.
     • GET  /api/v1/agents: List all declarative specialized agent manifests.
     • POST /api/v1/agents/{agent_id}/run: Execute a specific declarative agent.
     • POST /api/v1/audit/scan: Execute deterministic invariant repository audit.
     • POST /api/v1/graph/build: Extract & build semantic policy knowledge graph.
     • POST /api/v1/graph/query: Execute declarative Cypher/pattern queries.
     • GET  /api/v1/graph/impact/{rule_id}: Query topological rule dependencies.
   - Algorithm Catalog & Composition:
     • GET  /api/v1/algos/contracts: List and filter all 33 Layer 1 algorithm contracts.
     • GET  /api/v1/algos/contracts/{algo_id}: Get specific algorithm contract by ID.
     • GET  /api/v1/algos/adapters: List all 11 G4 Type Conversion Adapters.
     • POST /api/v1/algos/compose: Validate and compose dynamic multi-algorithm pipeline.
     • POST /api/v1/algos/execute/{algo_id}: Universal direct algorithm execution.
   - Search Algorithms (ALGO-SRCH-01..15):
     • POST /api/v1/algos/search/walk: Recursive file walker.
     • POST /api/v1/algos/search/work-stealing-walk: Parallel work-stealing walker.
     • POST /api/v1/algos/search/git-aware-walk: Git-aware ignore walker.
     • POST /api/v1/algos/search/glob-match: Fast glob pattern matcher.
     • POST /api/v1/algos/search/binary-check: Binary file classifier.
     • POST /api/v1/algos/search/content-type: MIME/Content-type prober.
     • POST /api/v1/algos/search/size-line-check: File size and line bouncer.
     • POST /api/v1/algos/search/generated-code-check: Generated code classifier.
     • POST /api/v1/algos/search/trigram-index: Trigram inverted index generator.
     • POST /api/v1/algos/search/simd-memchr: SIMD-Memchr vectorized byte scanner.
     • POST /api/v1/algos/search/aho-corasick: Aho-Corasick multi-pattern scanner.
     • POST /api/v1/algos/search/lazy-dfa: Lazy DFA regex matcher.
     • POST /api/v1/algos/search/streaming-chunk-scan: Streaming chunk scanner.
     • POST /api/v1/algos/search/context-snippet: Context snippet collector.
     • POST /api/v1/algos/search/mmap-scan: Memory-mapped file scanner.
     • POST /api/v1/algos/search/scan: Multi-pattern fast directory scan.
   - Observability Algorithms (ALGO-OBS-16..21):
     • POST /api/v1/algos/observability/span-track: Fast line-column span tracker.
     • POST /api/v1/algos/observability/ast: Language-agnostic AST extractor.
     • POST /api/v1/algos/observability/symbols: Lexical and global scope symbol resolver.
     • POST /api/v1/algos/observability/lint-comments: Zero-inline-comment doctrine linter.
     • POST /api/v1/algos/observability/dependencies: Module import dependency grapher.
     • POST /api/v1/algos/observability/outline: Hierarchical symbol outline generator.
   - Update Algorithms (ALGO-UPD-22..24):
     • POST /api/v1/algos/update/cst-match: CST matcher and syntax replacer.
     • POST /api/v1/algos/update/patch: Deterministic atomic multi-file patcher.
     • POST /api/v1/algos/update/diff: Unified GNU/Git context diff engine.
   - Vector Algorithms (ALGO-VEC-01..09):
     • POST /api/v1/algos/vector/normalize: Vector L2 Normalization.
     • POST /api/v1/algos/vector/center: Corpus Mean Centering.
     • POST /api/v1/algos/vector/layer-norm: Layer Normalization & Standardization.
     • POST /api/v1/algos/vector/scale: Min-Max and Z-Score Scaling.
     • POST /api/v1/algos/vector/slice: Matryoshka Representation Learning (MRL) Slicing.
     • POST /api/v1/algos/vector/quantize/scalar: Uniform Scalar Quantization (SQ8/SQ4).
     • POST /api/v1/algos/vector/quantize/binary: 1-Bit Binary Quantization.
     • POST /api/v1/algos/vector/pool: Token Pooling Engine.
     • POST /api/v1/algos/vector/chunk: Text Chunking and Semantic Breakpoints.
   - Vector Search Algorithms (ALGO-VEC-SRCH-51..64):
     • POST /api/v1/algos/vector-search/gemm: Exact kNN Brute-Force GEMM Scan.
     • POST /api/v1/algos/vector-search/simd-dist: SIMD Chunked Vector Distance Kernels.
     • POST /api/v1/algos/vector-search/topk: Bounded Memory Max/Min-Heap Top-k Selector.
     • POST /api/v1/algos/vector-search/radix-topk: Linear-Time Quickselect/Radix Top-k Partitioner.
     • POST /api/v1/algos/vector-search/early-abandon: Monotonic Distance Accumulator with Early Abandoning.
     • POST /api/v1/algos/vector-search/pivot-prune: Metric Pivot Triangle Inequality Filter.
     • POST /api/v1/algos/vector-search/kdtree: Orthogonal Axis Hyperplane KD-Tree Spatial Index.
     • POST /api/v1/algos/vector-search/ball-tree: Hyperspherical Metric Ball Tree Index.
     • POST /api/v1/algos/vector-search/vptree: Concentric Vantage-Point Spherical Shell Tree Index.
     • POST /api/v1/algos/vector-search/rp-forest: Annoy-Style Random Projection Hyperplane Forest.
     • POST /api/v1/algos/vector-search/ivf: Inverted File Voronoi Coarse Quantizer Index.
     • POST /api/v1/algos/vector-search/ivf-pq: Inverted File with Product Quantization and Asymmetric Distance.
     • POST /api/v1/algos/vector-search/nprobe-tune: Automated Pareto Frontier nprobe Tuner.
     • POST /api/v1/algos/vector-search/imi: Inverted Multi-Index Dual Codebook Coarse Quantizer.
     • POST /api/v1/algos/vector-search/nsw: Navigable Small World Proximity Graph.
     • POST /api/v1/algos/vector-search/hnsw-search: Hierarchical NSW Multilayer Beam Search.
     • POST /api/v1/algos/vector-search/hnsw-insert: HNSW Scale-Free Layer Insertion & Heuristic.
     • POST /api/v1/algos/vector-search/beam-search: Bounded Beam Search on Proximity Graphs.
     • POST /api/v1/algos/vector-search/vamana: Vamana/DiskANN Two-Pass Proximity Graph Index.
     • POST /api/v1/algos/vector-search/robust-prune: RobustPrune Alpha Diversity Filter.
     • POST /api/v1/algos/vector-search/nsg: Navigating Spreading-out Graph with MRNG Pruning.
     • POST /api/v1/algos/vector-search/cagra: GPU-Optimized Fixed-Degree Regular Graph.
     • POST /api/v1/algos/vector-search/entry-point: Medoid & Multi-Seed Entry-Point Selection.
     • POST /api/v1/algos/vector-search/connectivity-repair: Graph Reachability Audit & Island Repair.
     • POST /api/v1/algos/vector-search/filtered-diskann: Label-Constrained In-Index Graph Traversal.
     • POST /api/v1/algos/vector-search/spann: SPANN Memory-Disk Hybrid with Boundary Duplication.
     • POST /api/v1/algos/vector-search/random-hyperplane-lsh: Random-Hyperplane Cosine LSH.
     • POST /api/v1/algos/vector-search/multi-probe-lsh: Multi-Probe Perturbation Sequence LSH.
     • POST /api/v1/algos/vector-search/e2lsh: Exact 2-Stable Gaussian L2 Locality-Sensitive Hashing.
   - Vector Filter Algorithms (ALGO-VEC-FLTR-80..84):
     • POST /api/v1/algos/vector-filter/pre-filter: Metadata Pre-Filtering (ALGO-VEC-FLTR-80).
     • POST /api/v1/algos/vector-filter/post-filter: Oversampled Post-Filtering (ALGO-VEC-FLTR-81).
     • POST /api/v1/algos/vector-filter/in-graph: ACORN-Style In-Graph Filtering (ALGO-VEC-FLTR-82).
     • POST /api/v1/algos/vector-filter/selectivity-plan: Cost-Based Selectivity Query Planner (ALGO-VEC-FLTR-83).
     • POST /api/v1/algos/vector-filter/partitioned: Partitioned Multi-Tenant Index Search (ALGO-VEC-FLTR-84).

2. ARCHITECTURAL LAYOUT & DESIGN PILLARS:
   - Strict Protocol Envelope: All routes strictly return `{success, statusCode, data, errors, meta}`
     conforming to `policies/rules/folderStructure/api-request-response-structure.md` (v5.0).
   - Zero-Inline-Comment Doctrine: All router signatures, parameter mappings, dependency
     injections, and validation pipelines are articulated solely in this blueprint header.
     Router handler functions remain 100% comment-free and pure.
   - W3C Trace Context: Request traces and span contexts propagated across all envelopes.
================================================================================
"""

import os
import time
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from fastapi import APIRouter, Request, HTTPException

from src.api.rest.envelope import build_success_envelope, build_error_envelope
from src.features.rag.schema.rag_schema import (
    RAGSearchRequestDTO,
    IndexingStatusDTO,
)
from src.features.rag.types.rag_types import RAGQueryRequest
from src.features.agent.schema.agent_schema import (
    AgentRunRequestDTO,
)
from src.features.agent.types.agent_types import AgentExecutionRequest
from src.domain.ports.agent_manifest_port import AgentRole
from src.features.audit.service.audit_service import AuditService
from src.features.rag.service.rag_service import RAGService
from src.features.agent.service.agent_service import AgentService
from src.features.knowledge_graph.service.knowledge_graph_service import KnowledgeGraphService
from src.infra.adapters.knowledge.policy_rules_loader import PolicyRulesMarkdownLoader
from src.infra.adapters.vector.in_memory_vector_adapter import InMemoryCosineVectorAdapter
from src.infra.adapters.vector.qdrant_vector_adapter import QdrantVectorAdapter
from src.infra.adapters.graph.in_memory_graph_adapter import InMemoryGraphAdapter
from src.infra.adapters.graph.neo4j_adapter import Neo4jGraphAdapter
from src.infra.adapters.search.duckduckgo_search_adapter import DuckDuckGoSearchAdapter
from src.infra.adapters.search.mock_search_adapter import MockWebSearchAdapter
from src.infra.adapters.tools.in_memory_tool_registry_adapter import InMemoryToolRegistryAdapter
from src.infra.adapters.agent.in_memory_agent_registry_adapter import InMemoryAgentManifestRegistryAdapter
from src.infra.adapters.llm.openai_compatible_adapter import OpenAICompatibleAdapter
from src.infra.adapters.llm.mock_llm_adapter import MockLLMAdapter
from src.domain.models.algorithm_contract import (
    AlgorithmCategory,
    Purity,
    SideEffectScope,
    AlgorithmContract,
    TypeAdapterContract,
)
from src.infra.adapters.database import (
    InMemoryAlgorithmRegistryAdapter,
    SQLiteAlgorithmRegistryAdapter,
    AlloyDBAlgorithmRegistryAdapter,
    PostgresAlgorithmRegistryAdapter,
    DatabaseMigrationRunner,
)
from src.features.code_engine.service.algorithm_composer_service import AlgorithmComposerService
from src.features.code_engine.service.code_engine_service import CodeEngineService

router = APIRouter(prefix="/api/v1")


class GraphQueryDTO(BaseModel):
    query: str = Field(..., description="Cypher or pattern matching query")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Query parameters")


class AlgoScanDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to scan")
    patterns: List[str] = Field(..., description="Patterns to search for")
    max_files: int = Field(default=1000, description="Max files to scan")


class FilePathDTO(BaseModel):
    file_path: str = Field(..., description="File path to analyze")


class DirectoryPathDTO(BaseModel):
    directory: str = Field(default=".", description="Directory path to analyze")


class PatchOperationDTO(BaseModel):
    file_path: str = Field(..., description="File to patch")
    find_pattern: str = Field(..., description="Target pattern")
    replace_text: str = Field(..., description="Replacement text")
    expected_sha256: Optional[str] = Field(default=None, description="Precondition SHA-256")
    is_regex: bool = Field(default=False, description="Is regex pattern")


class BatchPatchRequestDTO(BaseModel):
    operations: List[PatchOperationDTO] = Field(..., description="List of patch operations")
    dry_run: bool = Field(default=False, description="Simulate patch without disk write")


class DiffRequestDTO(BaseModel):
    original_content: str = Field(..., description="Original text")
    modified_content: str = Field(..., description="Modified text")
    file_path: str = Field(default="file", description="File path identifier")


class AlgoComposeRequestDTO(BaseModel):
    algo_ids: List[str] = Field(..., description="Ordered list of algorithm IDs to compose")
    strict_check: bool = Field(default=True, description="Enforce strict contract safety checks")


class AlgoExecuteRequestDTO(BaseModel):
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Algorithm input parameters")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Optional algorithm execution parameters")


class SearchWalkDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to walk")
    max_depth: Optional[int] = Field(default=None, description="Maximum directory traversal depth")
    allowed_extensions: Optional[List[str]] = Field(default=None, description="Allowed file extensions")


class SearchWorkStealingDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to walk")
    workers: int = Field(default=4, description="Parallel worker threads")


class SearchGitAwareDTO(BaseModel):
    root_dir: str = Field(default=".", description="Root directory to walk")
    ignore_files: Optional[List[str]] = Field(default=None, description="Custom ignore patterns")


class SearchGlobDTO(BaseModel):
    pattern: str = Field(..., description="Glob pattern")
    path: str = Field(..., description="File path to test")


class SearchSizeLineDTO(BaseModel):
    file_path: str = Field(..., description="Target file path")
    max_bytes: int = Field(default=10485760, description="Max allowed bytes")
    max_lines: int = Field(default=50000, description="Max allowed lines")


class SearchTrigramDTO(BaseModel):
    text: str = Field(..., description="Input text to index into trigrams")


class SearchSimdMemchrDTO(BaseModel):
    data: str = Field(..., description="Input text/data")
    byte: str = Field(default="\n", description="Target character/byte to search")


class SearchAhoCorasickDTO(BaseModel):
    text: str = Field(..., description="Haystack text")
    patterns: List[str] = Field(..., description="Needle patterns to match simultaneously")


class SearchLazyDfaDTO(BaseModel):
    pattern: str = Field(..., description="Regex pattern")
    text: str = Field(..., description="Text to match against")


class SearchContextSnippetDTO(BaseModel):
    lines: List[str] = Field(..., description="File lines")
    line_number: int = Field(..., description="1-based match line number")
    lines_before: int = Field(default=2, description="Leading context lines")
    lines_after: int = Field(default=2, description="Trailing context lines")


class SearchMmapDTO(BaseModel):
    file_path: str = Field(..., description="Path to file")
    pattern: str = Field(..., description="Byte/text pattern to find")


class ObsSpanTrackDTO(BaseModel):
    content: str = Field(..., description="Source code content")
    offset: int = Field(default=0, description="Byte or character offset")


class ObsAstDTO(BaseModel):
    code: str = Field(..., description="Source code")
    language: str = Field(default="python", description="Programming language")


class ObsSymbolsDTO(BaseModel):
    code: str = Field(..., description="Source code")


class UpdateCstMatchDTO(BaseModel):
    code: str = Field(..., description="Source code")
    node_type: str = Field(default="function", description="Target CST node type")


class VectorNormalizeDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense float vector to normalize")
    eps: float = Field(default=1e-12, description="Zero-division guard epsilon")


class VectorCenterDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Batch of vectors for corpus mean centering")


class VectorLayerNormDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense input vector")
    gamma: Optional[List[float]] = Field(default=None, description="Learned scale parameter")
    beta: Optional[List[float]] = Field(default=None, description="Learned shift parameter")
    eps: float = Field(default=1e-5, description="Epsilon stability factor")


class VectorScaleDTO(BaseModel):
    vector: List[float] = Field(..., description="Input feature vector")
    min_val: float = Field(default=0.0, description="Target minimum range")
    max_val: float = Field(default=1.0, description="Target maximum range")
    method: str = Field(default="minmax", description="Scaling method ('minmax' or 'zscore')")


class VectorSliceDTO(BaseModel):
    vector: List[float] = Field(..., description="High-dimensional embedding vector")
    target_dim: int = Field(default=64, description="Target lower dimension prefix")
    renormalize: bool = Field(default=True, description="Apply L2 normalization after slicing")


class VectorScalarQuantizeDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense float vector")
    bits: int = Field(default=8, description="Quantization bit depth (8 or 4)")


class VectorBinaryQuantizeDTO(BaseModel):
    vector: List[float] = Field(..., description="Dense float vector")


class VectorPoolDTO(BaseModel):
    token_embeddings: List[List[float]] = Field(..., description="Sequence token embeddings (seq_len x dim)")
    attention_mask: Optional[List[int]] = Field(default=None, description="Attention mask (1 for token, 0 for pad)")
    pooling_strategy: str = Field(default="mean", description="Pooling method ('mean', 'cls', 'last')")


class VectorChunkDTO(BaseModel):
    text: str = Field(..., description="Document text to chunk")
    max_chunk_size: int = Field(default=200, description="Maximum characters/tokens per chunk")
    overlap: int = Field(default=40, description="Overlap between consecutive chunks")


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


class VecFilterPreFilterDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    metadata: List[Dict[str, Any]] = Field(..., description="Metadata dictionaries per vector")
    query: List[float] = Field(..., description="Query vector")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    k: int = Field(default=5, description="Top-k matching candidates")


class VecFilterPostFilterDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    metadata: List[Dict[str, Any]] = Field(..., description="Metadata dictionaries per vector")
    query: List[float] = Field(..., description="Query vector")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    k: int = Field(default=5, description="Top-k matching candidates")
    oversample_factor: float = Field(default=4.0, description="Oversampling multiplier")


class VecFilterInGraphDTO(BaseModel):
    vectors: List[List[float]] = Field(..., description="Dataset vectors")
    metadata: List[Dict[str, Any]] = Field(..., description="Metadata dictionaries per vector")
    adjacency: Dict[str, List[int]] = Field(..., description="Graph adjacency structure")
    entry_point: int = Field(default=0, description="Start traversal entry point node ID")
    query: List[float] = Field(..., description="Query vector")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    k: int = Field(default=5, description="Top-k matching candidates")
    ef_search: int = Field(default=16, description="Beam search width")


class VecFilterSelectivityPlanDTO(BaseModel):
    total_vectors: int = Field(..., description="Total size of vector dataset")
    metadata_sample: List[Dict[str, Any]] = Field(default_factory=list, description="Sample of metadata records")
    filters: Dict[str, Any] = Field(..., description="Filter predicate criteria")
    is_security_filter: bool = Field(default=False, description="Whether filter enforces strict security/tenant boundary")


class VecFilterPartitionedDTO(BaseModel):
    partitions: Dict[str, List[Dict[str, Any]]] = Field(..., description="Partition map keyed by tenant/collection")
    target_partition: str = Field(..., description="Partition key to query")
    query: List[float] = Field(..., description="Query vector")
    k: int = Field(default=5, description="Top-k matching candidates")


def get_orchestrator_services() -> Dict[str, Any]:
    rules_dir = os.environ.get("POLICY_RULES_DIR", "../rules")
    llm_backend = os.environ.get("LLM_BACKEND", "mock")
    vector_backend = os.environ.get("VECTOR_BACKEND", "inmemory")
    graph_backend = os.environ.get("GRAPH_BACKEND", "inmemory")
    search_backend = os.environ.get("SEARCH_BACKEND", "mock")
    
    knowledge_source = PolicyRulesMarkdownLoader(base_rules_dir=rules_dir)
    
    if vector_backend == "qdrant":
        vector_store = QdrantVectorAdapter(
            url=os.environ.get("QDRANT_URL", "http://localhost:6333"),
            collection_name=os.environ.get("QDRANT_COLLECTION", "policy_rules"),
            vector_size=int(os.environ.get("VECTOR_SIZE", "64")),
        )
    else:
        vector_store = InMemoryCosineVectorAdapter()
    
    if graph_backend == "neo4j":
        graph_store = Neo4jGraphAdapter(
            uri=os.environ.get("NEO4J_URI", "http://localhost:7474"),
            user=os.environ.get("NEO4J_USER", "neo4j"),
            password=os.environ.get("NEO4J_PASSWORD", "password"),
        )
    else:
        graph_store = InMemoryGraphAdapter()

    if search_backend == "duckduckgo":
        search_provider = DuckDuckGoSearchAdapter()
    else:
        search_provider = MockWebSearchAdapter()

    tool_registry = InMemoryToolRegistryAdapter()
    agent_registry = InMemoryAgentManifestRegistryAdapter(load_builtins=True)

    db_url = os.environ.get("DATABASE_URL")
    auto_migrate = os.environ.get("AUTO_MIGRATE", "true").lower() == "true"

    if db_url and (db_url.startswith("postgres://") or db_url.startswith("postgresql://")):
        if auto_migrate:
            try:
                migration_runner = DatabaseMigrationRunner(db_url)
                migration_runner.run_migrations()
                migration_runner.seed_algorithm_catalog()
            except Exception:
                pass
        algo_registry = AlloyDBAlgorithmRegistryAdapter(db_url)
    elif db_url and db_url.startswith("sqlite://"):
        if auto_migrate:
            try:
                migration_runner = DatabaseMigrationRunner(db_url)
                migration_runner.run_migrations()
                migration_runner.seed_algorithm_catalog()
            except Exception:
                pass
        db_path = db_url.replace("sqlite:///", "")
        algo_registry = SQLiteAlgorithmRegistryAdapter(db_path)
    else:
        algo_registry = SQLiteAlgorithmRegistryAdapter(":memory:")
        if auto_migrate:
            try:
                migration_runner = DatabaseMigrationRunner("sqlite:///:memory:")
                migration_runner.run_migrations(conn=algo_registry._memory_conn)
                migration_runner.seed_algorithm_catalog(conn=algo_registry._memory_conn)
            except Exception:
                pass

    composer_svc = AlgorithmComposerService(algo_registry)
    code_engine_svc = CodeEngineService()

    if llm_backend == "openai":
        llm_provider = OpenAICompatibleAdapter(
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", ""),
            model_name=os.environ.get("OPENAI_MODEL", "gpt-4o"),
        )
    elif llm_backend == "ollama":
        llm_provider = OpenAICompatibleAdapter(
            base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
            api_key="EMPTY",
            model_name=os.environ.get("OLLAMA_MODEL", "llama3.2"),
        )
    else:
        llm_provider = MockLLMAdapter()

    rag_svc = RAGService(
        knowledge_source=knowledge_source,
        vector_store=vector_store,
        llm_provider=llm_provider,
    )
    audit_svc = AuditService()
    agent_svc = AgentService(
        llm_provider=llm_provider,
        rag_service=rag_svc,
        audit_service=audit_svc,
        search_provider=search_provider,
        tool_registry=tool_registry,
    )
    graph_svc = KnowledgeGraphService(
        graph_store=graph_store,
        knowledge_source=knowledge_source,
    )

    return {
        "rag": rag_svc,
        "audit": audit_svc,
        "agent": agent_svc,
        "graph": graph_svc,
        "agent_registry": agent_registry,
        "tool_registry": tool_registry,
        "algo_registry": algo_registry,
        "composer": composer_svc,
        "code_engine": code_engine_svc,
    }


_SERVICES = None


def get_services() -> Dict[str, Any]:
    global _SERVICES
    if _SERVICES is None:
        _SERVICES = get_orchestrator_services()
    return _SERVICES


def get_code_engine_service() -> CodeEngineService:
    return get_services()["code_engine"]


@router.get("/health")
def health_check(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id") or request.headers.get("traceparent")
    return build_success_envelope(
        data={"status": "healthy", "service": "policy-orchestrator", "version": "0.1.0"},
        trace_id=trace_id,
    )


@router.post("/rag/index")
def index_policies(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    count = svcs["rag"].index_all_rules()
    return build_success_envelope(
        data={"indexed_documents": count, "status": "COMPLETED"},
        trace_id=trace_id,
    )


@router.post("/rag/search")
def search_policies(payload: RAGSearchRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    rag_req = RAGQueryRequest(
        query=payload.query,
        top_k=payload.top_k,
        category_filter=payload.category_filter,
        min_relevance_score=payload.min_score,
    )
    res = svcs["rag"].retrieve_context(rag_req)
    docs_data = [
        {
            "id": d.id,
            "source_file": d.source_file,
            "section_title": d.section_title,
            "content": d.content,
            "category": d.category,
            "rrf_score": d.rrf_score,
            "metadata": d.metadata,
        }
        for d in res.documents
    ]
    return build_success_envelope(
        data={
            "query": res.query,
            "total_found": res.total_found,
            "documents": docs_data,
            "formatted_context_block": res.formatted_context_block,
            "latency_ms": res.latency_ms,
        },
        trace_id=trace_id,
    )


@router.post("/agent/run")
def run_agent(payload: AgentRunRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    agent_req = AgentExecutionRequest(
        prompt=payload.prompt,
        target_directory=payload.target_directory,
        max_steps=payload.max_steps,
        temperature=payload.temperature,
        session_id=payload.session_id,
    )
    result = svcs["agent"].execute_agent_loop(agent_req)
    steps_data = [
        {
            "step_number": s.step_number,
            "thought": s.thought,
            "action": s.action,
            "observation": s.observation,
            "tool_calls": [
                {
                    "tool_name": tc.tool_name,
                    "arguments": tc.arguments,
                    "output": tc.output,
                    "duration_ms": tc.duration_ms,
                    "status": tc.status,
                }
                for tc in s.tool_calls
            ],
        }
        for s in result.steps
    ]
    return build_success_envelope(
        data={
            "session_id": result.session_id,
            "status": result.status,
            "final_response": result.final_response,
            "steps": steps_data,
            "total_steps": result.total_steps,
            "total_tokens": result.total_tokens,
            "grounded_sources": result.grounded_sources,
            "duration_ms": result.duration_ms,
        },
        trace_id=trace_id,
    )


@router.get("/agents")
def list_declarative_agents(request: Request, category: Optional[str] = None) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    manifests = svcs["agent_registry"].list_manifests(category=category)
    return build_success_envelope(
        data={
            "total_agents": len(manifests),
            "agents": [
                {
                    "agent_id": m.agent_id,
                    "name": m.name,
                    "role": m.role.value,
                    "category": m.category,
                    "description": m.description,
                    "algorithms": m.algorithms,
                    "allowed_tools": m.allowed_tools,
                    "tags": m.tags,
                }
                for m in manifests
            ],
        },
        trace_id=trace_id,
    )


@router.post("/agents/{agent_id}/run")
def run_specialized_agent(agent_id: str, payload: AgentRunRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    manifest = svcs["agent_registry"].get_manifest(agent_id)
    if not manifest:
        raise HTTPException(status_code=404, detail=f"Specialized Agent '{agent_id}' not found.")

    agent_req = AgentExecutionRequest(
        prompt=payload.prompt,
        target_directory=payload.target_directory,
        max_steps=payload.max_steps,
        temperature=payload.temperature,
        session_id=payload.session_id,
    )
    result = svcs["agent"].execute_agent_loop(agent_req, manifest=manifest)
    steps_data = [
        {
            "step_number": s.step_number,
            "thought": s.thought,
            "action": s.action,
            "observation": s.observation,
            "tool_calls": [
                {
                    "tool_name": tc.tool_name,
                    "arguments": tc.arguments,
                    "output": tc.output,
                    "duration_ms": tc.duration_ms,
                    "status": tc.status,
                }
                for tc in s.tool_calls
            ],
        }
        for s in result.steps
    ]
    return build_success_envelope(
        data={
            "agent_id": agent_id,
            "agent_name": manifest.name,
            "session_id": result.session_id,
            "status": result.status,
            "final_response": result.final_response,
            "steps": steps_data,
            "total_steps": result.total_steps,
            "total_tokens": result.total_tokens,
            "grounded_sources": result.grounded_sources,
            "duration_ms": result.duration_ms,
        },
        trace_id=trace_id,
    )


@router.post("/audit/scan")
def scan_repository(request: Request, target_directory: str = ".") -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    findings = svcs["audit"].audit_repository(target_directory)
    findings_data = [
        {
            "rule_id": f.rule_id,
            "category": f.category,
            "severity": f.severity,
            "description": f.description,
            "file": f.file,
            "line": f.line,
            "snippet": f.snippet,
            "recommendation": f.recommendation,
        }
        for f in findings
    ]
    return build_success_envelope(
        data={"total_findings": len(findings), "findings": findings_data},
        trace_id=trace_id,
    )


@router.post("/algos/search/walk")
def search_recursive_walk(payload: SearchWalkDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-01", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/work-stealing-walk")
def search_work_stealing_walk(payload: SearchWorkStealingDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-02", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/git-aware-walk")
def search_git_aware_walk(payload: SearchGitAwareDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-03", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/glob-match")
def search_glob_match(payload: SearchGlobDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-04", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/binary-check")
def search_binary_check(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-05", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/content-type")
def search_content_type(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-06", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/size-line-check")
def search_size_line_check(payload: SearchSizeLineDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-07", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/generated-code-check")
def search_generated_code_check(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-08", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/trigram-index")
def search_trigram_index(payload: SearchTrigramDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-09", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/simd-memchr")
def search_simd_memchr(payload: SearchSimdMemchrDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-10", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/aho-corasick")
def search_aho_corasick(payload: SearchAhoCorasickDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-11", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/lazy-dfa")
def search_lazy_dfa(payload: SearchLazyDfaDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-12", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/streaming-chunk-scan")
def search_streaming_chunk_scan(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-13", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/context-snippet")
def search_context_snippet(payload: SearchContextSnippetDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-14", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/mmap-scan")
def search_mmap_scan(payload: SearchMmapDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-SRCH-15", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/search/scan")
@router.post("/algos/scan")
def scan_multipattern(payload: AlgoScanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    results = svc.scan_directory_multipattern(
        root_dir=payload.root_dir,
        patterns=payload.patterns,
        max_files=payload.max_files,
    )
    return build_success_envelope(
        data={"total_files_matched": len(results), "results": results},
        trace_id=trace_id,
    )


@router.post("/algos/observability/span-track")
def obs_span_track(payload: ObsSpanTrackDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-OBS-16", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/observability/ast")
def obs_ast_extract(payload: ObsAstDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-OBS-17", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/observability/symbols")
def obs_symbols_resolve(payload: ObsSymbolsDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-OBS-18", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/observability/lint-comments")
@router.post("/algos/lint-comments")
def lint_comments(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    if not os.path.isfile(payload.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {payload.file_path}")
    report = svc.lint_zero_inline_comments(payload.file_path)
    return build_success_envelope(data=report, trace_id=trace_id)


@router.post("/algos/observability/dependencies")
@router.post("/algos/dependencies")
def analyze_dependencies(payload: DirectoryPathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    report = svc.analyze_module_dependencies(payload.directory)
    return build_success_envelope(data=report, trace_id=trace_id)


@router.post("/algos/observability/outline")
@router.post("/algos/outline")
def generate_file_outline(payload: FilePathDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    if not os.path.isfile(payload.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {payload.file_path}")
    outline = svc.inspect_file_outline(payload.file_path)
    return build_success_envelope(data=outline, trace_id=trace_id)


@router.post("/algos/update/cst-match")
def update_cst_match(payload: UpdateCstMatchDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-UPD-22", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/update/patch")
def apply_patch(payload: BatchPatchRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    raw_ops = [op.model_dump() for op in payload.operations]
    results = svc.apply_batch_patch(raw_ops, dry_run=payload.dry_run)
    return build_success_envelope(
        data={"total_operations": len(results), "dry_run": payload.dry_run, "results": results},
        trace_id=trace_id,
    )


@router.post("/algos/update/diff")
def generate_diff(payload: DiffRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    diff = svc.generate_diff(
        original_content=payload.original_content,
        modified_content=payload.modified_content,
        file_path=payload.file_path,
    )
    return build_success_envelope(data=diff, trace_id=trace_id)


@router.post("/algos/vector/normalize")
def normalize_vector_endpoint(payload: VectorNormalizeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    normalized = svc.normalize_vector(payload.vector, eps=payload.eps)
    return build_success_envelope(
        data={"original_dimension": len(payload.vector), "normalized_vector": normalized},
        trace_id=trace_id,
    )


@router.post("/algos/vector/center")
def center_vectors_endpoint(payload: VectorCenterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    centered = svc.center_vectors(payload.vectors)
    return build_success_envelope(
        data={"total_vectors": len(payload.vectors), "centered_vectors": centered},
        trace_id=trace_id,
    )


@router.post("/algos/vector/layer-norm")
def layer_norm_endpoint(payload: VectorLayerNormDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    norm = svc.layer_norm_vector(payload.vector, gamma=payload.gamma, beta=payload.beta, eps=payload.eps)
    return build_success_envelope(
        data={"dimension": len(payload.vector), "normalized_vector": norm},
        trace_id=trace_id,
    )


@router.post("/algos/vector/scale")
def scale_vector_endpoint(payload: VectorScaleDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    scaled = svc.scale_vector(payload.vector, min_val=payload.min_val, max_val=payload.max_val, method=payload.method)
    return build_success_envelope(
        data={"scaled_vector": scaled, "method": payload.method},
        trace_id=trace_id,
    )


@router.post("/algos/vector/slice")
def slice_vector_endpoint(payload: VectorSliceDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    sliced = svc.slice_vector(payload.vector, target_dim=payload.target_dim, renormalize=payload.renormalize)
    return build_success_envelope(
        data={"original_dimension": len(payload.vector), "target_dimension": payload.target_dim, "sliced_vector": sliced},
        trace_id=trace_id,
    )


@router.post("/algos/vector/quantize/scalar")
def quantize_scalar_endpoint(payload: VectorScalarQuantizeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.quantize_scalar(payload.vector, bits=payload.bits)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector/quantize/binary")
def quantize_binary_endpoint(payload: VectorBinaryQuantizeDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.quantize_binary(payload.vector)
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector/pool")
def pool_tokens_endpoint(payload: VectorPoolDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.pool_tokens(payload.token_embeddings, attention_mask=payload.attention_mask, pooling_strategy=payload.pooling_strategy)
    return build_success_envelope(
        data={"pooling_strategy": payload.pooling_strategy, "pooled_vector": res},
        trace_id=trace_id,
    )


@router.post("/algos/vector/chunk")
def chunk_text_endpoint(payload: VectorChunkDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    chunks = svc.chunk_text(
        text=payload.text,
        max_chunk_size=payload.max_chunk_size,
        overlap=payload.overlap,
    )
    return build_success_envelope(
        data={"total_chunks": len(chunks), "chunks": chunks},
        trace_id=trace_id,
    )


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


@router.post("/algos/vector-filter/pre-filter")
def vector_filter_pre_filter_endpoint(payload: VecFilterPreFilterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-80", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/post-filter")
def vector_filter_post_filter_endpoint(payload: VecFilterPostFilterDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-81", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/in-graph")
def vector_filter_in_graph_endpoint(payload: VecFilterInGraphDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-82", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/selectivity-plan")
def vector_filter_selectivity_plan_endpoint(payload: VecFilterSelectivityPlanDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-83", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)


@router.post("/algos/vector-filter/partitioned")
def vector_filter_partitioned_endpoint(payload: VecFilterPartitionedDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    res = svc.execute_algorithm("ALGO-VEC-FLTR-84", payload.model_dump())
    return build_success_envelope(data=res, trace_id=trace_id)



@router.post("/algos/execute/{algo_id}")
def execute_algorithm_direct(algo_id: str, payload: AlgoExecuteRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svc = get_code_engine_service()
    try:
        res = svc.execute_algorithm(algo_id=algo_id, inputs=payload.inputs, parameters=payload.parameters)
        return build_success_envelope(data={"algo_id": algo_id, "result": res}, trace_id=trace_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph/build")
def build_graph(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    summary = svcs["graph"].build_graph_from_rules()
    return build_success_envelope(data=summary, trace_id=trace_id)


@router.post("/graph/query")
def query_graph(payload: GraphQueryDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    res = svcs["graph"].query_cypher(payload.query, payload.parameters)
    return build_success_envelope(
        data={
            "records": res.records,
            "nodes_count": len(res.nodes),
            "relationships_count": len(res.relationships),
        },
        trace_id=trace_id,
    )


@router.get("/graph/impact/{rule_id}")
def get_rule_impact(rule_id: str, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    impact = svcs["graph"].get_rule_impact(rule_id)
    return build_success_envelope(data={"rule_id": rule_id, "impact": impact}, trace_id=trace_id)


@router.get("/algos/contracts")
def list_algorithm_contracts(
    request: Request,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    purity: Optional[str] = None,
    side_effects: Optional[str] = None,
) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    
    cat_enum = AlgorithmCategory(category) if category else None
    purity_enum = Purity(purity) if purity else None
    se_enum = SideEffectScope(side_effects) if side_effects else None
    tags_filter = [tag] if tag else None

    contracts = svcs["algo_registry"].list_algorithms(
        category=cat_enum,
        tags=tags_filter,
        purity=purity_enum,
        side_effects=se_enum,
    )
    return build_success_envelope(
        data={"total_contracts": len(contracts), "contracts": [c.model_dump() for c in contracts]},
        trace_id=trace_id,
    )


@router.get("/algos/contracts/{algo_id}")
def get_algorithm_contract(algo_id: str, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    contract = svcs["algo_registry"].get_algorithm(algo_id)
    if not contract:
        raise HTTPException(status_code=404, detail=f"Algorithm contract '{algo_id}' not found.")
    return build_success_envelope(data=contract.model_dump(), trace_id=trace_id)


@router.get("/algos/adapters")
def list_type_adapters(request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    adapters = svcs["algo_registry"].list_adapters()
    return build_success_envelope(
        data={"total_adapters": len(adapters), "adapters": [a.model_dump() for a in adapters]},
        trace_id=trace_id,
    )


@router.post("/algos/compose")
def compose_algorithm_pipeline(payload: AlgoComposeRequestDTO, request: Request) -> Dict[str, Any]:
    trace_id = request.headers.get("x-trace-id")
    svcs = get_services()
    try:
        plan = svcs["composer"].compose_pipeline(
            algo_ids=payload.algo_ids,
            strict_contract_check=payload.strict_check,
        )
        return build_success_envelope(data=plan, trace_id=trace_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
